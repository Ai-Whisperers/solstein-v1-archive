"""
Financial data connectors for SEC EDGAR, stock data, and financial APIs.

FREE sources:
- SEC EDGAR (free, rate limited)
- Yahoo Finance (via yfinance, free)
- Alpha Vantage (free tier)
- FRED (free API key)
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Optional

import aiohttp
import pandas as pd

from ..base import BaseConnector, ConnectorResult, RawData, SourceConfig

logger = logging.getLogger(__name__)


class SECEdgarConnector(BaseConnector):
    """Connector for SEC EDGAR filings."""

    BASE_URL = "https://www.sec.gov/Archives/edgar"

    def __init__(self, config: Optional[SourceConfig] = None):
        if config is None:
            config = SourceConfig(
                name="sec_edgar",
                base_url=self.BASE_URL,
                rate_limit=10,  # SEC requires max 10 requests/second
            )
        super().__init__(config)
        self._headers = {"User-Agent": "Solstein Research solstein@example.com"}

    async def connect(self) -> bool:
        """Test connection to SEC EDGAR."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.config.base_url}/daily-index/form-idx", headers=self._headers
                ) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Failed to connect to SEC EDGAR: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        """Search for company filings by CIK or ticker."""
        # Implementation would use edgartools or direct API
        # For now, return mock structure
        logger.info(f"Searching SEC EDGAR for: {query}")

        # TODO: Implement actual SEC search using edgartools
        return ConnectorResult(
            success=True,
            data=[],
            total_found=0,
        )

    async def get_by_id(self, entity_id: str) -> ConnectorResult:
        """Get filings by CIK."""
        logger.info(f"Getting SEC filings for CIK: {entity_id}")

        # TODO: Implement actual retrieval
        return ConnectorResult(
            success=True,
            data=[],
            total_found=0,
        )

    def normalize(self, raw_data: RawData) -> dict[str, Any]:
        """Normalize SEC filing to common format."""
        return {
            "source": "sec_edgar",
            "entity_type": "filing",
            "filing_type": raw_data.metadata.get("form_type"),
            "filing_date": raw_data.metadata.get("filing_date"),
            "company_name": raw_data.metadata.get("company_name"),
            "cik": raw_data.metadata.get("cik"),
            "raw_content": raw_data.raw_content,
        }


