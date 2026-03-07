"""
News data connectors for news APIs and aggregators.

FREE sources:
- NewsAPI (100 requests/day free)
- Hacker News (free API)
- GDELT (free, no API key)
"""

import logging
from datetime import datetime
from typing import Any, Optional

import aiohttp
import feedparser

from ..base import BaseConnector, ConnectorResult, RawData, SourceConfig

logger = logging.getLogger(__name__)


class HackerNewsConnector(BaseConnector):
    """Connector for Hacker News (free, no API key)."""

    BASE_URL = "https://hacker-news.firebaseio.com/v0"

    def __init__(self, config: Optional[SourceConfig] = None):
        if config is None:
            config = SourceConfig(
                name="hacker_news",
                base_url=self.BASE_URL,
                rate_limit=60,
            )
        super().__init__(config)

    async def connect(self) -> bool:
        """Test connection to Hacker News."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.config.base_url}/topstories.json") as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Failed to connect to Hacker News: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        """Search HN by keyword (using Algolia HN Search)."""
        logger.info(f"Searching Hacker News for: {query}")

        try:
            # Use Algolia HN Search API
            algolia_url = "https://hn.algolia.com/api/v1/search"

            async with aiohttp.ClientSession() as session:
                params = {
                    "query": query,
                    "tags": "story",
                    "hitsPerPage": kwargs.get("limit", 10),
                }
                async with session.get(algolia_url, params=params) as response:
                    data = await response.json()

                    hits = data.get("hits", [])

                    raw_data_list = []
                    for hit in hits:
                        raw_data = RawData(
                            source_name=self.config.name,
                            source_url=hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                            raw_content=hit,
                            extracted_at=datetime.utcnow(),
                            metadata={
                                "story_id": hit.get("objectID"),
                                "author": hit.get("author"),
                                "points": hit.get("points"),
                                "num_comments": hit.get("num_comments"),
                                "created_at": hit.get("created_at"),
                                "source_type": "news",
                            },
                        )
                        raw_data_list.append(raw_data)

                    return ConnectorResult(
                        success=True,
                        data=raw_data_list,
                        total_found=data.get("nbHits", 0),
                    )

        except Exception as e:
            logger.error(f"Hacker News search failed: {e}")
            return ConnectorResult(
                success=False,
                data=[],
                error_message=str(e),
            )

    async def get_by_id(self, entity_id: str) -> ConnectorResult:
        """Get story by ID."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.config.base_url}/item/{entity_id}.json") as response:
                    data = await response.json()

                    if not data:
                        return ConnectorResult(success=True, data=[], total_found=0)

                    raw_data = RawData(
                        source_name=self.config.name,
                        source_url=f"https://news.ycombinator.com/item?id={entity_id}",
                        raw_content=data,
                        extracted_at=datetime.utcnow(),
                        metadata={"story_id": entity_id, "source_type": "news"},
                    )

                    return ConnectorResult(
                        success=True,
                        data=[raw_data],
                        total_found=1,
                    )
        except Exception as e:
            return ConnectorResult(success=False, data=[], error_message=str(e))

    def normalize(self, raw_data: RawData) -> dict[str, Any]:
        """Normalize HN story to common format."""
        content = raw_data.raw_content

        return {
            "source": "hacker_news",
            "entity_type": "news_story",
            "title": content.get("title") or content.get("story_text", "")[:100],
            "url": content.get("url") or raw_data.source_url,
            "author": content.get("author") or content.get("by"),
            "points": content.get("points", 0),
            "num_comments": content.get("num_comments", 0),
            "published_date": content.get("created_at") or content.get("time"),
            "raw_content": content,
        }


