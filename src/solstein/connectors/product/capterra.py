"""Capterra connector for software reviews."""

import logging
from datetime import datetime
from typing import Any

from ..base import BaseConnector, ConnectorResult, RawData, SourceConfig

logger = logging.getLogger(__name__)


class CapterraConnector(BaseConnector):
    """Connector for Capterra (requires scraping or API)."""

    def __init__(self):
        config = SourceConfig(
            name="capterra",
            base_url="https://www.capterra.com",
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
            logger.error(f"Failed to connect to Capterra: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        """Search software (requires scraping or API)."""
        logger.info(f"Capterra search requires additional implementation: {query}")
        return ConnectorResult(success=True, data=[], total_found=0)

    async def get_by_id(self, entity_id: str) -> ConnectorResult:
        return ConnectorResult(success=False, data=[], error_message="Not implemented")

    def normalize(self, raw_data: RawData) -> dict[str, Any]:
        content = raw_data.raw_content

        return {
            "source": "capterra",
            "entity_type": "software_review",
            "name": content.get("name"),
            "url": content.get("url"),
            "rating": content.get("rating"),
            "review_count": content.get("review_count"),
            "category": content.get("category"),
            "description": content.get("description"),
            "raw_data": content,
        }
