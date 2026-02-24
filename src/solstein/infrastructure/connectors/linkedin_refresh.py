"""LinkedIn refresh connector for professional data updates.

Uses news-derived hiring signals (no direct LinkedIn API access).
Implements incremental refresh with hiring signal detection.
"""

from datetime import datetime
from typing import Any

from loguru import logger

from solstein.data.additional_sources import AdditionalDataSources
from solstein.infrastructure.conflict_resolution import SourceAuthority
from solstein.infrastructure.refresh import BaseRefreshConnector


class LinkedInRefreshConnector(BaseRefreshConnector):
    """LinkedIn refresh connector for hiring signals and professional data.

    Fetches hiring signals derived from news mentions:
    - AI-related job postings
    - Hiring momentum indicators
    - Professional growth signals

    Note: No direct LinkedIn API access - data is news-derived.
    Confidence: 0.75 (moderate, limited by news-derived nature)
    """

    def __init__(self, db_manager, news_api_key: str | None = None):
        super().__init__(
            source_name="linkedin",
            source_type="professional_data",
            db_manager=db_manager,
            confidence=0.75,
        )
        self.news_api_key = news_api_key
        self.client = AdditionalDataSources(news_api_key=news_api_key)

    async def fetch_facts(
        self,
        company_ids: list[str],
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch LinkedIn hiring signal facts for companies.

        Args:
            company_ids: List of company names to search for
            start_date: Not used (news-derived data)
            end_date: Not used

        Returns:
            List of fact dictionaries with hiring signal data
        """
        logger.info(f"Fetching LinkedIn data for {len(company_ids)} companies")
        facts = []

        for company_name in company_ids:
            try:
                data = self.client.get_linkedin_data(company_name)

                facts.append(
                    {
                        "company_id": company_name,
                        "fact_type": "hiring_signals",
                        "value": {
                            "ai_related_positions": data.ai_related_positions,
                            "has_hiring_activity": data.ai_related_positions > 0,
                        },
                        "confidence": 0.3,  # Lower confidence for news-derived data
                        "extracted_at": datetime.now(),
                        "source": self.source_name,
                        "metadata": {
                            "company_name": company_name,
                            "data_source": "news_heuristic",
                        },
                    }
                )

                # Add AI hiring fact separately if positive
                if data.ai_related_positions and data.ai_related_positions > 0:
                    facts.append(
                        {
                            "company_id": company_name,
                            "fact_type": "ai_hiring",
                            "value": {
                                "positions": data.ai_related_positions,
                                "signal_strength": min(data.ai_related_positions / 10, 1.0),
                            },
                            "confidence": 0.3,
                            "extracted_at": datetime.now(),
                            "source": self.source_name,
                            "metadata": {
                                "company_name": company_name,
                            },
                        }
                    )

            except Exception as e:
                logger.warning(f"Failed to fetch LinkedIn data for {company_name}: {e}")
                continue

        return facts

    def get_authority(self) -> SourceAuthority:
        """Return LinkedIn authority level."""
        return SourceAuthority.LINKEDIN

    def supports_incremental(self) -> bool:
        """LinkedIn supports incremental refresh via hash comparison."""
        return True
