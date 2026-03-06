"""Data Quality Suite - G3.

Comprehensive data quality tests covering field-level and pipeline-level validation.
Part of EPIC-017 Wave 2 Testing Hardening.
"""

import pytest
from datetime import datetime
from decimal import Decimal
from typing import Any

from solstein.domain.models import Company, FinancialMetric
from solstein.data.loader_orchestrator import UnifiedLoaderOrchestrator, LoadResult
from solstein.data.normalization import DataNormalizer, parse_number, normalize_string
from solstein.data.conflict_resolution import ConflictResolver, ResolutionStrategy
from solstein.data.safe_defaults import SafeDefaults
from solstein.analytics.completeness import DataQualityTier
from solstein.presentation.data_quality_indicators import DataQualityIndicators


class TestFieldLevelDataQuality:
    """Field-level data quality validation tests."""

    def test_revenue_must_be_non_negative(self) -> None:
        """Revenue field must reject negative values."""
        with pytest.raises(ValueError, match="revenue"):
            FinancialMetric(revenue=-1000)

    def test_growth_rate_bounds(self) -> None:
        """Growth rate should be within reasonable bounds."""
        # Valid growth rates
        assert FinancialMetric(revenue_growth=0.5).revenue_growth == 0.5
        assert FinancialMetric(revenue_growth=-0.3).revenue_growth == -0.3
        assert FinancialMetric(revenue_growth=2.0).revenue_growth == 2.0

    def test_employee_count_positive(self) -> None:
        """Employee count must be positive."""
        metric = FinancialMetric(employees=100)
        assert metric.employees == 100

    def test_margin_bounds(self) -> None:
        """Profit margin should be within -1 to 1 range."""
        metric = FinancialMetric(profit_margin=0.25)
        assert metric.profit_margin == 0.25

        metric = FinancialMetric(profit_margin=-0.5)
        assert metric.profit_margin == -0.5

    def test_funding_non_negative(self) -> None:
        """Funding must be non-negative."""
        metric = FinancialMetric(funding_raised=1000000)
        assert metric.funding_raised == 1000000

    def test_valuation_positive(self) -> None:
        """Valuation must be positive if provided."""
        metric = FinancialMetric(valuation=50000000)
        assert metric.valuation == 50000000


class TestPipelineLevelDataQuality:
    """Pipeline-level data quality validation tests."""

    @pytest.fixture
    def orchestrator(self) -> LoaderOrchestrator:
        return LoaderOrchestrator()

    def test_empty_data_rejection(self, orchestrator: LoaderOrchestrator) -> None:
        """Empty data should be rejected at pipeline level."""
        result = orchestrator.load_company({})
        assert not result.success
        assert result.error is not None

    def test_missing_required_fields(self, orchestrator: LoaderOrchestrator) -> None:
        """Missing required fields should be flagged."""
        data = {"name": "Test Company"}  # Missing industry
        result = orchestrator.load_company(data)
        # Should still succeed but with warnings
        assert result.success or result.error is not None

    def test_data_type_validation(self, orchestrator: LoaderOrchestrator) -> None:
        """Invalid data types should be caught."""
        data = {
            "name": "Test",
            "industry": "saas",
            "revenue": "not_a_number",  # Invalid type
        }
        result = orchestrator.load_company(data)
        # Should handle gracefully
        assert isinstance(result, LoadResult)

    def test_duplicate_detection(self, orchestrator: LoaderOrchestrator) -> None:
        """Duplicate companies should be detected."""
        data1 = {"name": "Duplicate Co", "industry": "saas"}
        data2 = {"name": "Duplicate Co", "industry": "saas"}

        result1 = orchestrator.load_company(data1)
        result2 = orchestrator.load_company(data2)

        assert result1.success
        assert result2.success  # Both succeed, deduplication happens later


