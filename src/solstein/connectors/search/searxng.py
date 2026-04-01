"""SearXNG meta-search engine connector.

STORY-101: Self-hosted SearXNG replaces Google Custom Search as the primary
web search backend. SearXNG aggregates results from Google, Bing, DuckDuckGo,
and Brave Search through their public interfaces — free, unlimited, and under
platform control.

SearXNG JSON API reference: https://docs.searxng.org/dev/search_api.html
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import aiohttp

from solstein.connectors.base import BaseConnector, ConnectorResult, RawData, SourceConfig

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Normalized search result from any backend."""

    title: str
    url: str
    snippet: str
    source_engine: str
    relevance_score: float = 0.0
    published_date: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict for caching and API responses."""
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "source_engine": self.source_engine,
            "relevance_score": self.relevance_score,
            "published_date": self.published_date,
        }


class SearXNGConnector(BaseConnector):
    """Connector for a self-hosted SearXNG instance.

    SearXNG aggregates results from multiple search engines and returns
    deduplicated, ranked results via its JSON API. This replaces Google
    Custom Search as the primary web search backend.
    """

    def __init__(
        self,
        base_url: str = "http://searxng:8080",
        engines: str | None = None,
    ) -> None:
        config = SourceConfig(
            name="searxng",
            base_url=base_url.rstrip("/"),
            rate_limit=600,  # internal service, generous limit
            timeout=15,
        )
        super().__init__(config)
        self.engines = engines  # comma-separated engine list, e.g. "google,bing,duckduckgo"

    async def connect(self) -> bool:
        """Verify SearXNG instance is reachable."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.config.base_url}/healthz",
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as resp:
                    return resp.status == 200
        except Exception as exc:
            logger.warning("[SearXNG] Health check failed: %s", exc)
            return False

    async def search(self, query: str, **kwargs: Any) -> ConnectorResult:
        """Search via SearXNG JSON API.

        Args:
            query: Search query string.
            **kwargs: Optional overrides — ``limit``, ``language``, ``time_range``,
                      ``engines`` (comma-separated).

        Returns:
            ConnectorResult with normalized RawData entries.
        """
        params: dict[str, Any] = {
            "q": query,
            "format": "json",
            "language": kwargs.get("language", "en"),
        }
        if self.engines or kwargs.get("engines"):
            params["engines"] = kwargs.get("engines", self.engines)
        if kwargs.get("time_range"):
            params["time_range"] = kwargs["time_range"]

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.config.base_url}/search",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout),
                ) as resp:
                    if resp.status != 200:
                        body = await resp.text()
                        logger.error(
                            "[SearXNG] HTTP %d: %s",
                            resp.status,
                            body[:200],
                        )
                        return ConnectorResult(
                            success=False,
                            data=[],
                            error_message=f"SearXNG returned HTTP {resp.status}",
                        )

                    data = await resp.json()

            results = data.get("results", [])
            limit = kwargs.get("limit", 10)
            results = results[:limit]

            raw_items: list[RawData] = []
            for idx, item in enumerate(results):
                raw = RawData(
                    source_name="searxng",
                    source_url=item.get("url", ""),
                    raw_content=item,
                    extracted_at=datetime.now(timezone.utc),
                    metadata={
                        "source_type": "web_search",
                        "engines": item.get("engines", []),
                        "score": item.get("score", 0.0),
                        "category": item.get("category", "general"),
                        "rank": idx,
                    },
                )
                raw_items.append(raw)

            return ConnectorResult(
                success=True,
                data=raw_items,
                total_found=len(data.get("results", [])),
            )

        except aiohttp.ClientError as exc:
            logger.error("[SearXNG] Connection error: %s", exc)
            return ConnectorResult(
                success=False,
                data=[],
                error_message=f"SearXNG connection error: {exc}",
            )
        except Exception as exc:
            logger.error("[SearXNG] Unexpected error: %s", exc)
            return ConnectorResult(
                success=False,
                data=[],
                error_message=f"SearXNG error: {exc}",
            )

    async def get_by_id(self, entity_id: str) -> ConnectorResult:
        """Not supported — SearXNG is a search engine, not an entity store."""
        return ConnectorResult(
            success=False,
            data=[],
            error_message="SearXNG does not support ID-based retrieval",
        )

    def normalize(self, raw_data: RawData) -> dict[str, Any]:
        """Normalize SearXNG result to common search result schema."""
        content = raw_data.raw_content
        return {
            "source": "searxng",
            "entity_type": "search_result",
            "title": content.get("title", ""),
            "url": content.get("url", ""),
            "snippet": content.get("content", ""),
            "source_engine": ",".join(content.get("engines", [])),
            "relevance_score": content.get("score", 0.0),
            "published_date": content.get("publishedDate"),
            "category": content.get("category", "general"),
        }

    def _handle_rate_limit(self, response_headers: dict) -> None:
        """SearXNG is self-hosted — no external rate limit headers to handle."""
        pass

    @staticmethod
    def normalize_to_search_result(raw_data: RawData) -> SearchResult:
        """Convert a SearXNG RawData entry to a SearchResult."""
        content = raw_data.raw_content
        engines = content.get("engines", [])
        return SearchResult(
            title=content.get("title", ""),
            url=content.get("url", ""),
            snippet=content.get("content", ""),
            source_engine=",".join(engines) if engines else "searxng",
            relevance_score=content.get("score", 0.0),
            published_date=content.get("publishedDate"),
        )


def normalize_gcs_to_search_result(item: dict[str, Any]) -> SearchResult:
    """Convert a Google Custom Search API result to a SearchResult.

    This ensures both SearXNG and GCS results conform to the same schema.
    """
    return SearchResult(
        title=item.get("title", ""),
        url=item.get("link", ""),
        snippet=item.get("snippet", ""),
        source_engine="google_cse",
        relevance_score=0.0,
        published_date=None,
    )


def cache_key_for_query(query: str) -> str:
    """Generate a deterministic Redis cache key for a search query.

    Key format: ``search:query:<sha256_hex[:16]>``
    """
    h = hashlib.sha256(query.strip().lower().encode()).hexdigest()[:16]
    return f"search:query:{h}"


def serialize_results(results: list[SearchResult]) -> str:
    """Serialize search results to JSON string for Redis caching."""
    return json.dumps([r.to_dict() for r in results])


def deserialize_results(data: str) -> list[SearchResult]:
    """Deserialize cached JSON string back to SearchResult list."""
    items = json.loads(data)
    return [SearchResult(**item) for item in items]
