"""Financial health scorer: revenue scale, profitability, efficiency, funding cushion."""

from ...core.scoring_config import ScoringSettings
from ...domain.models import (
    FinancialMetric,
    ScoreComponent,
    ScoringExplanation,
)


class FinancialHealthScorer:
    """Score company financial health (0-10)."""

    def __init__(self, config: ScoringSettings | None = None):
        self.config = config or ScoringSettings()

    def score(self, financials: FinancialMetric) -> tuple[float, ScoringExplanation]:
        """Calculate financial health score (0-10) with explanation."""
        cfg = self.config.financial
        score = cfg.base_score
        explanation = ScoringExplanation(base_score=score)

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
