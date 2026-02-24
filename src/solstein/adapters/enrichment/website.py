"""Enrichment adapter wrapping AdditionalDataSources.scrape_company_website().

Scrapes a company's website for product keywords and tech stack
mentions.  Requires a ``website`` URL to be provided.
"""

from __future__ import annotations

from datetime import UTC, datetime

from solstein.domain.models import DataSourceType, RawDataSource


class WebsiteEnrichment:
    """Wraps ``AdditionalDataSources.scrape_company_website()`` as an EnrichmentSource."""

    @property
    def source_name(self) -> str:
        return "website"

    @property
    def source_type(self) -> DataSourceType:
        return DataSourceType.WEBSITE

    def enrich(
        self,
        company_id: str,
        company_name: str,
        ticker: str | None = None,
        website: str | None = None,
    ) -> RawDataSource:
        if not website:
            raise ValueError(f"WebsiteEnrichment requires a website URL for {company_name}")

        from solstein.data.additional_sources import AdditionalDataSources

        client = AdditionalDataSources()
        info = client.scrape_company_website(company_name, website)

        return RawDataSource(
            source_type=DataSourceType.WEBSITE,
            source_name=f"Website scrape ({website})",
            raw_content=info.model_dump(mode="json"),
            url=website,
            retrieval_timestamp=datetime.now(UTC),
            confidence=0.5,
            relevance_score=0.7,
            metadata={
                "products_found": len(info.main_products),
                "tech_stack_found": len(info.tech_stack),
            },
            extraction_method="web_scrape",
        )
