"""
Unit tests for SolStein domain models.
"""

import pytest

from solstein.domain.models import (
    AIMaturity,
    Company,
    CompanyTier,
    CompetitiveOverlap,
    ConfidenceLevel,
    FinancialMetric,
    MarketAnalysis,
    ThreatLevel,
)


class TestFinancialMetric:
    """Test FinancialMetric model."""

    def test_create_financial_metric(self):
        """Test creating a FinancialMetric."""
        metric = FinancialMetric(
            revenue=1_000_000.0,
            revenue_confidence=ConfidenceLevel.CONFIRMED,
            growth_rate=15.5,
            growth_confidence=ConfidenceLevel.ESTIMATED,
            employees=50,
            employees_confidence=ConfidenceLevel.CONFIRMED,
        )

        assert metric.revenue == 1_000_000.0
        assert metric.revenue_confidence == ConfidenceLevel.CONFIRMED
        assert metric.growth_rate == 15.5
        assert metric.growth_confidence == ConfidenceLevel.ESTIMATED
        assert metric.employees == 50
        assert metric.employees_confidence == ConfidenceLevel.CONFIRMED

    def test_all_fields_default_to_none(self):
        """FinancialMetric fields are all optional — defaults should be None."""
        metric = FinancialMetric()
        assert metric.revenue is None
        assert metric.growth_rate is None
        assert metric.profit_margin is None
        assert metric.employees is None
        assert metric.funding_raised is None
        assert metric.valuation is None
        assert metric.valuation is None


class TestCompany:
    """Test Company model and computed properties."""

    def test_create_company(self):
        """Test creating a Company."""
        financials = FinancialMetric(
            revenue=10_000_000.0,
            growth_rate=25.0,
            employees=100,
        )

        profile = Company(
            id="test-company",
            name="Test Company",
            description="A test company",
            financials=financials,
            ai_maturity=AIMaturity.STRONG,
            threat_level=ThreatLevel.HIGH,
            tier=CompanyTier.TIER_2,
            geographic_presence=["US", "UK"],
            tech_stack=["Python", "React", "PostgreSQL"],
        )

        assert profile.id == "test-company"
        assert profile.name == "Test Company"
        assert profile.ai_maturity == AIMaturity.STRONG
        assert profile.threat_level == ThreatLevel.HIGH
        assert profile.tier == CompanyTier.TIER_2
        assert profile.geographic_presence == ["US", "UK"]
        assert profile.tech_stack == ["Python", "React", "PostgreSQL"]
        assert profile.financials.revenue == 10_000_000.0

    def test_properties_happy_path(self):
        """Test computed properties when all conditions are met."""
        profile = Company(
            id="high-growth",
            name="High Growth Inc",
            financials=FinancialMetric(
                revenue=50_000_000.0,
                growth_rate=30.0,
                profit_margin=15.0,
                valuation=200_000_000.0,
            ),
        )

        assert profile.is_large_cap is True  # valuation=200M > 100M
        assert profile.is_high_growth is True  # growth=30% > 20%
        assert profile.is_profitable is True  # margin=15% > 0

    def test_is_large_cap_false_when_no_valuation(self):
        """is_large_cap must return False when valuation is None (not set)."""
        profile = Company(id="x", name="X", financials=FinancialMetric(valuation=None))
        assert profile.is_large_cap is False

    def test_is_large_cap_false_when_valuation_below_threshold(self):
        """is_large_cap must return False when valuation ≤ 100M."""
        profile = Company(
            id="x",
            name="X",
            financials=FinancialMetric(valuation=50_000_000.0),
        )
        assert profile.is_large_cap is False

    def test_is_large_cap_true_exactly_above_threshold(self):
        """is_large_cap must return True when valuation is just above 100M."""
        profile = Company(
            id="x",
            name="X",
            financials=FinancialMetric(valuation=100_000_001.0),
        )
        assert profile.is_large_cap is True

    def test_is_high_growth_false_when_growth_rate_none(self):
        """is_high_growth must return False when growth_rate is None."""
        profile = Company(id="x", name="X", financials=FinancialMetric(growth_rate=None))
        assert profile.is_high_growth is False

    def test_is_high_growth_false_at_exactly_20(self):
        """is_high_growth boundary: growth_rate=20.0 is NOT high growth (must be > 20)."""
        profile = Company(id="x", name="X", financials=FinancialMetric(growth_rate=20.0))
        assert profile.is_high_growth is False

    def test_is_high_growth_true_above_20(self):
        """is_high_growth must return True only when growth_rate > 20."""
        profile = Company(id="x", name="X", financials=FinancialMetric(growth_rate=20.1))
        assert profile.is_high_growth is True

    def test_is_profitable_false_when_profit_margin_none(self):
        """is_profitable must return False when profit_margin is None."""
        profile = Company(id="x", name="X", financials=FinancialMetric(profit_margin=None))
        assert profile.is_profitable is False

    def test_is_profitable_false_at_zero(self):
        """is_profitable boundary: profit_margin=0 is NOT profitable (must be > 0)."""
        profile = Company(id="x", name="X", financials=FinancialMetric(profit_margin=0.0))
        assert profile.is_profitable is False

    def test_is_profitable_false_negative(self):
        """Negative profit margin must not be profitable."""
        profile = Company(id="x", name="X", financials=FinancialMetric(profit_margin=-5.0))
        assert profile.is_profitable is False

    def test_is_profitable_true_positive(self):
        """Positive profit margin must be profitable."""
        profile = Company(id="x", name="X", financials=FinancialMetric(profit_margin=0.1))
        assert profile.is_profitable is True

    def test_company_with_empty_tech_stack(self):
        """Company with no tech stack is valid and defaults to empty list."""
        profile = Company(id="x", name="X")
        assert profile.tech_stack == []

    def test_company_with_no_employees_is_valid(self):
        """Company with no employee data is valid."""
        profile = Company(id="x", name="X", financials=FinancialMetric(employees=None))
        assert profile.financials.employees is None

    def test_company_with_no_revenue_is_valid(self):
        """Company with no revenue data is valid."""
        profile = Company(id="x", name="X", financials=FinancialMetric(revenue=None))
        assert profile.financials.revenue is None

    def test_scores_default_to_none(self):
        """Unscored company has None scores."""
        profile = Company(id="x", name="X")
        assert profile.growth_score is None
        assert profile.financial_health_score is None
        assert profile.competitive_position_score is None


