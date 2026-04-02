"""Tests for STORY-075: Multi-Provider Fallback and Circuit Breaking.

Acceptance criteria:
- Primary provider failure causes automatic fallback to secondary
- Circuit breaker trips skip providers without attempting calls
- Template fallback returned when all providers fail
- Fallback chain order is configurable via settings
- Each fallback decision is logged with failure reason
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from solstein.agents.resilience import CircuitBreakerState
from solstein.llm.fallback import (
    TEMPLATE_FALLBACK_RESPONSE,
    FallbackChain,
    FallbackDecision,
    FallbackResult,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mock_settings(provider_order=None, cb_enabled=True):
    """Create a mock Settings with configurable provider order."""
    settings = MagicMock()
    settings.llm_provider_order = provider_order or ["deepinfra", "mistral", "nvidia"]
    settings.llm_circuit_breaker_enabled = cb_enabled
    settings.circuit_breaker = MagicMock()
    settings.circuit_breaker.failure_threshold = 3
    settings.circuit_breaker.recovery_timeout = 60.0
    return settings


# ---------------------------------------------------------------------------
# FallbackChain basic tests
# ---------------------------------------------------------------------------


class TestFallbackChainBasic:
    """Test basic fallback chain behavior."""

    def test_provider_order_from_settings(self):
        settings = _mock_settings(provider_order=["anthropic", "openai", "deepinfra"])
        chain = FallbackChain(settings=settings)
        assert chain.get_provider_order() == ["anthropic", "openai", "deepinfra"]

    def test_preferred_provider_goes_first(self):
        settings = _mock_settings(provider_order=["deepinfra", "mistral", "nvidia"])
        chain = FallbackChain(settings=settings)
        order = chain.get_provider_order(preferred="nvidia")
        assert order[0] == "nvidia"
        assert "deepinfra" in order
        assert "mistral" in order

    def test_circuit_breakers_created(self):
        settings = _mock_settings(provider_order=["a", "b", "c"])
        chain = FallbackChain(settings=settings)
        assert chain.get_circuit_breaker("a") is not None
        assert chain.get_circuit_breaker("b") is not None
        assert chain.get_circuit_breaker("c") is not None

    def test_circuit_breakers_disabled(self):
        settings = _mock_settings(cb_enabled=False)
        chain = FallbackChain(settings=settings)
        assert chain.get_circuit_breaker("deepinfra") is None


# ---------------------------------------------------------------------------
# Fallback execution tests
# ---------------------------------------------------------------------------


class TestFallbackExecution:
    """Test fallback chain execution behavior."""

    @pytest.mark.asyncio
    async def test_first_provider_succeeds(self):
        settings = _mock_settings()
        chain = FallbackChain(settings=settings)

        async def query_fn(provider):
            return f"result from {provider}"

        result = await chain.execute(query_fn)
        assert result.result == "result from deepinfra"
        assert result.provider_used == "deepinfra"
        assert not result.is_template_fallback

    @pytest.mark.asyncio
    async def test_fallback_to_second_provider(self):
        """AC: Primary provider failure causes fallback to secondary."""
        settings = _mock_settings()
        chain = FallbackChain(settings=settings)

        call_count = {"deepinfra": 0, "mistral": 0}

        async def query_fn(provider):
            call_count[provider] = call_count.get(provider, 0) + 1
            if provider == "deepinfra":
                raise ConnectionError("Provider down")
            return f"result from {provider}"

        result = await chain.execute(query_fn, max_retries=0)
        assert result.result == "result from mistral"
        assert result.provider_used == "mistral"

    @pytest.mark.asyncio
    async def test_template_fallback_when_all_fail(self):
        """AC: Template fallback when all providers fail."""
        settings = _mock_settings(provider_order=["a", "b"])
        chain = FallbackChain(settings=settings)

        async def query_fn(provider):
            raise ConnectionError(f"{provider} down")

        result = await chain.execute(query_fn, max_retries=0)
        assert result.is_template_fallback
        assert result.result is None
        assert result.template_response is not None
        assert result.template_response["generated_by"] == "template_fallback"

    @pytest.mark.asyncio
    async def test_retries_before_fallback(self):
        settings = _mock_settings(provider_order=["primary", "secondary"])
        chain = FallbackChain(settings=settings)

        attempts = []

        async def query_fn(provider):
            attempts.append(provider)
            if provider == "primary":
                raise ConnectionError("Down")
            return "ok"

        result = await chain.execute(query_fn, max_retries=2)
        # primary should be tried 3 times (initial + 2 retries)
        assert attempts.count("primary") == 3
        assert result.provider_used == "secondary"


# ---------------------------------------------------------------------------
# Circuit breaker integration tests
# ---------------------------------------------------------------------------


class TestCircuitBreakerIntegration:
    """Test circuit breaker wired to fallback chain."""

    @pytest.mark.asyncio
    async def test_open_circuit_skips_provider(self):
        """AC: Provider exceeding circuit breaker threshold is skipped."""
        settings = _mock_settings(provider_order=["broken", "healthy"])
        chain = FallbackChain(settings=settings)

        # Manually open the circuit for "broken"
        cb = chain.get_circuit_breaker("broken")
        for _ in range(5):
            cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN

        async def query_fn(provider):
            if provider == "broken":
                raise AssertionError("Should not be called!")
            return f"result from {provider}"

        result = await chain.execute(query_fn)
        assert result.provider_used == "healthy"

        # Verify the skip was recorded
        skip_decisions = [d for d in result.decisions if d.action == "skipped_circuit_open"]
        assert len(skip_decisions) == 1
        assert skip_decisions[0].provider == "broken"

    @pytest.mark.asyncio
    async def test_failures_trip_circuit_breaker(self):
        settings = _mock_settings(provider_order=["flaky"])
        settings.circuit_breaker.failure_threshold = 2
        chain = FallbackChain(settings=settings)

        call_count = 0

        async def query_fn(provider):
            nonlocal call_count
            call_count += 1
            raise ConnectionError("Always fails")

        # First execution exhausts retries
        await chain.execute(query_fn, max_retries=0)

        cb = chain.get_circuit_breaker("flaky")
        assert cb.failure_count >= 1

    @pytest.mark.asyncio
    async def test_circuit_breaker_disabled(self):
        settings = _mock_settings(cb_enabled=False, provider_order=["only"])
        chain = FallbackChain(settings=settings)

        async def query_fn(provider):
            return "ok"

        result = await chain.execute(query_fn)
        assert result.result == "ok"


# ---------------------------------------------------------------------------
# Template fallback tests
# ---------------------------------------------------------------------------


class TestTemplateFallback:
    """Test template fallback structure."""

    def test_template_has_required_fields(self):
        assert "generated_by" in TEMPLATE_FALLBACK_RESPONSE
        assert TEMPLATE_FALLBACK_RESPONSE["generated_by"] == "template_fallback"
        assert "content" in TEMPLATE_FALLBACK_RESPONSE
        assert "metadata" in TEMPLATE_FALLBACK_RESPONSE
        assert TEMPLATE_FALLBACK_RESPONSE["metadata"]["fallback"] is True

    def test_template_content_is_string(self):
        assert isinstance(TEMPLATE_FALLBACK_RESPONSE["content"], str)
        assert len(TEMPLATE_FALLBACK_RESPONSE["content"]) > 0


# ---------------------------------------------------------------------------
# Fallback decision logging tests
# ---------------------------------------------------------------------------


class TestFallbackDecisionLogging:
    """AC: Each fallback decision is logged with the failure reason."""

    @pytest.mark.asyncio
    async def test_decisions_include_failure_reasons(self):
        settings = _mock_settings(provider_order=["a", "b"])
        chain = FallbackChain(settings=settings)

        async def query_fn(provider):
            if provider == "a":
                raise TimeoutError("Request timeout after 30s")
            return "ok"

        result = await chain.execute(query_fn, max_retries=0)
        failed_decisions = [d for d in result.decisions if d.action == "failed"]
        assert len(failed_decisions) >= 1
        assert "timeout" in failed_decisions[0].reason.lower()

    @pytest.mark.asyncio
    async def test_success_decisions_recorded(self):
        settings = _mock_settings(provider_order=["a"])
        chain = FallbackChain(settings=settings)

        async def query_fn(provider):
            return "ok"

        result = await chain.execute(query_fn)
        success_decisions = [d for d in result.decisions if d.action == "attempted" and d.reason == "success"]
        assert len(success_decisions) == 1

    @pytest.mark.asyncio
    async def test_all_decisions_have_provider(self):
        settings = _mock_settings(provider_order=["a", "b"])
        chain = FallbackChain(settings=settings)

        async def query_fn(provider):
            raise ConnectionError("Down")

        result = await chain.execute(query_fn, max_retries=0)
        for d in result.decisions:
            assert d.provider is not None
            assert d.action is not None


# ---------------------------------------------------------------------------
# Configurable provider order tests
# ---------------------------------------------------------------------------


class TestConfigurableProviderOrder:
    """AC: Fallback chain order is configurable via settings."""

    def test_custom_order_respected(self):
        settings = _mock_settings(provider_order=["nvidia", "anthropic", "deepinfra"])
        chain = FallbackChain(settings=settings)
        assert chain.get_provider_order() == ["nvidia", "anthropic", "deepinfra"]

    def test_single_provider(self):
        settings = _mock_settings(provider_order=["anthropic"])
        chain = FallbackChain(settings=settings)
        assert chain.get_provider_order() == ["anthropic"]

    @pytest.mark.asyncio
    async def test_order_determines_attempt_sequence(self):
        settings = _mock_settings(provider_order=["third", "first", "second"])
        chain = FallbackChain(settings=settings)

        attempted = []

        async def query_fn(provider):
            attempted.append(provider)
            if provider != "second":
                raise ConnectionError("Down")
            return "ok"

        result = await chain.execute(query_fn, max_retries=0)
        assert attempted == ["third", "first", "second"]
        assert result.provider_used == "second"


# ---------------------------------------------------------------------------
# EnhancedLLMClient integration
# ---------------------------------------------------------------------------


class TestEnhancedClientWithFallback:
    """Test EnhancedLLMClient uses FallbackChain."""

    @pytest.mark.asyncio
    async def test_generate_uses_fallback_chain(self):
        from solstein.llm.enhanced_client import EnhancedLLMClient

        mock_health = MagicMock()
        mock_health.check_all_providers = AsyncMock(return_value={})
        mock_health.get_health = MagicMock(return_value=None)
        mock_health.report_success = MagicMock()

        mock_fallback = MagicMock()
        mock_fallback.execute = AsyncMock(
            return_value=FallbackResult(
                result="test result",
                provider_used="deepinfra",
                is_template_fallback=False,
                decisions=[],
            )
        )

        client = EnhancedLLMClient(
            health_checker=mock_health,
            fallback_chain=mock_fallback,
        )
        result = await client.generate("Test prompt")
        assert result == "test result"
        mock_fallback.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_returns_template_on_total_failure(self):
        from solstein.llm.enhanced_client import EnhancedLLMClient

        mock_health = MagicMock()
        mock_health.check_all_providers = AsyncMock(return_value={})

        mock_fallback = MagicMock()
        mock_fallback.execute = AsyncMock(
            return_value=FallbackResult(
                result=None,
                provider_used=None,
                is_template_fallback=True,
                decisions=[],
                template_response=TEMPLATE_FALLBACK_RESPONSE.copy(),
            )
        )

        client = EnhancedLLMClient(
            health_checker=mock_health,
            fallback_chain=mock_fallback,
        )
        result = await client.generate("Test prompt", use_template_fallback=True)
        assert "template_fallback" in TEMPLATE_FALLBACK_RESPONSE["generated_by"]
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_generate_raises_when_template_disabled(self):
        from solstein.llm.enhanced_client import EnhancedLLMClient, LLMGenerationError

        mock_health = MagicMock()
        mock_health.check_all_providers = AsyncMock(return_value={})

        mock_fallback = MagicMock()
        mock_fallback.execute = AsyncMock(
            return_value=FallbackResult(
                result=None,
                provider_used=None,
                is_template_fallback=True,
                decisions=[FallbackDecision(provider="x", action="failed", reason="down")],
            )
        )

        client = EnhancedLLMClient(
            health_checker=mock_health,
            fallback_chain=mock_fallback,
        )
        with pytest.raises(LLMGenerationError):
            await client.generate("Test", use_template_fallback=False)
