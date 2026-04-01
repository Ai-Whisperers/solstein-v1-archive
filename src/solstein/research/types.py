"""Shared types for the research module.

Extracted from discovery.py to break the circular import:
    adapters.registry -> adapters.enrichment.patents_unified -> research.discovery -> adapters.registry

DiscoveryCandidate and _slugify are pure data types with no dependencies,
so they can safely be imported from anywhere without triggering cycles.
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
