"""Domain-level discovery types and helpers.

STORY-246: Moved DiscoveryCandidate, _slugify, and _catalog_for_market here
from research.discovery to break the circular import between
adapters.discovery.* → research.discovery → adapters.registry → adapters.discovery.*.

These types belong in the domain layer because DiscoveryCandidate is a value
object consumed by both the adapters and research layers.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DiscoveryCandidate:
    company_id: str
    name: str
    market: str
    ticker: str | None
    industry: str
    region: str
    tags: list[str]
    seed_relevance: float
    discovery_reason: str
    source_links: list[str]


def _slugify(name: str) -> str:
    out = []
    for ch in name.lower():
        if ch.isalnum():
            out.append(ch)
        elif out and out[-1] != "-":
            out.append("-")
    slug = "".join(out).strip("-")
    return slug or "unknown-company"


def _catalog_for_market(market: str) -> list[dict[str, object]]:
    """Get company catalog for a given market.

    EPIC-020: Refactored from 429-line function to data-driven approach.
    Catalog data moved to market_catalogs.py module.
    """
    from solstein.research.market_catalogs import get_catalog_for_market

    return get_catalog_for_market(market)
