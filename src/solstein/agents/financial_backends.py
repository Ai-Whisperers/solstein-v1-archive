"""Financial backend dispatching: Yahoo Finance primary with circuit breaker, Alpha Vantage fallback.

STORY-103: Stabilize Yahoo Finance integration with circuit breaker,
consecutive failure detection, and data freshness tracking.

Pipeline:
1. Yahoo Finance via yfinance (wrapped in circuit breaker + retry)
2. Alpha Vantage fallback (when API key configured)
3. Consecutive failure detection -> DEGRADED state
4. Data freshness metadata on all results
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from solstein.config import get_settings
from solstein.connectors.base import RawData

from .resilience import CircuitBreaker, RetryConfig, call_with_retry

logger = logging.getLogger(__name__)

# Data freshness SLA: market data considered stale after 24 hours
DATA_FRESHNESS_HOURS = 24

# Consecutive failures before marking source as DEGRADED
DEGRADED_THRESHOLD = 3

# Retry config tuned for financial data sources
FINANCIAL_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    base_delay=2.0,
    exponential_base=2.0,
    max_delay=15.0,
    timeout=20.0,
)


@dataclass
class SourceHealthStatus:
    """Tracks health of a financial data source."""

    name: str
    consecutive_failures: int = 0
    last_success: datetime | None = None
    last_failure: datetime | None = None
    is_degraded: bool = False

    def record_success(self) -> None:
        """Record a successful fetch."""
        self.consecutive_failures = 0
        self.last_success = datetime.now(timezone.utc)
        if self.is_degraded:
            self.is_degraded = False
            logger.info(
                "[FinancialHealth] Source %s recovered from DEGRADED state",
                self.name,
            )

    def record_failure(self, reason: str) -> None:
        """Record a failed fetch. Mark DEGRADED after threshold."""
        self.consecutive_failures += 1
        self.last_failure = datetime.now(timezone.utc)

        if self.consecutive_failures >= DEGRADED_THRESHOLD and not self.is_degraded:
            self.is_degraded = True
            logger.warning(
                "[FinancialHealth] Source %s marked DEGRADED after %d consecutive failures. Last reason: %s",
                self.name,
                self.consecutive_failures,
                reason,
            )


def compute_data_freshness(extracted_at: datetime) -> dict[str, Any]:
    """Compute data freshness metadata for a financial data result.

    Returns:
        Dict with freshness fields: data_freshness, fetched_at,
        staleness_hours, is_stale.
    """
    now = datetime.now(timezone.utc)
    age_hours = (now - extracted_at).total_seconds() / 3600.0
    is_stale = age_hours > DATA_FRESHNESS_HOURS

    if is_stale:
        freshness = "stale"
    elif age_hours > DATA_FRESHNESS_HOURS / 2:
        freshness = "aging"
    else:
        freshness = "fresh"

    return {
        "data_freshness": freshness,
        "fetched_at": extracted_at.isoformat(),
        "staleness_hours": round(age_hours, 2),
        "is_stale": is_stale,
    }


def add_freshness_metadata(results: list[RawData]) -> list[RawData]:
    """Add data_freshness metadata to each RawData result."""
    for result in results:
        freshness = compute_data_freshness(result.extracted_at)
        result.metadata.update(freshness)
    return results


class FinancialBackendDispatcher:
    """Dispatches financial queries with circuit breaker and fallback.

    Pipeline:
    1. Yahoo Finance (yfinance) with circuit breaker + retry
    2. Alpha Vantage fallback (when API key configured)
    3. All results annotated with data_freshness metadata
    """

    def __init__(
        self,
        alpha_vantage_key: str | None = None,
    ) -> None:
        _settings = get_settings()
        self.alpha_vantage_key = alpha_vantage_key

        self.circuit_breaker_yf = CircuitBreaker(
            failure_threshold=_settings.circuit_breaker.failure_threshold,
            recovery_timeout=_settings.circuit_breaker.recovery_timeout,
            name="YahooFinance",
        )
        self.yf_health = SourceHealthStatus(name="yahoo_finance")
        self.av_health = SourceHealthStatus(name="alpha_vantage")

    async def search(self, ticker: str, **kwargs: Any) -> list[RawData]:
        """Search financial backends for ticker data."""
        # 1. Yahoo Finance (primary, with circuit breaker)
        yf_results = await self._search_yahoo(ticker, **kwargs)
        if yf_results:
            self.yf_health.record_success()
            logger.info("[FinancialDispatcher] Yahoo Finance returned data for %s", ticker)
            return add_freshness_metadata(yf_results)

        # Yahoo failed — record and check for degraded
        self.yf_health.record_failure(f"No data returned for {ticker}")

        # 2. Alpha Vantage fallback (only if key configured)
        if self.alpha_vantage_key:
            logger.warning(
                "[FinancialDispatcher] Yahoo Finance unavailable for %s, falling back to Alpha Vantage",
                ticker,
            )
            av_results = await self._search_alpha_vantage(ticker, **kwargs)
            if av_results:
                self.av_health.record_success()
                logger.info("[FinancialDispatcher] Alpha Vantage returned data for %s", ticker)
                return add_freshness_metadata(av_results)
            self.av_health.record_failure(f"No data returned for {ticker}")

        logger.warning(
            "[FinancialDispatcher] All financial backends returned empty for: %s",
            ticker,
        )
        return []

    async def _search_yahoo(self, ticker: str, **kwargs: Any) -> list[RawData] | None:
        """Query Yahoo Finance with circuit breaker + retry."""
        try:
            from solstein.connectors.financial.yahoo_finance import YahooFinanceConnector

            connector = YahooFinanceConnector()
            result = await call_with_retry(
                lambda t=ticker, kw=kwargs: connector.search(t, **kw),
                retry_config=FINANCIAL_RETRY_CONFIG,
                circuit_breaker=self.circuit_breaker_yf,
                name="yahoo_finance_search",
            )
            if result.success and result.data:
                # Validate: check if market_cap is present (None = scraping may be broken)
                for item in result.data:
                    content = item.raw_content
                    if content.get("marketCap") is None:
                        logger.warning(
                            "[YahooFinance] marketCap is None for %s — yfinance scraping may be broken",
                            ticker,
                        )
                return result.data
            if result.error_message:
                logger.warning("[YahooFinance] Search failure: %s", result.error_message)
            return None
        except Exception as exc:
            logger.warning("[YahooFinance] Search failed: %s", exc)
            return None

    async def _search_alpha_vantage(self, ticker: str, **kwargs: Any) -> list[RawData] | None:
        """Query Alpha Vantage as fallback."""
        if not self.alpha_vantage_key:
            return None

        try:
            from solstein.connectors.financial import AlphaVantageConnector

            connector = AlphaVantageConnector(api_key=self.alpha_vantage_key)
            result = await connector.search(ticker, **kwargs)
            if result.success and result.data:
                return result.data
            if result.error_message:
                logger.warning("[AlphaVantage] Search failure: %s", result.error_message)
            return None
        except Exception as exc:
            logger.warning("[AlphaVantage] Search failed: %s", exc)
            return None

    def get_health_status(self) -> dict[str, Any]:
        """Return health status of all financial backends."""
        return {
            "yahoo_finance": {
                "consecutive_failures": self.yf_health.consecutive_failures,
                "is_degraded": self.yf_health.is_degraded,
                "last_success": (self.yf_health.last_success.isoformat() if self.yf_health.last_success else None),
                "circuit_breaker_state": self.circuit_breaker_yf.get_state(),
            },
            "alpha_vantage": {
                "configured": self.alpha_vantage_key is not None,
                "consecutive_failures": self.av_health.consecutive_failures,
                "is_degraded": self.av_health.is_degraded,
            },
        }
