from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from enum import Enum


class FailureClassification(str, Enum):
    RETRYABLE = "retryable"
    TERMINAL = "terminal"

    @property
    def is_retryable(self) -> bool:
        return self is FailureClassification.RETRYABLE


@dataclass(frozen=True)
class RetryDecision:
    attempt: int
    classification: FailureClassification
    should_retry: bool
    delay_seconds: float


@dataclass
class RetryPolicy:
    max_attempts: int = 5
    base_delay_seconds: float = 0.25
    max_delay_seconds: float = 30.0
    jitter_ratio: float = 0.2

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        if self.base_delay_seconds <= 0:
            raise ValueError("base_delay_seconds must be > 0")
        if self.max_delay_seconds < self.base_delay_seconds:
            raise ValueError("max_delay_seconds must be >= base_delay_seconds")
        if not 0 <= self.jitter_ratio <= 1:
            raise ValueError("jitter_ratio must be between 0 and 1")

    @staticmethod
    def classify_failure(*, retryable: bool) -> FailureClassification:
        return (
            FailureClassification.RETRYABLE
            if retryable
            else FailureClassification.TERMINAL
        )

    def next_delay_seconds(self, *, attempt: int, key: str) -> float:
        if attempt < 1:
            raise ValueError("attempt must be >= 1")
        if not key:
            raise ValueError("key must be a non-empty string")

        scale = float(1 << (attempt - 1))
        exponential = float(self.base_delay_seconds * scale)
        capped = float(min(exponential, self.max_delay_seconds))
        jitter = self._deterministic_jitter_multiplier(key=key, attempt=attempt)
        return capped * jitter

    def evaluate(
        self,
        *,
        attempt: int,
        key: str,
        classification: FailureClassification,
    ) -> RetryDecision:
        if attempt < 1:
            raise ValueError("attempt must be >= 1")

        should_retry = classification.is_retryable and attempt < self.max_attempts
        delay_seconds = (
            self.next_delay_seconds(attempt=attempt, key=key) if should_retry else 0.0
        )
        return RetryDecision(
            attempt=attempt,
            classification=classification,
            should_retry=should_retry,
            delay_seconds=delay_seconds,
        )

    def _deterministic_jitter_multiplier(self, *, key: str, attempt: int) -> float:
        digest = hashlib.sha256(f"{key}:{attempt}".encode()).digest()
        numerator = int.from_bytes(digest[:8], byteorder="big", signed=False)
        unit_interval = numerator / float((1 << 64) - 1)
        centered = (unit_interval * 2.0) - 1.0
        return 1.0 + (centered * self.jitter_ratio)


class CircuitBreakerState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"


@dataclass
class CircuitBreaker:
    failure_threshold: int = 5
    cooldown_seconds: float = 60.0
    _state: CircuitBreakerState = CircuitBreakerState.CLOSED
    _consecutive_failures: int = 0
    _opened_at: float | None = None

    def __post_init__(self) -> None:
        if self.failure_threshold < 1:
            raise ValueError("failure_threshold must be >= 1")
        if self.cooldown_seconds < 0:
            raise ValueError("cooldown_seconds must be >= 0")

    @property
    def state(self) -> CircuitBreakerState:
        self._refresh_state()
        return self._state

    @property
    def consecutive_failures(self) -> int:
        return self._consecutive_failures

    def allow_request(self) -> bool:
        return self.state is CircuitBreakerState.CLOSED

    def record_success(self) -> None:
        self.close()

    def record_failure(self) -> None:
        self._refresh_state()
        self._consecutive_failures += 1
        if self._consecutive_failures >= self.failure_threshold:
            self.open()

    def open(self) -> None:
        self._state = CircuitBreakerState.OPEN
        self._opened_at = time.monotonic()

    def close(self) -> None:
        self._state = CircuitBreakerState.CLOSED
        self._consecutive_failures = 0
        self._opened_at = None

    def _refresh_state(self) -> None:
        if self._state is not CircuitBreakerState.OPEN:
            return
        if self._opened_at is None:
            return
        elapsed = time.monotonic() - self._opened_at
        if elapsed >= self.cooldown_seconds:
            self.close()


__all__ = [
    "CircuitBreaker",
    "CircuitBreakerState",
    "FailureClassification",
    "RetryDecision",
    "RetryPolicy",
]
