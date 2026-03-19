"""Stack Overflow connector for developer activity."""

import logging
from datetime import datetime, timezone
from typing import Any, Optional

import aiohttp

from ..base import BaseConnector, ConnectorResult, RawData, SourceConfig

logger = logging.getLogger(__name__)


class StackOverflowConnector(BaseConnector):
    """Connector for Stack Overflow API."""

    BASE_URL = "https://api.stackexchange.com/2.3"

    def __init__(self, api_key: Optional[str] = None):
        config = SourceConfig(
            name="stackoverflow",
            base_url=self.BASE_URL,
            api_key=api_key,
            rate_limit=100,  # with key: 10000/day, without: 300/day
        )
        super().__init__(config)

    async def connect(self) -> bool:
        """Test connection to Stack Overflow."""
        try:
            async with aiohttp.ClientSession() as session:
                params = {"site": "stackoverflow", "pagesize": 1}
                if self.config.api_key:
                    params["key"] = self.config.api_key

                async with session.get(f"{self.config.base_url}/questions", params=params) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Failed to connect to Stack Overflow: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        """Search questions."""
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "site": "stackoverflow",
                    "intitle": query,
                    "pagesize": kwargs.get("limit", 10),
                    "sort": "relevance",
                    "order": "desc",
                }
                if self.config.api_key:
                    params["key"] = self.config.api_key

                async with session.get(f"{self.config.base_url}/search/advanced", params=params) as response:
                    data = await response.json()

                    items = data.get("items", [])

                    raw_data_list = []
                    for item in items:
                        raw_data = RawData(
                            source_name=self.config.name,
                            source_url=item.get("link"),
                            raw_content=item,
                            extracted_at=datetime.now(timezone.utc),
                            metadata={
                                "question_id": item.get("question_id"),
                                "tags": item.get("tags", []),
                                "source_type": "developer_qa",
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
        """Get question by ID."""
        return ConnectorResult(success=False, data=[], error_message="Not implemented")

    def normalize(self, raw_data: RawData) -> dict[str, Any]:
        content = raw_data.raw_content

        return {
            "source": "stackoverflow",
            "entity_type": "developer_qa",
            "title": content.get("title"),
            "url": content.get("link"),
            "question_id": content.get("question_id"),
            "score": content.get("score"),
            "answer_count": content.get("answer_count"),
            "view_count": content.get("view_count"),
            "tags": content.get("tags", []),
            "is_answered": content.get("is_answered"),
            "creation_date": datetime.fromtimestamp(content.get("creation_date", 0)),
            "owner": content.get("owner", {}).get("display_name"),
            "raw_data": content,
        }
