"""Stock exchange definitions for Solstein."""

from __future__ import annotations

from .models import Currency, MarketRegion, StockExchange

STOCK_EXCHANGES = {
    "NYSE": StockExchange(
        code="NYSE",
        name="New York Stock Exchange",
        region=MarketRegion.USA,
        currency=Currency.USD,
    ),
    "NASDAQ": StockExchange(
        code="NASDAQ",
        name="NASDAQ Stock Exchange",
        region=MarketRegion.USA,
        currency=Currency.USD,
    ),
    "LSE": StockExchange(
        code="LSE",
        name="London Stock Exchange",
        region=MarketRegion.UK,
        currency=Currency.GBP,
        suffix=".L",
    ),
    "EURONEXT": StockExchange(
        code="ENX",
        name="Euronext",
        region=MarketRegion.EUROPE,
        currency=Currency.EUR,
    ),
    "XETRA": StockExchange(
        code="XETRA",
        name="Xetra (Germany)",
        region=MarketRegion.EUROPE,
        currency=Currency.EUR,
    ),
    "TSE": StockExchange(
        code="TSE",
        name="Tokyo Stock Exchange",
        region=MarketRegion.ASIA,
        currency=Currency.JPY,
    ),
    "HKEX": StockExchange(
        code="HKEX",
        name="Hong Kong Stock Exchange",
        region=MarketRegion.ASIA,
        currency=Currency.HKD,
    ),
    "SSE": StockExchange(
        code="SSE",
        name="Shanghai Stock Exchange",
        region=MarketRegion.ASIA,
        currency=Currency.CNY,
    ),
    "BSE": StockExchange(
        code="BSE",
        name="Bombay Stock Exchange",
        region=MarketRegion.EMERGING,
        currency=Currency.INR,
    ),
    "BOVESPA": StockExchange(
        code="BOVESPA",
        name="B3 (Brazil)",
        region=MarketRegion.EMERGING,
        currency=Currency.BRL,
    ),
}
