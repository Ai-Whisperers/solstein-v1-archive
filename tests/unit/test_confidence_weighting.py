"""
Task 8: Confidence-Based Weighting Tests

Tests for converting ConfidenceLevel enums to numeric weights and populating
signal_confidences for use in scoring component weighting.
"""

from src.solstein.analytics.confidence_weighting import (
    confidence_level_to_weight,
    get_average_confidence,
    get_confidence_summary,
    has_high_confidence_data,
    populate_signal_confidences,
)
from src.solstein.domain.models import Company, ConfidenceLevel, FinancialMetric


class TestConfidenceLevelToWeight:
    """Test confidence level to weight conversion."""

    def test_confirmed_to_weight(self):
        """Test CONFIRMED confidence converts to 1.0."""
        weight = confidence_level_to_weight(ConfidenceLevel.CONFIRMED)
        assert weight == 1.0

    def test_estimated_to_weight(self):
        """Test ESTIMATED confidence converts to 0.7."""
        weight = confidence_level_to_weight(ConfidenceLevel.ESTIMATED)
        assert weight == 0.7

    def test_unknown_to_weight(self):
        """Test UNKNOWN confidence converts to 0.3."""
        weight = confidence_level_to_weight(ConfidenceLevel.UNKNOWN)
        assert weight == 0.3


class TestPopulateSignalConfidences:
    """Test populating signal_confidences from financial metrics."""

    def test_populate_with_confirmed_revenue(self):
        """Test populating signal_confidences with confirmed revenue."""
        company = Company(
            id="test-1",
            name="Test Company",
            financials=FinancialMetric(
                revenue=100_000_000.0,
                revenue_confidence=ConfidenceLevel.CONFIRMED,
            ),
        )

        result = populate_signal_confidences(company)

        assert "revenue_level" in result.signal_confidences
        assert result.signal_confidences["revenue_level"] == 1.0

    def test_populate_with_estimated_growth(self):
        """Test populating signal_confidences with estimated growth."""
        company = Company(
            id="test-2",
            name="Test Company",
            financials=FinancialMetric(
                growth_rate=20.0,
                growth_confidence=ConfidenceLevel.ESTIMATED,
            ),
        )

        result = populate_signal_confidences(company)

        assert "growth_rate" in result.signal_confidences
        assert result.signal_confidences["growth_rate"] == 0.7

    def test_populate_with_unknown_employees(self):
        """Test populating signal_confidences with unknown employees."""
        company = Company(
            id="test-3",
            name="Test Company",
            financials=FinancialMetric(
                employees=500,
                employees_confidence=ConfidenceLevel.UNKNOWN,
            ),
        )

        result = populate_signal_confidences(company)

        assert "company_size" in result.signal_confidences
        assert result.signal_confidences["company_size"] == 0.3

    def test_populate_multiple_metrics(self):
        """Test populating signal_confidences with multiple metrics."""
        company = Company(
            id="test-4",
            name="Test Company",
            financials=FinancialMetric(
                revenue=100_000_000.0,
                revenue_confidence=ConfidenceLevel.CONFIRMED,
                growth_rate=20.0,
                growth_confidence=ConfidenceLevel.ESTIMATED,
                employees=500,
                employees_confidence=ConfidenceLevel.UNKNOWN,
            ),
        )

        result = populate_signal_confidences(company)

        assert result.signal_confidences["revenue_level"] == 1.0
        assert result.signal_confidences["growth_rate"] == 0.7
        assert result.signal_confidences["company_size"] == 0.3

    def test_populate_skips_none_values(self):
        """Test that None values are skipped."""
        company = Company(
            id="test-5",
            name="Test Company",
            financials=FinancialMetric(
                revenue=100_000_000.0,
                revenue_confidence=ConfidenceLevel.CONFIRMED,
                growth_rate=None,  # None value
                growth_confidence=ConfidenceLevel.ESTIMATED,
            ),
        )

        result = populate_signal_confidences(company)

        assert "revenue_level" in result.signal_confidences
        assert "growth_rate" not in result.signal_confidences  # Skipped

    def test_populate_with_no_financials(self):
        """Test populating when company has empty financials."""
        company = Company(
            id="test-6",
            name="Test Company",
            financials=FinancialMetric(),  # Empty financials
        )

        result = populate_signal_confidences(company)

        # Should return company with empty signal_confidences
        assert result.signal_confidences == {}


class TestGetConfidenceSummary:
    """Test getting confidence summary."""

    def test_get_summary_with_data(self):
        """Test getting confidence summary with data."""
        company = Company(
            id="test-7",
            name="Test Company",
            financials=FinancialMetric(
                revenue=100_000_000.0,
                revenue_confidence=ConfidenceLevel.CONFIRMED,
                growth_rate=20.0,
                growth_confidence=ConfidenceLevel.ESTIMATED,
            ),
        )

        populate_signal_confidences(company)
        summary = get_confidence_summary(company)

        assert summary["revenue_level"] == 1.0
        assert summary["growth_rate"] == 0.7

    def test_get_summary_empty(self):
        """Test getting confidence summary when empty."""
        company = Company(
            id="test-8",
            name="Test Company",
        )

        summary = get_confidence_summary(company)

        assert summary == {}


