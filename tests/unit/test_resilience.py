"""
Comprehensive tests for resilience layer: retry, backoff, circuit breaker.

Tests cover:
- Exponential backoff calculation and jitter
- Circuit breaker state transitions (CLOSED -> OPEN -> HALF_OPEN -> CLOSED)
- Retry logic with success/failure scenarios
- Timeout handling
- Non-retryable exceptions
- Circuit breaker preventing cascading failures
"""

import asyncio
from unittest.mock import AsyncMock

import pytest

from solstein.agents.resilience import (
    COMPANIES_HOUSE_RETRY_CONFIG,
    GITHUB_RETRY_CONFIG,
    WEB_SEARCH_RETRY_CONFIG,
    CircuitBreaker,
    CircuitBreakerState,
    ExponentialBackoff,
    RetryConfig,
    call_with_retry,
)

# ============================================================================
# Tests: ExponentialBackoff
# ============================================================================


class TestExponentialBackoff:
    """Test exponential backoff delay calculation."""

    def test_basic_exponential_sequence_no_jitter(self):
        """Test deterministic exponential sequence without jitter."""
        backoff = ExponentialBackoff(
            base_delay=1.0, exponential_base=2.0, max_delay=60.0, jitter=False
        )

        assert backoff.get_delay(0) == 1.0  # 1 * 2^0
        assert backoff.get_delay(1) == 2.0  # 1 * 2^1
        assert backoff.get_delay(2) == 4.0  # 1 * 2^2
        assert backoff.get_delay(3) == 8.0  # 1 * 2^3
        assert backoff.get_delay(4) == 16.0  # 1 * 2^4

    def test_max_delay_cap(self):
        """Test that delay is capped at max_delay."""
        backoff = ExponentialBackoff(
            base_delay=1.0, exponential_base=2.0, max_delay=10.0, jitter=False
        )

        assert backoff.get_delay(0) == 1.0
        assert backoff.get_delay(1) == 2.0
        assert backoff.get_delay(2) == 4.0
        assert backoff.get_delay(3) == 8.0
        assert backoff.get_delay(4) == 10.0  # Capped
        assert backoff.get_delay(5) == 10.0  # Still capped

    def test_jitter_within_bounds(self):
        """Test that jitter keeps delays within ±20% of base."""
        backoff = ExponentialBackoff(
            base_delay=1.0, exponential_base=2.0, max_delay=60.0, jitter=True
        )

        for attempt in range(5):
            delay = backoff.get_delay(attempt)
            base = 1.0 * (2.0**attempt)
            base = min(base, 60.0)

            # Allow ±20% jitter + small float tolerance
            lower_bound = base * 0.8 - 0.001
            upper_bound = base * 1.2 + 0.001

            assert lower_bound <= delay <= upper_bound, (
                f"Attempt {attempt}: delay {delay} not in [{lower_bound}, {upper_bound}]"
            )

    def test_custom_exponential_base(self):
        """Test different exponential base (e.g., 3.0)."""
        backoff = ExponentialBackoff(
            base_delay=1.0, exponential_base=3.0, max_delay=100.0, jitter=False
        )

        assert backoff.get_delay(0) == 1.0  # 1 * 3^0
        assert backoff.get_delay(1) == 3.0  # 1 * 3^1
        assert backoff.get_delay(2) == 9.0  # 1 * 3^2
        assert backoff.get_delay(3) == 27.0  # 1 * 3^3

    def test_invalid_config_raises_error(self):
        """Test that invalid configuration raises ValueError."""
        with pytest.raises(ValueError, match="base_delay must be > 0"):
            ExponentialBackoff(base_delay=0)

        with pytest.raises(ValueError, match="exponential_base must be > 1"):
            ExponentialBackoff(exponential_base=1.0)

        with pytest.raises(ValueError, match="max_delay must be >= base_delay"):
            ExponentialBackoff(base_delay=10.0, max_delay=5.0)

    def test_negative_attempt_raises_error(self):
        """Test that negative attempt number raises ValueError."""
        backoff = ExponentialBackoff()
        with pytest.raises(ValueError, match="attempt must be >= 0"):
            backoff.get_delay(-1)


# ============================================================================
# Tests: CircuitBreaker
# ============================================================================


