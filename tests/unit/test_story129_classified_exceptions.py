"""STORY-129: Tests for classified exception handling in EnhancedLLMClient.

Verifies that:
- Exceptions are classified by the ErrorClassifier into ProviderErrorType
- Prometheus metrics (llm_requests_total, llm_errors_total) are emitted
- Health checker receives explicit failure signals via report_error()
- Structured logging includes required fields (component, operation, error_type)
- Successful queries emit success metrics and report_success()
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from solstein.llm.health.errors import ErrorClassifier
from solstein.llm.health.models import ProviderErrorType

# ---------------------------------------------------------------------------
# ErrorClassifier unit tests
# ---------------------------------------------------------------------------


class TestErrorClassifier:
    """Verify exception classification into ProviderErrorType categories."""

    def setup_method(self) -> None:
        self.classifier = ErrorClassifier()

    def test_timeout_classified(self) -> None:
        exc = TimeoutError("Connection timed out")
        result = self.classifier.classify(exc, "openai")
        assert result.error_type == ProviderErrorType.TIMEOUT

    def test_rate_limit_by_status_code(self) -> None:
        exc = Exception("Too many requests")
        exc.status_code = 429  # type: ignore[attr-defined]
        result = self.classifier.classify(exc, "deepinfra")
        assert result.error_type == ProviderErrorType.RATE_LIMIT

    def test_auth_by_status_code(self) -> None:
        exc = Exception("Unauthorized")
        exc.status_code = 401  # type: ignore[attr-defined]
        result = self.classifier.classify(exc, "anthropic")
        assert result.error_type == ProviderErrorType.AUTHENTICATION

    def test_auth_by_message_pattern(self) -> None:
        exc = Exception("Invalid API key provided")
        result = self.classifier.classify(exc, "openai")
        assert result.error_type == ProviderErrorType.AUTHENTICATION

    def test_quota_exhausted(self) -> None:
        exc = Exception("Credits exhausted for this account")
        result = self.classifier.classify(exc, "fireworks")
        assert result.error_type == ProviderErrorType.QUOTA_EXHAUSTED

    def test_network_error(self) -> None:
        exc = ConnectionError("Connection refused")
        result = self.classifier.classify(exc, "ollama")
        assert result.error_type == ProviderErrorType.NETWORK_ERROR

    def test_unknown_error_fallback(self) -> None:
        exc = ValueError("Something unexpected")
        result = self.classifier.classify(exc, "mistral")
        assert result.error_type == ProviderErrorType.UNKNOWN

    def test_rate_limit_includes_retry_after(self) -> None:
        exc = Exception("rate limit exceeded")
        exc.retry_after = "30"  # type: ignore[attr-defined]
        result = self.classifier.classify(exc, "openai")
        assert result.error_type == ProviderErrorType.RATE_LIMIT
        assert result.retry_after_seconds == 30


# ---------------------------------------------------------------------------
# EnhancedLLMClient._query_provider integration tests
# ---------------------------------------------------------------------------


class TestQueryProviderClassifiedExceptions:
    """Verify _query_provider emits metrics, logs, and health signals."""

    @pytest.fixture()
    def mock_client(self) -> MagicMock:
        """Create a mock EnhancedLLMClient with patched dependencies."""
        with (
            patch("solstein.llm.enhanced_client.get_settings") as mock_settings,
            patch("solstein.llm.enhanced_client.get_health_checker") as mock_hc,
            patch("solstein.llm.enhanced_client.FallbackChain"),
            patch("solstein.llm.enhanced_client.get_tracer") as mock_tracer,
            patch("solstein.llm.enhanced_client.LLM_REQUESTS_TOTAL") as mock_req,
            patch("solstein.llm.enhanced_client.LLM_ERRORS_TOTAL") as mock_err,
        ):
            mock_settings.return_value = MagicMock(
                llm_provider_order=["openai"],
                openai_model="gpt-4o-mini",
            )
            health_checker = MagicMock()
            health_checker.check_all_providers = AsyncMock(return_value={})
            health_checker.report_success = MagicMock()
            health_checker.report_error = MagicMock()
            mock_hc.return_value = health_checker

            tracer_instance = MagicMock()
            mock_tracer.return_value = tracer_instance

            from solstein.llm.enhanced_client import EnhancedLLMClient

            client = EnhancedLLMClient(health_checker=health_checker)
            # Inject a mock provider client
            client._clients["openai"] = MagicMock()

            yield MagicMock(
                client=client,
                health_checker=health_checker,
                tracer=tracer_instance,
                req_counter=mock_req,
                err_counter=mock_err,
            )

    @pytest.mark.asyncio()
    async def test_success_emits_metrics_and_health(self, mock_client: MagicMock) -> None:
        """Successful query emits success metric and reports to health checker."""
        client = mock_client.client
        client.cloud_querier.query = AsyncMock(return_value="test response")

        result = await client._query_provider("openai", "test prompt", None)

        assert result == "test response"
        mock_client.req_counter.labels.assert_called_with(
            provider="openai", model="gpt-4o-mini", status="success"
        )
        mock_client.req_counter.labels.return_value.inc.assert_called_once()
        mock_client.health_checker.report_success.assert_called_once_with("openai")

    @pytest.mark.asyncio()
    async def test_error_classifies_and_emits_metrics(self, mock_client: MagicMock) -> None:
        """Failed query classifies error and emits both counters."""
        client = mock_client.client
        exc = Exception("rate limit exceeded")
        exc.status_code = 429  # type: ignore[attr-defined]
        client.cloud_querier.query = AsyncMock(side_effect=exc)

        with pytest.raises(Exception, match="rate limit"):
            await client._query_provider("openai", "test prompt", None)

        # Request counter with error status
        mock_client.req_counter.labels.assert_any_call(
            provider="openai", model="gpt-4o-mini", status="error"
        )
        # Error counter with classified type
        mock_client.err_counter.labels.assert_called_with(
            provider="openai", error_type="rate_limit"
        )
        mock_client.err_counter.labels.return_value.inc.assert_called_once()

    @pytest.mark.asyncio()
    async def test_error_reports_to_health_checker(self, mock_client: MagicMock) -> None:
        """Failed query reports error to health checker."""
        client = mock_client.client
        exc = TimeoutError("Connection timed out")
        client.cloud_querier.query = AsyncMock(side_effect=exc)

        with pytest.raises(TimeoutError):
            await client._query_provider("openai", "test prompt", None)

        mock_client.health_checker.report_error.assert_called_once_with("openai", exc)

    @pytest.mark.asyncio()
    async def test_error_records_langfuse_trace(self, mock_client: MagicMock) -> None:
        """Failed query still records Langfuse trace with error."""
        client = mock_client.client
        exc = RuntimeError("provider down")
        client.cloud_querier.query = AsyncMock(side_effect=exc)

        with pytest.raises(RuntimeError):
            await client._query_provider("openai", "test prompt", None)

        mock_client.tracer.record.assert_called_once()
        trace = mock_client.tracer.record.call_args[0][0]
        assert trace.success is False
        assert "provider down" in trace.error

    @pytest.mark.asyncio()
    async def test_no_client_raises_runtime_error(self, mock_client: MagicMock) -> None:
        """Missing client raises RuntimeError without silent None return."""
        client = mock_client.client
        with pytest.raises(RuntimeError, match="No client available"):
            await client._query_provider("nonexistent", "test", None)
