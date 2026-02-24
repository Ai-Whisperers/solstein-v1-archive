"""Funding refresh connector for investment data updates.

Uses Crunchbase API or news-based detection to fetch funding data.
Implements incremental refresh with funding round detection.
"""

from datetime import datetime
from typing import Any

from loguru import logger

from solstein.data.additional_sources import AdditionalDataSources
from solstein.infrastructure.conflict_resolution import SourceAuthority
from solstein.infrastructure.refresh import BaseRefreshConnector


class FundingRefreshConnector(BaseRefreshConnector):
    """Funding refresh connector for investment and funding data.

    Fetches funding data including:
    - Total funding raised
    - Number of funding rounds
    - Latest funding round details
    - Funding source (Crunchbase API vs news-based)

    Confidence: 0.73 (higher with Crunchbase API: 0.7, lower with news: 0.3)
    """

    def __init__(self, db_manager, crunchbase_key: str | None = None, news_api_key: str | None = None):
        super().__init__(
            source_name="funding",
            source_type="funding_data",
            db_manager=db_manager,
            confidence=0.73,
        )
        self.crunchbase_key = crunchbase_key
        self.news_api_key = news_api_key
        self.client = AdditionalDataSources(
            crunchbase_key=crunchbase_key,
            news_api_key=news_api_key,
        )

    async def fetch_facts(
        self,
        company_ids: list[str],
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch funding data facts for companies.

        Args:
            company_ids: List of company names to search funding for
            start_date: Not used (funding data returns current totals)
            end_date: Not used

        Returns:
            List of fact dictionaries with funding data
        """
        logger.info(f"Fetching funding data for {len(company_ids)} companies")
        facts = []

        for company_name in company_ids:
            try:
                funding = self.client.get_funding_data(company_name)

                # Calculate confidence based on data source
                confidence = 0.7 if self.crunchbase_key else 0.3
                backend = "crunchbase_api" if self.crunchbase_key else "news_heuristic"

                facts.append(
                    {
                        "company_id": company_name,
                        "fact_type": "funding_summary",
                        "value": {
                            "total_raised": funding.total_raised,
                            "num_rounds": funding.num_rounds,
                            "average_round_size": (
                                funding.total_raised / funding.num_rounds if funding.num_rounds > 0 else 0
                            ),
                        },
                        "confidence": confidence,
                        "extracted_at": datetime.now(),
                        "source": self.source_name,
                        "metadata": {
                            "company_name": company_name,
                            "backend": backend,
                            "has_crunchbase_access": bool(self.crunchbase_key),
                        },
                    }
                )

                # Add individual round facts if available
                if hasattr(funding, "latest_round") and funding.latest_round:
                    facts.append(
                        {
                            "company_id": company_name,
                            "fact_type": "latest_funding_round",
                            "value": {
                                "round_type": funding.latest_round.get("type", "unknown"),
                                "amount": funding.latest_round.get("amount"),
                                "date": funding.latest_round.get("date"),
                            },
                            "confidence": confidence,
                            "extracted_at": datetime.now(),
                            "source": self.source_name,
                            "metadata": {
                                "company_name": company_name,
                                "backend": backend,
                            },
                        }
                    )

            except Exception as e:
                logger.warning(f"Failed to fetch funding data for {company_name}: {e}")
                continue

        return facts

    def get_authority(self) -> SourceAuthority:
        """Return Funding authority level."""
        return SourceAuthority.FUNDING

    def supports_incremental(self) -> bool:
        """Funding supports incremental refresh via hash comparison."""
        return True
