"""
Unit tests for SolStein scoring algorithms.

Covers:
- GrowthScorer: exact score calculation, parametrized boundary tests, clamping
- MarketAnalyzer: SWOT, barriers with different company counts
- CompetitiveOverlapCalculator: overlap methods in isolation
- Custom ScoringSettings: config is respected
"""

import pytest
from solstein.analytics.scoring import (
    CompetitiveOverlapCalculator,
    GrowthScorer,
    MarketAnalyzer,
)
from solstein.core.scoring_config import ScoringSettings, GrowthScoringConfig
from solstein.domain.models import (
    AIMaturity,
    Company,
    CompanyTier,
    FinancialMetric,
)
from tests.factories import make_company, make_rocket_company, make_dinosaur_company


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def scorer():
    return GrowthScorer()


@pytest.fixture
def analyzer():
    return MarketAnalyzer()


@pytest.fixture
def overlap_calculator():
    return CompetitiveOverlapCalculator()


@pytest.fixture
def rocket_company():
    return make_rocket_company()


@pytest.fixture
def dinosaur_company():
    return make_dinosaur_company()


# ---------------------------------------------------------------------------
# GrowthScorer — exact score assertions
# ---------------------------------------------------------------------------

def test_calculate_growth_score_rocket(scorer, rocket_company):
    """
    Verify exact growth score for a high-growth company.

    Calculation:
        base(5.0) + growth(45/20=2.25) + margin_med_bonus(1.0) = 8.25
        (margin=15% hits margin_med_threshold=10.0, NOT margin_high_threshold=20.0)
    """
    scored = scorer.calculate_scores(rocket_company)
    assert scored.growth_score == pytest.approx(8.25)
    assert scored.financial_health_score >= 6.0


def test_calculate_growth_score_dinosaur(scorer, dinosaur_company):
    """
    Verify exact growth score for a declining company.

    Calculation:
        base(5.0) + growth(-5/20=-0.25) + margin_negative_penalty(-1.0) = 3.75
    """
    scored = scorer.calculate_scores(dinosaur_company)
    assert scored.growth_score == pytest.approx(3.75)
    # financial_health: base(5.0) + revenue_small(10 < 100 → no large bonus) + margin_negative(-2.5) = 2.5
    assert scored.financial_health_score == pytest.approx(2.5)


def test_calculate_scores_returns_same_company_object(scorer):
    """calculate_scores mutates and returns the same Company object."""
    company = make_company()
    result = scorer.calculate_scores(company)
    assert result is company
    assert company.growth_score is not None


# ---------------------------------------------------------------------------
# GrowthScorer — parametrized boundary tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("growth_rate,expected_min,expected_max", [
    (0.0,    4.9,  5.1),    # Neutral: base=5.0, no growth contribution, no margin
    (20.0,   5.9,  6.1),    # Exactly one divisor: 5.0 + 20/20=1.0 = 6.0
    (45.0,   7.2,  7.3),    # 5.0 + 2.25 = 7.25 (no margin, no funding on bare company)
    (400.0,  8.9,  9.1),    # 5.0 + cap(4.0) = 9.0 (revenue_growth_cap=4.0, no extras)
    (-10.0,  4.4,  4.6),    # 5.0 + (-10/20=-0.5) = 4.5 (no negative margin penalty)
    (-40.0,  2.9,  3.1),    # 5.0 + cap(-2.0) = 3.0 (growth capped at -20/20=-1.0 each div)
])
def test_growth_score_ranges(scorer, growth_rate, expected_min, expected_max):
    """Growth score stays within predicted range for each zone (bare company, no extras)."""
    # Use bare Company (no tech_stack, no geo, no margin) to isolate growth_rate effect
    company = Company(id="x", name="X", financials=FinancialMetric(growth_rate=growth_rate))
    scored = scorer.calculate_scores(company)
    assert expected_min <= scored.growth_score <= expected_max, (
        f"growth_rate={growth_rate}: expected [{expected_min}, {expected_max}], "
        f"got {scored.growth_score}"
    )


def test_growth_score_always_clamped_to_10(scorer):
    """Extreme growth_rate must never produce a score > 10.0."""
    company = make_company(financials=FinancialMetric(growth_rate=10_000.0))
    scored = scorer.calculate_scores(company)
    assert scored.growth_score <= 10.0


def test_growth_score_never_below_zero(scorer):
    """Extreme negative growth_rate must never produce a score < 0.0."""
    company = make_company(financials=FinancialMetric(growth_rate=-10_000.0))
    scored = scorer.calculate_scores(company)
    assert scored.growth_score >= 0.0


