"""
Integration tests for connector enrichment with REAL Company objects.

Tests the enrichment pipeline with actual Company model instances,
not fake fixtures. Verifies that:
1. Enrichment methods work with real Company objects
2. NULL fields are filled correctly
3. Existing data is never replaced
4. Errors are tracked properly
5. Enrichment sources are recorded
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock

from solstein.domain.models import Company, FinancialMetric, ConfidenceLevel
from solstein.data.unified_loader import UnifiedCompany, UnifiedCompanyLoader


class TestSECEdgarEnrichment:
    """Test SEC EDGAR enrichment with real Company objects."""

    def test_fill_nulls_from_sec_edgar_with_valid_ticker(self):
        """Test filling NULL fields from SEC EDGAR with valid ticker."""
        # Create a REAL Company object with NULL financials
        company = UnifiedCompany(
            id="AAPL",
            name="Apple Inc",
            ticker="AAPL",
            financials=FinancialMetric(
                revenue=None,  # NULL - should be filled
                growth_rate=None,  # NULL - should be filled
                employees=None,  # NULL - should be filled
                profit_margin=None,  # NULL - should be filled
            ),
        )

        # Mock SEC connector
        mock_sec = Mock()
        mock_sec.fetch_filing.return_value = {
            "revenue": 383285000000,
            "growth_rate": 0.08,
            "employees": 161000,
            "profit_margin": 0.25,
            "ebitda": 120000000000,
            "cash_position": 29000000000,
        }

        loader = UnifiedCompanyLoader(sec_connector=mock_sec)
        enriched = loader.fill_nulls_from_sec_edgar(company)

        # Verify fields were filled
        assert enriched.financials.revenue == 383285000000
        assert enriched.financials.growth_rate == 0.08
        assert enriched.financials.employees == 161000
        assert enriched.financials.profit_margin == 0.25

        # Verify confidence was set
        assert enriched.financials.revenue_confidence == ConfidenceLevel.CONFIRMED
        assert enriched.financials.growth_confidence == ConfidenceLevel.CONFIRMED
        assert enriched.financials.employees_confidence == ConfidenceLevel.CONFIRMED
        assert enriched.financials.margin_confidence == ConfidenceLevel.CONFIRMED

        # Verify enrichment tracking
        assert "SEC EDGAR" in enriched.enrichment_sources
        assert "SEC EDGAR" in enriched.enrichment_timestamps
        assert len(enriched.enrichment_errors) == 0

        # Verify data source tracking
        assert enriched.data_source_per_field.get("revenue") == "SEC EDGAR"
        assert enriched.data_source_per_field.get("growth_rate") == "SEC EDGAR"

    def test_fill_nulls_from_sec_edgar_never_replaces_existing(self):
        """Test that SEC EDGAR enrichment NEVER replaces existing data."""
        # Create a Company with EXISTING revenue
        company = UnifiedCompany(
            id="AAPL",
            name="Apple Inc",
            ticker="AAPL",
            financials=FinancialMetric(
                revenue=400000000000,  # EXISTING - should NOT be replaced
                growth_rate=None,  # NULL - should be filled
            ),
        )

        mock_sec = Mock()
        mock_sec.fetch_filing.return_value = {
            "revenue": 383285000000,  # Different value
            "growth_rate": 0.08,
        }

        loader = UnifiedCompanyLoader(sec_connector=mock_sec)
        enriched = loader.fill_nulls_from_sec_edgar(company)

        # Verify existing revenue was NOT replaced
        assert enriched.financials.revenue == 400000000000
        # Verify NULL growth_rate WAS filled
        assert enriched.financials.growth_rate == 0.08

    def test_fill_nulls_from_sec_edgar_skips_without_ticker(self):
        """Test that enrichment is skipped if no ticker."""
        company = UnifiedCompany(
            id="UNKNOWN",
            name="Unknown Company",
            ticker=None,  # No ticker
            financials=FinancialMetric(revenue=None),
        )

        mock_sec = Mock()
        loader = UnifiedCompanyLoader(sec_connector=mock_sec)
        enriched = loader.fill_nulls_from_sec_edgar(company)

        # Verify no enrichment happened
        assert enriched.financials.revenue is None
        assert "SEC EDGAR" not in enriched.enrichment_sources
        mock_sec.fetch_filing.assert_not_called()

    def test_fill_nulls_from_sec_edgar_handles_api_errors(self):
        """Test that API errors are caught and tracked."""
        company = UnifiedCompany(id="AAPL", name="Apple Inc", ticker="AAPL", financials=FinancialMetric(revenue=None))

        mock_sec = Mock()
        # Simulate all year attempts failing
        mock_sec.fetch_filing.side_effect = RuntimeError("SEC API rate limit exceeded")

        loader = UnifiedCompanyLoader(sec_connector=mock_sec)
        enriched = loader.fill_nulls_from_sec_edgar(company)

        # Verify error was tracked (after all retries failed)
        assert len(enriched.enrichment_errors) == 1
        assert "SEC EDGAR" in enriched.enrichment_errors[0]
        # Verify no data was filled
        assert enriched.financials.revenue is None


class TestCompaniesHouseEnrichment:
    """Test Companies House enrichment with real Company objects."""

    def test_fill_nulls_from_companies_house_with_valid_number(self):
        """Test filling NULL fields from Companies House with valid company_number."""
        company = UnifiedCompany(
            id="ACME-UK",
            name="ACME Ltd",
            company_number="01234567",
            financials=FinancialMetric(
                revenue=None,
                employees=None,
                profit_margin=None,
            ),
        )

        mock_ch = Mock()
        mock_ch.get_company_metrics.return_value = {
            "revenue": 50000000,
            "employees": 250,
            "profit_margin": 0.15,
        }

        loader = UnifiedCompanyLoader(companies_house_connector=mock_ch)
        enriched = loader.fill_nulls_from_companies_house(company)

        # Verify fields were filled
        assert enriched.financials.revenue == 58500000  # 50M GBP * 1.17 EUR/GBP
        assert enriched.financials.employees == 250
        assert enriched.financials.profit_margin == 0.15

        # Verify enrichment tracking
        assert "Companies House" in enriched.enrichment_sources
        assert "Companies House" in enriched.enrichment_timestamps
        assert len(enriched.enrichment_errors) == 0

    def test_fill_nulls_from_companies_house_skips_without_number(self):
        """Test that enrichment is skipped if no company_number."""
        company = UnifiedCompany(
            id="ACME-UK",
            name="ACME Ltd",
            company_number=None,  # No company number
            financials=FinancialMetric(revenue=None),
        )

        mock_ch = Mock()
        loader = UnifiedCompanyLoader(companies_house_connector=mock_ch)
        enriched = loader.fill_nulls_from_companies_house(company)

        # Verify no enrichment happened
        assert enriched.financials.revenue is None
        assert "Companies House" not in enriched.enrichment_sources
        mock_ch.get_company_metrics.assert_not_called()


class TestNewsSignalEnrichment:
    """Test News Signal enrichment with real Company objects."""

    def test_attach_news_signals_handles_api_errors(self):
        """Test that news API errors are caught and tracked."""
        company = UnifiedCompany(
            id="STARTUP",
            name="TechStartup Inc",
        )

        mock_news = Mock()
        mock_news.detect_funding_signal.side_effect = RuntimeError("NewsAPI rate limit")
        mock_news.detect_partnership_signal.return_value = None
        mock_news.detect_key_hire_signal.return_value = None

        loader = UnifiedCompanyLoader(news_detector=mock_news)
        enriched = loader.attach_news_signals(company)

        # Verify error was tracked
        assert len(enriched.enrichment_errors) == 1
        assert "News Signals" in enriched.enrichment_errors[0]


class TestEnrichmentPipeline:
    """Test the complete enrichment pipeline."""

    def test_enrich_from_connectors_calls_all_enrichers(self):
        """Test that enrich_from_connectors calls all enrichment methods."""
        company = UnifiedCompany(
            id="MIXED",
            name="Mixed Company",
            ticker="MIXED",
            company_number="98765432",
            financials=FinancialMetric(
                revenue=None,
                employees=None,
            ),
        )

        # Mock all connectors
        mock_sec = Mock()
        mock_sec.fetch_filing.return_value = {
            "revenue": 100000000,
            "employees": 500,
        }

        mock_ch = Mock()
        mock_ch.get_company_metrics.return_value = {
            "revenue": 100000000,
            "employees": 500,
        }

        mock_news = Mock()
        mock_news.detect_funding_signal.return_value = None
        mock_news.detect_partnership_signal.return_value = None
        mock_news.detect_key_hire_signal.return_value = None

        loader = UnifiedCompanyLoader(
            sec_connector=mock_sec, companies_house_connector=mock_ch, news_detector=mock_news
        )

        enriched = loader.enrich_from_connectors(company)

        # Verify all enrichers were called
        mock_sec.fetch_filing.assert_called_once()
        mock_ch.get_company_metrics.assert_called_once()
        mock_news.detect_funding_signal.assert_called_once()

        # Verify data was filled
        assert enriched.financials.revenue == 100000000
        assert enriched.financials.employees == 500

        # Verify enrichment sources recorded (SEC fills first, then CH doesn't replace)
        assert "SEC EDGAR" in enriched.enrichment_sources

    def test_enrich_from_connectors_graceful_failure(self):
        """Test that enrichment continues even if one connector fails."""
        company = UnifiedCompany(
            id="PART",
            name="Partial Company",
            ticker="PART",
            company_number="11111111",
            financials=FinancialMetric(revenue=None, employees=None),
        )

        # SEC fails, CH succeeds
        mock_sec = Mock()
        mock_sec.fetch_filing.side_effect = RuntimeError("SEC API down")

        mock_ch = Mock()
        mock_ch.get_company_metrics.return_value = {
            "revenue": 50000000,
            "employees": 200,
        }

        mock_news = Mock()
        mock_news.detect_funding_signal.return_value = None
        mock_news.detect_partnership_signal.return_value = None
        mock_news.detect_key_hire_signal.return_value = None

        loader = UnifiedCompanyLoader(
            sec_connector=mock_sec, companies_house_connector=mock_ch, news_detector=mock_news
        )

        enriched = loader.enrich_from_connectors(company)

        # Verify SEC error was tracked
        assert len(enriched.enrichment_errors) == 1
        assert "SEC EDGAR" in enriched.enrichment_errors[0]

        # Verify CH data was still filled
        assert enriched.financials.revenue == 58500000  # 50M GBP * 1.17 EUR/GBP
        assert enriched.financials.employees == 200
        assert "Companies House" in enriched.enrichment_sources


class TestEnrichmentWithoutConnectors:
    """Test enrichment behavior when connectors are not available."""

    def test_enrichment_skipped_when_no_connectors(self):
        """Test that enrichment is gracefully skipped when connectors unavailable."""
        company = UnifiedCompany(
            id="NOCON", name="No Connector Company", ticker="NOCON", financials=FinancialMetric(revenue=None)
        )

        # Create loader with NO connectors
        loader = UnifiedCompanyLoader(sec_connector=None, companies_house_connector=None, news_detector=None)

        enriched = loader.enrich_from_connectors(company)

        # Verify no enrichment happened
        assert enriched.financials.revenue is None
        assert len(enriched.enrichment_sources) == 0
        assert len(enriched.enrichment_errors) == 0  # No errors when connectors unavailable - just graceful skip
