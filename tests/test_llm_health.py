"""Tests for the enhanced LLM client with health checking.

Run with: pytest tests/test_llm_health.py -v
"""

import asyncio
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from src.solstein.llm.health_checker import (
    ProviderError,
    ProviderErrorType,
    ProviderHealth,
    ProviderHealthChecker,
    ProviderStatus,
    get_health_checker,
    reset_health_checker,
)
from src.solstein.llm.enhanced_client import (
    EnhancedLLMClient,
    LLMGenerationError,
)


class TestProviderHealth:
    """Test ProviderHealth dataclass."""

    def test_is_available_when_healthy(self):
        """Test that healthy providers are available."""
        health = ProviderHealth(
            provider="openai",
            status=ProviderStatus.HEALTHY,
        )
        assert health.is_available is True

    def test_is_available_when_rate_limited_and_expired(self):
        """Test that rate limited providers become available after retry_after."""
        past_time = datetime.now(timezone.utc) - timedelta(seconds=60)
        health = ProviderHealth(
            provider="openai",
            status=ProviderStatus.RATE_LIMITED,
            retry_after=past_time,
        )
        assert health.is_available is True

    def test_is_not_available_when_rate_limited_and_active(self):
        """Test that rate limited providers are not available before retry_after."""
        future_time = datetime.now(timezone.utc) + timedelta(seconds=60)
        health = ProviderHealth(
            provider="openai",
            status=ProviderStatus.RATE_LIMITED,
            retry_after=future_time,
        )
        assert health.is_available is False

    def test_should_retry_for_rate_limit(self):
        """Test that rate limited providers should be retried."""
        health = ProviderHealth(
            provider="openai",
            status=ProviderStatus.RATE_LIMITED,
        )
        assert health.should_retry is True

    def test_should_not_retry_after_many_failures(self):
        """Test that providers with many failures should not be retried."""
        health = ProviderHealth(
            provider="openai",
            status=ProviderStatus.UNHEALTHY,
            consecutive_failures=5,
        )
        assert health.should_retry is False


