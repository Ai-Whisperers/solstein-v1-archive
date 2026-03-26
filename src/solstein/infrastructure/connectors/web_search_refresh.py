"""Web Search refresh connector for general company information updates.

Uses Exa search to fetch general company information.
Implements incremental refresh for discovery data.
"""

import asyncio
from datetime import datetime
from typing import Any

from loguru import logger

from solstein.infrastructure.conflict_resolution import SourceAuthority
from solstein.infrastructure.refresh import BaseRefreshConnector


class WebSearchRefreshConnector(BaseRefreshConnector):
    """Web Search refresh connector for general company information.

    Uses Exa search to fetch:
    - General company mentions
    - Recent web content about companies
    - Related entities and context

    Note: Limited functionality - primarily a discovery source.
    Confidence: 0.68 (lower for web-derived information)
    """

    def __init__(self, db_manager, exa_api_key: str | None = None):
        super().__init__(
            source_name="web_search",
            source_type="web_discovery",
            db_manager=db_manager,
            confidence=0.68,
        )
        self.exa_api_key = exa_api_key

    async def fetch_facts(
        self,
        company_ids: list[str],
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch web search facts for companies.

        Note: Web search is primarily a discovery source.
        Refresh capabilities are limited.

        Args:
            company_ids: List of company names to search for
            start_date: Not used
            end_date: Not used

        Returns:
            List of fact dictionaries (limited - discovery source)
        """
        logger.info(f"Fetching web search data for {len(company_ids)} companies")
        facts = []

        if not self.exa_api_key:
            logger.warning("WebSearchRefreshConnector: No Exa API key provided")
            return facts

        for company_name in company_ids:
            try:
                from solstein.data.web_search_client import search_company_info

                results = await asyncio.to_thread(search_company_info, company_name, query_type="general")

                if results:
                    facts.append(
                        {
                            "company_id": company_name,
                            "fact_type": "web_presence",
                            "value": {
                                "mentions_found": len(results),
                                "has_recent_content": len(results) > 0,
                            },
                            "confidence": self.confidence,
                            "extracted_at": datetime.now(),
                            "source": self.source_name,
                            "metadata": {
                                "company_name": company_name,
                                "backend": "exa_search",
                            },
                        }
                    )

            except Exception as e:
                logger.warning(f"Failed to fetch web search data for {company_name}: {e}")
                continue

        return facts

    def get_authority(self) -> SourceAuthority:
        """Return Web Search authority level."""
        return SourceAuthority.WEB_SEARCH

    def supports_incremental(self) -> bool:
        """Web Search supports incremental refresh via hash comparison."""
        return True
