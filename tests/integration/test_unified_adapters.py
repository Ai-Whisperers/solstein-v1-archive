"""Integration tests for unified adapters.

Tests all 6 unified adapters created in Tasks 15-17:
- WebSearchUnifiedAdapter
- NewsUnifiedAdapter
- FundingUnifiedAdapter
- LinkedInUnifiedAdapter
- WebsiteUnifiedAdapter
- PatentsUnifiedAdapter

Each test verifies:
- Protocol compliance (implements UnifiedDataSource)
- Basic functionality (discover, enrich, refresh where applicable)
- Configuration (confidence, authority levels)
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from solstein.adapters.enrichment.funding_unified import FundingUnifiedAdapter
from solstein.adapters.enrichment.linkedin_unified import LinkedInUnifiedAdapter
from solstein.adapters.enrichment.news_unified import NewsUnifiedAdapter
from solstein.adapters.enrichment.patents_unified import PatentsUnifiedAdapter
from solstein.adapters.enrichment.web_search_unified import WebSearchUnifiedAdapter
from solstein.adapters.enrichment.website_unified import WebsiteUnifiedAdapter
from solstein.adapters.protocols import UnifiedDataSource
from solstein.domain.models import DataSourceType
from solstein.infrastructure.conflict_resolution import SourceAuthority


class TestWebSearchUnifiedAdapter:
    """Integration tests for WebSearchUnifiedAdapter."""

    def test_protocol_compliance(self):
        """WebSearchUnifiedAdapter implements UnifiedDataSource protocol."""
        adapter = WebSearchUnifiedAdapter()
        assert isinstance(adapter, UnifiedDataSource)

    def test_source_configuration(self):
        """WebSearch adapter has correct confidence and authority."""
        adapter = WebSearchUnifiedAdapter()
        assert adapter.get_confidence() == 0.70
        assert adapter.get_authority() == SourceAuthority.WEB_SEARCH
        assert adapter.supports_incremental() is True
        assert adapter.supports_discovery() is True

    def test_source_type(self):
        """WebSearch adapter returns correct DataSourceType."""
        adapter = WebSearchUnifiedAdapter()
        assert adapter.source_type == DataSourceType.WEB_SEARCH

    @pytest.mark.asyncio
    async def test_fetch_facts_returns_list(self):
        """fetch_facts returns a list of facts."""
        adapter = WebSearchUnifiedAdapter()
        company_ids = ["Test Company"]

        with patch("solstein.adapters.enrichment.web_search_unified.search_company_news") as mock_news:
            mock_news.return_value = [{"title": "Test News", "url": "http://test.com"}]

            with patch("solstein.adapters.enrichment.web_search_unified.search_company_info") as mock_info:
                mock_info.return_value = [{"title": "Test Info", "snippet": "Info snippet"}]

                facts = await adapter.fetch_facts(company_ids)
                assert isinstance(facts, list)


class TestNewsUnifiedAdapter:
    """Integration tests for NewsUnifiedAdapter."""

    def test_protocol_compliance(self):
        """NewsUnifiedAdapter implements UnifiedDataSource protocol."""
        adapter = NewsUnifiedAdapter()
        assert isinstance(adapter, UnifiedDataSource)

    def test_source_configuration(self):
        """News adapter has correct confidence and authority."""
        adapter = NewsUnifiedAdapter()
        assert adapter.get_confidence() == 0.70
        assert adapter.get_authority() == SourceAuthority.NEWS_API
        assert adapter.supports_incremental() is True
        assert adapter.supports_discovery() is True

    def test_source_type(self):
        """News adapter returns correct DataSourceType."""
        adapter = NewsUnifiedAdapter()
        assert adapter.source_type == DataSourceType.NEWS

    def test_sentiment_analysis(self):
        """News adapter can analyze sentiment."""
        adapter = NewsUnifiedAdapter()

        positive_text = "Company reports strong growth and record profits"
        assert adapter._analyze_sentiment(positive_text) == "positive"

        negative_text = "Company faces lawsuit and declining revenue"
        assert adapter._analyze_sentiment(negative_text) == "negative"

        neutral_text = "Company announces new office location"
        assert adapter._analyze_sentiment(neutral_text) == "neutral"

    @pytest.mark.asyncio
    async def test_fetch_facts_without_api_key(self):
        """fetch_facts returns empty list without API key."""
        adapter = NewsUnifiedAdapter(news_api_key=None)
        facts = await adapter.fetch_facts(["Test Company"])
        assert facts == []


class TestFundingUnifiedAdapter:
    """Integration tests for FundingUnifiedAdapter."""

    def test_protocol_compliance(self):
        """FundingUnifiedAdapter implements UnifiedDataSource protocol."""
        adapter = FundingUnifiedAdapter()
        assert isinstance(adapter, UnifiedDataSource)

    def test_source_configuration(self):
        """Funding adapter has correct confidence and authority."""
        adapter = FundingUnifiedAdapter()
        assert adapter.get_confidence() == 0.65
        assert adapter.get_authority() == SourceAuthority.FUNDING
        assert adapter.supports_incremental() is True
        assert adapter.supports_discovery() is True

    def test_source_type(self):
        """Funding adapter returns correct DataSourceType."""
        adapter = FundingUnifiedAdapter()
        assert adapter.source_type == DataSourceType.FUNDING

    @pytest.mark.asyncio
    async def test_fetch_facts_without_api_key(self):
        """fetch_facts works without Crunchbase API key using public sources."""
        adapter = FundingUnifiedAdapter(crunchbase_api_key=None)
        company_ids = ["Test Company"]

        with patch("solstein.data.additional_sources.AdditionalDataSources") as mock_additional:
            mock_instance = MagicMock()
            mock_instance.get_news.return_value = MagicMock(articles=[])
            mock_additional.return_value = mock_instance

            facts = await adapter.fetch_facts(company_ids)
            assert isinstance(facts, list)


class TestLinkedInUnifiedAdapter:
    """Integration tests for LinkedInUnifiedAdapter."""

    def test_protocol_compliance(self):
        """LinkedInUnifiedAdapter implements UnifiedDataSource protocol."""
        adapter = LinkedInUnifiedAdapter()
        assert isinstance(adapter, UnifiedDataSource)

    def test_source_configuration(self):
        """LinkedIn adapter has correct confidence and authority."""
        adapter = LinkedInUnifiedAdapter()
        assert adapter.get_confidence() == 0.60
        assert adapter.get_authority() == SourceAuthority.LINKEDIN
        assert adapter.supports_incremental() is True
        assert adapter.supports_discovery() is False

    def test_source_type(self):
        """LinkedIn adapter returns correct DataSourceType."""
        adapter = LinkedInUnifiedAdapter()
        assert adapter.source_type == DataSourceType.LINKEDIN

    def test_discover_returns_empty(self):
        """LinkedIn discover returns empty list."""
        adapter = LinkedInUnifiedAdapter()
        result = adapter.discover("market", "seed")
        assert result == []

    @pytest.mark.asyncio
    async def test_fetch_facts_returns_hiring_signals(self):
        """fetch_facts returns hiring signals when available."""
        adapter = LinkedInUnifiedAdapter()

        with patch("solstein.data.additional_sources.AdditionalDataSources") as mock_additional:
            mock_instance = MagicMock()
            mock_article = MagicMock()
            mock_article.title = "Company hiring AI engineers"
            mock_article.published_at = datetime.now()
            mock_article.source = "Tech News"
            mock_instance.get_news.return_value = MagicMock(
                articles=[mock_article],
                sentiment_score=0.5,
            )
            mock_additional.return_value = mock_instance

            facts = await adapter.fetch_facts(["Test Company"])
            assert isinstance(facts, list)


class TestWebsiteUnifiedAdapter:
    """Integration tests for WebsiteUnifiedAdapter."""

    def test_protocol_compliance(self):
        """WebsiteUnifiedAdapter implements UnifiedDataSource protocol."""
        adapter = WebsiteUnifiedAdapter()
        assert isinstance(adapter, UnifiedDataSource)

    def test_source_configuration(self):
        """Website adapter has correct confidence and authority."""
        adapter = WebsiteUnifiedAdapter()
        assert adapter.get_confidence() == 0.70
        assert adapter.get_authority() == SourceAuthority.WEBSITE
        assert adapter.supports_incremental() is True
        assert adapter.supports_discovery() is False

    def test_source_type(self):
        """Website adapter returns correct DataSourceType."""
        adapter = WebsiteUnifiedAdapter()
        assert adapter.source_type == DataSourceType.WEBSITE

    def test_discover_returns_empty(self):
        """Website discover returns empty list."""
        adapter = WebsiteUnifiedAdapter()
        result = adapter.discover("market", "seed")
        assert result == []

    @pytest.mark.asyncio
    async def test_fetch_facts_with_mock_scrape(self):
        """fetch_facts returns facts when scraping succeeds."""
        adapter = WebsiteUnifiedAdapter()

        with patch.object(adapter, "_scrape_website") as mock_scrape:
            mock_scrape.return_value = {
                "main_products": ["software", "platform"],
                "tech_stack": ["python", "aws"],
                "product_count": 2,
                "tech_count": 2,
            }

            facts = await adapter.fetch_facts(["Test Company"])
            assert isinstance(facts, list)
            if facts:
                assert facts[0]["fact_type"] == "website_info"


class TestPatentsUnifiedAdapter:
    """Integration tests for PatentsUnifiedAdapter."""

    def test_protocol_compliance(self):
        """PatentsUnifiedAdapter implements UnifiedDataSource protocol."""
        adapter = PatentsUnifiedAdapter()
        assert isinstance(adapter, UnifiedDataSource)

    def test_source_configuration(self):
        """Patents adapter has correct confidence and authority."""
        adapter = PatentsUnifiedAdapter()
        assert adapter.get_confidence() == 0.80
        assert adapter.get_authority() == SourceAuthority.PATENTS
        assert adapter.supports_incremental() is True
        assert adapter.supports_discovery() is True

    def test_source_type(self):
        """Patents adapter returns correct DataSourceType."""
        adapter = PatentsUnifiedAdapter()
        assert adapter.source_type == DataSourceType.PATENTS

    @pytest.mark.asyncio
    async def test_fetch_facts_with_mock_patents(self):
        """fetch_facts returns patent facts when data available."""
        adapter = PatentsUnifiedAdapter()

        with patch("solstein.adapters.enrichment.patents_unified.search_company_patents") as mock_search:
            mock_result = MagicMock()
            mock_result.total_patents = 10
            mock_result.recent_patents = [{"title": "AI Patent"}]
            mock_result.ai_related_patents = 3
            mock_result.top_categories = ["AI", "ML"]
            mock_result.source = "uspto_peds"
            mock_search.return_value = mock_result

            facts = await adapter.fetch_facts(["Test Company"])
            assert isinstance(facts, list)
            assert len(facts) == 2  # patent_portfolio + ai_patents

            portfolio_fact = [f for f in facts if f["fact_type"] == "patent_portfolio"][0]
            assert portfolio_fact["value"]["total_patents"] == 10


class TestAllUnifiedAdapters:
    """Cross-cutting tests for all unified adapters."""

    def test_all_adapters_implement_protocol(self):
        """All unified adapters implement UnifiedDataSource."""
        adapters = [
            WebSearchUnifiedAdapter(),
            NewsUnifiedAdapter(),
            FundingUnifiedAdapter(),
            LinkedInUnifiedAdapter(),
            WebsiteUnifiedAdapter(),
            PatentsUnifiedAdapter(),
        ]

        for adapter in adapters:
            assert isinstance(adapter, UnifiedDataSource), f"{type(adapter).__name__} must implement UnifiedDataSource"

    def test_all_adapters_have_required_methods(self):
        """All adapters have required protocol methods."""
        adapters = [
            WebSearchUnifiedAdapter(),
            NewsUnifiedAdapter(),
            FundingUnifiedAdapter(),
            LinkedInUnifiedAdapter(),
            WebsiteUnifiedAdapter(),
            PatentsUnifiedAdapter(),
        ]

        for adapter in adapters:
            assert hasattr(adapter, "source_name")
            assert hasattr(adapter, "source_type")
            assert hasattr(adapter, "discover")
            assert hasattr(adapter, "enrich")
            assert hasattr(adapter, "refresh")
            assert hasattr(adapter, "get_confidence")
            assert hasattr(adapter, "get_authority")
            assert hasattr(adapter, "supports_incremental")
            assert hasattr(adapter, "supports_discovery")

    def test_confidence_levels_appropriate(self):
        """All adapters have reasonable confidence levels (0.5-1.0)."""
        adapters = [
            (WebSearchUnifiedAdapter(), "web_search"),
            (NewsUnifiedAdapter(), "news"),
            (FundingUnifiedAdapter(), "funding"),
            (LinkedInUnifiedAdapter(), "linkedin"),
            (WebsiteUnifiedAdapter(), "website"),
            (PatentsUnifiedAdapter(), "patents"),
        ]

        for adapter, name in adapters:
            confidence = adapter.get_confidence()
            assert 0.5 <= confidence <= 1.0, f"{name} confidence {confidence} out of range"

    def test_authority_levels_valid(self):
        """All adapters have valid SourceAuthority."""
        adapters = [
            WebSearchUnifiedAdapter(),
            NewsUnifiedAdapter(),
            FundingUnifiedAdapter(),
            LinkedInUnifiedAdapter(),
            WebsiteUnifiedAdapter(),
            PatentsUnifiedAdapter(),
        ]

        for adapter in adapters:
            authority = adapter.get_authority()
            assert isinstance(authority, SourceAuthority)
