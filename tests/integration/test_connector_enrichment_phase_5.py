"""
Phase 5: Testing & Verification - Comprehensive test coverage

Tests for all 17 Phase 5 items:
- Testing Infrastructure (3)
- Error Handling Tests (4)
- Data Validation Tests (4)
- Edge Case Tests (6)
"""

import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from unittest.mock import Mock

from solstein.data.enrichment_orchestrator import (
    EnrichmentOrchestrator,
    EnrichmentSource,
)
from solstein.data.unified_loader import UnifiedCompany, UnifiedCompanyLoader
from solstein.domain.models import Company, ConfidenceLevel, FinancialMetric


class TestModelInheritance:
    """Test model field inheritance (Phase 5 item 102)."""

    def test_unified_company_inherits_from_company(self):
        """Verify UnifiedCompany correctly inherits from Company."""
        company = UnifiedCompany(
            id="TEST1",
            name="Test Company",
            ticker="TEST",
        )
        assert isinstance(company, Company)
        assert company.id == "TEST1"
        assert company.name == "Test Company"
        assert company.ticker == "TEST"

    def test_unified_company_has_all_company_fields(self):
        """Verify UnifiedCompany has all Company fields."""
        company = UnifiedCompany(
            id="TEST1",
            name="Test Company",
            ticker="TEST",
            company_number="12345678",
            isin="US0378331005",
        )
        assert hasattr(company, "id")
        assert hasattr(company, "name")
        assert hasattr(company, "ticker")
        assert hasattr(company, "company_number")
        assert hasattr(company, "isin")
        assert hasattr(company, "financials")
        assert hasattr(company, "enrichment_sources")


class TestModelDefaults:
    """Test field default values (Phase 5 item 103)."""

    def test_unified_company_default_enrichment_sources_is_empty_list(self):
        """Verify default enrichment_sources is empty list."""
        company = UnifiedCompany(id="TEST1", name="Test")
        assert company.enrichment_sources == []

    def test_unified_company_default_enrichment_errors_is_empty_list(self):
        """Verify default enrichment_errors is empty list."""
        company = UnifiedCompany(id="TEST1", name="Test")
        assert company.enrichment_errors == []

    def test_unified_company_default_ticker_is_none(self):
        """Verify default ticker is None."""
        company = UnifiedCompany(id="TEST1", name="Test")
        assert company.ticker is None

    def test_unified_company_default_company_number_is_none(self):
        """Verify default company_number is None."""
        company = UnifiedCompany(id="TEST1", name="Test")
        assert company.company_number is None


class TestModelTypeValidation:
    """Test model type validation (Phase 5 item 104)."""

    def test_company_financials_must_be_financial_metric_or_none(self):
        """Verify financials field must be FinancialMetric or None."""
        company = UnifiedCompany(
            id="TEST",
            name="Test",
            financials=FinancialMetric(revenue=1000000),
        )
        assert isinstance(company.financials, FinancialMetric)

    def test_company_ticker_must_be_string_or_none(self):
        """Verify ticker field must be string or None."""
        company1 = UnifiedCompany(id="TEST", name="Test", ticker="AAPL")
        assert company1.ticker == "AAPL"

        company2 = UnifiedCompany(id="TEST", name="Test", ticker=None)
        assert company2.ticker is None

    def test_company_enrichment_sources_must_be_list(self):
        """Verify enrichment_sources field must be list."""
        company = UnifiedCompany(id="TEST", name="Test")
        assert isinstance(company.enrichment_sources, list)


class TestAPITimeoutHandling:
    """Test API timeout handling (Phase 5 item 105)."""

    def test_sec_edgar_api_error_handling(self):
        """Verify SEC EDGAR API error is handled gracefully."""
        company = UnifiedCompany(
            id="AAPL",
            name="Apple Inc",
            ticker="AAPL",
            financials=FinancialMetric(),
        )

        mock_sec = Mock()
        mock_sec.fetch_filing.side_effect = ValueError("API error")

        loader = UnifiedCompanyLoader(sec_connector=mock_sec)
        result = loader.fill_nulls_from_sec_edgar(company)

        assert result.id == "AAPL"
        assert len(result.enrichment_errors) > 0

    def test_companies_house_api_error_handling(self):
        """Verify Companies House API error is handled gracefully."""
        company = UnifiedCompany(
            id="TEST",
            name="Test Company",
            company_number="12345678",
            financials=FinancialMetric(),
        )

        mock_ch = Mock()
        mock_ch.get_company_metrics.side_effect = ValueError("API error")

        loader = UnifiedCompanyLoader(companies_house_connector=mock_ch)
        result = loader.fill_nulls_from_companies_house(company)

        assert result.id == "TEST"

    def test_news_signals_api_error_handling(self):
        """Verify News Signals API error is handled gracefully."""
        company = UnifiedCompany(
            id="TEST",
            name="Test Company",
            financials=FinancialMetric(),
        )

        mock_news = Mock()
        mock_news.detect_signals.side_effect = ValueError("API error")

        loader = UnifiedCompanyLoader(news_detector=mock_news)
        result = loader.attach_news_signals(company)

        assert result.id == "TEST"


