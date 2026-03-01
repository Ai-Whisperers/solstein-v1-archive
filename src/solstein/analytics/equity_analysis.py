"""Equity analysis module for PE/VC valuation (EPIC-041).

Computes key equity metrics — EV/Revenue, EV/EBITDA, implied IRR,
and deal attractiveness — from company financials and a user-supplied
deal hypothesis.

Usage::

    from solstein.analytics.equity_analysis import EquityAnalyzer, DealParams

    params = DealParams(
        entry_ev_eur_m=250.0,
        equity_stake_pct=30.0,
        hold_period_years=5,
        exit_ev_revenue_multiple=8.0,
    )
    result = EquityAnalyzer().analyze(company, params)
    print(result.implied_irr_pct, result.deal_verdict)
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from solstein.domain.models import Company


@dataclass
class DealParams:
    """Input parameters for an equity deal scenario.

    Attributes:
        entry_ev_eur_m: Entry enterprise value in EUR millions.
        equity_stake_pct: Equity stake being acquired (0–100).
        hold_period_years: Expected holding period in years.
        exit_ev_revenue_multiple: Assumed EV/Revenue multiple at exit.
        debt_eur_m: Net debt at entry (EUR millions, default 0).
    """

    entry_ev_eur_m: float
    equity_stake_pct: float
    hold_period_years: int = 5
    exit_ev_revenue_multiple: float = 6.0
    debt_eur_m: float = 0.0


@dataclass
class EquityResult:
    """Result from equity analysis.

    Attributes:
        entry_ev_revenue_multiple: EV / Revenue at entry.
        entry_ev_ebitda_multiple: EV / EBITDA at entry (NaN if EBITDA unavailable).
        exit_ev_eur_m: Projected exit EV in EUR millions.
        exit_equity_value_eur_m: Projected equity value at exit in EUR millions.
        invested_equity_eur_m: Capital deployed for the stake.
        moic: Money-on-invested-capital (gross, before fees/carry).
        implied_irr_pct: Implied annualised IRR (%).
        deal_verdict: Qualitative assessment (``'Attractive'``, ``'Moderate'``, ``'Cautious'``).
    """

    entry_ev_revenue_multiple: float
    entry_ev_ebitda_multiple: float
    exit_ev_eur_m: float
    exit_equity_value_eur_m: float
    invested_equity_eur_m: float
    moic: float
    implied_irr_pct: float
    deal_verdict: str


class EquityAnalyzer:
    """PE/VC equity deal analyser."""

    def analyze(self, company: Company, params: DealParams) -> EquityResult:
        """Compute equity metrics for a deal scenario.

        Args:
            company: Company with financial data.
            params: Deal hypothesis parameters.

        Returns:
            EquityResult with MOIC, IRR, and qualitative verdict.
        """
        fin = getattr(company, "financials", None)
        revenue_eur_m: float = getattr(fin, "revenue", 0.0) or 0.0
        ebitda_margin: float = getattr(company, "ebitda_margin", 0.0) or 0.0
        growth_rate: float = getattr(fin, "growth_rate", 0.0) or 0.0

        # Projected exit revenue (apply CAGR from growth_rate)
        exit_revenue_eur_m = revenue_eur_m * ((1 + growth_rate / 100) ** params.hold_period_years)
        exit_ev_eur_m = exit_revenue_eur_m * params.exit_ev_revenue_multiple
        exit_equity_value_eur_m = exit_ev_eur_m - params.debt_eur_m

        invested_equity = params.entry_ev_eur_m * (params.equity_stake_pct / 100)
        exit_stake_value = exit_equity_value_eur_m * (params.equity_stake_pct / 100)

        moic = round(exit_stake_value / invested_equity, 2) if invested_equity > 0 else 0.0
        irr = self._irr(invested_equity, exit_stake_value, params.hold_period_years)

        entry_ev_rev = round(params.entry_ev_eur_m / revenue_eur_m, 2) if revenue_eur_m > 0 else float("nan")
        ebitda_eur_m = revenue_eur_m * ebitda_margin / 100.0
        entry_ev_ebitda = round(params.entry_ev_eur_m / ebitda_eur_m, 2) if ebitda_eur_m > 0 else float("nan")

        verdict = self._verdict(irr, moic, entry_ev_rev)

        return EquityResult(
            entry_ev_revenue_multiple=entry_ev_rev,
            entry_ev_ebitda_multiple=entry_ev_ebitda,
            exit_ev_eur_m=round(exit_ev_eur_m, 2),
            exit_equity_value_eur_m=round(exit_equity_value_eur_m, 2),
            invested_equity_eur_m=round(invested_equity, 2),
            moic=moic,
            implied_irr_pct=round(irr, 1),
            deal_verdict=verdict,
        )

    @staticmethod
    def _irr(invested: float, returned: float, years: int) -> float:
        if invested <= 0 or returned <= 0 or years <= 0:
            return 0.0
        return (math.pow(returned / invested, 1.0 / years) - 1) * 100

    @staticmethod
    def _verdict(irr: float, moic: float, entry_ev_rev: float) -> str:
        if irr >= 25 and moic >= 3.0:
            return "Attractive"
        elif irr >= 15 and moic >= 2.0:
            return "Moderate"
        else:
            return "Cautious"