class YahooFinanceConnector(BaseConnector):
    """Connector for Yahoo Finance data (via yfinance)."""

    def __init__(self, config: Optional[SourceConfig] = None):
        if config is None:
            config = SourceConfig(
                name="yahoo_finance",
                base_url="https://finance.yahoo.com",
                rate_limit=2000,  # yfinance is generous
            )
        super().__init__(config)

    async def connect(self) -> bool:
        """Test connection to Yahoo Finance."""
        try:
            import yfinance as yf

            # Test with a well-known ticker
            ticker = yf.Ticker("AAPL")
            info = ticker.info
            return "symbol" in info
        except Exception as e:
            logger.error(f"Failed to connect to Yahoo Finance: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        """Search for stock by ticker or company name."""
        logger.info(f"Searching Yahoo Finance for: {query}")

        try:
            import yfinance as yf

            ticker = yf.Ticker(query)
            info = ticker.info

            if not info or "symbol" not in info:
                return ConnectorResult(
                    success=True,
                    data=[],
                    total_found=0,
                )

            raw_data = RawData(
                source_name=self.config.name,
                source_url=f"https://finance.yahoo.com/quote/{query}",
                raw_content=info,
                extracted_at=datetime.now(timezone.utc),
                metadata={
                    "ticker": query,
                    "source_type": "stock_info",
                },
            )

            return ConnectorResult(
                success=True,
                data=[raw_data],
                total_found=1,
            )

        except Exception as e:
            logger.error(f"Yahoo Finance search failed: {e}")
            return ConnectorResult(
                success=False,
                data=[],
                error_message=str(e),
            )

    async def get_by_id(self, entity_id: str) -> ConnectorResult:
        """Get stock data by ticker symbol."""
        return await self.search(entity_id)

    def normalize(self, raw_data: RawData) -> dict[str, Any]:
        """Normalize Yahoo Finance data to common format."""
        content = raw_data.raw_content

        return {
            "source": "yahoo_finance",
            "entity_type": "stock",
            "ticker": raw_data.metadata.get("ticker"),
            "company_name": content.get("longName") or content.get("shortName"),
            "market_cap": content.get("marketCap"),
            "revenue": content.get("totalRevenue"),
            "employee_count": content.get("fullTimeEmployees"),
            "sector": content.get("sector"),
            "industry": content.get("industry"),
            "website": content.get("website"),
            "country": content.get("country"),
            "raw_metrics": content,
        }


class AlphaVantageConnector(BaseConnector):
    """Connector for Alpha Vantage API (free tier available)."""

    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self, api_key: Optional[str] = None):
        config = SourceConfig(
            name="alpha_vantage",
            base_url=self.BASE_URL,
            api_key=api_key,
            rate_limit=5,  # Free tier: 5 calls/minute
        )
        super().__init__(config)

    async def connect(self) -> bool:
        """Test connection to Alpha Vantage."""
        if not self.config.api_key:
            logger.warning("Alpha Vantage API key not provided")
            return False

        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "function": "TIME_SERIES_INTRADAY",
                    "symbol": "IBM",
                    "interval": "5min",
                    "apikey": self.config.api_key,
                }
                async with session.get(self.config.base_url, params=params) as response:
                    data = await response.json()
                    return "Meta Data" in data or "Note" in data
        except Exception as e:
            logger.error(f"Failed to connect to Alpha Vantage: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        """Search for company overview by ticker."""
        if not self.config.api_key:
            return ConnectorResult(
                success=False,
                data=[],
                error_message="API key required",
            )

        logger.info(f"Searching Alpha Vantage for: {query}")

        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "function": "OVERVIEW",
                    "symbol": query,
                    "apikey": self.config.api_key,
                }
                async with session.get(self.config.base_url, params=params) as response:
                    data = await response.json()

                    if not data or "Symbol" not in data:
                        return ConnectorResult(
                            success=True,
                            data=[],
                            total_found=0,
                        )

                    raw_data = RawData(
                        source_name=self.config.name,
                        source_url=f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={query}",
                        raw_content=data,
                        extracted_at=datetime.now(timezone.utc),
                        metadata={
                            "ticker": query,
                            "source_type": "company_overview",
                        },
                    )

                    return ConnectorResult(
                        success=True,
                        data=[raw_data],
                        total_found=1,
                    )

        except Exception as e:
            logger.error(f"Alpha Vantage search failed: {e}")
            return ConnectorResult(
                success=False,
                data=[],
                error_message=str(e),
            )

    async def get_by_id(self, entity_id: str) -> ConnectorResult:
        """Get company data by ticker."""
        return await self.search(entity_id)

    def normalize(self, raw_data: RawData) -> dict[str, Any]:
        """Normalize Alpha Vantage data to common format."""
        content = raw_data.raw_content

        return {
            "source": "alpha_vantage",
            "entity_type": "company",
            "ticker": content.get("Symbol"),
            "company_name": content.get("Name"),
            "description": content.get("Description"),
            "sector": content.get("Sector"),
            "industry": content.get("Industry"),
            "market_cap": content.get("MarketCapitalization"),
            "revenue": content.get("RevenueTTM"),
            "employee_count": content.get("FullTimeEmployees"),
            "fiscal_year_end": content.get("FiscalYearEnd"),
            "raw_metrics": content,
        }


# Factory function for easy connector creation
async def create_financial_connector(source_type: str, **kwargs) -> BaseConnector:
    """Factory function to create financial connectors."""
    connectors = {
        "sec_edgar": SECEdgarConnector,
        "yahoo_finance": YahooFinanceConnector,
        "alpha_vantage": AlphaVantageConnector,
    }

    connector_class = connectors.get(source_type)
    if not connector_class:
        raise ValueError(f"Unknown financial connector: {source_type}")

    connector = connector_class(**kwargs)
    return connector



# Import additional connectors
from .crunchbase import CrunchbaseConnector

__all__ = [
    "SECEdgarConnector",
    "YahooFinanceConnector",
    "AlphaVantageConnector",
    "create_financial_connector",
    "CrunchbaseConnector",
]


from .angellist import AngelListConnector
from .f6s import F6SConnector

__all__.extend([
    "AngelListConnector",
    "F6SConnector",
])

from .opencorporates import OpenCorporatesConnector
from .betalist import BetaListConnector

__all__.extend([
    "OpenCorporatesConnector",
    "BetaListConnector",
])

from .sec_edgar import SECEdgarConnector

__all__.extend([
    "SECEdgarConnector",
])