def test_financial_health_score_clamped(scorer):
    """Financial health score is always in [0, 10]."""
    company = make_company(
        financials=FinancialMetric(
            revenue=0.001,       # extreme small → penalty
            profit_margin=-99.0,  # huge negative margin
        )
    )
    scored = scorer.calculate_scores(company)
    assert 0.0 <= scored.financial_health_score <= 10.0


# ---------------------------------------------------------------------------
# GrowthScorer — competitive position score
# ---------------------------------------------------------------------------

def test_competitive_position_score_tier1_very_strong_ai(scorer):
    """Tier 1 + Very Strong AI should yield a high competitive score."""
    company = make_company(
        tier=CompanyTier.TIER_1,
        ai_maturity=AIMaturity.VERY_STRONG,
    )
    scored = scorer.calculate_scores(company)
    # base(5.0) + tier1(3.0) + very_strong(2.5) + saas(varied) = ~10.7, clamped to 10
    assert scored.competitive_position_score == pytest.approx(10.0)


def test_competitive_position_score_tier4_no_ai(scorer):
    """Tier 4 + None AI + single geo + no tech stack = low competitive score."""
    company = make_company(
        tier=CompanyTier.TIER_4,
        ai_maturity=AIMaturity.NONE,
        saas_maturity=1,
        geographic_presence=["US"],
        tech_stack=[],
    )
    scored = scorer.calculate_scores(company)
    # base(5.0) + tier4(-1.0) + none(-1.0) + saas(0) + single_geo(-0.5) + no_tech(-0.5) = 2.0
    assert scored.competitive_position_score == pytest.approx(2.0)


# ---------------------------------------------------------------------------
# GrowthScorer — custom config
# ---------------------------------------------------------------------------

def test_custom_scoring_config_is_respected():
    """Custom ScoringSettings should change scoring behavior."""
    default_scorer = GrowthScorer()
    # Double the revenue_growth_divisor → growth contribution halves
    custom_config = ScoringSettings()
    custom_config.growth.revenue_growth_divisor = 40.0  # was 20.0
    custom_scorer = GrowthScorer(config=custom_config)

    company = make_company(financials=FinancialMetric(growth_rate=40.0))

    default_scored = default_scorer.calculate_scores(company)
    default_score = default_scored.growth_score

    # Reset scores and use custom scorer
    company.growth_score = None
    company.financial_health_score = None
    company.competitive_position_score = None
    custom_scored = custom_scorer.calculate_scores(company)

    # Custom divisor → smaller growth contribution → lower score
    assert custom_scored.growth_score < default_score


# ---------------------------------------------------------------------------
# MarketAnalyzer
# ---------------------------------------------------------------------------

def test_market_analysis_swot(analyzer, rocket_company, dinosaur_company):
    """Verify SWOT analysis logic in MarketAnalyzer."""
    companies = [rocket_company, dinosaur_company]
    analysis = analyzer.analyze_market(companies)

    assert analysis.total_market_size == pytest.approx(510.0)  # 500 + 10
    assert "Strengths" in analysis.swot_analysis
    assert "Opportunities" in analysis.swot_analysis

    strengths = " ".join(analysis.swot_analysis["Strengths"])
    assert "growth" in strengths.lower()


def test_determine_barriers_few_companies(analyzer, rocket_company):
    """With ≤5 companies, 'High Competitive Rivalry' should NOT be a barrier."""
    analysis = analyzer.analyze_market([rocket_company])
    assert "Capital Intensity" in analysis.barriers_to_entry
    assert "High Competitive Rivalry" not in analysis.barriers_to_entry


def test_determine_barriers_many_companies(analyzer):
    """With >5 companies, 'High Competitive Rivalry' must be added as a barrier."""
    companies = [make_company(id=f"co-{i}", name=f"Co {i}") for i in range(6)]
    analysis = analyzer.analyze_market(companies)
    assert "High Competitive Rivalry" in analysis.barriers_to_entry


def test_market_analysis_average_growth(analyzer, rocket_company, dinosaur_company):
    """Market average growth is the mean of all company growth rates."""
    analysis = analyzer.analyze_market([rocket_company, dinosaur_company])
    # (45.0 + (-5.0)) / 2 = 20.0
    assert analysis.growth_rate == pytest.approx(20.0)


# ---------------------------------------------------------------------------
# CompetitiveOverlapCalculator
# ---------------------------------------------------------------------------

