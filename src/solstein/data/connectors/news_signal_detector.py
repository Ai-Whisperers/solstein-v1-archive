"""

News Signal Detector for Solstein.



Detects funding rounds, partnerships, and key hires from NewsAPI.

Provides pattern-based signal extraction with confidence scoring.



Features:

- Funding signal detection (Series A/B/C, raised, investment)

- Partnership detection (collaboration, integration, partnership)

- Key hire detection (appoints, joins, new CEO, executive)

- Deduplication by (company_id, signal_type, date)

- Rate limit tracking (100 queries/day limit)

- Confidence scoring (0.70-0.75 for news signals)

"""

import re
from datetime import datetime, timedelta
from typing import Any

import requests
from loguru import logger

from solstein.data.connectors.constants import (
    HTTP_STATUS_RATE_LIMITED,
    NEWS_SIGNAL_DAILY_QUERY_LIMIT,
    NEWS_SIGNAL_REQUEST_TIMEOUT_S,
)


class NewsSignalDetector:
    """
    Detect market signals from news articles using NewsAPI.

    Confidence Scoring:
    - Funding signals: 0.75 (news can be speculative)
    - Partnership signals: 0.72 (requires confirmation)
    - Key hire signals: 0.70 (often announced but may not materialize)
    """

    # Pattern definitions for signal detection
    FUNDING_PATTERNS = [
        r"Series\s+[A-Z]",  # Series A, Series B, etc.
        r"raised\s+\$[\d,]+\s*(?:million|billion|M|B)",
        r"\$[\d,]+\s*(?:million|billion|M|B)\s+(?:funding|investment|round)",
        r"funding\s+round",
        r"investment\s+round",
        r"announced\s+funding",
        r"secured\s+\$[\d,]+",
    ]

    PARTNERSHIP_PATTERNS = [
        r"partnership",
        r"collaboration",
        r"integrates\s+with",
        r"announces\s+partnership",
        r"partners\s+with",
        r"strategic\s+alliance",
        r"joint\s+venture",
        r"announces\s+collaboration",
    ]

    KEY_HIRE_PATTERNS = [
        r"appoints\s+(?:new\s+)?(?:CEO|CTO|CFO|COO|Chief)",
        r"joins\s+as\s+(?:CEO|CTO|CFO|COO|Chief)",
        r"new\s+(?:CEO|CTO|CFO|COO|Chief)",
        r"hires\s+(?:new\s+)?(?:CEO|CTO|CFO|COO|Chief)",
        r"executive\s+(?:appointment|hire|joins)",
        r"appoints\s+new\s+executive",
    ]

    def __init__(self, api_key: str | None = None):
        """
        Initialize NewsSignalDetector.

        Args:
            api_key: NewsAPI key. If None, reads from NEWSAPI_KEY env var.

        Raises:
            ValueError: If no API key provided and NEWSAPI_KEY not in environment.
        """
        from solstein.config import get_settings

        settings = get_settings()
        self.api_key = api_key or settings.news_api_key
        if not self.api_key:
            raise ValueError("NewsAPI key required. Set NEWSAPI_KEY env var or pass api_key parameter.")

        self.base_url = "https://newsapi.org/v2"
        self.daily_query_limit = NEWS_SIGNAL_DAILY_QUERY_LIMIT
        self.queries_today = 0
        self.last_reset = datetime.now().date()
        self.seen_signals = set()  # For deduplication

        logger.info("NewsSignalDetector initialized")

    def _reset_daily_counter(self) -> None:
        """Reset daily query counter if date changed."""
        today = datetime.now().date()
        if today != self.last_reset:
            self.queries_today = 0
            self.last_reset = today
            logger.info(f"Daily query counter reset for {today}")

    def _check_rate_limit(self) -> None:
        """Check if approaching daily rate limit."""
        self._reset_daily_counter()

        if self.queries_today >= self.daily_query_limit:
            logger.error(f"Daily query limit reached: {self.queries_today}/{self.daily_query_limit}")
            raise RuntimeError("NewsAPI daily query limit exceeded (100/day)")

        if self.queries_today >= NEWS_SIGNAL_DAILY_QUERY_LIMIT - 10:
            logger.warning(f"Approaching daily limit: {self.queries_today}/{self.daily_query_limit}")

    def _search_news(self, query: str) -> list[dict[str, Any]]:
        """
        Search news articles using NewsAPI.

        Args:
            query: Search query string

        Returns:
            List of article dictionaries from NewsAPI

        Raises:
            RuntimeError: If API call fails or rate limit exceeded
        """
        self._check_rate_limit()

        try:
            params = {
                "q": query,
                "apiKey": self.api_key,
                "sortBy": "publishedAt",
                "language": "en",
                "pageSize": 100,
            }

            response = requests.get(
                f"{self.base_url}/everything",
                params=params,
                timeout=NEWS_SIGNAL_REQUEST_TIMEOUT_S,
            )
            self.queries_today += 1

            if response.status_code == HTTP_STATUS_RATE_LIMITED:
                logger.error("NewsAPI rate limit hit (429)")
                raise RuntimeError("NewsAPI rate limit exceeded")

            if response.status_code != 200:
                logger.error(f"NewsAPI error {response.status_code}: {response.text}")
                raise RuntimeError(f"NewsAPI error: {response.status_code}")

            data = response.json()
            if data.get("status") != "ok":
                logger.error(f"NewsAPI error: {data.get('message')}")
                raise RuntimeError(f"NewsAPI error: {data.get('message')}")

            articles = data.get("articles", [])
            logger.info(f"Found {len(articles)} articles for query: {query}")
            return articles

        except requests.RequestException as e:
            logger.error(f"Request error searching news: {e}")
            raise RuntimeError(f"Failed to search news: {e}") from e

    def _match_patterns(self, text: str, patterns: list[str]) -> bool:
        """
        Check if text matches any pattern (case-insensitive).

        Args:
            text: Text to search
            patterns: List of regex patterns

        Returns:
            True if any pattern matches
        """
        text_lower = text.lower()
        return any(re.search(pattern, text_lower, re.IGNORECASE) for pattern in patterns)

    def _extract_signals(
        self,
        articles: list[dict[str, Any]],
        company_name: str,
        signal_type: str,
        patterns: list[str],
        confidence: float,
    ) -> list[dict[str, Any]]:
        """
        Extract signals from articles matching patterns.

        Args:
            articles: List of articles from NewsAPI
            company_name: Company name for deduplication
            signal_type: Type of signal (funding, partnership, key_hire)
            patterns: List of regex patterns to match
            confidence: Confidence score for this signal type

        Returns:
            List of signal dictionaries
        """
        signals = []

        for article in articles:
            title = article.get("title", "")
            description = article.get("description", "")
            content = article.get("content", "")
            published_at = article.get("publishedAt", "")
            url = article.get("url", "")
            source = article.get("source", {}).get("name", "Unknown")

            # Combine text for pattern matching
            full_text = f"{title} {description} {content}".lower()

            # Check if patterns match
            if not self._match_patterns(full_text, patterns):
                continue

            # Parse date
            try:
                signal_date = datetime.fromisoformat(published_at.replace("Z", "+00:00")).date()
            except (ValueError, AttributeError):
                signal_date = datetime.now().date()

            # Create deduplication key
            dedup_key = (company_name.lower(), signal_type, str(signal_date))
            if dedup_key in self.seen_signals:
                logger.debug(f"Skipping duplicate signal: {company_name} {signal_type} {signal_date}")
                continue

            self.seen_signals.add(dedup_key)

            signal = {
                "company_name": company_name,
                "signal_type": signal_type,
                "title": title,
                "description": description,
                "source": source,
                "url": url,
                "published_at": published_at,
                "signal_date": signal_date.isoformat(),
                "confidence": confidence,
                "detected_at": datetime.now().isoformat(),
            }

            signals.append(signal)
            logger.info(f"Detected {signal_type} signal for {company_name}: {title[:60]}...")

        return signals

    def detect_funding_signal(self, company_name: str) -> list[dict[str, Any]]:
        """
        Detect funding round announcements for a company.

        Args:
            company_name: Company name to search

        Returns:
            List of funding signals with confidence 0.75

        Raises:
            RuntimeError: If API call fails
        """
        logger.info(f"Detecting funding signals for: {company_name}")

        try:
            articles = self._search_news(company_name)
            signals = self._extract_signals(
                articles,
                company_name,
                "funding_round",
                self.FUNDING_PATTERNS,
                0.75,
            )
            return signals

        except RuntimeError as e:
            logger.error(f"Failed to detect funding signals: {e}")
            raise

    def detect_partnership_signal(self, company_name: str) -> list[dict[str, Any]]:
        """
        Detect partnership announcements for a company.

        Args:
            company_name: Company name to search

        Returns:
            List of partnership signals with confidence 0.72

        Raises:
            RuntimeError: If API call fails
        """
        logger.info(f"Detecting partnership signals for: {company_name}")

        try:
            articles = self._search_news(company_name)
            signals = self._extract_signals(
                articles,
                company_name,
                "partnership",
                self.PARTNERSHIP_PATTERNS,
                0.72,
            )
            return signals

        except RuntimeError as e:
            logger.error(f"Failed to detect partnership signals: {e}")
            raise

    def detect_key_hire_signal(self, company_name: str) -> list[dict[str, Any]]:
        """
        Detect key hire announcements for a company.

        Args:
            company_name: Company name to search

        Returns:
            List of key hire signals with confidence 0.70

        Raises:
            RuntimeError: If API call fails
        """
        logger.info(f"Detecting key hire signals for: {company_name}")

        try:
            articles = self._search_news(company_name)
            signals = self._extract_signals(
                articles,
                company_name,
                "key_hire",
                self.KEY_HIRE_PATTERNS,
                0.70,
            )
            return signals

        except RuntimeError as e:
            logger.error(f"Failed to detect key hire signals: {e}")
            raise

    def get_rate_limit_status(self) -> dict[str, Any]:
        """
        Get current rate limit status.

        Returns:
            Dictionary with queries_used, queries_remaining, reset_time
        """
        self._reset_daily_counter()

        remaining = max(0, self.daily_query_limit - self.queries_today)
        reset_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

        return {
            "queries_used": self.queries_today,
            "queries_remaining": remaining,
            "daily_limit": self.daily_query_limit,
            "reset_time": reset_time.isoformat(),
        }

    def clear_seen_signals(self) -> None:
        """Clear the deduplication cache."""
        self.seen_signals.clear()
        logger.info("Cleared deduplication cache")
