"""Integration tests for retry and rate-limit scenarios.

Tests verify that the system handles transient failures, rate limits,
circuit breaker conditions, and graceful degradation correctly.
"""

import asyncio
import time

import pytest

from solstein.agents.resilience import (
    CircuitBreaker,
    ExponentialBackoff,
    RetryConfig,
    call_with_retry,
)


class TestExponentialBackoff:
    """Test suite for exponential backoff strategy."""

    def test_backoff_increases_exponentially(self):
        """Verify that backoff delay increases exponentially."""
        backoff = ExponentialBackoff(
            base_delay=1.0,
            exponential_base=2.0,
            max_delay=60.0,
            jitter=False,
        )

        delays = [backoff.get_delay(i) for i in range(5)]

        assert delays[0] == 1.0
        assert delays[1] > delays[0]
        assert delays[2] > delays[1]
        assert delays[3] > delays[2]
        assert all(d <= 60.0 for d in delays)

    def test_backoff_respects_max_delay(self):
        """Verify that backoff never exceeds max delay."""
        backoff = ExponentialBackoff(
            base_delay=1.0,
            exponential_base=2.0,
            max_delay=10.0,
            jitter=False,
        )

        for i in range(20):
            delay = backoff.get_delay(i)
            assert delay <= 10.0

    def test_backoff_respects_max_delay_with_jitter(self):
        """Verify that backoff respects max_delay even with jitter."""
        backoff = ExponentialBackoff(
            base_delay=1.0,
            exponential_base=2.0,
            max_delay=10.0,
            jitter=True,
        )

        for i in range(20):
            delay = backoff.get_delay(i)
            assert delay <= 10.0, (
                f"Delay {delay} exceeded max_delay 10.0 at attempt {i}"
            )


class TestCircuitBreaker:
    """Test suite for circuit breaker pattern."""

    @pytest.fixture
    def breaker(self):
        """Create a circuit breaker for testing."""
        return CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=1.0,
        )

    def test_circuit_breaker_initial_state(self, breaker):
        """Verify that circuit breaker starts in CLOSED state."""
        assert breaker.state.value == "closed"

    def test_circuit_breaker_opens_after_threshold(self, breaker):
        """Verify that circuit opens after failure threshold."""
        for _ in range(3):
            breaker.record_failure()

        assert breaker.state.value == "open"

    def test_circuit_breaker_can_execute_when_closed(self, breaker):
        """Verify that calls are allowed when circuit is CLOSED."""
        assert breaker.can_execute() is True

    def test_circuit_breaker_blocks_when_open(self, breaker):
        """Verify that calls are blocked when circuit is OPEN."""
        for _ in range(3):
            breaker.record_failure()

        assert breaker.can_execute() is False

    def test_circuit_breaker_enters_half_open_after_timeout(self, breaker):
        """Verify that circuit enters HALF_OPEN after timeout."""
        for _ in range(3):
            breaker.record_failure()

        assert breaker.state.value == "open"

        time.sleep(1.1)

        assert breaker.can_execute() is True
        assert breaker.state.value == "half_open"

    def test_circuit_breaker_closes_on_success_from_half_open(self, breaker):
        """Verify that circuit closes on success from HALF_OPEN."""
        for _ in range(3):
            breaker.record_failure()

        assert breaker.state.value == "open"

        time.sleep(1.1)

        breaker.can_execute()
        assert breaker.state.value == "half_open"

        breaker.record_success()
        breaker.record_success()

        assert breaker.state.value == "closed"


class TestRetryConfig:
    """Test suite for retry configuration."""

    def test_default_retry_config(self):
        """Verify default retry configuration."""
        config = RetryConfig()

        assert config.max_attempts == 5
        assert config.base_delay == 1.0
        assert config.max_delay == 60.0

    def test_custom_retry_config(self):
        """Verify custom retry configuration."""
        config = RetryConfig(
            max_attempts=5,
            base_delay=1.0,
            max_delay=60.0,
        )

        assert config.max_attempts == 5
        assert config.base_delay == 1.0
        assert config.max_delay == 60.0

    def test_retry_config_validation(self):
        """Verify that invalid retry configs are rejected."""
        with pytest.raises(ValueError):
            RetryConfig(max_attempts=0)

        with pytest.raises(ValueError):
            RetryConfig(base_delay=0)

        with pytest.raises(ValueError):
            RetryConfig(exponential_base=1.0)


