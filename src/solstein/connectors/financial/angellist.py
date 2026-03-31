"""AngelList connector for startup data."""

import logging
from typing import Any

from ..base import BaseConnector, ConnectorResult, RawData, SourceConfig

logger = logging.getLogger(__name__)


class AngelListConnector(BaseConnector):
    """Connector for AngelList (requires scraping or API)."""

    def __init__(self):
        config = SourceConfig(
            name="angellist",
            base_url="https://angel.co",
            rate_limit=30,
        )
        super().__init__(config)

    async def connect(self) -> bool:
        """Test connection."""
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session, session.get(self.config.base_url) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Failed to connect to AngelList: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        """Search startups (requires scraping or API)."""
        logger.info(f"AngelList search requires additional implementation: {query}")
        return ConnectorResult(success=True, data=[], total_found=0)

    async def get_by_id(self, entity_id: str) -> ConnectorResult:
        return ConnectorResult(success=False, data=[], error_message="Not implemented")

    def normalize(self, raw_data: RawData) -> dict[str, Any]:
        content = raw_data.raw_content

        return {
            "source": "angellist",
            "entity_type": "startup",
            "name": content.get("name"),
            "url": content.get("url"),
            "description": content.get("description"),
            "stage": content.get("stage"),
            "raised": content.get("raised"),
            "employees": content.get("employees"),
            "market": content.get("market"),
            "raw_data": content,
        }
