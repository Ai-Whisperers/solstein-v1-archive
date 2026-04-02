from __future__ import annotations

from typing import TYPE_CHECKING, Any

from loguru import logger

from ...core.math_utils import safe_div
from ...core.scoring_config import ScoringSettings
from ...domain.models import FinancialMetric, ScoreComponent, ScoringExplanation

if TYPE_CHECKING:
    from ...infrastructure.repositories import FactRepository
from ._shared import calculate_data_confidence, merge_facts_into_financials

_STAGNANT_GROWTH_UPPER: float = 5.0
_BELOW_AVERAGE_GROWTH_UPPER: float = 10.0
_HYPER_GROWTH_THRESHOLD: float = 50.0
_STAGNANT_GROWTH_PENALTY: float = -0.75
_BELOW_AVERAGE_GROWTH_PENALTY: float = -0.25
_HYPER_GROWTH_BONUS: float = 2.5
_COMPOUND_RISK_PENALTY: float = -1.0
_UNKNOWN_DATA_PENALTY: float = -1.0  # Penalty when data is unknown
_DECLINING_GROWTH_PENALTY: float = -1.5


class GrowthMomentumScorer:
    """Score company growth momentum (revenue growth, employee efficiency, funding)."""

    def __init__(self, config: ScoringSettings | None = None):
        self.config = config or ScoringSettings()

    def score(
        self,
        financials: FinancialMetric,
        fact_repo: FactRepository | None = None,
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
            financials = merge_facts_into_financials(financials, fact_repo, company_id)

        # STORY-207: Calculate data confidence before scoring
        data_confidence, data_warnings = calculate_data_confidence(financials)
        explanation.data_confidence = data_confidence
        explanation.data_warnings = data_warnings

        if data_warnings:
            for warning in data_warnings:
                logger.warning(f"[EPIC-059] Growth scorer: {warning}")

        # Apply all scoring components
        score = self._score_growth_rate(financials, score, explanation, cfg)
        score = self._score_employee_efficiency(financials, score, explanation, cfg)
        score = self._score_funding_momentum(financials, score, explanation, cfg)
        score = self._score_profitability(financials, score, explanation, cfg)
        score = self._apply_compound_penalties(financials, score, explanation)

        final_score = max(0.0, min(score, 10.0))
        explanation.final_score = final_score
        return final_score, explanation

    def _score_growth_rate(
        self,
        financials: FinancialMetric,
        score: float,
        explanation: ScoringExplanation,
        cfg: Any,
    ) -> float:
        """Score revenue growth rate component."""
        if financials.growth_rate is None:
            logger.warning("[EPIC-059] Growth rate missing — no contribution to score")
            explanation.components.append(
                ScoreComponent(
                    name="Missing Growth Rate",
                    value=0.0,
                    formula="growth_rate = None",
                    reasoning="No growth rate data available — component contributes 0.",
                )
            )
            return score

        growth_rate = financials.growth_rate
        growth_quotient = safe_div(
            growth_rate,
            cfg.revenue_growth_divisor,
            default=0.0,
            label="growth_factor",
        )
        growth_factor = min(growth_quotient or 0.0, cfg.revenue_growth_cap)
        score += growth_factor

        # Apply growth penalties
        if growth_rate < 0:
            score += _DECLINING_GROWTH_PENALTY
            explanation.components.append(
                ScoreComponent(
                    name="Declining Revenue Penalty",
                    value=_DECLINING_GROWTH_PENALTY,
                    formula="growth_rate < 0% → -1.5",
                    reasoning="Negative growth indicates revenue contraction — serious viability concern.",
                )
            )
        elif 0 <= growth_rate < _STAGNANT_GROWTH_UPPER:
            score += _STAGNANT_GROWTH_PENALTY
            explanation.components.append(
                ScoreComponent(
                    name="Stagnant Growth Penalty",
                    value=_STAGNANT_GROWTH_PENALTY,
                    formula="growth_rate < 5% → -0.75",
                    reasoning="Growth rate below 5% indicates stagnation.",
                )
            )
        elif _STAGNANT_GROWTH_UPPER <= growth_rate < _BELOW_AVERAGE_GROWTH_UPPER:
            score += _BELOW_AVERAGE_GROWTH_PENALTY
            explanation.components.append(
                ScoreComponent(
                    name="Below-Average Growth Penalty",
                    value=_BELOW_AVERAGE_GROWTH_PENALTY,
                    formula="growth_rate 5-10% → -0.25",
                    reasoning="Growth rate below 10% is below sector average.",
                )
            )

        explanation.components.append(
            ScoreComponent(
                name="Revenue Growth",
                value=growth_factor,
                formula=f"min({growth_rate}% / {cfg.revenue_growth_divisor}, {cfg.revenue_growth_cap})",
                reasoning=f"High growth rate of {growth_rate}% identified."
                if growth_rate > 15
                else "Moderate growth rate identified.",
            )
        )

        if growth_rate >= _HYPER_GROWTH_THRESHOLD:
            score += _HYPER_GROWTH_BONUS
            explanation.components.append(
                ScoreComponent(
                    name="Hyper-Growth Bonus",
                    value=_HYPER_GROWTH_BONUS,
                    formula="growth_rate >= 50% → +2.5",
                    reasoning="Exceptional growth rate indicates hyper-growth momentum.",
                )
            )

        return score

    def _score_employee_efficiency(
        self,
        financials: FinancialMetric,
        score: float,
        explanation: ScoringExplanation,
        cfg: Any,
    ) -> float:
        """Score employee efficiency component."""
        if not financials.employees or not financials.revenue:
            logger.warning("[EPIC-059] Employee/revenue data missing — skipping efficiency component")
            return score

        revenue_eur = financials.revenue * 1_000_000
        rev_per_emp = safe_div(
            revenue_eur,
            financials.employees,
            default=None,
            label="revenue_per_employee_growth",
        )
        if rev_per_emp is None:
            return score
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

        return score

    def _score_funding_momentum(
        self,
        financials: FinancialMetric,
        score: float,
        explanation: ScoringExplanation,
        cfg: Any,
    ) -> float:
        """Score funding momentum component."""
        if not financials.funding_raised:
            logger.warning("[EPIC-059] Funding data missing — skipping funding momentum component")
            return score

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

        return score

    def _score_profitability(
        self,
        financials: FinancialMetric,
        score: float,
        explanation: ScoringExplanation,
        cfg: Any,
    ) -> float:
        """Score profitability profile component."""
        if financials.profit_margin is None:
            logger.warning("[EPIC-059] Profit margin missing — applying unknown-data penalty")
            explanation.components.append(
                ScoreComponent(
                    name="Missing Profitability Data",
                    value=_UNKNOWN_DATA_PENALTY,
                    formula="profit_margin = None",
                    reasoning="No profitability data — unknown margins = higher risk.",
                )
            )
            return score + _UNKNOWN_DATA_PENALTY

        adj = 0.0
        if financials.profit_margin > cfg.margin_high_threshold:
            adj = cfg.margin_high_bonus
        elif financials.profit_margin > cfg.margin_med_threshold:
            adj = cfg.margin_med_bonus
        elif financials.profit_margin < -10:
            adj = cfg.margin_negative_penalty * 1.5
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

        # STORY-179: EBITDA margin bonus — strong operational efficiency signal
        if financials.ebitda_margin is not None and financials.ebitda_margin > 25:
            _EBITDA_MARGIN_BONUS = 0.25
            score += _EBITDA_MARGIN_BONUS
            explanation.components.append(
                ScoreComponent(
                    name="Strong EBITDA Margin",
                    value=_EBITDA_MARGIN_BONUS,
                    formula=f"ebitda_margin({financials.ebitda_margin}%) > 25% → +0.25",
                    reasoning="EBITDA margin above 25% indicates strong operational efficiency and sustainable growth potential.",
                )
            )

        return score

    def _apply_compound_penalties(
        self,
        financials: FinancialMetric,
        score: float,
        explanation: ScoringExplanation,
    ) -> float:
        """Apply compound penalties for high-risk combinations."""
        if financials.growth_rate is not None and financials.growth_rate < 0 and not financials.funding_raised:
            score += _COMPOUND_RISK_PENALTY
            explanation.components.append(
                ScoreComponent(
                    name="Compound Risk Penalty",
                    value=_COMPOUND_RISK_PENALTY,
                    formula="growth_rate < 0 AND no_funding → -1.0",
                    reasoning="Negative growth with no funding raises serious viability concerns.",
                )
            )

        return score
