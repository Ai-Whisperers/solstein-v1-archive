from __future__ import annotations

from typing import TYPE_CHECKING, Any

from loguru import logger

from solstein.domain.models import (
    AggregatedDataRecord,
    AggregatedFact,
    AIMaturity,
    Company,
    CompanyTier,
    ConfidenceLevel,
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
    """Build Company profile from DiscoveryCandidate using appropriate builder.

    EPIC-020: Refactored from 188-line function to use builder functions.
    """
    from .profile_builders import (
        build_company_profile_from_ticker,
        build_company_profile_no_ticker,
        build_company_profile_ticker_failed,
        build_company_profile_yfinance_missing,
    )

    # No ticker available
    if not candidate.ticker:
        return build_company_profile_no_ticker(candidate)

    # Get yfinance module
    yf = _get_yfinance()
    if yf is None:
        return build_company_profile_yfinance_missing(candidate)

    # Try to get ticker info
    try:
        info = yf.Ticker(candidate.ticker).info
    except Exception as exc:
        return build_company_profile_ticker_failed(candidate, exc)

    # Build profile from ticker data
    return build_company_profile_from_ticker(candidate, info)


# ---------------------------------------------------------------------------
# Multi-source enrichment flow (Phase 4)
# ---------------------------------------------------------------------------

# Data quality tier thresholds
_WELL_SOURCED_MIN = 3
_PARTIAL_MIN = 1


def _data_quality_tier(source_count: int) -> str:
    """Classify data quality tier based on enrichment source count."""
    if source_count >= _WELL_SOURCED_MIN:
        return "well-sourced"
    if source_count >= _PARTIAL_MIN:
        return "partial"
    return "stub"


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
        company = build_company_profile(candidate)
        company.enrichment_source_count = 0
        company.data_quality_tier = "stub"
        return company

    raw_record = RawDataRecord(
        company_id=candidate.company_id,
        gathering_batch_id=batch_id,
        sources=raw_sources,
        total_sources_found=len(raw_sources),
    )

    aggregator = DefaultFactAggregator()
    aggregated = aggregator.aggregate(candidate.company_id, raw_record)
    signal_record = extract_signals(aggregated, batch_id=batch_id)

    company = build_company_from_signals(candidate, signal_record, aggregated)
    company.enrichment_source_count = len(raw_sources)
    company.data_quality_tier = _data_quality_tier(len(raw_sources))
    return company


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
                    f"{metric_name} from {len(fact.sources_used)} source(s), confidence {fact.confidence:.0%}"
                )
    return result


def build_company_from_signals(
    candidate: DiscoveryCandidate,
    signal_record: SignalExtractionRecord,
    aggregated: AggregatedDataRecord,
) -> Company:
    """
    Build a Company from extracted signals and aggregated facts.

    EPIC-020: Refactored to use company_builder module.
    """
    from .company_builder import build_company_entity_from_signals

    signals = {s.signal_name: s for s in signal_record.signals}
    facts = {f.fact_type: f for f in aggregated.facts}

    return build_company_entity_from_signals(candidate, signal_record, aggregated, signals, facts)


async def enrich_company_async(
    candidate: DiscoveryCandidate,
    registry: SourceRegistry,
    batch_id: str,
) -> Company:
    """Async version of enrich_company.

    Runs the synchronous enrichment in a thread pool for non-blocking execution.
    """
    import asyncio

    return await asyncio.to_thread(
        enrich_company,
        candidate,
        registry,
        batch_id,
    )
