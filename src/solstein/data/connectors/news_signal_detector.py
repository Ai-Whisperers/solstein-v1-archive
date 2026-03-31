"""News Signal Detector for Solstein.

EPIC-042: News Signal Detection
EPIC-022: Refactored to use Strategy Pattern

Detects funding rounds, partnerships, and key hires from NewsAPI.
Uses modular signal detectors for each signal type.

Features:
- Funding signal detection (Series A/B/C, raised, investment)
- Partnership detection (collaboration, integration, partnership)
- Key hire detection (appoints, joins, new CEO, executive)
- Deduplication by (company_id, signal_type, date)
- Rate limit tracking (100 queries/day limit)
- Confidence scoring (0.70-0.75 for news signals)
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import httpx
from loguru import logger

from .constants import (
    HTTP_STATUS_RATE_LIMITED,
    NEWS_SIGNAL_DAILY_QUERY_LIMIT,
    NEWS_SIGNAL_REQUEST_TIMEOUT_S,
)
from .contracts import ConnectorRequest, ConnectorResponse
from .runtime import ConnectorRuntime
from .signal_detectors import (
    FundingSignalDetector,
    KeyHireSignalDetector,
    PartnershipSignalDetector,
    Signal,
)


class NewsSignalDetector:
    """Detect market signals from news articles using Strategy Pattern.

    EPIC-022: Refactored to delegate to specialized signal detectors.
    Each signal type (funding, partnership, key hire) has its own
    detector with specific patterns and confidence scoring.

    Confidence Scoring:
    - Funding signals: 0.75 (news can be speculative)
    - Partnership signals: 0.72 (requires confirmation)
    - Key hire signals: 0.70 (often announced but may not materialize)
    """

    def __init__(self, api_key: str | None = None):
        """Initialize NewsSignalDetector with signal detectors.

        Args:
            api_key: NewsAPI key. If None, reads from NEWSAPI_KEY env var.

        Raises:
            ValueError: If no API key provided and NEWSAPI_KEY not in environment.
        """
        from solstein.config import get_settings
        from solstein.infrastructure.retry_policy import CircuitBreaker, RetryPolicy

        settings = get_settings()
        self.api_key = api_key or settings.news_api_key
        if not self.api_key:
            raise ValueError("NewsAPI key required. Set NEWSAPI_KEY env var or pass api_key parameter.")

        # Initialize signal detectors (Strategy Pattern)
        self._detectors = [
            FundingSignalDetector(),
            PartnershipSignalDetector(),
            KeyHireSignalDetector(),
        ]
        self._runtime = ConnectorRuntime(
            retry_policy=RetryPolicy(
                max_attempts=settings.connector_max_attempts,
                base_delay_seconds=settings.connector_retry_base_delay,
                max_delay_seconds=settings.connector_retry_max_delay,
            ),
            circuit_breaker=CircuitBreaker(
                failure_threshold=settings.connector_circuit_failure_threshold,
                cooldown_seconds=settings.connector_circuit_cooldown_seconds,
            ),
        )

        # Rate limit tracking
        self._daily_query_count = 0
        self._last_reset = datetime.now()
        self._seen_signals: set[str] = set()

    def _reset_daily_counter(self) -> None:
        """Reset daily query counter if day has changed."""
        now = datetime.now()
        if now.date() != self._last_reset.date():
            self._daily_query_count = 0
            self._last_reset = now
            logger.info("Daily query counter reset")

    def _check_rate_limit(self) -> None:
        """Check if we've hit the rate limit."""
        self._reset_daily_counter()
        if self._daily_query_count >= NEWS_SIGNAL_DAILY_QUERY_LIMIT:
            raise RuntimeError(f"Daily query limit reached ({NEWS_SIGNAL_DAILY_QUERY_LIMIT})")

    async def _search_news(self, query: str) -> list[dict[str, Any]]:
        """Search news articles via NewsAPI.

        Args:
            query: Search query

        Returns:
            List of article dictionaries
        """
        self._check_rate_limit()

        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "apiKey": self.api_key,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 20,
        }

        async with httpx.AsyncClient(timeout=NEWS_SIGNAL_REQUEST_TIMEOUT_S) as client:
            try:
                response = await client.get(url, params=params)

                if response.status_code == HTTP_STATUS_RATE_LIMITED:
                    raise RuntimeError("NewsAPI rate limit exceeded")

                response.raise_for_status()
                data = response.json()

                self._daily_query_count += 1

                if data.get("status") != "ok":
                    logger.warning("NewsAPI error", error=data.get("message"))
                    return []

                return data.get("articles", [])

            except httpx.HTTPStatusError as e:
                logger.error("NewsAPI HTTP error", status=e.response.status_code, error=str(e))
                raise
            except Exception as e:
                logger.error("NewsAPI request failed", error=str(e))
                raise

    def _is_duplicate(self, signal: Signal) -> bool:
        """Check if signal is a duplicate.

        Args:
            signal: Signal to check

        Returns:
            True if duplicate, False otherwise
        """
        # Create unique key
        key = f"{signal.company_name}:{signal.signal_type}:{signal.detected_at.date()}"

        if key in self._seen_signals:
            return True

        self._seen_signals.add(key)
        return False

    async def detect_signals(
        self,
        company_name: str,
        signal_types: list[str] | None = None,
    ) -> list[Signal]:
        """Detect all signal types for a company.

        Args:
            company_name: Company name to search
            signal_types: Optional list of signal types to detect

        Returns:
            List of detected signals
        """
        # Filter detectors by signal type
        detectors = self._detectors
        if signal_types:
            detectors = [d for d in self._detectors if d.signal_type in signal_types]

        all_signals: list[Signal] = []

        # Search for news about company
        query = f'"{company_name}" AND (funding OR investment OR partnership OR appoints OR hires)'
        articles = await self._search_news(query)

        logger.info(f"Found {len(articles)} articles for {company_name}")

        # Run each detector on each article
        for article in articles:
            for detector in detectors:
                signals = detector.detect(article, company_name)

                for signal in signals:
                    if not self._is_duplicate(signal):
                        all_signals.append(signal)
                        logger.info(
                            f"Detected {signal.signal_type} signal for {company_name}",
                            confidence=signal.confidence,
                            source=signal.source,
                        )

        return all_signals

    async def detect_signals_enveloped(
        self,
        company_name: str,
        signal_types: list[str] | None = None,
    ) -> ConnectorResponse[list[Signal]]:
        request = ConnectorRequest(
            connector="news_signal_detector",
            operation="detect_signals",
            inputs={
                "company_name": company_name,
                "signal_types": signal_types,
            },
        )

        async def _operation() -> list[Signal]:
            return await self.detect_signals(company_name, signal_types)

        return await self._runtime.run(
            request=request,
            operation=_operation,
            retryable_exceptions=(httpx.HTTPError, RuntimeError, TimeoutError),
            empty_is_degraded=True,
            empty_error="No signals detected",
            extra_metadata={"detector_count": len(self._detectors)},
        )

    # Convenience methods for specific signal types
    async def detect_funding_signal(self, company_name: str) -> list[Signal]:
        """Detect funding signals for a company."""
        return await self.detect_signals(company_name, ["funding"])

    async def detect_partnership_signal(self, company_name: str) -> list[Signal]:
        """Detect partnership signals for a company."""
        return await self.detect_signals(company_name, ["partnership"])

    async def detect_key_hire_signal(self, company_name: str) -> list[Signal]:
        """Detect key hire signals for a company."""
        return await self.detect_signals(company_name, ["key_hire"])

    def get_rate_limit_status(self) -> dict[str, Any]:
        """Get current rate limit status.

        Returns:
            Dictionary with rate limit info
        """
        self._reset_daily_counter()
        return {
            "daily_limit": NEWS_SIGNAL_DAILY_QUERY_LIMIT,
            "queries_used": self._daily_query_count,
            "queries_remaining": NEWS_SIGNAL_DAILY_QUERY_LIMIT - self._daily_query_count,
            "last_reset": self._last_reset.isoformat(),
        }

    def clear_seen_signals(self) -> None:
        """Clear the seen signals cache."""
        self._seen_signals.clear()
        logger.info("Seen signals cache cleared")
