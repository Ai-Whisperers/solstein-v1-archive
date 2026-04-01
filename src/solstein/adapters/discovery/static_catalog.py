"""Discovery adapter wrapping the hardcoded market catalogs.

This adapter preserves backward compatibility with the existing
``_catalog_for_market()`` function in ``research.discovery`` while
conforming to the ``DiscoverySource`` protocol so it can be composed
with other discovery sources via the registry.

Updated to implement UnifiedDataSource protocol.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from solstein.domain.models import DataSourceType, RawDataSource
from solstein.infrastructure.conflict_resolution import SourceAuthority
from solstein.research.discovery import DiscoveryCandidate, _catalog_for_market, _slugify


class StaticCatalogSource:
    """Wraps ``_catalog_for_market()`` as a DiscoverySource."""

    @property
    def source_name(self) -> str:
        return "static_catalog"

    @property
    def source_type(self) -> DataSourceType:
        return DataSourceType.STATIC_CATALOG

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
            src_links = [str(s) for s in sources_obj] if isinstance(sources_obj, list) else []
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

    def enrich(
        self,
        company_id: str,
        company_name: str,
        ticker: str | None = None,
        website: str | None = None,
    ) -> RawDataSource:
        """Static catalog doesn't support enrichment - returns empty data."""
        return RawDataSource(
            source_type=DataSourceType.STATIC_CATALOG,
            source_name=self.source_name,
            raw_content={"company_id": company_id, "company_name": company_name},
            retrieval_timestamp=datetime.now(tz=timezone.utc),
            confidence=0.5,
        )

    def refresh(
        self,
        company_ids: list[str],
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Static catalog doesn't support refresh - returns empty list."""
        return []

    def get_confidence(self) -> float:
        """Static catalog has moderate confidence."""
        return 0.7

    def get_authority(self) -> SourceAuthority:
        """Static catalog has medium authority."""
        return SourceAuthority.STATIC_CATALOG

    def supports_incremental(self) -> bool:
        """Static catalog doesn't support incremental refresh."""
        return False

    def supports_discovery(self) -> bool:
        """Static catalog supports discovery."""
        return True
