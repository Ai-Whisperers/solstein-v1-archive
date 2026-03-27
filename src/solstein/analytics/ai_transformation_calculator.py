"""AI Transformation Readiness Calculator (STORY-146, EPIC-038).

Quantifies the cost, timeline, and ROI of transforming a company to AI-Ready
status. Designed for PE due diligence: "how much, how long, what return?"

The calculator takes a company profile (or raw inputs) and produces a
:class:`TransformationEstimate` with:

- **Time to AI-Ready** (months)
- **Investment Required** (EUR)
- **Expected Efficiency Gains** (percentage)
- **Risk Factors** (categorised High / Medium / Low)
- **Confidence interval** around each numeric estimate

Scenario planning is supported via :meth:`TransformationCalculator.simulate`
which accepts overrides (e.g. "what if we double the AI budget?").

Usage::

    from solstein.analytics.ai_transformation_calculator import TransformationCalculator
    calculator = TransformationCalculator()
    estimate = calculator.estimate(company)
    scenario = calculator.simulate(company, overrides={"ai_budget_eur": 2_000_000})
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from solstein.domain.models import Company


# ---------------------------------------------------------------------------
# Constants & lookup tables
# ---------------------------------------------------------------------------

class RiskLevel(str, Enum):
    """Risk severity for a transformation risk factor."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass(frozen=True)
class RiskFactor:
    """A single identified risk in the transformation plan."""

    category: str
    description: str
    level: RiskLevel
    mitigation: str


@dataclass(frozen=True)
class ConfidenceInterval:
    """Symmetric confidence interval around a point estimate."""

    low: float
    point: float
    high: float


@dataclass
class TransformationEstimate:
    """Full output of the transformation calculator."""

    # Core estimates
    time_to_ai_ready_months: ConfidenceInterval
    investment_required_eur: ConfidenceInterval
    expected_efficiency_gain_pct: ConfidenceInterval

    # Breakdown
    breakdown: dict[str, Any] = field(default_factory=dict)

    # Risk assessment
    risk_factors: list[RiskFactor] = field(default_factory=list)
    overall_risk: RiskLevel = RiskLevel.MEDIUM

    # Metadata
    scenario_label: str = "baseline"
    overrides_applied: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Size-class thresholds (employee count)
# ---------------------------------------------------------------------------

_SIZE_CLASSES: list[tuple[int, str, float, float]] = [
    # (max_employees, label, base_months, base_cost_eur)
    (50, "startup", 6.0, 150_000),
    (200, "small", 10.0, 500_000),
    (1000, "mid-market", 16.0, 2_000_000),
    (5000, "large", 24.0, 8_000_000),
    (999_999, "enterprise", 36.0, 25_000_000),
]

# AI maturity string (lowercased) -> discount factor on time/cost (lower = more mature)
# Supports both the Company.ai_maturity enum values and the ai_readiness module labels.
_MATURITY_DISCOUNT: dict[str, float] = {
    "very strong": 0.20,
    "strong": 0.35,
    "moderate": 0.55,
    "low": 0.80,
    "none": 1.00,
    # ai_readiness style labels (STORY-145 compat)
    "exceptional": 0.20,
    "advanced": 0.45,
    "emerging": 0.75,
    "unknown": 0.85,
}

# SaaS maturity (0-10) -> discount multiplier
_SAAS_DISCOUNT_SLOPE = 0.06  # each SaaS point reduces time/cost by 6 %

# Tech-stack keywords that reduce transformation cost
_MODERN_STACK_KEYWORDS = frozenset({
    "python", "kubernetes", "docker", "aws", "azure", "gcp",
    "tensorflow", "pytorch", "spark", "airflow", "snowflake",
    "databricks", "mlflow", "cloud", "microservices", "api",
})

_LEGACY_STACK_KEYWORDS = frozenset({
    "cobol", "mainframe", "on-premise", "on-prem", "legacy",
    "fortran", "delphi", "foxpro", "access", "vba",
})


# ---------------------------------------------------------------------------
# Calculator
# ---------------------------------------------------------------------------

