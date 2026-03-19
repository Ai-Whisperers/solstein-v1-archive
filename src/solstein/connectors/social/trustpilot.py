"""Trustpilot connector for business reviews."""

import logging
from datetime import datetime, timezone
from typing import Any, Optional

import aiohttp

from ..base import BaseConnector, ConnectorResult, RawData, SourceConfig

logger = logging.getLogger(__name__)


class TrustpilotConnector(BaseConnector):
    """Connector for Trustpilot (requires API key)."""

    BASE_URL = "https://api.trustpilot.com/v1"

    def __init__(self, api_key: Optional[str] = None):
        config = SourceConfig(
            name="trustpilot",
            base_url=self.BASE_URL,
            api_key=api_key,
            rate_limit=100,
        )
        super().__init__(config)
        self._headers = {}
        if api_key:
            self._headers["apikey"] = api_key

    async def connect(self) -> bool:
        if not self.config.api_key:
            logger.warning("Trustpilot API key not provided")
            return False

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.config.base_url}/categories", headers=self._headers) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Failed to connect to Trustpilot: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        if not self.config.api_key:
            return ConnectorResult(success=False, data=[], error_message="API key required")

        try:
            async with aiohttp.ClientSession() as session:
                params = {"query": query, "perPage": kwargs.get("limit", 10)}

                async with session.get(
                    f"{self.config.base_url}/business-units", headers=self._headers, params=params
                ) as response:
                    data = await response.json()
                    businesses = data.get("businessUnits", [])

                    raw_data_list = []
                    for business in businesses:
                        raw_data = RawData(
                            source_name=self.config.name,
                            source_url=business.get("url"),
                            raw_content=business,
                            extracted_at=datetime.now(timezone.utc),
                            metadata={
                                "business_id": business.get("id"),
                                "rating": business.get("score", {}).get("trustScore"),
                                "source_type": "business_review",
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
        return ConnectorResult(success=False, data=[], error_message="Not implemented")

    def normalize(self, raw_data: RawData) -> dict[str, Any]:
        content = raw_data.raw_content

        return {
            "source": "trustpilot",
            "entity_type": "business_review",
            "name": content.get("displayName"),
            "url": content.get("url"),
            "rating": content.get("score", {}).get("trustScore"),
            "review_count": content.get("numberOfReviews", {}).get("total"),
            "category": content.get("category", {}).get("name"),
            "raw_data": content,
        }
