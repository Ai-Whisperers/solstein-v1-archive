"""Yahoo Finance connector for stock data."""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from ..base import BaseConnector, ConnectorResult, RawData, SourceConfig

logger = logging.getLogger(__name__)


class YahooFinanceConnector(BaseConnector):
    """Connector for Yahoo Finance data."""

    def __init__(self, config: Optional[SourceConfig] = None):
        if config is None:
            config = SourceConfig(
                name="yahoo_finance",
                base_url="https://finance.yahoo.com",
                rate_limit=2000,
            )
        super().__init__(config)

    async def connect(self) -> bool:
        try:
            import yfinance as yf

            def _probe() -> dict:
                ticker = yf.Ticker("AAPL")
                return ticker.info

            info = await asyncio.to_thread(_probe)
            return "symbol" in info
        except Exception as e:
            logger.error(f"Failed to connect to Yahoo Finance: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        try:
            import yfinance as yf

            def _fetch(symbol: str) -> dict:
                ticker = yf.Ticker(symbol)
                return ticker.info

            info = await asyncio.to_thread(_fetch, query)

            if not info or "symbol" not in info:
                return ConnectorResult(success=True, data=[], total_found=0)

            raw_data = RawData(
                source_name=self.config.name,
                source_url=f"https://finance.yahoo.com/quote/{query}",
                raw_content=info,
                extracted_at=datetime.now(timezone.utc),
                metadata={"ticker": query, "source_type": "stock_info"},
            )

            return ConnectorResult(success=True, data=[raw_data], total_found=1)
        except Exception as e:
            return ConnectorResult(success=False, data=[], error_message=str(e))

    async def get_by_id(self, entity_id: str) -> ConnectorResult:
        return await self.search(entity_id)

    def normalize(self, raw_data: RawData) -> dict[str, Any]:
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
