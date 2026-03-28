"""Web search agent for news, press releases, and market intelligence.

STORY-101: Uses SearXNG (self-hosted meta-search) as primary backend.
Falls back to Google Custom Search when SearXNG is unreachable.
Results are cached in Redis to avoid redundant queries within the TTL window.

Gathers information from web search, news articles, and press releases
to extract facts about company growth, funding, and announcements.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

import dateutil.parser

from solstein.config import get_settings

from ..domain.models import DataSourceType
from .base_agent import AgentTaskResult, BaseDataGatheringAgent
from .search_backends import SearchBackendDispatcher

logger = logging.getLogger(__name__)


class WebSearchAgent(BaseDataGatheringAgent):
    """Agent for gathering data from web search and news.

    Primary backend: SearXNG (self-hosted, free, unlimited).
    Fallback: Google Custom Search (100 free queries/day, paid after).
    """

    def __init__(
        self,
        google_api_key: str | None = None,
        search_engine_id: str | None = None,
    ) -> None:
        """Initialize web search agent.

        Args:
            google_api_key: Google Custom Search API key (fallback).
            search_engine_id: Google Custom Search Engine ID (fallback).
        """
        super().__init__("WebSearchAgent", DataSourceType.NEWS)

        _settings = get_settings()
        self.dispatcher = SearchBackendDispatcher(
            searxng_url=_settings.searxng_url,
            searxng_engines=_settings.searxng_engines,
            search_cache_ttl=_settings.search_cache_ttl,
            google_api_key=google_api_key,
            search_engine_id=search_engine_id,
        )

    async def gather(self, company_name: str, context: dict) -> AgentTaskResult:
        """Gather web search data for a company."""
        start_time = datetime.now(timezone.utc)
        result = AgentTaskResult(
            agent_name=self.agent_name,
            source_type=self.source_type,
            success=False,
        )

        try:
            self.log_info(f"Starting web search research for {company_name}")
            search_queries = self._generate_search_queries(company_name, context)
            self.log_info(f"Running {len(search_queries)} search queries")

            for query_name, query_text in search_queries:
                try:
                    search_results = await self.dispatcher.search(query_text)
                    self.log_info(
                        f"Found {len(search_results)} results for: {query_name}"
                    )

                    for sr in search_results[:5]:
                        raw_source = self._create_raw_source(
                            raw_content={
                                "title": sr.title,
                                "snippet": sr.snippet,
                                "link": sr.url,
                            },
                            source_name=f"Web Search: {sr.source_engine}",
                            url=sr.url,
                            publication_date=self._parse_date(sr.snippet),
                            confidence=0.75,
                            extraction_method=f"search_{sr.source_engine}",
                            metadata={
                                "query": query_name,
                                "title": sr.title,
                                "source_engine": sr.source_engine,
                                "relevance_score": sr.relevance_score,
                            },
                        )
                        result.raw_sources.append(raw_source)

                except Exception as e:  # noqa: BLE001
                    self.log_warning(f"Error searching {query_name}: {e}")

            if result.raw_sources:
                result.extracted_facts.extend(
                    self._extract_facts_from_sources(result.raw_sources, company_name)
                )

            result.success = True
            self.log_info(
                f"Successfully gathered {len(result.raw_sources)} web sources"
            )

        except Exception as e:  # noqa: BLE001
            self.log_error(f"Error gathering web search data: {e}")
            result.error_message = str(e)
            result.success = False

        finally:
            result.execution_time_seconds = (
                datetime.now(timezone.utc) - start_time
            ).total_seconds()

        return result

    def _generate_search_queries(
        self, company_name: str, context: dict
    ) -> list[tuple[str, str]]:
        """Generate relevant search queries."""
        industry = context.get("industry", "company")

        return [
            ("Funding Rounds", f"{company_name} funding raised Series"),
            ("Revenue & Growth", f"{company_name} revenue growth 2024 2025"),
            ("Hiring", f"{company_name} hiring announcement jobs"),
            ("M&A Activity", f"{company_name} acquisition merger"),
            ("Product Updates", f"{company_name} product launch announcement"),
            ("Executive Changes", f"{company_name} CEO founder leadership"),
            ("Industry News", f"{company_name} {industry} market"),
            ("Press Releases", f"{company_name} press release news"),
        ]

    def _extract_facts_from_sources(
        self, raw_sources: list, company_name: str
    ) -> list:
        """Extract facts from web search sources."""
        facts = []

        for fact_type, keyword, confidence in [
            ("funding_news_signal", "funding", 0.70),
            ("hiring_news_signal", "hiring", 0.70),
            ("product_innovation_signal", "product", 0.65),
        ]:
            mentions = [
                s
                for s in raw_sources
                if keyword in s.metadata.get("query", "").lower()
            ]
            if mentions:
                facts.append(
                    self._create_fact(
                        fact_type=fact_type,
                        value=len(mentions),
                        confidence=confidence,
                        sources_used=[s.source_name for s in mentions[:3]],
                    )
                )

        return facts

    def _parse_date(self, text: str | None) -> datetime | None:
        """Try to extract publication date from snippet."""
        if not text:
            return None

        try:
            for word in text.split():
                try:
                    return dateutil.parser.parse(word)
                except (ValueError, TypeError):
                    continue
        except Exception as e:  # noqa: BLE001
            self.log_warning(f"Error parsing date from text: {e}")

        return None
