"""LinkedIn connector for company data (requires scraping or API)."""

import logging
from typing import Any

from ..base import BaseConnector, ConnectorResult, RawData, SourceConfig

logger = logging.getLogger(__name__)


class LinkedInConnector(BaseConnector):
    """Connector for LinkedIn company data."""

    BASE_URL = "https://api.linkedin.com/v2"

    def __init__(self, access_token: str | None = None):
        config = SourceConfig(
            name="linkedin",
            base_url=self.BASE_URL,
            api_key=access_token,
            rate_limit=500,  # per day
        )
        super().__init__(config)
        self._headers = {}
        if access_token:
            self._headers["Authorization"] = f"Bearer {access_token}"

    async def connect(self) -> bool:
        if not self.config.api_key:
            logger.warning("LinkedIn access token not provided")
            return False

        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.config.base_url}/me", headers=self._headers) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Failed to connect to LinkedIn: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        """Search for companies."""
        if not self.config.api_key:
            return ConnectorResult(success=False, data=[], error_message="Access token required")

        # LinkedIn API requires specific permissions for company search
        logger.info(f"LinkedIn search not implemented: {query}")
        return ConnectorResult(success=True, data=[], total_found=0)

    async def get_by_id(self, entity_id: str) -> ConnectorResult:
        """Get company by LinkedIn ID."""
        return ConnectorResult(success=False, data=[], error_message="Not implemented")

    def normalize(self, raw_data: RawData) -> dict[str, Any]:
        content = raw_data.raw_content

        return {
            "source": "linkedin",
            "entity_type": "company",
            "name": content.get("localizedName"),
            "description": content.get("description", {}).get("localized", {}).get("en_US"),
            "industry": content.get("industry"),
            "company_size": content.get("staffCountRange"),
            "website": content.get("websiteUrl"),
            "specialties": content.get("specialities", []),
            "raw_data": content,
        }
