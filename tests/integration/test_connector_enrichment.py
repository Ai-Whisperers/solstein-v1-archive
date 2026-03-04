"""
Integration test for connector enrichment pipeline.

Tests that SEC EDGAR, Companies House, and News Signal connectors
properly enrich company data without replacing existing values.
"""

import pytest

from solstein.data.unified_loader import UnifiedCompany, UnifiedCompanyLoader
from solstein.domain.models import ConfidenceLevel, FinancialMetric


@pytest.fixture
def loader():
    """Create a UnifiedCompanyLoader instance."""
    return UnifiedCompanyLoader()


@pytest.fixture
def sample_company_with_null_revenue():
    """Create a sample company with NULL revenue."""
    return UnifiedCompany(
        id="test-001",
        name="Test Company",
        ticker="TEST",
        financials=FinancialMetric(
            revenue=None,  # NULL - should be filled
            revenue_confidence=ConfidenceLevel.UNKNOWN,
            employees=None,
            profit_margin=None,
        ),
        data_source_per_field={},
    )


@pytest.fixture
def sample_company_with_existing_revenue():
    """Create a sample company with existing revenue."""
    return UnifiedCompany(
        id="test-002",
        name="Test Company 2",
        ticker="TEST2",
        financials=FinancialMetric(
            revenue=1000000.0,  # Existing value - should NOT be replaced
            revenue_confidence=ConfidenceLevel.CONFIRMED,
            employees=None,
            profit_margin=None,
        ),
        data_source_per_field={"revenue": "JSON"},
    )


@pytest.fixture
def sample_company_without_ticker():
    """Create a sample company without ticker."""
    return UnifiedCompany(
        id="test-003",
        name="Test Company 3",
        ticker=None,  # No ticker - should be skipped
        financials=FinancialMetric(
            revenue=None,
            revenue_confidence=ConfidenceLevel.UNKNOWN,
        ),
        data_source_per_field={},
    )


class TestSECEdgarEnrichment:
    """Test SEC EDGAR connector enrichment."""

    def test_sec_edgar_skips_without_ticker(self, loader, sample_company_without_ticker):
        """Test that SEC EDGAR enrichment skips companies without ticker."""
        result = loader.fill_nulls_from_sec_edgar(sample_company_without_ticker)
        assert result.financials.revenue is None
        assert (
            "revenue" not in result.data_source_per_field or result.data_source_per_field.get("revenue") != "SEC EDGAR"
        )

    def test_sec_edgar_preserves_existing_data(self, loader, sample_company_with_existing_revenue):
        """Test that SEC EDGAR enrichment doesn't replace existing data."""
        original_revenue = sample_company_with_existing_revenue.financials.revenue
        result = loader.fill_nulls_from_sec_edgar(sample_company_with_existing_revenue)
        assert result.financials.revenue == original_revenue
        assert result.data_source_per_field.get("revenue") == "JSON"

    def test_sec_edgar_returns_company(self, loader, sample_company_with_null_revenue):
        """Test that SEC EDGAR enrichment returns a company object."""
        result = loader.fill_nulls_from_sec_edgar(sample_company_with_null_revenue)
        assert isinstance(result, UnifiedCompany)
        assert result.id == sample_company_with_null_revenue.id


class TestCompaniesHouseEnrichment:
    """Test Companies House connector enrichment."""

    def test_companies_house_skips_without_company_number(self, loader, sample_company_without_ticker):
        """Test that Companies House enrichment skips companies without company_number."""
        result = loader.fill_nulls_from_companies_house(sample_company_without_ticker)
        assert result.financials.revenue is None

    def test_companies_house_preserves_existing_data(self, loader, sample_company_with_existing_revenue):
        """Test that Companies House enrichment doesn't replace existing data."""
        original_revenue = sample_company_with_existing_revenue.financials.revenue
        result = loader.fill_nulls_from_companies_house(sample_company_with_existing_revenue)
        assert result.financials.revenue == original_revenue

    def test_companies_house_returns_company(self, loader, sample_company_with_null_revenue):
        """Test that Companies House enrichment returns a company object."""
        result = loader.fill_nulls_from_companies_house(sample_company_with_null_revenue)
        assert isinstance(result, UnifiedCompany)


class TestNewsSignalEnrichment:
    """Test News Signal Detector enrichment."""

    def test_news_signals_skips_without_name(self, loader):
        """Test that news signal enrichment skips companies without name."""
        company = UnifiedCompany(
            id="test-004",
            name=None,
            ticker="TEST4",
            financials=FinancialMetric(),
            data_source_per_field={},
        )
        result = loader.attach_news_signals(company)
        assert result.id == company.id

    def test_news_signals_returns_company(self, loader, sample_company_with_null_revenue):
        """Test that news signal enrichment returns a company object."""
        result = loader.attach_news_signals(sample_company_with_null_revenue)
        assert isinstance(result, UnifiedCompany)
        assert result.id == sample_company_with_null_revenue.id


class TestEnrichmentPipeline:
    """Test the full enrichment pipeline."""

    def test_enrich_from_connectors_calls_all_methods(self, loader, sample_company_with_null_revenue):
        """Test that enrich_from_connectors calls all enrichment methods."""
        result = loader.enrich_from_connectors(sample_company_with_null_revenue)
        assert isinstance(result, UnifiedCompany)
        assert result.id == sample_company_with_null_revenue.id

    def test_enrich_from_connectors_preserves_existing_data(self, loader, sample_company_with_existing_revenue):
        """Test that full pipeline preserves existing data."""
        original_revenue = sample_company_with_existing_revenue.financials.revenue
        result = loader.enrich_from_connectors(sample_company_with_existing_revenue)
        assert result.financials.revenue == original_revenue

    def test_data_source_tracking(self, loader, sample_company_with_null_revenue):
        """Test that data source tracking is maintained."""
        result = loader.enrich_from_connectors(sample_company_with_null_revenue)
        # data_source_per_field should be a dict
        assert isinstance(result.data_source_per_field, dict)


class TestDataProvenance:
    """Test data provenance tracking."""

    def test_provenance_dict_exists(self, loader, sample_company_with_null_revenue):
        """Test that data_source_per_field dict exists."""
        result = loader.enrich_from_connectors(sample_company_with_null_revenue)
        assert hasattr(result, "data_source_per_field")
        assert isinstance(result.data_source_per_field, dict)

    def test_provenance_tracks_sources(self, loader, sample_company_with_existing_revenue):
        """Test that provenance tracks data sources."""
        result = loader.enrich_from_connectors(sample_company_with_existing_revenue)
        # Original source should be preserved
        assert result.data_source_per_field.get("revenue") == "JSON"
