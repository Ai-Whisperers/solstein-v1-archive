"""F6S connector for startup programs and funding."""

import logging
from typing import Any

from ..base import BaseConnector, ConnectorResult, RawData, SourceConfig

logger = logging.getLogger(__name__)


class F6SConnector(BaseConnector):
    """Connector for F6S (requires scraping or API)."""

    def __init__(self):
        config = SourceConfig(
            name="f6s",
            base_url="https://www.f6s.com",
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
            logger.error(f"Failed to connect to F6S: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        """Search startups/programs (requires scraping or API)."""
        logger.info(f"F6S search requires additional implementation: {query}")
        return ConnectorResult(success=True, data=[], total_found=0)

    async def get_by_id(self, entity_id: str) -> ConnectorResult:
        return ConnectorResult(success=False, data=[], error_message="Not implemented")

    def normalize(self, raw_data: RawData) -> dict[str, Any]:
        content = raw_data.raw_content

        return {
            "source": "f6s",
            "entity_type": "startup",
            "name": content.get("name"),
            "url": content.get("url"),
            "description": content.get("description"),
            "stage": content.get("stage"),
            "location": content.get("location"),
            "founded": content.get("founded"),
            "team_size": content.get("team_size"),
            "raw_data": content,
        }
