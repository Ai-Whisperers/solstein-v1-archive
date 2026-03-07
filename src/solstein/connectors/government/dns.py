"""DNS connector for domain records."""

import logging
from datetime import datetime
from typing import Any

from ..base import BaseConnector, ConnectorResult, RawData, SourceConfig

logger = logging.getLogger(__name__)


class DNSConnector(BaseConnector):
    """Connector for DNS records."""

    def __init__(self):
        config = SourceConfig(
            name="dns",
            base_url="https://dns.google/resolve",
            rate_limit=100,
        )
        super().__init__(config)

    async def connect(self) -> bool:
        """Test connection."""
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.config.base_url}?name=google.com&type=A") as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Failed to connect to DNS: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        """Query DNS records."""
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                record_type = kwargs.get("type", "A")
                async with session.get(self.config.base_url, params={"name": query, "type": record_type}) as response:
                    data = await response.json()

                    if data.get("Status") != 0:
                        return ConnectorResult(success=True, data=[], total_found=0)

                    answers = data.get("Answer", [])

                    raw_data_list = []
                    for answer in answers:
                        raw_data = RawData(
                            source_name=self.config.name,
                            source_url=f"dns://{query}",
                            raw_content=answer,
                            extracted_at=datetime.utcnow(),
                            metadata={
                                "domain": query,
                                "record_type": answer.get("type"),
                                "source_type": "dns_record",
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
        return ConnectorResult(success=False, data=[], error_message="Use search with domain")

    def normalize(self, raw_data: RawData) -> dict[str, Any]:
        content = raw_data.raw_content

        return {
            "source": "dns",
            "entity_type": "dns_record",
            "domain": raw_data.metadata.get("domain"),
            "record_type": content.get("type"),
            "ttl": content.get("TTL"),
            "value": content.get("data"),
            "raw_data": content,
        }
