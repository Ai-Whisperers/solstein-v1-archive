"""OpenCorporates connector for company registries."""

import logging
from datetime import datetime, timezone
from typing import Any

import aiohttp

from ..base import BaseConnector, ConnectorResult, RawData, SourceConfig

logger = logging.getLogger(__name__)


class OpenCorporatesConnector(BaseConnector):
    """Connector for OpenCorporates (free tier available)."""

    BASE_URL = "https://api.opencorporates.com/v0.4"

    def __init__(self, api_token: str | None = None):
        config = SourceConfig(
            name="opencorporates",
            base_url=self.BASE_URL,
            api_key=api_token,
            rate_limit=200 if api_token else 50,  # per day
        )
        super().__init__(config)

    async def connect(self) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                params = {"q": "test"}
                if self.config.api_key:
                    params["api_token"] = self.config.api_key

                async with session.get(f"{self.config.base_url}/companies/search", params=params) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Failed to connect to OpenCorporates: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "q": query,
                    "per_page": kwargs.get("limit", 10),
                }
                if self.config.api_key:
                    params["api_token"] = self.config.api_key

                async with session.get(f"{self.config.base_url}/companies/search", params=params) as response:
                    data = await response.json()
                    companies = data.get("results", {}).get("companies", [])

                    raw_data_list = []
                    for company in companies:
                        company_data = company.get("company", {})
                        raw_data = RawData(
                            source_name=self.config.name,
                            source_url=company_data.get("opencorporates_url"),
                            raw_content=company_data,
                            extracted_at=datetime.now(timezone.utc),
                            metadata={
                                "company_number": company_data.get("company_number"),
                                "jurisdiction": company_data.get("jurisdiction_code"),
                                "source_type": "company_registry",
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
        try:
            async with aiohttp.ClientSession() as session:
                params = {}
                if self.config.api_key:
                    params["api_token"] = self.config.api_key

                async with session.get(f"{self.config.base_url}/companies/{entity_id}", params=params) as response:
                    if response.status == 404:
                        return ConnectorResult(success=True, data=[], total_found=0)

                    data = await response.json()
                    company = data.get("results", {}).get("company", {})

                    raw_data = RawData(
                        source_name=self.config.name,
                        source_url=company.get("opencorporates_url"),
                        raw_content=company,
                        extracted_at=datetime.now(timezone.utc),
                        metadata={
                            "company_number": company.get("company_number"),
                            "jurisdiction": company.get("jurisdiction_code"),
                            "source_type": "company_registry",
                        },
                    )

                    return ConnectorResult(success=True, data=[raw_data], total_found=1)
        except Exception as e:
            return ConnectorResult(success=False, data=[], error_message=str(e))

    def normalize(self, raw_data: RawData) -> dict[str, Any]:
        content = raw_data.raw_content

        return {
            "source": "opencorporates",
            "entity_type": "company_registry",
            "name": content.get("name"),
            "company_number": content.get("company_number"),
            "jurisdiction": content.get("jurisdiction_code"),
            "incorporation_date": content.get("incorporation_date"),
            "dissolution_date": content.get("dissolution_date"),
            "company_type": content.get("company_type"),
            "registry_url": content.get("registry_url"),
            "registered_address": content.get("registered_address_in_full"),
            "raw_data": content,
        }
