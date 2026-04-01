"""
Resilience utilities for agent API calls: retry logic, circuit breaker, exponential backoff.

This module provides production-grade resilience patterns for handling transient failures,
rate limiting, and cascading failures across external API calls.

Key Components:
- ExponentialBackoff: Calculate delay between retries with jitter
- CircuitBreaker: Prevent cascading failures by stopping calls when service is unhealthy
- call_with_retry: Unified async function call wrapper with all resilience patterns
"""

import asyncio
import logging
import random
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, TypeVar

from solstein.config import get_settings

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitBreakerState(Enum):
    """Circuit breaker states: CLOSED (normal), OPEN (failing), HALF_OPEN (testing)."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""

    max_attempts: int = 5
    base_delay: float = 1.0
    exponential_base: float = 2.0
    max_delay: float = 60.0
    jitter: bool = True
    timeout: float = 30.0
    retryable_exceptions: tuple = (Exception,)
    non_retryable_exceptions: tuple = ()

    def __post_init__(self):
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        if self.base_delay <= 0:
            raise ValueError("base_delay must be > 0")
        if self.exponential_base <= 1:
            raise ValueError("exponential_base must be > 1")
        if self.max_delay < self.base_delay:
            raise ValueError("max_delay must be >= base_delay")
        if self.timeout <= 0:
            raise ValueError("timeout must be > 0")


class ExponentialBackoff:
    """Calculate exponential backoff with optional jitter."""

    def __init__(
        self,
        base_delay: float = 1.0,
        exponential_base: float = 2.0,
        max_delay: float = 60.0,
        jitter: bool = True,
    ):
        """
        Initialize exponential backoff calculator.

        Args:
            base_delay: Initial delay in seconds.
            exponential_base: Multiplier for each retry (e.g., 2.0 = double each time).
            max_delay: Maximum delay cap in seconds.
            jitter: Add random jitter (±20%) to avoid thundering herd.
        """
        if base_delay <= 0:
            raise ValueError("base_delay must be > 0")
        if exponential_base <= 1:
            raise ValueError("exponential_base must be > 1")
        if max_delay < base_delay:
            raise ValueError("max_delay must be >= base_delay")

        self.base_delay = base_delay
        self.exponential_base = exponential_base
        self.max_delay = max_delay
        self.jitter = jitter

    def get_delay(self, attempt: int) -> float:
        """
        Calculate delay for given attempt number (0-indexed).

        Args:
            attempt: Attempt number (0 = first retry, 1 = second, etc.).

        Returns:
            Delay in seconds, capped at max_delay.
        """
        if attempt < 0:
            raise ValueError("attempt must be >= 0")

        delay = self.base_delay * (self.exponential_base**attempt)
        delay = min(delay, self.max_delay)

        if self.jitter:
            jitter_amount = delay * 0.2  # ±20%
            delay += random.uniform(-jitter_amount, jitter_amount)
            delay = max(0, delay)  # Ensure non-negative
            delay = min(delay, self.max_delay)  # Cap again after jitter

        return delay


class CircuitBreaker:
    """Prevent cascading failures using circuit breaker pattern (fail-fast)."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        name: str = "circuit_breaker",
    ):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit.
            recovery_timeout: Seconds to wait in HALF_OPEN state before retrying.
            name: Name for logging/debugging.
        """
        if failure_threshold < 1:
            raise ValueError("failure_threshold must be >= 1")
        if recovery_timeout <= 0:
            raise ValueError("recovery_timeout must be > 0")

        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.name = name

        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time: datetime | None = None
        self.success_count = 0

    def can_execute(self) -> bool:
        """Check if circuit allows execution."""
        if self.state == CircuitBreakerState.CLOSED:
            return True

        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_recovery():
                self.state = CircuitBreakerState.HALF_OPEN
                self.success_count = 0
                logger.info(f"[{self.name}] Circuit breaker entering HALF_OPEN state")
                return True
            return False

        # HALF_OPEN: allow execution
        return True

    def record_success(self) -> None:
        """Record successful call."""
        if self.state == CircuitBreakerState.CLOSED:
            return

        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= 2:  # 2 successes = circuit recovered
                self.state = CircuitBreakerState.CLOSED
                self.failure_count = 0
                logger.info(f"[{self.name}] Circuit breaker CLOSED (recovered)")

    def record_failure(self) -> None:
        """Record failed call, may open circuit."""
        self.failure_count += 1
        self.last_failure_time = datetime.now(timezone.utc)

        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.OPEN
            logger.warning(f"[{self.name}] Circuit breaker OPEN (failed during recovery)")
            return

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            logger.error(f"[{self.name}] Circuit breaker OPEN (threshold {self.failure_threshold} reached)")

    def _should_attempt_recovery(self) -> bool:
        """Check if enough time has passed to retry in HALF_OPEN state."""
        if not self.last_failure_time:
            return False
        elapsed = (datetime.now(timezone.utc) - self.last_failure_time).total_seconds()
        return elapsed >= self.recovery_timeout

    def get_state(self) -> str:
        """Get current state for logging."""
        return self.state.value


async def call_with_retry(
    func: Callable[[], Any],
    *,
    retry_config: RetryConfig | None = None,
    circuit_breaker: CircuitBreaker | None = None,
    name: str = "call",
) -> Any:
    """
    Execute a zero-argument async callable with retry logic, circuit breaker, and timeout.

    Args:
        func: Zero-argument async callable. Use ``functools.partial`` or a lambda to
              bind positional/keyword arguments before passing.
        retry_config: Retry configuration (default: RetryConfig()). Also carries
                      ``retryable_exceptions`` and ``non_retryable_exceptions``.
        circuit_breaker: Optional CircuitBreaker instance.
        name: Name for logging.

    Returns:
        Result of func() call.

    Raises:
        Exception: Original exception after max_attempts exhausted, or circuit open.
    """
    if retry_config is None:
        retry_config = RetryConfig()

    retryable_exceptions = retry_config.retryable_exceptions
    non_retryable_exceptions = retry_config.non_retryable_exceptions

    # Check circuit breaker first
    if circuit_breaker and not circuit_breaker.can_execute():
        raise RuntimeError(f"[{name}] Circuit breaker OPEN (service unavailable, try again later)")

    last_exception: Exception | None = None

    for attempt in range(retry_config.max_attempts):
        try:
            logger.debug(f"[{name}] Attempt {attempt + 1}/{retry_config.max_attempts}")

            # Execute with timeout
            result = await asyncio.wait_for(func(), timeout=retry_config.timeout)

            # Success: record and return
            if circuit_breaker:
                circuit_breaker.record_success()
            logger.debug(f"[{name}] Success on attempt {attempt + 1}")
            return result

        except non_retryable_exceptions as e:  # noqa: BLE001
            # Non-retryable: fail immediately
            if circuit_breaker:
                circuit_breaker.record_failure()
            logger.error(f"[{name}] Non-retryable exception: {type(e).__name__}: {e}")
            raise

        except TimeoutError as e:
            # Timeout: retryable
            last_exception = e
            logger.warning(f"[{name}] Timeout on attempt {attempt + 1}")
            if attempt < retry_config.max_attempts - 1:
                backoff = ExponentialBackoff(
                    base_delay=retry_config.base_delay,
                    exponential_base=retry_config.exponential_base,
                    max_delay=retry_config.max_delay,
                    jitter=retry_config.jitter,
                )
                delay = backoff.get_delay(attempt)
                logger.info(f"[{name}] Waiting {delay:.2f}s before retry")
                await asyncio.sleep(delay)

        except retryable_exceptions as e:  # noqa: BLE001
            # Retryable: log and retry if attempts remain
            last_exception = e
            logger.warning(f"[{name}] Retryable exception on attempt {attempt + 1}: {type(e).__name__}: {e}")

            if attempt < retry_config.max_attempts - 1:
                backoff = ExponentialBackoff(
                    base_delay=retry_config.base_delay,
                    exponential_base=retry_config.exponential_base,
                    max_delay=retry_config.max_delay,
                    jitter=retry_config.jitter,
                )
                delay = backoff.get_delay(attempt)
                logger.info(f"[{name}] Waiting {delay:.2f}s before retry")
                await asyncio.sleep(delay)
            else:
                # Last attempt failed: record and raise
                if circuit_breaker:
                    circuit_breaker.record_failure()

    # Exhausted retries: raise last exception
    if circuit_breaker:
        circuit_breaker.record_failure()

    if last_exception:
        logger.error(
            f"[{name}] Failed after {retry_config.max_attempts} attempts: "
            f"{type(last_exception).__name__}: {last_exception}"
        )
        raise last_exception

    raise RuntimeError(f"[{name}] Unknown failure after {retry_config.max_attempts} attempts")


def _build_retry_configs() -> tuple["RetryConfig", "RetryConfig", "RetryConfig"]:
    """Build preset retry configurations using settings-driven timeouts.

    Falls back to sensible defaults if settings cannot be loaded (e.g. during
    test collection without DATABASE__URL).
    """
    try:
        _settings = get_settings()
    except Exception:
        # Provide safe defaults so import succeeds without full config
        class _Defaults:
            class http_timeouts:
                github = 30.0
                companies_house = 30.0
                web_search_agent = 20.0
        _settings = _Defaults()
    github = RetryConfig(
        max_attempts=4,
        base_delay=2.0,
        exponential_base=2.0,
        max_delay=30.0,
        timeout=float(_settings.http_timeouts.github),
    )
    companies_house = RetryConfig(
        max_attempts=3,
        base_delay=3.0,
        exponential_base=2.0,
        max_delay=30.0,
        timeout=float(_settings.http_timeouts.companies_house),
    )
    web_search = RetryConfig(
        max_attempts=3,
        base_delay=1.0,
        exponential_base=2.0,
        max_delay=20.0,
        timeout=float(_settings.http_timeouts.web_search_agent),
    )
    return github, companies_house, web_search


# Preset configurations for common services — lazily built from config on first access
# to avoid import-time side effects (STORY-254 compliance).
_RETRY_CONFIGS: tuple["RetryConfig", "RetryConfig", "RetryConfig"] | None = None


def _get_retry_configs() -> tuple["RetryConfig", "RetryConfig", "RetryConfig"]:
    global _RETRY_CONFIGS
    if _RETRY_CONFIGS is None:
        _RETRY_CONFIGS = _build_retry_configs()
    return _RETRY_CONFIGS


def __getattr__(name: str):
    """Module-level lazy attribute access for retry configs."""
    _map = {
        "GITHUB_RETRY_CONFIG": 0,
        "COMPANIES_HOUSE_RETRY_CONFIG": 1,
        "WEB_SEARCH_RETRY_CONFIG": 2,
    }
    if name in _map:
        return _get_retry_configs()[_map[name]]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
