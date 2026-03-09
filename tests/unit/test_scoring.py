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
from solstein.core.scoring_config import ScoringSettings
from solstein.domain.models import (
    AIMaturity,
    Company,
    CompanyTier,
    FinancialMetric,
)
from tests.factories import make_company, make_lead_company, make_phoenix_company

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
def phoenix_company():
    return make_phoenix_company()


@pytest.fixture
def lead_company():
    return make_lead_company()


# ---------------------------------------------------------------------------
# GrowthScorer — exact score assertions
# ---------------------------------------------------------------------------


def test_calculate_growth_score_phoenix(scorer, phoenix_company):
    """
    Verify exact growth score for a high-growth company.

    Calculation:
        growth: base(0) + growth(45/20=2.25) + margin_med_bonus(1.0) = 3.25
        financial: base(2.5) + revenue_large(500M>=100M → +2.5) + margin_med(15%>5% → +1.25) = 6.25
    """
    scored = scorer.calculate_scores(phoenix_company)
    assert scored.growth_score == pytest.approx(3.25)
    assert scored.financial_health_score == pytest.approx(6.25)


def test_calculate_growth_score_lead(scorer, lead_company):
    """
    Verify exact growth score for a declining company.

    Calculation:
        growth: base(0) + growth(-5/20=-0.25) + neg_margin(-2% < 0 → -1.0) + compound(-1.0) → clamped to 0.0
        financial: base(2.5) + revenue_med(10M>=10M → +1.25) + margin_negative(-2% < 0 → -2.5) = 1.25
    """
    scored = scorer.calculate_scores(lead_company)
    assert scored.growth_score == pytest.approx(0.0)
    assert scored.financial_health_score == pytest.approx(1.25)


def test_calculate_scores_returns_same_company_object(scorer):
    """calculate_scores mutates and returns the same Company object."""
    company = make_company()
    result = scorer.calculate_scores(company)
    assert result is company
    assert company.growth_score is not None


