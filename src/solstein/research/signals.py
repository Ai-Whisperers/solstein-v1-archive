"""Signal extraction — maps aggregated facts to business signals for scoring.

Bridges the gap between raw facts (``AggregatedFact``) and the scoring
engine by producing ``SignalExtraction`` objects with confidence levels,
calculation methods, and human-readable reasoning.
"""

from __future__ import annotations

from datetime import datetime, timezone

from loguru import logger

from solstein.domain.models import (
    AggregatedDataRecord,
    AggregatedFact,
    SignalExtraction,
    SignalExtractionRecord,
)

# ---------------------------------------------------------------------------
# Signal definitions: each maps one or more fact types to a signal
# ---------------------------------------------------------------------------


def _get_fact(facts_by_type: dict[str, AggregatedFact], key: str) -> AggregatedFact | None:
    return facts_by_type.get(key)


def _get_numeric(facts_by_type: dict[str, AggregatedFact], key: str) -> float | None:
    fact = facts_by_type.get(key)
    if fact is None:
        return None
    v = fact.value
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return float(v)
    return None


def _signal_revenue_level(facts: dict[str, AggregatedFact]) -> SignalExtraction | None:
    """Revenue level signal from revenue facts."""
    revenue = _get_numeric(facts, "revenue")
    if revenue is None:
        return None

    rev_fact = facts["revenue"]

    return SignalExtraction(
        signal_name="revenue_level",
        signal_value=revenue,
        signal_confidence=rev_fact.confidence,
        source_facts=["revenue"],
        calculation_method="direct",
        calculation_formula="revenue from highest-confidence source",
        reasoning=f"Revenue of {revenue:,.0f} from {len(rev_fact.sources_used)} source(s), "
        f"{rev_fact.source_agreement_percentage:.0%} agreement",
        why_it_matters="Core financial metric for company size and market position",
    )


def _signal_growth_rate(facts: dict[str, AggregatedFact]) -> SignalExtraction | None:
    """Growth rate signal from revenue growth facts."""
    growth = _get_numeric(facts, "revenue_growth")
    if growth is None:
        return None

    growth_fact = facts["revenue_growth"]

    return SignalExtraction(
        signal_name="growth_rate",
        signal_value=growth,
        signal_confidence=growth_fact.confidence,
        source_facts=["revenue_growth"],
        calculation_method="direct",
        calculation_formula="revenue_growth_yoy from highest-confidence source",
        reasoning=f"Revenue growth of {growth:.1%} YoY, confidence {growth_fact.confidence:.0%}",
        why_it_matters="Growth rate drives scoring and threat assessment",
    )


def _signal_profitability(facts: dict[str, AggregatedFact]) -> SignalExtraction | None:
    """Profitability signal from profit margin facts."""
    margin = _get_numeric(facts, "profit_margin")
    if margin is None:
        return None

    margin_fact = facts["profit_margin"]

    return SignalExtraction(
        signal_name="profitability",
        signal_value=margin,
        signal_confidence=margin_fact.confidence,
        source_facts=["profit_margin"],
        calculation_method="direct",
        calculation_formula="profit_margin from highest-confidence source",
        reasoning=f"Profit margin of {margin:.1%}, confidence {margin_fact.confidence:.0%}",
        why_it_matters="Profitability indicates financial health and sustainability",
    )


def _signal_company_size(facts: dict[str, AggregatedFact]) -> SignalExtraction | None:
    """Company size signal from employee count and market cap."""
    employees = _get_numeric(facts, "employee_count")
    market_cap = _get_numeric(facts, "market_cap")

    if employees is None and market_cap is None:
        return None

    source_facts = []
    parts = []
    confidence_values = []

    if employees is not None:
        source_facts.append("employee_count")
        parts.append(f"{int(employees):,} employees")
        confidence_values.append(facts["employee_count"].confidence)

    if market_cap is not None:
        source_facts.append("market_cap")
        parts.append(f"${market_cap:,.0f} market cap")
        confidence_values.append(facts["market_cap"].confidence)

    # Composite: use market_cap if available, else employee count
    primary_value = market_cap if market_cap is not None else employees
    avg_confidence = sum(confidence_values) / len(confidence_values)

    return SignalExtraction(
        signal_name="company_size",
        signal_value=primary_value,
        signal_confidence=round(avg_confidence, 3),
        source_facts=source_facts,
        calculation_method="composite",
        calculation_formula="market_cap preferred, employee_count as fallback",
        reasoning=f"Company size: {', '.join(parts)}",
        why_it_matters="Company size determines tier classification and competitive positioning",
    )


