"""Tests for performance profiling infrastructure.

EPIC-023 Story 1: Test the profiling decorator and utilities.
"""

import asyncio
import time
from pathlib import Path

import pytest

from solstein.monitoring.profiling import (
    ProfileResult,
    profile,
    profiler,
    time_it,
)


class TestPerformanceProfiler:
    """Test the PerformanceProfiler class."""

    def setup_method(self):
        """Reset profiler before each test."""
        profiler.clear()
        profiler.disable()

    def test_profiler_initially_disabled(self):
        """Test that profiler is initially disabled."""
        assert not profiler.is_enabled

    def test_enable_disable(self):
        """Test enabling and disabling profiler."""
        profiler.enable()
        assert profiler.is_enabled

        profiler.disable()
        assert not profiler.is_enabled

    def test_record_result(self):
        """Test recording a profile result."""
        profiler.enable()

        result = ProfileResult(name="test_func", duration_ms=100.0)
        profiler.record(result)

        assert len(profiler.results) == 1
        assert profiler.results[0].name == "test_func"
        assert profiler.results[0].duration_ms == 100.0

    def test_record_when_disabled(self):
        """Test that recording is skipped when disabled."""
        result = ProfileResult(name="test_func", duration_ms=100.0)
        profiler.record(result)

        assert len(profiler.results) == 0

    def test_get_stats(self):
        """Test getting profiling statistics."""
        profiler.enable()

        # Add some results
        profiler.record(ProfileResult(name="func1", duration_ms=100.0))
        profiler.record(ProfileResult(name="func1", duration_ms=200.0))
        profiler.record(ProfileResult(name="func2", duration_ms=50.0))

        stats = profiler.get_stats()

        assert stats["count"] == 3
        assert stats["avg_duration_ms"] == pytest.approx(116.67, abs=0.01)  # (100 + 200 + 50) / 3
        assert stats["min_duration_ms"] == 50.0
        assert stats["max_duration_ms"] == 200.0

    def test_get_stats_by_name(self):
        """Test getting stats for specific function."""
        profiler.enable()

        profiler.record(ProfileResult(name="func1", duration_ms=100.0))
        profiler.record(ProfileResult(name="func1", duration_ms=200.0))
        profiler.record(ProfileResult(name="func2", duration_ms=50.0))

        stats = profiler.get_stats("func1")

        assert stats["count"] == 2
        assert stats["avg_duration_ms"] == 150.0

    def test_clear(self):
        """Test clearing results."""
        profiler.enable()
        profiler.record(ProfileResult(name="test", duration_ms=100.0))

        assert len(profiler.results) == 1

        profiler.clear()

        assert len(profiler.results) == 0


class TestProfileDecorator:
    """Test the @profile decorator."""

    def setup_method(self):
        """Reset profiler before each test."""
        profiler.clear()
        profiler.disable()

    def test_sync_function_profiling(self):
        """Test profiling synchronous function."""
        profiler.enable()

        @profile(name="sync_test")
        def slow_function():
            time.sleep(0.01)  # 10ms
            return "result"

        result = slow_function()

        assert result == "result"
        assert len(profiler.results) == 1
        assert profiler.results[0].name == "sync_test"
        assert profiler.results[0].duration_ms >= 10.0

    @pytest.mark.asyncio
    async def test_async_function_profiling(self):
        """Test profiling asynchronous function."""
        profiler.enable()

        @profile(name="async_test")
        async def async_slow_function():
            await asyncio.sleep(0.01)  # 10ms
            return "async_result"

        result = await async_slow_function()

        assert result == "async_result"
        assert len(profiler.results) == 1
        assert profiler.results[0].name == "async_test"

    def test_profiling_disabled(self):
        """Test that profiling is skipped when disabled."""

        @profile(name="disabled_test")
        def fast_function():
            return "result"

        result = fast_function()

        assert result == "result"
        assert len(profiler.results) == 0

    def test_default_name(self):
        """Test that function name is used as default profile name."""
        profiler.enable()

        @profile()
        def my_function():
            return "result"

        my_function()

        assert profiler.results[0].name == "my_function"


class TestTimeItContextManager:
    """Test the time_it context manager."""

    def setup_method(self):
        """Reset profiler before each test."""
        profiler.clear()
        profiler.disable()

    def test_time_it_sync(self):
        """Test timing synchronous code block."""
        profiler.enable()

        with time_it("block_test"):
            time.sleep(0.01)

        assert len(profiler.results) == 1
        assert profiler.results[0].name == "block_test"
        assert profiler.results[0].duration_ms >= 10.0

    @pytest.mark.asyncio
    async def test_time_it_async(self):
        """Test timing in async context."""
        profiler.enable()

        with time_it("async_block_test"):
            await asyncio.sleep(0.01)

        assert len(profiler.results) == 1
        assert profiler.results[0].name == "async_block_test"

    def test_time_it_disabled(self):
        """Test that timing is skipped when disabled."""

        with time_it("disabled_block"):
            pass

        assert len(profiler.results) == 0


class TestProfileResult:
    """Test the ProfileResult dataclass."""

    def test_to_dict(self):
        """Test converting result to dictionary."""
        result = ProfileResult(
            name="test",
            duration_ms=100.0,
            memory_delta_mb=5.0,
            calls=2,
            metadata={"key": "value"},
        )

        data = result.to_dict()

        assert data["name"] == "test"
        assert data["duration_ms"] == 100.0
        assert data["memory_delta_mb"] == 5.0
        assert data["calls"] == 2
        assert data["metadata"] == {"key": "value"}


class TestExport:
    """Test exporting profiling results."""

    def setup_method(self):
        """Reset profiler before each test."""
        profiler.clear()
        profiler.disable()

    def test_export_json(self, tmp_path: Path):
        """Test exporting results to JSON."""
        profiler.enable()
        profiler.record(ProfileResult(name="test", duration_ms=100.0))

        output_file = tmp_path / "test_export.json"
        profiler.export_json(output_file)

        assert output_file.exists()
        content = output_file.read_text()
        assert "test" in content
        assert "100.0" in content


# Integration test
@pytest.mark.integration
class TestProfilingIntegration:
    """Integration tests for profiling infrastructure."""

    def setup_method(self):
        """Reset profiler before each test."""
        profiler.clear()

    def test_full_profiling_workflow(self):
        """Test complete profiling workflow."""
        # Enable profiling
        profiler.enable()

        # Profile some functions
        @profile(name="workflow_test")
        def func1():
            time.sleep(0.005)
            return 1

        @profile(name="workflow_test")
        def func2():
            time.sleep(0.005)
            return 2

        func1()
        func2()

        # Check results
        assert len(profiler.results) == 2

        # Get stats
        stats = profiler.get_stats("workflow_test")
        assert stats["count"] == 2

        # Clear and verify
        profiler.clear()
        assert len(profiler.results) == 0