# ---------------------------------------------------------------------------
# GrowthScorer — parametrized boundary tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "growth_rate,expected_min,expected_max",
    [
        (0.0, -0.01, 0.01),  # base(0) + growth(0) + stagnant_penalty(-0.75) → clamped to 0.0
        (20.0, 0.9, 1.1),    # base(0) + 20/20=1.0 = 1.0
        (45.0, 2.2, 2.3),    # base(0) + 2.25 = 2.25 (no margin, no funding)
        (400.0, 6.4, 6.6),   # base(0) + cap(4.0) + hyper_growth(≥50%→+2.5) = 6.5
        (-10.0, -0.01, 0.01),  # base(0) + (-0.5) + compound(-1.0) → clamped to 0.0
        (
            -40.0,
            -0.01,
            0.01,
        ),  # base(0) + (-2.0) + compound(-1.0) → clamped to 0.0
    ],
)
def test_growth_score_ranges(scorer, growth_rate, expected_min, expected_max):
    """Growth score stays within predicted range for each zone (bare company, no extras)."""
    # Use bare Company (no tech_stack, no geo, no margin) to isolate growth_rate effect
    company = Company(id="xxx", name="X", financials=FinancialMetric(growth_rate=growth_rate))
    scored = scorer.calculate_scores(company)
    assert expected_min <= scored.growth_score <= expected_max, (
        f"growth_rate={growth_rate}: expected [{expected_min}, {expected_max}], got {scored.growth_score}"
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
            revenue=0.001,  # extreme small → penalty
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
    # base(5.0) + tier4(-1.0) + none(-1.0) + saas(0) = 3.0
    assert scored.competitive_position_score == pytest.approx(3.0)


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
    assert default_score is not None

    # Reset scores and use custom scorer
    company.growth_score = None
    company.financial_health_score = None
    company.competitive_position_score = None
    custom_scored = custom_scorer.calculate_scores(company)

    # Custom divisor → smaller growth contribution → lower score
    assert custom_scored.growth_score is not None
    assert custom_scored.growth_score < default_score


# ---------------------------------------------------------------------------
# MarketAnalyzer
# ---------------------------------------------------------------------------


def test_market_analysis_swot(analyzer, phoenix_company, lead_company):
    """Verify SWOT analysis logic in MarketAnalyzer."""
    companies = [phoenix_company, lead_company]
    analysis = analyzer.analyze_market(companies)

    assert analysis.total_market_size == pytest.approx(510.0)  # 500 + 10
    assert "Strengths" in analysis.swot_analysis
    assert "Opportunities" in analysis.swot_analysis

    strengths = " ".join(analysis.swot_analysis["Strengths"])
    assert "growth" in strengths.lower()


def test_determine_barriers_few_companies(analyzer, phoenix_company):
    """With ≤5 companies, 'High Competitive Rivalry' should NOT be a barrier."""
    analysis = analyzer.analyze_market([phoenix_company])
    assert "Capital Intensity" in analysis.barriers_to_entry
    assert "High Competitive Rivalry" not in analysis.barriers_to_entry


def test_determine_barriers_many_companies(analyzer):
    """With >5 companies, 'High Competitive Rivalry' must be added as a barrier."""
    companies = [make_company(id=f"co-{i}", name=f"Co {i}") for i in range(6)]
    analysis = analyzer.analyze_market(companies)
    assert "High Competitive Rivalry" in analysis.barriers_to_entry


def test_market_analysis_average_growth(analyzer, phoenix_company, lead_company):
    """Market average growth is the mean of all company growth rates."""
    analysis = analyzer.analyze_market([phoenix_company, lead_company])
    # (45.0 + (-5.0)) / 2 = 20.0
    assert analysis.growth_rate == pytest.approx(20.0)


# ---------------------------------------------------------------------------
# CompetitiveOverlapCalculator
# ---------------------------------------------------------------------------


def test_overlap_same_industry_same_tier(overlap_calculator):
    """Companies in the same industry and tier have a higher overlap score."""
    p1 = make_company(id="aaa", name="A", industry="Technology", tier=CompanyTier.TIER_1)
    p2 = make_company(id="bbb", name="B", industry="Technology", tier=CompanyTier.TIER_1)
    score = overlap_calculator.calculate_overlap(p1, p2)
    assert score >= 0.5


def test_overlap_different_industry(overlap_calculator):
    """Companies in different industries AND different tiers have a lower overlap score."""
    p1 = Company(
        id="aaa",
        name="A",
        industry="Technology",
        tier=CompanyTier.TIER_1,
        tech_stack=["Python"],
        geographic_presence=["US"],
    )
    p2 = Company(
        id="bbb",
        name="B",
        industry="Energy",
        tier=CompanyTier.TIER_4,
        tech_stack=["Java"],
        geographic_presence=["DE"],
    )
    score = overlap_calculator.calculate_overlap(p1, p2)
    # industry mismatch=0.0, geo=0.0, tech=0.0, tier=(4-1)/3=1, proximity=0.0 → avg ≈ 0.0
    assert score < 0.3


def test_geographic_overlap_identical(overlap_calculator):
    """Identical geographic presence yields overlap = 1.0."""
    p1 = make_company(id="aaa", name="A", geographic_presence=["US", "UK", "DE"])
    p2 = make_company(id="bbb", name="B", geographic_presence=["US", "UK", "DE"])
    # Access private method via the calculator for isolation
    score = overlap_calculator._calculate_geographic_overlap(p1, p2)
    assert score == pytest.approx(1.0)


def test_geographic_overlap_no_intersection(overlap_calculator):
    """No shared geographies yields overlap = 0.0."""
    p1 = make_company(id="aaa", name="A", geographic_presence=["US"])
    p2 = make_company(id="bbb", name="B", geographic_presence=["DE"])
    score = overlap_calculator._calculate_geographic_overlap(p1, p2)
    assert score == pytest.approx(0.0)


def test_geographic_overlap_partial(overlap_calculator):
    """Partial geographic overlap is between 0 and 1."""
    p1 = make_company(id="aaa", name="A", geographic_presence=["US", "UK"])
    p2 = make_company(id="bbb", name="B", geographic_presence=["US", "DE"])
    score = overlap_calculator._calculate_geographic_overlap(p1, p2)
    # intersection=1 (US), union=3 (US, UK, DE) → 1/3 ≈ 0.333
    assert score == pytest.approx(1 / 3)


def test_technology_overlap_identical(overlap_calculator):
    """Identical tech stacks yield overlap = 1.0."""
    p1 = make_company(id="aaa", name="A", tech_stack=["Python", "React"])
    p2 = make_company(id="bbb", name="B", tech_stack=["Python", "React"])
    score = overlap_calculator._calculate_technology_overlap(p1, p2)
    assert score == pytest.approx(1.0)


def test_technology_overlap_no_intersection(overlap_calculator):
    """No shared tech yields overlap = 0.0."""
    p1 = make_company(id="aaa", name="A", tech_stack=["Python"])
    p2 = make_company(id="bbb", name="B", tech_stack=["Java"])
    score = overlap_calculator._calculate_technology_overlap(p1, p2)
    assert score == pytest.approx(0.0)


def test_tier_proximity_same_tier(overlap_calculator):
    """Same tier should yield proximity = 1.0."""
    p1 = make_company(id="aaa", name="A", tier=CompanyTier.TIER_1)
    p2 = make_company(id="bbb", name="B", tier=CompanyTier.TIER_1)
    score = overlap_calculator._calculate_tier_proximity(p1, p2)
    assert score == pytest.approx(1.0)


def test_tier_proximity_max_distance(overlap_calculator):
    """Tier 1 vs Tier 4 (max distance=3) should yield proximity = 0.0."""
    p1 = make_company(id="aaa", name="A", tier=CompanyTier.TIER_1)
    p2 = make_company(id="bbb", name="B", tier=CompanyTier.TIER_4)
    score = overlap_calculator._calculate_tier_proximity(p1, p2)
    assert score == pytest.approx(0.0)


def test_tier_proximity_adjacent(overlap_calculator):
    """Adjacent tiers (distance=1) should yield proximity ≈ 0.667."""
    p1 = make_company(id="aaa", name="A", tier=CompanyTier.TIER_1)
    p2 = make_company(id="bbb", name="B", tier=CompanyTier.TIER_2)
    score = overlap_calculator._calculate_tier_proximity(p1, p2)
    assert score == pytest.approx(2 / 3)


# ---------------------------------------------------------------------------
# Confidence-Weighted Scoring (Phase 5)
# ---------------------------------------------------------------------------


def test_confidence_weighting_full_confidence_matches_unweighted():
    """Companies with all signal_confidences=1.0 should score identically to unweighted."""
    financials = FinancialMetric(
        revenue=500_000_000,
        growth_rate=25.0,
        employees=2000,
        profit_margin=15.0,
        funding_raised=100_000_000,
    )
    base = Company(
        id="no-conf",
        name="No Confidence",
        industry="Software",
        financials=financials,
    )
    full_conf = Company(
        id="full-conf",
        name="Full Confidence",
        industry="Software",
        financials=financials,
        signal_confidences={
            "revenue_level": 1.0,
            "growth_rate": 1.0,
            "profitability": 1.0,
            "company_size": 1.0,
            "valuation": 1.0,
            "funding": 1.0,
            "ai_maturity": 1.0,
        },
    )

    scorer = GrowthScorer()
    scorer.calculate_scores(base)
    scorer.calculate_scores(full_conf)

    assert base.growth_score == pytest.approx(full_conf.growth_score)
    assert base.financial_health_score == pytest.approx(full_conf.financial_health_score)
    assert base.competitive_position_score == pytest.approx(full_conf.competitive_position_score)
    assert base.composite_score == pytest.approx(full_conf.composite_score)


def test_confidence_weighting_half_confidence_reduces_scores():
    """Companies with signal_confidences=0.5 should have lower scores than unweighted."""
    financials = FinancialMetric(
        revenue=500_000_000,
        growth_rate=25.0,
        employees=2000,
        profit_margin=15.0,
        funding_raised=100_000_000,
    )
    base = Company(
        id="no-conf",
        name="No Confidence",
        industry="Software",
        financials=financials,
    )
    half_conf = Company(
        id="half-conf",
        name="Half Confidence",
        industry="Software",
        financials=financials,
        signal_confidences={
            "revenue_level": 0.5,
            "growth_rate": 0.5,
            "profitability": 0.5,
            "company_size": 0.5,
            "valuation": 0.5,
            "funding": 0.5,
            "ai_maturity": 0.5,
        },
    )

    scorer = GrowthScorer()
    scorer.calculate_scores(base)
    scorer.calculate_scores(half_conf)

    # Growth and financial scores should be lower with half confidence
    assert half_conf.growth_score < base.growth_score
    assert half_conf.financial_health_score < base.financial_health_score


def test_confidence_weighting_no_confidences_unchanged():
    """Companies with empty signal_confidences (legacy) should score normally."""
    financials = FinancialMetric(
        revenue=500_000_000,
        growth_rate=25.0,
        employees=2000,
        profit_margin=15.0,
    )
    legacy = Company(
        id="legacy",
        name="Legacy Company",
        industry="Software",
        financials=financials,
        signal_confidences={},  # Empty — legacy path
    )
    no_field = Company(
        id="no-field",
        name="No Field",
        industry="Software",
        financials=financials,
        # signal_confidences defaults to {}
    )

    scorer = GrowthScorer()
    scorer.calculate_scores(legacy)
    scorer.calculate_scores(no_field)

    assert legacy.growth_score == pytest.approx(no_field.growth_score)
    assert legacy.financial_health_score == pytest.approx(no_field.financial_health_score)


def test_confidence_weight_populates_score_components():
    """ScoreComponent.confidence_weight should be populated in breakdown."""
    financials = FinancialMetric(
        revenue=500_000_000,
        growth_rate=25.0,
        employees=2000,
        profit_margin=15.0,
        funding_raised=100_000_000,
    )
    company = Company(
        id="conf-check",
        name="Confidence Check",
        industry="Software",
        financials=financials,
        signal_confidences={
            "revenue_level": 0.8,
            "growth_rate": 0.6,
            "profitability": 0.9,
            "funding": 0.7,
            "company_size": 0.5,
        },
    )

    scorer = GrowthScorer()
    scorer.calculate_scores(company)

    # Check that growth breakdown has confidence_weight on components
    growth_expl = company.scoring_breakdown["growth"]
    for component in growth_expl.components:
        assert hasattr(component, "confidence_weight")
        assert 0.0 < component.confidence_weight <= 1.0


def test_confidence_weighting_scores_still_clamped():
    """Confidence-weighted scores should still be in [0, 10]."""
    financials = FinancialMetric(
        revenue=10_000_000_000,
        growth_rate=200.0,
        employees=100,
        profit_margin=50.0,
        funding_raised=5_000_000_000,
    )
    company = Company(
        id="extreme",
        name="Extreme",
        industry="Software",
        financials=financials,
        signal_confidences={
            "revenue_level": 0.3,
            "growth_rate": 0.3,
            "profitability": 0.3,
            "funding": 0.3,
            "company_size": 0.3,
        },
    )

    scorer = GrowthScorer()
    scorer.calculate_scores(company)

    assert 0.0 <= company.growth_score <= 10.0
    assert 0.0 <= company.financial_health_score <= 10.0
    assert 0.0 <= company.competitive_position_score <= 10.0