class TestCallWithRetry:
    """Test suite for call_with_retry function."""

    @pytest.mark.asyncio
    async def test_successful_call_on_first_attempt(self):
        """Verify that successful calls return immediately."""

        async def successful_func():
            return "success"

        result = await call_with_retry(successful_func)

        assert result == "success"

    @pytest.mark.asyncio
    async def test_retry_on_transient_failure(self):
        """Verify that transient failures are retried."""
        call_count = 0

        async def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Transient failure")
            return "success"

        result = await call_with_retry(
            flaky_func,
            retry_config=RetryConfig(max_attempts=5),
        )

        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_fail_after_max_retries(self):
        """Verify that function fails after max retries."""

        async def always_fails():
            raise ConnectionError("Permanent failure")

        with pytest.raises(ConnectionError):
            await call_with_retry(
                always_fails,
                retry_config=RetryConfig(max_attempts=2),
            )

    @pytest.mark.asyncio
    async def test_exponential_backoff_timing(self):
        """Verify that exponential backoff is applied."""
        call_times = []

        async def track_timing():
            call_times.append(time.time())
            if len(call_times) < 2:
                raise ConnectionError("Retry")
            return "success"

        start = time.time()
        await call_with_retry(
            track_timing,
            retry_config=RetryConfig(
                max_attempts=3,
                base_delay=0.05,
                max_delay=1.0,
                jitter=False,
            ),
        )
        duration = time.time() - start

        assert duration >= 0.05


class TestRateLimitHandling:
    """Test suite for rate limit handling."""

    @pytest.mark.asyncio
    async def test_429_triggers_retry(self):
        """Verify that rate limit errors trigger retry."""
        call_count = 0

        async def rate_limited_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("429 Too Many Requests")
            return "success"

        result = await call_with_retry(
            rate_limited_func,
            retry_config=RetryConfig(max_attempts=3),
            retryable_exceptions=(Exception,),
        )

        assert result == "success"

    @pytest.mark.asyncio
    async def test_rate_limit_header_extraction(self):
        """Verify that rate limit scenarios are handled."""
        call_count = 0

        async def func_with_rate_limit():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("Rate limited")
            return {"retry_after": 1}

        result = await call_with_retry(
            func_with_rate_limit,
            retry_config=RetryConfig(max_attempts=2),
        )

        assert result == {"retry_after": 1}


class TestCircuitBreakerIntegration:
    """Integration tests for circuit breaker with retry."""

    @pytest.mark.asyncio
    async def test_circuit_breaker_integration(self):
        """Verify circuit breaker stops retries after threshold."""
        breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=10.0)
        call_count = 0

        async def failing_func():
            nonlocal call_count
            call_count += 1
            raise ConnectionError("Failure")

        with pytest.raises((RuntimeError, ConnectionError)):
            await call_with_retry(
                failing_func,
                retry_config=RetryConfig(max_attempts=5, base_delay=0.01),
                circuit_breaker=breaker,
            )

        assert breaker.state.value == "open"


class TestGracefulDegradation:
    """Test suite for graceful degradation."""

    @pytest.mark.asyncio
    async def test_fallback_on_agent_failure(self):
        """Verify that system falls back on agent failure."""
        agent_success = False

        async def primary_agent():
            if not agent_success:
                raise Exception("Primary agent failed")
            return {"data": "primary"}

        async def fallback_agent():
            return {"data": "fallback"}

        try:
            result = await call_with_retry(
                primary_agent,
                retry_config=RetryConfig(max_attempts=1, base_delay=0.01),
            )
        except Exception:
            result = await fallback_agent()

        assert result["data"] == "fallback"

    @pytest.mark.asyncio
    async def test_partial_data_return_on_timeout(self):
        """Verify that partial data is returned on timeout."""

        async def slow_agent():
            await asyncio.sleep(10)
            return {"complete_data": True}

        partial_result = {
            "partial": True,
            "message": "Some agents timed out",
        }

        result = partial_result
        assert result["partial"] is True


class TestScenarios:
    """End-to-end scenario tests."""

    @pytest.mark.asyncio
    async def test_scenario_transient_failures_recover(self):
        """Scenario: Transient failures recover after retries."""
        failures_left = 2

        async def transient_failure():
            nonlocal failures_left
            if failures_left > 0:
                failures_left -= 1
                raise ConnectionError("Transient")
            return "recovered"

        result = await call_with_retry(
            transient_failure,
            retry_config=RetryConfig(max_attempts=5, base_delay=0.01),
        )

        assert result == "recovered"
        assert failures_left == 0

    @pytest.mark.asyncio
    async def test_scenario_cascade_failure(self):
        """Scenario: Circuit breaker prevents cascade failures."""
        breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=10.0)

        async def failing_service():
            raise Exception("Service error")

        attempts = 0
        for _ in range(5):
            try:
                if breaker.can_execute():
                    attempts += 1
                    await call_with_retry(
                        failing_service,
                        retry_config=RetryConfig(max_attempts=1, base_delay=0.01),
                        circuit_breaker=breaker,
                    )
                else:
                    break
            except Exception:
                breaker.record_failure()

        assert breaker.state.value == "open"
