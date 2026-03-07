"""Market models for Solstein."""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel


class Currency(str, Enum):
    """Supported currencies."""

    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CHF = "CHF"
    CAD = "CAD"
    AUD = "AUD"
    CNY = "CNY"
    HKD = "HKD"
    INR = "INR"
    BRL = "BRL"
    KRW = "KRW"
    MXN = "MXN"
    BTC = "BTC"
    ETH = "ETH"


class MarketRegion(str, Enum):
    """Market regions."""

    USA = "USA"
    UK = "UK"
    EUROPE = "EUROPE"
    ASIA = "ASIA"
    EMERGING = "EMERGING"
    CRYPTO = "CRYPTO"


class StockExchange(BaseModel):
    """Stock exchange definition."""

    code: str
    name: str
    region: MarketRegion
    currency: Currency
    suffix: str = ""

    @property
    def yahoo_code(self) -> str:
        return f"{self.code}{self.suffix}" if self.suffix else self.code


class MarketIndex(BaseModel):
    """Market index definition."""

    symbol: str
    name: str
    region: MarketRegion
    currency: Currency
    yahoo_symbol: str


class CurrencyRate(BaseModel):
    """Currency exchange rate."""

    from_currency: Currency
    to_currency: Currency
    rate: float
    timestamp: datetime

    def convert(self, amount: float) -> float:
        return amount * self.rate


class GlobalStockData(BaseModel):
    """Global stock data with currency tracking."""

    ticker: str
    exchange: str
    source_currency: Currency
    current_price: float
    price_date: date

    currency_adjusted_price: float | None = None
    target_currency: Currency | None = None

    eps_ttm: float | None = None
    revenue: float | None = None
    market_cap: float | None = None

    graham_intrinsic_value: float | None = None
    discount_to_intrinsic_pct: float | None = None
    valuation_classification: str | None = None

    def convert_currency(self, converter: "CurrencyConverter", target: Currency) -> "GlobalStockData":
        """Convert currency using provided converter."""
        if self.source_currency == target:
            return self

        converted = converter.convert(
            self.current_price,
            self.source_currency,
            target,
        )

        new_data = self.model_copy()
        new_data.currency_adjusted_price = converted
        new_data.target_currency = target

        if new_data.graham_intrinsic_value:
            new_data.graham_intrinsic_value = converter.convert(
                new_data.graham_intrinsic_value,
                self.source_currency,
                target,
            )

        if new_data.current_price and new_data.graham_intrinsic_value:
            ratio = new_data.current_price / new_data.graham_intrinsic_value
            new_data.discount_to_intrinsic_pct = (1 - ratio) * 100

        return new_data


class MarketDataPoint(BaseModel):
    """Single market data point."""

    symbol: str
    value: float
    currency: Currency
    timestamp: datetime
    source: str


class IndexData(BaseModel):
    """Index data with history."""

    index_symbol: str
    name: str
    current_value: float
    previous_close: float
    change_pct: float
    currency: Currency
    timestamp: datetime

    history: list[MarketDataPoint] = []
