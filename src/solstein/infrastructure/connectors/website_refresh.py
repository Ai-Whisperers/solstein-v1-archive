"""Website refresh connector for company website data updates.

Uses web scraping to fetch product and tech stack information.
Implements incremental refresh with content-based delta detection.
"""

from datetime import datetime
from typing import Any

from loguru import logger

from solstein.data.additional_sources import AdditionalDataSources
from solstein.infrastructure.conflict_resolution import SourceAuthority
from solstein.infrastructure.refresh import BaseRefreshConnector


class WebsiteRefreshConnector(BaseRefreshConnector):
    """Website refresh connector for company website data.

    Scrapes company websites for:
    - Product/service offerings
    - Technology stack mentions
    - Company descriptions
    - Contact information

    Confidence: 0.84 (high for directly scraped company data)
    """

    def __init__(self, db_manager):
        super().__init__(
            source_name="website",
            source_type="website_data",
            db_manager=db_manager,
            confidence=0.84,
        )
        self.client = AdditionalDataSources()

    async def fetch_facts(
        self,
        company_ids: list[str],
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch website data facts for companies.

        Args:
            company_ids: List of company names (requires website mapping)
            start_date: Not used for website scraping
            end_date: Not used

        Returns:
            List of fact dictionaries with website data
        """
        logger.info(f"Fetching website data for {len(company_ids)} companies")
        facts = []

        # Look up website URLs from company records in the database
        company_website_map: dict[str, str] = {}
        try:
            from sqlalchemy import select
            from solstein.infrastructure.database_models import CompanyRecord

            async with self.db_manager.get_session() as session:
                result = await session.execute(
                    select(CompanyRecord.company_id, CompanyRecord.website).where(
                        CompanyRecord.company_id.in_(company_ids),
                        CompanyRecord.website.isnot(None),
                    )
                )
                for row in result.fetchall():
                    if row[1]:
                        company_website_map[row[0]] = row[1]
        except Exception as e:
            logger.warning(f"Failed to look up company websites from DB: {e}")

        if not company_website_map:
            logger.info("No website URLs found for requested companies, skipping website refresh")
            return facts

        return await self.fetch_facts_with_websites(company_website_map, start_date, end_date)

    async def fetch_facts_with_websites(
        self,
        company_website_map: dict[str, str],
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch website data with explicit website URLs.

        Args:
            company_website_map: Dict mapping company names to website URLs
            start_date: Not used for website scraping
            end_date: Not used

        Returns:
            List of fact dictionaries with website data
        """
        logger.info(f"Fetching website data for {len(company_website_map)} companies")
        facts = []

        for company_name, website in company_website_map.items():
            try:
                info = await self.client.scrape_company_website(company_name, website)

                facts.append(
                    {
                        "company_id": company_name,
                        "fact_type": "website_products",
                        "value": {
                            "main_products": info.main_products,
                            "products_count": len(info.main_products),
                        },
                        "confidence": self.confidence,
                        "extracted_at": datetime.now(),
                        "source": self.source_name,
                        "metadata": {
                            "website": website,
                            "company_name": company_name,
                        },
                    }
                )

                facts.append(
                    {
                        "company_id": company_name,
                        "fact_type": "tech_stack",
                        "value": {
                            "technologies": info.tech_stack,
                            "tech_count": len(info.tech_stack),
                        },
                        "confidence": self.confidence,
                        "extracted_at": datetime.now(),
                        "source": self.source_name,
                        "metadata": {
                            "website": website,
                            "company_name": company_name,
                        },
                    }
                )

            except Exception as e:
                logger.warning(f"Failed to fetch website data for {company_name}: {e}")
                continue

        return facts

    def get_authority(self) -> SourceAuthority:
        """Return Website authority level."""
        return SourceAuthority.WEBSITE

    def supports_incremental(self) -> bool:
        """Website supports incremental refresh via hash comparison."""
        return True
