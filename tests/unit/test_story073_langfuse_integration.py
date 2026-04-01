"""Tests for STORY-073: Langfuse Integration for Cost Tracking and Prompt Management.

Acceptance criteria:
- Every LLM call appears as a trace with token counts and cost estimate
- Langfuse unavailability does not cause LLM call failures
- Prompts retrieved from PromptManager (Langfuse-first, local fallback)
- UsageTracker class is deleted
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from solstein.llm.prompts import _DEFAULT_PROMPTS, PromptManager, get_prompt
from solstein.llm.tracing import LLMTracer, TraceRecord, reset_tracer

# ---------------------------------------------------------------------------
# TraceRecord tests
# ---------------------------------------------------------------------------


class TestTraceRecord:
    """Verify TraceRecord captures all required fields."""

    def test_trace_record_defaults(self):
        record = TraceRecord(prompt="test prompt")
        assert record.provider == ""
        assert record.model == ""
        assert record.success is True
        assert record.input_tokens == 0
        assert record.correlation_id is None
        assert record.tenant_id is None

    def test_trace_record_full(self):
        record = TraceRecord(
            prompt="Analyze Stripe",
            provider="deepinfra",
            model="meta-llama/Llama-3.3-70B-Instruct",
            latency_s=1.5,
            success=True,
            input_tokens=150,
            output_tokens=300,
            cost_usd=0.0012,
            correlation_id="req-123",
            tenant_id="tenant-abc",
        )
        assert record.provider == "deepinfra"
        assert record.cost_usd == 0.0012
        assert record.correlation_id == "req-123"
        assert record.tenant_id == "tenant-abc"


# ---------------------------------------------------------------------------
# LLMTracer tests
# ---------------------------------------------------------------------------


class TestLLMTracer:
    """Verify LLMTracer records and reports correctly."""

    def test_record_and_stats(self):
        tracer = LLMTracer()
        tracer.record(TraceRecord(prompt="test1", latency_s=1.0, success=True))
        tracer.record(TraceRecord(prompt="test2", latency_s=2.0, success=False, error="timeout"))

        stats = tracer.stats()
        assert stats["total"] == 2
        assert stats["success"] == 1
        assert stats["failure"] == 1
        assert stats["avg_latency_s"] == 1.5

    def test_empty_stats(self):
        tracer = LLMTracer()
        stats = tracer.stats()
        assert stats["total"] == 0

    def test_bounded_buffer(self):
        tracer = LLMTracer(max_records=3)
        for i in range(5):
            tracer.record(TraceRecord(prompt=f"prompt-{i}"))
        assert len(tracer._records) == 3

    def test_langfuse_not_enabled_without_settings(self):
        tracer = LLMTracer()
        assert tracer.langfuse_enabled is False

    def test_langfuse_not_enabled_without_keys(self):
        mock_settings = MagicMock()
        mock_settings.langfuse_public_key = None
        mock_settings.langfuse_secret_key = None
        tracer = LLMTracer(settings=mock_settings)
        assert tracer.langfuse_enabled is False

    def test_clear(self):
        tracer = LLMTracer()
        tracer.record(TraceRecord(prompt="test"))
        tracer.clear()
        assert tracer.stats()["total"] == 0

    def test_cost_tracking_in_stats(self):
        tracer = LLMTracer()
        tracer.record(TraceRecord(prompt="t1", cost_usd=0.001))
        tracer.record(TraceRecord(prompt="t2", cost_usd=0.002))
        stats = tracer.stats()
        assert stats["total_cost_usd"] == 0.003


# ---------------------------------------------------------------------------
# Langfuse resilience tests (REQ-5)
# ---------------------------------------------------------------------------


class TestLangfuseResilience:
    """Langfuse failures must not propagate to callers."""

    def test_langfuse_trace_failure_is_swallowed(self):
        """If Langfuse emission fails, the record is still kept."""
        tracer = LLMTracer()
        mock_langfuse = MagicMock()
        mock_langfuse.trace.side_effect = ConnectionError("Langfuse down")
        tracer._langfuse = mock_langfuse

        # Should not raise
        tracer.record(TraceRecord(prompt="test", provider="deepinfra"))
        assert tracer.stats()["total"] == 1

    def test_langfuse_flush_failure_is_swallowed(self):
        tracer = LLMTracer()
        mock_langfuse = MagicMock()
        mock_langfuse.flush.side_effect = ConnectionError("Langfuse down")
        tracer._langfuse = mock_langfuse

        # Should not raise
        tracer.flush()

    @pytest.mark.asyncio
    async def test_llm_call_succeeds_without_langfuse(self):
        """LLM calls work fine without Langfuse configured."""
        from solstein.llm.enhanced_client import EnhancedLLMClient

        mock_health = MagicMock()
        mock_health.check_all_providers = AsyncMock(return_value={})
        mock_health.get_health = MagicMock(return_value=None)
        mock_health.report_success = MagicMock()

        client = EnhancedLLMClient(health_checker=mock_health)
        mock_querier = MagicMock()
        mock_querier.query = AsyncMock(return_value="Analysis result")
        client.cloud_querier = mock_querier

        with patch.object(client, "_get_client", return_value=MagicMock()):
            result = await client.generate("Analyze company X")

        assert result == "Analysis result"


# ---------------------------------------------------------------------------
# PromptManager tests
# ---------------------------------------------------------------------------


class TestPromptManager:
    """Test prompt retrieval with Langfuse-first, local fallback."""

    def test_local_fallback_when_no_langfuse(self):
        pm = PromptManager(langfuse_client=None)
        prompt = pm.get("research_planner", company_name="Acme", industry_context="in Tech")
        assert "Acme" in prompt
        assert "search queries" in prompt

    def test_unknown_prompt_returns_empty(self):
        pm = PromptManager(langfuse_client=None)
        prompt = pm.get("nonexistent_prompt")
        assert prompt == ""

    def test_langfuse_prompt_used_when_available(self):
        mock_lf = MagicMock()
        mock_prompt = MagicMock()
        mock_prompt.prompt = "Custom Langfuse prompt for {company_name}"
        mock_lf.get_prompt.return_value = mock_prompt

        pm = PromptManager(langfuse_client=mock_lf)
        result = pm.get("research_planner", company_name="Acme", industry_context="")
        assert result == "Custom Langfuse prompt for Acme"

    def test_langfuse_failure_falls_back_to_local(self):
        mock_lf = MagicMock()
        mock_lf.get_prompt.side_effect = ConnectionError("Langfuse down")

        pm = PromptManager(langfuse_client=mock_lf)
        prompt = pm.get("research_planner", company_name="Acme", industry_context="")
        assert "Acme" in prompt  # Got local fallback

    def test_all_default_prompts_exist(self):
        """All required default prompts are defined."""
        required = [
            "research_planner",
            "company_extractor",
            "system_research_planner",
            "system_company_extractor",
            "system_business_analyst",
            "system_data_extractor",
        ]
        for name in required:
            assert name in _DEFAULT_PROMPTS, f"Missing default prompt: {name}"

    def test_get_prompt_convenience_function(self):
        prompt = get_prompt("system_business_analyst")
        assert "business analyst" in prompt.lower()


# ---------------------------------------------------------------------------
# UsageTracker deletion verification
# ---------------------------------------------------------------------------


class TestUsageTrackerDeleted:
    """Verify UsageTracker class no longer exists (REQ-6/AC)."""

    def test_usage_tracker_file_deleted(self):
        import importlib

        with pytest.raises(ImportError):
            importlib.import_module("solstein.llm.usage_tracker")

    def test_usage_tracker_not_in_exports(self):
        import solstein.llm as llm_mod

        assert not hasattr(llm_mod, "UsageTracker")
        assert not hasattr(llm_mod, "get_usage_tracker")


# ---------------------------------------------------------------------------
# Enhanced client tracing integration
# ---------------------------------------------------------------------------


class TestEnhancedClientTracing:
    """Verify enhanced client emits trace records."""

    @pytest.mark.asyncio
    async def test_successful_call_emits_trace(self):
        from solstein.llm.enhanced_client import EnhancedLLMClient

        reset_tracer()

        mock_health = MagicMock()
        mock_health.check_all_providers = AsyncMock(return_value={})
        mock_health.get_health = MagicMock(return_value=None)
        mock_health.report_success = MagicMock()

        client = EnhancedLLMClient(health_checker=mock_health)
        mock_querier = MagicMock()
        mock_querier.query = AsyncMock(return_value="test result")
        client.cloud_querier = mock_querier

        with patch.object(client, "_get_client", return_value=MagicMock()):
            await client.generate("Test prompt")

        from solstein.llm.tracing import get_tracer

        tracer = get_tracer()
        stats = tracer.stats()
        assert stats["total"] >= 1
        assert stats["success"] >= 1
