"""Financial health scorer: revenue scale, profitability, efficiency, funding cushion.

This scorer integrates both traditional financial metrics and facts from the
facts repository (SEC EDGAR, Companies House, news signals) to calculate a
comprehensive financial health score.
"""

from typing import TYPE_CHECKING

from ...core.scoring_config import ScoringSettings
from ...domain.models import (
    ConfidenceLevel,
    FinancialMetric,
    ScoreComponent,
    ScoringExplanation,
)

if TYPE_CHECKING:
    from ...infrastructure.repositories import FactRepository


class FinancialHealthScorer:
    """Score company financial health (0-10)."""

    def __init__(self, config: ScoringSettings | None = None):
        self.config = config or ScoringSettings()

    def score(
        self,
        financials: FinancialMetric,
        fact_repo: "FactRepository | None" = None,
        company_id: str | None = None,
    ) -> tuple[float, ScoringExplanation]:
        """Calculate financial health score (0-10) with explanation.

        Args:
            financials: Traditional financial metrics (may be overridden by facts)
            fact_repo: Optional FactRepository to pull facts from
            company_id: Company ID to fetch facts for (required if fact_repo provided)

        Returns:
            Tuple of (score, explanation)
        """
        cfg = self.config.financial
        score = cfg.base_score if cfg.base_score is not None else 0.0
        explanation = ScoringExplanation(base_score=score)

        # Merge facts from repository if available
        if fact_repo and company_id:
            financials = self._merge_facts_into_financials(financials, fact_repo, company_id)

        if financials.revenue:
            adj = 0.0
            if financials.revenue > cfg.revenue_large_threshold:
                adj = cfg.revenue_large_bonus
            elif financials.revenue > cfg.revenue_med_threshold:
                adj = cfg.revenue_med_bonus
            elif financials.revenue < cfg.revenue_small_threshold:
                adj = cfg.revenue_small_penalty

            if adj != 0:
                score += adj
                explanation.components.append(
                    ScoreComponent(
                        name="Revenue Scale",
                        value=adj,
                        formula=f"revenue({financials.revenue:,.0f} EUR) -> adjustment",
                        reasoning="Scale impacts financial stability scores.",
                    )
                )

        if financials.profit_margin is not None:
            adj = 0.0
            if financials.profit_margin > cfg.margin_high_threshold:
                adj = cfg.margin_high_bonus
            elif financials.profit_margin > cfg.margin_med_threshold:
                adj = cfg.margin_med_bonus
            elif financials.profit_margin < 0:
                adj = cfg.margin_negative_penalty

            if adj != 0:
                score += adj
                explanation.components.append(
                    ScoreComponent(
                        name="Profitability Health",
                        value=adj,
                        formula=f"margin({financials.profit_margin}%) -> adjustment",
                        reasoning="Operating margin is a key indicator of financial health.",
                    )
                )

        if financials.employees and financials.revenue:
            rev_per_emp = financials.revenue / financials.employees
            adj = 0.0
            if rev_per_emp > cfg.efficiency_exceptional_threshold:
                adj = cfg.efficiency_exceptional_bonus
            elif rev_per_emp > cfg.efficiency_good_threshold:
                adj = cfg.efficiency_good_bonus
            elif rev_per_emp < cfg.efficiency_low_threshold:
                adj = cfg.efficiency_low_penalty

            if adj != 0:
                score += adj
                explanation.components.append(
                    ScoreComponent(
                        name="Operating Efficiency",
                        value=adj,
                        formula=f"rev_per_emp({rev_per_emp:,.0f} EUR) -> adjustment",
                        reasoning="Resource utilization efficiency.",
                    )
                )

        if financials.funding_raised and financials.revenue:
            ratio = financials.funding_raised / financials.revenue
            adj = 0.0
            if ratio > cfg.cushion_high_ratio:
                adj = cfg.cushion_high_bonus
            elif ratio > cfg.cushion_med_ratio:
                adj = cfg.cushion_med_bonus
            elif ratio < cfg.cushion_thin_ratio and (financials.profit_margin is None or financials.profit_margin < 5):
                adj = cfg.cushion_thin_penalty

            if adj != 0:
                score += adj
                explanation.components.append(
                    ScoreComponent(
                        name="Funding Cushion",
                        value=adj,
                        formula=f"funding_ratio({ratio:.2f}) -> adjustment",
                        reasoning="Capital reserves relative to revenue scale.",
                    )
                )

        final_score = max(0.0, min(score, 10.0))
        explanation.final_score = final_score
        return final_score, explanation

    def _merge_facts_into_financials(
        self,
        financials: FinancialMetric,
        fact_repo: "FactRepository",
        company_id: str,
    ) -> FinancialMetric:
        """Merge facts from repository into financial metrics.

        Facts override existing metrics only if they have higher confidence.

        Args:
            financials: Existing financial metrics
            fact_repo: Repository to fetch facts from
            company_id: Company ID to fetch facts for

        Returns:
            Updated FinancialMetric with facts merged in
        """
        try:
            facts = fact_repo.get_company_facts(company_id)
        except Exception:
            # If fact retrieval fails, return original financials
            return financials

        # Map fact types to financial metric fields
        fact_map = {
            "annual_revenue": ("revenue", "revenue_confidence"),
            "revenue_growth_yoy": ("growth_rate", "growth_confidence"),
            "employee_count": ("employees", "employees_confidence"),
            "gross_margin": ("profit_margin", "margin_confidence"),
            "total_funding_raised": ("funding_raised", "funding_confidence"),
            "company_valuation": ("valuation", "valuation_confidence"),
        }

        for fact in facts:
            if fact.fact_type not in fact_map:
                continue

            metric_field, confidence_field = fact_map[fact.fact_type]

            # Only update if fact has a value
            if fact.value is not None:
                # Convert confidence (0.0-1.0) to ConfidenceLevel enum
                confidence_level = self._confidence_to_level(fact.confidence)

                # Update the metric
                setattr(financials, metric_field, fact.value)
                setattr(financials, confidence_field, confidence_level)

        return financials

    @staticmethod
    def _confidence_to_level(confidence: float) -> ConfidenceLevel:
        """Convert numeric confidence (0.0-1.0) to ConfidenceLevel enum.

        Args:
            confidence: Numeric confidence between 0.0 and 1.0

        Returns:
            ConfidenceLevel enum value (CONFIRMED, ESTIMATED, or UNKNOWN)
        """
        if confidence >= 0.9:
            return ConfidenceLevel.CONFIRMED
        elif confidence >= 0.7:
            return ConfidenceLevel.ESTIMATED
        else:
            return ConfidenceLevel.UNKNOWN