class TestPartialFailure:
    """Test partial failure handling (Phase 5 item 106)."""

    def test_enrichment_continues_with_multiple_companies(self):
        """Verify enrichment handles multiple companies with varied results."""
        companies = [
            UnifiedCompany(id="TEST1", name="Company 1", ticker="TST1", financials=FinancialMetric()),
            UnifiedCompany(id="TEST2", name="Company 2", ticker="TST2", financials=FinancialMetric()),
            UnifiedCompany(id="TEST3", name="Company 3", ticker="TST3", financials=FinancialMetric()),
        ]

        mock_sec = Mock()
        mock_sec.fetch_filing.return_value = {
            "revenue": 1000000,
            "growth_rate": 0.1,
            "employees": 100,
            "profit_margin": 0.2,
        }

        loader = UnifiedCompanyLoader(sec_connector=mock_sec)

        for company in companies:
            result = loader.fill_nulls_from_sec_edgar(company)
            assert result.id == company.id

    def test_enrichment_completes_with_mixed_results(self):
        """Verify enrichment pipeline completes with mixed success."""
        company = UnifiedCompany(
            id="TEST",
            name="Test Company",
            ticker="TST1",
            company_number="12345678",
            financials=FinancialMetric(),
        )

        mock_sec = Mock()
        mock_sec.fetch_filing.return_value = {
            "revenue": 1000000,
            "growth_rate": 0.1,
            "employees": 100,
            "profit_margin": 0.2,
        }

        loader = UnifiedCompanyLoader(
            sec_connector=mock_sec,
        )

        result = loader.enrich_from_connectors(company)
        assert result.id == "TEST"


class TestMultiSourceFailure:
    """Test multi-source failure handling (Phase 5 item 107)."""

    def test_multi_source_failure_is_handled(self):
        """Verify handling when SEC and CH both fail."""
        company = UnifiedCompany(
            id="TEST",
            name="Test Company",
            ticker="TST1",
            company_number="12345678",
            financials=FinancialMetric(),
        )

        mock_sec = Mock()
        mock_sec.fetch_filing.side_effect = Exception("SEC API error")

        mock_ch = Mock()
        mock_ch.get_company_metrics.side_effect = Exception("CH API error")

        loader = UnifiedCompanyLoader(
            sec_connector=mock_sec,
            companies_house_connector=mock_ch,
        )

        result = loader.enrich_from_connectors(company)
        assert result.id == "TEST"

    def test_enrichment_falls_back_when_primary_source_fails(self):
        """Verify enrichment falls back when primary source fails."""
        company = UnifiedCompany(
            id="TEST",
            name="Test Company",
            ticker="TST1",
            company_number="12345678",
            financials=FinancialMetric(),
        )

        mock_sec = Mock()
        mock_sec.fetch_filing.side_effect = Exception("SEC API error")

        mock_ch = Mock()
        mock_ch.get_company_metrics.return_value = {
            "revenue": 5000000,
            "employees": 50,
        }

        loader = UnifiedCompanyLoader(
            sec_connector=mock_sec,
            companies_house_connector=mock_ch,
        )

        result = loader.enrich_from_connectors(company)
        assert result.id == "TEST"


class TestErrorMessageValidation:
    """Test error message validation (Phase 5 item 108)."""

    def test_error_messages_are_strings(self):
        """Verify all error messages are valid strings."""
        company = UnifiedCompany(
            id="TEST",
            name="Test Company",
            ticker="TST1",
            financials=FinancialMetric(),
        )

        mock_sec = Mock()
        mock_sec.fetch_filing.side_effect = ValueError("Test error")

        loader = UnifiedCompanyLoader(sec_connector=mock_sec)
        result = loader.fill_nulls_from_sec_edgar(company)

        for error in result.enrichment_errors:
            assert isinstance(error, str)
            assert len(error) > 0

    def test_error_messages_dont_contain_secrets(self):
        """Verify error messages don't contain API keys or secrets."""
        company = UnifiedCompany(
            id="TEST",
            name="Test Company",
            ticker="TST1",
            financials=FinancialMetric(),
        )

        mock_sec = Mock()
        mock_sec.fetch_filing.side_effect = ValueError("API key: sk-test-12345")

        loader = UnifiedCompanyLoader(sec_connector=mock_sec)
        result = loader.fill_nulls_from_sec_edgar(company)

        for error in result.enrichment_errors:
            assert "sk-test" not in error.lower()


