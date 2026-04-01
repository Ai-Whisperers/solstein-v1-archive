"""News backend dispatching: GDELT primary, RSS supplement, NewsAPI fallback.

STORY-102: Extracted news source aggregation logic.
Provides the GDELT-primary / RSS-supplement / NewsAPI-fallback pipeline
with deduplication by URL.
"""

from __future__ import annotations

import logging
from typing import Any

from solstein.config import get_settings
from solstein.connectors.base import RawData
from solstein.connectors.news.gdelt import GDELTConnector, deduplicate_by_url
from solstein.connectors.news.rss import RSSFeedConnector

from .resilience import WEB_SEARCH_RETRY_CONFIG, CircuitBreaker, call_with_retry

logger = logging.getLogger(__name__)

# Default RSS feeds for company news (press wires, industry)
DEFAULT_RSS_FEEDS: list[tuple[str, str]] = [
    ("Reuters Business", "https://feeds.reuters.com/reuters/businessNews"),
    ("TechCrunch", "https://techcrunch.com/feed/"),
]


class NewsBackendDispatcher:
    """Dispatches news queries to GDELT (primary) with RSS and NewsAPI fallback.

    Pipeline:
    1. Query GDELT for broad news coverage (free, unlimited)
    2. Supplement with RSS feeds for targeted sources
    3. Fall back to NewsAPI only if GDELT fails and API key is configured
    4. Deduplicate all results by URL
    """

    def __init__(
        self,
        news_api_key: str | None = None,
        rss_feeds: list[tuple[str, str]] | None = None,
    ) -> None:
        _settings = get_settings()
        self.news_api_key = news_api_key
        self.rss_feeds = rss_feeds or DEFAULT_RSS_FEEDS
        self.http_timeout = _settings.http_timeouts.news_api

        self.gdelt = GDELTConnector()
        self.circuit_breaker_gdelt = CircuitBreaker(
            failure_threshold=_settings.circuit_breaker.failure_threshold,
            recovery_timeout=_settings.circuit_breaker.recovery_timeout,
            name="GDELT",
        )

    async def search(self, query: str, **kwargs: Any) -> list[RawData]:
        """Search all news backends and return deduplicated results."""
        all_results: list[RawData] = []

        # 1. GDELT (primary)
        gdelt_results = await self._search_gdelt(query, **kwargs)
        if gdelt_results:
            all_results.extend(gdelt_results)
            logger.info("[NewsDispatcher] GDELT returned %d articles", len(gdelt_results))

        # 2. RSS feeds (supplement)
        rss_results = await self._search_rss(query, **kwargs)
        if rss_results:
            all_results.extend(rss_results)
            logger.info("[NewsDispatcher] RSS returned %d articles", len(rss_results))

        # 3. NewsAPI fallback (only if GDELT failed AND key is configured)
        if not gdelt_results and self.news_api_key:
            logger.warning("[NewsDispatcher] GDELT unavailable, falling back to NewsAPI")
            newsapi_results = await self._search_newsapi(query, **kwargs)
            if newsapi_results:
                all_results.extend(newsapi_results)
                logger.info("[NewsDispatcher] NewsAPI returned %d articles", len(newsapi_results))

        if not all_results:
            logger.warning("[NewsDispatcher] All news backends returned empty for: %s", query[:50])
            return []

        # 4. Deduplicate by URL
        unique = deduplicate_by_url(all_results)
        logger.info(
            "[NewsDispatcher] %d total -> %d unique after dedup",
            len(all_results),
            len(unique),
        )
        return unique

    async def _search_gdelt(self, query: str, **kwargs: Any) -> list[RawData] | None:
        """Query GDELT. Returns None on failure."""
        try:
            result = await call_with_retry(
                lambda q=query, kw=kwargs: self.gdelt.search(q, **kw),
                retry_config=WEB_SEARCH_RETRY_CONFIG,
                circuit_breaker=self.circuit_breaker_gdelt,
                name="gdelt_search",
            )
            if result.success:
                return result.data
            logger.warning("[GDELT] Search returned failure: %s", result.error_message)
            return None
        except Exception as exc:
            logger.warning("[GDELT] Search failed: %s", exc)
            return None

    async def _search_rss(self, query: str, **kwargs: Any) -> list[RawData]:
        """Query configured RSS feeds. Returns empty list on failure."""
        results: list[RawData] = []
        limit_per_feed = kwargs.get("limit", 5)

        for feed_name, feed_url in self.rss_feeds:
            try:
                connector = RSSFeedConnector(feed_url=feed_url, name=feed_name)
                result = await connector.search(query, limit=limit_per_feed)
                if result.success and result.data:
                    results.extend(result.data)
            except Exception as exc:
                logger.warning("[RSS] Feed %s failed: %s", feed_name, exc)

        return results

    async def _search_newsapi(self, query: str, **kwargs: Any) -> list[RawData] | None:
        """Query NewsAPI as fallback. Returns None on failure or if not configured."""
        if not self.news_api_key:
            return None

        try:
            from solstein.connectors.news.newsapi import NewsAPIConnector

            connector = NewsAPIConnector(api_key=self.news_api_key)
            result = await connector.search(query, **kwargs)
            if result.success:
                return result.data
            logger.warning("[NewsAPI] Search returned failure: %s", result.error_message)
            return None
        except Exception as exc:
            logger.error("[NewsAPI] Search failed: %s", exc)
            return None
