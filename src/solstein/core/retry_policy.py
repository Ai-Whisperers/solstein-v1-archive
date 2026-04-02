"""Canonical retry policy module for all Solstein adapters and services.

STORY-116: All retry logic MUST use this module. Independent retry
implementations in adapters are forbidden.

This module provides:
- RetryProfile enum with standard profiles (NETWORK_DEFAULT, RATE_LIMIT, STRICT)
- RetryConfig dataclass for retry configuration
- call_with_retry / call_with_retry_sync wrappers with metrics
- retry_policy decorator for async functions
- Re-exports from infrastructure.retry_policy for backward compatibility

Usage:
    from solstein.core.retry_policy import retry_policy, RetryProfile

    @retry_policy(profile=RetryProfile.RATE_LIMIT)
    async def fetch_data():
        ...
"""

import asyncio
import functools
import logging
import random
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, ParamSpec, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")
P = ParamSpec("P")


# Re-export infrastructure types for backward compatibility
from solstein.infrastructure.retry_policy import (  # noqa: E402
    CircuitBreaker,
    CircuitBreakerState,
    FailureClassification,
    RetryDecision,
    RetryPolicy,
)

# ---------------------------------------------------------------------------
# Retry profiles
# ---------------------------------------------------------------------------


class RetryProfile(Enum):
    """Pre-defined retry profiles for common use cases."""

    NETWORK_DEFAULT = "network_default"
    RATE_LIMIT = "rate_limit"
    STRICT = "strict"


@dataclass(frozen=True)
class RetryConfig:
    """Immutable retry configuration with standard defaults."""

    max_retries: int = 3
    backoff_base: float = 1.0
    backoff_max: float = 30.0
    jitter: bool = True
    retryable_exceptions: tuple[type[Exception], ...] = (
        OSError,
        TimeoutError,
        ConnectionError,
    )
    non_retryable_exceptions: tuple[type[Exception], ...] = ()
    timeout_per_attempt: float = 30.0


# Standard profiles referenced by all adapters
PROFILES: dict[RetryProfile, RetryConfig] = {
    RetryProfile.NETWORK_DEFAULT: RetryConfig(
        max_retries=3,
        backoff_base=1.0,
        backoff_max=30.0,
        jitter=True,
        retryable_exceptions=(OSError, TimeoutError, ConnectionError),
        timeout_per_attempt=30.0,
    ),
    RetryProfile.RATE_LIMIT: RetryConfig(
        max_retries=5,
        backoff_base=5.0,
        backoff_max=60.0,
        jitter=True,
        retryable_exceptions=(OSError, TimeoutError, ConnectionError),
        timeout_per_attempt=60.0,
    ),
    RetryProfile.STRICT: RetryConfig(
        max_retries=1,
        backoff_base=0.0,
        backoff_max=0.0,
        jitter=False,
        retryable_exceptions=(OSError, TimeoutError),
        timeout_per_attempt=30.0,
    ),
}


def get_config(
    profile: RetryProfile | None = None,
    **overrides: Any,
) -> RetryConfig:
    """Get a RetryConfig by profile, with optional field overrides."""
    if profile is None:
        profile = RetryProfile.NETWORK_DEFAULT
    base = PROFILES[profile]
    if not overrides:
        return base
    fields = {f.name: getattr(base, f.name) for f in base.__dataclass_fields__.values()}
    fields.update(overrides)
    return RetryConfig(**fields)


# ---------------------------------------------------------------------------
# Backoff calculation
# ---------------------------------------------------------------------------


def _calculate_delay(attempt: int, config: RetryConfig) -> float:
    """Calculate backoff delay for a given attempt (0-indexed)."""
    if config.backoff_base <= 0:
        return 0.0
    delay = config.backoff_base * (2.0**attempt)
    delay = min(delay, config.backoff_max)
    if config.jitter:
        jitter_amount = delay * 0.2
        delay += random.uniform(-jitter_amount, jitter_amount)
        delay = max(0.0, delay)
        delay = min(delay, config.backoff_max)
    return delay


# ---------------------------------------------------------------------------
# Retry metrics
# ---------------------------------------------------------------------------


@dataclass
class RetryMetrics:
    """Metrics emitted per retry sequence."""

    name: str
    profile: str
    attempts: int = 0
    final_outcome: str = "unknown"
    total_duration_s: float = 0.0
    errors: list[str] = field(default_factory=list)

    def log(self) -> None:
        """Emit structured log entry for the retry sequence."""
        logger.info(
            "[RetryMetrics] %s: %s after %d attempts (%.2fs)",
            self.name,
            self.final_outcome,
            self.attempts,
            self.total_duration_s,
            extra={
                "retry_name": self.name,
                "retry_profile": self.profile,
                "retry_attempts": self.attempts,
                "retry_outcome": self.final_outcome,
                "retry_duration_s": self.total_duration_s,
            },
        )


# ---------------------------------------------------------------------------
# Async retry wrapper
# ---------------------------------------------------------------------------


