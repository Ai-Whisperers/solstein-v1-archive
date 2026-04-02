"""Tests for STORY-102: GDELT + RSS news intelligence.

Covers:
- GDELT connector search and normalization
- GDELTArticle schema
- URL-based deduplication
- NewsBackendDispatcher fallback logic (GDELT -> RSS -> NewsAPI)
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from solstein.agents.news_backends import NewsBackendDispatcher
from solstein.connectors.base import ConnectorResult, RawData
from solstein.connectors.news.gdelt import (
    GDELTArticle,
    GDELTConnector,
    deduplicate_by_url,
)

# -----------------------------------------------------------------------
# GDELTArticle schema tests
# -----------------------------------------------------------------------


class TestGDELTArticle:
    """Verify GDELT article schema."""

    def test_article_has_required_fields(self):
        """GDELTArticle has all required fields."""
        article = GDELTArticle(
            url="https://example.com/article",
            title="Test Article",
            source_name="example.com",
            language="English",
            published_date="20260315",
            tone=-1.5,
            domain="example.com",
            seendate="20260315T120000Z",
        )
        d = article.to_dict()
        assert d["url"] == "https://example.com/article"
        assert d["title"] == "Test Article"
        assert d["tone"] == -1.5
        assert d["language"] == "English"

    def test_article_defaults(self):
        """GDELTArticle uses safe defaults."""
        article = GDELTArticle(
            url="https://a.com",
            title="A",
            source_name="a",
            language="en",
            published_date="20260101",
        )
        assert article.tone == 0.0
        assert article.domain == ""
        assert article.seendate == ""


# -----------------------------------------------------------------------
# Deduplication tests
# -----------------------------------------------------------------------


class TestDeduplication:
    """Verify URL-based deduplication."""

    def _make_raw(self, url: str) -> RawData:
        return RawData(
            source_name="test",
            source_url=url,
            raw_content={"title": f"Article at {url}"},
            extracted_at=datetime.now(timezone.utc),
            metadata={},
        )

    def test_dedup_removes_exact_duplicates(self):
        """Identical URLs are deduplicated."""
        articles = [
            self._make_raw("https://example.com/article1"),
            self._make_raw("https://example.com/article1"),
            self._make_raw("https://example.com/article2"),
        ]
        result = deduplicate_by_url(articles)
        assert len(result) == 2

    def test_dedup_case_insensitive(self):
        """URL dedup is case-insensitive."""
        articles = [
            self._make_raw("https://Example.com/Article"),
            self._make_raw("https://example.com/article"),
        ]
        result = deduplicate_by_url(articles)
        assert len(result) == 1

    def test_dedup_empty_list(self):
        """Empty list returns empty."""
        assert deduplicate_by_url([]) == []

    def test_dedup_preserves_order(self):
        """First occurrence is kept."""
        articles = [
            self._make_raw("https://a.com"),
            self._make_raw("https://b.com"),
            self._make_raw("https://a.com"),
        ]
        result = deduplicate_by_url(articles)
        assert len(result) == 2
        assert result[0].source_url == "https://a.com"
        assert result[1].source_url == "https://b.com"


# -----------------------------------------------------------------------
# GDELT connector tests
# -----------------------------------------------------------------------


class TestGDELTConnector:
    """Test GDELT connector normalization."""

    def test_normalize_gdelt_result(self):
        """GDELT RawData normalizes to expected schema."""
        connector = GDELTConnector()
        raw = RawData(
            source_name="gdelt",
            source_url="https://news.example.com/story",
            raw_content={
                "url": "https://news.example.com/story",
                "title": "Breaking News",
                "domain": "news.example.com",
                "language": "English",
                "seendate": "20260315T120000Z",
                "tone": -2.3,
                "sourcecountry": "United States",
            },
            extracted_at=datetime.now(timezone.utc),
            metadata={},
        )
        normalized = connector.normalize(raw)
        assert normalized["source"] == "gdelt"
        assert normalized["entity_type"] == "news_article"
        assert normalized["title"] == "Breaking News"
        assert normalized["tone"] == -2.3
        assert normalized["url"] == "https://news.example.com/story"

    def test_normalize_to_article(self):
        """Static method converts RawData to GDELTArticle."""
        raw = RawData(
            source_name="gdelt",
            source_url="https://test.com",
            raw_content={
                "url": "https://test.com",
                "title": "Test",
                "domain": "test.com",
                "language": "English",
                "seendate": "20260101T000000Z",
                "tone": 1.5,
            },
            extracted_at=datetime.now(timezone.utc),
            metadata={},
        )
        article = GDELTConnector.normalize_to_article(raw)
        assert article.title == "Test"
        assert article.tone == 1.5
        assert article.domain == "test.com"

    @pytest.mark.asyncio
    async def test_get_by_id_not_supported(self):
        """get_by_id returns error for GDELT."""
        connector = GDELTConnector()
        result = await connector.get_by_id("some-id")
        assert result.success is False
        assert "not support" in result.error_message.lower()


# -----------------------------------------------------------------------
# NewsBackendDispatcher fallback tests
# -----------------------------------------------------------------------


class TestNewsBackendDispatcher:
    """Test GDELT primary / RSS supplement / NewsAPI fallback logic."""

    def _make_dispatcher(self, news_api_key=None):
        """Create a dispatcher with mocked settings."""
        with patch("solstein.agents.news_backends.get_settings") as mock_settings:
            settings = MagicMock()
            settings.http_timeouts.news_api = 15.0
            settings.circuit_breaker.failure_threshold = 5
            settings.circuit_breaker.recovery_timeout = 60.0
            mock_settings.return_value = settings

            return NewsBackendDispatcher(
                news_api_key=news_api_key,
                rss_feeds=[],  # No RSS feeds in tests
            )

    def _make_raw_data(self, url: str, source: str = "gdelt") -> RawData:
        return RawData(
            source_name=source,
            source_url=url,
            raw_content={"title": f"Article from {source}", "url": url},
            extracted_at=datetime.now(timezone.utc),
            metadata={"source_type": "news"},
        )

    @pytest.mark.asyncio
    async def test_gdelt_primary_success(self):
        """When GDELT succeeds, NewsAPI is never called."""
        dispatcher = self._make_dispatcher()
        mock_result = ConnectorResult(
            success=True,
            data=[self._make_raw_data("https://a.com")],
            total_found=1,
        )
        with patch.object(dispatcher, "_search_gdelt", new_callable=AsyncMock, return_value=mock_result.data):
            with patch.object(dispatcher, "_search_newsapi", new_callable=AsyncMock) as mock_newsapi:
                results = await dispatcher.search("test company")
                assert len(results) == 1
                mock_newsapi.assert_not_called()

    @pytest.mark.asyncio
    async def test_gdelt_failure_triggers_newsapi_fallback(self):
        """When GDELT fails and API key exists, falls back to NewsAPI."""
        dispatcher = self._make_dispatcher(news_api_key="test-key")
        newsapi_data = [self._make_raw_data("https://newsapi.com/article", "newsapi")]

        with patch.object(dispatcher, "_search_gdelt", new_callable=AsyncMock, return_value=None):
            with patch.object(dispatcher, "_search_newsapi", new_callable=AsyncMock, return_value=newsapi_data):
                results = await dispatcher.search("test company")
                assert len(results) == 1
                assert results[0].source_name == "newsapi"

    @pytest.mark.asyncio
    async def test_no_newsapi_key_skips_fallback(self):
        """When GDELT fails and no API key, returns empty."""
        dispatcher = self._make_dispatcher(news_api_key=None)
        with patch.object(dispatcher, "_search_gdelt", new_callable=AsyncMock, return_value=None):
            results = await dispatcher.search("test company")
            assert results == []

    @pytest.mark.asyncio
    async def test_deduplication_across_sources(self):
        """Duplicate URLs from GDELT and RSS are deduplicated."""
        dispatcher = self._make_dispatcher()
        gdelt_data = [
            self._make_raw_data("https://shared.com/article", "gdelt"),
            self._make_raw_data("https://unique-gdelt.com", "gdelt"),
        ]
        rss_data = [
            self._make_raw_data("https://shared.com/article", "rss"),
            self._make_raw_data("https://unique-rss.com", "rss"),
        ]

        with patch.object(dispatcher, "_search_gdelt", new_callable=AsyncMock, return_value=gdelt_data):
            with patch.object(dispatcher, "_search_rss", new_callable=AsyncMock, return_value=rss_data):
                results = await dispatcher.search("test company")
                # 4 total, 1 duplicate -> 3 unique
                assert len(results) == 3
                urls = [r.source_url for r in results]
                assert "https://shared.com/article" in urls
                assert "https://unique-gdelt.com" in urls
                assert "https://unique-rss.com" in urls
