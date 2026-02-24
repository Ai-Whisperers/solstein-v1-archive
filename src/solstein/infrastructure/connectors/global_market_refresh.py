"""Global Market refresh connector for international market data updates.

Uses GlobalMarketLoader with currency normalization to USD.
Implements incremental refresh for global stock data.
"""

from datetime import datetime
from typing import Any

from loguru import logger

from solstein.data.fetchers import GlobalMarketLoader
from solstein.infrastructure.conflict_resolution import SourceAuthority
from solstein.infrastructure.refresh import BaseRefreshConnector


class GlobalMarketRefreshConnector(BaseRefreshConnector):
    """Global Market refresh connector for international stock data.

    Fetches market data with currency normalization:
    - Current stock price
    - Market capitalization (USD normalized)
    - EPS (TTM)
    - Revenue (USD normalized)
    - Exchange and currency info

    Confidence: 0.87 (high for normalized market data)
    """

    def __init__(self, db_manager):
        super().__init__(
            source_name="global_market",
            source_type="global_market_data",
            db_manager=db_manager,
            confidence=0.87,
        )
        self.loader = GlobalMarketLoader()

    async def fetch_facts(
        self,
        company_ids: list[str],
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch global market data facts for companies.

        Args:
            company_ids: List of company tickers (supports international exchanges)
            start_date: Not used (always returns current data)
            end_date: Not used

        Returns:
            List of fact dictionaries with global market data
        """
        logger.info(f"Fetching global market data for {len(company_ids)} companies")
        facts = []

        for ticker in company_ids:
            try:
                stock_data = self.loader.get_stock_data(ticker)

                if stock_data is None:
                    logger.warning(f"No market data available for ticker {ticker}")
                    continue

                facts.append(
                    {
                        "company_id": ticker,
                        "fact_type": "global_stock_data",
                        "value": {
                            "current_price": stock_data.current_price,
                            "market_cap": stock_data.market_cap,
                            "eps_ttm": stock_data.eps_ttm,
                            "revenue": stock_data.revenue,
                        },
                        "confidence": self.confidence,
                        "extracted_at": datetime.now(),
                        "source": self.source_name,
                        "metadata": {
                            "ticker": stock_data.ticker,
                            "exchange": stock_data.exchange,
                            "source_currency": stock_data.source_currency.value,
                            "price_date": str(stock_data.price_date),
                        },
                    }
                )

                # Add currency info fact
                facts.append(
                    {
                        "company_id": ticker,
                        "fact_type": "currency_info",
                        "value": {
                            "source_currency": stock_data.source_currency.value,
                            "normalized_to_usd": True,
                        },
                        "confidence": self.confidence,
                        "extracted_at": datetime.now(),
                        "source": self.source_name,
                        "metadata": {
                            "ticker": ticker,
                            "exchange": stock_data.exchange,
                        },
                    }
                )

            except Exception as e:
                logger.warning(f"Failed to fetch global market data for {ticker}: {e}")
                continue

        return facts

    def get_authority(self) -> SourceAuthority:
        """Return Global Market authority level."""
        return SourceAuthority.GLOBAL_MARKET

    def supports_incremental(self) -> bool:
        """Global Market supports incremental refresh via hash comparison."""
        return True
