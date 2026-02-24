import pytest

from solstein.infrastructure.retry_policy import (
    CircuitBreaker,
    CircuitBreakerState,
    RetryPolicy,
)


def test_next_delay_seconds_is_deterministic_for_same_key_and_attempt() -> None:
    policy = RetryPolicy(
        base_delay_seconds=0.25, max_delay_seconds=30.0, jitter_ratio=0.2
    )

    first = policy.next_delay_seconds(attempt=3, key="company:abc")
    second = policy.next_delay_seconds(attempt=3, key="company:abc")
    different_attempt = policy.next_delay_seconds(attempt=4, key="company:abc")

    assert first == pytest.approx(second)
    assert different_attempt != pytest.approx(first)


def test_next_delay_seconds_is_monotonic_until_cap_without_jitter() -> None:
    policy = RetryPolicy(
        base_delay_seconds=0.5, max_delay_seconds=2.0, jitter_ratio=0.0
    )

    delays = [
        policy.next_delay_seconds(attempt=attempt, key="market:xyz")
        for attempt in range(1, 7)
    ]

    assert delays == pytest.approx([0.5, 1.0, 2.0, 2.0, 2.0, 2.0])
    assert all(
        current <= following
        for current, following in zip(delays, delays[1:], strict=False)
    )


def test_circuit_breaker_opens_at_threshold_and_closes_after_cooldown(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_clock = {"now": 100.0}

    def fake_monotonic() -> float:
        return fake_clock["now"]

    monkeypatch.setattr(
        "solstein.infrastructure.retry_policy.time.monotonic", fake_monotonic
    )

    breaker = CircuitBreaker(failure_threshold=2, cooldown_seconds=5.0)

    assert breaker.state is CircuitBreakerState.CLOSED
    assert breaker.allow_request() is True

    breaker.record_failure()
    assert breaker.state is CircuitBreakerState.CLOSED

    breaker.record_failure()
    assert breaker.state is CircuitBreakerState.OPEN
    assert breaker.allow_request() is False

    fake_clock["now"] += 4.9
    assert breaker.allow_request() is False
    assert breaker.state is CircuitBreakerState.OPEN

    fake_clock["now"] += 0.1
    assert breaker.allow_request() is True
    assert breaker.state is CircuitBreakerState.CLOSED
    assert breaker.consecutive_failures == 0
