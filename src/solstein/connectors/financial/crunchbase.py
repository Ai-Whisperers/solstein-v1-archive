"""Crunchbase connector for startup and funding data."""

import logging
from datetime import datetime, timezone
from typing import Any, Optional

import aiohttp

from ..base import BaseConnector, ConnectorResult, RawData, SourceConfig

logger = logging.getLogger(__name__)


class CrunchbaseConnector(BaseConnector):
    """Connector for Crunchbase API (requires API key)."""

    BASE_URL = "https://api.crunchbase.com/api/v4"

    def __init__(self, api_key: Optional[str] = None):
        config = SourceConfig(
            name="crunchbase",
            base_url=self.BASE_URL,
            api_key=api_key,
            rate_limit=100,  # per day for free tier
        )
        super().__init__(config)
        self._headers = {}
        if api_key:
            self._headers["X-cb-user-key"] = api_key

    async def connect(self) -> bool:
        if not self.config.api_key:
            logger.warning("Crunchbase API key not provided")
            return False

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.config.base_url}/entities/organizations/tesla", headers=self._headers
                ) as response:
                    return response.status in [200, 404]  # 404 means API works but entity not found
        except Exception as e:
            logger.error(f"Failed to connect to Crunchbase: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        if not self.config.api_key:
            return ConnectorResult(success=False, data=[], error_message="API key required")

        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "field_ids": "identifier,short_description,funding_total,raised_investor_count",
                    "limit": kwargs.get("limit", 10),
                }

                async with session.get(
                    f"{self.config.base_url}/searches/organizations", headers=self._headers, params=params
                ) as response:
                    data = await response.json()
                    entities = data.get("entities", [])

                    raw_data_list = []
                    for entity in entities:
                        props = entity.get("properties", {})
                        raw_data = RawData(
                            source_name=self.config.name,
                            source_url=f"https://crunchbase.com/organization/{props.get('identifier', {}).get('value', '')}",
                            raw_content=entity,
                            extracted_at=datetime.now(timezone.utc),
                            metadata={
                                "entity_id": entity.get("uuid"),
                                "entity_type": "organization",
                                "source_type": "startup_data",
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
        props = content.get("properties", {})

        return {
            "source": "crunchbase",
            "entity_type": "organization",
            "name": props.get("identifier", {}).get("value"),
            "description": props.get("short_description"),
            "funding_total": props.get("funding_total", {}).get("value"),
            "investor_count": props.get("raised_investor_count"),
            "url": raw_data.source_url,
            "raw_data": content,
        }
