"""Unified Web Search adapter for Solstein.

Converts the legacy web_search_client module to a unified adapter
implementing the full UnifiedDataSource protocol.

Provides web search capabilities using multiple backends:
- Exa (primary)
- Google Search (fallback)

This enables news gathering without requiring NewsAPI keys.
"""

from datetime import datetime
from typing import Any

from loguru import logger

from solstein.data.web_search_client import (
    search_company_info,
    search_company_news,
)
from solstein.domain.models import RawDataSource
from solstein.infrastructure.conflict_resolution import SourceAuthority
from solstein.infrastructure.refresh import BaseRefreshConnector
from solstein.research.discovery import DiscoveryCandidate


class WebSearchUnifiedAdapter(BaseRefreshConnector):
    """Unified Web Search adapter implementing the full protocol.

    Combines discovery, enrichment, and refresh capabilities for web search.
    Uses Exa API as primary with Google Search fallback.

    Confidence: 0.70 (web search can have varying quality)
    Authority: WEB_SEARCH (lower authority than official sources)
    """

    def __init__(self, db_manager=None):
        super().__init__(
            source_name="web_search",
            source_type="web_search",
            db_manager=db_manager,
            confidence=0.70,
        )
    def discover(
        self,
        market: str,
        seed_company: str,
        max_results: int = 50,
        extra_keywords: list[str] | None = None,
    ) -> list[DiscoveryCandidate]:
        """Discover companies via web search.

        Searches for companies in the target market using web search.
        Returns candidates found in search results.

        Args:
            market: Target market/industry (e.g., "energy software")
            seed_company: Seed company name for context
            max_results: Maximum candidates to return
            extra_keywords: Additional search keywords

        Returns:
            List of DiscoveryCandidate objects
        """
        logger.info(f"Discovering companies in {market} via web search")

        # Build search query
        query = f"{market} companies like {seed_company}"
        if extra_keywords:
            query += " " + " ".join(extra_keywords)

        try:
            # Search for companies
            results = search_company_info(query, query_type="general")

            candidates = []
            for result in results[:max_results]:
                # Extract company name from title
                title = result.get("title", "")
                snippet = result.get("snippet", "")

                # Create candidate
                candidate = DiscoveryCandidate(
                    name=title.split(" - ")[0].split(" | ")[0][:100],
                    source_url=result.get("url", ""),
                    source_type="web_search",
                    confidence=0.60,  # Web search discovery has lower confidence
                    discovery_metadata={
                        "snippet": snippet[:200],
                        "market": market,
                        "source": "web_search",
                    },
                )
                candidates.append(candidate)

            logger.info(f"Discovered {len(candidates)} companies via web search")
            return candidates

        except Exception as e:
            logger.error(f"Web search discovery failed: {e}")
            return []

    def enrich(
        self,
        company_id: str,
        company_name: str,
        ticker: str | None = None,
        website: str | None = None,
    ) -> RawDataSource:
        """Enrich company data via web search.

        Fetches news and general information about the company.

        Args:
            company_id: Unique company identifier
            company_name: Company name
            ticker: Optional stock ticker
            website: Optional company website

        Returns:
            RawDataSource with web search results
        """
        logger.info(f"Enriching {company_name} via web search")

        try:
            # Fetch news
            news = search_company_news(company_name, max_results=20)

            # Fetch general info
            info = search_company_info(company_name, query_type="general")

            # Fetch funding info
            funding_info = search_company_info(company_name, query_type="funding")

            # Fetch tech info
            tech_info = search_company_info(company_name, query_type="technology")

            # Build raw data source
            raw_data = RawDataSource(
                source_name=self.source_name,
                source_type=self.source_type,
                company_id=company_id,
                fetch_timestamp=datetime.now(),
                data={
                    "news": news,
                    "general_info": info,
                    "funding_info": funding_info,
                    "tech_info": tech_info,
                },
                metadata={
                    "news_count": len(news),
                    "info_count": len(info),
                    "funding_info_count": len(funding_info),
                    "tech_info_count": len(tech_info),
                },
            )

            return raw_data

        except Exception as e:
            logger.error(f"Web search enrichment failed: {e}")
            # Return empty raw data source
            return RawDataSource(
                source_name=self.source_name,
                source_type=self.source_type,
                company_id=company_id,
                fetch_timestamp=datetime.now(),
                data={},
                metadata={"error": str(e)},
            )

    async def fetch_facts(
        self,
        company_ids: list[str],
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch facts via web search refresh.

        Searches for latest news and information about companies.

        Args:
            company_ids: List of company IDs (names) to search
            start_date: Not used (web search returns current data)
            end_date: Not used

        Returns:
            List of fact dictionaries
        """
        logger.info(f"Fetching web search facts for {len(company_ids)} companies")
        facts = []

        for company_name in company_ids:
            try:
                # Search for news
                news = search_company_news(company_name, max_results=10)

                # Create news fact
                if news:
                    facts.append(
                        {
                            "company_id": company_name,
                            "fact_type": "web_search_news",
                            "value": {
                                "articles": news,
                                "article_count": len(news),
                            },
                            "confidence": self.confidence,
                            "extracted_at": datetime.now(),
                            "source": self.source_name,
                            "metadata": {
                                "latest_article_date": news[0].get("date") if news else None,
                                "sources": list(set(article.get("source", "Web") for article in news)),
                            },
                        }
                    )

                # Search for general updates
                info = search_company_info(company_name, query_type="general")
                if info:
                    facts.append(
                        {
                            "company_id": company_name,
                            "fact_type": "web_search_info",
                            "value": {
                                "results": info[:5],  # Top 5 results
                                "result_count": len(info),
                            },
                            "confidence": self.confidence * 0.9,  # Slightly lower for general info
                            "extracted_at": datetime.now(),
                            "source": self.source_name,
                            "metadata": {
                                "top_sources": [r.get("url", "") for r in info[:3]],
                            },
                        }
                    )

            except Exception as e:
                logger.warning(f"Failed to fetch web search data for {company_name}: {e}")
                continue

        return facts

    def get_confidence(self) -> float:
        """Return base confidence score for web search.

        Web search results can vary in quality and accuracy.
        """
        return 0.70

    def get_authority(self) -> SourceAuthority:
        """Return authority level for web search.

        Web search has lower authority than official sources
        like SEC EDGAR or Companies House.
        """
        return SourceAuthority.WEB_SEARCH

    def supports_incremental(self) -> bool:
        """Return True - web search supports incremental refresh.

        Can search for recent news/articles only.
        """
        return True

    def supports_discovery(self) -> bool:
        """Return True - web search supports company discovery."""
        return True

    async def _filter_delta(
        self,
        facts: list[dict[str, Any]],
        since: datetime,
    ) -> list[dict[str, Any]]:
        """Filter facts to only return changed data since last refresh.

        For web search, we use hash comparison from base class
        to detect actual content changes.
        """
        return await super()._filter_delta(facts, since)
