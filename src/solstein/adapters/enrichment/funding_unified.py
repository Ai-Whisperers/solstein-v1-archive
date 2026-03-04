"""Unified Funding adapter for Solstein.

Converts funding functionality from additional_sources to a unified adapter
implementing the full UnifiedDataSource protocol.

Uses Crunchbase API when available, falls back to public sources.
"""

from datetime import datetime
from typing import Any

import requests
from loguru import logger

from solstein.domain.models import RawDataSource
from solstein.infrastructure.conflict_resolution import SourceAuthority
from solstein.infrastructure.refresh import BaseRefreshConnector
from solstein.research.discovery import DiscoveryCandidate


class FundingUnifiedAdapter(BaseRefreshConnector):
    """Unified Funding adapter implementing the full protocol.

    Fetches funding and investment data for companies.
    Uses Crunchbase API or public news sources.

    Confidence: 0.65
    Authority: FUNDING
    """

    def __init__(self, db_manager=None, crunchbase_api_key: str | None = None):
        super().__init__(
            source_name="funding_unified",
            source_type="funding",
            db_manager=db_manager,
            confidence=0.65,
        )
        self.crunchbase_api_key = crunchbase_api_key

    def _get_crunchbase_data(self, company_name: str) -> dict[str, Any] | None:
        """Get funding data from Crunchbase API."""
        if not self.crunchbase_api_key:
            return None

        url = f"https://api.crunchbase.com/v4/organizations/{company_name}"
        headers = {"Authorization": f"Bearer {self.crunchbase_api_key}"}

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                props = data.get("properties", {})
                return {
                    "total_raised": props.get("total_funding"),
                    "last_round_amount": props.get("last_funding_amount"),
                    "last_round_date": props.get("last_funded_at"),
                    "last_round_stage": props.get("last_funding_stage"),
                    "last_round_valuation": props.get("valuation"),
                    "num_rounds": props.get("funding_rounds", 0),
                }
        except Exception as e:
            logger.warning("Crunchbase API error", error=str(e))

        return None

    def _get_public_funding_data(self, company_name: str) -> list[dict[str, Any]]:
        """Get funding news from public sources."""
        try:
            from solstein.data.additional_sources import AdditionalDataSources

            additional = AdditionalDataSources()
            news = additional.get_news(company_name, days_back=180)

            rounds = []
            for article in news.articles:
                title = article.title.lower()
                if any(word in title for word in ["funding", "raised", "series", "investment"]):
                    rounds.append(
                        {
                            "title": article.title,
                            "date": article.published_at,
                            "source": article.source,
                        }
                    )

            return rounds
        except Exception as e:
            logger.warning("Public funding search error", error=str(e))
            return []

    def discover(
        self,
        market: str,
        seed_company: str,
        max_results: int = 50,
        extra_keywords: list[str] | None = None,
    ) -> list[DiscoveryCandidate]:
        """Discover recently funded companies in market."""
        logger.info(f"Discovering funded companies in {market}")

        query = f"{market} funding raised investment"
        if extra_keywords:
            query += " " + " ".join(extra_keywords)

        rounds = self._get_public_funding_data(query)

        candidates = []
        for funding_news in rounds[:max_results]:
            candidate = DiscoveryCandidate(
                name=funding_news.get("title", "").split(":")[0][:100],
                source_url="",
                source_type="funding",
                confidence=0.60,
                discovery_metadata={
                    "funding_news": funding_news.get("title", ""),
                    "date": funding_news.get("date"),
                    "market": market,
                },
            )
            candidates.append(candidate)

        return candidates

    def enrich(
        self,
        company_id: str,
        company_name: str,
        ticker: str | None = None,
        website: str | None = None,
    ) -> RawDataSource:
        """Enrich company with funding data."""
        logger.info(f"Enriching {company_name} with funding data")

        # Try Crunchbase first
        crunchbase_data = self._get_crunchbase_data(company_name)

        # Get public funding news
        funding_news = self._get_public_funding_data(company_name)

        data = {
            "has_crunchbase_data": crunchbase_data is not None,
            "funding_news": funding_news,
            "news_count": len(funding_news),
        }

        if crunchbase_data:
            data.update(crunchbase_data)

        return RawDataSource(
            source_name=self.source_name,
            source_type=self.source_type,
            company_id=company_id,
            fetch_timestamp=datetime.now(),
            data=data,
            metadata={
                "source": "crunchbase" if crunchbase_data else "public_news",
                "has_api_data": crunchbase_data is not None,
            },
        )

    async def fetch_facts(
        self,
        company_ids: list[str],
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch funding facts for companies."""
        facts = []

        for company_name in company_ids:
            crunchbase_data = self._get_crunchbase_data(company_name)

            if crunchbase_data:
                facts.append(
                    {
                        "company_id": company_name,
                        "fact_type": "funding_summary",
                        "value": crunchbase_data,
                        "confidence": self.confidence,
                        "extracted_at": datetime.now(),
                        "source": self.source_name,
                    }
                )

        return facts

    def get_confidence(self) -> float:
        return 0.65

    def get_authority(self) -> SourceAuthority:
        return SourceAuthority.FUNDING

    def supports_incremental(self) -> bool:
        return True

    def supports_discovery(self) -> bool:
        return True
