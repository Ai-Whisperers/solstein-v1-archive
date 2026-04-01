"""Unified LinkedIn adapter for Solstein.

Converts LinkedIn functionality from additional_sources to a unified adapter.
Note: LinkedIn has no official API, so we use hiring signals from news.

Confidence: 0.60
Authority: LINKEDIN
"""

from datetime import datetime
from typing import Any

from loguru import logger

from solstein.adapters.logging import log_adapter_error
from solstein.domain.discovery import DiscoveryCandidate  # STORY-246
from solstein.domain.models import RawDataSource
from solstein.infrastructure.conflict_resolution import SourceAuthority
from solstein.infrastructure.refresh import BaseRefreshConnector


class LinkedInUnifiedAdapter(BaseRefreshConnector):
    """Unified LinkedIn adapter implementing the full protocol.

    Fetches hiring and employment signals from news sources.
    LinkedIn has strict anti-scraping, so we use news as proxy.

    Confidence: 0.60 (lower due to indirect sourcing)
    Authority: LINKEDIN
    """

    def __init__(self, db_manager=None, news_api_key: str | None = None):
        super().__init__(
            source_name="linkedin_unified",
            source_type="linkedin",
            db_manager=db_manager,
            confidence=0.60,
        )
        self.news_api_key = news_api_key

    def _get_hiring_signals(self, company_name: str) -> dict[str, Any]:
        """Get hiring signals from news."""
        try:
            from solstein.data.additional_sources import AdditionalDataSources

            additional = AdditionalDataSources(news_api_key=self.news_api_key)
            news = additional.get_news(company_name, days_back=90)

            ai_related = 0
            total_hiring_mentions = 0
            recent_hires = []

            for article in news.articles:
                title = article.title.lower()
                if any(w in title for w in ["hiring", "jobs", "recruit", "expansion", "growing"]):
                    total_hiring_mentions += 1
                    if any(w in title for w in ["ai", "engineer", "developer", "data", "ml"]):
                        ai_related += 1
                    recent_hires.append(
                        {
                            "title": article.title,
                            "date": article.published_at,
                            "source": article.source,
                        }
                    )

            return {
                "ai_related_positions": ai_related,
                "hiring_mentions": total_hiring_mentions,
                "recent_hires": recent_hires[:10],
                "sentiment": news.sentiment_score,
            }
        except Exception as e:
            log_adapter_error(
                component="LinkedInUnifiedSource",
                operation="_get_hiring_signals",
                error=e,
                entity_name=company_name,
                level="warning",
            )
            return {
                "ai_related_positions": None,
                "hiring_mentions": 0,
                "recent_hires": [],
                "sentiment": None,
            }

    def discover(
        self,
        market: str,
        seed_company: str,
        max_results: int = 50,
        extra_keywords: list[str] | None = None,
    ) -> list[DiscoveryCandidate]:
        """Discover companies via hiring signals."""
        logger.info(f"Discovering companies hiring in {market}")

        # Hiring discovery has limited value
        return []

    def enrich(
        self,
        company_id: str,
        company_name: str,
        ticker: str | None = None,
        website: str | None = None,
    ) -> RawDataSource:
        """Enrich company with LinkedIn/hiring data."""
        logger.info(f"Enriching {company_name} with LinkedIn data")

        signals = self._get_hiring_signals(company_name)

        return RawDataSource(
            source_name=self.source_name,
            source_type=self.source_type,
            retrieval_timestamp=datetime.now(),
            raw_content=signals,
            metadata={
                "data_source": "news_proxy",
                "has_hiring_signals": signals["hiring_mentions"] > 0,
            },
        )

    async def fetch_facts(
        self,
        company_ids: list[str],
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch LinkedIn/hiring facts for companies."""
        facts = []

        for company_name in company_ids:
            signals = self._get_hiring_signals(company_name)

            if signals["hiring_mentions"] > 0:
                facts.append(
                    {
                        "company_id": company_name,
                        "fact_type": "hiring_signals",
                        "value": signals,
                        "confidence": self.confidence,
                        "extracted_at": datetime.now(),
                        "source": self.source_name,
                    }
                )

        return facts

    def get_confidence(self) -> float:
        return 0.60

    def get_authority(self) -> SourceAuthority:
        return SourceAuthority.LINKEDIN

    def supports_incremental(self) -> bool:
        return True

    def supports_discovery(self) -> bool:
        return False
