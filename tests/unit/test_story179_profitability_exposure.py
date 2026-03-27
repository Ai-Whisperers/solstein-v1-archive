"""
STORY-179: Expose ebitda_margin_pct and recurring_revenue_pct on Company.

Verifies that convert_to_domain_company() populates Company.ebitda_margin,
Company.recurring_revenue_pct, and Company.revenue_per_employee_eur_k from
profitability data in the source JSON.

Also verifies that FinancialHealthScorer awards +0.25 for recurring_revenue_pct > 80
and GrowthMomentumScorer awards +0.25 for ebitda_margin > 25.
"""

from __future__ import annotations

import pytest

from solstein.analytics.scorers.financial_health import FinancialHealthScorer
from solstein.analytics.scorers.growth_momentum import GrowthMomentumScorer
from solstein.data.converters.company import convert_to_domain_company
from solstein.domain.models import FinancialMetric


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAAS_COMPANY = {
    "id": "saas-001",
    "name": "SaaS Corp",
    "industry": "Energy Software",
    "financials": {"revenue": 10.0, "employees": 50},
    "profitability": {
        "ebitda_margin_pct": 30.0,
        "recurring_revenue_pct": 85.0,
        "revenue_per_employee_eur_k": 333.0,
    },
}

LOW_RECURRING_COMPANY = {
    "id": "low-001",
    "name": "Low Recurring Corp",
    "industry": "Energy Software",
    "financials": {"revenue": 5.0, "employees": 30},
    "profitability": {
        "ebitda_margin_pct": 10.0,
        "recurring_revenue_pct": 40.0,
    },
}

NO_PROFITABILITY_COMPANY = {
    "id": "no-prof-001",
    "name": "No Profitability Corp",
    "industry": "Energy Software",
    "financials": {"revenue": 8.0, "employees": 40},
}


# ---------------------------------------------------------------------------
# STORY-179: Top-level Company fields
# ---------------------------------------------------------------------------


def test_ebitda_margin_populated_on_company() -> None:
    """Company.ebitda_margin is set from JSON profitability.ebitda_margin_pct."""
    company = convert_to_domain_company(SAAS_COMPANY)
    assert company.ebitda_margin == 30.0


def test_recurring_revenue_pct_populated_on_company() -> None:
    """Company.recurring_revenue_pct is set from JSON profitability.recurring_revenue_pct."""
    company = convert_to_domain_company(SAAS_COMPANY)
    assert company.recurring_revenue_pct == 85.0


def test_revenue_per_employee_eur_k_populated_on_company() -> None:
    """Company.revenue_per_employee_eur_k is set from JSON profitability."""
    company = convert_to_domain_company(SAAS_COMPANY)
    assert company.revenue_per_employee_eur_k == 333.0


def test_profitability_fields_none_when_missing() -> None:
    """Company.ebitda_margin and recurring_revenue_pct are None when JSON has no profitability."""
    company = convert_to_domain_company(NO_PROFITABILITY_COMPANY)
    assert company.ebitda_margin is None
    assert company.recurring_revenue_pct is None


def test_top_level_and_financials_fields_are_in_sync() -> None:
    """Top-level Company fields mirror FinancialMetric fields for same data."""
    company = convert_to_domain_company(SAAS_COMPANY)
    # Both should have the same values
    assert company.ebitda_margin == company.financials.ebitda_margin
    assert company.recurring_revenue_pct == company.financials.recurring_revenue_pct


# ---------------------------------------------------------------------------
# STORY-179: FinancialHealthScorer — recurring revenue bonus
# ---------------------------------------------------------------------------


def test_financial_health_scorer_awards_bonus_for_high_recurring_revenue() -> None:
    """FinancialHealthScorer awards +0.25 when recurring_revenue_pct > 80."""
    scorer = FinancialHealthScorer()

    with_bonus = FinancialMetric(revenue=10.0, profit_margin=15.0, recurring_revenue_pct=85.0)
    without_bonus = FinancialMetric(revenue=10.0, profit_margin=15.0)

    score_with, _ = scorer.score(with_bonus)
    score_without, _ = scorer.score(without_bonus)

    assert score_with - score_without == pytest.approx(0.25, abs=0.01)


