"""Discovery adapter wrapping the hardcoded market catalogs.

This adapter preserves backward compatibility with the existing
``_catalog_for_market()`` function in ``research.discovery`` while
conforming to the ``DiscoverySource`` protocol so it can be composed
with other discovery sources via the registry.
"""

from __future__ import annotations

from solstein.research.discovery import DiscoveryCandidate, _catalog_for_market, _slugify


class StaticCatalogSource:
    """Wraps ``_catalog_for_market()`` as a DiscoverySource."""

    @property
    def source_name(self) -> str:
        return "static_catalog"

    def discover(
        self,
        market: str,
        seed_company: str,
        max_results: int = 50,
        extra_keywords: list[str] | None = None,
    ) -> list[DiscoveryCandidate]:
        catalog = _catalog_for_market(market)
        candidates: list[DiscoveryCandidate] = []
        for item in catalog[:max_results]:
            name = str(item["name"])
            raw_tags = item.get("tags", [])
            tags_list = raw_tags if isinstance(raw_tags, list) else []
            sources_obj = item.get("sources")
            src_links = (
                [str(s) for s in sources_obj] if isinstance(sources_obj, list) else []
            )
            candidates.append(
                DiscoveryCandidate(
                    company_id=_slugify(name),
                    name=name,
                    market=market,
                    ticker=str(item["ticker"]) if item.get("ticker") else None,
                    industry=str(item.get("industry", "Unknown")),
                    region=str(item.get("region", "Unknown")),
                    tags=[str(t) for t in tags_list],
                    seed_relevance=0.0,
                    discovery_reason="static catalog",
                    source_links=src_links,
                )
            )
        return candidates
