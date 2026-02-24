"""Enrichment adapter wrapping web_search_client.search_company_news().

Searches for recent company news via Exa (primary) or Google Search
(fallback).  No API key strictly required — Exa uses an environment
variable, and Google is a scraping fallback.
"""

from __future__ import annotations

from datetime import datetime, timezone

from solstein.domain.models import DataSourceType, RawDataSource


class WebSearchNewsEnrichment:
    """Wraps ``search_company_news()`` as an EnrichmentSource."""

    @property
    def source_name(self) -> str:
        return "web_search_news"

    @property
    def source_type(self) -> DataSourceType:
        return DataSourceType.EXA_SEARCH

    def enrich(
        self,
        company_id: str,
        company_name: str,
        ticker: str | None = None,
        website: str | None = None,
    ) -> RawDataSource:
        from solstein.data.web_search_client import search_company_news

        articles = search_company_news(company_name, max_results=20)

        return RawDataSource(
            source_type=DataSourceType.EXA_SEARCH,
            source_name="Exa/Google news search",
            raw_content=articles,
            url=None,
            retrieval_timestamp=datetime.now(timezone.utc),
            confidence=0.5,
            relevance_score=0.7,
            metadata={"article_count": len(articles)},
            extraction_method="exa_search",
        )
