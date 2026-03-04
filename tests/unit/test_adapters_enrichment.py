"""Tests for enrichment adapters (funding, news, web_search_news)."""

from unittest.mock import MagicMock, patch

from solstein.adapters.enrichment.funding import FundingEnrichment
from solstein.adapters.enrichment.news import NewsEnrichment
from solstein.adapters.enrichment.web_search_news import WebSearchNewsEnrichment
from solstein.domain.models import DataSourceType


class TestFundingEnrichment:
    """Test suite for FundingEnrichment adapter."""

    def test_source_name(self):
        """Test that source_name property returns 'funding'."""
        enrichment = FundingEnrichment()
        assert enrichment.source_name == "funding"

    def test_source_type(self):
        """Test that source_type property returns CRUNCHBASE."""
        enrichment = FundingEnrichment()
        assert enrichment.source_type == DataSourceType.CRUNCHBASE

    def test_init_with_keys(self):
        """Test initialization with API keys."""
        enrichment = FundingEnrichment(crunchbase_api_key="cb_key", news_api_key="news_key")
        assert enrichment._crunchbase_key == "cb_key"
        assert enrichment._news_api_key == "news_key"

    def test_init_without_keys(self):
        """Test initialization without API keys."""
        enrichment = FundingEnrichment()
        assert enrichment._crunchbase_key is None
        assert enrichment._news_api_key is None

    def test_enrich_with_crunchbase_key(self):
        """Test enrichment with Crunchbase API key."""
        with patch("solstein.data.additional_sources.AdditionalDataSources") as mock_sources:
            # Mock the funding data
            mock_funding = MagicMock()
            mock_funding.model_dump.return_value = {"total_raised": 10000000, "num_rounds": 2}
            mock_funding.total_raised = 10000000
            mock_funding.num_rounds = 2

            mock_client = MagicMock()
            mock_client.get_funding_data.return_value = mock_funding
            mock_sources.return_value = mock_client

            enrichment = FundingEnrichment(crunchbase_api_key="test_key")
            result = enrichment.enrich("acme_001", "ACME Corp")

            assert result.source_type == DataSourceType.CRUNCHBASE
            assert result.source_name == "Crunchbase"
            assert result.confidence == 0.7

    def test_enrich_without_crunchbase_key(self):
        """Test enrichment with fallback to news-based detection."""
        with patch("solstein.data.additional_sources.AdditionalDataSources") as mock_sources:
            mock_funding = MagicMock()
            mock_funding.model_dump.return_value = {}
            mock_funding.total_raised = None
            mock_funding.num_rounds = 0

            mock_client = MagicMock()
            mock_client.get_funding_data.return_value = mock_funding
            mock_sources.return_value = mock_client

            enrichment = FundingEnrichment()
            result = enrichment.enrich("acme_001", "ACME Corp")

            assert result.source_name == "News-based funding detection"
            assert result.confidence == 0.3


class TestNewsEnrichment:
    """Test suite for NewsEnrichment adapter."""

    def test_source_name(self):
        """Test that source_name property returns 'news'."""
        enrichment = NewsEnrichment()
        assert enrichment.source_name == "news"

    def test_source_type(self):
        """Test that source_type property returns NEWS."""
        enrichment = NewsEnrichment()
        assert enrichment.source_type == DataSourceType.NEWS

    def test_init(self):
        """Test initialization."""
        enrichment = NewsEnrichment(news_api_key="test_key")
        assert enrichment._news_api_key == "test_key"


class TestWebSearchNewsEnrichment:
    """Test suite for WebSearchNewsEnrichment adapter."""

    def test_source_name(self):
        """Test that source_name property returns 'web_search_news'."""
        enrichment = WebSearchNewsEnrichment()
        assert enrichment.source_name == "web_search_news"

    def test_source_type(self):
        """Test that source_type property returns EXA_SEARCH."""
        enrichment = WebSearchNewsEnrichment()
        assert enrichment.source_type == DataSourceType.EXA_SEARCH
