"""Search backend dispatching: SearXNG primary, Google CSE fallback.

STORY-101: Extracted from WebSearchAgent to keep class under 300 lines.
Provides the search-with-fallback logic and Redis caching layer.
"""

from __future__ import annotations

import logging

import httpx
import redis

from solstein.config import get_settings
from solstein.connectors.search.searxng import (
    SearchResult,
    cache_key_for_query,
    deserialize_results,
    normalize_gcs_to_search_result,
    serialize_results,
)

from .resilience import WEB_SEARCH_RETRY_CONFIG, CircuitBreaker, call_with_retry

logger = logging.getLogger(__name__)


class SearchBackendDispatcher:
    """Dispatches search queries to SearXNG (primary) with GCS fallback.

    Also handles Redis-based result caching with configurable TTL.
    """

    def __init__(
        self,
        searxng_url: str,
        searxng_engines: str | None,
        search_cache_ttl: int,
        google_api_key: str | None,
        search_engine_id: str | None,
    ) -> None:
        self.searxng_url = searxng_url.rstrip("/")
        self.searxng_engines = searxng_engines
        self.search_cache_ttl = search_cache_ttl
        self.google_api_key = google_api_key
        self.search_engine_id = search_engine_id
        self.gcs_base = "https://www.googleapis.com/customsearch/v1"

        _settings = get_settings()
        self.http_timeout = _settings.http_timeouts.web_search_agent

        self.circuit_breaker_searxng = CircuitBreaker(
            failure_threshold=_settings.circuit_breaker.failure_threshold,
            recovery_timeout=_settings.circuit_breaker.recovery_timeout,
            name="SearXNG",
        )
        self.circuit_breaker_gcs = CircuitBreaker(
            failure_threshold=_settings.circuit_breaker.failure_threshold,
            recovery_timeout=_settings.circuit_breaker.recovery_timeout,
            name="GoogleCSE",
        )

    async def search(self, query: str) -> list[SearchResult]:
        """Search with SearXNG primary / GCS fallback and Redis cache."""
        cached = self._get_cached_results(query)
        if cached is not None:
            logger.info("Cache hit for query: %s...", query[:50])
            return cached

        # Try SearXNG (primary)
        results = await self._search_searxng(query)
        if results is not None:
            self._cache_results(query, results)
            return results

        # SearXNG failed — fall back to GCS
        logger.warning(
            "SearXNG unavailable, falling back to Google CSE for: %s...",
            query[:50],
        )
        results = await self._search_gcs(query)
        if results is not None:
            self._cache_results(query, results)
            return results

        logger.error("Both SearXNG and Google CSE failed for query")
        return []

    # ------------------------------------------------------------------
    # SearXNG
    # ------------------------------------------------------------------

    async def _search_searxng(self, query: str) -> list[SearchResult] | None:
        """Query SearXNG. Returns None on failure."""
        try:
            return await call_with_retry(
                lambda q=query: self._api_searxng(q),
                retry_config=WEB_SEARCH_RETRY_CONFIG,
                circuit_breaker=self.circuit_breaker_searxng,
                name="searxng_search",
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("SearXNG search failed: %s", exc)
            return None

    async def _api_searxng(self, query: str) -> list[SearchResult]:
        """Direct API call to SearXNG JSON endpoint."""
        params: dict = {"q": query, "format": "json", "language": "en"}
        if self.searxng_engines:
            params["engines"] = self.searxng_engines

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.searxng_url}/search",
                params=params,
                timeout=self.http_timeout,
            )
            if resp.status_code != 200:
                raise RuntimeError(f"SearXNG HTTP {resp.status_code}")
            data = resp.json()
            items = data.get("results", [])
            results: list[SearchResult] = []
            for item in items[:10]:
                engines = item.get("engines", [])
                results.append(
                    SearchResult(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        snippet=item.get("content", ""),
                        source_engine=",".join(engines) if engines else "searxng",
                        relevance_score=item.get("score", 0.0),
                        published_date=item.get("publishedDate"),
                    )
                )
            return results

    # ------------------------------------------------------------------
    # Google CSE fallback
    # ------------------------------------------------------------------

    async def _search_gcs(self, query: str) -> list[SearchResult] | None:
        """Query Google CSE as fallback. Returns None on failure."""
        if not self.google_api_key or not self.search_engine_id:
            logger.warning("Google CSE not configured, cannot fall back")
            return None
        try:
            gcs_items = await call_with_retry(
                lambda q=query: self._api_gcs(q),
                retry_config=WEB_SEARCH_RETRY_CONFIG,
                circuit_breaker=self.circuit_breaker_gcs,
                name="gcs_search",
            )
            return [normalize_gcs_to_search_result(item) for item in gcs_items]
        except Exception as exc:  # noqa: BLE001
            logger.error("Google CSE search failed: %s", exc)
            return None

    async def _api_gcs(self, query: str) -> list[dict]:
        """API call to Google Custom Search."""
        params = {
            "q": query,
            "key": self.google_api_key,
            "cx": self.search_engine_id,
            "num": 10,
            "sort": "date",
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(self.gcs_base, params=params, timeout=self.http_timeout)
            if resp.status_code == 200:
                return resp.json().get("items", [])
            raise RuntimeError(f"Google CSE HTTP {resp.status_code}")

    # ------------------------------------------------------------------
    # Redis caching
    # ------------------------------------------------------------------

    def _get_cached_results(self, query: str) -> list[SearchResult] | None:
        """Check Redis for cached results (sync call, thread-safe)."""
        try:
            r = self._get_redis()
            if r is None:
                return None
            cached = r.get(cache_key_for_query(query))
            if cached:
                return deserialize_results(cached)
        except Exception as exc:  # noqa: BLE001
            logger.debug("[SearchCache] Redis read failed: %s", exc)
        return None

    def _cache_results(self, query: str, results: list[SearchResult]) -> None:
        """Store results in Redis with TTL."""
        try:
            r = self._get_redis()
            if r is None:
                return
            r.setex(cache_key_for_query(query), self.search_cache_ttl, serialize_results(results))
        except Exception as exc:  # noqa: BLE001
            logger.debug("[SearchCache] Redis write failed: %s", exc)

    def _get_redis(self) -> redis.Redis | None:
        """Get Redis client, or None if unavailable."""
        try:
            settings = get_settings()
            if not settings.redis.url:
                return None
            return redis.Redis.from_url(settings.redis.url, decode_responses=True)
        except Exception:  # noqa: BLE001
            return None
