"""LLM Provider Health Checker.

⚠️ DEPRECATED: This module has been split into solstein.llm.health package.
For new code, use: from solstein.llm.health import HealthChecker

This file is kept for backward compatibility and re-exports all symbols.
"""

from __future__ import annotations

# Re-export from the new modular package
from datetime import datetime, timedelta, timezone

from .health import (
    HealthChecker,
    ProviderError,
    ProviderErrorType,
    ProviderHealth,
    ProviderStatus,
)


class ProviderHealthChecker(HealthChecker):
    def get_health(self, provider: str) -> ProviderHealth | None:
        return self.get_cached_health(provider)

    def report_success(self, provider: str) -> ProviderHealth:
        health = self._healthy(provider)
        health.total_successes = 1
        self.cache_health(provider, health)
        return health

    def report_error(self, provider: str, error: Exception) -> ProviderHealth:
        classified = self.error_classifier.classify(error, provider)
        health = self._unhealthy_from_error(provider, classified)
        health.consecutive_failures = 1
        health.total_failures = 1
        if classified.retry_after_seconds:
            health.retry_after = datetime.now(timezone.utc) + timedelta(seconds=classified.retry_after_seconds)
        self.cache_health(provider, health)
        return health

    def should_retry(self, provider: str) -> bool:
        health = self.get_cached_health(provider)
        return True if health is None else health.should_retry

    def get_retry_delay(self, provider: str) -> float:
        health = self.get_cached_health(provider)
        if health is None or health.retry_after is None:
            return 1.0
        delay = (health.retry_after - datetime.now(timezone.utc)).total_seconds()
        return max(delay, 0.0)


# Backward compatibility aliases
ProviderHealthStatus = ProviderStatus
HealthCheckResult = ProviderHealth

__all__ = [
    "HealthCheckResult",
    "ProviderError",
    "ProviderErrorType",
    "ProviderHealth",
    "ProviderHealthChecker",
    "ProviderHealthStatus",
    "ProviderStatus",
    "get_health_checker",
    "reset_health_checker",
]

# Singleton instance for get_health_checker
_health_checker_instance: ProviderHealthChecker | None = None


def get_health_checker() -> ProviderHealthChecker:
    """Get singleton health checker instance."""
    global _health_checker_instance
    if _health_checker_instance is None:
        _health_checker_instance = ProviderHealthChecker()
    return _health_checker_instance


def reset_health_checker() -> None:
    """Reset singleton instance (useful for testing)."""
    global _health_checker_instance
    _health_checker_instance = None
