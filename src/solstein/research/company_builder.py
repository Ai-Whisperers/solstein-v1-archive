"""Company builder from signals helper.

EPIC-020: Extracted from build_company_from_signals function.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from solstein.domain.models import (
    AIMaturity,
    Company,
    CompanyTier,
    ConfidenceLevel,
    FinancialMetric,
    ThreatLevel,
)

if TYPE_CHECKING:
    from .discovery import DiscoveryCandidate
    from .signals import AggregatedDataRecord, SignalExtraction, SignalExtractionRecord


def _extract_source_links(
    candidate: "DiscoveryCandidate",
    aggregated: "AggregatedDataRecord",
) -> list[str]:
    """Extract source links from aggregated facts."""
    all_sources: list[str] = []
    for fact in aggregated.facts:
        for src in fact.sources_used:
            if src and src not in all_sources:
                all_sources.append(src)
    return list(dict.fromkeys(candidate.source_links + all_sources))


def _build_financials(
    signals: dict[str, "SignalExtraction"],
    facts: dict[str, Any],
) -> FinancialMetric:
    """Build FinancialMetric from signals and facts."""
    from .gather import _get_signal_numeric, _confidence_from_signal

    revenue = _get_signal_numeric(signals, "revenue_level")
    growth = _get_signal_numeric(signals, "growth_rate")
    margin = _get_signal_numeric(signals, "profitability")
    employees_raw = facts.get("employee_count")
    employees = int(employees_raw.value) if employees_raw is not None and hasattr(employees_raw, "value") else None
    funding_raised = _get_signal_numeric(signals, "funding")
    valuation = _get_signal_numeric(signals, "valuation")

    return FinancialMetric(
        revenue=revenue,
        revenue_confidence=_confidence_from_signal(signals["revenue_level"].signal_confidence)
        if "revenue_level" in signals
        else ConfidenceLevel.UNKNOWN,
        growth_rate=growth,
        growth_confidence=_confidence_from_signal(signals["growth_rate"].signal_confidence)
        if "growth_rate" in signals
        else ConfidenceLevel.UNKNOWN,
        employees=employees,
        employees_confidence=_confidence_from_signal(facts["employee_count"].confidence)
        if "employee_count" in facts
        else ConfidenceLevel.UNKNOWN,
        profit_margin=margin,
        margin_confidence=_confidence_from_signal(signals["profitability"].signal_confidence)
        if "profitability" in signals
        else ConfidenceLevel.UNKNOWN,
        funding_raised=funding_raised,
        funding_confidence=_confidence_from_signal(signals["funding"].signal_confidence)
        if "funding" in signals
        else ConfidenceLevel.UNKNOWN,
        valuation=valuation,
        valuation_confidence=_confidence_from_signal(signals["valuation"].signal_confidence)
        if "valuation" in signals
        else ConfidenceLevel.UNKNOWN,
    )


def _extract_descriptive_fields(
    candidate: "DiscoveryCandidate",
    facts: dict[str, Any],
) -> dict[str, Any]:
    """Extract descriptive fields from facts."""
    from .gather import _get_fact_value

    return {
        "description": _get_fact_value(facts, "description"),
        "headquarters": _get_fact_value(facts, "headquarters") or candidate.region,
        "industry": _get_fact_value(facts, "industry") or candidate.industry,
        "website": _get_fact_value(facts, "website"),
        "founded_year": _get_fact_value(facts, "founded_year"),
        "sector": _get_fact_value(facts, "sector") or candidate.industry,
    }


def _build_tech_stack(
    facts: dict[str, Any],
    candidate: "DiscoveryCandidate",
) -> list[str]:
    """Build tech stack from facts and candidate tags."""
    from .gather import _get_fact_value

    tech_stack_fact = _get_fact_value(facts, "tech_stack")
    tech_stack = list(tech_stack_fact) if isinstance(tech_stack_fact, list) else []
    sector = _get_fact_value(facts, "sector") or candidate.industry
    if sector and str(sector) not in tech_stack:
        tech_stack.insert(0, str(sector))
    tech_stack.extend(t for t in candidate.tags if t not in tech_stack)
    return tech_stack


def _determine_tier_threat_ai(
    signals: dict[str, "SignalExtraction"],
    facts: dict[str, Any],
    description: Any,
) -> tuple[CompanyTier, ThreatLevel, AIMaturity, float | None]:
    """Determine tier, threat level, and AI maturity."""
    from .gather import (
        _get_signal_numeric,
        _tier_from_market_cap,
        _threat_from_growth,
        _ai_maturity_from_score,
        _ai_maturity_from_text,
    )

    market_cap = _get_signal_numeric(signals, "valuation")
    growth = _get_signal_numeric(signals, "growth_rate")
    tier = _tier_from_market_cap(market_cap)
    threat = _threat_from_growth(growth)

    ai_score_val = _get_signal_numeric(signals, "ai_maturity")
    if ai_score_val is not None:
        ai_maturity = _ai_maturity_from_score(ai_score_val)
    elif description:
        ai_maturity = _ai_maturity_from_text(str(description))
    else:
        ai_maturity = AIMaturity.NONE

    return tier, threat, ai_maturity, ai_score_val


def _extract_lead_investors(facts: dict[str, Any]) -> list[str]:
    """Extract lead investors from facts."""
    from .gather import _get_fact_value

    investors = _get_fact_value(facts, "investors")
    return list(investors) if isinstance(investors, list) else []


def _build_data_source_description(aggregated: "AggregatedDataRecord") -> str:
    """Build data source description."""
    source_count = len(aggregated.facts)
    return (
        f"Multi-source aggregation ({source_count} facts, {aggregated.data_completeness_percentage:.0%} completeness)"
    )


def build_company_entity_from_signals(
    candidate: "DiscoveryCandidate",
    signal_record: "SignalExtractionRecord",
    aggregated: "AggregatedDataRecord",
    signals: dict[str, "SignalExtraction"],
    facts: dict[str, Any],
) -> Company:
    """Build Company entity from signals and aggregated facts."""
    from .gather import (
        _get_signal,
        _get_fact_value,
        _build_metric_sources,
        _build_metric_observations,
        _build_metric_justifications,
    )

    now = datetime.now(timezone.utc)

    # Extract components
    source_links = _extract_source_links(candidate, aggregated)
    financials = _build_financials(signals, facts)
    descriptive = _extract_descriptive_fields(candidate, facts)
    tech_stack = _build_tech_stack(facts, candidate)
    tier, threat, ai_maturity, ai_score_val = _determine_tier_threat_ai(signals, facts, descriptive["description"])
    lead_investors = _extract_lead_investors(facts)
    data_source = _build_data_source_description(aggregated)

    # Get additional fields
    name = _get_fact_value(facts, "name") or candidate.name
    open_positions_val = _get_fact_value(facts, "open_positions")
    ai_sig = _get_signal(signals, "ai_maturity")

    # Build provenance
    metric_sources = _build_metric_sources(signals, facts)
    metric_observations = _build_metric_observations(facts)
    metric_justifications = _build_metric_justifications(signals, facts)

    return Company(
        id=candidate.company_id,
        name=str(name),
        industry=str(descriptive["industry"]),
        description=str(descriptive["description"])
        if descriptive["description"]
        else f"Discovered candidate in {candidate.market}.",
        website=str(descriptive["website"]) if descriptive["website"] else None,
        headquarters=str(descriptive["headquarters"]),
        founded_year=int(descriptive["founded_year"]) if descriptive["founded_year"] is not None else None,
        tier=tier,
        threat_level=threat,
        ai_maturity=ai_maturity,
        ai_score=int(ai_score_val) if ai_score_val is not None else None,
        ai_signal_level=str(ai_sig.signal_value) if ai_sig else None,
        tech_stack=tech_stack,
        financials=financials,
        geographic_presence=[str(descriptive["headquarters"])],
        lead_investors=lead_investors,
        employee_count=financials.employees,
        open_positions=int(open_positions_val) if open_positions_val is not None else None,
        data_source=data_source,
        source_links=source_links,
        metric_sources=metric_sources,
        metric_justifications=metric_justifications,
        metric_observations=metric_observations,
        signal_confidences={s.signal_name: s.signal_confidence for s in signal_record.signals},
        last_updated=now,
    )
