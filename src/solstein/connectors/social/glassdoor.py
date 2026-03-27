"""Glassdoor connector for company reviews."""

import logging
from typing import Any

from ..base import BaseConnector, ConnectorResult, RawData, SourceConfig

logger = logging.getLogger(__name__)


class GlassdoorConnector(BaseConnector):
    """Connector for Glassdoor reviews (requires scraping or API)."""

    def __init__(self):
        config = SourceConfig(
            name="glassdoor",
            base_url="https://www.glassdoor.com",
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
            logger.error(f"Failed to connect to Glassdoor: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        """Search companies (requires scraping or API)."""
        logger.info(f"Glassdoor search requires additional implementation: {query}")
        return ConnectorResult(success=True, data=[], total_found=0)

    async def get_by_id(self, entity_id: str) -> ConnectorResult:
        return ConnectorResult(success=False, data=[], error_message="Not implemented")

    def normalize(self, raw_data: RawData) -> dict[str, Any]:
        content = raw_data.raw_content

        return {
            "source": "glassdoor",
            "entity_type": "company_review",
            "company": content.get("company"),
            "rating": content.get("rating"),
            "review_count": content.get("review_count"),
            "recommendation_percentage": content.get("recommendation_percentage"),
            "ceo_approval": content.get("ceo_approval"),
            "pros": content.get("pros", []),
            "cons": content.get("cons", []),
            "raw_data": content,
        }
