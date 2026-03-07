"""Market utilities for Solstein."""

from __future__ import annotations

from .models import Currency, MarketIndex, MarketRegion, StockExchange
from .exchanges import STOCK_EXCHANGES
from .indices import MARKET_INDICES


def get_exchange_for_ticker(ticker: str) -> StockExchange:
    """Determine stock exchange from ticker."""
    if "." in ticker:
        suffix = ticker.split(".")[-1].upper()
        for exchange in STOCK_EXCHANGES.values():
            if suffix == exchange.suffix.replace(".", ""):
                return exchange

    if ticker.isalpha() and len(ticker) <= 4:
        if ticker.isupper():
            return STOCK_EXCHANGES["NYSE"]

    return STOCK_EXCHANGES["NYSE"]


def get_index_for_region(region: MarketRegion) -> list[MarketIndex]:
    """Get all indices for a region."""
    return [idx for idx in MARKET_INDICES.values() if idx.region == region]


def format_price(price: float, currency: Currency, decimals: int = 2) -> str:
    """Format price with currency symbol."""
    symbols = {
        Currency.USD: "$",
        Currency.EUR: "€",
        Currency.GBP: "£",
        Currency.JPY: "¥",
        Currency.CHF: "CHF ",
        Currency.CAD: "C$",
        Currency.AUD: "A$",
        Currency.CNY: "¥",
        Currency.HKD: "HK$",
        Currency.INR: "₹",
        Currency.BRL: "R$",
        Currency.BTC: "₿",
        Currency.ETH: "Ξ",
    }

    symbol = symbols.get(currency, "")

    if currency in [Currency.JPY, Currency.CNY, Currency.INR]:
        return f"{symbol}{price:,.0f}"

    return f"{symbol}{price:,.{decimals}f}"
