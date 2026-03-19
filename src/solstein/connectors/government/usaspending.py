"""USAspending connector for government contract data."""

import logging
from datetime import datetime, timezone
from typing import Any

import aiohttp

from ..base import BaseConnector, ConnectorResult, RawData, SourceConfig

logger = logging.getLogger(__name__)


class USAspendingConnector(BaseConnector):
    """Connector for USAspending.gov (government contracts)."""

    BASE_URL = "https://api.usaspending.gov/api/v2"

    def __init__(self):
        config = SourceConfig(
            name="usaspending",
            base_url=self.BASE_URL,
            rate_limit=1000,
        )
        super().__init__(config)

    async def connect(self) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.config.base_url}/references/agency") as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Failed to connect to USAspending: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        try:
            async with aiohttp.ClientSession() as session:
                json_data = {"filters": {"recipient_name": query}, "limit": kwargs.get("limit", 10)}

                async with session.post(f"{self.config.base_url}/search/spending_by_award", json=json_data) as response:
                    data = await response.json()
                    results = data.get("results", [])

                    raw_data_list = []
                    for award in results:
                        raw_data = RawData(
                            source_name=self.config.name,
                            source_url=f"https://usaspending.gov/award/{award.get('generated_internal_id')}",
                            raw_content=award,
                            extracted_at=datetime.now(timezone.utc),
                            metadata={
                                "award_id": award.get("generated_internal_id"),
                                "recipient": award.get("recipient_name"),
                                "source_type": "government_contract",
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
            "source": "usaspending",
            "entity_type": "government_contract",
            "award_id": content.get("generated_internal_id"),
            "recipient": content.get("recipient_name"),
            "amount": content.get("award_amount"),
            "date": content.get("action_date"),
            "agency": content.get("funding_agency_name"),
            "description": content.get("award_description"),
            "contract_type": content.get("award_type"),
            "raw_data": content,
        }
