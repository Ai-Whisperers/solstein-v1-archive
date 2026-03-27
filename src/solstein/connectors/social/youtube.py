"""YouTube connector for video content."""

import logging
from datetime import datetime, timezone
from typing import Any

from ..base import BaseConnector, ConnectorResult, RawData, SourceConfig

logger = logging.getLogger(__name__)


class YouTubeConnector(BaseConnector):
    """Connector for YouTube Data API."""

    BASE_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(self, api_key: str | None = None):
        config = SourceConfig(
            name="youtube",
            base_url=self.BASE_URL,
            api_key=api_key,
            rate_limit=10000,  # per day
        )
        super().__init__(config)

    async def connect(self) -> bool:
        if not self.config.api_key:
            logger.warning("YouTube API key not provided")
            return False

        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                params = {"part": "snippet", "id": "dQw4w9WgXcQ", "key": self.config.api_key}
                async with session.get(f"{self.config.base_url}/videos", params=params) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Failed to connect to YouTube: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        if not self.config.api_key:
            return ConnectorResult(success=False, data=[], error_message="API key required")

        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                params = {
                    "part": "snippet",
                    "q": query,
                    "type": "video",
                    "maxResults": kwargs.get("limit", 10),
                    "key": self.config.api_key,
                }

                async with session.get(f"{self.config.base_url}/search", params=params) as response:
                    data = await response.json()
                    items = data.get("items", [])

                    raw_data_list = []
                    for item in items:
                        video_id = item.get("id", {}).get("videoId")
                        snippet = item.get("snippet", {})

                        raw_data = RawData(
                            source_name=self.config.name,
                            source_url=f"https://youtube.com/watch?v={video_id}",
                            raw_content=item,
                            extracted_at=datetime.now(timezone.utc),
                            metadata={
                                "video_id": video_id,
                                "channel_id": snippet.get("channelId"),
                                "source_type": "video",
                            },
                        )
                        raw_data_list.append(raw_data)

                    return ConnectorResult(success=True, data=raw_data_list, total_found=len(items))
        except Exception as e:
            return ConnectorResult(success=False, data=[], error_message=str(e))

    async def get_by_id(self, entity_id: str) -> ConnectorResult:
        return ConnectorResult(success=False, data=[], error_message="Not implemented")

    def normalize(self, raw_data: RawData) -> dict[str, Any]:
        content = raw_data.raw_content
        snippet = content.get("snippet", {})

        return {
            "source": "youtube",
            "entity_type": "video",
            "video_id": raw_data.metadata.get("video_id"),
            "title": snippet.get("title"),
            "description": snippet.get("description"),
            "url": raw_data.source_url,
            "channel": snippet.get("channelTitle"),
            "channel_id": snippet.get("channelId"),
            "published_at": snippet.get("publishedAt"),
            "thumbnails": snippet.get("thumbnails", {}),
            "raw_data": content,
        }
