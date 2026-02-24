"""Enrichment adapter wrapping AdditionalDataSources.get_news().

Fetches press coverage and sentiment analysis for a company via
NewsAPI (primary) or Google web search (fallback).
"""

from __future__ import annotations

from datetime import UTC, datetime

from solstein.domain.models import DataSourceType, RawDataSource


class NewsEnrichment:
    """Wraps ``AdditionalDataSources.get_news()`` as an EnrichmentSource."""

    def __init__(self, news_api_key: str | None = None):
        self._news_api_key = news_api_key

    @property
    def source_name(self) -> str:
        return "news"

    @property
    def source_type(self) -> DataSourceType:
        if self._news_api_key:
            return DataSourceType.NEWSAPI
        return DataSourceType.NEWS

    def enrich(
        self,
        company_id: str,
        company_name: str,
        ticker: str | None = None,
        website: str | None = None,
    ) -> RawDataSource:
        from solstein.data.additional_sources import AdditionalDataSources

        client = AdditionalDataSources(news_api_key=self._news_api_key)
        coverage = client.get_news(company_name, days_back=30)

        return RawDataSource(
            source_type=self.source_type,
            source_name="NewsAPI" if self._news_api_key else "Google News Search",
            raw_content=coverage.model_dump(mode="json"),
            url=None,
            retrieval_timestamp=datetime.now(UTC),
            confidence=0.6 if self._news_api_key else 0.4,
            relevance_score=0.7,
            metadata={
                "total_articles": coverage.total_articles,
                "sentiment_score": coverage.sentiment_score,
            },
            extraction_method="newsapi" if self._news_api_key else "web_scrape",
        )
