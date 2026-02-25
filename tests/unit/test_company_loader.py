"""
Task 5: Tests for UnifiedCompanyScoreLoader

Ensures companies are loaded with merged JSON + Markdown data before scoring.
This fixes the revenue per employee bug by using unified financials.
"""

from unittest.mock import Mock, patch

import pytest

from solstein.analytics.company_loader import UnifiedCompanyScoreLoader
from solstein.domain.models import Company, FinancialMetric


class TestUnifiedCompanyScoreLoader:
    """Test suite for UnifiedCompanyScoreLoader."""

    @pytest.fixture
    def mock_unified_loader(self):
        """Create a mock unified loader."""
        return Mock()

    @pytest.fixture
    def loader(self, mock_unified_loader):
        """Create a loader with mocked unified loader."""
        with patch(
            "solstein.analytics.company_loader.UnifiedCompanyLoader",
            return_value=mock_unified_loader,
        ):
            loader = UnifiedCompanyScoreLoader()
            loader.unified_loader = mock_unified_loader
            return loader

    def test_initialization(self, loader):
        """Test that loader initializes with empty cache."""
        assert loader._unified_companies_cache is None
        assert loader.unified_loader is not None

    def test_load_company_for_scoring_first_call_loads_all(self, loader):
        """Test that first call loads all unified companies."""
        # Create mock companies
        company1 = Mock(spec=Company)
        company1.id = "comp-1"
        company2 = Mock(spec=Company)
        company2.id = "comp-2"

        loader.unified_loader.load_unified_companies.return_value = [
            company1,
            company2,
        ]

        # First call should load all companies
        result = loader.load_company_for_scoring("comp-1")

        assert result == company1
        assert loader._unified_companies_cache == {"comp-1": company1, "comp-2": company2}
        loader.unified_loader.load_unified_companies.assert_called_once()

    def test_load_company_for_scoring_uses_cache(self, loader):
        """Test that subsequent calls use cache."""
        # Pre-populate cache
        company1 = Mock(spec=Company)
        company1.id = "comp-1"
        loader._unified_companies_cache = {"comp-1": company1}

        # Call should use cache, not reload
        result = loader.load_company_for_scoring("comp-1")

        assert result == company1
        loader.unified_loader.load_unified_companies.assert_not_called()

    def test_load_company_for_scoring_not_found(self, loader):
        """Test loading a company that doesn't exist."""
        company1 = Mock(spec=Company)
        company1.id = "comp-1"

        loader.unified_loader.load_unified_companies.return_value = [company1]

        result = loader.load_company_for_scoring("comp-nonexistent")

        assert result is None

    def test_load_company_for_scoring_handles_load_failure(self, loader):
        """Test that loader handles failures gracefully."""
        loader.unified_loader.load_unified_companies.side_effect = Exception("Load failed")

        result = loader.load_company_for_scoring("comp-1")

        assert result is None
        assert loader._unified_companies_cache == {}

    def test_clear_cache(self, loader):
        """Test that cache can be cleared."""
        # Pre-populate cache
        company1 = Mock(spec=Company)
        company1.id = "comp-1"
        loader._unified_companies_cache = {"comp-1": company1}

        # Clear cache
        loader.clear_cache()

        assert loader._unified_companies_cache is None

    def test_load_company_reloads_after_clear(self, loader):
        """Test that cache is reloaded after clear."""
        company1 = Mock(spec=Company)
        company1.id = "comp-1"
        company2 = Mock(spec=Company)
        company2.id = "comp-2"

        loader.unified_loader.load_unified_companies.return_value = [
            company1,
            company2,
        ]

        # First load
        result1 = loader.load_company_for_scoring("comp-1")
        assert result1 == company1
        assert loader.unified_loader.load_unified_companies.call_count == 1

        # Clear cache
        loader.clear_cache()

        # Second load should reload
        result2 = loader.load_company_for_scoring("comp-1")
        assert result2 == company1
        assert loader.unified_loader.load_unified_companies.call_count == 2

    def test_load_multiple_companies_from_cache(self, loader):
        """Test loading multiple companies uses same cache."""
        company1 = Mock(spec=Company)
        company1.id = "comp-1"
        company2 = Mock(spec=Company)
        company2.id = "comp-2"

        loader.unified_loader.load_unified_companies.return_value = [
            company1,
            company2,
        ]

        # Load first company
        result1 = loader.load_company_for_scoring("comp-1")
        assert result1 == company1

        # Load second company (should use cache)
        result2 = loader.load_company_for_scoring("comp-2")
        assert result2 == company2

        # Verify load_unified_companies was called only once
        loader.unified_loader.load_unified_companies.assert_called_once()

    def test_global_instance_exists(self):
        """Test that global instance is created."""
        from solstein.analytics.company_loader import unified_score_loader

        assert unified_score_loader is not None
        assert isinstance(unified_score_loader, UnifiedCompanyScoreLoader)

    def test_load_company_with_real_financials(self, loader):
        """Test loading company with real financial data."""
        # Create a realistic company with financials
        financials = Mock(spec=FinancialMetric)
        financials.revenue = 450_000_000  # €450M
        financials.employees = 1600

        company = Mock(spec=Company)
        company.id = "envision-digital"
        company.name = "Envision Digital"
        company.financials = financials

        loader.unified_loader.load_unified_companies.return_value = [company]

        result = loader.load_company_for_scoring("envision-digital")

        assert result == company
        assert result.financials.revenue == 450_000_000
        assert result.financials.employees == 1600
        # Revenue per employee should be €281K (450M / 1600)
        assert result.financials.revenue / result.financials.employees == 281_250

    def test_empty_unified_companies_list(self, loader):
        """Test handling of empty unified companies list."""
        loader.unified_loader.load_unified_companies.return_value = []

        result = loader.load_company_for_scoring("comp-1")

        assert result is None
        assert loader._unified_companies_cache == {}

    def test_cache_populated_on_first_load(self, loader):
        """Test that cache is populated correctly on first load."""
        companies = [Mock(spec=Company, id=f"comp-{i}") for i in range(5)]
        loader.unified_loader.load_unified_companies.return_value = companies

        # Load first company
        loader.load_company_for_scoring("comp-0")

        # Verify all companies are in cache
        assert len(loader._unified_companies_cache) == 5
        for i, company in enumerate(companies):
            assert loader._unified_companies_cache[f"comp-{i}"] == company

    def test_load_company_with_none_cache_initializes(self, loader):
        """Test that None cache is properly initialized."""
        company = Mock(spec=Company)
        company.id = "comp-1"

        loader.unified_loader.load_unified_companies.return_value = [company]

        # Verify cache starts as None
        assert loader._unified_companies_cache is None

        # Load company
        result = loader.load_company_for_scoring("comp-1")

        # Verify cache is now initialized
        assert loader._unified_companies_cache is not None
        assert isinstance(loader._unified_companies_cache, dict)
        assert result == company

    def test_concurrent_load_calls_use_same_cache(self, loader):
        """Test that concurrent calls use the same cache."""
        company1 = Mock(spec=Company)
        company1.id = "comp-1"
        company2 = Mock(spec=Company)
        company2.id = "comp-2"

        loader.unified_loader.load_unified_companies.return_value = [
            company1,
            company2,
        ]

        # Simulate concurrent calls
        result1 = loader.load_company_for_scoring("comp-1")
        result2 = loader.load_company_for_scoring("comp-2")

        # Both should succeed and use same cache
        assert result1 == company1
        assert result2 == company2
        assert loader.unified_loader.load_unified_companies.call_count == 1

    def test_load_company_returns_none_on_empty_cache_after_error(self, loader):
        """Test that empty cache is set after error."""
        loader.unified_loader.load_unified_companies.side_effect = RuntimeError("Connection failed")

        result = loader.load_company_for_scoring("comp-1")

        assert result is None
        assert loader._unified_companies_cache == {}

        # Second call should not retry (cache is empty dict)
        result2 = loader.load_company_for_scoring("comp-1")
        assert result2 is None
        # Should still only be called once
        assert loader.unified_loader.load_unified_companies.call_count == 1
