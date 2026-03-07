"""Hacker News connector for tech news."""

import logging
from datetime import datetime
from typing import Any, Optional

import aiohttp

from ..base import BaseConnector, ConnectorResult, RawData, SourceConfig

logger = logging.getLogger(__name__)


class HackerNewsConnector(BaseConnector):
    """Connector for Hacker News."""

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
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.config.base_url}/topstories.json") as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Failed to connect to Hacker News: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        try:
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
            return ConnectorResult(success=False, data=[], error_message=str(e))

    async def get_by_id(self, entity_id: str) -> ConnectorResult:
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

                    return ConnectorResult(success=True, data=[raw_data], total_found=1)
        except Exception as e:
            return ConnectorResult(success=False, data=[], error_message=str(e))

    def normalize(self, raw_data: RawData) -> dict[str, Any]:
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
