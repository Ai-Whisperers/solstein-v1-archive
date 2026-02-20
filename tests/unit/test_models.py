"""
Unit tests for SolStein data models.
"""

from datetime import datetime

import pytest
from src.solstein.data.models import (
    AIMaturity,
    CompanyProfile,
    CompanyTier,
    ConfidenceLevel,
    FinancialMetric,
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

    def test_numeric_parsing(self):
        """Test parsing numeric values from strings."""
        metric = FinancialMetric(
            revenue="€1.5M",
            growth_rate="15.5%",
            employees="1,000",
            profit_margin="12.5%",
            funding_raised="$2.5M",
            valuation="€100M",
        )

        assert metric.revenue == 1_500_000.0
        assert metric.growth_rate == 15.5
        assert metric.employees == 1000
        assert metric.profit_margin == 12.5
        assert metric.funding_raised == 2_500_000.0
        assert metric.valuation == 100_000_000.0

    def test_validation_bounds(self):
        """Test validation bounds."""
        # Growth rate should be between -100 and 1000
        metric = FinancialMetric(growth_rate=-50.0)
        assert metric.growth_rate == -50.0

        with pytest.raises(ValueError):
            FinancialMetric(growth_rate=-150.0)

        with pytest.raises(ValueError):
            FinancialMetric(growth_rate=1500.0)


class TestCompanyProfile:
    """Test CompanyProfile model."""

    def test_create_company_profile(self):
        """Test creating a CompanyProfile."""
        financials = FinancialMetric(
            revenue=10_000_000.0,
            growth_rate=25.0,
            employees=100,
        )

        profile = CompanyProfile(
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

    def test_properties(self):
        """Test computed properties."""
        financials = FinancialMetric(
            revenue=50_000_000.0,
            growth_rate=30.0,
            profit_margin=15.0,
            valuation=200_000_000.0,
        )

        profile = CompanyProfile(
            id="high-growth",
            name="High Growth Inc",
            financials=financials,
        )

        assert profile.is_public is True  # Valuation > 100M
        assert profile.is_high_growth is True  # Growth > 20%
        assert profile.is_profitable is True  # Profit margin > 0

    def test_serialization(self):
        """Test serialization to dict and JSON."""
        profile = CompanyProfile(
            id="serialize-test",
            name="Serialize Test",
            financials=FinancialMetric(revenue=1_000_000.0),
        )

        # Test dict serialization
        data = profile.model_dump()
        assert data["id"] == "serialize-test"
        assert data["name"] == "Serialize Test"
        assert data["financials"]["revenue"] == 1_000_000.0

        # Test JSON serialization
        json_str = profile.model_dump_json()
        assert "serialize-test" in json_str
        assert "Serialize Test" in json_str

    def test_default_values(self):
        """Test default values."""
        profile = CompanyProfile(
            id="default-test",
            name="Default Test",
            financials=FinancialMetric(),
        )

        assert profile.industry == "Energy Software"
        assert profile.tier == CompanyTier.TIER_3
        assert profile.threat_level == ThreatLevel.MEDIUM
        assert profile.ai_maturity == AIMaturity.NONE
        assert profile.saas_maturity == 1
        assert isinstance(profile.last_updated, datetime)


class TestEnums:
    """Test enum types."""

    def test_confidence_level(self):
        """Test ConfidenceLevel enum."""
        assert ConfidenceLevel.CONFIRMED == "Confirmed"
        assert ConfidenceLevel.ESTIMATED == "Estimated"
        assert ConfidenceLevel.UNKNOWN == "Unknown"

        # Test string conversion
        assert str(ConfidenceLevel.CONFIRMED) == "Confirmed"

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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
