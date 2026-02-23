"""
Global Market Data Fetchers.

Fetches real-time data from:
- Yahoo Finance via yfinance (free, global coverage)
- Handles all major exchanges and indices
- Currency conversion support
"""

from datetime import date, datetime
from typing import Any

import pandas as pd
import yfinance as yf
from loguru import logger

from .markets import (
    MARKET_INDICES,
    STOCK_EXCHANGES,
    Currency,
    CurrencyConverter,
    GlobalStockData,
    IndexData,
    StockExchange,
)


class YahooFinanceFetcher:
    """
    Fetch market data from Yahoo Finance using yfinance.

    Covers:
    - US stocks (NYSE, NASDAQ)
    - UK stocks (LSE with .L suffix)
    - European stocks
    - Asian stocks
    - Indices
    - Crypto
    """

    def __init__(self):
        pass

    def get_quote(self, ticker: str) -> dict[str, Any] | None:
        """Get real-time quote for a ticker."""
        try:
            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info

            if not info or info.get("regularMarketPrice") is None:
                return None

            return info

        except Exception as e:
            logger.error(f"Error fetching quote for {ticker}: {e}")
            return None

    def get_historical(
        self,
        ticker: str,
        start_date: date,
        end_date: date | None = None,
        interval: str = "1d",
    ) -> pd.DataFrame:
        """Get historical price data."""
        try:
            end = end_date or date.today()

            ticker_obj = yf.Ticker(ticker)
            df = ticker_obj.history(start=start_date, end=end, interval=interval)

            if df.empty:
                return pd.DataFrame()

            df = df.reset_index()
            df.columns = [c.lower().replace(" ", "_") for c in df.columns]

            return df

        except Exception as e:
            logger.error(f"Error fetching historical for {ticker}: {e}")
            return pd.DataFrame()

    def get_index_data(self, index_symbol: str) -> IndexData | None:
        """Get index data."""
        index = MARKET_INDICES.get(index_symbol)

        if not index:
            logger.warning(f"Index not found: {index_symbol}")
            return None

        try:
            ticker_obj = yf.Ticker(index.yahoo_symbol)
            info = ticker_obj.info

            current_value = info.get("regularMarketPrice")
            previous_close = info.get("regularMarketPreviousClose")

            if current_value is None:
                hist = ticker_obj.history(period="2d")
                if not hist.empty:
                    current_value = hist["Close"].iloc[-1]
                    if len(hist) > 1:
                        previous_close = hist["Close"].iloc[-2]

            if current_value is None:
                return None

            if previous_close is None:
                previous_close = current_value

            change_pct = ((current_value - previous_close) / previous_close * 100) if previous_close else 0

            return IndexData(
                index_symbol=index.symbol,
                name=index.name,
                current_value=current_value,
                previous_close=previous_close,
                change_pct=change_pct,
                currency=index.currency,
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Error fetching index {index_symbol}: {e}")
            return None


class CurrencyRateFetcher:
    """Fetch live currency exchange rates using Yahoo Finance."""

    def __init__(self):
        self.yf = YahooFinanceFetcher()
        self._cached_rates: dict[str, float] = {}
        self._last_fetch: datetime | None = None

    def fetch_all_rates(self, base_currency: Currency = Currency.USD) -> dict[tuple[Currency, Currency], float]:
        """Fetch all exchange rates relative to base currency."""
        rates = {}

        pairs = [
            (Currency.EUR, "EURUSD=X"),
            (Currency.GBP, "GBPUSD=X"),
            (Currency.JPY, "JPY=X"),
            (Currency.CHF, "CHFUSD=X"),
            (Currency.CAD, "CADUSD=X"),
            (Currency.AUD, "AUDUSD=X"),
            (Currency.CNY, "CNY=X"),
            (Currency.HKD, "HKD=X"),
            (Currency.INR, "INR=X"),
            (Currency.BRL, "BRL=X"),
            (Currency.BTC, "BTC-USD"),
            (Currency.ETH, "ETH-USD"),
        ]

        for currency, yahoo_pair in pairs:
            quote = self.yf.get_quote(yahoo_pair)

            if quote:
                rate = quote.get("regularMarketPrice")
                if rate:
                    rates[(currency, base_currency)] = rate

        self._cached_rates = {f"{k[0].value}_{k[1].value}": v for k, v in rates.items()}
        self._last_fetch = datetime.now()

        return rates

    def get_live_rate(self, from_currency: Currency, to_currency: Currency) -> float | None:
        """Get live rate between two currencies."""
        if from_currency == to_currency:
            return 1.0

        if not self._cached_rates or not self._last_fetch:
            self.fetch_all_rates()

        key = f"{from_currency.value}_{to_currency.value}"

        if key in self._cached_rates:
            return self._cached_rates[key]

        from_usd = self._cached_rates.get(f"{from_currency.value}_USD", 1.0)
        to_usd = self._cached_rates.get(f"{to_currency.value}_USD", 1.0)

        if from_usd and to_usd:
            return to_usd / from_usd

        return None

    def convert(self, amount: float, from_currency: Currency, to_currency: Currency) -> float:
        rate = self.get_live_rate(from_currency, to_currency)
        return amount * rate if rate else amount


class GlobalMarketLoader:
    """
    Unified loader for global market data.

    Combines:
    - Stock data
    - Index data
    - Currency conversion
    - Historical data
    """

    def __init__(self):
        self.yf = YahooFinanceFetcher()
        self.currency_fetcher = CurrencyRateFetcher()
        self.currency_converter = CurrencyConverter()

    def get_stock_data(
        self,
        ticker: str,
        target_currency: Currency = Currency.USD,
    ) -> GlobalStockData | None:
        """Get comprehensive stock data for a ticker."""
        quote = self.yf.get_quote(ticker)

        if not quote:
            return None

        exchange = self._detect_exchange(ticker, quote)
        source_currency = exchange.currency

        data = GlobalStockData(
            ticker=ticker,
            exchange=exchange.code,
            source_currency=source_currency,
            current_price=quote.get("regularMarketPrice") or 0,
            price_date=date.today(),
            eps_ttm=quote.get("trailingEps"),
            revenue=quote.get("revenue"),
            market_cap=quote.get("marketCap"),
        )

        if target_currency and target_currency != source_currency:
            data = data.convert_currency(self.currency_converter, target_currency)

        return data

    def get_index_data(self, index_symbol: str) -> IndexData | None:
        """Get index data."""
        return self.yf.get_index_data(index_symbol)

    def get_multiple_stocks(
        self,
        tickers: list[str],
        target_currency: Currency = Currency.USD,
    ) -> list[GlobalStockData]:
        """Get data for multiple tickers."""
        results = []

        for ticker in tickers:
            data = self.get_stock_data(ticker, target_currency)
            if data:
                results.append(data)

        return results

    def get_indices_by_region(self, region: str) -> list[IndexData]:
        """Get all indices for a region."""
        results = []

        for idx in MARKET_INDICES.values():
            if idx.region.value.upper() == region.upper():
                data = self.get_index_data(idx.symbol)
                if data:
                    results.append(data)

        return results

    def get_all_major_indices(self) -> list[IndexData]:
        """Get all major indices."""
        symbols = [
            "SPX",
            "DJI",
            "FTSE100",
            "DAX",
            "CAC40",
            "N225",
            "HSI",
            "BOVESPA",
            "BTC",
        ]
        results = []

        for symbol in symbols:
            data = self.get_index_data(symbol)
            if data:
                results.append(data)

        return results

    def _detect_exchange(self, ticker: str, quote: dict[str, Any]) -> StockExchange:
        exchange_name = (quote.get("exchangeName") or "").lower()

        if "london" in exchange_name:
            return STOCK_EXCHANGES["LSE"]
        elif "tokyo" in exchange_name:
            return STOCK_EXCHANGES["TSE"]
        elif "hong kong" in exchange_name:
            return STOCK_EXCHANGES["HKEX"]
        elif "frankfurt" in exchange_name or "xetra" in exchange_name:
            return STOCK_EXCHANGES["XETRA"]
        elif "paris" in exchange_name or "amsterdam" in exchange_name:
            return STOCK_EXCHANGES["EURONEXT"]

        return STOCK_EXCHANGES["NYSE"]


def get_market_summary() -> dict[str, Any]:
    """Get summary of all major markets."""
    loader = GlobalMarketLoader()
    indices = loader.get_all_major_indices()

    summary = {
        "timestamp": datetime.now().isoformat(),
        "markets": {},
    }

    for idx in indices:
        summary["markets"][idx.index_symbol] = {
            "name": idx.name,
            "value": idx.current_value,
            "change_pct": idx.change_pct,
            "currency": idx.currency.value,
        }

    return summary
