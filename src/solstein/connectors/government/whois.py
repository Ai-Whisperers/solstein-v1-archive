"""WHOIS connector for domain data."""

import logging
from typing import Any

from ..base import BaseConnector, ConnectorResult, RawData, SourceConfig

logger = logging.getLogger(__name__)


class WHOISConnector(BaseConnector):
    """Connector for WHOIS domain data."""

    def __init__(self):
        config = SourceConfig(
            name="whois",
            base_url="https://whois.domaintools.com",
            rate_limit=50,
        )
        super().__init__(config)

    async def connect(self) -> bool:
        """Test connection."""
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.get("https://whois.domaintools.com/google.com") as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Failed to connect to WHOIS: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        """Search domain (requires scraping or third-party API)."""
        logger.info(f"WHOIS search requires additional implementation: {query}")
        return ConnectorResult(success=True, data=[], total_found=0)

    async def get_by_id(self, entity_id: str) -> ConnectorResult:
        """Get WHOIS data for domain."""
        return ConnectorResult(success=False, data=[], error_message="Not implemented")

    def normalize(self, raw_data: RawData) -> dict[str, Any]:
        content = raw_data.raw_content

        return {
            "source": "whois",
            "entity_type": "domain",
            "domain": content.get("domain"),
            "registrar": content.get("registrar"),
            "creation_date": content.get("creation_date"),
            "expiration_date": content.get("expiration_date"),
            "name_servers": content.get("name_servers", []),
            "status": content.get("status", []),
            "raw_data": content,
        }
