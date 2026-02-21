"""Growth momentum scorer: revenue growth, employee efficiency, funding momentum."""

from solstein.domain.models import FinancialMetric, ScoreComponent, ScoringExplanation
from solstein.core.scoring_config import ScoringSettings


class GrowthMomentumScorer:
    """Score company growth momentum (revenue growth, employee efficiency, funding)."""

    def __init__(self, config: ScoringSettings | None = None):
        self.config = config or ScoringSettings()

    def score(self, financials: FinancialMetric) -> tuple[float, ScoringExplanation]:
        """Calculate growth momentum score (0-10) with explanation."""
        cfg = self.config.growth
        score = cfg.base_score
        explanation = ScoringExplanation(base_score=score)

        if financials.growth_rate is not None:
            growth_factor = min(
                financials.growth_rate / cfg.revenue_growth_divisor,
                cfg.revenue_growth_cap,
            )
            score += growth_factor
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

        final_score = max(0.0, min(score, 10.0))
        explanation.final_score = final_score
        return final_score, explanation
