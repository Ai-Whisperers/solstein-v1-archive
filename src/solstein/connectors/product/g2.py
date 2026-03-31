"""G2 connector for software reviews."""

import logging
from typing import Any

import aiohttp

from ..base import BaseConnector, ConnectorResult, RawData, SourceConfig

logger = logging.getLogger(__name__)


class G2Connector(BaseConnector):
    """Connector for G2 reviews (requires scraping or API)."""

    def __init__(self):
        config = SourceConfig(
            name="g2",
            base_url="https://www.g2.com",
            rate_limit=30,
        )
        super().__init__(config)

    async def connect(self) -> bool:
        """Test connection."""
        try:
            async with aiohttp.ClientSession() as session, session.get(self.config.base_url) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Failed to connect to G2: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        """Search products (requires scraping or API)."""
        logger.info(f"G2 search requires additional implementation: {query}")
        return ConnectorResult(success=True, data=[], total_found=0)

    async def get_by_id(self, entity_id: str) -> ConnectorResult:
        return ConnectorResult(success=False, data=[], error_message="Not implemented")

    def normalize(self, raw_data: RawData) -> dict[str, Any]:
        content = raw_data.raw_content

        return {
            "source": "g2",
            "entity_type": "software_review",
            "name": content.get("name"),
            "url": content.get("url"),
            "rating": content.get("rating"),
            "review_count": content.get("review_count"),
            "category": content.get("category"),
            "description": content.get("description"),
            "raw_data": content,
        }
