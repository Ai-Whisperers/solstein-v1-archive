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
    candidate: DiscoveryCandidate,
    aggregated: AggregatedDataRecord,
) -> list[str]:
    """Extract source links from aggregated facts."""
    all_sources: list[str] = []
    for fact in aggregated.facts:
        for src in fact.sources_used:
            if src and src not in all_sources:
                all_sources.append(src)
    return list(dict.fromkeys(candidate.source_links + all_sources))


def _build_financials(
    signals: dict[str, SignalExtraction],
    facts: dict[str, Any],
) -> FinancialMetric:
    """Build FinancialMetric from signals and facts."""
    from .gather import _confidence_from_signal, _get_signal_numeric

    revenue = _get_signal_numeric(signals, "revenue_level")
    growth = _get_signal_numeric(signals, "growth_rate")
    margin = _get_signal_numeric(signals, "profitability")
    employees_raw = facts.get("employee_count")
    employees = int(employees_raw.value) if employees_raw is not None and hasattr(employees_raw, "value") else None
    funding_raised = _get_signal_numeric(signals, "funding")
    valuation = _get_signal_numeric(signals, "valuation")
    # Allow empty primary when this source set provides no revenue/employees
    allow_empty = revenue is None and employees is None

    # STORY-350: populate new financial fields from signals added in STORY-349
    ebitda = _get_signal_numeric(signals, "ebitda")
    net_income = _get_signal_numeric(signals, "net_income")
    pe_ratio = _get_signal_numeric(signals, "pe_ratio")
    current_price = _get_signal_numeric(signals, "current_price")
    eps_ttm = _get_signal_numeric(signals, "eps_ttm")

    # ebitda_margin is a ratio — only compute when both absolute values are present
    ebitda_margin: float | None = None
    if ebitda is not None and revenue is not None and revenue > 0:
        ebitda_margin = ebitda / revenue

    return FinancialMetric(
        allow_empty_primary=allow_empty,
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
        ebitda=ebitda,
        ebitda_margin=ebitda_margin,
        net_income=net_income,
        pe_ratio=pe_ratio,
        current_price=current_price,
        eps_ttm=eps_ttm,
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
    candidate: DiscoveryCandidate,
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
    candidate: DiscoveryCandidate,
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
    signals: dict[str, SignalExtraction],
    facts: dict[str, Any],
    description: Any,
) -> tuple[CompanyTier, ThreatLevel, AIMaturity, float | None]:
    """Determine tier, threat level, and AI maturity."""
    from .gather import (
        _ai_maturity_from_score,
        _ai_maturity_from_text,
        _get_signal_numeric,
        _threat_from_growth,
        _tier_from_market_cap,
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


def _build_data_source_description(aggregated: AggregatedDataRecord) -> str:
    """Build data source description."""
    source_count = len(aggregated.facts)
    return (
        f"Multi-source aggregation ({source_count} facts, {aggregated.data_completeness_percentage:.0%} completeness)"
    )


def build_company_entity_from_signals(
    candidate: DiscoveryCandidate,
    signal_record: SignalExtractionRecord,
    aggregated: AggregatedDataRecord,
    signals: dict[str, SignalExtraction],
    facts: dict[str, Any],
) -> Company:
    """Build Company entity from signals and aggregated facts."""
    from .gather import (
        _build_metric_justifications,
        _build_metric_observations,
        _build_metric_sources,
        _get_fact_value,
        _get_signal,
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

    # STORY-350: extract new fields from facts
    exchange_val = _get_fact_value(facts, "exchange")
    products_val = _get_fact_value(facts, "products")
    pricing_model_val = _get_fact_value(facts, "pricing_model")
    target_customers_val = _get_fact_value(facts, "target_customers")
    funding_rounds_val = _get_fact_value(facts, "funding_rounds")
    last_round_stage_val = _get_fact_value(facts, "last_round_stage")
    last_round_amount_val = _get_fact_value(facts, "last_round_amount")
    patent_count_val = _get_fact_value(facts, "total_patents")
    patent_categories_val = _get_fact_value(facts, "patent_categories")
    article_count_val = _get_fact_value(facts, "article_count")
    ai_jobs_val = _get_fact_value(facts, "ai_related_positions")
    hiring_sig = _get_signal(signals, "hiring_velocity")
    sentiment_sig = _get_signal(signals, "market_sentiment")

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
        sector=str(descriptive["sector"]) if descriptive.get("sector") else None,
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
        # STORY-350: new fields wired from facts and signals
        exchange=str(exchange_val) if exchange_val else None,
        products=list(products_val) if isinstance(products_val, list) else [],
        pricing_model=str(pricing_model_val) if pricing_model_val else None,
        target_customers=list(target_customers_val) if isinstance(target_customers_val, list) else [],
        funding_round_count=int(funding_rounds_val) if funding_rounds_val is not None else None,
        last_round_stage=str(last_round_stage_val) if last_round_stage_val else None,
        last_round_amount=float(last_round_amount_val) if last_round_amount_val is not None else None,
        patent_count=int(patent_count_val) if patent_count_val is not None else None,
        patent_categories=list(patent_categories_val) if isinstance(patent_categories_val, list) else [],
        news_sentiment=float(sentiment_sig.signal_value) if sentiment_sig else None,
        news_article_count=int(article_count_val) if article_count_val is not None else None,
        employee_growth_pct=float(hiring_sig.signal_value)
        if hiring_sig and isinstance(hiring_sig.signal_value, (int, float))
        else None,
        ai_jobs_count=int(ai_jobs_val) if ai_jobs_val is not None else None,
    )
