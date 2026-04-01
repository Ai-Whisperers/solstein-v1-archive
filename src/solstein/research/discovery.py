from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

from solstein.data.loaders import CompetitorDataLoader

# STORY-246: DiscoveryCandidate, _slugify, _catalog_for_market moved to
# solstein.domain.discovery to break import cycles.  Re-exported here for
# backward compatibility.
from solstein.domain.discovery import (  # noqa: F401
    DiscoveryCandidate,
    _catalog_for_market,
    _slugify,
)

if TYPE_CHECKING:
    from solstein.adapters.registry import SourceRegistry


def _score_candidate(
    candidate: DiscoveryCandidate,
    seed_company: str,
    market: str,
    extra_keywords: list[str] | None = None,
) -> DiscoveryCandidate:
    """Apply relevance scoring to a candidate based on seed/market/keywords."""
    keywords = [k.lower() for k in (extra_keywords or [])]
    seed_tokens = [tok for tok in seed_company.lower().replace("/", " ").split() if tok]
    tags = [t.lower() for t in candidate.tags]

    score = candidate.seed_relevance  # preserve any pre-existing score
    reasons: list[str] = []

    if any(tok in candidate.name.lower() for tok in seed_tokens):
        score += 3.0
        reasons.append("name similarity with seed")

    overlap = len(set(tags) & set(keywords))
    if overlap:
        score += float(overlap)
        reasons.append("keyword tag overlap")

    if "latam" in market.lower() and "latam" in candidate.region.lower():
        score += 1.0
        reasons.append("market region match")

    if any(k in tags for k in ["energy", "bank", "fintech", "payments", "software"]):
        score += 0.5

    candidate.seed_relevance = score
    if reasons:
        candidate.discovery_reason = ", ".join(reasons)
    return candidate


def _deduplicate_candidates(
    candidates: list[DiscoveryCandidate],
) -> list[DiscoveryCandidate]:
    """Deduplicate candidates by company_id, keeping highest relevance."""
    best: dict[str, DiscoveryCandidate] = {}
    for c in candidates:
        existing = best.get(c.company_id)
        if existing is None or c.seed_relevance > existing.seed_relevance:
            best[c.company_id] = c
    return list(best.values())


def discover_companies(
    seed_company: str,
    market: str,
    max_companies: int = 25,
    extra_keywords: list[str] | None = None,
    registry: SourceRegistry | None = None,
) -> list[DiscoveryCandidate]:
    if registry is not None:
        return _discover_via_registry(seed_company, market, max_companies, extra_keywords, registry)
    return _discover_legacy(seed_company, market, max_companies, extra_keywords)


def _discover_via_registry(
    seed_company: str,
    market: str,
    max_companies: int,
    extra_keywords: list[str] | None,
    registry: SourceRegistry,
) -> list[DiscoveryCandidate]:
    """New path: iterate all DiscoverySource adapters from the registry."""
    all_candidates: list[DiscoveryCandidate] = []
    for source in registry.discovery_sources:
        try:
            candidates = source.discover(
                market=market,
                seed_company=seed_company,
                max_results=max_companies * 2,  # over-fetch to allow dedup
                extra_keywords=extra_keywords,
            )
            logger.info(
                "Discovery source '{}' returned {} candidates",
                source.source_name,
                len(candidates),
            )
            all_candidates.extend(candidates)
        except Exception as exc:
            logger.warning(
                "Discovery source '{}' failed: {}",
                source.source_name,
                exc,
            )

    deduped = _deduplicate_candidates(all_candidates)

    # Apply relevance scoring
    for candidate in deduped:
        _score_candidate(candidate, seed_company, market, extra_keywords)

    deduped.sort(key=lambda c: (c.seed_relevance, c.name), reverse=True)
    return deduped[:max_companies]


def _discover_legacy(
    seed_company: str,
    market: str,
    max_companies: int,
    extra_keywords: list[str] | None,
) -> list[DiscoveryCandidate]:
    """Legacy path: hardcoded catalog + CompetitorDataLoader expansion."""
    keywords = [k.lower() for k in (extra_keywords or [])]
    seed_tokens = [tok for tok in seed_company.lower().replace("/", " ").split() if tok]
    catalog = _catalog_for_market(market)

    if (
        "dutch" in market.lower() or "netherlands" in market.lower() or "energy" in market.lower()
    ) and max_companies > len(catalog):
        try:
            loader = CompetitorDataLoader()
            existing = {str(item["name"]).lower() for item in catalog}
            source_primary = "https://github.com/ai-whisperers/solstein/blob/main/data/input/competitor_data.json"
            for company in loader.load_companies():
                if company.name.lower() in existing:
                    continue
                catalog.append(
                    {
                        "name": company.name,
                        "ticker": None,
                        "industry": company.industry,
                        "region": (", ".join(company.geographic_presence) if company.geographic_presence else "NL/EU"),
                        "tags": (company.tech_stack[:3] if company.tech_stack else ["energy", "software"]),
                        "sources": [source_primary],
                    }
                )
                existing.add(company.name.lower())
        except Exception as exc:
            logger.warning(
                "CompetitorDataLoader enrichment failed; proceeding without expansion: {}",
                exc,
            )

    scored: list[DiscoveryCandidate] = []
    for item in catalog:
        name = str(item["name"])
        src_links: list[str] = []
        sources_obj = item.get("sources")
        if isinstance(sources_obj, list):
            src_links = [str(s) for s in sources_obj]
        raw_tags = item.get("tags", [])
        tags_list = raw_tags if isinstance(raw_tags, list) else []
        tags = [str(t).lower() for t in tags_list]
        score = 0.0
        reasons: list[str] = []

        if any(tok in name.lower() for tok in seed_tokens):
            score += 3.0
            reasons.append("name similarity with seed")

        overlap = len(set(tags) & set(keywords))
        if overlap:
            score += float(overlap)
            reasons.append("keyword tag overlap")

        if "latam" in market.lower() and str(item.get("region", "")).lower().find("latam") >= 0:
            score += 1.0
            reasons.append("market region match")

        if any(k in tags for k in ["energy", "bank", "fintech", "payments", "software"]):
            score += 0.5

        candidate = DiscoveryCandidate(
            company_id=_slugify(name),
            name=name,
            market=market,
            ticker=str(item["ticker"]) if item.get("ticker") else None,
            industry=str(item.get("industry", "Unknown")),
            region=str(item.get("region", "Unknown")),
            tags=[str(t) for t in tags_list],
            seed_relevance=score,
            discovery_reason=", ".join(reasons) or "catalog inclusion",
            source_links=src_links,
        )
        scored.append(candidate)

    scored.sort(key=lambda c: (c.seed_relevance, c.name), reverse=True)
    return scored[:max_companies]


async def discover_companies_async(
    seed_company: str,
    market: str,
    max_companies: int = 25,
    extra_keywords: list[str] | None = None,
    registry: SourceRegistry | None = None,
) -> list[DiscoveryCandidate]:
    """Async version of discover_companies.

    Runs the synchronous discovery in a thread pool for non-blocking execution.
    """
    import asyncio

    return await asyncio.to_thread(
        discover_companies,
        seed_company,
        market,
        max_companies,
        extra_keywords,
        registry,
    )
