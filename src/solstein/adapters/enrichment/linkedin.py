"""Enrichment adapter wrapping AdditionalDataSources.get_linkedin_data().

Returns hiring signals derived from news mentions (no direct LinkedIn
API access).  Data quality is limited — this adapter sets confidence
accordingly.
"""

from __future__ import annotations

from datetime import UTC, datetime

from solstein.domain.models import DataSourceType, RawDataSource


class LinkedInEnrichment:
    """Wraps ``AdditionalDataSources.get_linkedin_data()`` as an EnrichmentSource."""

    def __init__(self, news_api_key: str | None = None):
        self._news_api_key = news_api_key

    @property
    def source_name(self) -> str:
        return "linkedin"

    @property
    def source_type(self) -> DataSourceType:
        return DataSourceType.LINKEDIN

    def enrich(
        self,
        company_id: str,
        company_name: str,
        ticker: str | None = None,
        website: str | None = None,
    ) -> RawDataSource:
        from solstein.data.additional_sources import AdditionalDataSources

        client = AdditionalDataSources(news_api_key=self._news_api_key)
        data = client.get_linkedin_data(company_name)

        return RawDataSource(
            source_type=DataSourceType.LINKEDIN,
            source_name="LinkedIn (news-derived)",
            raw_content=data.model_dump(mode="json"),
            url=None,
            retrieval_timestamp=datetime.now(UTC),
            confidence=0.3,
            relevance_score=0.5,
            metadata={
                "ai_related_positions": data.ai_related_positions,
            },
            extraction_method="news_heuristic",
        )