class TestHasHighConfidenceData:
    """Test checking for high-confidence data."""

    def test_has_high_confidence_confirmed(self):
        """Test detecting high-confidence confirmed data."""
        company = Company(
            id="test-9",
            name="Test Company",
            financials=FinancialMetric(
                revenue=100_000_000.0,
                revenue_confidence=ConfidenceLevel.CONFIRMED,
            ),
        )

        populate_signal_confidences(company)
        result = has_high_confidence_data(company, threshold=0.8)

        assert result is True

    def test_no_high_confidence_estimated(self):
        """Test that estimated data is not high-confidence."""
        company = Company(
            id="test-10",
            name="Test Company",
            financials=FinancialMetric(
                revenue=100_000_000.0,
                revenue_confidence=ConfidenceLevel.ESTIMATED,
            ),
        )

        populate_signal_confidences(company)
        result = has_high_confidence_data(company, threshold=0.8)

        assert result is False

    def test_no_high_confidence_unknown(self):
        """Test that unknown data is not high-confidence."""
        company = Company(
            id="test-11",
            name="Test Company",
            financials=FinancialMetric(
                revenue=100_000_000.0,
                revenue_confidence=ConfidenceLevel.UNKNOWN,
            ),
        )

        populate_signal_confidences(company)
        result = has_high_confidence_data(company, threshold=0.8)

        assert result is False


class TestGetAverageConfidence:
    """Test calculating average confidence."""

    def test_average_single_confirmed(self):
        """Test average with single confirmed metric."""
        company = Company(
            id="test-12",
            name="Test Company",
            financials=FinancialMetric(
                revenue=100_000_000.0,
                revenue_confidence=ConfidenceLevel.CONFIRMED,
            ),
        )

        populate_signal_confidences(company)
        average = get_average_confidence(company)

        assert average == 1.0

    def test_average_mixed_confidences(self):
        """Test average with mixed confidence levels."""
        company = Company(
            id="test-13",
            name="Test Company",
            financials=FinancialMetric(
                revenue=100_000_000.0,
                revenue_confidence=ConfidenceLevel.CONFIRMED,  # 1.0
                growth_rate=20.0,
                growth_confidence=ConfidenceLevel.ESTIMATED,  # 0.7
                employees=500,
                employees_confidence=ConfidenceLevel.UNKNOWN,  # 0.3
            ),
        )

        populate_signal_confidences(company)
        average = get_average_confidence(company)

        # (1.0 + 0.7 + 0.3) / 3 = 0.666...
        assert abs(average - 0.6666666) < 0.0001

    def test_average_empty_signals(self):
        """Test average with no signals."""
        company = Company(
            id="test-14",
            name="Test Company",
        )

        average = get_average_confidence(company)

        assert average == 0.3  # Default to unknown


class TestConfidenceIntegration:
    """Integration tests for confidence weighting."""

    def test_eneve_confidence_weighting(self):
        """Test confidence weighting for Eneve company."""
        # Eneve has mixed confidence levels
        company = Company(
            id="eneve",
            name="Eneve",
            financials=FinancialMetric(
                revenue=30_000_000.0,
                revenue_confidence=ConfidenceLevel.ESTIMATED,  # Markdown: estimated
                growth_rate=22.0,
                growth_confidence=ConfidenceLevel.ESTIMATED,
                employees=130,
                employees_confidence=ConfidenceLevel.CONFIRMED,  # Markdown: confirmed
                profit_margin=11.0,
                margin_confidence=ConfidenceLevel.ESTIMATED,
                funding_raised=15_000_000.0,
                funding_confidence=ConfidenceLevel.ESTIMATED,
                valuation=120_000_000.0,
                valuation_confidence=ConfidenceLevel.ESTIMATED,
            ),
        )

        populate_signal_confidences(company)

        # Check that signal_confidences is populated
        assert len(company.signal_confidences) > 0

        # Check that confirmed data has full weight
        assert company.signal_confidences["company_size"] == 1.0

        # Check that estimated data has reduced weight
        assert company.signal_confidences["revenue_level"] == 0.7
        assert company.signal_confidences["growth_rate"] == 0.7

        # Check average confidence
        average = get_average_confidence(company)
        assert 0.6 < average < 0.8  # Mostly estimated with one confirmed

    def test_confidence_weights_vary(self):
        """Test that confidence weights vary (not all 1.0)."""
        company = Company(
            id="test-15",
            name="Test Company",
            financials=FinancialMetric(
                revenue=100_000_000.0,
                revenue_confidence=ConfidenceLevel.CONFIRMED,
                growth_rate=20.0,
                growth_confidence=ConfidenceLevel.ESTIMATED,
                employees=500,
                employees_confidence=ConfidenceLevel.UNKNOWN,
            ),
        )

        populate_signal_confidences(company)

        weights = list(company.signal_confidences.values())

        # Verify weights vary
        assert len(set(weights)) > 1  # More than one unique weight
        assert 1.0 in weights  # Has confirmed
        assert 0.7 in weights  # Has estimated
        assert 0.3 in weights  # Has unknown