async def call_with_retry(
    func: Callable[[], Awaitable[T]],
    *,
    profile: RetryProfile = RetryProfile.NETWORK_DEFAULT,
    config: RetryConfig | None = None,
    name: str = "call",
) -> T:
    """Execute an async callable with retry, backoff, and metrics.

    Args:
        func: Zero-argument async callable.
        profile: Retry profile (ignored if config provided).
        config: Explicit RetryConfig (overrides profile).
        name: Name for logging and metrics.

    Returns:
        Result of func().

    Raises:
        The last exception after all retries are exhausted.
    """
    cfg = config or PROFILES[profile]
    profile_name = profile.value if config is None else "custom"
    metrics = RetryMetrics(name=name, profile=profile_name)
    start = time.monotonic()
    last_exception: Exception | None = None

    for attempt in range(cfg.max_retries + 1):
        metrics.attempts = attempt + 1
        try:
            result = await asyncio.wait_for(
                func(),
                timeout=cfg.timeout_per_attempt,
            )
            metrics.final_outcome = "success"
            metrics.total_duration_s = time.monotonic() - start
            metrics.log()
            return result

        except cfg.non_retryable_exceptions as exc:
            _record_non_retryable(metrics, exc, start)
            raise

        except (*cfg.retryable_exceptions, TimeoutError) as exc:
            last_exception = exc
            metrics.errors.append(f"{type(exc).__name__}: {exc}")
            _log_attempt_failure(name, attempt, cfg.max_retries, exc)
            if attempt < cfg.max_retries:
                delay = _calculate_delay(attempt, cfg)
                if delay > 0:
                    await asyncio.sleep(delay)

    return _raise_exhausted(metrics, last_exception, start, name)


# ---------------------------------------------------------------------------
# Sync retry wrapper
# ---------------------------------------------------------------------------


def call_with_retry_sync(
    func: Callable[[], T],
    *,
    profile: RetryProfile = RetryProfile.NETWORK_DEFAULT,
    config: RetryConfig | None = None,
    name: str = "call",
) -> T:
    """Execute a sync callable with retry, backoff, and metrics."""
    cfg = config or PROFILES[profile]
    profile_name = profile.value if config is None else "custom"
    metrics = RetryMetrics(name=name, profile=profile_name)
    start = time.monotonic()
    last_exception: Exception | None = None

    for attempt in range(cfg.max_retries + 1):
        metrics.attempts = attempt + 1
        try:
            result = func()
            metrics.final_outcome = "success"
            metrics.total_duration_s = time.monotonic() - start
            metrics.log()
            return result

        except cfg.non_retryable_exceptions as exc:
            _record_non_retryable(metrics, exc, start)
            raise

        except (*cfg.retryable_exceptions, TimeoutError) as exc:
            last_exception = exc
            metrics.errors.append(f"{type(exc).__name__}: {exc}")
            _log_attempt_failure(name, attempt, cfg.max_retries, exc)
            if attempt < cfg.max_retries:
                delay = _calculate_delay(attempt, cfg)
                if delay > 0:
                    time.sleep(delay)

    return _raise_exhausted(metrics, last_exception, start, name)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _record_non_retryable(
    metrics: RetryMetrics,
    exc: Exception,
    start: float,
) -> None:
    metrics.final_outcome = "non_retryable_error"
    metrics.errors.append(f"{type(exc).__name__}: {exc}")
    metrics.total_duration_s = time.monotonic() - start
    metrics.log()


def _log_attempt_failure(
    name: str,
    attempt: int,
    max_retries: int,
    exc: Exception,
) -> None:
    logger.warning(
        "[%s] Attempt %d/%d failed: %s: %s",
        name,
        attempt + 1,
        max_retries + 1,
        type(exc).__name__,
        exc,
    )


def _raise_exhausted(
    metrics: RetryMetrics,
    last_exception: Exception | None,
    start: float,
    name: str,
) -> Any:
    metrics.final_outcome = "exhausted"
    metrics.total_duration_s = time.monotonic() - start
    metrics.log()
    if last_exception is not None:
        raise last_exception
    raise RuntimeError(f"[{name}] Retry exhausted with no exception captured")


# ---------------------------------------------------------------------------
# Decorator
# ---------------------------------------------------------------------------


def retry_policy(
    profile: RetryProfile = RetryProfile.NETWORK_DEFAULT,
    name: str | None = None,
    **overrides: Any,
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    """Decorator that adds retry behavior to an async function.

    Usage:
        @retry_policy(profile=RetryProfile.RATE_LIMIT)
        async def fetch_from_api():
            ...
    """
    cfg = get_config(profile, **overrides)

    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        call_name = name or func.__qualname__

        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            return await call_with_retry(
                lambda: func(*args, **kwargs),
                config=cfg,
                name=call_name,
            )

        return wrapper

    return decorator


__all__ = [
    "CircuitBreaker",
    "CircuitBreakerState",
    "FailureClassification",
    "PROFILES",
    "RetryConfig",
    "RetryDecision",
    "RetryMetrics",
    "RetryPolicy",
    "RetryProfile",
    "call_with_retry",
    "call_with_retry_sync",
    "get_config",
    "retry_policy",
]
