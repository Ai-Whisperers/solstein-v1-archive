"""News refresh connector for press coverage and sentiment updates.

Uses NewsAPI or Google web search to fetch company news.
Implements incremental refresh with date-based delta detection.
"""

from datetime import datetime, timedelta
from typing import Any

from loguru import logger

from solstein.data.additional_sources import AdditionalDataSources
from solstein.infrastructure.conflict_resolution import SourceAuthority
from solstein.infrastructure.refresh import BaseRefreshConnector


class NewsRefreshConnector(BaseRefreshConnector):
    """News refresh connector for press coverage and sentiment analysis.

    Fetches news data including:
    - Article count and sources
    - Sentiment analysis
    - Key topics and themes
    - Recent press coverage

    Confidence: 0.72 (moderate, varies by source)
    """

    def __init__(self, db_manager, news_api_key: str | None = None):
        super().__init__(
            source_name="news",
            source_type="press_coverage",
            db_manager=db_manager,
            confidence=0.72,
        )
        self.news_api_key = news_api_key
        self.client = AdditionalDataSources(news_api_key=news_api_key)

    async def fetch_facts(
        self,
        company_ids: list[str],
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch news coverage facts for companies.

        Args:
            company_ids: List of company names to search news for
            start_date: Start date for news search (default: 30 days ago)
            end_date: End date for news search (default: now)

        Returns:
            List of fact dictionaries with news data
        """
        logger.info(f"Fetching news coverage for {len(company_ids)} companies")
        facts = []

        # Default to last 30 days if no dates specified
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=30)

        days_back = (end_date - start_date).days

        for company_name in company_ids:
            try:
                coverage = self.client.get_news(company_name, days_back=days_back)

                # Calculate confidence based on data source
                confidence = 0.6 if self.news_api_key else 0.4

                facts.append(
                    {
                        "company_id": company_name,
                        "fact_type": "press_coverage",
                        "value": {
                            "total_articles": coverage.total_articles,
                            "sentiment_score": coverage.sentiment_score,
                            "days_back": days_back,
                        },
                        "confidence": confidence,
                        "extracted_at": datetime.now(),
                        "source": self.source_name,
                        "metadata": {
                            "company_name": company_name,
                            "backend": "newsapi" if self.news_api_key else "web_scrape",
                        },
                    }
                )

                # Add sentiment fact separately
                if coverage.sentiment_score is not None:
                    facts.append(
                        {
                            "company_id": company_name,
                            "fact_type": "news_sentiment",
                            "value": {
                                "score": coverage.sentiment_score,
                                "interpretation": self._interpret_sentiment(coverage.sentiment_score),
                            },
                            "confidence": confidence,
                            "extracted_at": datetime.now(),
                            "source": self.source_name,
                            "metadata": {
                                "company_name": company_name,
                                "total_articles": coverage.total_articles,
                            },
                        }
                    )

            except Exception as e:
                logger.warning(f"Failed to fetch news for {company_name}: {e}")
                continue

        return facts

    def _interpret_sentiment(self, score: float) -> str:
        """Interpret sentiment score as human-readable label."""
        if score > 0.2:
            return "positive"
        elif score < -0.2:
            return "negative"
        return "neutral"

    def get_authority(self) -> SourceAuthority:
        """Return News authority level."""
        return SourceAuthority.NEWS

    def supports_incremental(self) -> bool:
        """News supports incremental refresh via hash comparison."""
        return True