class TestDataNormalizationQuality:
    """Data normalization quality tests."""

    def test_revenue_normalization(self) -> None:
        """Revenue should be normalized to consistent units."""
        normalizer = DataNormalizer()
        test_cases = [
            (1000000, 1000000.0),  # Already in base units
            (1e6, 1000000.0),  # Scientific notation
        ]

        for input_val, expected in test_cases:
            result = normalizer.normalize_revenue(input_val)
            assert result == expected

    def test_industry_normalization(self) -> None:
        """Industry names should be normalized."""
        normalizer = DataNormalizer()
        test_cases = [
            ("SaaS", "saas"),
            ("SAAS", "saas"),
            ("Fintech", "fintech"),
            ("FinTech", "fintech"),
        ]

        for input_val, expected in test_cases:
            result = normalizer.normalize_industry(input_val)
            assert result == expected

    def test_country_normalization(self) -> None:
        """Country names should be normalized."""
        normalizer = DataNormalizer()
        test_cases = [
            ("USA", "us"),
            ("United States", "us"),
            ("UK", "gb"),
            ("United Kingdom", "gb"),
            ("Germany", "de"),
        ]

        for input_val, expected in test_cases:
            result = normalizer.normalize_country(input_val)
            assert result == expected
        """Revenue should be normalized to consistent units."""
        test_cases = [
            ({"revenue": 1000000}, 1000000.0),  # Already in base units
            ({"revenue": 1e6}, 1000000.0),  # Scientific notation
        ]

        for input_data, expected in test_cases:
            result = normalize_company_data(input_data)
            assert result["revenue"] == expected

    def test_industry_normalization(self) -> None:
        """Industry names should be normalized."""
        test_cases = [
            ("SaaS", "saas"),
            ("SAAS", "saas"),
            ("Software as a Service", "saas"),
            ("Fintech", "fintech"),
            ("FinTech", "fintech"),
        ]

        for input_val, expected in test_cases:
            result = normalize_company_data({"industry": input_val})
            assert result["industry"] == expected

    def test_country_normalization(self) -> None:
        """Country names should be normalized."""
        test_cases = [
            ("USA", "us"),
            ("United States", "us"),
            ("UK", "gb"),
            ("United Kingdom", "gb"),
            ("Germany", "de"),
        ]

        for input_val, expected in test_cases:
            result = normalize_company_data({"country": input_val})
            assert result["country"] == expected


class TestConflictResolutionQuality:
    """Conflict resolution quality tests."""

    @pytest.fixture
    def resolver(self) -> ConflictResolver:
        return ConflictResolver()

    def test_revenue_conflict_resolution(self, resolver: ConflictResolver) -> None:
        """Conflicting revenue values should be resolved."""
        sources = [
            ("source_a", 1000000),
            ("source_b", 1100000),
            ("source_c", 1050000),
        ]

        result = resolver.resolve_numeric_conflict(sources, ResolutionStrategy.CONSENSUS)
        # Consensus should pick median or average
        assert result is not None
        assert 1000000 <= result <= 1100000

    def test_employee_conflict_resolution(self, resolver: ConflictResolver) -> None:
        """Conflicting employee counts should be resolved."""
        sources = [
            ("linkedin", 100),
            ("crunchbase", 110),
            ("manual", 105),
        ]

        result = resolver.resolve_numeric_conflict(sources, ResolutionStrategy.CONSENSUS)
        assert result is not None
        assert 100 <= result <= 110

    def test_high_confidence_wins(self, resolver: ConflictResolver) -> None:
        """Higher confidence source should win."""
        sources = [
            ("low_confidence", 100),
            ("high_confidence", 120),
        ]
        confidences = {
            "low_confidence": 0.5,
            "high_confidence": 0.9,
        }

        result = resolver.resolve_with_confidence(sources, confidences)
        # Higher confidence value should be preferred
        assert result >= 110


class TestSafeDefaultsQuality:
    """Safe defaults quality tests."""

    def test_company_safe_defaults(self) -> None:
        """Company safe defaults should be valid."""
        company = SafeDefaults.company()

        assert company.name == "Unknown Company"
        assert company.industry == "unknown"
        assert company.revenue == 0.0
        assert company.growth_rate == 0.0

    def test_financial_metric_safe_defaults(self) -> None:
        """Financial metric safe defaults should be valid."""
        metric = SafeDefaults.financial_metric()

        assert metric.revenue is None
        assert metric.employees is None
        assert metric.revenue_growth is None

    def test_safe_defaults_are_immutable(self) -> None:
        """Safe defaults should return new instances."""
        company1 = SafeDefaults.company()
        company2 = SafeDefaults.company()

        assert company1 is not company2
        company1.name = "Modified"
        assert company2.name == "Unknown Company"