def test_financial_health_scorer_no_bonus_below_threshold() -> None:
    """FinancialHealthScorer does NOT award bonus when recurring_revenue_pct <= 80."""
    scorer = FinancialHealthScorer()

    at_threshold = FinancialMetric(revenue=10.0, profit_margin=15.0, recurring_revenue_pct=80.0)
    without = FinancialMetric(revenue=10.0, profit_margin=15.0)

    score_at, _ = scorer.score(at_threshold)
    score_without, _ = scorer.score(without)

    assert score_at == pytest.approx(score_without, abs=0.01)


def test_financial_health_scorer_bonus_not_applied_when_none() -> None:
    """FinancialHealthScorer does not error when recurring_revenue_pct is None."""
    scorer = FinancialHealthScorer()
    financials = FinancialMetric(revenue=5.0, profit_margin=10.0, recurring_revenue_pct=None)
    score, _ = scorer.score(financials)
    assert isinstance(score, float)


# ---------------------------------------------------------------------------
# STORY-179: GrowthMomentumScorer — EBITDA margin bonus
# ---------------------------------------------------------------------------


def test_growth_momentum_scorer_awards_bonus_for_high_ebitda() -> None:
    """GrowthMomentumScorer awards +0.25 when ebitda_margin > 25."""
    scorer = GrowthMomentumScorer()

    with_bonus = FinancialMetric(revenue=10.0, profit_margin=15.0, ebitda_margin=30.0)
    without_bonus = FinancialMetric(revenue=10.0, profit_margin=15.0)

    score_with, _ = scorer.score(with_bonus)
    score_without, _ = scorer.score(without_bonus)

    assert score_with - score_without == pytest.approx(0.25, abs=0.01)


def test_growth_momentum_scorer_no_bonus_below_threshold() -> None:
    """GrowthMomentumScorer does NOT award bonus when ebitda_margin <= 25."""
    scorer = GrowthMomentumScorer()

    at_threshold = FinancialMetric(revenue=10.0, profit_margin=15.0, ebitda_margin=25.0)
    without = FinancialMetric(revenue=10.0, profit_margin=15.0)

    score_at, _ = scorer.score(at_threshold)
    score_without, _ = scorer.score(without)

    assert score_at == pytest.approx(score_without, abs=0.01)


def test_growth_momentum_scorer_bonus_not_applied_when_none() -> None:
    """GrowthMomentumScorer does not error when ebitda_margin is None."""
    scorer = GrowthMomentumScorer()
    financials = FinancialMetric(revenue=5.0, profit_margin=10.0, ebitda_margin=None)
    score, _ = scorer.score(financials)
    assert isinstance(score, float)


# ---------------------------------------------------------------------------
# Integration: end-to-end verify Eneve scores higher with profitability data
# ---------------------------------------------------------------------------


def test_eneve_scores_higher_with_profitability_signals() -> None:
    """Company with strong EBITDA and recurring revenue gets higher composite score."""
    scorer_fh = FinancialHealthScorer()
    scorer_gm = GrowthMomentumScorer()

    financials_full = FinancialMetric(
        revenue=3.0,
        profit_margin=15.0,
        recurring_revenue_pct=85.0,
        ebitda_margin=30.0,
    )
    financials_sparse = FinancialMetric(
        revenue=3.0,
        profit_margin=15.0,
    )

    score_fh_full, _ = scorer_fh.score(financials_full)
    score_fh_sparse, _ = scorer_fh.score(financials_sparse)
    score_gm_full, _ = scorer_gm.score(financials_full)
    score_gm_sparse, _ = scorer_gm.score(financials_sparse)

    assert score_fh_full > score_fh_sparse, "FinancialHealth: full data should score higher"
    assert score_gm_full > score_gm_sparse, "GrowthMomentum: full data should score higher"
    assert (score_fh_full - score_fh_sparse) == pytest.approx(0.25, abs=0.01)
    assert (score_gm_full - score_gm_sparse) == pytest.approx(0.25, abs=0.01)
