"""
STORY-209: Conversion validation gate tests (EPIC-059).

Test that the conversion validation detects when critical financial fields
are lost during the conversion process (>30% field loss).

Acceptance Criteria:
- AC-1: Validation correctly identifies field loss >30%
- AC-2: Logger emits warning with [EPIC-059] marker when field loss detected
- AC-3: Conversion proceeds gracefully even when validation fails (graceful degradation)
- AC-4: No exceptions raised, financial metric returned with available data
"""

import logging

from solstein.data.converters.company import (
    _validate_financial_conversion,
    convert_to_domain_company,
)
from solstein.domain.models import ConfidenceLevel, FinancialMetric


class TestValidationGate:
    """Test conversion validation gate (STORY-209)."""

    def test_validation_detects_high_field_loss(self):
        """AC-1: Validation detects >30% field loss."""
        # Raw data has 4 critical fields
        raw_data = {
            "company_name": "Test Corp",
            "revenue": 100.0,
            "employees": 500,
            "growth_rate": 0.15,
            "profit_margin": 0.25,
            # Missing: funding_raised, valuation
        }

        # Financial metric has only 2 of the 4 expected fields
        financial = FinancialMetric(
            revenue=100.0,
            revenue_confidence=ConfidenceLevel.CONFIRMED,
            employees=500,
            employees_confidence=ConfidenceLevel.CONFIRMED,
            growth_rate=None,  # Lost
            growth_confidence=ConfidenceLevel.UNKNOWN,
            profit_margin=None,  # Lost
            margin_confidence=ConfidenceLevel.UNKNOWN,
        )

        is_valid = _validate_financial_conversion(financial, raw_data)

        # 50% field loss (2 out of 4 lost) > 30% threshold
        assert is_valid is False

    def test_validation_passes_low_field_loss(self):
        """Validation passes when field loss <30%."""
        raw_data = {
            "company_name": "Test Corp",
            "revenue": 100.0,
            "employees": 500,
            "growth_rate": 0.15,
            "profit_margin": 0.25,
            "funding_raised": 50.0,
        }

        # Financial metric has 5 of 6 expected fields (16.7% loss < 30%)
        financial = FinancialMetric(
            revenue=100.0,
            revenue_confidence=ConfidenceLevel.CONFIRMED,
            employees=500,
            employees_confidence=ConfidenceLevel.CONFIRMED,
            growth_rate=0.15,
            growth_confidence=ConfidenceLevel.ESTIMATED,
            profit_margin=0.25,
            margin_confidence=ConfidenceLevel.CONFIRMED,
            funding_raised=50.0,
            funding_confidence=ConfidenceLevel.ESTIMATED,
            valuation=None,  # Only missing field
        )

        is_valid = _validate_financial_conversion(financial, raw_data)

        assert is_valid is True

    def test_validation_logs_error_on_high_loss(self, caplog):
        """AC-2: Logger emits [EPIC-059] marker when field loss detected."""
        raw_data = {
            "company_name": "Test Corp",
            "revenue": 100.0,
            "employees": 500,
            "growth_rate": 0.15,
        }

        financial = FinancialMetric(
            revenue=100.0,
            revenue_confidence=ConfidenceLevel.CONFIRMED,
            employees=None,
            employees_confidence=ConfidenceLevel.UNKNOWN,
            growth_rate=None,
            growth_confidence=ConfidenceLevel.UNKNOWN,
        )

        with caplog.at_level(logging.ERROR):
            _validate_financial_conversion(financial, raw_data)

        # Verify error was logged with EPIC-059 marker
        assert any("[EPIC-059]" in record.message for record in caplog.records)
        assert any("Conversion lost" in record.message for record in caplog.records)

    def test_converter_proceeds_on_validation_failure(self):
        """AC-3: Converter proceeds gracefully even when validation fails."""
        raw_data = {
            "company_name": "Incomplete Corp",
            "folder": "test-company",
            "industry": "Energy",
            "revenue": 100.0,
            "employees": 500,
            "growth_rate": 0.15,
            "profit_margin": 0.20,
            "funding_raised": None,  # Missing critical field
            "valuation": None,  # Missing critical field
        }

        # Should not raise exception despite validation failure
        company = convert_to_domain_company(raw_data, index=0)

        # Verify company was still created (AC-3: graceful degradation)
        assert company is not None
        assert company.name == "Incomplete Corp"
        assert company.financials.revenue == 100.0
        # Test validates that no exception was raised during conversion
    def test_converter_handles_none_fields_gracefully(self):
        """AC-4: No exceptions raised, financial metric returned with available data."""
        raw_data = {
            "company_name": "Minimal Corp",
            "folder": "minimal",
            "revenue": 1.0,  # Minimal revenue to satisfy validator
        }

        company = convert_to_domain_company(raw_data, index=0)

        # Should have created company with minimal financials
        assert company is not None
        assert company.name == "Minimal Corp"
        assert company.financials is not None
        assert company.financials.revenue == 1.0

    def test_validation_with_nested_data_format(self):
        """Validation works with nested data format (EPIC-058 compatibility)."""
        raw_data = {
            "company_name": "Nested Corp",
            "financials": {
                "revenue": {"value": 100.0, "currency": "EUR"},
                "employees": {"value": 500},
                "growth_rate": 0.15,
            },
        }

        financial = FinancialMetric(
            revenue=100.0,
            revenue_confidence=ConfidenceLevel.CONFIRMED,
            employees=500,
            employees_confidence=ConfidenceLevel.CONFIRMED,
            growth_rate=0.15,
            growth_confidence=ConfidenceLevel.ESTIMATED,
        )

        # Validation should pass (3 out of 6 critical fields present = 50% loss)
        # Actually, only 3 fields in raw_data critical list, so 3/3 = 0% loss
        is_valid = _validate_financial_conversion(financial, raw_data)

        # This should pass because only 3 fields expected, all present
        assert is_valid is True

    def test_validation_returns_true_when_no_expected_fields(self):
        """Validation returns True when raw data has no critical fields to lose."""
        raw_data = {
            "company_name": "Empty Corp",
            # No critical financial fields
        }

        financial = FinancialMetric(
            revenue=0.0,  # Must provide at least one to satisfy validator
            revenue_confidence=ConfidenceLevel.UNKNOWN,
            employees=None,
            employees_confidence=ConfidenceLevel.UNKNOWN,
        )

        # Should pass because there's nothing expected to lose (only revenue=0, no field in raw_data)
        is_valid = _validate_financial_conversion(financial, raw_data)

        assert is_valid is True
