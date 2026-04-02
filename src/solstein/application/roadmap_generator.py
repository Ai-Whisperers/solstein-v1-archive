"""AI Transformation Roadmap Generator (STORY-148, EPIC-038).

Generates a phased transformation roadmap customised to a company's
starting point, industry, and AI-readiness signals. Designed for PE
portfolio value creation: "what to do in months 1-6, 6-12, 12-24".

Four phases:
1. **Foundation** — data infrastructure, team training, governance
2. **Quick Wins** — high-impact, low-effort automations
3. **Transformation** — core process AI integration
4. **Optimization** — advanced AI, predictive analytics

Usage::

    from solstein.application.roadmap_generator import RoadmapGenerator
    generator = RoadmapGenerator()
    roadmap = generator.generate(company)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from loguru import logger

if TYPE_CHECKING:
    from solstein.domain.models import Company


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Initiative:
    """A single initiative within a roadmap phase."""

    name: str
    description: str
    timeline_months: str  # e.g. "1-3", "4-6"
    effort: str  # "low", "medium", "high"
    impact: str  # "low", "medium", "high"
    resources: str  # e.g. "2 ML engineers, 1 data engineer"
    success_metric: str
    priority: int = 1  # 1 = highest


@dataclass
class Phase:
    """A transformation phase containing multiple initiatives."""

    name: str
    description: str
    start_month: int
    end_month: int
    initiatives: list[Initiative] = field(default_factory=list)
    total_budget_eur: float = 0.0
    key_milestone: str = ""


@dataclass
class TransformationRoadmap:
    """Complete transformation roadmap output."""

    company_name: str
    industry: str
    phases: list[Phase] = field(default_factory=list)
    total_duration_months: int = 24
    total_investment_eur: float = 0.0
    executive_summary: str = ""
    customisations_applied: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Industry patterns
# ---------------------------------------------------------------------------

_ENERGY_QUICK_WINS = [
    Initiative(
        "Predictive maintenance alerting",
        "Deploy ML models on equipment sensor data to predict failures",
        "4-6",
        "medium",
        "high",
        "1 ML engineer, 1 domain expert",
        "30% reduction in unplanned downtime",
    ),
    Initiative(
        "Automated regulatory compliance checking",
        "NLP-based scanning of regulatory updates against company policies",
        "4-6",
        "medium",
        "high",
        "1 NLP engineer, 1 compliance analyst",
        "80% of regulatory changes auto-flagged",
    ),
]

_ENERGY_TRANSFORMATION = [
    Initiative(
        "Grid optimisation AI",
        "Real-time demand/supply balancing using reinforcement learning",
        "7-12",
        "high",
        "high",
        "2 ML engineers, 1 grid specialist",
        "15% improvement in grid efficiency",
    ),
    Initiative(
        "Energy trading signal generation",
        "ML-powered price prediction for energy trading",
        "7-12",
        "high",
        "high",
        "2 quant engineers, 1 trader",
        "Measurable alpha in trading decisions",
    ),
]

_FINTECH_QUICK_WINS = [
    Initiative(
        "Fraud detection enhancement",
        "Add ML layer to existing rule-based fraud detection",
        "4-6",
        "medium",
        "high",
        "1 ML engineer, 1 fraud analyst",
        "40% more fraud detected, 20% fewer false positives",
    ),
    Initiative(
        "Customer churn prediction",
        "Predict at-risk customers using transaction patterns",
        "4-6",
        "medium",
        "medium",
        "1 data scientist, 1 product manager",
        "25% improvement in retention intervention success",
    ),
]

_FINTECH_TRANSFORMATION = [
    Initiative(
        "AI-powered credit scoring",
        "Replace legacy credit models with ML-based scoring",
        "7-12",
        "high",
        "high",
        "2 ML engineers, 1 risk manager",
        "15% improvement in default prediction accuracy",
    ),
]

_GENERIC_QUICK_WINS = [
    Initiative(
        "Document processing automation",
        "OCR + NLP pipeline for invoice/contract processing",
        "4-6",
        "medium",
        "high",
        "1 ML engineer, 1 ops lead",
        "60% reduction in manual document handling",
    ),
    Initiative(
        "Customer support AI assistant",
        "Deploy LLM-powered support chatbot for tier-1 queries",
        "4-6",
        "low",
        "medium",
        "1 engineer, 1 support lead",
        "40% of tier-1 queries resolved without human",
    ),
]

_GENERIC_TRANSFORMATION = [
    Initiative(
        "Core process AI integration",
        "Embed ML into primary business workflow",
        "7-12",
        "high",
        "high",
        "2 ML engineers, 1 process owner",
        "20% efficiency improvement in core process",
    ),
]


# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------


class RoadmapGenerator:
    """Generate phased AI transformation roadmaps from company signals."""

    def generate(
        self,
        company: Company,
        customisations: dict[str, Any] | None = None,
    ) -> TransformationRoadmap:
        """Generate a transformation roadmap for *company*.

        Args:
            company: Target company.
            customisations: Optional overrides (e.g. focus_areas, budget_cap).

        Returns:
            TransformationRoadmap with 4 phases.
        """
        logger.info("[Roadmap] Generating for {}", company.name)
        params = self._extract_params(company)
        industry = params["industry"]
        custom = customisations or {}

        phases = [
            self._foundation_phase(params, custom),
            self._quick_wins_phase(params, industry, custom),
            self._transformation_phase(params, industry, custom),
            self._optimisation_phase(params, custom),
        ]

        total_investment = sum(p.total_budget_eur for p in phases)
        duration = phases[-1].end_month

        applied = []
        if custom:
            applied.append(f"Custom overrides: {', '.join(custom.keys())}")
        applied.append(f"Industry pattern: {industry}")

        roadmap = TransformationRoadmap(
            company_name=company.name,
            industry=industry,
            phases=phases,
            total_duration_months=duration,
            total_investment_eur=total_investment,
            executive_summary=self._build_summary(company.name, phases, total_investment, duration),
            customisations_applied=applied,
            metadata={"ai_maturity": params["ai_maturity"], "saas_maturity": params["saas_maturity"]},
        )
        logger.info("[Roadmap] Generated {} phases for {}", len(phases), company.name)
        return roadmap

    # -- parameter extraction -----------------------------------------------

    @staticmethod
    def _extract_params(company: Company) -> dict[str, Any]:
        """Extract relevant company signals."""
        employees: int | None = None
        if company.financials is not None:
            employees = getattr(company.financials, "employees", None)

        industry_raw = getattr(company, "industry", "Energy Software").lower()
        if "energy" in industry_raw or "power" in industry_raw or "grid" in industry_raw:
            industry = "energy"
        elif "fintech" in industry_raw or "finance" in industry_raw or "banking" in industry_raw:
            industry = "fintech"
        else:
            industry = "generic"

        return {
            "employees": employees or 100,
            "ai_maturity": str(getattr(company, "ai_maturity", "None")).lower(),
            "saas_maturity": getattr(company, "saas_maturity", 1),
            "tech_stack": [s.lower() for s in getattr(company, "tech_stack", [])],
            "industry": industry,
            "revenue": company.revenue,
        }

    # -- phase builders -----------------------------------------------------

    @staticmethod
    def _foundation_phase(params: dict[str, Any], custom: dict[str, Any]) -> Phase:
        """Phase 1: Foundation — data infrastructure, governance, training."""
        saas = params.get("saas_maturity", 1)
        ai_mat = params.get("ai_maturity", "none")

        initiatives = [
            Initiative(
                "Data platform assessment and setup",
                "Audit existing data infrastructure, implement data lake/warehouse",
                "1-3",
                "high" if saas <= 3 else "medium",
                "high",
                "1 data architect, 1 DevOps engineer",
                "Unified data platform operational",
            ),
            Initiative(
                "AI/ML team formation",
                "Hire or train core AI team, establish ML engineering practices",
                "1-3",
                "high" if ai_mat in ("none", "low") else "medium",
                "high",
                "HR + 1 AI lead hire",
                "Core AI team of 2-3 engineers operational",
            ),
            Initiative(
                "Data governance framework",
                "Establish data quality standards, access controls, lineage tracking",
                "2-4",
                "medium",
                "medium",
                "1 data steward, 1 compliance lead",
                "Data governance policy documented and enforced",
            ),
        ]

        budget = custom.get("foundation_budget", 150_000 if saas > 5 else 300_000)
        return Phase(
            name="Foundation",
            description="Establish data infrastructure, team, and governance",
            start_month=1,
            end_month=4,
            initiatives=initiatives,
            total_budget_eur=budget,
            key_milestone="Data platform and core AI team operational",
        )

    @staticmethod
    def _quick_wins_phase(
        params: dict[str, Any],
        industry: str,
        custom: dict[str, Any],
    ) -> Phase:
        """Phase 2: Quick Wins — high-impact, low-effort automations."""
        if industry == "energy":
            initiatives = list(_ENERGY_QUICK_WINS)
        elif industry == "fintech":
            initiatives = list(_FINTECH_QUICK_WINS)
        else:
            initiatives = list(_GENERIC_QUICK_WINS)

        budget = custom.get("quick_wins_budget", 200_000)
        return Phase(
            name="Quick Wins",
            description="Deploy high-impact, low-effort AI automations",
            start_month=4,
            end_month=7,
            initiatives=initiatives,
            total_budget_eur=budget,
            key_milestone="First AI system in production",
        )

    @staticmethod
    def _transformation_phase(
        params: dict[str, Any],
        industry: str,
        custom: dict[str, Any],
    ) -> Phase:
        """Phase 3: Transformation — core process AI integration."""
        if industry == "energy":
            initiatives = list(_ENERGY_TRANSFORMATION)
        elif industry == "fintech":
            initiatives = list(_FINTECH_TRANSFORMATION)
        else:
            initiatives = list(_GENERIC_TRANSFORMATION)

        budget = custom.get("transformation_budget", 500_000)
        return Phase(
            name="Transformation",
            description="Integrate AI into core business processes",
            start_month=7,
            end_month=14,
            initiatives=initiatives,
            total_budget_eur=budget,
            key_milestone="AI embedded in primary revenue-generating process",
        )

    @staticmethod
    def _optimisation_phase(params: dict[str, Any], custom: dict[str, Any]) -> Phase:
        """Phase 4: Optimisation — advanced AI and predictive analytics."""
        initiatives = [
            Initiative(
                "Advanced analytics platform",
                "Deploy real-time analytics with ML-powered anomaly detection",
                "14-18",
                "high",
                "high",
                "2 ML engineers, 1 analytics lead",
                "Real-time dashboards with predictive insights operational",
            ),
            Initiative(
                "AI strategy review and scale-up",
                "Review transformation outcomes, plan next-generation AI initiatives",
                "18-24",
                "medium",
                "medium",
                "CTO + AI lead",
                "AI roadmap v2 published with measurable ROI from v1",
            ),
        ]

        budget = custom.get("optimisation_budget", 350_000)
        return Phase(
            name="Optimisation",
            description="Advanced AI capabilities and continuous improvement",
            start_month=14,
            end_month=24,
            initiatives=initiatives,
            total_budget_eur=budget,
            key_milestone="AI driving measurable business KPI improvements",
        )

    # -- helpers ------------------------------------------------------------

    @staticmethod
    def _build_summary(
        name: str,
        phases: list[Phase],
        total: float,
        duration: int,
    ) -> str:
        """Build an executive summary paragraph."""
        phase_names = ", ".join(p.name for p in phases)
        return (
            f"Transformation roadmap for {name}: {len(phases)} phases "
            f"({phase_names}) over {duration} months with estimated total "
            f"investment of EUR {total:,.0f}. Each phase builds on the "
            f"previous, progressing from infrastructure setup through "
            f"quick wins to full AI integration and optimisation."
        )
