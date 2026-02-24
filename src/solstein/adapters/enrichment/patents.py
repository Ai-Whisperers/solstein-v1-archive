"""Enrichment adapter wrapping patent_client.search_company_patents().

Searches for company patents via USPTO PEDS (primary), Google Patents,
or DuckDuckGo (fallback).  No API key required.

Note: The underlying patent_client had fabricated count multipliers
(x5 for Google, x3 for DuckDuckGo) which have been fixed to report
actual counts.
"""

from __future__ import annotations

from datetime import timezone, datetime

from solstein.domain.models import DataSourceType, RawDataSource


_SOURCE_TYPE_MAP = {
    "uspto_peds": DataSourceType.USPTO,
    "google_patents": DataSourceType.GOOGLE_PATENTS,
    "duckduckgo": DataSourceType.PATENTS,
    "none": DataSourceType.PATENTS,
}


class PatentEnrichment:
    """Wraps ``search_company_patents()`` as an EnrichmentSource."""

    @property
    def source_name(self) -> str:
        return "patents"

    @property
    def source_type(self) -> DataSourceType:
        return DataSourceType.PATENTS

    def enrich(
        self,
        company_id: str,
        company_name: str,
        ticker: str | None = None,
        website: str | None = None,
    ) -> RawDataSource:
        from solstein.data.patent_client import search_company_patents

        result = search_company_patents(company_name)

        actual_source_type = _SOURCE_TYPE_MAP.get(result.source, DataSourceType.PATENTS)

        confidence = 0.7 if result.source == "uspto_peds" else 0.4

        return RawDataSource(
            source_type=actual_source_type,
            source_name=f"Patent search ({result.source})",
            raw_content={
                "total_patents": result.total_patents,
                "recent_patents": result.recent_patents,
                "ai_related_patents": result.ai_related_patents,
                "top_categories": result.top_categories,
                "source_backend": result.source,
            },
            url=None,
            retrieval_timestamp=datetime.now(timezone.utc),
            confidence=confidence,
            relevance_score=0.6,
            metadata={
                "backend": result.source,
                "total_patents": result.total_patents,
                "ai_related_patents": result.ai_related_patents,
            },
            extraction_method=f"patent_client_{result.source}",
        )