class TestProviderHealthChecker:
    """Test ProviderHealthChecker functionality."""

    def setup_method(self):
        """Reset health checker before each test."""
        reset_health_checker()

    def test_classify_rate_limit_error(self):
        """Test error classification for rate limit."""
        checker = ProviderHealthChecker()
        error = Exception("Rate limit exceeded (429)")

        result = checker._classify_error(error, "openai")

        assert result.error_type == ProviderErrorType.RATE_LIMIT
        assert result.status_code == 429
        assert result.provider == "openai"

    def test_classify_auth_error(self):
        """Test error classification for authentication failure."""
        checker = ProviderHealthChecker()
        error = Exception("Invalid API key provided (401)")

        result = checker._classify_error(error, "openai")

        assert result.error_type == ProviderErrorType.AUTHENTICATION
        assert result.status_code == 401

    def test_classify_quota_error(self):
        """Test error classification for quota exhaustion."""
        checker = ProviderHealthChecker()
        error = Exception("You exceeded your current quota")

        result = checker._classify_error(error, "openai")

        assert result.error_type == ProviderErrorType.QUOTA_EXHAUSTED

    def test_update_health_on_rate_limit(self):
        """Test health update after rate limit error."""
        checker = ProviderHealthChecker()
        error = ProviderError(
            error_type=ProviderErrorType.RATE_LIMIT,
            message="Rate limited",
            retry_after_seconds=120,
            provider="openai",
        )

        health = checker._update_health_on_error("openai", error)

        assert health.status == ProviderStatus.RATE_LIMITED
        assert health.retry_after is not None
        assert health.consecutive_failures == 1

    def test_update_health_on_quota_exhausted(self):
        """Test health update after quota exhausted error."""
        checker = ProviderHealthChecker()
        error = ProviderError(
            error_type=ProviderErrorType.QUOTA_EXHAUSTED,
            message="Quota exceeded",
            provider="openai",
        )

        health = checker._update_health_on_error("openai", error)

        assert health.status == ProviderStatus.EXHAUSTED
        assert health.estimated_credits_remaining is False

    def test_update_health_on_success(self):
        """Test health update after successful call."""
        checker = ProviderHealthChecker()

        # First simulate some failures
        checker._health["openai"] = ProviderHealth(
            provider="openai",
            status=ProviderStatus.DEGRADED,
            consecutive_failures=3,
        )

        health = checker._update_health_on_success("openai")

        assert health.status == ProviderStatus.HEALTHY
        assert health.consecutive_failures == 0
        assert health.total_successes == 1

    def test_get_best_provider_priority_order(self):
        """Test that best provider respects priority order."""
        checker = ProviderHealthChecker()

        # Make all providers healthy
        for provider in ["ollama", "fireworks", "openai", "groq"]:
            checker._health[provider] = ProviderHealth(
                provider=provider,
                status=ProviderStatus.HEALTHY,
            )

        best = checker.get_best_provider()

        # Ollama has highest priority
        assert best == "ollama"

    def test_get_best_provider_skips_unavailable(self):
        """Test that unavailable providers are skipped."""
        checker = ProviderHealthChecker()

        checker._health["ollama"] = ProviderHealth(
            provider="ollama",
            status=ProviderStatus.UNHEALTHY,
        )
        checker._health["openai"] = ProviderHealth(
            provider="openai",
            status=ProviderStatus.HEALTHY,
        )

        best = checker.get_best_provider()

        # Should skip ollama and return openai
        assert best == "openai"

    @pytest.mark.asyncio
    async def test_check_ollama_success(self):
        """Test Ollama health check when server is running."""
        checker = ProviderHealthChecker()

        with patch("aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=False)

            mock_session_instance = AsyncMock()
            mock_session_instance.get = MagicMock(return_value=mock_response)
            mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
            mock_session_instance.__aexit__ = AsyncMock(return_value=False)

            mock_session.return_value = mock_session_instance

            health = await checker.check_ollama()

            assert health.provider == "ollama"
            assert health.status == ProviderStatus.HEALTHY

    @pytest.mark.asyncio
    async def test_check_ollama_failure(self):
        """Test Ollama health check when server is down."""
        checker = ProviderHealthChecker()

        with patch("aiohttp.ClientSession") as mock_session:
            mock_session_instance = AsyncMock()
            mock_session_instance.get = AsyncMock(side_effect=Exception("Connection refused"))
            mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
            mock_session_instance.__aexit__ = AsyncMock(return_value=False)

            mock_session.return_value = mock_session_instance

            health = await checker.check_ollama()

            assert health.provider == "ollama"
            assert health.status == ProviderStatus.UNHEALTHY

    def test_get_retry_delay_for_rate_limit(self):
        """Test retry delay calculation for rate limited providers."""
        checker = ProviderHealthChecker()
        future_time = datetime.now(timezone.utc) + timedelta(seconds=30)

        checker._health["openai"] = ProviderHealth(
            provider="openai",
            status=ProviderStatus.RATE_LIMITED,
            retry_after=future_time,
        )

        delay = checker.get_retry_delay("openai")

        assert 25 <= delay <= 35  # Allow some tolerance

    def test_get_retry_delay_exponential_backoff(self):
        """Test exponential backoff for failed providers."""
        checker = ProviderHealthChecker()

        checker._health["openai"] = ProviderHealth(
            provider="openai",
            status=ProviderStatus.DEGRADED,
            consecutive_failures=3,
        )

        delay = checker.get_retry_delay("openai")

        # 1.0 * 2^3 = 8.0
        assert delay == 8.0


class TestEnhancedLLMClient:
    """Test EnhancedLLMClient functionality."""

    def setup_method(self):
        """Reset health checker before each test."""
        reset_health_checker()

    @pytest.mark.asyncio
    async def test_generate_with_success(self):
        """Test successful generation."""
        mock_checker = MagicMock()
        mock_checker.PROVIDER_PRIORITY = ["openai"]
        mock_checker.get_health.return_value = ProviderHealth(
            provider="openai",
            status=ProviderStatus.HEALTHY,
        )
        mock_checker.should_retry.return_value = True
        mock_checker.get_retry_delay.return_value = 1.0
        mock_checker.report_success.return_value = ProviderHealth(
            provider="openai",
            status=ProviderStatus.HEALTHY,
        )

        client = EnhancedLLMClient(health_checker=mock_checker)

        # Mock the _query_cloud_provider method
        with patch.object(client, "_query_cloud_provider", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = "Generated text"

            result = await client.generate("Test prompt")

            assert result == "Generated text"
            mock_checker.report_success.assert_called_once_with("openai")

    @pytest.mark.asyncio
    async def test_generate_falls_back_on_failure(self):
        """Test that generation falls back to next provider on failure."""
        mock_checker = MagicMock()
        mock_checker.PROVIDER_PRIORITY = ["openai", "groq"]
        mock_checker.get_health.side_effect = [
            ProviderHealth(provider="openai", status=ProviderStatus.HEALTHY),
            ProviderHealth(provider="groq", status=ProviderStatus.HEALTHY),
        ]
        mock_checker.should_retry.return_value = False  # Don't retry openai
        mock_checker.report_error.return_value = ProviderHealth(
            provider="openai",
            status=ProviderStatus.RATE_LIMITED,
        )

        client = EnhancedLLMClient(health_checker=mock_checker)

        # Mock _query_cloud_provider to fail for openai but succeed for groq
        call_count = 0

        async def mock_query(provider, *args, **kwargs):
            nonlocal call_count
            call_count += 1
            if provider == "openai":
                raise Exception("Rate limit")
            return "Generated from groq"

        with patch.object(client, "_query_cloud_provider", side_effect=mock_query):
            result = await client.generate("Test prompt")

            assert result == "Generated from groq"
            assert call_count == 2  # Tried openai then groq

    @pytest.mark.asyncio
    async def test_generate_structured_output(self):
        """Test structured output generation."""
        from pydantic import BaseModel

        class TestSchema(BaseModel):
            answer: str

        mock_checker = MagicMock()
        mock_checker.PROVIDER_PRIORITY = ["openai"]
        mock_checker.get_health.return_value = ProviderHealth(
            provider="openai",
            status=ProviderStatus.HEALTHY,
        )
        mock_checker.should_retry.return_value = True
        mock_checker.report_success.return_value = ProviderHealth(
            provider="openai",
            status=ProviderStatus.HEALTHY,
        )

        client = EnhancedLLMClient(health_checker=mock_checker)

        with patch.object(client, "generate", new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = '{"answer": "test"}'

            result = await client.generate_structured("Test", TestSchema)

            assert result is not None
            assert result.answer == "test"


class TestIntegration:
    """Integration tests for the full LLM health system."""

    def setup_method(self):
        """Reset health checker before each test."""
        reset_health_checker()

    @pytest.mark.asyncio
    async def test_full_health_check_flow(self):
        """Test the complete health check flow."""
        checker = get_health_checker()

        # Mock settings to have no API keys (simulates exhausted credits)
        with patch.object(checker, "_get_settings") as mock_settings:
            settings = MagicMock()
            settings.llm_provider = "auto"
            settings.ollama_url = "http://localhost:11434"
            settings.openai_api_key = None
            settings.groq_api_key = None
            settings.fireworks_api_key = None
            mock_settings.return_value = settings

            health = await checker.check_all_providers()

            # Should have checked but found no providers
            assert len(health) == 0 or all(h.status != ProviderStatus.HEALTHY for h in health.values())

    def test_error_classification_comprehensive(self):
        """Test comprehensive error classification patterns."""
        checker = ProviderHealthChecker()

        test_cases = [
            ("Rate limit exceeded", ProviderErrorType.RATE_LIMIT),
            ("429 Too Many Requests", ProviderErrorType.RATE_LIMIT),
            ("throttled, try again later", ProviderErrorType.RATE_LIMIT),
            ("Invalid API key (401)", ProviderErrorType.AUTHENTICATION),
            ("Authentication failed", ProviderErrorType.AUTHENTICATION),
            ("You exceeded your quota", ProviderErrorType.QUOTA_EXHAUSTED),
            ("insufficient credits", ProviderErrorType.QUOTA_EXHAUSTED),
            ("Connection timeout", ProviderErrorType.TIMEOUT),
            ("Network unreachable", ProviderErrorType.NETWORK_ERROR),
            ("DNS lookup failed", ProviderErrorType.NETWORK_ERROR),
            ("Something went wrong", ProviderErrorType.UNKNOWN),
        ]

        for error_msg, expected_type in test_cases:
            error = Exception(error_msg)
            result = checker._classify_error(error, "test")
            assert result.error_type == expected_type, f"Failed for: {error_msg}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
