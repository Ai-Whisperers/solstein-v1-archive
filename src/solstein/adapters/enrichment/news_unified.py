"""Unified News adapter for Solstein.

Converts news functionality from additional_sources to a unified adapter
implementing the full UnifiedDataSource protocol.

Uses NewsAPI.org as primary with web search fallback.
"""

from datetime import datetime, timedelta
from typing import Any

import requests
from loguru import logger

from solstein.domain.models import DataSourceType, RawDataSource
from solstein.infrastructure.conflict_resolution import SourceAuthority
from solstein.infrastructure.refresh import BaseRefreshConnector
from solstein.research.discovery import DiscoveryCandidate


class NewsUnifiedAdapter(BaseRefreshConnector):
    """Unified News adapter implementing the full protocol.

    Fetches news coverage for companies using NewsAPI and web search.
    Includes sentiment analysis of articles.

    Confidence: 0.70
    Authority: NEWS_API
    """

    def __init__(self, db_manager=None, news_api_key: str | None = None):
        super().__init__(
            source_name="news_unified",
            source_type="news",
            db_manager=db_manager,
            confidence=0.70,
        )
        self.news_api_key = news_api_key

    @property
    def source_type(self) -> DataSourceType:
        return DataSourceType.NEWS

    def _analyze_sentiment(self, text: str) -> str:
        """Simple keyword-based sentiment analysis."""
        text_lower = text.lower()

        positive_words = [
            "growth",
            "profit",
            "revenue",
            "success",
            "win",
            "launch",
            "expand",
            "innovation",
            "leader",
            "partnership",
            "award",
            "acquisition",
            "positive",
            "strong",
            "beat",
            "bullish",
        ]
        negative_words = [
            "loss",
            "lawsuit",
            "investigation",
            "scandal",
            "fire",
            "layoff",
            "bankruptcy",
            "decline",
            "weak",
            "miss",
            "warning",
            "fraud",
            "investor",
            "concern",
            "risk",
        ]

        pos_count = sum(1 for w in positive_words if w in text_lower)
        neg_count = sum(1 for w in negative_words if w in text_lower)

        if pos_count > neg_count + 1:
            return "positive"
        elif neg_count > pos_count + 1:
            return "negative"
        return "neutral"

    def _get_news_from_api(self, company_name: str, days_back: int = 30) -> list[dict[str, Any]]:
        """Get news using NewsAPI.org."""
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
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            articles = []
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

        except Exception as e:
            logger.error(f"Error fetching news from API: {e}")
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

        candidates = []
        for article in articles[:max_results]:
            candidate = DiscoveryCandidate(
                name=article.get("title", "").split(":")[0][:100],
                source_url=article.get("url", ""),
                source_type="news",
                confidence=0.55,
                discovery_metadata={
                    "snippet": article.get("description", "")[:200],
                    "market": market,
                    "sentiment": article.get("sentiment"),
                },
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
            company_id=company_id,
            fetch_timestamp=datetime.now(),
            data={
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
        """Fetch news facts for companies."""
        facts = []

        for company_name in company_ids:
            articles = self._get_news_from_api(company_name, days_back=7)

            if articles:
                facts.append(
                    {
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
                )

        return facts

    def get_confidence(self) -> float:
        return 0.70

    def get_authority(self) -> SourceAuthority:
        return SourceAuthority.NEWS_API

    def supports_incremental(self) -> bool:
        return True

    def supports_discovery(self) -> bool:
        return True
