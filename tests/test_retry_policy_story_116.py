"""Tests for STORY-116: Centralize All Retry/Backoff in core/retry_policy.py.

Tests the canonical retry policy module with all three profiles,
backoff calculation, metrics, and decorator forms.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from solstein.core.retry_policy import (
    PROFILES,
    RetryConfig,
    RetryMetrics,
    RetryProfile,
    _calculate_delay,
    call_with_retry,
    call_with_retry_sync,
    get_config,
    retry_policy,
)


class TestRetryProfiles:
    """Verify that all three required profiles exist and have correct defaults."""

    def test_network_default_exists(self) -> None:
        cfg = PROFILES[RetryProfile.NETWORK_DEFAULT]
        assert cfg.max_retries == 3
        assert cfg.backoff_base == 1.0
        assert cfg.backoff_max == 30.0
        assert cfg.jitter is True

    def test_rate_limit_exists(self) -> None:
        cfg = PROFILES[RetryProfile.RATE_LIMIT]
        assert cfg.max_retries == 5
        assert cfg.backoff_base == 5.0
        assert cfg.backoff_max == 60.0
        assert cfg.jitter is True

    def test_strict_exists(self) -> None:
        cfg = PROFILES[RetryProfile.STRICT]
        assert cfg.max_retries == 1
        assert cfg.backoff_base == 0.0
        assert cfg.jitter is False


class TestRetryConfig:
    """Verify RetryConfig dataclass behavior."""

    def test_frozen(self) -> None:
        cfg = RetryConfig()
        with pytest.raises(AttributeError):
            cfg.max_retries = 10  # type: ignore[misc]

    def test_get_config_default(self) -> None:
        cfg = get_config()
        assert cfg == PROFILES[RetryProfile.NETWORK_DEFAULT]

    def test_get_config_with_overrides(self) -> None:
        cfg = get_config(RetryProfile.NETWORK_DEFAULT, max_retries=7)
        assert cfg.max_retries == 7
        assert cfg.backoff_base == 1.0  # unchanged


class TestBackoffCalculation:
    """Verify exponential backoff with jitter."""

    def test_zero_base_returns_zero(self) -> None:
        cfg = RetryConfig(backoff_base=0.0, backoff_max=0.0, jitter=False)
        assert _calculate_delay(0, cfg) == 0.0

    def test_exponential_growth(self) -> None:
        cfg = RetryConfig(backoff_base=1.0, backoff_max=100.0, jitter=False)
        assert _calculate_delay(0, cfg) == 1.0
        assert _calculate_delay(1, cfg) == 2.0
        assert _calculate_delay(2, cfg) == 4.0

    def test_capped_at_max(self) -> None:
        cfg = RetryConfig(backoff_base=1.0, backoff_max=5.0, jitter=False)
        assert _calculate_delay(10, cfg) == 5.0

    def test_jitter_stays_in_range(self) -> None:
        cfg = RetryConfig(backoff_base=10.0, backoff_max=100.0, jitter=True)
        for _ in range(100):
            delay = _calculate_delay(0, cfg)
            assert 0.0 <= delay <= 100.0


class TestRetryMetrics:
    """Verify metrics logging."""

    def test_metrics_log_produces_structured_output(self) -> None:
        metrics = RetryMetrics(
            name="test_call",
            profile="network_default",
            attempts=3,
            final_outcome="success",
            total_duration_s=1.5,
        )
        # Should not raise
        metrics.log()


class TestCallWithRetry:
    """Verify async retry wrapper."""

    @pytest.mark.asyncio
    async def test_success_on_first_attempt(self) -> None:
        func = AsyncMock(return_value="ok")
        result = await call_with_retry(func, name="test")
        assert result == "ok"
        assert func.call_count == 1

    @pytest.mark.asyncio
    async def test_retry_on_transient_failure(self) -> None:
        func = AsyncMock(side_effect=[OSError("fail"), "ok"])
        cfg = RetryConfig(
            max_retries=2, backoff_base=0.01, backoff_max=0.01,
            jitter=False, timeout_per_attempt=5.0,
        )
        result = await call_with_retry(func, config=cfg, name="test")
        assert result == "ok"
        assert func.call_count == 2

    @pytest.mark.asyncio
    async def test_exhausted_retries_raises(self) -> None:
        func = AsyncMock(side_effect=OSError("always fails"))
        cfg = RetryConfig(
            max_retries=2, backoff_base=0.01, backoff_max=0.01,
            jitter=False, timeout_per_attempt=5.0,
        )
        with pytest.raises(OSError, match="always fails"):
            await call_with_retry(func, config=cfg, name="test")
        assert func.call_count == 3  # initial + 2 retries

    @pytest.mark.asyncio
    async def test_non_retryable_fails_immediately(self) -> None:
        func = AsyncMock(side_effect=ValueError("bad input"))
        cfg = RetryConfig(
            max_retries=3,
            non_retryable_exceptions=(ValueError,),
            retryable_exceptions=(OSError,),
            backoff_base=0.01, backoff_max=0.01,
            jitter=False, timeout_per_attempt=5.0,
        )
        with pytest.raises(ValueError, match="bad input"):
            await call_with_retry(func, config=cfg, name="test")
        assert func.call_count == 1


class TestCallWithRetrySync:
    """Verify sync retry wrapper."""

    def test_success_on_first_attempt(self) -> None:
        func = MagicMock(return_value="ok")
        result = call_with_retry_sync(func, name="test")
        assert result == "ok"
        assert func.call_count == 1

    def test_retry_on_failure(self) -> None:
        func = MagicMock(side_effect=[OSError("fail"), "ok"])
        cfg = RetryConfig(
            max_retries=2, backoff_base=0.01, backoff_max=0.01,
            jitter=False, timeout_per_attempt=5.0,
        )
        result = call_with_retry_sync(func, config=cfg, name="test")
        assert result == "ok"
        assert func.call_count == 2

    def test_exhausted_raises(self) -> None:
        func = MagicMock(side_effect=ConnectionError("down"))
        cfg = RetryConfig(
            max_retries=1, backoff_base=0.01, backoff_max=0.01,
            jitter=False, timeout_per_attempt=5.0,
        )
        with pytest.raises(ConnectionError, match="down"):
            call_with_retry_sync(func, config=cfg, name="test")
        assert func.call_count == 2


class TestRetryPolicyDecorator:
    """Verify the @retry_policy decorator."""

    @pytest.mark.asyncio
    async def test_decorator_retries(self) -> None:
        call_count = 0

        @retry_policy(
            profile=RetryProfile.NETWORK_DEFAULT,
            max_retries=2,
            backoff_base=0.01,
            backoff_max=0.01,
            jitter=False,
            timeout_per_attempt=5.0,
        )
        async def flaky_func() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise OSError("transient")
            return "success"

        result = await flaky_func()
        assert result == "success"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_decorator_passes_args(self) -> None:
        @retry_policy(
            profile=RetryProfile.STRICT,
            timeout_per_attempt=5.0,
        )
        async def add(a: int, b: int) -> int:
            return a + b

        assert await add(3, 4) == 7
