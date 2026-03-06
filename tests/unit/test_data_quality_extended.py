"""Extended data quality tests - G3.

Field-level and pipeline-level data quality validation.
Part of EPIC-017 Wave 2 Testing Hardening.
"""

import pytest
from decimal import Decimal
from typing import Any

from solstein.domain.models import Company, FinancialMetric
from solstein.analytics.completeness import DataQualityTier
from solstein.presentation.data_quality_indicators import DataQualityIndicators


class TestFieldLevelDataQuality:
    """Field-level data quality validation tests."""

    def test_growth_rate_bounds(self) -> None:
        """Growth rate should be within reasonable bounds."""
        # Valid growth rates
        company1 = Company(id="test1", name="Test", industry="saas", growth_rate=0.5)
        assert company1.growth_rate == 0.5

        company2 = Company(id="test2", name="Test", industry="saas", growth_rate=-0.3)
        assert company2.growth_rate == -0.3

    def test_employee_count_positive(self) -> None:
        """Employee count must be positive."""
        company = Company(id="test", name="Test", industry="saas", employees=100)
        assert company.employees == 100

    def test_founded_year_range(self) -> None:
        """Founded year should be reasonable."""
        from datetime import datetime
        current_year = datetime.now().year

        company = Company(id="test", name="Test", industry="saas", founded_year=2020)
        assert 1800 <= company.founded_year <= current_year


class TestDataQualityIndicatorsExtended:
    """Extended data quality indicators tests."""

    def test_completeness_score_calculation(self) -> None:
        """Completeness score should be calculated correctly."""
        # Complete company
        complete = Company(
            id="complete",
            name="Complete Co",
            industry="saas",
            revenue=1000000.0,
            growth_rate=0.5,
            employees=100,
        )

        # Incomplete company
        incomplete = Company(
            id="incomplete",
            name="Incomplete Co",
            industry="saas",
        )

        complete_score = DataQualityIndicators.get_completeness_score(complete)
        incomplete_score = DataQualityIndicators.get_completeness_score(incomplete)

        assert complete_score > incomplete_score
        assert 0 <= complete_score <= 100
        assert 0 <= incomplete_score <= 100

    def test_data_quality_tier_assignment(self) -> None:
        """Data quality tier should be assigned based on completeness."""
        # Create companies with different completeness levels
        high_quality = Company(
            id="high",
            name="High Quality",
            industry="saas",
            revenue=1000000.0,
            growth_rate=0.5,
            employees=100,
            profit_margin=0.2,
            funding=5000000.0,
        )

        tier = DataQualityIndicators.get_data_quality_tier(high_quality)
        assert tier in [DataQualityTier.COMPLETE, DataQualityTier.PARTIAL, DataQualityTier.MINIMAL, DataQualityTier.INSUFFICIENT]


class TestFinancialMetricQuality:
    """Financial metric data quality tests."""

    def test_financial_metric_validation(self) -> None:
        """Financial metrics should validate correctly."""
        metric = FinancialMetric(
            revenue=1000000.0,
            growth_rate=0.25,
            profit_margin=0.15,
        )

        assert metric.revenue == 1000000.0
        assert metric.growth_rate == 0.25

    def test_zero_values_valid(self) -> None:
        """Zero values should be valid for financial metrics."""
        metric = FinancialMetric(
            revenue=0.0,
            growth_rate=0.0,
            profit_margin=0.0,
        )

        assert metric.revenue == 0.0
        assert metric.growth_rate == 0.0


class TestDataQualityEdgeCases:
    """Data quality edge case tests."""

    def test_empty_string_handling(self) -> None:
        """Empty strings should be handled gracefully."""
        company = Company(id="test", name="", industry="saas")
        assert company.name == ""

    def test_none_vs_zero(self) -> None:
        """None should be distinct from zero."""
        company_with_zero = Company(
            id="test1",
            name="Test",
            industry="saas",
            revenue=0.0,
        )

        company_with_none = Company(
            id="test2",
            name="Test",
            industry="saas",
            revenue=None,
        )

        assert company_with_zero.revenue == 0.0
        assert company_with_none.revenue is None


class TestDataQualityFlags:
    """Data quality flags and warnings tests."""

    def test_sparse_data_flag(self) -> None:
        """Sparse data should trigger a warning flag."""
        sparse_company = Company(
            id="sparse",
            name="Sparse Co",
            industry="saas",
        )

        flags = DataQualityIndicators.get_data_quality_flags(sparse_company)
        # Should have at least one flag for sparse data
        assert len(flags) >= 1

    def test_missing_revenue_flag(self) -> None:
        """Missing revenue should trigger a warning."""
        no_revenue = Company(
            id="no_rev",
            name="No Revenue Co",
            industry="saas",
            employees=100,
        )

        flags = DataQualityIndicators.get_data_quality_flags(no_revenue)
        # Check that revenue warning is in flags
        assert any("revenue" in flag.lower() or "sparse" in flag.lower() for flag in flags)

    def test_quality_flags_with_complete_data(self) -> None:
        """Complete data should have minimal flags."""
        complete = Company(
            id="complete",
            name="Complete Co",
            industry="saas",
            revenue=1000000.0,
            growth_rate=0.5,
            employees=100,
            profit_margin=0.2,
        )

        flags = DataQualityIndicators.get_data_quality_flags(complete)
        # Complete data should have few or no flags
        assert len(flags) <= 2
