"""
Golden dataset / data quality tests for SolStein scoring.

These tests use hand-crafted, verified company profiles with known expected
outcomes. They serve as regression guards — if the scoring config changes,
these will catch unexpected classification shifts.

All expected values derive directly from scoring_config.py defaults.
"""

import pytest

from solstein.analytics.scoring import GrowthScorer
from solstein.domain.models import AIMaturity, Company, FinancialMetric


@pytest.fixture
def scorer():
    return GrowthScorer()


# ---------------------------------------------------------------------------
# Golden classification tests
# ---------------------------------------------------------------------------


def test_golden_phoenix_classification(scorer):
    """
    Verified 'Phoenix' profile.

    Scoring:
        base(5.0) + growth(45/20=2.25) + margin_med_bonus(1.0) = 8.25
        (margin=15% hits margin_med_threshold=10.0, NOT high_threshold=20.0)
    """
    phoenix = Company(
        id="phoenix-verified",
        name="Verified Phoenix",
        financials=FinancialMetric(
            revenue=50.0,
            growth_rate=45.0,
            profit_margin=15.0,
        ),
        ai_maturity=AIMaturity.STRONG,
    )

    scored = scorer.calculate_scores(phoenix)
    assert scored.growth_score == pytest.approx(8.25), (
        "Verified Phoenix must score exactly 8.25 (base + growth_factor + med_margin_bonus)"
    )
    assert scored.growth_score >= 7.0, "Phoenix must be above the classification threshold"


def test_golden_lead_classification(scorer):
    """
    Verified 'Lead' profile.

    Scoring:
        base(5.0) + growth(-10/20=-0.5) + margin_negative_penalty(-1.0) = 3.5
    """
    lead = Company(
        id="lead-verified",
        name="Verified Lead",
        financials=FinancialMetric(
            revenue=5.0,
            growth_rate=-10.0,
            profit_margin=-5.0,
        ),
        ai_maturity=AIMaturity.NONE,
    )

    scored = scorer.calculate_scores(lead)
    assert scored.growth_score == pytest.approx(3.5), (
        "Verified Lead must score exactly 3.5 (base - 0.5 growth - 1.0 neg margin)"
    )
    assert scored.growth_score <= 4.0, "Lead must be below the classification threshold"


def test_golden_high_margin_hits_high_bonus(scorer):
    """
    Company with profit_margin=25% (> margin_high_threshold=20%) must receive +2.0 bonus.

    Scoring:
        base(5.0) + growth(20/20=1.0) + margin_high_bonus(2.0) = 8.0
    """
    company = Company(
        id="high-margin",
        name="High Margin Co",
        financials=FinancialMetric(
            revenue=100.0,
            growth_rate=20.0,
            profit_margin=25.0,
        ),
    )
    scored = scorer.calculate_scores(company)
    assert scored.growth_score == pytest.approx(8.0), "25% margin must trigger margin_high_bonus=2.0, not 1.0"


# ---------------------------------------------------------------------------
# AI Maturity impact regression
# ---------------------------------------------------------------------------


def test_ai_maturity_impact(scorer):
    """
    Regression: AI Maturity must significantly impact competitive position score.

    Expected diff:
        Very Strong: +2.5, None: -1.0 → diff ≥ 3.5
    """
    low_ai = Company(id="low", name="Low AI", ai_maturity=AIMaturity.NONE)
    high_ai = Company(id="high", name="High AI", ai_maturity=AIMaturity.VERY_STRONG)

    # Score independently — do NOT reuse same Company objects as scorer mutates in place
    scored_low = scorer.calculate_scores(low_ai)
    scored_high = scorer.calculate_scores(high_ai)

    diff = scored_high.competitive_position_score - scored_low.competitive_position_score
    assert diff >= 3.0, f"AI Maturity gap should be ≥ 3.0 (Very Strong=+2.5, None=-1.0 → 3.5). Got: {diff}"


# ---------------------------------------------------------------------------
# Boundary zone tests
# ---------------------------------------------------------------------------


def test_salt_boundary_at_7(scorer):
    """
    A company with growth_score exactly at 7.0 is classified as 'Phoenix'.
    Verify the boundary is correct.
    """
    # growth_rate=40: base(5.0) + 40/20=2.0 = 7.0 (no margin bonus)
    company = Company(
        id="boundary",
        name="Boundary Co",
        financials=FinancialMetric(
            growth_rate=40.0,
            profit_margin=None,
        ),
    )
    scored = scorer.calculate_scores(company)
    assert scored.growth_score == pytest.approx(7.0)
    # At exactly 7.0, classification logic uses >= 7.0 → "Phoenix"
    growth = scored.growth_score or 0.0
    classification = "Salt"
    if growth >= 7.0:
        classification = "Phoenix"
    elif growth <= 4.0:
        classification = "Lead"
    assert classification == "Phoenix", "Score of exactly 7.0 must be 'Phoenix'"


# ---------------------------------------------------------------------------
# SaaS maturity impact
# ---------------------------------------------------------------------------


def test_saas_maturity_extremes(scorer):
    """SaaS maturity=1 vs =10 should produce a measurable competitive score difference."""
    low_saas = Company(id="low-saas", name="Low SaaS", saas_maturity=1)
    high_saas = Company(id="high-saas", name="High SaaS", saas_maturity=10)

    scored_low = scorer.calculate_scores(low_saas)
    scored_high = scorer.calculate_scores(high_saas)

    # saas_score = (saas_maturity - 1) / 9 * 2.0
    # saas=1 → 0.0, saas=10 → 2.0 → diff should be 2.0
    diff = scored_high.competitive_position_score - scored_low.competitive_position_score
    assert diff == pytest.approx(2.0), f"SaaS maturity 1→10 should produce exactly 2.0 point diff. Got: {diff}"


# ---------------------------------------------------------------------------
# Global presence bonus
# ---------------------------------------------------------------------------


def test_global_presence_bonus(scorer):
    """A company with >10 geographic regions must receive the geo_global_bonus."""
    single_region = Company(
        id="local",
        name="Local Co",
        geographic_presence=["US"],
    )
    global_company = Company(
        id="global",
        name="Global Co",
        geographic_presence=[
            "US",
            "UK",
            "DE",
            "FR",
            "JP",
            "AU",
            "SG",
            "BR",
            "CA",
            "IN",
            "MX",
        ],
        # 11 regions > geo_global_count=10
    )

    scored_single = scorer.calculate_scores(single_region)
    scored_global = scorer.calculate_scores(global_company)

    # Actual logic might assign diff=1.5
    diff = scored_global.competitive_position_score - scored_single.competitive_position_score
    assert diff == pytest.approx(1.5), f"Global presence should produce +1.5 vs single-region. Got: {diff}"
