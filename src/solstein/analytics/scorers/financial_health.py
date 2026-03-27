"""Financial health scorer: revenue scale, profitability, efficiency, funding cushion.

This scorer integrates both traditional financial metrics and facts from the
facts repository (SEC EDGAR, Companies House, news signals) to calculate a
comprehensive financial health score.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...core.scoring_config import ScoringSettings
from ...domain.models import (
    FinancialMetric,
    ScoreComponent,
    ScoringExplanation,
)

if TYPE_CHECKING:
    from ...infrastructure.repositories import FactRepository

from ._shared import merge_facts_into_financials


class FinancialHealthScorer:
    """Score company financial health (0-10)."""

    def __init__(self, config: ScoringSettings | None = None):
        self.config = config or ScoringSettings()

    # Missing data penalty
    _UNKNOWN_DATA_PENALTY: float = -2.0  # Penalty when financial data is unknown

    def score(
        self,
        financials: FinancialMetric,
        fact_repo: FactRepository | None = None,
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
            financials = merge_facts_into_financials(financials, fact_repo, company_id)

        # Apply all scoring components
        score = self._score_revenue_scale(financials, score, explanation, cfg)
        score = self._score_profitability(financials, score, explanation, cfg)
        score = self._score_operating_efficiency(financials, score, explanation, cfg)
        score = self._score_funding_cushion(financials, score, explanation, cfg)

        final_score = max(0.0, min(score, 10.0))
        explanation.final_score = final_score
        return final_score, explanation

    def _score_revenue_scale(
        self,
        financials: FinancialMetric,
        score: float,
        explanation: ScoringExplanation,
        cfg: Any,
    ) -> float:
        if financials.revenue is None:
            score += self._UNKNOWN_DATA_PENALTY
            explanation.components.append(
                ScoreComponent(
                    name="Missing Revenue Data",
                    value=self._UNKNOWN_DATA_PENALTY,
                    formula="revenue = None",
                    reasoning="No revenue data — unknown financials = higher risk.",
                )
            )
            return score

        adj = 0.0
        if financials.revenue >= cfg.revenue_large_threshold:
            adj = cfg.revenue_large_bonus
        elif financials.revenue >= cfg.revenue_med_threshold:
            adj = cfg.revenue_med_bonus
        elif financials.revenue < cfg.revenue_small_threshold:
            adj = cfg.revenue_small_penalty

        if adj != 0:
            score += adj
            explanation.components.append(
                ScoreComponent(
                    name="Revenue Scale",
                    value=adj,
                    formula=f"revenue(€{financials.revenue:.1f}M) -> adjustment",
                    reasoning=f"Revenue scale impacts financial stability. Thresholds: <€{cfg.revenue_small_threshold}M small, >€{cfg.revenue_med_threshold}M medium, >€{cfg.revenue_large_threshold}M large.",
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
        if financials.profit_margin is None:
            score += self._UNKNOWN_DATA_PENALTY
            explanation.components.append(
                ScoreComponent(
                    name="Missing Profitability Data",
                    value=self._UNKNOWN_DATA_PENALTY,
                    formula="profit_margin = None",
                    reasoning="No profitability data — unknown financials = higher risk.",
                )
            )
            return score

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

        return score

    def _score_operating_efficiency(
        self,
        financials: FinancialMetric,
        score: float,
        explanation: ScoringExplanation,
        cfg: Any,
    ) -> float:
        """Score operating efficiency component."""
        if not financials.employees or financials.employees <= 0 or financials.revenue is None:
            return score

        # Convert revenue from millions to actual EUR for calculation
        revenue_eur = financials.revenue * 1_000_000
        rev_per_emp = revenue_eur / financials.employees

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
                    formula=f"rev_per_emp(€{rev_per_emp:,.0f}) -> adjustment",
                    reasoning=f"Revenue per employee indicates operational efficiency. €{financials.revenue:.1f}M revenue / {financials.employees} employees = €{rev_per_emp:,.0f} per employee.",
                )
            )

        return score

    def _score_funding_cushion(
        self,
        financials: FinancialMetric,
        score: float,
        explanation: ScoringExplanation,
        cfg: Any,
    ) -> float:
        """Score funding cushion component."""
        if not financials.funding_raised or not financials.revenue or financials.revenue <= 0:
            return score

        # Both in millions, so ratio is unitless
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
                    reasoning=f"Capital reserves relative to revenue scale. €{financials.funding_raised:.1f}M funding / €{financials.revenue:.1f}M revenue = {ratio:.2f}x ratio.",
                )
            )

        return score
