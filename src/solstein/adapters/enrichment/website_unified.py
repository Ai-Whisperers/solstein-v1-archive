"""Unified Website adapter for Solstein.

Converts website scraping functionality from additional_sources
to a unified adapter implementing the full UnifiedDataSource protocol.

Extracts product info, tech stack, and company details from websites.
"""

from datetime import datetime
from typing import Any

import requests
from loguru import logger

from solstein.domain.models import RawDataSource
from solstein.infrastructure.conflict_resolution import SourceAuthority
from solstein.infrastructure.database import DatabaseManager
from solstein.infrastructure.database import db_manager as default_db_manager
from solstein.infrastructure.refresh import BaseRefreshConnector
from solstein.research.discovery import DiscoveryCandidate


class WebsiteUnifiedAdapter(BaseRefreshConnector):
    """Unified Website adapter implementing the full protocol.

    Scrapes company websites for product information and tech stack.
    Be respectful of robots.txt and rate limits.

    Confidence: 0.70
    Authority: WEBSITE
    """

    def __init__(self, db_manager: DatabaseManager | None = None):
        super().__init__(
            source_name="website_unified",
            source_type="website",
            db_manager=db_manager or default_db_manager,
            confidence=0.70,
        )

    def _scrape_website(self, website: str) -> dict[str, Any]:
        """Scrape company website for product/tech info."""
        try:
            if not website.startswith(("http://", "https://")):
                website = f"https://{website}"

            response = requests.get(
                website,
                timeout=10,
                headers={"User-Agent": "Mozilla/5.0 (compatible; SolsteinBot/1.0)"},
            )
            response.raise_for_status()

            html = response.text.lower()

            product_keywords = [
                "software",
                "platform",
                "solution",
                "service",
                "product",
                "app",
                "application",
                "tool",
                "system",
                "api",
                "cloud",
                "saas",
                "enterprise",
                "analytics",
                "ai",
                "ml",
                "machine learning",
                "automation",
                "digital",
                "mobile",
                "web",
                "dashboard",
            ]

            tech_keywords = [
                "python",
                "java",
                "javascript",
                "typescript",
                "react",
                "angular",
                "vue",
                "node",
                "aws",
                "azure",
                "gcp",
                "kubernetes",
                "docker",
                "sql",
                "postgresql",
                "mongodb",
                "redis",
                "graphql",
                "rest",
                "microservices",
                "microservice",
                "serverless",
                "lambda",
            ]

            products = [kw for kw in product_keywords if kw in html]
            tech_stack = [kw for kw in tech_keywords if kw in html]

            return {
                "main_products": products[:10],
                "tech_stack": tech_stack[:10],
                "product_count": len(products),
                "tech_count": len(tech_stack),
            }

        except Exception as e:
            logger.error(f"Error scraping {website}: {e}")
            return {
                "main_products": [],
                "tech_stack": [],
                "product_count": 0,
                "tech_count": 0,
            }

    def discover(
        self,
        market: str,
        seed_company: str,
        max_results: int = 50,
        extra_keywords: list[str] | None = None,
    ) -> list[DiscoveryCandidate]:
        """Website adapter does not support discovery."""
        return []

    def enrich(
        self,
        company_id: str,
        company_name: str,
        ticker: str | None = None,
        website: str | None = None,
    ) -> RawDataSource:
        """Enrich company with website data."""
        logger.info(f"Enriching {company_name} with website data")

        if not website:
            # Try to guess website from company name
            website = f"www.{company_name.lower().replace(' ', '')}.com"

        data = self._scrape_website(website)

        return RawDataSource(
            source_name=self.source_name,
            source_type=self.source_type,
            retrieval_timestamp=datetime.now(),
            raw_content=data,
            metadata={
                "website": website,
                "scraped": data["product_count"] > 0 or data["tech_count"] > 0,
            },
        )

    async def fetch_facts(
        self,
        company_ids: list[str],
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch website facts for companies.

        Note: This requires website URLs, not just company names.
        """
        import asyncio

        facts: list[dict[str, Any]] = []

        for company_name in company_ids:
            website = f"www.{company_name.lower().replace(' ', '')}.com"
            data = await asyncio.to_thread(self._scrape_website, website)

            if data["product_count"] > 0:
                facts.append(
                    {
                        "company_id": company_name,
                        "fact_type": "website_info",
                        "value": data,
                        "confidence": self.confidence,
                        "extracted_at": datetime.now(),
                        "source": self.source_name,
                    }
                )

        return facts

    def get_confidence(self) -> float:
        return 0.70

    def get_authority(self) -> SourceAuthority:
        return SourceAuthority.WEBSITE

    def supports_incremental(self) -> bool:
        return True

    def supports_discovery(self) -> bool:
        return False
