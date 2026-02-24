from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from loguru import logger

from solstein.domain.models import (
    AggregatedDataRecord,
    AggregatedFact,
    AIMaturity,
    Company,
    CompanyTier,
    ConfidenceLevel,
    FinancialMetric,
    RawDataRecord,
    SignalExtraction,
    SignalExtractionRecord,
    ThreatLevel,
)

from .discovery import DiscoveryCandidate

if TYPE_CHECKING:
    from solstein.adapters.registry import SourceRegistry


def _get_yfinance():
    try:
        import yfinance as yf

        return yf
    except ModuleNotFoundError:  # pragma: no cover
        return None


def _ai_maturity_from_text(text: str) -> AIMaturity:
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
    if market_cap is None:
        return CompanyTier.TIER_3
    if market_cap >= 10_000_000_000:
        return CompanyTier.TIER_1
    if market_cap >= 2_000_000_000:
        return CompanyTier.TIER_2
    return CompanyTier.TIER_3


def _threat_from_growth(growth_rate: float | None) -> ThreatLevel:
    if growth_rate is None:
        return ThreatLevel.MEDIUM
    if growth_rate >= 20:
        return ThreatLevel.HIGH
    if growth_rate >= 8:
        return ThreatLevel.MEDIUM
    return ThreatLevel.LOW


def _as_percent(value: float | None) -> float | None:
    if value is None:
        return None
    return float(value) * 100.0


