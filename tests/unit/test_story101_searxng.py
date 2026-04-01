"""Tests for STORY-101: SearXNG web search integration.

Covers:
- SearXNG connector search and normalization
- SearchResult schema consistency between SearXNG and GCS
- Cache key generation and serialization round-trip
- SearchBackendDispatcher fallback logic (SearXNG -> GCS)
- Result normalization produces identical schema from both backends
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from solstein.agents.search_backends import SearchBackendDispatcher
from solstein.connectors.base import RawData
from solstein.connectors.search.searxng import (
    SearchResult,
    SearXNGConnector,
    cache_key_for_query,
    deserialize_results,
    normalize_gcs_to_search_result,
    serialize_results,
)

# -----------------------------------------------------------------------
# SearchResult schema tests
# -----------------------------------------------------------------------


class TestSearchResult:
    """Verify normalized search result schema."""

    def test_searxng_result_has_required_fields(self):
        """SearchResult from SearXNG has all required fields."""
        sr = SearchResult(
            title="Test Title",
            url="https://example.com",
            snippet="A test snippet",
            source_engine="google,bing",
            relevance_score=0.85,
            published_date="2026-03-01",
        )
        d = sr.to_dict()
        assert d["title"] == "Test Title"
        assert d["url"] == "https://example.com"
        assert d["snippet"] == "A test snippet"
        assert d["source_engine"] == "google,bing"
        assert d["relevance_score"] == 0.85
        assert d["published_date"] == "2026-03-01"

    def test_gcs_result_has_same_schema(self):
        """Google CSE result normalizes to identical schema."""
        gcs_item = {
            "title": "GCS Title",
            "link": "https://gcs.example.com",
            "snippet": "GCS snippet text",
            "displayLink": "gcs.example.com",
        }
        sr = normalize_gcs_to_search_result(gcs_item)
        d = sr.to_dict()

        expected_keys = {"title", "url", "snippet", "source_engine", "relevance_score", "published_date"}
        assert set(d.keys()) == expected_keys
        assert d["source_engine"] == "google_cse"
        assert d["url"] == "https://gcs.example.com"

    def test_schema_parity_between_backends(self):
        """Both backends produce results with identical dict keys."""
        searxng_result = SearchResult(
            title="A", url="https://a.com", snippet="a",
            source_engine="bing", relevance_score=0.5,
        )
        gcs_result = normalize_gcs_to_search_result({
            "title": "B", "link": "https://b.com", "snippet": "b",
        })
        assert set(searxng_result.to_dict().keys()) == set(gcs_result.to_dict().keys())


# -----------------------------------------------------------------------
# Cache key and serialization tests
# -----------------------------------------------------------------------


class TestCaching:
    """Verify cache key generation and serialization."""

    def test_cache_key_deterministic(self):
        """Same query always produces the same cache key."""
        k1 = cache_key_for_query("test query")
        k2 = cache_key_for_query("test query")
        assert k1 == k2
        assert k1.startswith("search:query:")

    def test_cache_key_case_insensitive(self):
        """Cache keys are case-insensitive."""
        k1 = cache_key_for_query("Test Query")
        k2 = cache_key_for_query("test query")
        assert k1 == k2

    def test_cache_key_trims_whitespace(self):
        """Leading/trailing whitespace doesn't change cache key."""
        k1 = cache_key_for_query("  test  ")
        k2 = cache_key_for_query("test")
        assert k1 == k2

    def test_different_queries_different_keys(self):
        """Different queries produce different cache keys."""
        k1 = cache_key_for_query("alpha")
        k2 = cache_key_for_query("beta")
        assert k1 != k2

    def test_serialization_round_trip(self):
        """Serialize -> deserialize produces identical SearchResult list."""
        original = [
            SearchResult(
                title="Title 1", url="https://a.com", snippet="Snippet 1",
                source_engine="google", relevance_score=0.9, published_date="2026-01-01",
            ),
            SearchResult(
                title="Title 2", url="https://b.com", snippet="Snippet 2",
                source_engine="bing,duckduckgo", relevance_score=0.7,
            ),
        ]
        serialized = serialize_results(original)
        deserialized = deserialize_results(serialized)

        assert len(deserialized) == 2
        assert deserialized[0].title == "Title 1"
        assert deserialized[0].url == "https://a.com"
        assert deserialized[0].source_engine == "google"
        assert deserialized[1].relevance_score == 0.7
        assert deserialized[1].published_date is None

    def test_empty_list_round_trip(self):
        """Empty list serializes and deserializes correctly."""
        s = serialize_results([])
        d = deserialize_results(s)
        assert d == []


# -----------------------------------------------------------------------
# SearXNG connector tests
# -----------------------------------------------------------------------