def _signal_valuation(facts: dict[str, AggregatedFact]) -> SignalExtraction | None:
    """Valuation signal from market cap or funding valuation."""
    market_cap = _get_numeric(facts, "market_cap")
    funding_val = _get_numeric(facts, "valuation")

    value = market_cap or funding_val
    if value is None:
        return None

    source_facts = []
    if market_cap is not None:
        source_facts.append("market_cap")
    if funding_val is not None:
        source_facts.append("valuation")

    source_fact = facts.get("market_cap") or facts.get("valuation")
    confidence = source_fact.confidence if source_fact else 0.5

    method = "market_cap" if market_cap is not None else "last_round_valuation"

    return SignalExtraction(
        signal_name="valuation",
        signal_value=value,
        signal_confidence=confidence,
        source_facts=source_facts,
        calculation_method="direct",
        calculation_formula=f"valuation from {method}",
        reasoning=f"Valuation of ${value:,.0f} via {method}",
        why_it_matters="Valuation determines tier classification",
    )


def _signal_innovation(facts: dict[str, AggregatedFact]) -> SignalExtraction | None:
    """Innovation signal from patent portfolio."""
    total_patents = _get_numeric(facts, "total_patents")
    ai_patents = _get_numeric(facts, "ai_related_patents")

    if total_patents is None:
        return None

    source_facts = ["total_patents"]
    parts = [f"{int(total_patents)} total patents"]

    ai_ratio = None
    if ai_patents is not None and total_patents > 0:
        ai_ratio = ai_patents / total_patents
        source_facts.append("ai_related_patents")
        parts.append(f"{int(ai_patents)} AI-related ({ai_ratio:.0%})")

    patent_fact = facts["total_patents"]

    return SignalExtraction(
        signal_name="innovation",
        signal_value=total_patents,
        signal_confidence=patent_fact.confidence,
        source_facts=source_facts,
        calculation_method="direct",
        calculation_formula="total_patents with ai_ratio annotation",
        reasoning=f"Patent portfolio: {', '.join(parts)}",
        why_it_matters="Patent activity indicates R&D investment and competitive moat",
    )


def _signal_ai_maturity(facts: dict[str, AggregatedFact]) -> SignalExtraction | None:
    """AI maturity signal from AI assessment facts."""
    ai_score = _get_numeric(facts, "ai_score")
    ai_strength = facts.get("ai_signal_strength")
    ai_positions = _get_numeric(facts, "ai_related_positions")

    if ai_score is None and ai_strength is None:
        return None

    source_facts = []
    parts = []
    confidence = 0.5

    if ai_score is not None:
        source_facts.append("ai_score")
        parts.append(f"AI score: {int(ai_score)}/10")
        confidence = facts["ai_score"].confidence

    if ai_strength is not None:
        source_facts.append("ai_signal_strength")
        parts.append(f"Signal: {ai_strength.value}")

    if ai_positions is not None:
        source_facts.append("ai_related_positions")
        parts.append(f"{int(ai_positions)} AI job postings")

    value = ai_score if ai_score is not None else ai_strength.value

    return SignalExtraction(
        signal_name="ai_maturity",
        signal_value=value,
        signal_confidence=confidence,
        source_facts=source_facts,
        calculation_method="composite",
        calculation_formula="ai_score preferred, ai_signal_strength fallback",
        reasoning=f"AI maturity: {', '.join(parts)}",
        why_it_matters="AI adoption level drives competitive threat assessment",
    )


def _signal_hiring_velocity(facts: dict[str, AggregatedFact]) -> SignalExtraction | None:
    """Hiring velocity signal from employment growth metrics."""
    growth_pct = _get_numeric(facts, "employee_growth_pct")
    open_positions = _get_numeric(facts, "open_positions")

    if growth_pct is None and open_positions is None:
        return None

    source_facts = []
    parts = []
    confidence_values = []

    if growth_pct is not None:
        source_facts.append("employee_growth_pct")
        parts.append(f"{growth_pct:.1f}% headcount growth")
        confidence_values.append(facts["employee_growth_pct"].confidence)

    if open_positions is not None:
        source_facts.append("open_positions")
        parts.append(f"{int(open_positions)} open positions")
        confidence_values.append(facts["open_positions"].confidence)

    value = growth_pct if growth_pct is not None else open_positions
    avg_confidence = sum(confidence_values) / len(confidence_values)

    return SignalExtraction(
        signal_name="hiring_velocity",
        signal_value=value,
        signal_confidence=round(avg_confidence, 3),
        source_facts=source_facts,
        calculation_method="composite",
        calculation_formula="employee_growth_pct preferred, open_positions fallback",
        reasoning=f"Hiring velocity: {', '.join(parts)}",
        why_it_matters="Hiring activity signals growth trajectory and investment in capabilities",
    )


