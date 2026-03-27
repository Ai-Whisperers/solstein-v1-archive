"""Additional data sources package.

EPIC-021: Modularized from monolithic 769-line additional_sources.py file.
"""

from __future__ import annotations

# Sources
from .funding import FundingSource
from .linkedin import LinkedInSource

# Models
from .models import (
    FundingData,
    LinkedInData,
    NewsArticle,
    PatentData,
    PressCoverage,
    ProductInfo,
)
from .news import NewsSource
from .patents import PatentSource
from .web import WebSource


# Backward compatibility - AdditionalDataSources orchestrates all sources
class AdditionalDataSources:
    """
    Additional data sources for enhanced company research.

    This is a compatibility wrapper that delegates to individual source modules.
    New code should use the specific source classes directly.
    """

    def __init__(
        self,
        news_api_key: str | None = None,
        crunchbase_key: str | None = None,
        patentsview_api_key: str | None = None,
    ):
        self.news_source = NewsSource(api_key=news_api_key)
        self.funding_source = FundingSource(api_key=crunchbase_key)
        self.patent_source = PatentSource(api_key=patentsview_api_key)
        self.web_source = WebSource()
        self.linkedin_source = LinkedInSource()

    def get_news(self, company_name: str, days_back: int = 30) -> PressCoverage:
        """Get news coverage for a company."""
        return self.news_source.get_news(company_name, days_back)

    async def get_funding_data(self, company_name: str) -> FundingData:
        """Get funding data."""
        return await self.funding_source.get_funding_data(company_name)

    async def get_patent_data(self, company_name: str) -> PatentData:
        """Get patent data."""
        return await self.patent_source.get_patent_data(company_name)

    async def scrape_company_website(self, company_name: str, website: str) -> ProductInfo:
        """Scrape company website for product information."""
        return await self.web_source.scrape_company_website(company_name, website)

    def get_linkedin_data(self, company_name: str) -> LinkedInData:
        """Get LinkedIn hiring data."""
        return self.linkedin_source.get_linkedin_data(company_name)


__all__ = [
    # Models
    "FundingData",
    "LinkedInData",
    "NewsArticle",
    "PatentData",
    "PressCoverage",
    "ProductInfo",
    # Sources
    "AdditionalDataSources",
    "FundingSource",
    "LinkedInSource",
    "NewsSource",
    "PatentSource",
    "WebSource",
]
