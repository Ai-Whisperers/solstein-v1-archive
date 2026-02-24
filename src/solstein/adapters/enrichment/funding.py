"""Enrichment adapter wrapping AdditionalDataSources.get_funding_data().

Fetches funding/investment data via Crunchbase API (if key provided)
or falls back to news-based funding detection.
"""

from __future__ import annotations

from datetime import timezone, datetime

from solstein.domain.models import DataSourceType, RawDataSource


class FundingEnrichment:
    """Wraps ``AdditionalDataSources.get_funding_data()`` as an EnrichmentSource."""

    def __init__(self, crunchbase_api_key: str | None = None, news_api_key: str | None = None):
        self._crunchbase_key = crunchbase_api_key
        self._news_api_key = news_api_key

    @property
    def source_name(self) -> str:
        return "funding"

    @property
    def source_type(self) -> DataSourceType:
        return DataSourceType.CRUNCHBASE

    def enrich(
        self,
        company_id: str,
        company_name: str,
        ticker: str | None = None,
        website: str | None = None,
    ) -> RawDataSource:
        from solstein.data.additional_sources import AdditionalDataSources

        client = AdditionalDataSources(
            crunchbase_key=self._crunchbase_key,
            news_api_key=self._news_api_key,
        )
        funding = client.get_funding_data(company_name)

        return RawDataSource(
            source_type=DataSourceType.CRUNCHBASE,
            source_name="Crunchbase" if self._crunchbase_key else "News-based funding detection",
            raw_content=funding.model_dump(mode="json"),
            url=None,
            retrieval_timestamp=datetime.now(timezone.utc),
            confidence=0.7 if self._crunchbase_key else 0.3,
            relevance_score=0.8,
            metadata={
                "total_raised": funding.total_raised,
                "num_rounds": funding.num_rounds,
            },
            extraction_method="crunchbase_api" if self._crunchbase_key else "news_heuristic",
        )
