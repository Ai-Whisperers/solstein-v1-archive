"""Patents refresh connector for IP data updates.

Uses USPTO PEDS, Google Patents, and DuckDuckGo to fetch patent data.
Implements incremental refresh with patent count-based delta detection.
"""

import asyncio
from datetime import datetime
from typing import Any

from loguru import logger

from solstein.data.patent_client import search_company_patents
from solstein.infrastructure.conflict_resolution import SourceAuthority
from solstein.infrastructure.refresh import BaseRefreshConnector


class PatentsRefreshConnector(BaseRefreshConnector):
    """Patents refresh connector for intellectual property data.

    Fetches patent data including:
    - Total patent count
    - Recent patent applications
    - AI-related patents
    - Top technology categories

    Confidence: 0.80 (authoritative for IP data from USPTO)
    """

    def __init__(self, db_manager):
        super().__init__(
            source_name="patents",
            source_type="ip_data",
            db_manager=db_manager,
            confidence=0.80,
        )

    async def fetch_facts(
        self,
        company_ids: list[str],
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch patent data facts for companies.

        Args:
            company_ids: List of company names to search patents for
            start_date: Not used (patent search returns current data)
            end_date: Not used

        Returns:
            List of fact dictionaries with patent data
        """
        logger.info(f"Fetching patent data for {len(company_ids)} companies")
        facts = []

        for company_name in company_ids:
            try:
                result = await asyncio.to_thread(search_company_patents, company_name)

                # Calculate confidence based on data source
                confidence = 0.7 if result.source == "uspto_peds" else 0.4

                facts.append(
                    {
                        "company_id": company_name,
                        "fact_type": "patent_portfolio",
                        "value": {
                            "total_patents": result.total_patents,
                            "recent_patents": result.recent_patents,
                            "ai_related_patents": result.ai_related_patents,
                            "top_categories": result.top_categories,
                            "source_backend": result.source,
                        },
                        "confidence": confidence,
                        "extracted_at": datetime.now(),
                        "source": self.source_name,
                        "metadata": {
                            "backend": result.source,
                            "company_name": company_name,
                        },
                    }
                )

                # Add AI patents fact separately if available
                if result.ai_related_patents and result.ai_related_patents > 0:
                    facts.append(
                        {
                            "company_id": company_name,
                            "fact_type": "ai_patents",
                            "value": {
                                "count": result.ai_related_patents,
                                "percentage": (
                                    (result.ai_related_patents / result.total_patents * 100)
                                    if result.total_patents > 0
                                    else 0
                                ),
                            },
                            "confidence": confidence,
                            "extracted_at": datetime.now(),
                            "source": self.source_name,
                            "metadata": {
                                "backend": result.source,
                                "company_name": company_name,
                            },
                        }
                    )

            except Exception as e:
                logger.warning(f"Failed to fetch patent data for {company_name}: {e}")
                continue

        return facts

    def get_authority(self) -> SourceAuthority:
        """Return Patents authority level."""
        return SourceAuthority.PATENTS

    def supports_incremental(self) -> bool:
        """Patents supports incremental refresh via hash comparison."""
        return True
