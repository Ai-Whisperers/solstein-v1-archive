"""
Global Market Data Module for Solstein.

Comprehensive market data covering:
- Global stock exchanges (US, UK, Europe, Asia, Emerging)
- Major indices (S&P 500, FTSE, DAX, Nikkei, etc.)
- Currency conversion (live rates)
- Crypto currencies (BTC, ETH)
- Source currency preservation throughout the data chain
"""

from datetime import date, datetime
from enum import Enum

from loguru import logger
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
        code="ENX", name="Euronext", region=MarketRegion.EUROPE, currency=Currency.EUR
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


class MarketIndex(BaseModel):
    """Market index definition."""

    symbol: str
    name: str
    region: MarketRegion
    currency: Currency
    yahoo_symbol: str


MARKET_INDICES = {
    # US Indices
    "SPX": MarketIndex(
        symbol="SPX",
        name="S&P 500",
        region=MarketRegion.USA,
        currency=Currency.USD,
        yahoo_symbol="^GSPC",
    ),
    "DJI": MarketIndex(
        symbol="DJI",
        name="Dow Jones Industrial Average",
        region=MarketRegion.USA,
        currency=Currency.USD,
        yahoo_symbol="^DJI",
    ),
    "IXIC": MarketIndex(
        symbol="IXIC",
        name="NASDAQ Composite",
        region=MarketRegion.USA,
        currency=Currency.USD,
        yahoo_symbol="^IXIC",
    ),
    "RUT": MarketIndex(
        symbol="RUT",
        name="Russell 2000",
        region=MarketRegion.USA,
        currency=Currency.USD,
        yahoo_symbol="^RUT",
    ),
    # UK Indices
    "FTSE100": MarketIndex(
        symbol="FTSE100",
        name="FTSE 100",
        region=MarketRegion.UK,
        currency=Currency.GBP,
        yahoo_symbol="^FTSE",
    ),
    "FTSE250": MarketIndex(
        symbol="FTSE250",
        name="FTSE 250",
        region=MarketRegion.UK,
        currency=Currency.GBP,
        yahoo_symbol="^FTMC",
    ),
    "FTSE350": MarketIndex(
        symbol="FTSE350",
        name="FTSE 350",
        region=MarketRegion.UK,
        currency=Currency.GBP,
        yahoo_symbol="^FTSE",
    ),
    # European Indices
    "DAX": MarketIndex(
        symbol="DAX",
        name="DAX Performance Index",
        region=MarketRegion.EUROPE,
        currency=Currency.EUR,
        yahoo_symbol="^GDAXI",
    ),
    "CAC40": MarketIndex(
        symbol="CAC40",
        name="CAC 40",
        region=MarketRegion.EUROPE,
        currency=Currency.EUR,
        yahoo_symbol="^FCHI",
    ),
    "EUROSTOXX50": MarketIndex(
        symbol="EUROSTOXX50",
        name="Euro Stoxx 50",
        region=MarketRegion.EUROPE,
        currency=Currency.EUR,
        yahoo_symbol="^STOXX50E",
    ),
    "IBEX35": MarketIndex(
        symbol="IBEX35",
        name="IBEX 35",
        region=MarketRegion.EUROPE,
        currency=Currency.EUR,
        yahoo_symbol="^IBEX",
    ),
    "FTSE_MIB": MarketIndex(
        symbol="FTSE_MIB",
        name="FTSE MIB",
        region=MarketRegion.EUROPE,
        currency=Currency.EUR,
        yahoo_symbol="^FTSEMIB",
    ),
    # Asian Indices
    "N225": MarketIndex(
        symbol="N225",
        name="Nikkei 225",
        region=MarketRegion.ASIA,
        currency=Currency.JPY,
        yahoo_symbol="^N225",
    ),
    "HSI": MarketIndex(
        symbol="HSI",
        name="Hang Seng Index",
        region=MarketRegion.ASIA,
        currency=Currency.HKD,
        yahoo_symbol="^HSI",
    ),
    "SSE Composite": MarketIndex(
        symbol="SSEC",
        name="Shanghai Composite",
        region=MarketRegion.ASIA,
        currency=Currency.CNY,
        yahoo_symbol="000001.SS",
    ),
    "KOSPI": MarketIndex(
        symbol="KOSPI",
        name="KOSPI",
        region=MarketRegion.ASIA,
        currency=Currency.KRW,
        yahoo_symbol="^KS11",
    ),
    "SENSEX": MarketIndex(
        symbol="SENSEX",
        name="BSE Sensex",
        region=MarketRegion.ASIA,
        currency=Currency.INR,
        yahoo_symbol="^BSESN",
    ),
    "NIFTY50": MarketIndex(
        symbol="NIFTY50",
        name="Nifty 50",
        region=MarketRegion.ASIA,
        currency=Currency.INR,
        yahoo_symbol="^NSEI",
    ),
    # Emerging Indices
    "BOVESPA": MarketIndex(
        symbol="BOVESPA",
        name="Bovespa Index",
        region=MarketRegion.EMERGING,
        currency=Currency.BRL,
        yahoo_symbol="^BVSP",
    ),
    "MXX": MarketIndex(
        symbol="MXX",
        name="IPC Mexico",
        region=MarketRegion.EMERGING,
        currency=Currency.MXN,
        yahoo_symbol="^MXX",
    ),
    "MSCI_EM": MarketIndex(
        symbol="MSCI_EM",
        name="MSCI Emerging Markets",
        region=MarketRegion.EMERGING,
        currency=Currency.USD,
        yahoo_symbol="^EEM",
    ),
    # Crypto Indices
    "BTC": MarketIndex(
        symbol="BTC",
        name="Bitcoin USD",
        region=MarketRegion.CRYPTO,
        currency=Currency.BTC,
        yahoo_symbol="BTC-USD",
    ),
    "ETH": MarketIndex(
        symbol="ETH",
        name="Ethereum USD",
        region=MarketRegion.CRYPTO,
        currency=Currency.ETH,
        yahoo_symbol="ETH-USD",
    ),
}


