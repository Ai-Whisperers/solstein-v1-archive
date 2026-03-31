"""Web search agent for news, press releases, and market intelligence.

Gathers information from web search, news articles, and press releases
to extract facts about company growth, funding, and announcements.
"""

from datetime import datetime, timezone

import httpx

from ..domain.models import DataSourceType
from .base_agent import AgentTaskResult, BaseDataGatheringAgent
from .resilience import WEB_SEARCH_RETRY_CONFIG, CircuitBreaker, call_with_retry


class WebSearchAgent(BaseDataGatheringAgent):
    """Agent for gathering data from web search and news."""

    def __init__(self, google_api_key: str | None = None, search_engine_id: str | None = None):
        """Initialize web search agent.

        Args:
            google_api_key: Google Custom Search API key
            search_engine_id: Google Custom Search Engine ID
        """
        super().__init__("WebSearchAgent", DataSourceType.NEWS)
        self.google_api_key = google_api_key
        self.search_engine_id = search_engine_id
        self.search_base = "https://www.googleapis.com/customsearch/v1"

        self.circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=45.0, name="GoogleSearchAPI")

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

            if not self.google_api_key or not self.search_engine_id:
                self.log_warning("Google Custom Search API not configured")
                result.coverage_gaps.append("Web search API not configured")
                result.success = False
                result.error_message = "Web search API not configured"
                result.execution_time_seconds = (datetime.now(timezone.utc) - start_time).total_seconds()
                return result

            search_queries = self._generate_search_queries(company_name, context)
            self.log_info(f"Running {len(search_queries)} search queries")

            for query_name, query_text in search_queries:
                try:
                    articles = await call_with_retry(
                        self._api_search_news,
                        query_text,
                        retry_config=WEB_SEARCH_RETRY_CONFIG,
                        circuit_breaker=self.circuit_breaker,
                        name=f"search_news[{query_name}]",
                    )
                    self.log_info(f"Found {len(articles)} articles for: {query_name}")

                    for article in articles[:5]:
                        raw_source = self._create_raw_source(
                            raw_content={
                                "title": article.get("title"),
                                "snippet": article.get("snippet"),
                                "link": article.get("link"),
                            },
                            source_name=f"Web Search: {article.get('displayLink', 'unknown')}",
                            url=article.get("link"),
                            publication_date=self._parse_date(article.get("snippet")),
                            confidence=0.75,
                            extraction_method="google_custom_search",
                            metadata={
                                "query": query_name,
                                "title": article.get("title"),
                            },
                        )
                        result.raw_sources.append(raw_source)

                except Exception as e:
                    self.log_warning(f"Error searching {query_name}: {e}")

            if result.raw_sources:
                result.extracted_facts.extend(self._extract_facts_from_sources(result.raw_sources, company_name))

            result.success = True
            self.log_info(f"Successfully gathered {len(result.raw_sources)} web sources")

        except Exception as e:
            self.log_error(f"Error gathering web search data: {e}")
            result.error_message = str(e)
            result.success = False

        finally:
            result.execution_time_seconds = (datetime.now(timezone.utc) - start_time).total_seconds()

        return result

    def _generate_search_queries(self, company_name: str, context: dict) -> list[tuple[str, str]]:
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

    async def _api_search_news(self, query: str) -> list[dict]:
        """API call to Google Custom Search."""
        if not self.google_api_key or not self.search_engine_id:
            return []

        try:
            params = {
                "q": query,
                "key": self.google_api_key,
                "cx": self.search_engine_id,
                "num": 10,
                "sort": "date",
            }

            async with httpx.AsyncClient() as client:
                resp = await client.get(self.search_base, params=params, timeout=15.0)
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get("items", [])
                else:
                    self.log_warning(f"Search API error {resp.status_code}")
        except Exception as e:
            self.log_error(f"Error calling search API: {e}")

        return []

    def _extract_facts_from_sources(self, raw_sources: list, company_name: str) -> list:
        """Extract facts from web search sources."""
        facts = []

        funding_mentions = [s for s in raw_sources if "funding" in s.metadata.get("query", "").lower()]
        if funding_mentions:
            facts.append(
                self._create_fact(
                    fact_type="funding_news_signal",
                    value=len(funding_mentions),
                    confidence=0.70,
                    sources_used=[s.source_name for s in funding_mentions[:3]],
                )
            )

        hiring_mentions = [s for s in raw_sources if "hiring" in s.metadata.get("query", "").lower()]
        if hiring_mentions:
            facts.append(
                self._create_fact(
                    fact_type="hiring_news_signal",
                    value=len(hiring_mentions),
                    confidence=0.70,
                    sources_used=[s.source_name for s in hiring_mentions[:3]],
                )
            )

        product_mentions = [s for s in raw_sources if "product" in s.metadata.get("query", "").lower()]
        if product_mentions:
            facts.append(
                self._create_fact(
                    fact_type="product_innovation_signal",
                    value=len(product_mentions),
                    confidence=0.65,
                    sources_used=[s.source_name for s in product_mentions[:3]],
                )
            )

        return facts

    def _parse_date(self, text: str | None) -> datetime | None:
        """Try to extract publication date from snippet."""
        if not text:
            return None

        try:
            import dateutil.parser

            for word in text.split():
                try:
                    return dateutil.parser.parse(word)
                except (ValueError, TypeError):
                    continue
        except Exception as e:
            self.log_warning(f"Error parsing date from text: {e}")

        return None
