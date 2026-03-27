"""RSS Feed connector for generic feeds."""

import logging
from datetime import datetime, timezone
from typing import Any

import feedparser

from ..base import BaseConnector, ConnectorResult, RawData, SourceConfig

logger = logging.getLogger(__name__)


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
            return len(feed.entries) >= 0
        except Exception as e:
            logger.error(f"Failed to parse RSS feed: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        """Search RSS feed entries by keyword."""
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
                        extracted_at=datetime.now(timezone.utc),
                        metadata={
                            "published": entry.get("published"),
                            "author": entry.get("author"),
                            "source_type": "rss",
                        },
                    )
                    matching_entries.append(raw_data)

            limit = kwargs.get("limit", 10)
            matching_entries = matching_entries[:limit]

            return ConnectorResult(
                success=True,
                data=matching_entries,
                total_found=len(matching_entries),
            )
        except Exception as e:
            return ConnectorResult(success=False, data=[], error_message=str(e))

    async def get_by_id(self, entity_id: str) -> ConnectorResult:
        return ConnectorResult(
            success=False,
            data=[],
            error_message="RSS feeds don't support ID-based retrieval",
        )

    def normalize(self, raw_data: RawData) -> dict[str, Any]:
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
