"""Tests for benchmarks module.

E6: Tests for loader-level performance benchmarks.
"""

import asyncio
import time

import pytest

from solstein.data.benchmarks import (
    BenchmarkResult,
    LoaderBenchmark,
    LoaderPerformanceMonitor,
    PerformanceBenchmark,
    benchmark_operation,
    get_benchmark,
    reset_benchmark,
)


class TestBenchmarkResult:
    """Tests for BenchmarkResult dataclass."""

    def test_basic_creation(self) -> None:
        result = BenchmarkResult(
            operation="test_op",
            duration_ms=100.0,
            item_count=50,
        )
        assert result.operation == "test_op"
        assert result.duration_ms == 100.0
        assert result.item_count == 50
        assert result.throughput_per_second == 500.0  # (50/100)*1000

    def test_throughput_calculation(self) -> None:
        result = BenchmarkResult(
            operation="test",
            duration_ms=200.0,
            item_count=100,
        )
        assert result.throughput_per_second == 500.0

    def test_zero_duration(self) -> None:
        result = BenchmarkResult(
            operation="test",
            duration_ms=0.0,
            item_count=100,
        )
        assert result.throughput_per_second == 0.0

    def test_zero_items(self) -> None:
        result = BenchmarkResult(
            operation="test",
            duration_ms=100.0,
            item_count=0,
        )
        assert result.throughput_per_second == 0.0


class TestLoaderBenchmark:
    """Tests for LoaderBenchmark dataclass."""

    def test_default_values(self) -> None:
        benchmark = LoaderBenchmark()
        assert benchmark.total_duration_ms == 0.0
        assert benchmark.companies_loaded == 0
        assert benchmark.source_results == []

    def test_to_dict(self) -> None:
        benchmark = LoaderBenchmark(
            total_duration_ms=1000.0,
            discovery_duration_ms=200.0,
            companies_loaded=100,
            errors_count=5,
        )
        result = benchmark.to_dict()

        assert result["total_duration_ms"] == 1000.0
        assert result["discovery_duration_ms"] == 200.0
        assert result["companies_loaded"] == 100
        assert result["errors_count"] == 5
        assert result["throughput_per_second"] == 100.0  # (100/1000)*1000

    def test_throughput_with_zero_duration(self) -> None:
        benchmark = LoaderBenchmark(companies_loaded=100)
        result = benchmark.to_dict()
        assert result["throughput_per_second"] == 0.0


class TestPerformanceBenchmark:
    """Tests for PerformanceBenchmark class."""

    def test_measure_context_manager(self) -> None:
        benchmark = PerformanceBenchmark()

        with benchmark.measure("test_op", item_count=10):
            time.sleep(0.001)  # Small delay

        assert len(benchmark.results) == 1
        assert benchmark.results[0].operation == "test_op"
        assert benchmark.results[0].item_count == 10
        assert benchmark.results[0].duration_ms > 0

    def test_measure_with_metadata(self) -> None:
        benchmark = PerformanceBenchmark()

        with benchmark.measure("test_op", item_count=5, source="test"):
            pass

        assert benchmark.results[0].metadata["source"] == "test"

    def test_measure_sync(self) -> None:
        benchmark = PerformanceBenchmark()

        def test_fn(x: int) -> int:
            time.sleep(0.001)
            return x * 2

        result = benchmark.measure_sync("test_fn", test_fn, 5, item_count=1)

        assert result == 10
        assert len(benchmark.results) == 1
        assert benchmark.results[0].operation == "test_fn"

    @pytest.mark.asyncio
    async def test_measure_async(self) -> None:
        benchmark = PerformanceBenchmark()

        async def async_fn() -> str:
            await asyncio.sleep(0.001)
            return "done"

        result = await benchmark.measure_async("async_op", async_fn(), item_count=1)

        assert result == "done"
        assert len(benchmark.results) == 1

    def test_get_summary_empty(self) -> None:
        benchmark = PerformanceBenchmark()
        summary = benchmark.get_summary()

        assert summary["message"] == "No benchmarks recorded"

    def test_get_summary_with_results(self) -> None:
        benchmark = PerformanceBenchmark()

        # Add some results
        benchmark.results.append(BenchmarkResult(operation="op1", duration_ms=100.0, item_count=10))
        benchmark.results.append(BenchmarkResult(operation="op1", duration_ms=200.0, item_count=20))
        benchmark.results.append(BenchmarkResult(operation="op2", duration_ms=50.0, item_count=5))

        summary = benchmark.get_summary()

        assert summary["total_benchmarks"] == 3
        assert summary["total_duration_ms"] == 350.0
        assert summary["total_items_processed"] == 35

        # Check operation stats
        assert "op1" in summary["by_operation"]
        assert summary["by_operation"]["op1"]["count"] == 2
        assert summary["by_operation"]["op1"]["total_ms"] == 300.0

        assert "op2" in summary["by_operation"]
        assert summary["by_operation"]["op2"]["count"] == 1

    def test_reset(self) -> None:
        benchmark = PerformanceBenchmark()
        benchmark.results.append(BenchmarkResult(operation="test", duration_ms=100.0))

        benchmark.reset()

        assert len(benchmark.results) == 0


