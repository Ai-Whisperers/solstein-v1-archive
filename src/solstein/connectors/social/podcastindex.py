"""Podcast Index connector for podcast data."""

import logging
from datetime import datetime
from typing import Any, Optional

import aiohttp

from ..base import BaseConnector, ConnectorResult, RawData, SourceConfig

logger = logging.getLogger(__name__)


class PodcastIndexConnector(BaseConnector):
    """Connector for Podcast Index (free, open podcast database)."""

    BASE_URL = "https://api.podcastindex.org/api/1.0"

    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        config = SourceConfig(
            name="podcastindex",
            base_url=self.BASE_URL,
            api_key=api_key,
            rate_limit=1000,  # per hour
        )
        super().__init__(config)
        self.api_secret = api_secret

    async def connect(self) -> bool:
        """Test connection."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.config.base_url}/podcasts/byfeedid?id=75075") as response:
                    return response.status in [200, 401]  # 401 means API works but needs auth
        except Exception as e:
            logger.error(f"Failed to connect to Podcast Index: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        """Search podcasts."""
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "q": query,
                    "max": kwargs.get("limit", 10),
                }

                async with session.get(f"{self.config.base_url}/search/byterm", params=params) as response:
                    data = await response.json()
                    feeds = data.get("feeds", [])

                    raw_data_list = []
                    for feed in feeds:
                        raw_data = RawData(
                            source_name=self.config.name,
                            source_url=feed.get("link"),
                            raw_content=feed,
                            extracted_at=datetime.utcnow(),
                            metadata={
                                "feed_id": feed.get("id"),
                                "title": feed.get("title"),
                                "source_type": "podcast",
                            },
                        )
                        raw_data_list.append(raw_data)

                    return ConnectorResult(
                        success=True,
                        data=raw_data_list,
                        total_found=len(raw_data_list),
                    )
        except Exception as e:
            return ConnectorResult(success=False, data=[], error_message=str(e))

    async def get_by_id(self, entity_id: str) -> ConnectorResult:
        return ConnectorResult(success=False, data=[], error_message="Not implemented")

    def normalize(self, raw_data: RawData) -> dict[str, Any]:
        content = raw_data.raw_content

        return {
            "source": "podcastindex",
            "entity_type": "podcast",
            "title": content.get("title"),
            "url": content.get("link"),
            "feed_url": content.get("url"),
            "description": content.get("description"),
            "author": content.get("author"),
            "image": content.get("image"),
            "categories": content.get("categories", []),
            "episode_count": content.get("episodeCount"),
            "last_update": content.get("lastUpdateTime"),
            "raw_data": content,
        }
