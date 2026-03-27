"""SEC EDGAR connector for company filings."""

import logging
from typing import Any

import aiohttp

from ..base import BaseConnector, ConnectorResult, RawData, SourceConfig

logger = logging.getLogger(__name__)


class SECEdgarConnector(BaseConnector):
    """Connector for SEC EDGAR filings (FREE, requires email in User-Agent)."""

    BASE_URL = "https://www.sec.gov"

    def __init__(self, email: str = "solstein@example.com"):
        config = SourceConfig(
            name="sec_edgar",
            base_url=self.BASE_URL,
            rate_limit=10,  # Max 10 requests/second per SEC guidelines
        )
        super().__init__(config)
        self._headers = {"User-Agent": f"Solstein Research {email}"}

    async def connect(self) -> bool:
        """Test connection to SEC EDGAR."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.config.base_url}/Archives/edgar/daily-index/form-idx", headers=self._headers
                ) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Failed to connect to SEC EDGAR: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        """Search for company by ticker or CIK."""
        # EDGAR doesn't have a direct search API
        # Would need to use company tickers JSON
        logger.info(f"SEC EDGAR search not implemented yet: {query}")
        return ConnectorResult(success=True, data=[], total_found=0)

    async def get_by_id(self, entity_id: str) -> ConnectorResult:
        """Get company filings by CIK."""
        logger.info(f"Getting SEC filings for CIK: {entity_id}")
        # TODO: Implement using edgartools library
        return ConnectorResult(success=True, data=[], total_found=0)

    def normalize(self, raw_data: RawData) -> dict[str, Any]:
        """Normalize SEC filing."""
        return {
            "source": "sec_edgar",
            "entity_type": "sec_filing",
            "cik": raw_data.metadata.get("cik"),
            "form_type": raw_data.metadata.get("form_type"),
            "filing_date": raw_data.metadata.get("filing_date"),
            "raw_content": raw_data.raw_content,
        }
