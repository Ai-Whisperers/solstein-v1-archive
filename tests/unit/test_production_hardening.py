"""Tests for production hardening and graceful degradation.

Tests verify feature flags, response caching, graceful degradation,
timeout management, and graceful shutdown.
"""

import asyncio

import pytest

from solstein.core.production_hardening import (
    FeatureFlag,
    FeatureFlagManager,
    GracefulDegradation,
    GracefulShutdown,
    RequestTimeoutManager,
    ResponseCache,
)


class TestFeatureFlagManager:
    """Test suite for feature flag manager."""

    @pytest.fixture
    def manager(self):
        """Create a feature flag manager for testing."""
        return FeatureFlagManager()

    def test_feature_flags_initialized(self, manager):
        """Verify that feature flags are initialized."""
        assert manager.is_enabled(FeatureFlag.ENABLE_LINKEDIN_AGENT) is True
        assert manager.is_enabled(FeatureFlag.ENABLE_RESPONSE_CACHING) is True

    def test_enable_feature_flag(self, manager):
        """Verify that feature flags can be enabled."""
        manager.disable(FeatureFlag.ENABLE_LINKEDIN_AGENT)
        assert manager.is_enabled(FeatureFlag.ENABLE_LINKEDIN_AGENT) is False

        manager.enable(FeatureFlag.ENABLE_LINKEDIN_AGENT)
        assert manager.is_enabled(FeatureFlag.ENABLE_LINKEDIN_AGENT) is True

    def test_disable_feature_flag(self, manager):
        """Verify that feature flags can be disabled."""
        manager.disable(FeatureFlag.ENABLE_NEWS_AGENT)
        assert manager.is_enabled(FeatureFlag.ENABLE_NEWS_AGENT) is False

    def test_get_all_flags(self, manager):
        """Verify that all flags can be retrieved."""
        all_flags = manager.get_all()

        assert len(all_flags) >= 9
        assert all_flags["enable_linkedin_agent"] is True
        assert all_flags["enable_response_caching"] is True


class TestResponseCache:
    """Test suite for response cache."""

    @pytest.fixture
    def cache(self):
        """Create a response cache for testing."""
        return ResponseCache()

    def test_cache_set_and_get(self, cache):
        """Verify that values can be cached and retrieved."""
        cache.set("key1", {"data": "value1"})
        result = cache.get("key1")

        assert result == {"data": "value1"}

    def test_cache_returns_none_for_missing_key(self, cache):
        """Verify that missing keys return None."""
        result = cache.get("nonexistent")

        assert result is None

    def test_cache_respects_ttl(self, cache):
        """Verify that cached values expire after TTL."""
        cache.set("expiring", "value", ttl_seconds=0)

        import time

        time.sleep(0.1)

        result = cache.get("expiring")
        assert result is None

    def test_cache_size(self, cache):
        """Verify that cache size is tracked."""
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        assert cache.size() == 3

    def test_cache_clear(self, cache):
        """Verify that cache can be cleared."""
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        cache.clear()

        assert cache.size() == 0
        assert cache.get("key1") is None


class TestGracefulDegradation:
    """Test suite for graceful degradation."""

    @pytest.fixture
    def degradation(self):
        """Create a graceful degradation handler for testing."""
        return GracefulDegradation()

    @pytest.mark.asyncio
    async def test_successful_agent_call(self, degradation):
        """Verify that successful calls are handled."""

        async def successful_agent():
            return {"status": "success"}

        result = await degradation.wrap_agent_call("test_agent", successful_agent)

        assert result == {"status": "success"}
        assert degradation.is_agent_degraded("test_agent") is False

    @pytest.mark.asyncio
    async def test_failed_agent_call_with_fallback(self, degradation):
        """Verify that failed calls use fallback."""

        async def failing_agent():
            raise Exception("Agent failed")

        async def fallback_agent():
            return {"status": "fallback"}

        result = await degradation.wrap_agent_call(
            "test_agent",
            failing_agent,
            fallback_agent,
        )

        assert result == {"status": "fallback"}

    @pytest.mark.asyncio
    async def test_degradation_threshold(self, degradation):
        """Verify that agents degrade after threshold."""

        async def failing_agent():
            raise Exception("Always fails")

        for _ in range(5):
            await degradation.wrap_agent_call("degraded_agent", failing_agent)

        assert degradation.is_agent_degraded("degraded_agent") is True

    def test_degradation_status(self, degradation):
        """Verify that degradation status is reported."""
        status = degradation.get_status()

        assert isinstance(status, dict)


class TestRequestTimeoutManager:
    """Test suite for request timeout manager."""

    @pytest.fixture
    def manager(self):
        """Create a timeout manager for testing."""
        return RequestTimeoutManager()

    def test_get_default_timeout(self, manager):
        """Verify that default timeouts are set."""
        assert manager.get_timeout("agent_call") == 30.0
        assert manager.get_timeout("database_query") == 10.0

    def test_set_custom_timeout(self, manager):
        """Verify that custom timeouts can be set."""
        manager.set_timeout("agent_call", 60.0)

        assert manager.get_timeout("agent_call") == 60.0

    @pytest.mark.asyncio
    async def test_run_with_timeout_success(self, manager):
        """Verify that operations complete within timeout."""

        async def quick_operation():
            await asyncio.sleep(0.01)
            return "success"

        manager.set_timeout("test_op", 5.0)
        result = await manager.run_with_timeout("test_op", quick_operation())

        assert result == "success"

    @pytest.mark.asyncio
    async def test_run_with_timeout_exceeds(self, manager):
        """Verify that timeout raises error."""

        async def slow_operation():
            await asyncio.sleep(10)
            return "success"

        manager.set_timeout("test_op", 0.1)

        with pytest.raises(asyncio.TimeoutError):
            await manager.run_with_timeout("test_op", slow_operation())


class TestGracefulShutdown:
    """Test suite for graceful shutdown."""

    @pytest.fixture
    def shutdown(self):
        """Create a graceful shutdown handler for testing."""
        return GracefulShutdown()

    @pytest.mark.asyncio
    async def test_shutdown_handler_execution(self, shutdown):
        """Verify that shutdown handlers are executed."""
        call_order = []

        async def handler1():
            call_order.append("handler1")

        async def handler2():
            call_order.append("handler2")

        shutdown.register_shutdown_handler(handler1)
        shutdown.register_shutdown_handler(handler2)

        await shutdown.shutdown()

        assert call_order == ["handler1", "handler2"]

    @pytest.mark.asyncio
    async def test_shutdown_idempotent(self, shutdown):
        """Verify that shutdown can be called multiple times safely."""
        call_count = 0

        async def counter_handler():
            nonlocal call_count
            call_count += 1

        shutdown.register_shutdown_handler(counter_handler)

        await shutdown.shutdown()
        await shutdown.shutdown()

        assert call_count == 1

    @pytest.mark.asyncio
    async def test_shutdown_flag_set(self, shutdown):
        """Verify that shutdown flag is set."""

        async def dummy_handler():
            pass

        shutdown.register_shutdown_handler(dummy_handler)
        await shutdown.shutdown()

        assert shutdown.is_shutting_down is True
