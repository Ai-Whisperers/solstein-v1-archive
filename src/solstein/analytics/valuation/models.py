"""
Valuation Analysis Module for Solstein PE Intelligence.

Provides Graham-based valuation analysis for Private Equity due diligence.
This is NOT a trading tool - it provides valuation context to help PE firms
understand intrinsic company worth relative to market price.

Use cases:
- Due diligence: Is the company undervalued vs intrinsic value?
- Market context: How does market price compare to fundamental value?
- Benchmarking: Compare valuation across portfolio companies
"""

from datetime import date
from typing import Any

import numpy as np
import pandas as pd
from loguru import logger
from pydantic import BaseModel


class ValuationContext(BaseModel):
    """Valuation analysis context for PE due diligence."""

    ticker: str
    current_price: float | None = None
    eps_ttm: float | None = None
    estimated_growth_rate: float | None = None
    bond_yield: float | None = None
    graham_intrinsic_value: float | None = None
    price_to_intrinsic_ratio: float | None = None
    discount_to_intrinsic_pct: float | None = None
    valuation_classification: str | None = None

    @property
    def is_undervalued(self) -> bool:
        if self.discount_to_intrinsic_pct is None:
            return False
        return self.discount_to_intrinsic_pct > 20

    @property
    def is_overvalued(self) -> bool:
        if self.discount_to_intrinsic_pct is None:
            return False
        return self.discount_to_intrinsic_pct < -20


class ValuationAnalyzer:
    """
    Analyze company valuation using Graham methodology for PE due diligence.

    Provides context for understanding intrinsic company value relative to
    market price - used for investment thesis validation, not trading.
    """

    BASE_MULTIPLIER = 8.5
    GROWTH_MULTIPLIER = 2.0
    BOND_YIELD_BASE = 4.4

    def calculate_intrinsic_value(
        self,
        eps_ttm: float,
        growth_rate: float,
        bond_yield: float,
    ) -> float:
        if eps_ttm <= 0:
            raise ValueError("EPS TTM must be positive for valuation")
        if bond_yield <= 0:
            raise ValueError("Bond yield must be positive")

        growth_percent = growth_rate * 100
        pe_ratio = self.BASE_MULTIPLIER + (self.GROWTH_MULTIPLIER * growth_percent)
        yield_adj = self.BOND_YIELD_BASE / bond_yield

        return eps_ttm * pe_ratio * yield_adj

    def analyze(
        self,
        ticker: str,
        eps_ttm: float | None,
        growth_rate: float | None,
        bond_yield: float | None,
        current_price: float | None,
    ) -> ValuationContext:
        context = ValuationContext(
            ticker=ticker,
            current_price=current_price,
            eps_ttm=eps_ttm,
            estimated_growth_rate=growth_rate,
            bond_yield=bond_yield,
        )

        if eps_ttm and growth_rate is not None and bond_yield:
            try:
                context.graham_intrinsic_value = self.calculate_intrinsic_value(
                    eps_ttm=eps_ttm,
                    growth_rate=growth_rate,
                    bond_yield=bond_yield,
                )
            except ValueError as e:
                logger.warning(f"Could not calculate intrinsic value for {ticker}: {e}")

        if context.graham_intrinsic_value and current_price:
            ratio = current_price / context.graham_intrinsic_value
            context.price_to_intrinsic_ratio = ratio
            context.discount_to_intrinsic_pct = (1 - ratio) * 100
            context.valuation_classification = self._classify_valuation(context.discount_to_intrinsic_pct)

        return context

    def _classify_valuation(self, discount_pct: float) -> str:
        if discount_pct > 50:
            return "Significant Discount"
        elif discount_pct > 20:
            return "Moderate Discount"
        elif discount_pct > -20:
            return "Fair Value"
        elif discount_pct > -50:
            return "Moderate Premium"
        else:
            return "Significant Premium"


