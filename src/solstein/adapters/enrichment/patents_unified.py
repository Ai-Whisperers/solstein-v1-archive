"""Unified Patents adapter for Solstein.

Converts patent_client functionality to a unified adapter
implementing the full UnifiedDataSource protocol.

Combines PatentEnrichment and PatentsRefreshConnector capabilities.
Uses USPTO PEDS (primary), Google Patents, or DuckDuckGo (fallback).
No API key required.
"""

from datetime import datetime, timezone
from typing import Any

from loguru import logger

from solstein.data.patent_client import search_company_patents
from solstein.domain.models import DataSourceType, RawDataSource
from solstein.infrastructure.conflict_resolution import SourceAuthority
from solstein.infrastructure.refresh import BaseRefreshConnector
from solstein.research.discovery import DiscoveryCandidate


class PatentsUnifiedAdapter(BaseRefreshConnector):
    """Unified Patents adapter implementing the full protocol.

    Fetches patent data from USPTO PEDS, Google Patents, or DuckDuckGo.
    Combines enrichment and refresh capabilities.

    Confidence: 0.80 for USPTO, 0.40 for fallbacks
    Authority: PATENTS (0.85)
    """

    _SOURCE_TYPE_MAP = {
        "uspto_peds": DataSourceType.USPTO,
        "google_patents": DataSourceType.GOOGLE_PATENTS,
        "duckduckgo": DataSourceType.PATENTS,
        "none": DataSourceType.PATENTS,
    }

    def __init__(self, db_manager=None):
        super().__init__(
            source_name="patents_unified",
            source_type="patents",
            db_manager=db_manager,
            confidence=0.80,
        )

    def discover(
        self,
        market: str,
        seed_company: str,
        max_results: int = 50,
        extra_keywords: list[str] | None = None,
    ) -> list[DiscoveryCandidate]:
        """Discover companies by patent activity in market.

        Searches for companies with patents in the target market.
        """
        logger.info(f"Discovering companies with patents in {market}")

        # Search for patents in the market
        query = f"{market} patents"
        if extra_keywords:
            query += " " + " ".join(extra_keywords)

        result = search_company_patents(query)

        candidates = []
        if result.total_patents > 0:
            # Create candidate from patent search
            candidate = DiscoveryCandidate(
                name=f"{market} patent holder",
                source_url="",
                source_type="patents",
                confidence=0.60,
                discovery_metadata={
                    "market": market,
                    "total_patents": result.total_patents,
                    "recent_patents": result.recent_patents,
                    "ai_related": result.ai_related_patents,
                },
            )
            candidates.append(candidate)

        return candidates[:max_results]

    def enrich(
        self,
        company_id: str,
        company_name: str,
        ticker: str | None = None,
        website: str | None = None,
    ) -> RawDataSource:
        """Enrich company with patent data."""
        logger.info(f"Enriching {company_name} with patent data")

        result = search_company_patents(company_name)

        actual_source_type = self._SOURCE_TYPE_MAP.get(result.source, DataSourceType.PATENTS)
        confidence = 0.8 if result.source == "uspto_peds" else 0.4

        return RawDataSource(
            source_name=f"patents_unified ({result.source})",
            source_type=actual_source_type,
            company_id=company_id,
            fetch_timestamp=datetime.now(timezone.utc),
            data={
                "total_patents": result.total_patents,
                "recent_patents": result.recent_patents,
                "ai_related_patents": result.ai_related_patents,
                "top_categories": result.top_categories,
                "source_backend": result.source,
            },
            metadata={
                "backend": result.source,
                "total_patents": result.total_patents,
                "ai_related_patents": result.ai_related_patents,
                "confidence": confidence,
            },
        )

    async def fetch_facts(
        self,
        company_ids: list[str],
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch patent facts for companies."""
        logger.info(f"Fetching patent data for {len(company_ids)} companies")
        facts = []

        for company_name in company_ids:
            try:
                result = search_company_patents(company_name)
                confidence = 0.8 if result.source == "uspto_peds" else 0.4

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
                        },
                    }
                )

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
                        }
                    )

            except Exception as e:
                logger.warning(f"Failed to fetch patent data for {company_name}: {e}")
                continue

        return facts

    def get_confidence(self) -> float:
        return 0.80

    def get_authority(self) -> SourceAuthority:
        return SourceAuthority.PATENTS

    def supports_incremental(self) -> bool:
        return True

    def supports_discovery(self) -> bool:
        return True
