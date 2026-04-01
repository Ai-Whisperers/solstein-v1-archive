"""Unified Funding adapter for Solstein.

Converts funding functionality from additional_sources to a unified adapter
implementing the full UnifiedDataSource protocol.

Uses Crunchbase API when available, falls back to public sources.

STORY-134: Replaced requests with httpx. fetch_facts uses asyncio.gather
for concurrent per-company fetches.
"""

import asyncio
from datetime import datetime
from typing import Any

import httpx
from loguru import logger

from solstein.adapters.logging import log_adapter_error
from solstein.config import get_settings
from solstein.data.additional_sources import AdditionalDataSources
from solstein.domain.discovery import DiscoveryCandidate  # STORY-246
from solstein.domain.models import DataSourceType, RawDataSource
from solstein.infrastructure.conflict_resolution import SourceAuthority
from solstein.infrastructure.database import DatabaseManager
from solstein.infrastructure.database import db_manager as default_db_manager
from solstein.infrastructure.refresh import BaseRefreshConnector


class FundingUnifiedAdapter(BaseRefreshConnector):
    """Unified Funding adapter implementing the full protocol.

    Fetches funding and investment data for companies.
    Uses Crunchbase API or public news sources.

    Confidence: 0.65
    Authority: FUNDING
    """

    def __init__(self, db_manager: DatabaseManager | None = None, crunchbase_api_key: str | None = None):
        super().__init__(
            source_name="funding_unified",
            source_type=DataSourceType.CRUNCHBASE,
            db_manager=db_manager or default_db_manager,
            confidence=0.65,
        )
        self.crunchbase_api_key = crunchbase_api_key

    def _get_crunchbase_data(self, company_name: str) -> dict[str, Any] | None:
        """Get funding data from Crunchbase API (sync, uses httpx)."""
        if not self.crunchbase_api_key:
            return None

        url = f"https://api.crunchbase.com/v4/organizations/{company_name}"
        headers = {"Authorization": f"Bearer {self.crunchbase_api_key}"}

        try:
            _settings = get_settings()
            response = httpx.get(url, headers=headers, timeout=_settings.http_timeouts.funding)
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
        except (httpx.HTTPError, httpx.TimeoutException, OSError) as e:
            log_adapter_error(
                component="FundingUnifiedSource",
                operation="_get_crunchbase_data",
                error=e,
                entity_name=company_name,
                level="warning",
            )

        return None

    async def _get_crunchbase_data_async(self, company_name: str) -> dict[str, Any] | None:
        """Get funding data from Crunchbase API (async, uses httpx.AsyncClient)."""
        if not self.crunchbase_api_key:
            return None

        url = f"https://api.crunchbase.com/v4/organizations/{company_name}"
        headers = {"Authorization": f"Bearer {self.crunchbase_api_key}"}

        try:
            _settings = get_settings()
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=_settings.http_timeouts.funding)
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
        except (httpx.HTTPError, httpx.TimeoutException, OSError) as e:
            log_adapter_error(
                component="FundingUnifiedSource",
                operation="_get_crunchbase_data_async",
                error=e,
                entity_name=company_name,
                level="warning",
            )

        return None

    def _get_public_funding_data(self, company_name: str) -> list[dict[str, Any]]:
        """Get funding news from public sources."""
        try:
            additional = AdditionalDataSources()
            news = additional.get_news(company_name, days_back=180)

            rounds: list[dict[str, Any]] = []
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
        except Exception as e:  # noqa: BLE001
            log_adapter_error(
                component="FundingUnifiedSource",
                operation="_get_public_funding_data",
                error=e,
                entity_name=company_name,
                level="warning",
            )
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

        candidates: list[DiscoveryCandidate] = []
        for funding_news in rounds[:max_results]:
            name = funding_news.get("title", "").split(":")[0][:100] or "unknown-company"
            company_id = "-".join(part for part in "".join(ch if ch.isalnum() else " " for ch in name.lower()).split())
            candidate = DiscoveryCandidate(
                company_id=company_id or "unknown-company",
                name=name,
                market=market,
                ticker=None,
                industry="Unknown",
                region="Unknown",
                tags=["funding", market.lower()],
                seed_relevance=0.60,
                discovery_reason="funding activity mention",
                source_links=[],
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
            retrieval_timestamp=datetime.now(),
            raw_content=data,
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
        """Fetch funding facts for companies concurrently.

        STORY-134: Uses asyncio.gather for concurrent per-company fetches
        instead of sequential asyncio.to_thread calls.
        """

        async def _fetch_one(company_name: str) -> dict[str, Any] | None:
            crunchbase_data = await self._get_crunchbase_data_async(company_name)
            if crunchbase_data:
                return {
                    "company_id": company_name,
                    "fact_type": "funding_summary",
                    "value": crunchbase_data,
                    "confidence": self.confidence,
                    "extracted_at": datetime.now(),
                    "source": self.source_name,
                }
            return None

        results = await asyncio.gather(
            *[_fetch_one(cid) for cid in company_ids],
            return_exceptions=True,
        )

        facts: list[dict[str, Any]] = []
        for i, result in enumerate(results):
            if isinstance(result, BaseException):
                logger.warning(f"[FundingUnifiedAdapter] fetch_facts failed for {company_ids[i]}: {result}")
            elif result is not None:
                facts.append(result)

        return facts

    def get_confidence(self) -> float:
        return 0.65

    def get_authority(self) -> SourceAuthority:
        return SourceAuthority.FUNDING

    def supports_incremental(self) -> bool:
        return True

    def supports_discovery(self) -> bool:
        return True