class TestCircuitBreaker:
    """Test circuit breaker state machine."""

    def test_initial_state_closed(self):
        """Test that circuit breaker starts in CLOSED state."""
        cb = CircuitBreaker()
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.can_execute() is True

    def test_success_keeps_circuit_closed(self):
        """Test that success doesn't affect CLOSED state."""
        cb = CircuitBreaker()
        cb.record_success()
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.can_execute() is True

    def test_failures_open_circuit(self):
        """Test that failures reach threshold open circuit."""
        cb = CircuitBreaker(failure_threshold=3)
        assert cb.can_execute() is True

        cb.record_failure()
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.can_execute() is True

        cb.record_failure()
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.can_execute() is True

        cb.record_failure()  # Threshold reached
        assert cb.state == CircuitBreakerState.OPEN
        assert cb.can_execute() is False

    def test_open_circuit_rejects_execution(self):
        """Test that OPEN circuit rejects all execution until recovery timeout."""
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=1.0)

        cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN
        assert cb.can_execute() is False

        # Still open before timeout
        assert cb.can_execute() is False

    def test_half_open_recovery_on_success(self):
        """Test recovery path: OPEN -> HALF_OPEN -> CLOSED on success."""
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.1)

        # Open the circuit
        cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN

        # Wait for recovery window
        import time

        time.sleep(0.15)

        # Should enter HALF_OPEN
        assert cb.can_execute() is True
        assert cb.state == CircuitBreakerState.HALF_OPEN

        # First success
        cb.record_success()
        assert cb.state == CircuitBreakerState.HALF_OPEN

        # Second success = recovery complete
        cb.record_success()
        assert cb.state == CircuitBreakerState.CLOSED

    def test_half_open_failure_reopens_circuit(self):
        """Test that failure during HALF_OPEN reopens circuit."""
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.1)

        # Open and enter HALF_OPEN
        cb.record_failure()
        import time

        time.sleep(0.15)
        cb.can_execute()

        assert cb.state == CircuitBreakerState.HALF_OPEN

        # Failure reopens
        cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN

    def test_get_state_returns_string(self):
        """Test that get_state() returns human-readable state."""
        cb = CircuitBreaker(failure_threshold=1)
        assert cb.get_state() == "closed"

        cb.record_failure()
        assert cb.get_state() == "open"

    def test_invalid_config_raises_error(self):
        """Test that invalid configuration raises ValueError."""
        with pytest.raises(ValueError, match="failure_threshold must be >= 1"):
            CircuitBreaker(failure_threshold=0)

        with pytest.raises(ValueError, match="recovery_timeout must be > 0"):
            CircuitBreaker(recovery_timeout=-1)


# ============================================================================
# Tests: call_with_retry
# ============================================================================


class TestCallWithRetry:
    """Test retry logic integration."""

    @pytest.mark.asyncio
    async def test_success_on_first_attempt(self):
        """Test that success on first attempt returns immediately."""
        mock_func = AsyncMock(return_value="success")
        result = await call_with_retry(mock_func)

        assert result == "success"
        assert mock_func.call_count == 1

    @pytest.mark.asyncio
    async def test_retry_on_failure_then_success(self):
        """Test retry after transient failure."""
        mock_func = AsyncMock(
            side_effect=[Exception("fail"), Exception("fail"), "success"]
        )

        result = await call_with_retry(
            mock_func, retry_config=RetryConfig(max_attempts=3, base_delay=0.01)
        )

        assert result == "success"
        assert mock_func.call_count == 3

    @pytest.mark.asyncio
    async def test_fail_after_max_attempts(self):
        """Test that retries exhaust and exception is raised."""
        mock_func = AsyncMock(side_effect=Exception("always fails"))

        with pytest.raises(Exception, match="always fails"):
            await call_with_retry(
                mock_func, retry_config=RetryConfig(max_attempts=3, base_delay=0.01)
            )

        assert mock_func.call_count == 3

    @pytest.mark.asyncio
    async def test_non_retryable_exception_fails_immediately(self):
        """Test that non-retryable exceptions fail immediately."""

        class NonRetryableError(Exception):
            pass

        mock_func = AsyncMock(side_effect=NonRetryableError("fail fast"))

        with pytest.raises(NonRetryableError, match="fail fast"):
            await call_with_retry(
                mock_func,
                retry_config=RetryConfig(max_attempts=5, base_delay=0.01),
                non_retryable_exceptions=(NonRetryableError,),
            )

        assert mock_func.call_count == 1  # No retries

    @pytest.mark.asyncio
    async def test_timeout_triggers_retry(self):
        """Test that timeout is treated as retryable failure."""
        attempt_count = 0

        async def slow_then_fast():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count == 1:
                await asyncio.sleep(1.0)  # Timeout
            return "success"

        result = await call_with_retry(
            slow_then_fast,
            retry_config=RetryConfig(max_attempts=3, base_delay=0.01, timeout=0.1),
        )

        assert result == "success"
        assert attempt_count == 2

    @pytest.mark.asyncio
    async def test_circuit_breaker_integration(self):
        """Test that circuit breaker prevents cascading failures."""
        mock_func = AsyncMock(side_effect=Exception("service down"))
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=10.0)

        # First two attempts fail and open circuit
        with pytest.raises(Exception):
            await call_with_retry(
                mock_func,
                retry_config=RetryConfig(max_attempts=2, base_delay=0.01),
                circuit_breaker=cb,
            )

        assert cb.state == CircuitBreakerState.OPEN

        # Third call rejected by circuit breaker immediately
        with pytest.raises(RuntimeError, match="Circuit breaker OPEN"):
            await call_with_retry(mock_func, circuit_breaker=cb)

        assert mock_func.call_count == 2  # No additional calls

    @pytest.mark.asyncio
    async def test_passes_args_and_kwargs(self):
        """Test that args and kwargs are passed to function."""
        mock_func = AsyncMock(return_value="success")

        result = await call_with_retry(
            mock_func, "arg1", "arg2", kwarg1="value1", kwarg2="value2"
        )

        assert result == "success"
        mock_func.assert_called_once_with(
            "arg1", "arg2", kwarg1="value1", kwarg2="value2"
        )

    @pytest.mark.asyncio
    async def test_retry_config_validation(self):
        """Test that invalid RetryConfig raises error."""
        with pytest.raises(ValueError, match="max_attempts must be >= 1"):
            RetryConfig(max_attempts=0)

        with pytest.raises(ValueError, match="base_delay must be > 0"):
            RetryConfig(base_delay=-1)