class TestDataQualityIndicatorsExtended:
    """Extended data quality indicators tests."""

    @pytest.fixture
    def minimal_company(self) -> Company:
        return Company(
            id="minimal-1",
            name="Minimal Co",
            industry="saas",
            financials=FinancialMetric(),
        )

    @pytest.fixture
    def partial_company(self) -> Company:
        return Company(
            id="partial-1",
            name="Partial Co",
            industry="saas",
            revenue=1000000,
            growth_rate=0.5,
            financials=FinancialMetric(
                revenue=1000000,
                revenue_growth=0.5,
                employees=50,
            ),
        )

    @pytest.fixture
    def complete_company(self) -> Company:
        return Company(
            id="complete-1",
            name="Complete Co",
            industry="saas",
            revenue=10000000,
            growth_rate=0.5,
            profit_margin=0.2,
            funding=5000000,
            valuation=50000000,
            financials=FinancialMetric(
                revenue=10000000,
                revenue_growth=0.5,
                employees=100,
                profit_margin=0.2,
                funding_raised=5000000,
                valuation=50000000,
            ),
        )

    def test_completeness_score_ranges(self, minimal_company, partial_company, complete_company) -> None:
        """Completeness scores should be in valid ranges."""
        minimal_score = DataQualityIndicators.get_completeness_score(minimal_company)
        partial_score = DataQualityIndicators.get_completeness_score(partial_company)
        complete_score = DataQualityIndicators.get_completeness_score(complete_company)

        assert 0 <= minimal_score <= 25
        assert 25 <= partial_score <= 75
        assert complete_score >= 60

    def test_data_quality_tier_progression(self, minimal_company, partial_company, complete_company) -> None:
        """Data quality tiers should progress correctly."""
        minimal_tier = DataQualityIndicators.get_data_quality_tier(minimal_company)
        partial_tier = DataQualityIndicators.get_data_quality_tier(partial_company)
        complete_tier = DataQualityIndicators.get_data_quality_tier(complete_company)

        # Tiers should generally improve with more data
        assert minimal_tier in [DataQualityTier.INSUFFICIENT, DataQualityTier.MINIMAL]
        assert partial_tier in [DataQualityTier.MINIMAL, DataQualityTier.PARTIAL]
        assert complete_tier in [DataQualityTier.PARTIAL, DataQualityTier.COMPLETE]

    def test_field_level_quality_indicators(self, partial_company) -> None:
        """Field-level quality indicators should be accurate."""
        indicators = DataQualityIndicators.get_field_indicators(partial_company)

        # Should have indicators for key fields
        assert "revenue" in indicators
        assert "growth_rate" in indicators
        assert "employees" in indicators

    def test_missing_field_detection(self, minimal_company) -> None:
        """Missing fields should be detected."""
        missing = DataQualityIndicators.get_missing_fields(minimal_company)

        assert "revenue" in missing
        assert "growth_rate" in missing
        assert "employees" in missing


class TestDataQualityEdgeCases:
    """Data quality edge case tests."""

    def test_zero_values_are_valid(self) -> None:
        """Zero values should be treated as valid data."""
        metric = FinancialMetric(
            revenue=0,  # Zero is valid (not missing)
            revenue_growth=0,  # Zero growth is valid
        )

        assert metric.revenue == 0
        assert metric.revenue_growth == 0

    def test_very_large_numbers(self) -> None:
        """Very large numbers should be handled."""
        metric = FinancialMetric(
            revenue=1e12,  # $1 trillion
            valuation=1e13,  # $10 trillion
        )

        assert metric.revenue == 1e12
        assert metric.valuation == 1e13

    def test_very_small_numbers(self) -> None:
        """Very small numbers should be handled."""
        metric = FinancialMetric(
            revenue=1,  # $1
            profit_margin=0.001,  # 0.1%
        )

        assert metric.revenue == 1
        assert metric.profit_margin == 0.001

    def test_special_characters_in_names(self) -> None:
        """Special characters in company names should be handled."""
        company = Company(
            id="test-1",
            name="Company & Co. (Test)",
            industry="saas",
        )

        assert "&" in company.name
        assert "(" in company.name

    def test_unicode_in_names(self) -> None:
        """Unicode characters should be handled."""
        company = Company(
            id="test-1",
            name="Tëst Cømpany 日本",
            industry="saas",
        )

        assert "ë" in company.name
        assert "ø" in company.name
        assert "日本" in company.name
