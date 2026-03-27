"""Markets data package for Solstein.

EPIC-021: Modularized from monolithic 510-line markets.py file.
"""

from __future__ import annotations

# Classes
from .currency import CurrencyConverter

# Data
from .exchanges import STOCK_EXCHANGES
from .indices import MARKET_INDICES

# Enums
# Models
from .models import (
    Currency,
    CurrencyRate,
    GlobalStockData,
    IndexData,
    MarketDataPoint,
    MarketIndex,
    MarketRegion,
    StockExchange,
)

# Functions
from .utils import format_price, get_exchange_for_ticker, get_index_for_region

__all__ = [
    "Currency",
    "CurrencyConverter",
    "CurrencyRate",
    "GlobalStockData",
    "IndexData",
    "MARKET_INDICES",
    "MarketDataPoint",
    "MarketIndex",
    "MarketRegion",
    "STOCK_EXCHANGES",
    "StockExchange",
    "format_price",
    "get_exchange_for_ticker",
    "get_index_for_region",
]