def test_overlap_same_industry_same_tier(overlap_calculator):
    """Companies in the same industry and tier have a higher overlap score."""
    p1 = make_company(id="a", name="A", industry="Technology", tier=CompanyTier.TIER_1)
    p2 = make_company(id="b", name="B", industry="Technology", tier=CompanyTier.TIER_1)
    score = overlap_calculator.calculate_overlap(p1, p2)
    assert score > 0.5


def test_overlap_different_industry(overlap_calculator):
    """Companies in different industries AND different tiers have a lower overlap score."""
    p1 = Company(id="a", name="A", industry="Technology", tier=CompanyTier.TIER_1,
                 tech_stack=["Python"], geographic_presence=["US"])
    p2 = Company(id="b", name="B", industry="Energy", tier=CompanyTier.TIER_4,
                 tech_stack=["Java"], geographic_presence=["DE"])
    score = overlap_calculator.calculate_overlap(p1, p2)
    # industry mismatch=0.0, geo=0.0, tech=0.0, tier=(4-1)/3=1, proximity=0.0 → avg ≈ 0.0
    assert score < 0.3


def test_geographic_overlap_identical(overlap_calculator):
    """Identical geographic presence yields overlap = 1.0."""
    p1 = make_company(id="a", name="A", geographic_presence=["US", "UK", "DE"])
    p2 = make_company(id="b", name="B", geographic_presence=["US", "UK", "DE"])
    # Access private method via the calculator for isolation
    score = overlap_calculator._calculate_geographic_overlap(p1, p2)
    assert score == pytest.approx(1.0)


def test_geographic_overlap_no_intersection(overlap_calculator):
    """No shared geographies yields overlap = 0.0."""
    p1 = make_company(id="a", name="A", geographic_presence=["US"])
    p2 = make_company(id="b", name="B", geographic_presence=["DE"])
    score = overlap_calculator._calculate_geographic_overlap(p1, p2)
    assert score == pytest.approx(0.0)


def test_geographic_overlap_partial(overlap_calculator):
    """Partial geographic overlap is between 0 and 1."""
    p1 = make_company(id="a", name="A", geographic_presence=["US", "UK"])
    p2 = make_company(id="b", name="B", geographic_presence=["US", "DE"])
    score = overlap_calculator._calculate_geographic_overlap(p1, p2)
    # intersection=1 (US), union=3 (US, UK, DE) → 1/3 ≈ 0.333
    assert score == pytest.approx(1 / 3)


def test_technology_overlap_identical(overlap_calculator):
    """Identical tech stacks yield overlap = 1.0."""
    p1 = make_company(id="a", name="A", tech_stack=["Python", "React"])
    p2 = make_company(id="b", name="B", tech_stack=["Python", "React"])
    score = overlap_calculator._calculate_technology_overlap(p1, p2)
    assert score == pytest.approx(1.0)


def test_technology_overlap_no_intersection(overlap_calculator):
    """No shared tech yields overlap = 0.0."""
    p1 = make_company(id="a", name="A", tech_stack=["Python"])
    p2 = make_company(id="b", name="B", tech_stack=["Java"])
    score = overlap_calculator._calculate_technology_overlap(p1, p2)
    assert score == pytest.approx(0.0)


def test_tier_proximity_same_tier(overlap_calculator):
    """Same tier should yield proximity = 1.0."""
    p1 = make_company(id="a", name="A", tier=CompanyTier.TIER_1)
    p2 = make_company(id="b", name="B", tier=CompanyTier.TIER_1)
    score = overlap_calculator._calculate_tier_proximity(p1, p2)
    assert score == pytest.approx(1.0)


def test_tier_proximity_max_distance(overlap_calculator):
    """Tier 1 vs Tier 4 (max distance=3) should yield proximity = 0.0."""
    p1 = make_company(id="a", name="A", tier=CompanyTier.TIER_1)
    p2 = make_company(id="b", name="B", tier=CompanyTier.TIER_4)
    score = overlap_calculator._calculate_tier_proximity(p1, p2)
    assert score == pytest.approx(0.0)


def test_tier_proximity_adjacent(overlap_calculator):
    """Adjacent tiers (distance=1) should yield proximity ≈ 0.667."""
    p1 = make_company(id="a", name="A", tier=CompanyTier.TIER_1)
    p2 = make_company(id="b", name="B", tier=CompanyTier.TIER_2)
    score = overlap_calculator._calculate_tier_proximity(p1, p2)
    assert score == pytest.approx(2 / 3)