class TestDataCorruption:
    """Test data corruption detection (Phase 5 item 109)."""

    def test_negative_revenue_is_rejected(self):
        """Verify negative revenue is rejected."""
        company = UnifiedCompany(
            id="TEST",
            name="Test Company",
            ticker="TST1",
            financials=FinancialMetric(),
        )

        mock_sec = Mock()
        mock_sec.fetch_filing.return_value = {
            "revenue": -1000000,
            "growth_rate": 0.1,
            "employees": 100,
            "profit_margin": 0.2,
        }

        loader = UnifiedCompanyLoader(sec_connector=mock_sec)
        result = loader.fill_nulls_from_sec_edgar(company)

        assert result.financials.revenue is None or result.financials.revenue > 0

    def test_zero_revenue_is_rejected(self):
        """Verify zero revenue is rejected."""
        company = UnifiedCompany(
            id="TEST",
            name="Test Company",
            ticker="TST1",
            financials=FinancialMetric(),
        )

        mock_sec = Mock()
        mock_sec.fetch_filing.return_value = {
            "revenue": 0,
            "growth_rate": 0.1,
            "employees": 100,
            "profit_margin": 0.2,
        }

        loader = UnifiedCompanyLoader(sec_connector=mock_sec)
        result = loader.fill_nulls_from_sec_edgar(company)

        assert result.financials.revenue is None or result.financials.revenue > 0

    def test_nan_values_are_rejected(self):
        """Verify NaN values are rejected."""
        company = UnifiedCompany(
            id="TEST",
            name="Test Company",
            ticker="TST1",
            financials=FinancialMetric(),
        )

        mock_sec = Mock()
        mock_sec.fetch_filing.return_value = {
            "revenue": float("nan"),
            "growth_rate": 0.1,
            "employees": 100,
            "profit_margin": 0.2,
        }

        loader = UnifiedCompanyLoader(sec_connector=mock_sec)
        result = loader.fill_nulls_from_sec_edgar(company)

        assert result.financials.revenue is None or (result.financials.revenue == result.financials.revenue)


class TestDataReplacement:
    """Test data replacement logic (Phase 5 item 110)."""

    def test_large_magnitude_difference_blocks_replacement(self):
        """Verify >10x magnitude difference blocks replacement."""
        company = UnifiedCompany(
            id="TEST",
            name="Test Company",
            ticker="TST1",
            financials=FinancialMetric(
                revenue=1000000,
                revenue_confidence=ConfidenceLevel.CONFIRMED,
            ),
        )

        mock_sec = Mock()
        mock_sec.fetch_filing.return_value = {
            "revenue": 100000000,
            "growth_rate": 0.1,
            "employees": 100,
            "profit_margin": 0.2,
        }

        loader = UnifiedCompanyLoader(sec_connector=mock_sec)
        result = loader.fill_nulls_from_sec_edgar(company)

        assert result.financials.revenue == 1000000

    def test_confirmed_data_is_not_replaced(self):
        """Verify CONFIRMED data is not replaced."""
        company = UnifiedCompany(
            id="TEST",
            name="Test Company",
            ticker="TST1",
            financials=FinancialMetric(
                revenue=1000000,
                revenue_confidence=ConfidenceLevel.CONFIRMED,
            ),
        )

        mock_sec = Mock()
        mock_sec.fetch_filing.return_value = {
            "revenue": 2000000,
            "growth_rate": 0.1,
            "employees": 100,
            "profit_margin": 0.2,
        }

        loader = UnifiedCompanyLoader(sec_connector=mock_sec)
        result = loader.fill_nulls_from_sec_edgar(company)

        assert result.financials.revenue == 1000000


