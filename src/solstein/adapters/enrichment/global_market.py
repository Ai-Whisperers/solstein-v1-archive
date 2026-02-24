"""Enrichment adapter wrapping fetchers.GlobalMarketLoader.

Provides market data (price, market cap, EPS) with automatic
currency normalization to USD via the CurrencyConverter.
Requires a ticker.
"""

from __future__ import annotations

from datetime import timezone, datetime

from solstein.domain.models import DataSourceType, RawDataSource


class GlobalMarketEnrichment:
    """Wraps ``GlobalMarketLoader.get_stock_data()`` as an EnrichmentSource."""

    @property
    def source_name(self) -> str:
        return "global_market"

    @property
    def source_type(self) -> DataSourceType:
        return DataSourceType.YAHOO_FINANCE

    def enrich(
        self,
        company_id: str,
        company_name: str,
        ticker: str | None = None,
        website: str | None = None,
    ) -> RawDataSource:
        if not ticker:
            raise ValueError(f"GlobalMarketEnrichment requires a ticker for {company_name}")

        from solstein.data.fetchers import GlobalMarketLoader

        loader = GlobalMarketLoader()
        stock_data = loader.get_stock_data(ticker)

        if stock_data is None:
            raise ValueError(f"No market data available for ticker {ticker}")

        content = {
            "ticker": stock_data.ticker,
            "exchange": stock_data.exchange,
            "source_currency": stock_data.source_currency.value,
            "current_price": stock_data.current_price,
            "price_date": str(stock_data.price_date),
            "eps_ttm": stock_data.eps_ttm,
            "revenue": stock_data.revenue,
            "market_cap": stock_data.market_cap,
        }

        return RawDataSource(
            source_type=DataSourceType.YAHOO_FINANCE,
            source_name="GlobalMarketLoader",
            raw_content=content,
            url=f"https://finance.yahoo.com/quote/{ticker}/",
            retrieval_timestamp=datetime.now(timezone.utc),
            confidence=0.8,
            relevance_score=0.9,
            metadata={
                "ticker": ticker,
                "exchange": stock_data.exchange,
                "currency": stock_data.source_currency.value,
            },
            extraction_method="yfinance_global_market",
        )