class NewsAPIConnector(BaseConnector):
    """Connector for NewsAPI (free tier: 100 requests/day)."""

    BASE_URL = "https://newsapi.org/v2"

    def __init__(self, api_key: str):
        config = SourceConfig(
            name="newsapi",
            base_url=self.BASE_URL,
            api_key=api_key,
            rate_limit=100,  # Daily limit for free tier
        )
        super().__init__(config)

    async def connect(self) -> bool:
        """Test connection to NewsAPI."""
        if not self.config.api_key:
            return False

        try:
            async with aiohttp.ClientSession() as session:
                params = {"apiKey": self.config.api_key, "q": "test", "pageSize": 1}
                async with session.get(f"{self.config.base_url}/everything", params=params) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Failed to connect to NewsAPI: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        """Search news articles."""
        if not self.config.api_key:
            return ConnectorResult(
                success=False,
                data=[],
                error_message="API key required",
            )

        logger.info(f"Searching NewsAPI for: {query}")

        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "apiKey": self.config.api_key,
                    "q": query,
                    "pageSize": kwargs.get("limit", 10),
                    "language": kwargs.get("language", "en"),
                    "sortBy": "relevancy",
                }

                # Add optional date filters
                if "from_date" in kwargs:
                    params["from"] = kwargs["from_date"]
                if "to_date" in kwargs:
                    params["to"] = kwargs["to_date"]

                async with session.get(f"{self.config.base_url}/everything", params=params) as response:
                    data = await response.json()

                    if data.get("status") != "ok":
                        return ConnectorResult(
                            success=False,
                            data=[],
                            error_message=data.get("message", "Unknown error"),
                        )

                    articles = data.get("articles", [])

                    raw_data_list = []
                    for article in articles:
                        raw_data = RawData(
                            source_name=self.config.name,
                            source_url=article.get("url"),
                            raw_content=article,
                            extracted_at=datetime.utcnow(),
                            metadata={
                                "source": article.get("source", {}).get("name"),
                                "author": article.get("author"),
                                "published_at": article.get("publishedAt"),
                                "source_type": "news",
                            },
                        )
                        raw_data_list.append(raw_data)

                    return ConnectorResult(
                        success=True,
                        data=raw_data_list,
                        total_found=data.get("totalResults", 0),
                    )

        except Exception as e:
            logger.error(f"NewsAPI search failed: {e}")
            return ConnectorResult(
                success=False,
                data=[],
                error_message=str(e),
            )

    async def get_by_id(self, entity_id: str) -> ConnectorResult:
        """NewsAPI doesn't support getting by ID directly."""
        return ConnectorResult(
            success=False,
            data=[],
            error_message="NewsAPI doesn't support ID-based retrieval",
        )

    def normalize(self, raw_data: RawData) -> dict[str, Any]:
        """Normalize news article to common format."""
        content = raw_data.raw_content

        return {
            "source": "newsapi",
            "entity_type": "news_article",
            "title": content.get("title"),
            "url": content.get("url"),
            "author": content.get("author"),
            "published_date": content.get("publishedAt"),
            "description": content.get("description"),
            "content_preview": content.get("content"),
            "source_name": content.get("source", {}).get("name"),
            "raw_content": content,
        }


class RSSFeedConnector(BaseConnector):
    """Generic RSS feed connector."""

    def __init__(self, feed_url: str, name: str = "rss"):
        config = SourceConfig(
            name=name,
            base_url=feed_url,
            rate_limit=30,
        )
        super().__init__(config)
        self.feed_url = feed_url

    async def connect(self) -> bool:
        """Test connection by parsing feed."""
        try:
            feed = feedparser.parse(self.feed_url)
            return len(feed.entries) > 0
        except Exception as e:
            logger.error(f"Failed to parse RSS feed: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        """Search RSS feed entries by keyword."""
        logger.info(f"Searching RSS feed for: {query}")

        try:
            feed = feedparser.parse(self.feed_url)

            query_lower = query.lower()
            matching_entries = []

            for entry in feed.entries:
                title = entry.get("title", "").lower()
                summary = entry.get("summary", "").lower()

                if query_lower in title or query_lower in summary:
                    raw_data = RawData(
                        source_name=self.config.name,
                        source_url=entry.get("link"),
                        raw_content=entry,
                        extracted_at=datetime.utcnow(),
                        metadata={
                            "published": entry.get("published"),
                            "author": entry.get("author"),
                            "source_type": "news",
                        },
                    )
                    matching_entries.append(raw_data)

            # Limit results
            limit = kwargs.get("limit", 10)
            matching_entries = matching_entries[:limit]

            return ConnectorResult(
                success=True,
                data=matching_entries,
                total_found=len(matching_entries),
            )

        except Exception as e:
            logger.error(f"RSS search failed: {e}")
            return ConnectorResult(
                success=False,
                data=[],
                error_message=str(e),
            )

    async def get_by_id(self, entity_id: str) -> ConnectorResult:
        """RSS doesn't support ID-based retrieval."""
        return ConnectorResult(
            success=False,
            data=[],
            error_message="RSS feeds don't support ID-based retrieval",
        )

    def normalize(self, raw_data: RawData) -> dict[str, Any]:
        """Normalize RSS entry to common format."""
        content = raw_data.raw_content

        return {
            "source": self.config.name,
            "entity_type": "rss_entry",
            "title": content.get("title"),
            "url": content.get("link"),
            "published_date": content.get("published"),
            "author": content.get("author"),
            "summary": content.get("summary"),
            "raw_content": content,
        }



__all__ = [
    "HackerNewsConnector",
    "NewsAPIConnector",
    "RSSFeedConnector",
]