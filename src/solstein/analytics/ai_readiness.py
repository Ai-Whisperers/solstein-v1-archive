"""AI Readiness Scoring Module (EPIC-038).

Evaluates how ready a company is to successfully adopt or expand AI use
across three dimensions:
- **Deployment Maturity**: current AI use, production deployments, patents
- **Data Infrastructure**: data quality, data science team, tooling
- **Strategic Alignment**: leadership buy-in, AI roadmap, investment signals

The final AI Readiness Score (0–10) is stored alongside the composite score.

Usage::

    from solstein.analytics.ai_readiness import AIReadinessScorer
    from solstein.domain.models import Company

    scorer = AIReadinessScorer()
    result = scorer.score(company)
    print(result.score, result.tier, result.breakdown)
"""

from __future__ import annotations

from dataclasses import dataclass, field

from solstein.domain.models import Company

# Weights for each dimension
_WEIGHTS = {
    "deployment_maturity": 0.40,
    "data_infrastructure": 0.35,
    "strategic_alignment": 0.25,
}

# AI maturity level → base deployment score
_MATURITY_TO_SCORE: dict[str, float] = {
    "exceptional": 9.5,
    "very strong": 9.0,
    "strong": 8.0,
    "advanced": 7.5,
    "emerging": 5.0,
    "none": 1.0,
    "unknown": 3.0,
}


@dataclass
class AIReadinessResult:
    """Result from ``AIReadinessScorer.score()``.

    Attributes:
        score: Composite AI readiness score (0–10).
        tier: Qualitative tier (``'Leader'``, ``'Adopter'``, ``'Laggard'``).
        breakdown: Per-dimension raw scores (0–10 each).
        insights: Human-readable findings per dimension.
    """

    score: float
    tier: str
    breakdown: dict[str, float] = field(default_factory=dict)
    insights: list[str] = field(default_factory=list)


class AIReadinessScorer:
    """Score a company's AI readiness across deployment, data, and strategy."""

    def score(self, company: Company) -> AIReadinessResult:
        """Compute the AI readiness score for *company*.

        Args:
            company: Fully-populated Company domain object.

        Returns:
            AIReadinessResult with score, tier, breakdown, and insights.
        """
        deployment = self._deployment_maturity(company)
        data_infra = self._data_infrastructure(company)
        strategic = self._strategic_alignment(company)

        weighted = (
            deployment * _WEIGHTS["deployment_maturity"]
            + data_infra * _WEIGHTS["data_infrastructure"]
            + strategic * _WEIGHTS["strategic_alignment"]
        )
        final = round(min(10.0, max(0.0, weighted)), 2)

        tier = self._classify(final)
        insights = self._build_insights(company, deployment, data_infra, strategic)

        return AIReadinessResult(
            score=final,
            tier=tier,
            breakdown={
                "deployment_maturity": round(deployment, 2),
                "data_infrastructure": round(data_infra, 2),
                "strategic_alignment": round(strategic, 2),
            },
            insights=insights,
        )

    # ------------------------------------------------------------------
    # Dimension scorers
    # ------------------------------------------------------------------

    def _deployment_maturity(self, c: Company) -> float:
        """Score current AI deployment status (0–10)."""
        ai_score: float = getattr(c, "ai_score", 0.0) or 0.0

        # Map from AIMaturity enum if available
        maturity = getattr(c, "ai_maturity", None)
        if maturity is not None:
            key = maturity.value.lower() if hasattr(maturity, "value") else str(maturity).lower()
            base = _MATURITY_TO_SCORE.get(key, _MATURITY_TO_SCORE["unknown"])
        else:
            # Fall back to ai_score (0–10 scale already)
            base = ai_score

        # Bonus for production AI
        in_production: bool = getattr(c, "ai_in_production", False) or False
        bonus = 1.0 if in_production else 0.0

        return min(10.0, base + bonus)

    def _data_infrastructure(self, c: Company) -> float:
        """Score data infrastructure readiness (0–10)."""
        score = 5.0  # neutral baseline

        # SaaS maturity correlates with modern data stack
        saas: float = getattr(c, "saas_maturity", 0.0) or 0.0
        score += saas * 0.3  # max +3.0 from SaaS maturity

        # Large company → more likely to have data team
        employees: int = getattr(c, "employees", 0) or 0
        if employees > 500:
            score += 1.0
        elif employees > 100:
            score += 0.5

        # High growth → investing in infrastructure
        growth = getattr(c, "financials", None)
        if growth and getattr(growth, "growth_rate", 0.0):
            if growth.growth_rate > 20:
                score += 1.0

        return min(10.0, max(0.0, score))

    def _strategic_alignment(self, c: Company) -> float:
        """Score strategic AI alignment (0–10)."""
        score = 3.0  # baseline — companies rarely have no AI strategy

        # Funding signals strategic investment capacity
        funding: float = getattr(c, "total_funding_raised_eur", 0.0) or 0.0
        if funding > 100_000_000:  # > 100M EUR
            score += 2.5
        elif funding > 10_000_000:  # > 10M EUR
            score += 1.5
        elif funding > 1_000_000:  # > 1M EUR
            score += 0.5

        # Phoenix tier companies have the resources and motivation
        tier = getattr(c, "tier", None)
        if tier is not None:
            tier_str = tier.value.lower() if hasattr(tier, "value") else str(tier).lower()
            if tier_str == "phoenix":
                score += 2.0
            elif tier_str == "salt":
                score += 1.0

        return min(10.0, max(0.0, score))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _classify(self, score: float) -> str:
        if score >= 7.5:
            return "Leader"
        elif score >= 4.5:
            return "Adopter"
        else:
            return "Laggard"

    def _build_insights(
        self,
        c: Company,
        deployment: float,
        data_infra: float,
        strategic: float,
    ) -> list[str]:
        insights: list[str] = []
        if deployment < 4.0:
            insights.append("Low AI deployment maturity — consider piloting AI in a non-critical process.")
        elif deployment >= 8.0:
            insights.append("Strong AI deployment — well-positioned to scale existing AI investments.")

        if data_infra < 4.0:
            insights.append("Data infrastructure gaps detected — invest in data quality and tooling.")
        if strategic < 4.0:
            insights.append("Limited strategic AI signals — leadership buy-in may be lacking.")
        elif strategic >= 7.0:
            insights.append("High strategic alignment — AI is embedded in the company roadmap.")

        return insights or ["Moderate AI readiness across all dimensions."]
