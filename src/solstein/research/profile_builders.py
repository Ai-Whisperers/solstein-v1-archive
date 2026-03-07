"""Company profile builders for research pipeline.

EPIC-020: Extracted from build_company_profile function.
Each builder creates a Company profile for a specific scenario.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from solstein.domain.models import (
    AIMaturity,
    Company,
    CompanyTier,
    ConfidenceLevel,
    FinancialMetric,
    ThreatLevel,
)

from .discovery import DiscoveryCandidate

if TYPE_CHECKING:
    from typing import Any


def _build_metric_sources(candidate: DiscoveryCandidate, ticker_url: str | None) -> dict[str, list[str | None]]:
    """Build metric sources dictionary."""
    return {
        "revenue": [ticker_url] if ticker_url else [],
        "growth_rate": [ticker_url] if ticker_url else [],
        "employees": [ticker_url] if ticker_url else [],
        "profit_margin": [ticker_url] if ticker_url else [],
        "funding": candidate.source_links,
        "valuation": [ticker_url] if ticker_url else candidate.source_links,
    }


def _build_metric_observations_empty() -> dict[str, list]:
    """Build empty metric observations for all metrics."""
    return {
        metric: []
        for metric in [
            "revenue",
            "growth_rate",
            "employees",
            "profit_margin",
            "funding",
            "valuation",
        ]
    }


def build_company_profile_no_ticker(candidate: DiscoveryCandidate) -> Company:
    """Build Company profile when no ticker is available."""
    now = datetime.now(timezone.utc)
    ticker_url = None
    source_links = list(dict.fromkeys(candidate.source_links))

    metric_sources = _build_metric_sources(candidate, ticker_url)
    metric_observations = _build_metric_observations_empty()

    metric_justifications = {
        "revenue": "No direct public ticker feed available; value requires manual filing-level collection.",
        "growth_rate": "No direct public ticker feed available; estimated from public narrative sources.",
        "employees": "No direct public ticker feed available; estimated from company/about pages or hiring signals.",
        "profit_margin": "No direct public ticker feed available; margin cannot be verified from market feed.",
        "funding": "Funding history not disclosed through market feed; requires private/company disclosures.",
        "valuation": "Valuation unavailable from ticker feed for non-listed/private entity.",
    }

    return Company(
        id=candidate.company_id,
        name=candidate.name,
        industry=candidate.industry,
        description=f"Discovered via market catalog: {candidate.discovery_reason}",
        headquarters=candidate.region,
        tier=CompanyTier.TIER_3,
        threat_level=ThreatLevel.MEDIUM,
        ai_maturity=AIMaturity.MODERATE,
        financials=FinancialMetric(),
        geographic_presence=[candidate.region],
        tech_stack=candidate.tags,
        data_source="Automated market discovery catalog",
        source_links=source_links,
        metric_sources=metric_sources,
        metric_justifications=metric_justifications,
        metric_observations=metric_observations,
        last_updated=now,
    )


def build_company_profile_yfinance_missing(candidate: DiscoveryCandidate) -> Company:
    """Build Company profile when yfinance is not installed."""
    now = datetime.now(timezone.utc)
    ticker_url = f"https://finance.yahoo.com/quote/{candidate.ticker}/" if candidate.ticker else None
    source_links = list(dict.fromkeys(candidate.source_links + ([ticker_url] if ticker_url else [])))

    metric_sources = _build_metric_sources(candidate, ticker_url)
    metric_observations = _build_metric_observations_empty()

    metric_justifications = {
        "revenue": "Optional dependency 'yfinance' is not installed; ticker enrichment is unavailable.",
        "growth_rate": "Optional dependency 'yfinance' is not installed; ticker enrichment is unavailable.",
        "employees": "Optional dependency 'yfinance' is not installed; ticker enrichment is unavailable.",
        "profit_margin": "Optional dependency 'yfinance' is not installed; ticker enrichment is unavailable.",
        "funding": "Funding data not provided in ticker profile metadata.",
        "valuation": "Optional dependency 'yfinance' is not installed; ticker enrichment is unavailable.",
    }

    return Company(
        id=candidate.company_id,
        name=candidate.name,
        industry=candidate.industry,
        description=f"Discovery candidate without live enrichment: {candidate.discovery_reason}",
        headquarters=candidate.region,
        tier=CompanyTier.TIER_3,
        threat_level=ThreatLevel.MEDIUM,
        ai_maturity=AIMaturity.LOW,
        financials=FinancialMetric(),
        geographic_presence=[candidate.region],
        tech_stack=candidate.tags,
        data_source="Discovery catalog (yfinance missing)",
        source_links=source_links,
        metric_sources=metric_sources,
        metric_justifications=metric_justifications,
        metric_observations=metric_observations,
        last_updated=now,
    )


def build_company_profile_ticker_failed(candidate: DiscoveryCandidate, exc: Exception) -> Company:
    """Build Company profile when ticker lookup fails."""
    now = datetime.now(timezone.utc)
    ticker_url = f"https://finance.yahoo.com/quote/{candidate.ticker}/" if candidate.ticker else None
    source_links = list(dict.fromkeys(candidate.source_links + ([ticker_url] if ticker_url else [])))

    metric_sources = _build_metric_sources(candidate, ticker_url)
    metric_observations = _build_metric_observations_empty()

    metric_justifications = {
        "revenue": f"Ticker lookup failed: {exc}",
        "growth_rate": f"Ticker lookup failed: {exc}",
        "employees": f"Ticker lookup failed: {exc}",
        "profit_margin": f"Ticker lookup failed: {exc}",
        "funding": "Funding data not provided in yfinance company profile.",
        "valuation": f"Ticker lookup failed: {exc}",
    }

    return Company(
        id=candidate.company_id,
        name=candidate.name,
        industry=candidate.industry,
        description=f"Discovery candidate with failed live enrichment: {candidate.discovery_reason}",
        headquarters=candidate.region,
        tier=CompanyTier.TIER_3,
        threat_level=ThreatLevel.MEDIUM,
        ai_maturity=AIMaturity.LOW,
        financials=FinancialMetric(),
        geographic_presence=[candidate.region],
        tech_stack=candidate.tags,
        data_source="Discovery + yfinance (lookup failed)",
        source_links=source_links,
        metric_sources=metric_sources,
        metric_justifications=metric_justifications,
        metric_observations=metric_observations,
        last_updated=now,
    )


def _as_percent(value: float | None) -> float | None:
    """Convert decimal to percentage."""
    if value is None:
        return None
    return float(value) * 100.0


def _ai_maturity_from_text(text: str) -> AIMaturity:
    """Determine AI maturity from text description."""
    txt = text.lower()
    if any(
        k in txt
        for k in [
            "generative",
            "llm",
            "artificial intelligence",
            "machine learning",
            "neural",
        ]
    ):
        return AIMaturity.STRONG
    if any(k in txt for k in ["analytics", "automation", "digital"]):
        return AIMaturity.MODERATE
    return AIMaturity.LOW


def _tier_from_market_cap(market_cap: float | None) -> CompanyTier:
    """Determine company tier from market cap."""
    if market_cap is None:
        return CompanyTier.TIER_3
    if market_cap >= 10_000_000_000:
        return CompanyTier.TIER_1
    if market_cap >= 2_000_000_000:
        return CompanyTier.TIER_2
    return CompanyTier.TIER_3


def _threat_from_growth(growth_rate: float | None) -> ThreatLevel:
    """Determine threat level from growth rate."""
    if growth_rate is None:
        return ThreatLevel.MEDIUM
    if growth_rate >= 20:
        return ThreatLevel.HIGH
    if growth_rate >= 8:
        return ThreatLevel.MEDIUM
    return ThreatLevel.LOW


def build_company_profile_from_ticker(candidate: DiscoveryCandidate, info: dict[str, Any]) -> Company:
    """Build Company profile from yfinance ticker data."""
    now = datetime.now(timezone.utc)
    ticker_url = f"https://finance.yahoo.com/quote/{candidate.ticker}/"
    source_links = list(dict.fromkeys(candidate.source_links + [ticker_url]))

    metric_sources = _build_metric_sources(candidate, ticker_url)
    metric_justifications: dict[str, str] = {}

    revenue = info.get("totalRevenue")
    growth = _as_percent(info.get("revenueGrowth"))
    employees = info.get("fullTimeEmployees")
    margin = _as_percent(info.get("profitMargins"))
    market_cap = info.get("marketCap")
    description = info.get("longBusinessSummary") or f"Discovered candidate in {candidate.market}."

    metric_observations = {
        "revenue": ([{"source": ticker_url, "value": revenue}] if revenue is not None else []),
        "growth_rate": ([{"source": ticker_url, "value": growth}] if growth is not None else []),
        "employees": ([{"source": ticker_url, "value": employees}] if employees is not None else []),
        "profit_margin": ([{"source": ticker_url, "value": margin}] if margin is not None else []),
        "funding": [],
        "valuation": ([{"source": ticker_url, "value": market_cap}] if market_cap is not None else []),
    }

    if revenue is None:
        metric_justifications["revenue"] = "Revenue not published in ticker profile metadata."
    if growth is None:
        metric_justifications["growth_rate"] = "Growth rate not published in ticker profile metadata."
    if employees is None:
        metric_justifications["employees"] = "Employee count not published in ticker profile metadata."
    if margin is None:
        metric_justifications["profit_margin"] = "Profit margin not published in ticker profile metadata."

    metric_justifications["funding"] = (
        "Funding rounds are typically unavailable in ticker metadata; needs private round sources."
    )
    if market_cap is None:
        metric_justifications["valuation"] = "Market cap/valuation not available in ticker metadata at retrieval time."

    financials = FinancialMetric(
        revenue=float(revenue) if revenue is not None else None,
        revenue_confidence=(ConfidenceLevel.CONFIRMED if revenue is not None else ConfidenceLevel.UNKNOWN),
        growth_rate=float(growth) if growth is not None else None,
        growth_confidence=(ConfidenceLevel.ESTIMATED if growth is not None else ConfidenceLevel.UNKNOWN),
        employees=int(employees) if employees is not None else None,
        employees_confidence=(ConfidenceLevel.ESTIMATED if employees is not None else ConfidenceLevel.UNKNOWN),
        profit_margin=float(margin) if margin is not None else None,
        margin_confidence=(ConfidenceLevel.ESTIMATED if margin is not None else ConfidenceLevel.UNKNOWN),
        funding_raised=None,
        funding_confidence=ConfidenceLevel.UNKNOWN,
        valuation=float(market_cap) if market_cap is not None else None,
        valuation_confidence=(ConfidenceLevel.ESTIMATED if market_cap is not None else ConfidenceLevel.UNKNOWN),
    )

    region = info.get("country") or candidate.region
    industry = info.get("industry") or candidate.industry
    sector = info.get("sector") or candidate.industry

    return Company(
        id=candidate.company_id,
        name=info.get("longName") or info.get("shortName") or candidate.name,
        industry=str(industry),
        description=str(description),
        website=info.get("website"),
        headquarters=region,
        founded_year=info.get("foundedDate"),
        tier=_tier_from_market_cap(float(market_cap) if market_cap is not None else None),
        threat_level=_threat_from_growth(float(growth) if growth is not None else None),
        ai_maturity=_ai_maturity_from_text(str(description)),
        saas_maturity=5,
        tech_stack=[str(sector)] + candidate.tags,
        financials=financials,
        geographic_presence=[str(region)],
        data_source="Automated discovery + yfinance",
        source_links=source_links,
        metric_sources=metric_sources,
        metric_justifications=metric_justifications,
        metric_observations=metric_observations,
        last_updated=now,
    )
