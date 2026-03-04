"""Tests for synthetic data detection and blocking functionality."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from solstein.domain.models import Company
from solstein.exceptions import SyntheticDataBlockingError
from solstein.exporters.markdown.generator import ReportGenerator


class TestSyntheticDataGate:
    """Test suite for synthetic data detection and blocking."""

    def setup_method(self):
        """Setup test fixtures."""
        self.generator = ReportGenerator(output_dir=Path("/tmp/test"))

    def test_check_data_authenticity_no_synthetic(self):
        """Test that authentic data passes validation."""
        # Create authentic companies
        companies = [
            Company(id="1", name="Real Company 1", data_source_type="api"),
            Company(id="2", name="Real Company 2", data_source_type="manual"),
        ]

        # Should return True with empty warning
        is_authentic, warning = self.generator._check_data_authenticity(companies)

        assert is_authentic is True
        assert warning == ""

    def test_check_data_authenticity_synthetic_by_source(self):
        """Test detection of synthetic data by source type."""
        # Create synthetic company via source type
        companies = [
            Company(id="1", name="Real Company", data_source_type="api"),
            Company(id="2", name="Test Company", data_source_type="synthetic"),
        ]

        # Should raise exception
        with pytest.raises(SyntheticDataBlockingError) as exc_info:
            self.generator._check_data_authenticity(companies)

        assert "Found 1 out of 2 companies" in str(exc_info.value)
        assert "synthetic data" in str(exc_info.value).lower()
        assert "Test Company" in str(exc_info.value)

    def test_check_data_authenticity_synthetic_by_name_pattern(self):
        """Test detection of synthetic data by name patterns."""
        # Test various synthetic name patterns
        test_cases = [
            "test-company-inc",
            "test_company_llc",
            "synthetic-corp",
            "fake-enterprise",
            "TEST_COMPANY",  # case insensitive
            "SYNTHETIC CORP",
        ]

        for pattern in test_cases:
            companies = [Company(id="1", name=pattern, data_source_type="api")]

            with pytest.raises(SyntheticDataBlockingError) as exc_info:
                self.generator._check_data_authenticity(companies)

            assert pattern.lower() in str(exc_info.value).lower()

    def test_check_data_authenticity_multiple_synthetic(self):
        """Test detection of multiple synthetic companies."""
        companies = [
            Company(id="1", name="Real Company", data_source_type="api"),
            Company(id="2", name="test-company-1", data_source_type="api"),
            Company(id="3", name="test-company-2", data_source_type="synthetic"),
            Company(id="4", name="synthetic-corp", data_source_type="api"),
        ]

        with pytest.raises(SyntheticDataBlockingError) as exc_info:
            self.generator._check_data_authenticity(companies)

        error_message = str(exc_info.value)
        assert "Found 3 out of 4 companies" in error_message

        # Should mention synthetic names
        assert "test-company-1" in error_message or "test-company-2" in error_message

    def test_check_data_authenticity_no_name_attribute(self):
        """Test handling of companies without name attribute."""
        # Create company without name attribute
        company = Mock()
        company.id = "1"
        company.data_source_type = "synthetic"
        company.name = None

        with pytest.raises(SyntheticDataBlockingError) as exc_info:
            self.generator._check_data_authenticity([company])

        assert "Unknown" in str(exc_info.value)

    def test_check_data_authenticity_empty_list(self):
        """Test validation of empty company list."""
        is_authentic, warning = self.generator._check_data_authenticity([])

        assert is_authentic is True
        assert warning == ""

    def test_check_data_authenticity_mixed_sources_and_names(self):
        """Test detection with mixed synthetic indicators."""
        companies = [
            Company(id="1", name="Real Company", data_source_type="api"),  # OK
            Company(id="2", name="Real Company 2", data_source_type="synthetic"),  # Synthetic by source
            Company(id="3", name="synthetic-real", data_source_type="api"),  # Synthetic by name
            Company(id="4", name="test-company", data_source_type="synthetic"),  # Both indicators
        ]

        with pytest.raises(SyntheticDataBlockingError) as exc_info:
            self.generator._check_data_authenticity(companies)

        error_message = str(exc_info.value)
        assert "Found 3 out of 4 companies" in error_message
        assert "(75.0%)" in error_message

    def test_synthetic_detection_real_but_suspicious_names(self):
        """Test that real companies with suspicious substrings are NOT flagged.

        Edge case: names containing but not exactly matching patterns.
        """
        # These should NOT be flagged as synthetic (they contain but don't START with patterns)
        companies = [
            Company(id="1", name="Atest Company B", data_source_type="api"),  # Contains "test" but not at start
            Company(
                id="2", name="Best Synthetic Resins", data_source_type="api"
            ),  # Contains "synthetic" but not at start
            Company(id="3", name="The Fake News", data_source_type="api"),  # Contains "fake" but not at start
        ]

        is_authentic, warning = self.generator._check_data_authenticity(companies)

        assert is_authentic is True
        assert warning == ""

    def test_check_data_authenticity_partial_matches(self):
        """Test that partial matches don't trigger synthetic detection."""
        companies = [
            Company(id="1", name="ATestosterone Corp", data_source_type="api"),  # Starts with A, not exactly test-
            Company(id="2", name="Best-in-Class LLC", data_source_type="api"),  # Contains "test" but not at start
            Company(id="3", name="Asynthetic Polymer", data_source_type="api"),  # Starts with A, not exactly synthetic
        ]

        is_authentic, warning = self.generator._check_data_authenticity(companies)

        assert is_authentic is True
        assert warning == ""

    def test_synthetic_data_blocking_error_inheritance(self):
        """Test that SyntheticDataBlockingError is a proper subclass."""
        error = SyntheticDataBlockingError("Test error")

        # Should be instance of SolsteinError
        from solstein.exceptions import SolsteinError

        assert isinstance(error, SolsteinError)

        # Should have proper string representation
        assert "Test error" in str(error)