class TestCompetitiveOverlap:
    """Test CompetitiveOverlap domain entity."""

    def test_create_competitive_overlap(self):
        """Test creating a CompetitiveOverlap."""
        overlap = CompetitiveOverlap(
            company_a_id="company-a",
            company_b_id="company-b",
            overlap_score=0.75,
            overlap_areas=["Technology", "Geography"],
            competitive_intensity="High",
        )

        assert overlap.company_a_id == "company-a"
        assert overlap.company_b_id == "company-b"
        assert overlap.overlap_score == 0.75
        assert overlap.overlap_areas == ["Technology", "Geography"]
        assert overlap.competitive_intensity == "High"

    def test_competitive_overlap_defaults(self):
        """CompetitiveOverlap has sensible defaults."""
        overlap = CompetitiveOverlap(
            company_a_id="a",
            company_b_id="b",
            overlap_score=0.5,
        )
        assert overlap.overlap_areas == []
        assert overlap.competitive_intensity == "Medium"
        assert overlap.notes is None


class TestMarketAnalysis:
    """Test MarketAnalysis domain entity."""

    def test_create_market_analysis(self):
        """Test creating a MarketAnalysis."""
        companies = [
            Company(id="co1", name="Co1", financials=FinancialMetric(growth_rate=20.0)),
            Company(id="co2", name="Co2", financials=FinancialMetric(growth_rate=10.0)),
        ]
        analysis = MarketAnalysis(
            market_name="Tech",
            companies=companies,
            total_market_size=1000.0,
        )
        assert analysis.market_name == "Tech"
        assert analysis.total_market_size == 1000.0

    def test_company_count_property(self):
        """company_count property returns the number of companies."""
        companies = [
            Company(id="co1", name="Co1"),
            Company(id="co2", name="Co2"),
        ]
        analysis = MarketAnalysis(market_name="Tech", companies=companies)
        assert analysis.company_count == 2

    def test_average_growth_rate_property(self):
        """average_growth_rate computes correctly."""
        companies = [
            Company(id="co1", name="Co1", financials=FinancialMetric(growth_rate=20.0)),
            Company(id="co2", name="Co2", financials=FinancialMetric(growth_rate=10.0)),
        ]
        analysis = MarketAnalysis(market_name="Tech", companies=companies)
        assert analysis.average_growth_rate == pytest.approx(15.0)

    def test_average_growth_rate_none_when_no_data(self):
        """average_growth_rate returns None when no companies have growth data."""
        companies = [Company(id="co1", name="Co1", financials=FinancialMetric(growth_rate=None))]
        analysis = MarketAnalysis(market_name="Tech", companies=companies)
        assert analysis.average_growth_rate is None

    def test_market_leaders_returns_tier1_only(self):
        """market_leaders returns only Tier 1 companies."""
        tier1 = Company(id="t1", name="Leader", tier=CompanyTier.TIER_1)
        tier2 = Company(id="t2", name="Follower", tier=CompanyTier.TIER_2)
        analysis = MarketAnalysis(market_name="Tech", companies=[tier1, tier2])
        leaders = analysis.market_leaders
        assert len(leaders) == 1
        assert leaders[0].id == "t1"


class TestEnums:
    """Test enum types."""

    def test_confidence_level(self):
        """Test ConfidenceLevel enum."""
        assert ConfidenceLevel.CONFIRMED == "Confirmed"
        assert ConfidenceLevel.ESTIMATED == "Estimated"
        assert ConfidenceLevel.UNKNOWN == "Unknown"

    def test_ai_maturity(self):
        """Test AIMaturity enum."""
        levels = list(AIMaturity)
        assert len(levels) == 5
        assert AIMaturity.NONE == "None"
        assert AIMaturity.VERY_STRONG == "Very Strong"

    def test_company_tier(self):
        """Test CompanyTier enum."""
        tiers = list(CompanyTier)
        assert len(tiers) == 4
        assert CompanyTier.TIER_1 == "Tier 1"
        assert CompanyTier.TIER_4 == "Tier 4"

    def test_threat_level(self):
        """Test ThreatLevel enum."""
        assert ThreatLevel.LOW == "Low"
        assert ThreatLevel.CRITICAL == "Critical"
        levels = list(ThreatLevel)
        assert len(levels) == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