def _signal_market_sentiment(facts: dict[str, AggregatedFact]) -> SignalExtraction | None:
    """Market sentiment signal from news coverage."""
    sentiment = _get_numeric(facts, "sentiment_score")
    article_count = _get_numeric(facts, "article_count")
    positive_count = _get_numeric(facts, "positive_article_count")
    negative_count = _get_numeric(facts, "negative_article_count")

    if sentiment is None and article_count is None and positive_count is None:
        return None

    source_facts = []
    parts = []
    confidence = 0.4

    if sentiment is not None:
        source_facts.append("sentiment_score")
        parts.append(f"sentiment {sentiment:.2f}")
        confidence = facts["sentiment_score"].confidence

    if article_count is not None:
        source_facts.append("article_count")
        parts.append(f"{int(article_count)} articles")

    if positive_count is not None:
        source_facts.append("positive_article_count")
        parts.append(f"{int(positive_count)} positive")

    if negative_count is not None:
        source_facts.append("negative_article_count")
        parts.append(f"{int(negative_count)} negative")

    # Derive sentiment from article polarity when no explicit score
    if sentiment is None and positive_count is not None and negative_count is not None:
        total = (positive_count + negative_count) or 1
        sentiment = (positive_count - negative_count) / total

    value = sentiment if sentiment is not None else 0.0

    return SignalExtraction(
        signal_name="market_sentiment",
        signal_value=value,
        signal_confidence=confidence,
        source_facts=source_facts,
        calculation_method="direct" if _get_numeric(facts, "sentiment_score") is not None else "derived",
        calculation_formula="sentiment_score direct, or (positive - negative) / total from article counts",
        reasoning=f"Market sentiment: {', '.join(parts)}",
        why_it_matters="Press sentiment reflects market perception and brand strength",
    )


def _signal_funding(facts: dict[str, AggregatedFact]) -> SignalExtraction | None:
    """Funding signal from investment data."""
    total_raised = _get_numeric(facts, "total_funding_raised")
    if total_raised is None:
        return None

    funding_fact = facts["total_funding_raised"]
    source_facts = ["total_funding_raised"]
    parts = [f"${total_raised:,.0f} total raised"]

    rounds = _get_numeric(facts, "funding_rounds")
    stage_fact = facts.get("last_round_stage")
    last_round_amount = _get_numeric(facts, "last_round_amount")

    if rounds is not None:
        source_facts.append("funding_rounds")
        parts.append(f"{int(rounds)} rounds")

    if last_round_amount is not None:
        source_facts.append("last_round_amount")
        parts.append(f"${last_round_amount:,.0f} last round")

    if stage_fact is not None:
        source_facts.append("last_round_stage")
        parts.append(f"latest: {stage_fact.value}")

    return SignalExtraction(
        signal_name="funding",
        signal_value=total_raised,
        signal_confidence=funding_fact.confidence,
        source_facts=source_facts,
        calculation_method="direct",
        calculation_formula="total_funding_raised from Crunchbase/news",
        reasoning=f"Funding: {', '.join(parts)}",
        why_it_matters="Funding level indicates runway, investor confidence, and growth potential",
    )


# ---------------------------------------------------------------------------
# STORY-349: New signal extractors for numeric Group A orphaned facts
# ---------------------------------------------------------------------------


def _signal_ebitda(facts: dict[str, AggregatedFact]) -> SignalExtraction | None:
    """EBITDA signal from financial facts."""
    ebitda = _get_numeric(facts, "ebitda")
    if ebitda is None:
        return None
    fact = facts["ebitda"]
    return SignalExtraction(
        signal_name="ebitda",
        signal_value=ebitda,
        signal_confidence=fact.confidence,
        source_facts=["ebitda"],
        calculation_method="direct",
        calculation_formula="ebitda from highest-confidence source",
        reasoning=f"EBITDA of {ebitda:,.0f} from {len(fact.sources_used)} source(s)",
        why_it_matters="EBITDA indicates operating profitability before capital structure effects",
    )


