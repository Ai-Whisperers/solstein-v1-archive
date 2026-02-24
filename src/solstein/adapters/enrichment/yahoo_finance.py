"""Enrichment adapter wrapping CompanyResearcher (yfinance).

This is the most comprehensive single-source enrichment adapter.
It replaces the ad-hoc yfinance usage in ``gather.py`` with a
structured ``RawDataSource`` output.
"""

from __future__ import annotations

from datetime import UTC, datetime

from solstein.domain.models import DataSourceType, RawDataSource


class YahooFinanceEnrichment:
    """Wraps ``CompanyResearcher.research()`` as an EnrichmentSource."""

    @property
    def source_name(self) -> str:
        return "yahoo_finance"

    @property
    def source_type(self) -> DataSourceType:
        return DataSourceType.YAHOO_FINANCE

    def enrich(
        self,
        company_id: str,
        company_name: str,
        ticker: str | None = None,
        website: str | None = None,
    ) -> RawDataSource:
        if not ticker:
            raise ValueError(f"YahooFinanceEnrichment requires a ticker for {company_name}")

        from solstein.data.company_research import CompanyResearcher

        researcher = CompanyResearcher()
        profile = researcher.research(ticker)

        url = f"https://finance.yahoo.com/quote/{ticker}/"

        return RawDataSource(
            source_type=DataSourceType.YAHOO_FINANCE,
            source_name="Yahoo Finance",
            raw_content=profile.model_dump(mode="json"),
            url=url,
            retrieval_timestamp=datetime.now(UTC),
            confidence=0.8,
            relevance_score=0.9,
            metadata={"ticker": ticker, "exchange": profile.exchange},
            extraction_method="yfinance_api",
        )
