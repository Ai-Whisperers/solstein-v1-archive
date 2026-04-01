"""Unified News adapter for Solstein.

Converts news functionality from additional_sources to a unified adapter
implementing the full UnifiedDataSource protocol.

Uses NewsAPI.org as primary with web search fallback.

STORY-134: Replaced requests with httpx. fetch_facts uses asyncio.gather
for concurrent per-company fetches.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any

import httpx
from loguru import logger

from solstein.adapters.logging import log_adapter_error
from solstein.config import get_settings
from solstein.domain.discovery import DiscoveryCandidate  # STORY-246
from solstein.domain.models import RawDataSource
from solstein.infrastructure.conflict_resolution import SourceAuthority
from solstein.infrastructure.database import DatabaseManager
from solstein.infrastructure.database import db_manager as default_db_manager
from solstein.infrastructure.refresh import BaseRefreshConnector

_POSITIVE_WORDS = [
    "growth", "profit", "revenue", "success", "win", "launch",
    "expand", "innovation", "leader", "partnership", "award",
    "acquisition", "positive", "strong", "beat", "bullish",
]

_NEGATIVE_WORDS = [
    "loss", "lawsuit", "investigation", "scandal", "fire", "layoff",
    "bankruptcy", "decline", "weak", "miss", "warning", "fraud",
    "investor", "concern", "risk",
]


def analyze_sentiment(text: str) -> str:
    """Simple keyword-based sentiment analysis."""
    text_lower = text.lower()
    pos_count = sum(1 for w in _POSITIVE_WORDS if w in text_lower)
    neg_count = sum(1 for w in _NEGATIVE_WORDS if w in text_lower)
    if pos_count > neg_count + 1:
        return "positive"
    elif neg_count > pos_count + 1:
        return "negative"
    return "neutral"


class NewsUnifiedAdapter(BaseRefreshConnector):
    """Unified News adapter implementing the full protocol.

    Fetches news coverage for companies using NewsAPI and web search.

    Confidence: 0.70
    Authority: NEWS_API
    """

    def __init__(self, db_manager: DatabaseManager | None = None, news_api_key: str | None = None):
        super().__init__(
            source_name="news_unified",
            source_type="news",
            db_manager=db_manager or default_db_manager,
            confidence=0.70,
        )
        self.news_api_key = news_api_key

    # Keep backward-compatible alias
    _analyze_sentiment = staticmethod(analyze_sentiment)

    def _get_news_from_api(self, company_name: str, days_back: int = 30) -> list[dict[str, Any]]:
        """Get news using NewsAPI.org (sync, uses httpx)."""
        if not self.news_api_key:
            return []

        from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

        url = "https://newsapi.org/v2/everything"
        params = {
            "q": company_name,
            "from": from_date,
            "sortBy": "relevancy",
            "pageSize": 50,
            "apiKey": self.news_api_key,
        }

        try:
            _settings = get_settings()
            response = httpx.get(url, params=params, timeout=_settings.http_timeouts.news_api)
            data = response.json()

            articles: list[dict[str, Any]] = []
            for article in data.get("articles", [])[:20]:
                published = article.get("publishedAt")
                if published:
                    published = datetime.fromisoformat(published.replace("Z", "+00:00"))

                sentiment = self._analyze_sentiment(article.get("title", "") + " " + (article.get("description") or ""))

                articles.append(
                    {
                        "title": article.get("title", ""),
                        "description": article.get("description"),
                        "source": article.get("source", {}).get("name", "Unknown"),
                        "url": article.get("url", ""),
                        "published_at": published or datetime.now(),
                        "sentiment": sentiment,
                    }
                )

            return articles

        except (httpx.HTTPError, httpx.TimeoutException, OSError) as e:
            log_adapter_error(
                component="NewsUnifiedSource",
                operation="_fetch_from_api",
                error=e,
                entity_name=company_name,
            )
            return []

    async def _get_news_from_api_async(self, company_name: str, days_back: int = 30) -> list[dict[str, Any]]:
        """Get news using NewsAPI.org (async, uses httpx.AsyncClient)."""
        if not self.news_api_key:
            return []

        from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

        url = "https://newsapi.org/v2/everything"
        params = {
            "q": company_name,
            "from": from_date,
            "sortBy": "relevancy",
            "pageSize": 50,
            "apiKey": self.news_api_key,
        }

        try:
            _settings = get_settings()
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=_settings.http_timeouts.news_api)
            data = response.json()

            articles: list[dict[str, Any]] = []
            for article in data.get("articles", [])[:20]:
                published = article.get("publishedAt")
                if published:
                    published = datetime.fromisoformat(published.replace("Z", "+00:00"))

                sentiment = self._analyze_sentiment(article.get("title", "") + " " + (article.get("description") or ""))

                articles.append(
                    {
                        "title": article.get("title", ""),
                        "description": article.get("description"),
                        "source": article.get("source", {}).get("name", "Unknown"),
                        "url": article.get("url", ""),
                        "published_at": published or datetime.now(),
                        "sentiment": sentiment,
                    }
                )

            return articles

        except (httpx.HTTPError, httpx.TimeoutException, OSError) as e:
            log_adapter_error(
                component="NewsUnifiedSource",
                operation="_fetch_from_api_async",
                error=e,
                entity_name=company_name,
            )
            return []

    def discover(
        self,
        market: str,
        seed_company: str,
        max_results: int = 50,
        extra_keywords: list[str] | None = None,
    ) -> list[DiscoveryCandidate]:
        """Discover companies via news search."""
        logger.info(f"Discovering companies in {market} via news")

        query = f"{market} companies"
        if extra_keywords:
            query += " " + " ".join(extra_keywords)

        articles = self._get_news_from_api(query, days_back=90)

        candidates: list[DiscoveryCandidate] = []
        for article in articles[:max_results]:
            name = article.get("title", "").split(":")[0][:100] or "unknown-company"
            company_id = "-".join(part for part in "".join(ch if ch.isalnum() else " " for ch in name.lower()).split())
            source_url = article.get("url", "")
            candidate = DiscoveryCandidate(
                company_id=company_id or "unknown-company",
                name=name,
                market=market,
                ticker=None,
                industry="Unknown",
                region="Unknown",
                tags=["news", market.lower()],
                seed_relevance=0.55,
                discovery_reason=f"news mention: {article.get('sentiment', 'neutral')}",
                source_links=[source_url] if source_url else [],
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
        """Enrich company with news data."""
        logger.info(f"Enriching {company_name} with news data")

        articles = self._get_news_from_api(company_name, days_back=30)

        positive = sum(1 for a in articles if a.get("sentiment") == "positive")
        negative = sum(1 for a in articles if a.get("sentiment") == "negative")
        neutral = len(articles) - positive - negative

        total = len(articles)
        sentiment_score = (positive - negative) / total if total > 0 else None

        return RawDataSource(
            source_name=self.source_name,
            source_type=self.source_type,
            retrieval_timestamp=datetime.now(),
            raw_content={
                "articles": articles,
                "total_articles": total,
                "positive_count": positive,
                "negative_count": negative,
                "neutral_count": neutral,
                "sentiment_score": sentiment_score,
            },
            metadata={
                "article_count": total,
                "sentiment": "positive"
                if sentiment_score and sentiment_score > 0.1
                else "negative"
                if sentiment_score and sentiment_score < -0.1
                else "neutral",
            },
        )

    async def fetch_facts(
        self,
        company_ids: list[str],
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch news facts for companies concurrently.

        STORY-134: Uses asyncio.gather for concurrent per-company fetches
        instead of sequential asyncio.to_thread calls.
        """
        async def _fetch_one(company_name: str) -> dict[str, Any] | None:
            articles = await self._get_news_from_api_async(company_name, 7)
            if articles:
                return {
                    "company_id": company_name,
                    "fact_type": "news_coverage",
                    "value": {
                        "articles": articles[:10],
                        "article_count": len(articles),
                    },
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
                logger.warning(f"[NewsUnifiedAdapter] fetch_facts failed for {company_ids[i]}: {result}")
            elif result is not None:
                facts.append(result)

        return facts

    def get_confidence(self) -> float:
        return 0.70

    def get_authority(self) -> SourceAuthority:
        return SourceAuthority.NEWS

    def supports_incremental(self) -> bool:
        return True

    def supports_discovery(self) -> bool:
        return True