def _signal_net_income(facts: dict[str, AggregatedFact]) -> SignalExtraction | None:
    """Net income signal from financial facts."""
    net_income = _get_numeric(facts, "net_income")
    if net_income is None:
        return None
    fact = facts["net_income"]
    return SignalExtraction(
        signal_name="net_income",
        signal_value=net_income,
        signal_confidence=fact.confidence,
        source_facts=["net_income"],
        calculation_method="direct",
        calculation_formula="net_income from highest-confidence source",
        reasoning=f"Net income of {net_income:,.0f} from {len(fact.sources_used)} source(s)",
        why_it_matters="Net income is the bottom-line profitability after all expenses and taxes",
    )


def _signal_pe_ratio(facts: dict[str, AggregatedFact]) -> SignalExtraction | None:
    """Price-to-earnings ratio signal from market data."""
    pe = _get_numeric(facts, "pe_ratio")
    if pe is None:
        return None
    fact = facts["pe_ratio"]
    return SignalExtraction(
        signal_name="pe_ratio",
        signal_value=pe,
        signal_confidence=fact.confidence,
        source_facts=["pe_ratio"],
        calculation_method="direct",
        calculation_formula="pe_ratio from market data",
        reasoning=f"P/E ratio of {pe:.1f}x",
        why_it_matters="P/E ratio reflects market expectations of earnings growth",
    )


def _signal_current_price(facts: dict[str, AggregatedFact]) -> SignalExtraction | None:
    """Current stock price signal from market data."""
    price = _get_numeric(facts, "current_price")
    if price is None:
        return None
    fact = facts["current_price"]
    return SignalExtraction(
        signal_name="current_price",
        signal_value=price,
        signal_confidence=fact.confidence,
        source_facts=["current_price"],
        calculation_method="direct",
        calculation_formula="current_price from market data",
        reasoning=f"Current price of {price:.2f}",
        why_it_matters="Current stock price is a real-time market valuation signal",
    )


def _signal_eps_ttm(facts: dict[str, AggregatedFact]) -> SignalExtraction | None:
    """Earnings per share (trailing twelve months) signal."""
    eps = _get_numeric(facts, "eps_ttm")
    if eps is None:
        return None
    fact = facts["eps_ttm"]
    return SignalExtraction(
        signal_name="eps_ttm",
        signal_value=eps,
        signal_confidence=fact.confidence,
        source_facts=["eps_ttm"],
        calculation_method="direct",
        calculation_formula="eps_ttm from financial data",
        reasoning=f"EPS (TTM) of {eps:.2f}",
        why_it_matters="Trailing EPS captures per-share profitability over the last year",
    )


# ---------------------------------------------------------------------------
# All signal extractors
# ---------------------------------------------------------------------------

_SIGNAL_EXTRACTORS = [
    _signal_revenue_level,
    _signal_growth_rate,
    _signal_profitability,
    _signal_company_size,
    _signal_valuation,
    _signal_innovation,
    _signal_ai_maturity,
    _signal_hiring_velocity,
    _signal_market_sentiment,
    _signal_funding,
    # STORY-349: new extractors for Group A numeric orphaned facts
    _signal_ebitda,
    _signal_net_income,
    _signal_pe_ratio,
    _signal_current_price,
    _signal_eps_ttm,
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def extract_signals(
    aggregated: AggregatedDataRecord,
    batch_id: str | None = None,
) -> SignalExtractionRecord:
    """Extract business signals from aggregated facts.

    Parameters
    ----------
    aggregated:
        The aggregated fact record for one company.
    batch_id:
        Optional batch ID override (defaults to the aggregated record's).

    Returns
    -------
    SignalExtractionRecord with all extracted signals.
    """
    facts_by_type: dict[str, AggregatedFact] = {f.fact_type: f for f in aggregated.facts}

    signals: list[SignalExtraction] = []
    for extractor in _SIGNAL_EXTRACTORS:
        try:
            signal = extractor(facts_by_type)
            if signal is not None:
                signals.append(signal)
        except Exception as exc:
            logger.warning(
                "Signal extractor {} failed for {}: {}",
                extractor.__name__,
                aggregated.company_id,
                exc,
            )

    record = SignalExtractionRecord(
        company_id=aggregated.company_id,
        gathering_batch_id=batch_id or aggregated.gathering_batch_id,
        timestamp=datetime.now(timezone.utc),
        signals=signals,
    )

    logger.info(
        "Extracted {} signals for {} from {} facts",
        len(signals),
        aggregated.company_id,
        len(aggregated.facts),
    )

    return record
