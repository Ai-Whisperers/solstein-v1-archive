"""News data sources for Solstein."""

from __future__ import annotations

from datetime import datetime, timedelta
from urllib.parse import quote

import requests
from loguru import logger

from .base import analyze_sentiment
from .models import NewsArticle, PressCoverage


class NewsSource:
    """News API and web search data source."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key

    def get_news(self, company_name: str, days_back: int = 30) -> PressCoverage:
        """
        Get news coverage for a company.

        First tries NewsAPI.org, falls back to web search if API unavailable.
        """
        if self.api_key:
            result = self._get_news_from_api(company_name, days_back)
            if result.total_articles > 0:
                return result
            logger.info("NewsAPI returned no results, trying web search fallback")

        return self._get_news_from_web_search(company_name, days_back)

    def _get_news_from_api(self, company_name: str, days_back: int) -> PressCoverage:
        """Get news using NewsAPI.org."""
        if not self.api_key:
            return self._empty_coverage()

        from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

        url = "https://newsapi.org/v2/everything"
        params = {
            "q": company_name,
            "from": from_date,
            "sortBy": "relevancy",
            "pageSize": 50,
            "apiKey": self.api_key,
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            articles = []
            positive = 0
            negative = 0
            neutral = 0

            for article in data.get("articles", [])[:20]:
                published = article.get("publishedAt")
                if published:
                    published = datetime.fromisoformat(published.replace("Z", "+00:00"))

                sentiment = analyze_sentiment(article.get("title", "") + " " + (article.get("description") or ""))

                if sentiment == "positive":
                    positive += 1
                elif sentiment == "negative":
                    negative += 1
                else:
                    neutral += 1

                articles.append(
                    NewsArticle(
                        title=article.get("title", ""),
                        description=article.get("description"),
                        source=article.get("source", {}).get("name", "Unknown"),
                        url=article.get("url", ""),
                        published_at=published or datetime.now(),
                        sentiment=sentiment,
                    )
                )

            total = len(articles)
            sentiment_score = (positive - negative) / total if total > 0 else None

            return PressCoverage(
                articles=articles,
                total_articles=total,
                positive_count=positive,
                negative_count=negative,
                neutral_count=neutral,
                sentiment_score=sentiment_score,
            )

        except Exception as e:
            logger.error(f"Error fetching news from API: {e}")
            return self._empty_coverage()

    def _get_news_from_web_search(self, company_name: str, days_back: int) -> PressCoverage:
        """
        Get news using web search as fallback.

        This method is used when:
        - NewsAPI key is not configured
        - NewsAPI returns no results
        - NewsAPI quota is exhausted
        """
        try:
            search_url = f"https://www.google.com/search?q={quote(company_name)}+news&tbs=qdr:w"

            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

            response = requests.get(search_url, headers=headers, timeout=15)
            html = response.text

            import re

            articles = []
            positive = 0
            negative = 0
            neutral = 0

            news_pattern = re.compile(r'<a href="(https?://[^"]+)"[^>]*>([^<]+)</a>')
            matches = news_pattern.findall(html)
            seen_urls = set()

            for url, title in matches[:20]:
                if any(
                    skip in url
                    for skip in [
                        "google",
                        "youtube",
                        "facebook",
                        "twitter",
                        "wikipedia",
                    ]
                ):
                    continue
                if url in seen_urls:
                    continue
                seen_urls.add(url)

                sentiment = analyze_sentiment(title)
                if sentiment == "positive":
                    positive += 1
                elif sentiment == "negative":
                    negative += 1
                else:
                    neutral += 1

                articles.append(
                    NewsArticle(
                        title=title[:200] if title else "No title",
                        description=None,
                        source=url.split("/")[2] if len(url.split("/")) > 2 else "Web",
                        url=url,
                        published_at=datetime.now(),
                        sentiment=sentiment,
                    )
                )

            total = len(articles)
            sentiment_score = (positive - negative) / total if total > 0 else None

            if total > 0:
                logger.info(f"Found {total} news articles via web search for {company_name}")

            return PressCoverage(
                articles=articles,
                total_articles=total,
                positive_count=positive,
                negative_count=negative,
                neutral_count=neutral,
                sentiment_score=sentiment_score,
            )

        except Exception as e:
            logger.error(f"Error fetching news from web search: {e}")
            return self._empty_coverage()

    def _empty_coverage(self) -> PressCoverage:
        """Return empty press coverage."""
        return PressCoverage(
            articles=[],
            total_articles=0,
            positive_count=0,
            negative_count=0,
            neutral_count=0,
            sentiment_score=None,
        )
