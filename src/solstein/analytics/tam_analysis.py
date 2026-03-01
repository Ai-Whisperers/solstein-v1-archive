"""TAM / SAM / SOM Market Size Analysis (EPIC-040).

Estimates Total Addressable Market (TAM), Serviceable Addressable Market
(SAM), and Serviceable Obtainable Market (SOM) from company financial data
and market parameters.

Usage::

    from solstein.analytics.tam_analysis import TamAnalyzer, MarketParams

    params = MarketParams(
        market_name="B2B SaaS Security",
        total_market_size_eur_bn=45.0,
        target_segment_share=0.15,  # 15% of market
        realistic_capture_rate=0.05,  # 5% of SAM
        cagr_pct=22.0,
        forecast_years=5,
    )
    result = TamAnalyzer().analyze(company, params)
    print(result.tam_eur_bn, result.sam_eur_bn, result.som_eur_bn)
"""

from __future__ import annotations

from dataclasses import dataclass

from solstein.domain.models import Company


@dataclass
class MarketParams:
    """Input parameters for TAM/SAM/SOM estimation.

    Attributes:
        market_name: Descriptive name of the target market.
        total_market_size_eur_bn: Current TAM in EUR billions.
        target_segment_share: Fraction of TAM the company targets (0–1).
        realistic_capture_rate: Fraction of SAM the company can realistically win (0–1).
        cagr_pct: Expected annual market growth rate (%).
        forecast_years: Number of years for forward-looking projection.
    """

    market_name: str
    total_market_size_eur_bn: float
    target_segment_share: float = 0.10
    realistic_capture_rate: float = 0.05
    cagr_pct: float = 10.0
    forecast_years: int = 5


@dataclass
class TamResult:
    """TAM/SAM/SOM analysis output.

    Attributes:
        tam_eur_bn: Total addressable market (EUR billions).
        sam_eur_bn: Serviceable addressable market (EUR billions).
        som_eur_bn: Serviceable obtainable market (EUR billions).
        tam_forecast_eur_bn: TAM projected *forecast_years* out at CAGR.
        market_share_pct: Current implied company market share (%).
        headroom_multiplier: How many times larger SOM is vs. current revenue.
        insight: Summary recommendation for the PE/VC investor.
    """

    tam_eur_bn: float
    sam_eur_bn: float
    som_eur_bn: float
    tam_forecast_eur_bn: float
    market_share_pct: float
    headroom_multiplier: float
    insight: str


class TamAnalyzer:
    """TAM/SAM/SOM estimator for PE/VC deal assessment."""

    def analyze(self, company: Company, params: MarketParams) -> TamResult:
        """Estimate TAM/SAM/SOM for *company* in the given market.

        Args:
            company: Company domain object with revenue data.
            params: Market sizing parameters.

        Returns:
            TamResult with all market size estimates and deal insight.
        """
        tam = params.total_market_size_eur_bn
        sam = round(tam * params.target_segment_share, 4)
        som = round(sam * params.realistic_capture_rate, 4)

        # Forward-looking TAM at CAGR
        tam_forecast = round(tam * (1 + params.cagr_pct / 100) ** params.forecast_years, 4)

        # Current company revenue (from financials if available)
        fin = getattr(company, "financials", None)
        revenue_eur_m: float = 0.0
        if fin and getattr(fin, "revenue", None):
            revenue_eur_m = fin.revenue  # Assumed EUR millions

        revenue_eur_bn = revenue_eur_m / 1000.0 if revenue_eur_m else 0.0

        market_share_pct = round((revenue_eur_bn / tam) * 100, 4) if tam > 0 else 0.0
        headroom = round(som / revenue_eur_bn, 1) if revenue_eur_bn > 0 else 999.0

        insight = self._insight(
            company=company,
            market_share_pct=market_share_pct,
            headroom=headroom,
            params=params,
        )

        return TamResult(
            tam_eur_bn=tam,
            sam_eur_bn=sam,
            som_eur_bn=som,
            tam_forecast_eur_bn=tam_forecast,
            market_share_pct=market_share_pct,
            headroom_multiplier=headroom,
            insight=insight,
        )

    def _insight(
        self,
        company: Company,
        market_share_pct: float,
        headroom: float,
        params: MarketParams,
    ) -> str:
        if market_share_pct > 10.0:
            return (
                f"{company.name} already holds >{market_share_pct:.1f}% market share — "
                "potential market-leader dynamics; assess defensibility."
            )
        elif headroom > 50:
            return (
                f"SOM headroom is {headroom:.0f}× current revenue — "
                f"significant white-space opportunity in {params.market_name}."
            )
        elif params.cagr_pct > 20:
            return (
                f"Fast-growing market ({params.cagr_pct:.0f}% CAGR) — "
                "capture window is time-sensitive; early mover advantage at stake."
            )
        else:
            return (
                f"Moderate market opportunity in {params.market_name}. "
                f"SAM: EUR {params.total_market_size_eur_bn * params.target_segment_share:.1f}bn."
            )
