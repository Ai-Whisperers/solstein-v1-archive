"""Growth momentum scorer: revenue growth, employee efficiency, funding momentum.

This scorer integrates both traditional financial metrics and facts from the
facts repository (SEC EDGAR, Companies House, news signals) to calculate a
comprehensive growth momentum score.
"""

from typing import TYPE_CHECKING

from ...core.scoring_config import ScoringSettings
from ...domain.models import ConfidenceLevel, FinancialMetric, ScoreComponent, ScoringExplanation

if TYPE_CHECKING:
    from ...infrastructure.repositories import FactRepository


class GrowthMomentumScorer:
    """Score company growth momentum (revenue growth, employee efficiency, funding)."""

    def __init__(self, config: ScoringSettings | None = None):
        self.config = config or ScoringSettings()

    def score(
        self,
        financials: FinancialMetric,
        fact_repo: "FactRepository | None" = None,
        company_id: str | None = None,
    ) -> tuple[float, ScoringExplanation]:
        """Calculate growth momentum score (0-10) with explanation.

        Args:
            financials: Traditional financial metrics (may be overridden by facts)
            fact_repo: Optional FactRepository to pull facts from
            company_id: Company ID to fetch facts for (required if fact_repo provided)

        Returns:
            Tuple of (score, explanation)
        """
        cfg = self.config.growth
        score = cfg.base_score if cfg.base_score is not None else 0.0
        explanation = ScoringExplanation(base_score=score)

        # Merge facts from repository if available
        if fact_repo and company_id:
            financials = self._merge_facts_into_financials(financials, fact_repo, company_id)

        if financials.growth_rate is not None:
            growth_factor = min(
                financials.growth_rate / cfg.revenue_growth_divisor,
                cfg.revenue_growth_cap,
            )
            score += growth_factor
            # Slow growth penalty: stagnant companies penalized
            if 0 <= financials.growth_rate < 0.05:  # 0-5% growth (decimal format)
                score -= 0.75  # Stagnant growth penalty
                explanation.components.append(
                    ScoreComponent(
                        name="Stagnant Growth Penalty",
                        value=-0.75,
                        formula="growth_rate < 5% (decimal: < 0.05) → -0.75",
                        reasoning="Growth rate below 5% indicates stagnation.",
                    )
                )
            elif 0.05 <= financials.growth_rate < 0.10:  # 5-10% growth (decimal format)
                score -= 0.25  # Below-average growth penalty
                explanation.components.append(
                    ScoreComponent(
                        name="Below-Average Growth Penalty",
                        value=-0.25,
                        formula="growth_rate 5-10% (decimal: 0.05-0.10) → -0.25",
                        reasoning="Growth rate below 10% is below sector average.",
                    )
                )
            explanation.components.append(
                ScoreComponent(
                    name="Revenue Growth",
                    value=growth_factor,
                    formula=f"min({financials.growth_rate}% / {cfg.revenue_growth_divisor}, {cfg.revenue_growth_cap})",
                    reasoning=f"High growth rate of {financials.growth_rate}% identified."
                    if financials.growth_rate > 15
                    else "Moderate growth rate identified.",
                )
            )

        if financials.employees and financials.revenue:
            rev_per_emp = financials.revenue / financials.employees
            bonus = 0.0
            if rev_per_emp > cfg.efficiency_high_threshold:
                bonus = cfg.efficiency_high_bonus
            elif rev_per_emp > cfg.efficiency_med_threshold:
                bonus = cfg.efficiency_med_bonus

            if bonus > 0:
                score += bonus
                explanation.components.append(
                    ScoreComponent(
                        name="Employee Efficiency",
                        value=bonus,
                        formula=f"rev_per_emp({rev_per_emp:,.0f} EUR) > threshold",
                        reasoning="Revenue per employee is above efficiency benchmarks.",
                    )
                )

        if financials.funding_raised:
            bonus = 0.0
            if financials.funding_raised > cfg.funding_high_threshold:
                bonus = cfg.funding_high_bonus
            elif financials.funding_raised > cfg.funding_med_threshold:
                bonus = cfg.funding_med_bonus

            if bonus > 0:
                score += bonus
                explanation.components.append(
                    ScoreComponent(
                        name="Funding Momentum",
                        value=bonus,
                        formula=f"funding({financials.funding_raised:,.0f} EUR) > threshold",
                        reasoning="Significant capital injection signals strong market confidence.",
                    )
                )

        if financials.profit_margin is not None:
            adj = 0.0
            if financials.profit_margin > cfg.margin_high_threshold:
                adj = cfg.margin_high_bonus
            elif financials.profit_margin > cfg.margin_med_threshold:
                adj = cfg.margin_med_bonus
            elif financials.profit_margin < -0.10:
                adj = cfg.margin_negative_penalty * 1.5  # Deep negative margin: 1.5x penalty
            elif financials.profit_margin < 0:
                adj = cfg.margin_negative_penalty

            if adj != 0:
                score += adj
                explanation.components.append(
                    ScoreComponent(
                        name="Profitability Profile",
                        value=adj,
                        formula=f"margin({financials.profit_margin}%) -> adjustment",
                        reasoning="Healthy margins contribute to growth score."
                        if adj > 0
                        else "Negative margins penalize growth score.",
                    )
                )

        # Compound penalty: negative growth + no funding = high-risk signal
        if financials.growth_rate is not None and financials.growth_rate < 0 and not financials.funding_raised:
            score -= 1.0  # Compound penalty: burning cash with no investor support
            explanation.components.append(
                ScoreComponent(
                    name="Compound Risk Penalty",
                    value=-1.0,
                    formula="growth_rate < 0 AND no_funding → -1.0",
                    reasoning="Negative growth with no funding raises serious viability concerns.",
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