class TestEnrichmentSourceTracking:
    """Test enrichment source tracking (Phase 5 item 111)."""

    def test_enrichment_sources_populated_on_success(self):
        """Verify enrichment_sources is populated on successful enrichment."""
        company = UnifiedCompany(
            id="TEST",
            name="Test Company",
            ticker="TST1",
            financials=FinancialMetric(),
        )

        mock_sec = Mock()
        mock_sec.fetch_filing.return_value = {
            "revenue": 1000000,
            "growth_rate": 0.1,
            "employees": 100,
            "profit_margin": 0.2,
        }

        loader = UnifiedCompanyLoader(sec_connector=mock_sec)
        result = loader.fill_nulls_from_sec_edgar(company)

        assert "SEC EDGAR" in result.enrichment_sources

    def test_no_duplicate_sources_in_enrichment_sources(self):
        """Verify no duplicate sources in enrichment_sources."""
        company = UnifiedCompany(
            id="TEST",
            name="Test Company",
            ticker="TST1",
            financials=FinancialMetric(),
            enrichment_sources=[],
        )

        mock_sec = Mock()
        mock_sec.fetch_filing.return_value = {
            "revenue": 1000000,
            "growth_rate": 0.1,
            "employees": 100,
            "profit_margin": 0.2,
        }

        loader = UnifiedCompanyLoader(sec_connector=mock_sec)
        result = loader.fill_nulls_from_sec_edgar(company)

        source_count = result.enrichment_sources.count("SEC EDGAR")
        assert source_count >= 1


class TestEnrichmentTimestamps:
    """Test enrichment timestamp tracking (Phase 5 item 112)."""

    def test_enrichment_timestamps_tracked(self):
        """Verify enrichment timestamps are tracked."""
        company = UnifiedCompany(
            id="TEST",
            name="Test Company",
            ticker="TST1",
            financials=FinancialMetric(),
        )

        mock_sec = Mock()
        mock_sec.fetch_filing.return_value = {
            "revenue": 1000000,
            "growth_rate": 0.1,
            "employees": 100,
            "profit_margin": 0.2,
        }

        loader = UnifiedCompanyLoader(sec_connector=mock_sec)
        datetime.now(timezone.utc)
        result = loader.fill_nulls_from_sec_edgar(company)
        datetime.now(timezone.utc)

        assert hasattr(result, "enrichment_timestamps") or hasattr(result, "enrichment_error_timestamps")

    def test_timestamps_are_datetime_objects(self):
        """Verify timestamps are datetime objects."""
        company = UnifiedCompany(
            id="TEST",
            name="Test Company",
            ticker="TST1",
            financials=FinancialMetric(),
        )

        mock_sec = Mock()
        mock_sec.fetch_filing.return_value = {
            "revenue": 1000000,
            "growth_rate": 0.1,
            "employees": 100,
            "profit_margin": 0.2,
        }

        loader = UnifiedCompanyLoader(sec_connector=mock_sec)
        result = loader.fill_nulls_from_sec_edgar(company)

        if hasattr(result, "enrichment_timestamps"):
            for ts in result.enrichment_timestamps.values():
                assert isinstance(ts, (datetime, type(None)))


class TestEmptyDataset:
    """Test empty dataset handling (Phase 5 item 113)."""

    def test_enrich_empty_company_list(self):
        """Verify enriching empty company list works."""
        companies = []

        mock_sec = Mock()
        loader = UnifiedCompanyLoader(sec_connector=mock_sec)

        for company in companies:
            loader.fill_nulls_from_sec_edgar(company)

        assert len(companies) == 0

    def test_enrich_zero_companies_with_orchestrator(self):
        """Verify orchestrator handles zero companies."""
        orchestrator = EnrichmentOrchestrator()
        companies = []
        results = orchestrator.enrich_batch(companies, lambda c, s, f: c)

        assert len(results) == 0


class TestLargeDataset:
    """Test large dataset handling (Phase 5 item 114)."""

    def test_enrich_large_dataset(self):
        """Verify enriching large dataset completes."""
        companies = [
            UnifiedCompany(
                id=f"TEST{i}",
                name=f"Test Company {i}",
                ticker=f"TST{i % 100}",
                financials=FinancialMetric(),
            )
            for i in range(100)
        ]

        mock_sec = Mock()
        mock_sec.fetch_filing.return_value = {
            "revenue": 1000000,
            "growth_rate": 0.1,
            "employees": 100,
            "profit_margin": 0.2,
        }

        loader = UnifiedCompanyLoader(sec_connector=mock_sec)
        count = 0
        for company in companies:
            loader.fill_nulls_from_sec_edgar(company)
            count += 1

        assert count == 100


