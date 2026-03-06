"""Tests for dependency tracing.

This module tests the DependencyTracer that tracks outbound calls
to databases, LLMs, and external services with timing and metrics.
"""

import pytest
import asyncio
from unittest.mock import patch

from solstein.utils.tracing import DependencyTracer, DependencyCall, tracer, get_tracer


class TestDependencyTracer:
    """Test DependencyTracer functionality."""

    def test_tracer_singleton(self):
        """Test that get_tracer returns singleton."""
        t1 = get_tracer()
        t2 = get_tracer()
        assert t1 is t2
        assert t1 is tracer

    @pytest.mark.asyncio
    async def test_successful_call_traced(self):
        """Test successful dependency call is traced."""
        test_tracer = DependencyTracer()

        async with test_tracer.trace("test-service", "test-op", key="value"):
            await asyncio.sleep(0.01)

        assert len(test_tracer._calls) == 1
        call = test_tracer._calls[0]
        assert call.service == "test-service"
        assert call.operation == "test-op"
        assert call.success is True
        assert call.metadata["key"] == "value"
        assert call.duration_ms >= 10  # At least 10ms

    @pytest.mark.asyncio
    async def test_failed_call_traced(self):
        """Test failed dependency call is traced."""
        test_tracer = DependencyTracer()

        with pytest.raises(ValueError):
            async with test_tracer.trace("test-service", "failing-op"):
                raise ValueError("Test error")

        assert len(test_tracer._calls) == 1
        call = test_tracer._calls[0]
        assert call.success is False
        assert call.error_type == "ValueError"

    @pytest.mark.asyncio
    async def test_span_metadata_updated(self):
        """Test span metadata can be updated during trace."""
        test_tracer = DependencyTracer()

        async with test_tracer.trace("db", "query") as span:
            span["rows"] = 100
            span["table"] = "users"

        call = test_tracer._calls[0]
        assert call.metadata["rows"] == 100
        assert call.metadata["table"] == "users"

    def test_max_calls_limit(self):
        """Test that old calls are dropped when limit reached."""
        test_tracer = DependencyTracer()
        test_tracer._max_calls = 10

        # Add 15 calls
        for i in range(15):
            test_tracer._record_call(DependencyCall("svc", "op", float(i), True))

        # Should have dropped oldest half
        assert len(test_tracer._calls) < 15


class TestMetricsCalculation:
    """Test metrics calculation."""

    def test_empty_metrics(self):
        """Test metrics with no calls."""
        test_tracer = DependencyTracer()
        metrics = test_tracer.get_metrics()
        assert metrics == {}

    def test_single_service_metrics(self):
        """Test metrics for single service."""
        test_tracer = DependencyTracer()
        test_tracer._calls = [
            DependencyCall("db", "query", 10.0, True),
            DependencyCall("db", "query", 20.0, True),
            DependencyCall("db", "query", 30.0, False),
        ]

        metrics = test_tracer.get_metrics()

        assert "db" in metrics
        db_metrics = metrics["db"]
        assert db_metrics["total_calls"] == 3
        assert db_metrics["error_count"] == 1
        assert db_metrics["error_rate"] == 1 / 3
        assert db_metrics["latency_ms"]["p50"] == 20.0
        assert db_metrics["latency_ms"]["max"] == 30.0

    def test_multiple_services_metrics(self):
        """Test metrics for multiple services."""
        test_tracer = DependencyTracer()
        test_tracer._calls = [
            DependencyCall("db", "query", 10.0, True),
            DependencyCall("api", "get", 50.0, True),
            DependencyCall("llm", "generate", 1000.0, True),
        ]

        metrics = test_tracer.get_metrics()

        assert "db" in metrics
        assert "api" in metrics
        assert "llm" in metrics

    def test_filter_by_service(self):
        """Test filtering metrics by service."""
        test_tracer = DependencyTracer()
        test_tracer._calls = [
            DependencyCall("db", "query", 10.0, True),
            DependencyCall("api", "get", 50.0, True),
        ]

        metrics = test_tracer.get_metrics(service="db")

        assert "db" in metrics
        assert "api" not in metrics
        assert metrics["db"]["total_calls"] == 1

    def test_percentile_calculation(self):
        """Test percentile calculation."""
        test_tracer = DependencyTracer()
        test_tracer._calls = [
            DependencyCall("svc", "op", float(i), True)
            for i in range(1, 101)  # 1-100
        ]

        metrics = test_tracer.get_metrics()

        svc_metrics = metrics["svc"]["latency_ms"]
        assert svc_metrics["p50"] == 50.0
        assert svc_metrics["p95"] == 95.0
        assert svc_metrics["p99"] == 99.0
        assert svc_metrics["avg"] == 50.5


class TestGlobalTracer:
    """Test the global tracer instance."""

    @pytest.mark.asyncio
    async def test_global_tracer_accumulates(self):
        """Test that global tracer accumulates calls."""
        # Clear existing calls
        tracer._calls = []

        async with tracer.trace("global-test", "op1"):
            pass

        async with tracer.trace("global-test", "op2"):
            pass

        assert len(tracer._calls) >= 2

    def test_global_metrics(self):
        """Test getting metrics from global tracer."""
        metrics = tracer.get_metrics()
        assert isinstance(metrics, dict)