class TransformationCalculator:
    """Estimate cost, timeline and ROI for AI transformation.

    The calculator is stateless — all company data flows through
    method arguments so it can be reused across companies.
    """

    # -- public API ---------------------------------------------------------

    def estimate(self, company: Company) -> TransformationEstimate:
        """Produce a baseline transformation estimate for *company*."""
        params = self._extract_params(company)
        return self._calculate(params, scenario_label="baseline")

    def simulate(
        self,
        company: Company,
        overrides: dict[str, Any] | None = None,
    ) -> TransformationEstimate:
        """Run a what-if scenario with *overrides* applied on top of company data.

        Supported override keys:
            ai_budget_eur, employees, ai_maturity, saas_maturity,
            tech_stack, growth_rate
        """
        params = self._extract_params(company)
        if overrides:
            params.update(overrides)
        return self._calculate(
            params,
            scenario_label="simulation",
            overrides_applied=overrides or {},
        )

    def estimate_from_params(self, params: dict[str, Any]) -> TransformationEstimate:
        """Estimate directly from a parameter dict (no Company needed)."""
        return self._calculate(params, scenario_label="manual")

    # -- parameter extraction -----------------------------------------------

    @staticmethod
    def _extract_params(company: Company) -> dict[str, Any]:
        """Pull relevant signals from a Company into a flat dict."""
        employees: int | None = None
        if company.financials is not None:
            employees = getattr(company.financials, "employees", None)

        return {
            "employees": employees,
            "ai_maturity": getattr(company, "ai_maturity", None),
            "saas_maturity": getattr(company, "saas_maturity", 1),
            "tech_stack": getattr(company, "tech_stack", []),
            "revenue": company.revenue,
            "growth_rate": company.growth_rate,
            "funding": getattr(company, "funding_raised", None) or getattr(company, "funding", None),
            "ai_score": getattr(company, "ai_score", None),
            "ai_in_production": getattr(company, "ai_in_production", None),
            "industry": getattr(company, "industry", "Energy Software"),
        }

    # -- core calculation ---------------------------------------------------

    def _calculate(
        self,
        params: dict[str, Any],
        *,
        scenario_label: str = "baseline",
        overrides_applied: dict[str, Any] | None = None,
    ) -> TransformationEstimate:
        """Core estimation logic."""
        employees = params.get("employees") or 100  # default assumption
        ai_maturity = str(params.get("ai_maturity") or "unknown").lower()
        saas_maturity = int(params.get("saas_maturity") or 1)
        tech_stack = [s.lower() for s in (params.get("tech_stack") or [])]
        growth_rate = params.get("growth_rate")
        ai_budget = params.get("ai_budget_eur")

        # 1. Base time & cost from company size
        base_months, base_cost = self._size_class_estimates(employees)

        # 2. AI maturity discount
        maturity_factor = _MATURITY_DISCOUNT.get(ai_maturity, 0.85)

        # 3. SaaS maturity discount
        saas_factor = max(0.30, 1.0 - saas_maturity * _SAAS_DISCOUNT_SLOPE)

        # 4. Tech stack modifier
        stack_factor = self._tech_stack_factor(tech_stack)

        # 5. Combine factors
        combined_factor = maturity_factor * saas_factor * stack_factor

        time_months = base_months * combined_factor
        investment_eur = base_cost * combined_factor

        # 6. If explicit AI budget provided, adjust timeline proportionally
        if ai_budget is not None and ai_budget > 0 and investment_eur > 0:
            budget_ratio = ai_budget / investment_eur
            # More budget -> faster, but diminishing returns
            time_months = time_months / max(0.5, math.sqrt(budget_ratio))
            investment_eur = min(ai_budget, investment_eur)

        # 7. Efficiency gain estimate (higher maturity -> less room for gain)
        efficiency_gain_pct = self._efficiency_gain(
            maturity_factor, saas_maturity, growth_rate,
        )

        # 8. Risk assessment
        risk_factors = self._assess_risks(params)
        overall_risk = self._overall_risk(risk_factors)

        # 9. Confidence intervals (wider for less data)
        data_quality = self._data_quality_score(params)
        margin = 0.15 + (1.0 - data_quality) * 0.35  # 15-50 % margin

        breakdown = {
            "base_months": round(base_months, 1),
            "base_cost_eur": round(base_cost, 0),
            "maturity_factor": round(maturity_factor, 3),
            "saas_factor": round(saas_factor, 3),
            "stack_factor": round(stack_factor, 3),
            "combined_factor": round(combined_factor, 3),
            "data_quality": round(data_quality, 2),
            "confidence_margin": round(margin, 2),
            "employees_used": employees,
            "ai_maturity_used": ai_maturity,
        }

        return TransformationEstimate(
            time_to_ai_ready_months=_ci(time_months, margin),
            investment_required_eur=_ci(investment_eur, margin),
            expected_efficiency_gain_pct=_ci(efficiency_gain_pct, margin * 0.6),
            breakdown=breakdown,
            risk_factors=risk_factors,
            overall_risk=overall_risk,
            scenario_label=scenario_label,
            overrides_applied=overrides_applied or {},
        )

    # -- sub-calculations ---------------------------------------------------

    @staticmethod
    def _size_class_estimates(employees: int) -> tuple[float, float]:
        """Return (base_months, base_cost_eur) for the employee count."""
        for max_emp, _label, months, cost in _SIZE_CLASSES:
            if employees <= max_emp:
                return months, cost
        return _SIZE_CLASSES[-1][2], _SIZE_CLASSES[-1][3]

    @staticmethod
    def _tech_stack_factor(stack: list[str]) -> float:
        """Score tech stack modernity: lower = more modern = less effort."""
        if not stack:
            return 0.90  # unknown stack, slight penalty

        modern_count = sum(1 for s in stack if s in _MODERN_STACK_KEYWORDS)
        legacy_count = sum(1 for s in stack if s in _LEGACY_STACK_KEYWORDS)

        if legacy_count > modern_count:
            return min(1.40, 1.0 + legacy_count * 0.10)
        if modern_count > 0:
            return max(0.50, 1.0 - modern_count * 0.08)
        return 0.90

    @staticmethod
    def _efficiency_gain(
        maturity_factor: float,
        saas_maturity: int,
        growth_rate: float | None,
    ) -> float:
        """Estimate expected efficiency gain (%) from AI adoption.

        Companies that are *less* mature have more room for improvement,
        so the gain is inversely related to current maturity.
        """
        # Base gain: 15-45 % depending on maturity gap
        base_gain = 15.0 + (maturity_factor * 30.0)

        # SaaS-mature companies realise gains faster
        saas_bonus = min(10.0, saas_maturity * 1.5)

        # High-growth companies tend to capture more value
        growth_bonus = 0.0
        if growth_rate is not None and growth_rate > 20:
            growth_bonus = min(8.0, (growth_rate - 20) * 0.4)

        return min(55.0, base_gain + saas_bonus + growth_bonus)

    @staticmethod
    def _assess_risks(params: dict[str, Any]) -> list[RiskFactor]:
        """Identify transformation risk factors from company signals."""
        risks: list[RiskFactor] = []

        employees = params.get("employees") or 100
        ai_maturity = str(params.get("ai_maturity") or "unknown").lower()
        saas_maturity = int(params.get("saas_maturity") or 1)
        tech_stack = [s.lower() for s in (params.get("tech_stack") or [])]
        funding = params.get("funding")

        # Talent risk
        if employees < 50:
            risks.append(RiskFactor(
                category="talent",
                description="Small team may lack capacity for parallel AI initiatives",
                level=RiskLevel.HIGH,
                mitigation="Consider outsourced AI team or managed ML platform",
            ))
        elif employees < 200:
            risks.append(RiskFactor(
                category="talent",
                description="Limited internal talent pool for AI roles",
                level=RiskLevel.MEDIUM,
                mitigation="Hire 2-3 ML engineers or partner with AI consultancy",
            ))

        # Legacy tech risk
        legacy_count = sum(1 for s in tech_stack if s in _LEGACY_STACK_KEYWORDS)
        if legacy_count >= 2:
            risks.append(RiskFactor(
                category="technology",
                description="Heavy legacy technology stack increases migration complexity",
                level=RiskLevel.HIGH,
                mitigation="Phased modernisation: containerise first, then migrate",
            ))
        elif legacy_count == 1:
            risks.append(RiskFactor(
                category="technology",
                description="Some legacy technology present",
                level=RiskLevel.MEDIUM,
                mitigation="Isolate legacy components behind APIs",
            ))

        # Data maturity risk
        if saas_maturity <= 2:
            risks.append(RiskFactor(
                category="data",
                description="Low SaaS/data maturity hinders AI data pipeline setup",
                level=RiskLevel.HIGH,
                mitigation="Invest in data platform before AI initiatives",
            ))

        # AI experience risk
        if ai_maturity in ("none", "unknown"):
            risks.append(RiskFactor(
                category="experience",
                description="No prior AI experience increases adoption risk",
                level=RiskLevel.MEDIUM,
                mitigation="Start with low-risk AI pilot project",
            ))

        # Funding risk
        if funding is not None and funding < 500_000:
            risks.append(RiskFactor(
                category="financial",
                description="Limited funding may constrain AI investment capacity",
                level=RiskLevel.MEDIUM,
                mitigation="Seek AI-specific grants or strategic investor",
            ))

        return risks

    @staticmethod
    def _overall_risk(risk_factors: list[RiskFactor]) -> RiskLevel:
        """Determine overall risk level from individual factors."""
        if not risk_factors:
            return RiskLevel.LOW
        high_count = sum(1 for r in risk_factors if r.level == RiskLevel.HIGH)
        if high_count >= 2:
            return RiskLevel.HIGH
        if high_count == 1:
            return RiskLevel.MEDIUM
        return RiskLevel.MEDIUM if len(risk_factors) >= 3 else RiskLevel.LOW

    @staticmethod
    def _data_quality_score(params: dict[str, Any]) -> float:
        """Score how much data we have (0-1). More data -> tighter CI."""
        fields_present = 0
        total_fields = 7
        if params.get("employees") is not None:
            fields_present += 1
        if params.get("ai_maturity") not in (None, "unknown", "none"):
            fields_present += 1
        if params.get("saas_maturity", 1) > 1:
            fields_present += 1
        if params.get("tech_stack"):
            fields_present += 1
        if params.get("revenue") is not None:
            fields_present += 1
        if params.get("growth_rate") is not None:
            fields_present += 1
        if params.get("funding") is not None:
            fields_present += 1
        return fields_present / total_fields


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ci(point: float, margin_pct: float) -> ConfidenceInterval:
    """Build a symmetric confidence interval."""
    delta = abs(point * margin_pct)
    return ConfidenceInterval(
        low=round(max(0.0, point - delta), 2),
        point=round(point, 2),
        high=round(point + delta, 2),
    )
