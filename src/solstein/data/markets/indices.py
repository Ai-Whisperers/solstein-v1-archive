"""Market index definitions for Solstein."""

from __future__ import annotations

from .models import Currency, MarketIndex, MarketRegion

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
    "SSE_Composite": MarketIndex(
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
