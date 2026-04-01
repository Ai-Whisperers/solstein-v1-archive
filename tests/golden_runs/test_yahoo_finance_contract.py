"""Golden contract run tests for Yahoo Finance provider adapter.

STORY-267 / EPIC-070: Yahoo Finance covers structured API surface
(yfinance SDK), single-source with no fallback, hard-fail semantics.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from solstein.adapters.enrichment.yahoo_finance import YahooFinanceEnrichment
from solstein.domain.models import DataSourceType, RawDataSource

from .artifact_differ import ArtifactDiffer
from .conftest import ARTIFACTS_DIR, load_artifact


def _raw_data_source_to_dict(rds: RawDataSource) -> dict[str, Any]:
    """Convert a RawDataSource to a flat dict for contract comparison."""
    data = rds.model_dump(mode="json")
    if hasattr(rds.source_type, "name"):
        data["source_type"] = rds.source_type.name
    elif hasattr(rds.source_type, "value"):
        data["source_type"] = rds.source_type.value
    return data


def _make_mock_company_research(
    ticker: str = "AAPL",
    name: str = "Apple Inc.",
    exchange: str = "NMS",
) -> MagicMock:
    """Create a mock CompanyResearch-like object."""
    mock = MagicMock()
    mock.exchange = exchange
    mock.model_dump.return_value = {
        "ticker": ticker,
        "name": name,
        "exchange": exchange,
        "description": "Technology company",
        "market_cap": 3_000_000_000_000,
    }
    return mock


def _enrich_with_mock(adapter: YahooFinanceEnrichment, **kwargs: Any) -> RawDataSource:
    """Run adapter.enrich with a mocked CompanyResearcher."""
    mock_profile = _make_mock_company_research()
    with patch(
        "solstein.data.company_research.CompanyResearcher"
    ) as mock_cls:
        mock_cls.return_value.research.return_value = mock_profile
        return adapter.enrich(**kwargs)


# ---------------------------------------------------------------------------
# Yahoo Finance: Success Contract
# ---------------------------------------------------------------------------

class TestYahooFinanceSuccessContract:
    """Verify Yahoo Finance adapter output matches golden success contract."""

    @pytest.fixture()
    def contract(self) -> dict[str, Any]:
        return load_artifact("yahoo_finance_success")

    @pytest.fixture()
    def adapter(self) -> YahooFinanceEnrichment:
        return YahooFinanceEnrichment()

    def test_success_output_shape(
        self, adapter: YahooFinanceEnrichment, contract: dict[str, Any]
    ) -> None:
        """Success path produces RawDataSource matching the golden contract."""
        result = _enrich_with_mock(
            adapter, company_id="test-001", company_name="Apple Inc.", ticker="AAPL",
        )
        assert isinstance(result, RawDataSource)
        actual = _raw_data_source_to_dict(result)

        differ = ArtifactDiffer(ARTIFACTS_DIR)
        report = differ.compare_success("yahoo_finance", actual, contract)
        differ.store_actual("yahoo_finance", "success", actual)

        assert report.passed, report.summary()
        assert report.checked_fields >= 5

    def test_source_type_is_yahoo_finance(self, adapter: YahooFinanceEnrichment) -> None:
        """Source type must be YAHOO_FINANCE."""
        result = _enrich_with_mock(
            adapter, company_id="t2", company_name="Apple Inc.", ticker="AAPL",
        )
        assert result.source_type == DataSourceType.YAHOO_FINANCE

    def test_confidence_is_0_8(self, adapter: YahooFinanceEnrichment) -> None:
        """Confidence must be 0.8 per contract."""
        result = _enrich_with_mock(
            adapter, company_id="t3", company_name="Apple Inc.", ticker="AAPL",
        )
        assert result.confidence == 0.8

    def test_url_contains_ticker(self, adapter: YahooFinanceEnrichment) -> None:
        """URL must include the ticker symbol."""
        result = _enrich_with_mock(
            adapter, company_id="t4", company_name="Apple Inc.", ticker="AAPL",
        )
        assert result.url is not None
        assert "AAPL" in result.url
        assert re.match(r"https://finance\.yahoo\.com/quote/.+/", result.url)

    def test_metadata_has_ticker(self, adapter: YahooFinanceEnrichment) -> None:
        """Metadata must include the ticker key."""
        result = _enrich_with_mock(
            adapter, company_id="t5", company_name="Apple Inc.", ticker="AAPL",
        )
        assert "ticker" in result.metadata
        assert result.metadata["ticker"] == "AAPL"

    def test_extraction_method_is_yfinance_api(self, adapter: YahooFinanceEnrichment) -> None:
        """Extraction method must be 'yfinance_api'."""
        result = _enrich_with_mock(
            adapter, company_id="t6", company_name="Apple Inc.", ticker="AAPL",
        )
        assert result.extraction_method == "yfinance_api"

    def test_raw_content_is_dict(self, adapter: YahooFinanceEnrichment) -> None:
        """raw_content must be a dict (from CompanyResearch.model_dump)."""
        result = _enrich_with_mock(
            adapter, company_id="t7", company_name="Apple Inc.", ticker="AAPL",
        )
        assert isinstance(result.raw_content, dict)

    def test_retrieval_timestamp_is_utc(self, adapter: YahooFinanceEnrichment) -> None:
        """Retrieval timestamp must be UTC and recent."""
        before = datetime.now(timezone.utc)
        result = _enrich_with_mock(
            adapter, company_id="t8", company_name="Apple Inc.", ticker="AAPL",
        )
        after = datetime.now(timezone.utc)
        assert result.retrieval_timestamp.tzinfo is not None
        assert before <= result.retrieval_timestamp <= after


# ---------------------------------------------------------------------------
# Yahoo Finance: Degraded / Failure Contract
# ---------------------------------------------------------------------------

class TestYahooFinanceDegradedContract:
    """Verify Yahoo Finance adapter failure semantics."""

    @pytest.fixture()
    def adapter(self) -> YahooFinanceEnrichment:
        return YahooFinanceEnrichment()

    def test_missing_ticker_raises_value_error(self, adapter: YahooFinanceEnrichment) -> None:
        """Missing ticker must raise ValueError."""
        with pytest.raises(ValueError, match="requires a ticker"):
            adapter.enrich(company_id="d01", company_name="Unknown Corp", ticker=None)

    def test_empty_ticker_raises_value_error(self, adapter: YahooFinanceEnrichment) -> None:
        """Empty string ticker must raise ValueError."""
        with pytest.raises(ValueError, match="requires a ticker"):
            adapter.enrich(company_id="d02", company_name="Unknown Corp", ticker="")

    def test_sdk_error_propagates(self, adapter: YahooFinanceEnrichment) -> None:
        """yfinance SDK errors must propagate, not be silently swallowed."""
        with patch(
            "solstein.data.company_research.CompanyResearcher"
        ) as mock_cls:
            mock_cls.return_value.research.side_effect = RuntimeError("API rate limited")
            with pytest.raises(RuntimeError, match="API rate limited"):
                adapter.enrich(company_id="d03", company_name="Failing Corp", ticker="FAIL")

    def test_no_silent_none_return(self, adapter: YahooFinanceEnrichment) -> None:
        """Adapter must never return None on failure; it must raise."""
        with patch(
            "solstein.data.company_research.CompanyResearcher"
        ) as mock_cls:
            mock_cls.return_value.research.side_effect = Exception("Network error")
            with pytest.raises(Exception):
                adapter.enrich(company_id="d04", company_name="Net Error Corp", ticker="NETERR")