class CurrencyRate(BaseModel):
    """Currency exchange rate."""

    from_currency: Currency
    to_currency: Currency
    rate: float
    timestamp: datetime

    def convert(self, amount: float) -> float:
        return amount * self.rate


class CurrencyConverter:
    """
    Currency converter with live rates.

    Handles conversion between all major currencies including crypto.
    Preserves source currency throughout the chain.
    """

    def __init__(self):
        self._rates: dict[str, float] = {}
        self._last_update: datetime | None = None

    def set_rates(self, rates: dict[tuple[Currency, Currency], float]) -> None:
        for (from_curr, to_curr), rate in rates.items():
            key = f"{from_curr.value}_{to_curr.value}"
            self._rates[key] = rate
        self._last_update = datetime.now()

    def convert(
        self,
        amount: float,
        from_currency: Currency,
        to_currency: Currency,
    ) -> float:
        if from_currency == to_currency:
            return amount

        if from_currency == Currency.BTC or to_currency == Currency.BTC:
            btc_key = f"BTC_{Currency.USD.value}"
            if btc_key not in self._rates:
                logger.warning("BTC rate not available")
                return amount

            btc_rate = self._rates[btc_key]

            if from_currency == Currency.BTC:
                usd_amount = amount * btc_rate
            else:
                usd_amount = amount

            if to_currency == Currency.BTC:
                return usd_amount / btc_rate
            elif to_currency == Currency.USD:
                return usd_amount
            else:
                usd_to_target = self._rates.get(f"USD_{to_currency.value}", 1.0)
                return usd_amount * usd_to_target

        key = f"{from_currency.value}_{to_currency.value}"
        rate = self._rates.get(key)

        if rate is None:
            usd_key = f"{from_currency.value}_USD"
            usd_to_key = f"USD_{to_currency.value}"

            from_usd = self._rates.get(usd_key, 1.0)
            to_usd = self._rates.get(usd_to_key, 1.0)

            if from_usd and to_usd:
                return amount * (to_usd / from_usd)

            logger.warning(f"Currency rate not found: {from_currency} -> {to_currency}")
            return amount

        return amount * rate

    def get_rate(self, from_currency: Currency, to_currency: Currency) -> float | None:
        if from_currency == to_currency:
            return 1.0

        key = f"{from_currency.value}_{to_currency.value}"
        return self._rates.get(key)

    @property
    def last_update(self) -> datetime | None:
        return self._last_update


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

    def convert_currency(
        self, converter: CurrencyConverter, target: Currency
    ) -> "GlobalStockData":
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


def get_exchange_for_ticker(ticker: str) -> StockExchange:
    """Determine stock exchange from ticker."""
    ticker_upper = ticker.upper()

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
