"""BetaList connector for product launches."""

import logging
from datetime import datetime
from typing import Any

from ..base import BaseConnector, ConnectorResult, RawData, SourceConfig

logger = logging.getLogger(__name__)


class BetaListConnector(BaseConnector):
    """Connector for BetaList (requires scraping or API)."""

    def __init__(self):
        config = SourceConfig(
            name="betalist",
            base_url="https://betalist.com",
            rate_limit=30,
        )
        super().__init__(config)

    async def connect(self) -> bool:
        """Test connection."""
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.get(self.config.base_url) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Failed to connect to BetaList: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        """Search startups (requires scraping or API)."""
        logger.info(f"BetaList search requires additional implementation: {query}")
        return ConnectorResult(success=True, data=[], total_found=0)

    async def get_by_id(self, entity_id: str) -> ConnectorResult:
        return ConnectorResult(success=False, data=[], error_message="Not implemented")

    def normalize(self, raw_data: RawData) -> dict[str, Any]:
        content = raw_data.raw_content

        return {
            "source": "betalist",
            "entity_type": "startup",
            "name": content.get("name"),
            "url": content.get("url"),
            "description": content.get("description"),
            "stage": content.get("stage"),
            "launched_at": content.get("launched_at"),
            "raw_data": content,
        }