class TestSearXNGConnector:
    """Test SearXNG connector search and normalization."""

    def test_normalize_searxng_result(self):
        """SearXNG RawData normalizes to expected schema."""
        connector = SearXNGConnector(base_url="http://test:8080")
        raw = RawData(
            source_name="searxng",
            source_url="https://example.com/article",
            raw_content={
                "title": "Test Article",
                "url": "https://example.com/article",
                "content": "Article content snippet",
                "engines": ["google", "bing"],
                "score": 0.85,
                "publishedDate": "2026-03-15",
                "category": "general",
            },
            extracted_at=datetime.now(timezone.utc),
            metadata={},
        )
        normalized = connector.normalize(raw)
        assert normalized["source"] == "searxng"
        assert normalized["title"] == "Test Article"
        assert normalized["url"] == "https://example.com/article"
        assert normalized["snippet"] == "Article content snippet"
        assert normalized["source_engine"] == "google,bing"
        assert normalized["relevance_score"] == 0.85

    def test_normalize_to_search_result(self):
        """Static method converts RawData to SearchResult."""
        raw = RawData(
            source_name="searxng",
            source_url="https://test.com",
            raw_content={
                "title": "SR Title",
                "url": "https://test.com",
                "content": "SR Snippet",
                "engines": ["duckduckgo"],
                "score": 0.6,
            },
            extracted_at=datetime.now(timezone.utc),
            metadata={},
        )
        sr = SearXNGConnector.normalize_to_search_result(raw)
        assert sr.title == "SR Title"
        assert sr.source_engine == "duckduckgo"
        assert sr.relevance_score == 0.6

    @pytest.mark.asyncio
    async def test_get_by_id_not_supported(self):
        """get_by_id returns error for search engines."""
        connector = SearXNGConnector(base_url="http://test:8080")
        result = await connector.get_by_id("some-id")
        assert result.success is False
        assert "not support" in result.error_message.lower()


# -----------------------------------------------------------------------
# SearchBackendDispatcher fallback tests
# -----------------------------------------------------------------------


class TestSearchBackendDispatcher:
    """Test SearXNG primary / GCS fallback logic."""

    def _make_dispatcher(self, google_api_key="key", search_engine_id="cse"):
        """Create a dispatcher with mocked settings."""
        with patch("solstein.agents.search_backends.get_settings") as mock_settings:
            settings = MagicMock()
            settings.http_timeouts.web_search_agent = 15.0
            settings.circuit_breaker.failure_threshold = 5
            settings.circuit_breaker.recovery_timeout = 60.0
            settings.redis.url = ""
            mock_settings.return_value = settings

            return SearchBackendDispatcher(
                searxng_url="http://searxng:8080",
                searxng_engines=None,
                search_cache_ttl=3600,
                google_api_key=google_api_key,
                search_engine_id=search_engine_id,
            )

    @pytest.mark.asyncio
    async def test_searxng_primary_success(self):
        """When SearXNG succeeds, GCS is never called."""
        with patch("solstein.agents.search_backends.call_with_retry") as mock_retry:
            mock_retry.return_value = [
                SearchResult(
                    title="Result 1", url="https://a.com", snippet="Snippet",
                    source_engine="google", relevance_score=0.8,
                ),
            ]
            dispatcher = self._make_dispatcher()
            results = await dispatcher.search("test query")

            assert len(results) == 1
            assert results[0].source_engine == "google"
            assert mock_retry.call_count == 1

    @pytest.mark.asyncio
    async def test_searxng_failure_triggers_gcs_fallback(self):
        """When SearXNG fails, dispatcher falls back to Google CSE."""
        with patch("solstein.agents.search_backends.call_with_retry") as mock_retry:
            mock_retry.side_effect = [
                RuntimeError("SearXNG down"),
                [{"title": "GCS Result", "link": "https://gcs.com", "snippet": "GCS"}],
            ]
            dispatcher = self._make_dispatcher()
            results = await dispatcher.search("test query")

            assert len(results) == 1
            assert results[0].source_engine == "google_cse"
            assert mock_retry.call_count == 2

    @pytest.mark.asyncio
    async def test_both_backends_fail_returns_empty(self):
        """When both SearXNG and GCS fail, returns empty list."""
        with patch("solstein.agents.search_backends.call_with_retry") as mock_retry:
            mock_retry.side_effect = RuntimeError("All backends down")
            dispatcher = self._make_dispatcher()
            results = await dispatcher.search("test query")
            assert results == []

    @pytest.mark.asyncio
    async def test_no_gcs_config_skips_fallback(self):
        """When GCS is not configured, only SearXNG is attempted."""
        with patch("solstein.agents.search_backends.call_with_retry") as mock_retry:
            mock_retry.side_effect = RuntimeError("SearXNG down")
            dispatcher = self._make_dispatcher(google_api_key=None, search_engine_id=None)
            results = await dispatcher.search("test query")

            assert results == []
            assert mock_retry.call_count == 1


# -----------------------------------------------------------------------
# GCS normalization tests
# -----------------------------------------------------------------------


class TestGCSNormalization:
    """Verify Google CSE results normalize correctly."""

    def test_gcs_missing_fields_default(self):
        """GCS result with missing fields gets safe defaults."""
        gcs_item = {}
        sr = normalize_gcs_to_search_result(gcs_item)
        assert sr.title == ""
        assert sr.url == ""
        assert sr.snippet == ""
        assert sr.source_engine == "google_cse"
        assert sr.relevance_score == 0.0
        assert sr.published_date is None

    def test_gcs_full_result(self):
        """GCS result with all fields normalizes correctly."""
        gcs_item = {
            "title": "Full GCS",
            "link": "https://full.gcs.com",
            "snippet": "Full snippet from Google",
            "displayLink": "full.gcs.com",
        }
        sr = normalize_gcs_to_search_result(gcs_item)
        assert sr.title == "Full GCS"
        assert sr.url == "https://full.gcs.com"
        assert sr.snippet == "Full snippet from Google"
