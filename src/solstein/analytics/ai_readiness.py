"""AI Readiness Scoring Module (EPIC-038, STORY-145).

Evaluates how ready a company is to successfully adopt or expand AI use
across four dimensions:

- **Data Infrastructure**: data quality/availability, modern data stack, tooling
- **Technical Debt**: legacy vs. modern tech stack, API-first architecture
- **AI Literacy**: team AI/ML capabilities, hiring signals, AI maturity
- **Process Automation**: current automation level, SaaS maturity, production AI

The final AI Readiness Score (0-100) determines a qualitative tier:

- **AI-Ready** (>=75): Premium transformation target
- **AI-Capable** (>=50): Can transform with investment
- **AI-Challenged** (>=25): Significant barriers to transformation
- **AI-Resistant** (<25): Not a viable AI transformation candidate

The score can optionally influence the overall composite classification
via a configurable weight in ``AIReadinessConfig``.

Usage::

    from solstein.analytics.ai_readiness import AIReadinessScorer
    from solstein.domain.models import Company

    scorer = AIReadinessScorer()
    result = scorer.score(company)
    print(result.score, result.tier, result.breakdown)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from solstein.domain.models import Company

logger = logging.getLogger(__name__)


class AIReadinessTier(str, Enum):
    """Qualitative AI readiness classification."""

    AI_READY = "AI-Ready"
    AI_CAPABLE = "AI-Capable"
    AI_CHALLENGED = "AI-Challenged"
    AI_RESISTANT = "AI-Resistant"


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class AIReadinessConfig:
    """Tunable parameters for the AI readiness scorer.

    Attributes:
        data_infrastructure_weight: Weight for data infrastructure dimension.
        technical_debt_weight: Weight for technical debt dimension.
        ai_literacy_weight: Weight for AI literacy dimension.
        process_automation_weight: Weight for process automation dimension.
        classification_influence_weight: How much AI readiness affects the
            overall composite score (0.0 = no influence, 1.0 = full weight).
            Default 0.0 keeps backward-compatible behavior.
    """

    data_infrastructure_weight: float = 0.25
    technical_debt_weight: float = 0.25
    ai_literacy_weight: float = 0.30
    process_automation_weight: float = 0.20
    classification_influence_weight: float = 0.0

    def validate_weights(self) -> bool:
        """Check dimension weights sum to ~1.0."""
        total = (
            self.data_infrastructure_weight
            + self.technical_debt_weight
            + self.ai_literacy_weight
            + self.process_automation_weight
        )
        return 0.99 <= total <= 1.01


# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------

@dataclass
class AIReadinessResult:
    """Result from ``AIReadinessScorer.score()``.

    Attributes:
        score: Composite AI readiness score (0-100).
        tier: Qualitative tier enum value.
        breakdown: Per-dimension raw scores (0-100 each).
        insights: Human-readable findings per dimension.
    """

    score: float
    tier: AIReadinessTier
    breakdown: dict[str, float] = field(default_factory=dict)
    insights: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Scorer
# ---------------------------------------------------------------------------

# AI maturity level -> base AI literacy score (0-100)
_MATURITY_TO_LITERACY: dict[str, float] = {
    "exceptional": 95.0,
    "very strong": 90.0,
    "strong": 80.0,
    "advanced": 70.0,
    "emerging": 45.0,
    "none": 10.0,
    "unknown": 25.0,
}


class AIReadinessScorer:
    """Score a company's AI readiness across four dimensions.

    Dimensions:
        1. Data Infrastructure (25%): data quality, modern stack, tooling
        2. Technical Debt (25%): legacy burden, API readiness, stack modernity
        3. AI Literacy (30%): team AI capabilities, hiring, maturity level
        4. Process Automation (20%): SaaS maturity, production AI, automation

    Each dimension produces a score from 0-100. The weighted composite
    determines the final score and tier classification.
    """

    def __init__(self, config: AIReadinessConfig | None = None) -> None:
        self.config = config or AIReadinessConfig()

    def score(self, company: Company) -> AIReadinessResult:
        """Compute the AI readiness score for *company*.

        Args:
            company: Fully-populated Company domain object.

        Returns:
            AIReadinessResult with score (0-100), tier, breakdown, and insights.
        """
        data_infra = self._score_data_infrastructure(company)
        tech_debt = self._score_technical_debt(company)
        ai_literacy = self._score_ai_literacy(company)
        process_auto = self._score_process_automation(company)

        cfg = self.config
        weighted = (
            data_infra * cfg.data_infrastructure_weight
            + tech_debt * cfg.technical_debt_weight
            + ai_literacy * cfg.ai_literacy_weight
            + process_auto * cfg.process_automation_weight
        )
        final = round(min(100.0, max(0.0, weighted)), 2)

        tier = self._classify(final)
        insights = self._build_insights(
            company, data_infra, tech_debt, ai_literacy, process_auto
        )

        logger.debug(
            "AI readiness for %s: %.1f (%s) — data=%.1f tech=%.1f lit=%.1f auto=%.1f",
            getattr(company, "name", "unknown"),
            final,
            tier.value,
            data_infra,
            tech_debt,
            ai_literacy,
            process_auto,
        )

        return AIReadinessResult(
            score=final,
            tier=tier,
            breakdown={
                "data_infrastructure": round(data_infra, 2),
                "technical_debt": round(tech_debt, 2),
                "ai_literacy": round(ai_literacy, 2),
                "process_automation": round(process_auto, 2),
            },
            insights=insights,
        )

    # ------------------------------------------------------------------
    # Dimension scorers (each returns 0-100)
    # ------------------------------------------------------------------

    def _score_data_infrastructure(self, c: Company) -> float:
        """Score data infrastructure quality and availability (0-100).

        Signals: SaaS maturity (modern data stack), employee count
        (data team capacity), growth rate (infrastructure investment),
        data_availability flag.
        """
        score = 30.0  # neutral baseline

        # SaaS maturity correlates with modern data stack
        saas: int = getattr(c, "saas_maturity", 0) or 0
        score += saas * 3.0  # max +30 from SaaS maturity (0-10 scale)

        # Larger companies more likely to have dedicated data teams
        employees: int = 0
        financials = getattr(c, "financials", None)
        if financials is not None:
            employees = getattr(financials, "employees", 0) or 0
        if employees > 500:
            score += 15.0
        elif employees > 100:
            score += 10.0
        elif employees > 20:
            score += 5.0

        # Growth signals infrastructure investment
        if financials and getattr(financials, "growth_rate", None):
            if financials.growth_rate > 30:
                score += 10.0
            elif financials.growth_rate > 10:
                score += 5.0

        # Data availability flag
        data_avail: str | None = getattr(c, "data_availability", None)
        if data_avail and data_avail.lower() in ("high", "extensive"):
            score += 10.0
        elif data_avail and data_avail.lower() in ("medium", "moderate"):
            score += 5.0

        return min(100.0, max(0.0, score))

    def _score_technical_debt(self, c: Company) -> float:
        """Score technical modernity / low technical debt (0-100).

        Higher score = less technical debt = better positioned for AI.
        Signals: tech stack diversity, SaaS maturity, founding year,
        recent funding (implies modernization).
        """
        score = 40.0  # neutral — assume average

        # Modern tech stack signals low debt
        tech_stack: list[str] = getattr(c, "tech_stack", []) or []
        modern_indicators = {
            "python", "kubernetes", "docker", "react", "typescript",
            "graphql", "terraform", "aws", "gcp", "azure", "kafka",
            "spark", "airflow", "dbt", "snowflake", "databricks",
        }
        modern_count = sum(
            1 for t in tech_stack
            if t.lower() in modern_indicators
        )
        if modern_count >= 5:
            score += 25.0
        elif modern_count >= 3:
            score += 15.0
        elif modern_count >= 1:
            score += 5.0

        # Legacy indicators (negative signals)
        legacy_indicators = {
            "cobol", "fortran", "delphi", "vb6", "classic asp",
            "mainframe", "foxpro",
        }
        legacy_count = sum(
            1 for t in tech_stack
            if t.lower() in legacy_indicators
        )
        score -= legacy_count * 10.0

        # SaaS maturity as proxy for cloud-native architecture
        saas: int = getattr(c, "saas_maturity", 0) or 0
        if saas >= 8:
            score += 15.0
        elif saas >= 5:
            score += 10.0

        # Recent significant funding implies modernization investment
        funding: float = getattr(c, "total_funding_raised_eur", 0.0) or 0.0
        if funding > 50_000_000:
            score += 10.0
        elif funding > 10_000_000:
            score += 5.0

        return min(100.0, max(0.0, score))

    def _score_ai_literacy(self, c: Company) -> float:
        """Score team AI/ML capabilities and hiring signals (0-100).

        Signals: ai_maturity enum, ai_score (0-10), ai_in_production,
        ai_key_capabilities, ai_signal_level, open AI/ML positions.
        """
        # Start from ai_maturity enum mapping
        maturity = getattr(c, "ai_maturity", None)
        if maturity is not None:
            key = (
                maturity.value.lower()
                if hasattr(maturity, "value")
                else str(maturity).lower()
            )
            base = _MATURITY_TO_LITERACY.get(key, _MATURITY_TO_LITERACY["unknown"])
        else:
            base = _MATURITY_TO_LITERACY["unknown"]

        score = base

        # ai_score (0-10) as supplementary signal
        ai_score_raw: float = getattr(c, "ai_score", 0.0) or 0.0
        score = (score + ai_score_raw * 10.0) / 2.0  # average with ai_score scaled to 0-100

        # Bonus for production AI deployment
        in_production: bool = getattr(c, "ai_in_production", False) or False
        if in_production:
            score += 15.0

        # AI key capabilities text
        capabilities: str | None = getattr(c, "ai_key_capabilities", None)
        if capabilities and len(capabilities) > 20:
            score += 5.0  # has documented AI capabilities

        # AI signal level
        signal_level: str | None = getattr(c, "ai_signal_level", None)
        if signal_level and signal_level.lower() in ("high", "very high"):
            score += 10.0
        elif signal_level and signal_level.lower() == "medium":
            score += 5.0

        return min(100.0, max(0.0, score))

    def _score_process_automation(self, c: Company) -> float:
        """Score current process automation level (0-100).

        Signals: SaaS maturity, ai_in_production, tech stack (CI/CD,
        orchestration tools), employee efficiency (high rev/employee
        suggests automation).
        """
        score = 20.0  # baseline

        # SaaS maturity is a strong automation proxy
        saas: int = getattr(c, "saas_maturity", 0) or 0
        score += saas * 4.0  # max +40

        # Production AI is a strong automation signal
        in_production: bool = getattr(c, "ai_in_production", False) or False
        if in_production:
            score += 15.0

        # Tech stack automation indicators
        tech_stack: list[str] = getattr(c, "tech_stack", []) or []
        automation_indicators = {
            "airflow", "prefect", "dagster", "jenkins", "github actions",
            "terraform", "ansible", "puppet", "chef", "kubernetes",
            "argo", "mlflow", "kubeflow", "sagemaker",
        }
        auto_count = sum(
            1 for t in tech_stack
            if t.lower() in automation_indicators
        )
        score += min(auto_count * 5.0, 15.0)

        # Revenue per employee as efficiency/automation proxy
        employees: int = 0
        revenue: float = 0.0
        financials = getattr(c, "financials", None)
        if financials is not None:
            employees = getattr(financials, "employees", 0) or 0
            revenue = getattr(financials, "revenue", 0.0) or 0.0
        if employees > 0 and revenue > 0:
            rev_per_emp = (revenue * 1_000_000) / employees  # revenue in millions
            if rev_per_emp > 500_000:
                score += 10.0
            elif rev_per_emp > 200_000:
                score += 5.0

        return min(100.0, max(0.0, score))

    # ------------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------------

    @staticmethod
    def _classify(score: float) -> AIReadinessTier:
        """Map score (0-100) to qualitative tier."""
        if score >= 75.0:
            return AIReadinessTier.AI_READY
        elif score >= 50.0:
            return AIReadinessTier.AI_CAPABLE
        elif score >= 25.0:
            return AIReadinessTier.AI_CHALLENGED
        else:
            return AIReadinessTier.AI_RESISTANT

    # ------------------------------------------------------------------
    # Insights
    # ------------------------------------------------------------------

    def _build_insights(
        self,
        _company: Company,
        data_infra: float,
        tech_debt: float,
        ai_literacy: float,
        process_auto: float,
    ) -> list[str]:
        """Generate human-readable insights from dimension scores."""
        insights: list[str] = []

        # Data Infrastructure
        if data_infra < 30.0:
            insights.append(
                "Critical data infrastructure gaps — invest in data quality, "
                "storage, and modern tooling before attempting AI adoption."
            )
        elif data_infra < 50.0:
            insights.append(
                "Data infrastructure needs improvement — consider cloud "
                "migration and data cataloging."
            )
        elif data_infra >= 75.0:
            insights.append(
                "Strong data infrastructure — well-positioned to support "
                "AI/ML workloads."
            )

        # Technical Debt
        if tech_debt < 30.0:
            insights.append(
                "High technical debt — legacy systems will impede AI adoption. "
                "Modernization is a prerequisite."
            )
        elif tech_debt < 50.0:
            insights.append(
                "Moderate technical debt — targeted modernization recommended "
                "before AI transformation."
            )
        elif tech_debt >= 75.0:
            insights.append(
                "Modern tech stack with low technical debt — minimal barriers "
                "to AI integration."
            )

        # AI Literacy
        if ai_literacy < 30.0:
            insights.append(
                "Low AI literacy — no evidence of AI capabilities or hiring. "
                "Significant upskilling and recruitment required."
            )
        elif ai_literacy < 50.0:
            insights.append(
                "Emerging AI awareness — team has basic understanding but "
                "lacks production AI experience."
            )
        elif ai_literacy >= 75.0:
            insights.append(
                "High AI literacy — team has production AI experience and "
                "active AI capabilities."
            )

        # Process Automation
        if process_auto < 30.0:
            insights.append(
                "Minimal process automation — manual processes dominate. "
                "Start with basic automation before AI."
            )
        elif process_auto < 50.0:
            insights.append(
                "Partial automation — some processes automated but significant "
                "manual work remains."
            )
        elif process_auto >= 75.0:
            insights.append(
                "High automation maturity — strong foundation for AI-powered "
                "process enhancement."
            )

        if not insights:
            insights.append(
                "Moderate AI readiness across all dimensions — targeted "
                "investment can unlock transformation potential."
            )

        return insights
