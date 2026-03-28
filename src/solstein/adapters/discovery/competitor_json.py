"""Discovery adapter wrapping CompetitorDataLoader.

Reads ``data/input/competitor_data.json`` and converts each entry
into a ``DiscoveryCandidate`` so the pipeline can merge them with
candidates from other discovery sources.

Updated to implement UnifiedDataSource protocol.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from loguru import logger

from solstein.adapters.logging import log_adapter_error

from solstein.domain.models import DataSourceType, RawDataSource
from solstein.infrastructure.conflict_resolution import SourceAuthority


class CompetitorJsonSource:
    """Wraps ``CompetitorDataLoader`` as a DiscoverySource."""

    @property
    def source_name(self) -> str:
        return "competitor_json"

    @property
    def source_type(self) -> DataSourceType:
        return DataSourceType.COMPETITOR_JSON

    def discover(
        self,
        market: str,
        seed_company: str,
        max_results: int = 50,
        extra_keywords: list[str] | None = None,
    ) -> list[DiscoveryCandidate]:
        from solstein.research.discovery import DiscoveryCandidate, _slugify

        try:
            from solstein.data.loaders import CompetitorDataLoader

            loader = CompetitorDataLoader()
            companies = loader.load_companies()
        except Exception as exc:
            log_adapter_error(
                component="CompetitorJsonSource",
                operation="discover",
                error=exc,
                entity_name=market,
                level="warning",
            )
            return []

        source_url = "https://github.com/ai-whisperers/solstein/blob/main/data/input/competitor_data.json"
        candidates: list[DiscoveryCandidate] = []
        for company in companies[:max_results]:
            region = ", ".join(company.geographic_presence) if company.geographic_presence else "Unknown"
            tags = company.tech_stack[:3] if company.tech_stack else []
            candidates.append(
                DiscoveryCandidate(
                    company_id=_slugify(company.name),
                    name=company.name,
                    market=market,
                    ticker=None,
                    industry=company.industry,
                    region=region,
                    tags=tags,
                    seed_relevance=0.0,
                    discovery_reason="competitor_data.json",
                    source_links=[source_url],
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
        """Competitor JSON doesn't support enrichment - returns empty data."""
        return RawDataSource(
            source_type=DataSourceType.COMPETITOR_JSON,
            source_name=self.source_name,
            raw_content={"company_id": company_id, "company_name": company_name},
            retrieval_timestamp=datetime.now(),
            confidence=0.5,
        )

    def refresh(
        self,
        company_ids: list[str],
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Competitor JSON doesn't support refresh - returns empty list."""
        return []

    def get_confidence(self) -> float:
        """Competitor JSON has moderate confidence."""
        return 0.7

    def get_authority(self) -> SourceAuthority:
        """Competitor JSON has medium authority."""
        return SourceAuthority.COMPETITOR_JSON

    def supports_incremental(self) -> bool:
        """Competitor JSON doesn't support incremental refresh."""
        return False

    def supports_discovery(self) -> bool:
        """Competitor JSON supports discovery."""
        return True