def build_company_profile(candidate: DiscoveryCandidate) -> Company:
    now = datetime.now(UTC)
    ticker_url = (
        f"https://finance.yahoo.com/quote/{candidate.ticker}/"
        if candidate.ticker
        else None
    )
    source_links = list(
        dict.fromkeys(candidate.source_links + ([ticker_url] if ticker_url else []))
    )

    metric_sources = {
        "revenue": [ticker_url] if ticker_url else [],
        "growth_rate": [ticker_url] if ticker_url else [],
        "employees": [ticker_url] if ticker_url else [],
        "profit_margin": [ticker_url] if ticker_url else [],
        "funding": source_links,
        "valuation": [ticker_url] if ticker_url else source_links,
    }

    metric_justifications: dict[str, str] = {}

    if not candidate.ticker:
        metric_observations = {
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

    yf = _get_yfinance()
    if yf is None:
        metric_justifications = {
            "revenue": "Optional dependency 'yfinance' is not installed; ticker enrichment is unavailable.",
            "growth_rate": "Optional dependency 'yfinance' is not installed; ticker enrichment is unavailable.",
            "employees": "Optional dependency 'yfinance' is not installed; ticker enrichment is unavailable.",
            "profit_margin": "Optional dependency 'yfinance' is not installed; ticker enrichment is unavailable.",
            "funding": "Funding data not provided in ticker profile metadata.",
            "valuation": "Optional dependency 'yfinance' is not installed; ticker enrichment is unavailable.",
        }
        metric_observations = {metric: [] for metric in metric_sources}
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

    try:
        info = yf.Ticker(candidate.ticker).info
    except Exception as exc:
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
            last_updated=now,
        )

    revenue = info.get("totalRevenue")
    growth = _as_percent(info.get("revenueGrowth"))
    employees = info.get("fullTimeEmployees")
    margin = _as_percent(info.get("profitMargins"))
    market_cap = info.get("marketCap")
    description = (
        info.get("longBusinessSummary")
        or f"Discovered candidate in {candidate.market}."
    )

    metric_observations = {
        "revenue": (
            [{"source": ticker_url, "value": revenue}]
            if revenue is not None and ticker_url
            else []
        ),
        "growth_rate": (
            [{"source": ticker_url, "value": growth}]
            if growth is not None and ticker_url
            else []
        ),
        "employees": (
            [{"source": ticker_url, "value": employees}]
            if employees is not None and ticker_url
            else []
        ),
        "profit_margin": (
            [{"source": ticker_url, "value": margin}]
            if margin is not None and ticker_url
            else []
        ),
        "funding": [],
        "valuation": (
            [{"source": ticker_url, "value": market_cap}]
            if market_cap is not None and ticker_url
            else []
        ),
    }

    if revenue is None:
        metric_justifications["revenue"] = (
            "Revenue not published in ticker profile metadata."
        )
    if growth is None:
        metric_justifications["growth_rate"] = (
            "Growth rate not published in ticker profile metadata."
        )
    if employees is None:
        metric_justifications["employees"] = (
            "Employee count not published in ticker profile metadata."
        )
    if margin is None:
        metric_justifications["profit_margin"] = (
            "Profit margin not published in ticker profile metadata."
        )

    metric_justifications["funding"] = (
        "Funding rounds are typically unavailable in ticker metadata; needs private round sources."
    )
    if market_cap is None:
        metric_justifications["valuation"] = (
            "Market cap/valuation not available in ticker metadata at retrieval time."
        )

    financials = FinancialMetric(
        revenue=float(revenue) if revenue is not None else None,
        revenue_confidence=(
            ConfidenceLevel.CONFIRMED
            if revenue is not None
            else ConfidenceLevel.UNKNOWN
        ),
        growth_rate=float(growth) if growth is not None else None,
        growth_confidence=(
            ConfidenceLevel.ESTIMATED if growth is not None else ConfidenceLevel.UNKNOWN
        ),
        employees=int(employees) if employees is not None else None,
        employees_confidence=(
            ConfidenceLevel.ESTIMATED
            if employees is not None
            else ConfidenceLevel.UNKNOWN
        ),
        profit_margin=float(margin) if margin is not None else None,
        margin_confidence=(
            ConfidenceLevel.ESTIMATED if margin is not None else ConfidenceLevel.UNKNOWN
        ),
        funding_raised=None,
        funding_confidence=ConfidenceLevel.UNKNOWN,
        valuation=float(market_cap) if market_cap is not None else None,
        valuation_confidence=(
            ConfidenceLevel.ESTIMATED
            if market_cap is not None
            else ConfidenceLevel.UNKNOWN
        ),
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
        tier=_tier_from_market_cap(
            float(market_cap) if market_cap is not None else None
        ),
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


# ---------------------------------------------------------------------------
# Multi-source enrichment flow (Phase 4)
# ---------------------------------------------------------------------------


def enrich_company(
    candidate: DiscoveryCandidate,
    registry: SourceRegistry,
    batch_id: str,
) -> Company:
    """Enrich a candidate via multi-source adapters, aggregation, and signal extraction.

    This is the Phase 4 replacement for ``build_company_profile()``.
    It iterates all registered enrichment sources, aggregates facts
    across sources, extracts business signals, and builds the Company
    model with full provenance.

    If all enrichment sources fail, falls back to ``build_company_profile()``.
    """
    from .aggregate import DefaultFactAggregator
    from .signals import extract_signals

    raw_sources = []
    for source in registry.enrichment_sources:
        try:
            raw = source.enrich(
                company_id=candidate.company_id,
                company_name=candidate.name,
                ticker=candidate.ticker,
                website=None,
            )
            raw_sources.append(raw)
        except Exception as exc:
            logger.debug(
                "Enrichment source '{}' skipped for {}: {}",
                source.source_name,
                candidate.name,
                exc,
            )

    if not raw_sources:
        logger.warning(
            "No enrichment sources succeeded for {}; using legacy profile",
            candidate.name,
        )
        return build_company_profile(candidate)

    raw_record = RawDataRecord(
        company_id=candidate.company_id,
        gathering_batch_id=batch_id,
        sources=raw_sources,
        total_sources_found=len(raw_sources),
    )

    aggregator = DefaultFactAggregator()
    aggregated = aggregator.aggregate(candidate.company_id, raw_record)
    signal_record = extract_signals(aggregated, batch_id=batch_id)

    return build_company_from_signals(candidate, signal_record, aggregated)


# ---------------------------------------------------------------------------
# Signal-based Company builder (Phase 3)
# ---------------------------------------------------------------------------


def _confidence_from_signal(confidence: float) -> ConfidenceLevel:
    """Map a 0-1 signal confidence to a ConfidenceLevel enum."""
    if confidence >= 0.7:
        return ConfidenceLevel.CONFIRMED
    if confidence >= 0.4:
        return ConfidenceLevel.ESTIMATED
    return ConfidenceLevel.UNKNOWN


def _get_signal(
    signals: dict[str, SignalExtraction],
    name: str,
) -> SignalExtraction | None:
    return signals.get(name)


def _get_signal_numeric(
    signals: dict[str, SignalExtraction],
    name: str,
) -> float | None:
    sig = signals.get(name)
    if sig is None:
        return None
    v = sig.signal_value
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return float(v)
    return None


def _get_fact_value(
    facts: dict[str, AggregatedFact],
    name: str,
) -> Any:
    fact = facts.get(name)
    return fact.value if fact is not None else None


def _ai_maturity_from_score(score: float | None) -> AIMaturity:
    """Map an AI score (0-10) to an AIMaturity enum."""
    if score is None:
        return AIMaturity.NONE
    if score >= 8:
        return AIMaturity.VERY_STRONG
    if score >= 6:
        return AIMaturity.STRONG
    if score >= 4:
        return AIMaturity.MODERATE
    if score >= 2:
        return AIMaturity.LOW
    return AIMaturity.NONE


def _build_metric_sources(
    signals: dict[str, SignalExtraction],
    facts: dict[str, AggregatedFact],
) -> dict[str, list[str]]:
    """Build metric_sources from signal/fact source attribution."""
    metric_map = {
        "revenue": ["revenue"],
        "growth_rate": ["revenue_growth"],
        "employees": ["employee_count"],
        "profit_margin": ["profit_margin"],
        "funding": ["total_funding_raised"],
        "valuation": ["market_cap", "valuation"],
    }

    result: dict[str, list[str]] = {}
    for metric_name, fact_types in metric_map.items():
        sources: list[str] = []
        for ft in fact_types:
            fact = facts.get(ft)
            if fact is not None:
                sources.extend(s for s in fact.sources_used if s not in sources)
        result[metric_name] = sources
    return result


def _build_metric_observations(
    facts: dict[str, AggregatedFact],
) -> dict[str, list[dict[str, Any]]]:
    """Build metric_observations from aggregated fact values and sources."""
    metric_map = {
        "revenue": "revenue",
        "growth_rate": "revenue_growth",
        "employees": "employee_count",
        "profit_margin": "profit_margin",
        "funding": "total_funding_raised",
        "valuation": "market_cap",
    }

    result: dict[str, list[dict[str, Any]]] = {}
    for metric_name, fact_type in metric_map.items():
        fact = facts.get(fact_type)
        if fact is not None and fact.value is not None:
            obs = [{"source": src, "value": fact.value} for src in fact.sources_used[:3]]
            result[metric_name] = obs
        else:
            result[metric_name] = []
    return result


def _build_metric_justifications(
    signals: dict[str, SignalExtraction],
    facts: dict[str, AggregatedFact],
) -> dict[str, str]:
    """Build metric_justifications from signal reasoning."""
    justification_map = {
        "revenue": "revenue_level",
        "growth_rate": "growth_rate",
        "employees": "company_size",
        "profit_margin": "profitability",
        "funding": "funding",
        "valuation": "valuation",
    }

    result: dict[str, str] = {}
    for metric_name, signal_name in justification_map.items():
        sig = signals.get(signal_name)
        if sig is not None and sig.reasoning:
            result[metric_name] = sig.reasoning
        else:
            fact_type = {
                "revenue": "revenue",
                "growth_rate": "revenue_growth",
                "employees": "employee_count",
                "profit_margin": "profit_margin",
                "funding": "total_funding_raised",
                "valuation": "market_cap",
            }.get(metric_name, metric_name)
            fact = facts.get(fact_type)
            if fact is None:
                result[metric_name] = f"No data available for {metric_name} from any source."
            else:
                result[metric_name] = (
                    f"{metric_name} from {len(fact.sources_used)} source(s), "
                    f"confidence {fact.confidence:.0%}"
                )
    return result


def build_company_from_signals(
    candidate: DiscoveryCandidate,
    signal_record: SignalExtractionRecord,
    aggregated: AggregatedDataRecord,
) -> Company:
    """Build a Company from extracted signals and aggregated facts.

    This replaces the direct-yfinance approach in ``build_company_profile``
    with one that uses pre-aggregated multi-source data.  Provenance
    (metric_sources, metric_observations, metric_justifications) is
    populated from actual source attribution rather than pre-assumed URLs.

    Parameters
    ----------
    candidate:
        The DiscoveryCandidate being enriched.
    signal_record:
        Extracted business signals (revenue, growth, AI maturity, etc.).
    aggregated:
        The aggregated fact record with cross-referenced source data.
    """
    now = datetime.now(UTC)
    signals = {s.signal_name: s for s in signal_record.signals}
    facts = {f.fact_type: f for f in aggregated.facts}

    # -- Source links: union of all source URLs from aggregated facts --
    all_sources: list[str] = []
    for fact in aggregated.facts:
        for src in fact.sources_used:
            if src and src not in all_sources:
                all_sources.append(src)
    source_links = list(dict.fromkeys(candidate.source_links + all_sources))

    # -- Financials --
    revenue = _get_signal_numeric(signals, "revenue_level")
    growth = _get_signal_numeric(signals, "growth_rate")
    margin = _get_signal_numeric(signals, "profitability")
    employees_raw = _get_fact_value(facts, "employee_count")
    employees = int(employees_raw) if employees_raw is not None else None
    funding_raised = _get_signal_numeric(signals, "funding")
    valuation = _get_signal_numeric(signals, "valuation")

    financials = FinancialMetric(
        revenue=revenue,
        revenue_confidence=_confidence_from_signal(
            signals["revenue_level"].signal_confidence
        )
        if "revenue_level" in signals
        else ConfidenceLevel.UNKNOWN,
        growth_rate=growth,
        growth_confidence=_confidence_from_signal(
            signals["growth_rate"].signal_confidence
        )
        if "growth_rate" in signals
        else ConfidenceLevel.UNKNOWN,
        employees=employees,
        employees_confidence=_confidence_from_signal(
            facts["employee_count"].confidence
        )
        if "employee_count" in facts
        else ConfidenceLevel.UNKNOWN,
        profit_margin=margin,
        margin_confidence=_confidence_from_signal(
            signals["profitability"].signal_confidence
        )
        if "profitability" in signals
        else ConfidenceLevel.UNKNOWN,
        funding_raised=funding_raised,
        funding_confidence=_confidence_from_signal(
            signals["funding"].signal_confidence
        )
        if "funding" in signals
        else ConfidenceLevel.UNKNOWN,
        valuation=valuation,
        valuation_confidence=_confidence_from_signal(
            signals["valuation"].signal_confidence
        )
        if "valuation" in signals
        else ConfidenceLevel.UNKNOWN,
    )

    # -- Descriptive fields from facts --
    description = _get_fact_value(facts, "description")
    headquarters = _get_fact_value(facts, "headquarters") or candidate.region
    industry = _get_fact_value(facts, "industry") or candidate.industry
    website = _get_fact_value(facts, "website")
    founded_year = _get_fact_value(facts, "founded_year")
    sector = _get_fact_value(facts, "sector") or candidate.industry

    # -- Tech stack from facts --
    tech_stack_fact = _get_fact_value(facts, "tech_stack")
    tech_stack = list(tech_stack_fact) if isinstance(tech_stack_fact, list) else []
    if sector and str(sector) not in tech_stack:
        tech_stack.insert(0, str(sector))
    tech_stack.extend(t for t in candidate.tags if t not in tech_stack)

    # -- Tier / Threat / AI --
    market_cap = _get_signal_numeric(signals, "valuation")
    tier = _tier_from_market_cap(market_cap)
    threat = _threat_from_growth(growth)

    ai_sig = _get_signal(signals, "ai_maturity")
    ai_score_val = _get_signal_numeric(signals, "ai_maturity")
    if ai_score_val is not None:
        ai_maturity = _ai_maturity_from_score(ai_score_val)
    elif description:
        ai_maturity = _ai_maturity_from_text(str(description))
    else:
        ai_maturity = AIMaturity.NONE

    # -- Innovation / Patents --
    total_patents_val = _get_fact_value(facts, "total_patents")
    ai_related_patents_val = _get_fact_value(facts, "ai_related_patents")

    # -- Hiring / Employment --
    employee_growth = _get_signal_numeric(signals, "hiring_velocity")
    open_positions_val = _get_fact_value(facts, "open_positions")

    # -- Funding --
    investors = _get_fact_value(facts, "investors")
    lead_investors = list(investors) if isinstance(investors, list) else []
    last_round_stage = _get_fact_value(facts, "last_round_stage")

    # -- Name: prefer enriched name from facts --
    name = _get_fact_value(facts, "name") or candidate.name

    # -- Provenance --
    metric_sources = _build_metric_sources(signals, facts)
    metric_observations = _build_metric_observations(facts)
    metric_justifications = _build_metric_justifications(signals, facts)

    # -- Data source description --
    source_count = len(aggregated.facts)
    data_source = (
        f"Multi-source aggregation ({source_count} facts, "
        f"{aggregated.data_completeness_percentage:.0%} completeness)"
    )

    return Company(
        id=candidate.company_id,
        name=str(name),
        industry=str(industry),
        description=str(description) if description else f"Discovered candidate in {candidate.market}.",
        website=str(website) if website else None,
        headquarters=str(headquarters),
        founded_year=int(founded_year) if founded_year is not None else None,
        tier=tier,
        threat_level=threat,
        ai_maturity=ai_maturity,
        ai_score=int(ai_score_val) if ai_score_val is not None else None,
        ai_signal_level=str(ai_sig.signal_value) if ai_sig else None,
        tech_stack=tech_stack,
        financials=financials,
        geographic_presence=[str(headquarters)],
        lead_investors=lead_investors,
        employee_count=employees,
        open_positions=int(open_positions_val) if open_positions_val is not None else None,
        data_source=data_source,
        source_links=source_links,
        metric_sources=metric_sources,
        metric_justifications=metric_justifications,
        metric_observations=metric_observations,
        last_updated=now,
    )