# ============================================================================
# Tests: Preset Configurations
# ============================================================================


class TestPresetConfigs:
    """Test that preset configs are sensible."""

    def test_github_config_reasonable(self):
        """Test GitHub retry config."""
        assert GITHUB_RETRY_CONFIG.max_attempts == 4
        assert GITHUB_RETRY_CONFIG.timeout == 15.0
        assert GITHUB_RETRY_CONFIG.base_delay == 2.0

    def test_companies_house_config_reasonable(self):
        """Test Companies House retry config (slower service)."""
        assert COMPANIES_HOUSE_RETRY_CONFIG.max_attempts == 3
        assert COMPANIES_HOUSE_RETRY_CONFIG.timeout == 20.0
        assert COMPANIES_HOUSE_RETRY_CONFIG.base_delay == 3.0

    def test_web_search_config_reasonable(self):
        """Test web search retry config."""
        assert WEB_SEARCH_RETRY_CONFIG.max_attempts == 3
        assert WEB_SEARCH_RETRY_CONFIG.timeout == 15.0


# ============================================================================
# Tests: Integration Scenarios
# ============================================================================


class TestIntegrationScenarios:
    """Test realistic failure scenarios."""

    @pytest.mark.asyncio
    async def test_github_api_rate_limit_recovery(self):
        """Simulate GitHub rate limit hit, then recovery."""

        class RateLimitError(Exception):
            pass

        attempt = 0

        async def github_call():
            nonlocal attempt
            attempt += 1
            if attempt < 2:
                raise RateLimitError("403: API rate limit exceeded")
            return {"repos": 42}

        result = await call_with_retry(
            github_call,
            retry_config=GITHUB_RETRY_CONFIG,
            retryable_exceptions=(RateLimitError,),
        )

        assert result == {"repos": 42}
        assert attempt == 2

    @pytest.mark.asyncio
    async def test_cascading_failure_with_circuit_breaker(self):
        """Demonstrate circuit breaker preventing cascading failures."""
        call_count = 0

        async def failing_service():
            nonlocal call_count
            call_count += 1
            raise Exception("service down")

        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=10.0)

        # Exhaust retries and trigger circuit breaker open
        with pytest.raises(Exception, match="service down"):
            await call_with_retry(
                failing_service,
                retry_config=RetryConfig(
                    max_attempts=2, base_delay=0.001, jitter=False
                ),
                circuit_breaker=cb,
            )

        calls_after_first_attempt = call_count
        assert calls_after_first_attempt == 2
        assert cb.state == CircuitBreakerState.OPEN

        # Once circuit is OPEN, new calls fail immediately without retrying
        with pytest.raises(RuntimeError, match="Circuit breaker OPEN"):
            await call_with_retry(failing_service, circuit_breaker=cb)

        # No new service calls after circuit opened
        assert call_count == calls_after_first_attempt

    @pytest.mark.asyncio
    async def test_exponential_backoff_timing(self):
        """Test that exponential backoff actually delays between attempts."""
        import time

        attempt_times = []

        async def track_time():
            attempt_times.append(time.time())
            if len(attempt_times) < 3:
                raise Exception("retry")
            return "success"

        start = time.time()
        result = await call_with_retry(
            track_time,
            retry_config=RetryConfig(
                max_attempts=3, base_delay=0.1, exponential_base=2.0, jitter=False
            ),
        )

        assert result == "success"
        assert len(attempt_times) == 3

        # First retry should have ~0.1s delay
        delay_1 = attempt_times[1] - attempt_times[0]
        assert 0.08 < delay_1 < 0.15, f"Expected ~0.1s, got {delay_1}s"

        # Second retry should have ~0.2s delay
        delay_2 = attempt_times[2] - attempt_times[1]
        assert 0.18 < delay_2 < 0.25, f"Expected ~0.2s, got {delay_2}s"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
