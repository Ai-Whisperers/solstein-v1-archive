"""Cross-provider contract invariant tests.

STORY-267 / EPIC-070: Verify that all canonical providers satisfy
shared RawDataSource shape invariants and cover different surfaces.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from solstein.adapters.enrichment.patents import PatentEnrichment
from solstein.adapters.enrichment.yahoo_finance import YahooFinanceEnrichment
from solstein.data.patent_client import PatentResult
from solstein.domain.models import DataSourceType, RawDataSource


def _get_yahoo_result() -> RawDataSource:
    """Get a Yahoo Finance result using mocked SDK."""
    mock = MagicMock()
    mock.exchange = "NMS"
    mock.model_dump.return_value = {"ticker": "AAPL", "name": "Apple", "exchange": "NMS"}

    adapter = YahooFinanceEnrichment()
    with patch("solstein.data.company_research.CompanyResearcher") as cls:
        cls.return_value.research.return_value = mock
        return adapter.enrich(company_id="x1", company_name="Apple", ticker="AAPL")


def _get_patent_result() -> RawDataSource:
    """Get a Patents result using mocked search."""
    adapter = PatentEnrichment()
    result = PatentResult(total_patents=10, source="uspto_peds", top_categories=["AI"])
    with patch(
        "solstein.data.patent_client.search_company_patents",
        return_value=result,
    ):
        return adapter.enrich(company_id="x2", company_name="Google")


class TestCrossProviderInvariants:
    """All canonical providers must satisfy these shared invariants."""

    def test_all_return_raw_data_source(self) -> None:
        """All providers must return RawDataSource instances."""
        assert isinstance(_get_yahoo_result(), RawDataSource)
        assert isinstance(_get_patent_result(), RawDataSource)

    def test_all_have_source_type(self) -> None:
        """All providers must set a DataSourceType."""
        assert isinstance(_get_yahoo_result().source_type, DataSourceType)
        assert isinstance(_get_patent_result().source_type, DataSourceType)

    def test_all_have_confidence_in_range(self) -> None:
        """All providers must have confidence in [0, 1]."""
        for result in [_get_yahoo_result(), _get_patent_result()]:
            assert 0.0 <= result.confidence <= 1.0

    def test_all_have_relevance_in_range(self) -> None:
        """All providers must have relevance_score in [0, 1]."""
        for result in [_get_yahoo_result(), _get_patent_result()]:
            assert 0.0 <= result.relevance_score <= 1.0

    def test_all_have_utc_timestamp(self) -> None:
        """All providers must produce UTC retrieval timestamps."""
        for result in [_get_yahoo_result(), _get_patent_result()]:
            assert result.retrieval_timestamp.tzinfo is not None

    def test_all_have_extraction_method(self) -> None:
        """All providers must declare an extraction_method."""
        for result in [_get_yahoo_result(), _get_patent_result()]:
            assert result.extraction_method is not None
            assert len(result.extraction_method) > 0

    def test_providers_cover_different_surfaces(self) -> None:
        """The two providers must cover materially different source types."""
        yahoo = _get_yahoo_result()
        patent = _get_patent_result()
        assert yahoo.source_type != patent.source_type
