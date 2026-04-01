"""Circuit breaker pattern for external API resilience.

Implements the circuit breaker pattern to prevent cascading failures
when external APIs (LinkedIn, Crunchbase, etc.) are unavailable.
"""

import time
from collections.abc import Callable
from enum import Enum
from functools import wraps
from typing import Any, TypeVar

from loguru import logger

from solstein.config import get_settings

T = TypeVar("T")


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject calls
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """Circuit breaker for external API calls.

    Prevents cascading failures by rejecting calls when a service
    is experiencing high failure rates.

    Usage:
        cb = get_settings().circuit_breaker  # from solstein.config
        breaker = CircuitBreaker(
            failure_threshold=cb.failure_threshold,
            recovery_timeout=cb.recovery_timeout,
        )

        @breaker
        async def call_external_api():
            return await make_http_request()
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        half_open_max_calls: int = 3,
        expected_exception: type[Exception] = Exception,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        self.expected_exception = expected_exception

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: float | None = None
        self._half_open_calls = 0

    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        return self._state

    @property
    def failure_count(self) -> int:
        """Get current failure count."""
        return self._failure_count

    def _can_attempt(self) -> bool:
        """Check if a call can be attempted."""
        if self._state == CircuitState.CLOSED:
            return True

        if self._state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if self._last_failure_time is None:
                return True

            elapsed = time.time() - self._last_failure_time
            if elapsed >= self.recovery_timeout:
                logger.info(f"Circuit breaker transitioning to HALF_OPEN after {elapsed:.0f}s")
                self._state = CircuitState.HALF_OPEN
                self._half_open_calls = 0
                return True

            return False

        if self._state == CircuitState.HALF_OPEN:
            return self._half_open_calls < self.half_open_max_calls

        return False

    def _record_success(self) -> None:
        """Record a successful call."""
        if self._state == CircuitState.HALF_OPEN:
            self._success_count += 1

            # If we've seen enough successes, close the circuit
            if self._success_count >= self.half_open_max_calls:
                logger.info("Circuit breaker transitioning to CLOSED")
                self._state = CircuitState.CLOSED
                self._failure_count = 0
                self._success_count = 0
                self._half_open_calls = 0
        else:
            self._failure_count = max(0, self._failure_count - 1)

    def _record_failure(self) -> None:
        """Record a failed call."""
        self._failure_count += 1
        self._last_failure_time = time.time()

        if self._state == CircuitState.HALF_OPEN:
            logger.warning("Circuit breaker transitioning to OPEN (failure in HALF_OPEN)")
            self._state = CircuitState.OPEN
            self._half_open_calls = 0
        elif self._failure_count >= self.failure_threshold:
            if self._state == CircuitState.CLOSED:
                logger.warning(f"Circuit breaker transitioning to OPEN ({self._failure_count} failures)")
                self._state = CircuitState.OPEN

    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        """Decorator to apply circuit breaker to a function."""

        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> T:
            if not self._can_attempt():
                raise CircuitBreakerOpen(
                    f"Circuit breaker is OPEN for {func.__name__}. Last failure: {self._last_failure_time}"
                )

            if self._state == CircuitState.HALF_OPEN:
                self._half_open_calls += 1

            try:
                result = await func(*args, **kwargs)
                self._record_success()
                return result
            except self.expected_exception:
                self._record_failure()
                raise

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> T:
            if not self._can_attempt():
                raise CircuitBreakerOpen(
                    f"Circuit breaker is OPEN for {func.__name__}. Last failure: {self._last_failure_time}"
                )

            if self._state == CircuitState.HALF_OPEN:
                self._half_open_calls += 1

            try:
                result = func(*args, **kwargs)
                self._record_success()
                return result
            except self.expected_exception:
                self._record_failure()
                raise

        # Return appropriate wrapper based on function type
        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        return sync_wrapper  # type: ignore


class CircuitBreakerOpen(Exception):  # noqa: N818
    """Exception raised when circuit breaker is open."""

    pass


def _make_preconfigured_breakers() -> tuple["CircuitBreaker", "CircuitBreaker", "CircuitBreaker"]:
    """Build pre-configured circuit breakers using settings-driven defaults.

    LinkedIn and Crunchbase previously used 5 failures / 120s and 5 / 60s respectively.
    News used 10 / 30s. All now share the same failure_threshold from config; recovery
    timeouts remain source-specific multiples of the base recovery_timeout.
    """
    _settings = get_settings()
    cb = _settings.circuit_breaker

    _linkedin = CircuitBreaker(
        failure_threshold=cb.failure_threshold,
        recovery_timeout=cb.recovery_timeout * 2,  # LinkedIn is slower to recover — 2x default
        expected_exception=Exception,
    )
    _crunchbase = CircuitBreaker(
        failure_threshold=cb.failure_threshold,
        recovery_timeout=cb.recovery_timeout,
        expected_exception=Exception,
    )
    _news = CircuitBreaker(
        failure_threshold=cb.failure_threshold * 2,  # News is higher-volume; tolerate more failures
        recovery_timeout=cb.recovery_timeout / 2,  # But recover faster (30s at default)
        expected_exception=Exception,
    )
    return _linkedin, _crunchbase, _news


# Pre-configured circuit breakers for common enrichment sources.
# Values are driven by CircuitBreakerConfig in config.py rather than hardcoded literals.
linkedin_breaker, crunchbase_breaker, news_breaker = _make_preconfigured_breakers()
