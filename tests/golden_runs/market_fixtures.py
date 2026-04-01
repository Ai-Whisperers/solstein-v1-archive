"""Benchmark company fixtures for full-market golden runs.

STORY-268 / EPIC-070: Defines a representative company set covering
different enrichment paths (ticker-based, patent-heavy, no-ticker).
All external dependencies are mocked; these fixtures produce
deterministic, reproducible outputs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from unittest.mock import MagicMock

from solstein.data.patent_client import PatentResult


@dataclass(frozen=True)
class BenchmarkCompany:
    """A single company in the golden-run benchmark set."""

    company_id: str
    company_name: str
    ticker: str | None = None
    website: str | None = None


# --- Benchmark set -----------------------------------------------------------
# Five companies chosen to exercise different enrichment paths:
#   1. Large-cap with ticker  → Yahoo Finance + GlobalMarket + Patents
#   2. Mid-cap with ticker    → Yahoo Finance + GlobalMarket + Patents
#   3. Private (no ticker)    → Patents only (Yahoo/GlobalMarket raise)
#   4. Patent-heavy           → Large patent portfolio, ticker available
#   5. Startup (no patents)   → Ticker available, zero patents

BENCHMARK_COMPANIES: list[BenchmarkCompany] = [
    BenchmarkCompany("bench-001", "TechGiant Inc.", ticker="TGNT", website="https://techgiant.example.com"),
    BenchmarkCompany("bench-002", "MidScale Corp.", ticker="MDSC"),
    BenchmarkCompany("bench-003", "PrivateSoft LLC"),
    BenchmarkCompany("bench-004", "PatentKing AG", ticker="PTKG"),
    BenchmarkCompany("bench-005", "FreshStart AI", ticker="FRAI"),
]


def make_mock_company_research(
    ticker: str,
    name: str = "Mock Company",
    exchange: str = "NMS",
    market_cap: int = 1_000_000_000,
) -> MagicMock:
    """Create a mock CompanyResearch-like object for Yahoo Finance adapter."""
    mock = MagicMock()
    mock.exchange = exchange
    mock.model_dump.return_value = {
        "ticker": ticker,
        "name": name,
        "exchange": exchange,
        "description": f"{name} is a technology company.",
        "market_cap": market_cap,
    }
    return mock


def make_mock_stock_data(
    ticker: str,
    price: float = 150.0,
    market_cap: float = 50_000_000_000.0,
) -> MagicMock:
    """Create a mock StockData-like object for GlobalMarket adapter."""
    mock = MagicMock()
    mock.ticker = ticker
    mock.exchange = "NMS"
    mock.source_currency.value = "USD"
    mock.current_price = price
    mock.price_date = "2026-03-31"
    mock.eps_ttm = 6.5
    mock.revenue = 100_000_000_000.0
    mock.market_cap = market_cap
    return mock


def make_patent_result(
    total: int = 42,
    source: str = "uspto_peds",
    ai_related: int = 5,
    recent_count: int = 3,
) -> PatentResult:
    """Create a PatentResult fixture."""
    return PatentResult(
        total_patents=total,
        recent_patents=[{"title": f"Patent {i}"} for i in range(recent_count)],
        ai_related_patents=ai_related,
        top_categories=["AI", "ML", "Cloud"],
        source=source,
    )


# Pre-built mock data keyed by company_id for deterministic pipeline runs.
COMPANY_MOCK_DATA: dict[str, dict[str, Any]] = {
    "bench-001": {
        "company_research": lambda: make_mock_company_research("TGNT", "TechGiant Inc.", "NMS", 3_000_000_000_000),
        "stock_data": lambda: make_mock_stock_data("TGNT", 450.0, 3_000_000_000_000.0),
        "patent_result": lambda: make_patent_result(total=120, ai_related=30, recent_count=10),
    },
    "bench-002": {
        "company_research": lambda: make_mock_company_research("MDSC", "MidScale Corp.", "NYQ", 50_000_000_000),
        "stock_data": lambda: make_mock_stock_data("MDSC", 85.0, 50_000_000_000.0),
        "patent_result": lambda: make_patent_result(total=25, ai_related=3, recent_count=2),
    },
    "bench-003": {
        # No ticker → Yahoo Finance and GlobalMarket will raise ValueError
        "patent_result": lambda: make_patent_result(total=8, source="google_patents", ai_related=1, recent_count=1),
    },
    "bench-004": {
        "company_research": lambda: make_mock_company_research("PTKG", "PatentKing AG", "FRA", 15_000_000_000),
        "stock_data": lambda: make_mock_stock_data("PTKG", 200.0, 15_000_000_000.0),
        "patent_result": lambda: make_patent_result(total=500, ai_related=150, recent_count=20),
    },
    "bench-005": {
        "company_research": lambda: make_mock_company_research("FRAI", "FreshStart AI", "NMS", 500_000_000),
        "stock_data": lambda: make_mock_stock_data("FRAI", 12.0, 500_000_000.0),
        "patent_result": lambda: make_patent_result(total=0, source="none", ai_related=0, recent_count=0),
    },
}
