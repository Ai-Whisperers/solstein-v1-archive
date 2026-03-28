"""GDELT (Global Database of Events, Language, and Tone) news connector.

STORY-102: GDELT replaces NewsAPI as the primary news intelligence backend.
GDELT is free, open-access, covers 100+ languages, and provides structured
event data including tone analysis. No API key required.

GDELT DOC 2.0 API reference: https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote

import aiohttp

from solstein.connectors.base import BaseConnector, ConnectorResult, RawData, SourceConfig

logger = logging.getLogger(__name__)

# GDELT DOC 2.0 API base URL
GDELT_DOC_API = "https://api.gdeltproject.org/api/v2/doc/doc"


@dataclass
class GDELTArticle:
    """Normalized GDELT article from DOC 2.0 API."""

    url: str
    title: str
    source_name: str
    language: str
    published_date: str
    tone: float = 0.0
    domain: str = ""
    seendate: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict for caching and API responses."""
        return {
            "url": self.url,
            "title": self.title,
            "source_name": self.source_name,
            "language": self.language,
            "published_date": self.published_date,
            "tone": self.tone,
            "domain": self.domain,
            "seendate": self.seendate,
        }


class GDELTConnector(BaseConnector):
    """Connector for the GDELT DOC 2.0 API.

    GDELT aggregates news from tens of thousands of sources worldwide.
    The DOC API provides full-text search across articles with tone
    analysis, geographic tagging, and theme classification.

    No API key required. Rate limit is generous but we self-limit to
    avoid hammering a free public service.
    """

    def __init__(self) -> None:
        config = SourceConfig(
            name="gdelt",
            base_url=GDELT_DOC_API,
            rate_limit=120,  # Self-imposed: 2 requests/sec
            timeout=20,
        )
        super().__init__(config)

    async def connect(self) -> bool:
        """Verify GDELT API is reachable."""
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "query": "test",
                    "mode": "artlist",
                    "maxrecords": "1",
                    "format": "json",
                }
                async with session.get(
                    GDELT_DOC_API,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    return resp.status == 200
        except Exception as exc:
            logger.warning("[GDELT] Health check failed: %s", exc)
            return False

    async def search(self, query: str, **kwargs: Any) -> ConnectorResult:
        """Search GDELT DOC 2.0 API for news articles.

        Args:
            query: Search query (company name, keywords).
            **kwargs: Optional overrides -- ``limit``, ``language``,
                      ``timespan`` (e.g. '7d', '30d'), ``mode``.

        Returns:
            ConnectorResult with normalized RawData entries.
        """
        timespan = kwargs.get("timespan", "30d")
        limit = kwargs.get("limit", 25)
        mode = kwargs.get("mode", "artlist")

        params: dict[str, str] = {
            "query": quote(query, safe=""),
            "mode": mode,
            "maxrecords": str(min(limit, 250)),
            "format": "json",
            "timespan": timespan,
        }
        lang = kwargs.get("language")
        if lang:
            params["sourcelang"] = lang

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    GDELT_DOC_API,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout),
                ) as resp:
                    if resp.status != 200:
                        body = await resp.text()
                        logger.error("[GDELT] HTTP %d: %s", resp.status, body[:200])
                        return ConnectorResult(
                            success=False,
                            data=[],
                            error_message=f"GDELT returned HTTP {resp.status}",
                        )

                    data = await resp.json(content_type=None)

            articles = data.get("articles", [])
            raw_items: list[RawData] = []
            for idx, article in enumerate(articles[:limit]):
                raw = RawData(
                    source_name="gdelt",
                    source_url=article.get("url", ""),
                    raw_content=article,
                    extracted_at=datetime.now(timezone.utc),
                    metadata={
                        "source_type": "news",
                        "tone": article.get("tone", 0.0),
                        "domain": article.get("domain", ""),
                        "language": article.get("language", ""),
                        "seendate": article.get("seendate", ""),
                        "rank": idx,
                    },
                )
                raw_items.append(raw)

            return ConnectorResult(
                success=True,
                data=raw_items,
                total_found=len(articles),
            )

        except aiohttp.ClientError as exc:
            logger.error("[GDELT] Connection error: %s", exc)
            return ConnectorResult(
                success=False,
                data=[],
                error_message=f"GDELT connection error: {exc}",
            )
        except Exception as exc:
            logger.error("[GDELT] Unexpected error: %s", exc)
            return ConnectorResult(
                success=False,
                data=[],
                error_message=f"GDELT error: {exc}",
            )

    async def get_by_id(self, entity_id: str) -> ConnectorResult:
        """Not supported -- GDELT is a search engine, not an entity store."""
        return ConnectorResult(
            success=False,
            data=[],
            error_message="GDELT does not support ID-based retrieval",
        )

    def normalize(self, raw_data: RawData) -> dict[str, Any]:
        """Normalize GDELT article to common news schema."""
        content = raw_data.raw_content
        return {
            "source": "gdelt",
            "entity_type": "news_article",
            "title": content.get("title", ""),
            "url": content.get("url", ""),
            "source_name": content.get("sourcecountry", content.get("domain", "")),
            "published_date": content.get("seendate", ""),
            "language": content.get("language", "English"),
            "tone": content.get("tone", 0.0),
            "domain": content.get("domain", ""),
        }

    def _handle_rate_limit(self, response_headers: dict[str, Any]) -> None:
        """GDELT is free -- no external rate limit headers to handle."""
        pass

    @staticmethod
    def normalize_to_article(raw_data: RawData) -> GDELTArticle:
        """Convert a GDELT RawData entry to a GDELTArticle."""
        content = raw_data.raw_content
        return GDELTArticle(
            url=content.get("url", ""),
            title=content.get("title", ""),
            source_name=content.get("domain", ""),
            language=content.get("language", "English"),
            published_date=content.get("seendate", ""),
            tone=content.get("tone", 0.0),
            domain=content.get("domain", ""),
            seendate=content.get("seendate", ""),
        )


def deduplicate_by_url(articles: list[RawData]) -> list[RawData]:
    """Deduplicate articles by URL.

    Same article from multiple sources (GDELT, RSS, NewsAPI) = one record.
    Uses URL as the deduplication key.
    """
    seen: set[str] = set()
    unique: list[RawData] = []
    for article in articles:
        url = article.source_url or ""
        url_key = hashlib.sha256(url.strip().lower().encode()).hexdigest()[:16]
        if url_key not in seen:
            seen.add(url_key)
            unique.append(article)
    return unique