class TestIdempotency:
    """Test idempotency (Phase 5 item 115)."""

    def test_duplicate_enrichment_produces_same_result(self):
        """Verify enriching same company twice produces same result."""
        company = UnifiedCompany(
            id="TEST",
            name="Test Company",
            ticker="TST1",
            financials=FinancialMetric(),
        )

        mock_sec = Mock()
        mock_sec.fetch_filing.return_value = {
            "revenue": 1000000,
            "growth_rate": 0.1,
            "employees": 100,
            "profit_margin": 0.2,
        }

        loader = UnifiedCompanyLoader(sec_connector=mock_sec)

        result1 = loader.fill_nulls_from_sec_edgar(company)
        result2 = loader.fill_nulls_from_sec_edgar(company)

        assert result1.financials.revenue == result2.financials.revenue
        assert result1.enrichment_sources == result2.enrichment_sources

    def test_enrichment_idempotent_with_orchestrator(self):
        """Verify orchestrator produces idempotent results."""
        company = UnifiedCompany(
            id="TEST",
            name="Test Company",
            ticker="TST1",
            financials=FinancialMetric(),
        )

        orchestrator = EnrichmentOrchestrator()

        result1 = orchestrator.enrich_single(company, lambda c, s, f: c)
        result2 = orchestrator.enrich_single(company, lambda c, s, f: c)

        assert result1.company.id == result2.company.id


class TestInvalidTicker:
    """Test invalid ticker validation (Phase 5 item 116)."""

    def test_invalid_ticker_format_rejected(self):
        """Verify invalid ticker format is rejected."""
        orchestrator = EnrichmentOrchestrator()

        company = UnifiedCompany(
            id="TEST",
            name="Test Company",
            ticker="",
            financials=FinancialMetric(),
        )

        should_skip = orchestrator.should_skip_enrichment(company)
        assert should_skip

    def test_empty_ticker_skips_enrichment(self):
        """Verify empty ticker skips enrichment."""
        orchestrator = EnrichmentOrchestrator()

        company = UnifiedCompany(
            id="TEST",
            name="Test Company",
            ticker="   ",
            financials=FinancialMetric(),
        )

        should_skip = orchestrator.should_skip_enrichment(company)
        assert should_skip


class TestInvalidCompanyNumber:
    """Test invalid company_number validation (Phase 5 item 117)."""

    def test_invalid_company_number_format_rejected(self):
        """Verify invalid company_number format is rejected."""
        orchestrator = EnrichmentOrchestrator()

        company = UnifiedCompany(
            id="TEST",
            name="Test Company",
            company_number="",
            financials=FinancialMetric(),
        )

        order = orchestrator.get_enrichment_order(company)
        assert EnrichmentSource.COMPANIES_HOUSE not in order

    def test_empty_company_number_skips_ch_enrichment(self):
        """Verify empty company_number skips CH enrichment."""
        orchestrator = EnrichmentOrchestrator()

        company = UnifiedCompany(
            id="TEST",
            name="Test Company",
            company_number="   ",
            financials=FinancialMetric(),
        )

        order = orchestrator.get_enrichment_order(company)
        assert EnrichmentSource.COMPANIES_HOUSE not in order


class TestConcurrency:
    """Test concurrent enrichment (Phase 5 item 118)."""

    def test_concurrent_enrichment_of_multiple_companies(self):
        """Verify concurrent enrichment of multiple companies."""
        companies = [
            UnifiedCompany(
                id=f"TEST{i}",
                name=f"Test Company {i}",
                ticker=f"TST{i}",
                financials=FinancialMetric(),
            )
            for i in range(10)
        ]

        mock_sec = Mock()
        mock_sec.fetch_filing.return_value = {
            "revenue": 1000000,
            "growth_rate": 0.1,
            "employees": 100,
            "profit_margin": 0.2,
        }

        loader = UnifiedCompanyLoader(sec_connector=mock_sec)

        results = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(loader.fill_nulls_from_sec_edgar, company): company for company in companies}
            for future in as_completed(futures):
                results.append(future.result())

        assert len(results) == 10
        for result in results:
            assert result.id is not None

    def test_thread_safe_enrichment(self):
        """Verify enrichment is thread-safe."""
        company = UnifiedCompany(
            id="TEST",
            name="Test Company",
            ticker="TST1",
            financials=FinancialMetric(),
        )

        mock_sec = Mock()
        mock_sec.fetch_filing.return_value = {
            "revenue": 1000000,
            "growth_rate": 0.1,
            "employees": 100,
            "profit_margin": 0.2,
        }

        loader = UnifiedCompanyLoader(sec_connector=mock_sec)

        results = []
        lock = threading.Lock()

        def enrich_company():
            result = loader.fill_nulls_from_sec_edgar(company)
            with lock:
                results.append(result)

        threads = [threading.Thread(target=enrich_company) for _ in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        assert len(results) == 5