class TestGlobalBenchmark:
    """Tests for global benchmark functions."""

    def setup_method(self) -> None:
        reset_benchmark()

    def teardown_method(self) -> None:
        reset_benchmark()

    def test_get_benchmark_creates_instance(self) -> None:
        benchmark = get_benchmark()
        assert isinstance(benchmark, PerformanceBenchmark)

    def test_get_benchmark_returns_same_instance(self) -> None:
        benchmark1 = get_benchmark()
        benchmark2 = get_benchmark()
        assert benchmark1 is benchmark2

    def test_reset_benchmark_creates_new_instance(self) -> None:
        benchmark1 = get_benchmark()
        reset_benchmark()
        benchmark2 = get_benchmark()
        assert benchmark1 is not benchmark2

    def test_benchmark_operation_context_manager(self) -> None:
        with benchmark_operation("test_op", item_count=5):
            time.sleep(0.001)

        benchmark = get_benchmark()
        assert len(benchmark.results) == 1


class TestLoaderPerformanceMonitor:
    """Tests for LoaderPerformanceMonitor class."""

    def test_start_end_phase(self) -> None:
        monitor = LoaderPerformanceMonitor()

        monitor.start_phase("discovery")
        time.sleep(0.001)
        monitor.end_phase("discovery")

        assert monitor.benchmark.discovery_duration_ms > 0

    def test_end_phase_without_start(self) -> None:
        monitor = LoaderPerformanceMonitor()
        # Should not raise error
        monitor.end_phase("discovery")
        assert monitor.benchmark.discovery_duration_ms == 0.0

    def test_measure_phase_context_manager(self) -> None:
        monitor = LoaderPerformanceMonitor()

        with monitor.measure_phase("enrichment"):
            time.sleep(0.001)

        assert monitor.benchmark.enrichment_duration_ms > 0

    def test_record_source_result(self) -> None:
        monitor = LoaderPerformanceMonitor()
        monitor.record_source_result("source_a", 100.0, 50)

        assert len(monitor.benchmark.source_results) == 1
        assert monitor.benchmark.source_results[0].operation == "source:source_a"
        assert monitor.benchmark.source_results[0].item_count == 50

    def test_record_enrichment_result(self) -> None:
        monitor = LoaderPerformanceMonitor()
        monitor.record_enrichment_result("connector_x", 200.0, 30, 25)

        assert len(monitor.benchmark.enrichment_results) == 1
        result = monitor.benchmark.enrichment_results[0]
        assert result.operation == "enrichment:connector_x"
        assert result.metadata["success_count"] == 25

    def test_finalize(self) -> None:
        monitor = LoaderPerformanceMonitor()
        monitor.benchmark.discovery_duration_ms = 100.0
        monitor.benchmark.normalization_duration_ms = 50.0

        result = monitor.finalize(
            companies_loaded=100,
            companies_enriched=80,
            errors_count=5,
        )

        assert result.companies_loaded == 100
        assert result.companies_enriched == 80
        assert result.errors_count == 5
        assert result.total_duration_ms == 150.0  # Sum of phases

    def test_finalize_preserves_existing_total(self) -> None:
        monitor = LoaderPerformanceMonitor()
        monitor.benchmark.total_duration_ms = 500.0
        monitor.benchmark.discovery_duration_ms = 100.0

        result = monitor.finalize(10, 8, 0)

        # Should not recalculate if already set
        assert result.total_duration_ms == 500.0

    def test_all_phases(self) -> None:
        monitor = LoaderPerformanceMonitor()

        with monitor.measure_phase("discovery"):
            time.sleep(0.001)

        with monitor.measure_phase("normalization"):
            time.sleep(0.001)

        with monitor.measure_phase("merge"):
            time.sleep(0.001)

        with monitor.measure_phase("enrichment"):
            time.sleep(0.001)

        monitor.finalize(10, 8, 0)
        summary = monitor.benchmark.to_dict()

        assert summary["discovery_duration_ms"] > 0
        assert summary["normalization_duration_ms"] > 0
        assert summary["merge_duration_ms"] > 0
        assert summary["enrichment_duration_ms"] > 0