class GrowthAnalyzer:
    """Analyze historical EPS to estimate growth rates for valuation."""

    def __init__(self, min_quarters: int = 6):
        self.min_quarters = min_quarters

    def estimate_growth_rate(self, eps_series: pd.Series) -> float | None:
        eps = eps_series.dropna()
        eps = eps[eps > 0]

        if len(eps) < self.min_quarters:
            return None

        eps_recent = eps.tail(30)
        if len(eps_recent) < self.min_quarters:
            return None

        y = np.log(eps_recent.values)
        x = np.arange(len(eps_recent))

        try:
            slope, _ = np.polyfit(x, y, 1)
        except np.linalg.LinAlgError:
            return None

        quarterly_growth = np.exp(slope) - 1
        return (1 + quarterly_growth) ** 4 - 1


class TTMEPSAnalyzer:
    """Calculate TTM EPS from quarterly data."""

    def calculate(self, eps_series: pd.Series) -> float | None:
        eps = eps_series.dropna()
        if len(eps) < 4:
            return None
        return float(eps.tail(4).sum())


class ValuationBenchmark:
    """
    Compare companies using Graham valuation for PE portfolio analysis.

    Enables PE firms to compare valuation across portfolio companies
    and identify undervalued vs overvalued positions.
    """

    def __init__(self):
        self.analyzer = ValuationAnalyzer()

    def benchmark_companies(
        self,
        company_data: list[dict[str, Any]],
    ) -> list[ValuationContext]:
        results = []
        for company in company_data:
            context = self.analyzer.analyze(
                ticker=company.get("ticker", "UNKNOWN"),
                eps_ttm=company.get("eps_ttm"),
                growth_rate=company.get("growth_rate"),
                bond_yield=company.get("bond_yield"),
                current_price=company.get("current_price"),
            )
            results.append(context)

        return sorted(results, key=lambda x: x.discount_to_intrinsic_pct or 0, reverse=True)

    def get_undervalued(self, valuations: list[ValuationContext]) -> list[ValuationContext]:
        return [v for v in valuations if v.is_undervalued]

    def get_overvalued(self, valuations: list[ValuationContext]) -> list[ValuationContext]:
        return [v for v in valuations if v.is_overvalued]


class SP500Membership(BaseModel):
    """S&P 500 membership tracking for market context."""

    ticker: str
    date_added: date | None = None
    date_removed: date | None = None

    def is_member(self, as_of: date) -> bool:
        if self.date_added is None:
            return False
        if as_of < self.date_added:
            return False
        if self.date_removed is not None and as_of >= self.date_removed:
            return False
        return True


def create_pe_valuation_insight(
    ticker: str,
    market_cap: float | None,
    current_price: float | None,
    eps_ttm: float | None,
    growth_rate: float | None,
    bond_yield: float | None,
) -> dict[str, Any]:
    """Create PE-focused valuation insight for due diligence reports."""
    analyzer = ValuationAnalyzer()

    context = analyzer.analyze(
        ticker=ticker,
        eps_ttm=eps_ttm,
        growth_rate=growth_rate,
        bond_yield=bond_yield,
        current_price=current_price,
    )

    return {
        "ticker": ticker,
        "market_cap_eur": market_cap,
        "valuation": {
            "graham_intrinsic_value": context.graham_intrinsic_value,
            "current_price": context.current_price,
            "discount_to_intrinsic_pct": context.discount_to_intrinsic_pct,
            "classification": context.valuation_classification,
        },
        "fundamentals": {
            "eps_ttm": eps_ttm,
            "estimated_growth_rate": growth_rate,
            "bond_yield": bond_yield,
        },
        "pe_insight": _generate_pe_insight(context),
    }


def _generate_pe_insight(context: ValuationContext) -> str:
    if context.valuation_classification is None:
        return "Insufficient data for valuation analysis"

    if context.is_undervalued:
        return (
            f"{context.ticker} trades at {abs(context.discount_to_intrinsic_pct):.1f}% "
            f"discount to Graham intrinsic value. May represent opportunity "
            f"for value creation if market recognizes fundamental worth."
        )
    elif context.is_overvalued:
        return (
            f"{context.ticker} trades at {abs(context.discount_to_intrinsic_pct):.1f}% "
            f"premium to Graham intrinsic value. Market may be overvaluing "
            f"growth expectations - careful due diligence recommended."
        )
    else:
        return (
            f"{context.ticker} trades near fair value relative to Graham "
            f"intrinsic value. Standard market pricing - look for other "
            f"differentiators in investment thesis."
        )
