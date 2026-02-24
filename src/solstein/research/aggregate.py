"""Default fact aggregator — cross-references multiple raw sources into verified facts.

Takes a RawDataRecord (multiple RawDataSource objects from different
enrichment adapters) and produces an AggregatedDataRecord with
deduplicated facts, agreement percentages, and contradiction tracking.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from loguru import logger

from solstein.domain.models import (
    AggregatedDataRecord,
    AggregatedFact,
    DataSourceType,
    RawDataRecord,
    RawDataSource,
)

# Desired fact types for data completeness calculation
_DESIRED_FACTS = frozenset({
    "revenue",
    "employee_count",
    "market_cap",
    "profit_margin",
    "revenue_growth",
    "total_patents",
    "total_funding_raised",
    "description",
    "industry",
    "headquarters",
})

# Numeric fact types where cross-source agreement is meaningful
_NUMERIC_FACT_TYPES = frozenset({
    "revenue",
    "revenue_growth",
    "employee_count",
    "profit_margin",
    "market_cap",
    "ebitda",
    "net_income",
    "pe_ratio",
    "current_price",
    "eps_ttm",
    "total_funding_raised",
    "last_round_amount",
    "total_patents",
    "ai_related_patents",
    "sentiment_score",
    "open_positions",
    "employee_growth_pct",
    "ai_related_positions",
    "ai_score",
    "funding_rounds",
    "founded_year",
    "article_count",
})

# Threshold for numeric agreement (within this fraction = agree)
_AGREEMENT_TOLERANCE = 0.10  # 10%
# Threshold for contradiction (beyond this fraction = contradiction)
_CONTRADICTION_TOLERANCE = 0.25  # 25%


# ---------------------------------------------------------------------------
# Internal types
# ---------------------------------------------------------------------------


@dataclass
class _FactObservation:
    """A single observation of a fact from one source."""

    value: Any
    source_name: str
    source_confidence: float
    url: str | None


# ---------------------------------------------------------------------------
# Per-source-type fact extractors
# ---------------------------------------------------------------------------


def _extract_facts_from_source(source: RawDataSource) -> list[tuple[str, Any]]:
    """Extract (fact_type, value) pairs from a single RawDataSource."""
    content = source.raw_content
    if isinstance(content, str):
        return []

    if isinstance(content, list):
        # e.g., WebSearchNewsEnrichment returns a list of articles
        return [("article_count", len(content))]

    if not isinstance(content, dict):
        return []

    st = source.source_type
    facts: list[tuple[str, Any]] = []

    if st == DataSourceType.YAHOO_FINANCE:
        facts.extend(_extract_yahoo_finance(content))
    elif st in (DataSourceType.NEWSAPI, DataSourceType.NEWS):
        facts.extend(_extract_news(content))
    elif st == DataSourceType.EXA_SEARCH:
        facts.extend(_extract_exa_search(content))
    elif st == DataSourceType.CRUNCHBASE:
        facts.extend(_extract_crunchbase(content))
    elif st in (DataSourceType.PATENTS, DataSourceType.USPTO, DataSourceType.GOOGLE_PATENTS):
        facts.extend(_extract_patents(content))
    elif st == DataSourceType.LINKEDIN:
        facts.extend(_extract_linkedin(content))
    elif st == DataSourceType.WEBSITE:
        facts.extend(_extract_website(content))

    return facts


def _extract_yahoo_finance(content: dict[str, Any]) -> list[tuple[str, Any]]:
    """Extract facts from CompanyResearch or GlobalMarketEnrichment dicts."""
    facts: list[tuple[str, Any]] = []

    # -- CompanyResearch nested financials --
    fin = content.get("financials")
    if isinstance(fin, dict):
        for key, fact_type in [
            ("revenue", "revenue"),
            ("revenue_growth_yoy", "revenue_growth"),
            ("profit_margin", "profit_margin"),
            ("ebitda", "ebitda"),
            ("net_income", "net_income"),
        ]:
            if fin.get(key) is not None:
                facts.append((fact_type, fin[key]))

    # -- Top-level numeric fields (CompanyResearch + GlobalMarket) --
    for key, fact_type in [
        ("market_cap", "market_cap"),
        ("pe_ratio", "pe_ratio"),
        ("current_price", "current_price"),
        ("eps_ttm", "eps_ttm"),
        ("employees", "employee_count"),
        ("founded", "founded_year"),
    ]:
        if content.get(key) is not None:
            facts.append((fact_type, content[key]))

    # GlobalMarket has top-level revenue and market_cap
    if "source_currency" in content:
        if content.get("revenue") is not None:
            facts.append(("revenue", content["revenue"]))
        # market_cap already handled above

    # -- String facts --
    for key, fact_type in [
        ("description", "description"),
        ("headquarters", "headquarters"),
        ("website", "website"),
        ("name", "name"),
        ("exchange", "exchange"),
    ]:
        if content.get(key) is not None:
            facts.append((fact_type, content[key]))

    # -- Growth signals --
    growth = content.get("growth")
    if isinstance(growth, dict):
        for key, fact_type in [
            ("employee_count", "employee_count"),
            ("employee_growth", "employee_growth_pct"),
            ("job_postings_count", "open_positions"),
            ("ai_related_jobs", "ai_related_positions"),
        ]:
            if growth.get(key) is not None:
                facts.append((fact_type, growth[key]))

    # -- AI assessment --
    ai = content.get("ai")
    if isinstance(ai, dict):
        if ai.get("ai_score") is not None:
            facts.append(("ai_score", ai["ai_score"]))
        if ai.get("ai_signal_strength") is not None:
            facts.append(("ai_signal_strength", ai["ai_signal_strength"]))

    # -- Technology --
    tech = content.get("technology")
    if isinstance(tech, dict):
        if tech.get("industry") is not None:
            facts.append(("industry", tech["industry"]))
        if tech.get("sector") is not None:
            facts.append(("sector", tech["sector"]))

    # -- Products --
    products = content.get("products")
    if isinstance(products, dict):
        if products.get("products"):
            facts.append(("products", products["products"]))

    return facts


def _extract_news(content: dict[str, Any]) -> list[tuple[str, Any]]:
    """Extract facts from PressCoverage model dump."""
    facts: list[tuple[str, Any]] = []
    if content.get("total_articles") is not None:
        facts.append(("article_count", content["total_articles"]))
    if content.get("sentiment_score") is not None:
        facts.append(("sentiment_score", content["sentiment_score"]))
    if content.get("positive_count") is not None:
        facts.append(("positive_article_count", content["positive_count"]))
    if content.get("negative_count") is not None:
        facts.append(("negative_article_count", content["negative_count"]))
    return facts


def _extract_exa_search(content: dict[str, Any]) -> list[tuple[str, Any]]:
    """Extract facts from Exa/Google web search results."""
    facts: list[tuple[str, Any]] = []
    if content.get("article_count") is not None:
        facts.append(("article_count", content["article_count"]))
    return facts


def _extract_crunchbase(content: dict[str, Any]) -> list[tuple[str, Any]]:
    """Extract facts from FundingData model dump."""
    facts: list[tuple[str, Any]] = []
    for key, fact_type in [
        ("total_raised", "total_funding_raised"),
        ("last_round_amount", "last_round_amount"),
        ("last_round_valuation", "valuation"),
        ("num_rounds", "funding_rounds"),
    ]:
        if content.get(key) is not None:
            facts.append((fact_type, content[key]))
    if content.get("last_round_stage") is not None:
        facts.append(("last_round_stage", content["last_round_stage"]))
    if content.get("investors"):
        facts.append(("investors", content["investors"]))
    return facts


def _extract_patents(content: dict[str, Any]) -> list[tuple[str, Any]]:
    """Extract facts from PatentResult / PatentData dicts."""
    facts: list[tuple[str, Any]] = []
    if content.get("total_patents") is not None:
        facts.append(("total_patents", content["total_patents"]))
    if content.get("ai_related_patents") is not None:
        facts.append(("ai_related_patents", content["ai_related_patents"]))
    if content.get("top_categories"):
        facts.append(("patent_categories", content["top_categories"]))
    return facts


def _extract_linkedin(content: dict[str, Any]) -> list[tuple[str, Any]]:
    """Extract facts from LinkedInData model dump."""
    facts: list[tuple[str, Any]] = []
    for key, fact_type in [
        ("employee_count", "employee_count"),
        ("employee_growth_pct", "employee_growth_pct"),
        ("open_positions", "open_positions"),
        ("ai_related_positions", "ai_related_positions"),
    ]:
        if content.get(key) is not None:
            facts.append((fact_type, content[key]))
    return facts


def _extract_website(content: dict[str, Any]) -> list[tuple[str, Any]]:
    """Extract facts from ProductInfo model dump."""
    facts: list[tuple[str, Any]] = []
    if content.get("main_products"):
        facts.append(("products", content["main_products"]))
    if content.get("tech_stack"):
        facts.append(("tech_stack", content["tech_stack"]))
    if content.get("pricing_model") is not None:
        facts.append(("pricing_model", content["pricing_model"]))
    if content.get("target_customers"):
        facts.append(("target_customers", content["target_customers"]))
    return facts


# ---------------------------------------------------------------------------
# Aggregation logic
# ---------------------------------------------------------------------------


def _is_numeric(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _aggregate_numeric_fact(
    fact_type: str,
    observations: list[_FactObservation],
) -> AggregatedFact:
    """Aggregate numeric observations with agreement/contradiction detection."""
    numeric_obs = [o for o in observations if _is_numeric(o.value)]
    if not numeric_obs:
        # Fall back to non-numeric aggregation if values aren't actually numeric
        return _aggregate_non_numeric_fact(fact_type, observations)

    # Best value: from highest-confidence source
    best_obs = max(numeric_obs, key=lambda o: o.source_confidence)
    best_value = best_obs.value

    # Agreement: what fraction of sources are within tolerance of best_value
    if len(numeric_obs) == 1:
        agreement = 1.0
    else:
        if best_value == 0:
            agreeing = sum(1 for o in numeric_obs if o.value == 0)
        else:
            agreeing = sum(
                1
                for o in numeric_obs
                if abs(o.value - best_value) / abs(best_value) <= _AGREEMENT_TOLERANCE
            )
        agreement = agreeing / len(numeric_obs)

    # Contradiction detection
    contradictions: list[dict[str, Any]] = []
    if len(numeric_obs) >= 2 and best_value != 0:
        for obs in numeric_obs:
            if obs is best_obs:
                continue
            divergence = abs(obs.value - best_value) / abs(best_value)
            if divergence > _CONTRADICTION_TOLERANCE:
                contradictions.append({
                    "source": obs.source_name,
                    "value": obs.value,
                    "best_value": best_value,
                    "divergence_pct": round(divergence * 100, 1),
                })

    sources_used = [o.url or o.source_name for o in observations]
    credibility = {o.source_name: o.source_confidence for o in observations}

    # Confidence: base from best source, penalized by contradictions
    confidence = best_obs.source_confidence
    if contradictions:
        confidence *= max(0.3, 1.0 - 0.15 * len(contradictions))

    contradiction_notes = None
    if contradictions:
        contradiction_notes = (
            f"{len(contradictions)} source(s) diverge >25% from best value"
        )

    return AggregatedFact(
        fact_type=fact_type,
        value=best_value,
        confidence=round(min(confidence, 1.0), 3),
        sources_used=sources_used,
        source_agreement_percentage=round(agreement, 3),
        source_credibility_scores=credibility,
        contradictions_detected=contradictions,
        contradiction_notes=contradiction_notes,
    )


def _aggregate_non_numeric_fact(
    fact_type: str,
    observations: list[_FactObservation],
) -> AggregatedFact:
    """Aggregate non-numeric observations (strings, lists)."""
    # Best value: from highest-confidence source
    best_obs = max(observations, key=lambda o: o.source_confidence)
    best_value = best_obs.value

    # Agreement for strings: exact match ratio
    if len(observations) == 1:
        agreement = 1.0
    else:
        agreeing = sum(1 for o in observations if o.value == best_value)
        agreement = agreeing / len(observations)

    sources_used = [o.url or o.source_name for o in observations]
    credibility = {o.source_name: o.source_confidence for o in observations}

    return AggregatedFact(
        fact_type=fact_type,
        value=best_value,
        confidence=round(best_obs.source_confidence, 3),
        sources_used=sources_used,
        source_agreement_percentage=round(agreement, 3),
        source_credibility_scores=credibility,
    )


# ---------------------------------------------------------------------------
# DefaultFactAggregator
# ---------------------------------------------------------------------------


class DefaultFactAggregator:
    """Cross-references multiple raw sources into verified, deduplicated facts.

    Implements the ``FactAggregator`` protocol defined in
    ``solstein.adapters.protocols``.
    """

    def aggregate(
        self,
        company_id: str,
        raw_record: RawDataRecord,
    ) -> AggregatedDataRecord:
        """Cross-reference sources and return aggregated facts."""
        # 1. Extract all facts from all sources
        fact_groups: dict[str, list[_FactObservation]] = defaultdict(list)

        for source in raw_record.sources:
            try:
                extracted = _extract_facts_from_source(source)
            except Exception as exc:
                logger.warning(
                    "Fact extraction failed for {} ({}): {}",
                    source.source_name,
                    source.source_type,
                    exc,
                )
                continue

            for fact_type, value in extracted:
                fact_groups[fact_type].append(
                    _FactObservation(
                        value=value,
                        source_name=source.source_name,
                        source_confidence=source.confidence,
                        url=source.url,
                    )
                )

        # 2. Aggregate each fact type
        aggregated_facts: list[AggregatedFact] = []
        for fact_type, observations in sorted(fact_groups.items()):
            if fact_type in _NUMERIC_FACT_TYPES:
                fact = _aggregate_numeric_fact(fact_type, observations)
            else:
                fact = _aggregate_non_numeric_fact(fact_type, observations)
            aggregated_facts.append(fact)

        # 3. Build record
        record = AggregatedDataRecord(
            company_id=company_id,
            gathering_batch_id=raw_record.gathering_batch_id,
            timestamp=datetime.now(UTC),
            facts=aggregated_facts,
        )

        # 4. Quality metrics
        record.update_quality_metrics()
        found_fact_types = {f.fact_type for f in aggregated_facts}
        if _DESIRED_FACTS:
            record.data_completeness_percentage = round(
                len(found_fact_types & _DESIRED_FACTS) / len(_DESIRED_FACTS), 3
            )

        logger.info(
            "Aggregated {} facts for {} ({} sources, {:.0%} completeness)",
            len(aggregated_facts),
            company_id,
            len(raw_record.sources),
            record.data_completeness_percentage,
        )

        return record
