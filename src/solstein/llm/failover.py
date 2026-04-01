"""Provider failover and retry logic for LLM calls.

STORY-071: Extracted from enhanced_client.py to keep the main client
under 100 lines. Contains retry decision logic and provider attempt tracking.
"""

from __future__ import annotations

import asyncio
from typing import Any

from .health_checker import (
    ProviderErrorType,
    ProviderHealthChecker,
)


class ProviderAttempt:
    """Record of a single provider attempt (success or failure)."""

    def __init__(
        self,
        provider: str,
        attempt: int,
        result: Any = None,
        error: str | None = None,
        error_type: str | None = None,
    ):
        self.provider = provider
        self.attempt = attempt
        self.result = result
        self.error = error
        self.error_type = error_type

    def to_dict(self) -> dict[str, Any]:
        """Serialize attempt for error reporting."""
        d: dict[str, Any] = {"provider": self.provider, "attempt": self.attempt}
        if self.result is not None:
            d["result"] = self.result
        if self.error is not None:
            d["error"] = self.error
            d["error_type"] = self.error_type or "unknown"
        return d


async def try_provider(
    provider: str,
    query_fn: Any,
    health_checker: ProviderHealthChecker,
    max_retries: int,
    attempts: list[dict],
) -> str | None:
    """Try to generate with a provider, handling retries.

    Args:
        provider: Provider name.
        query_fn: Async callable that performs the actual query.
        health_checker: Health checker for availability and error tracking.
        max_retries: Maximum retry attempts per provider.
        attempts: Mutable list to append attempt records.

    Returns:
        Result string on success, None on failure.
    """
    health = health_checker.get_health(provider)
    if health and not health.is_available:
        return None

    for attempt in range(max_retries + 1):
        try:
            result = await query_fn(provider)
            health_checker.report_success(provider)
            attempts.append(
                ProviderAttempt(provider, attempt + 1, result=result).to_dict()
            )
            return result

        except Exception as e:  # noqa: BLE001 — intentional broad catch for provider failover
            error = health_checker.report_error(provider, e)
            attempts.append(
                ProviderAttempt(
                    provider,
                    attempt + 1,
                    error=str(e),
                    error_type=error.last_error.value if error.last_error else "unknown",
                ).to_dict()
            )

            if not await _should_retry(
                provider, error, attempt, max_retries, health_checker
            ):
                break

    return None


async def _should_retry(
    provider: str,
    error: Any,
    attempt: int,
    max_retries: int,
    health_checker: ProviderHealthChecker,
) -> bool:
    """Determine if we should retry the provider."""
    if not health_checker.should_retry(provider):
        return False

    if error.last_error == ProviderErrorType.QUOTA_EXHAUSTED:
        return False

    if error.last_error == ProviderErrorType.AUTHENTICATION:
        return False

    if error.last_error == ProviderErrorType.RATE_LIMIT:
        delay = health_checker.get_retry_delay(provider)
        await asyncio.sleep(delay)
        return True

    if attempt < max_retries:
        await asyncio.sleep(1.0 * (attempt + 1))
        return True

    return False
