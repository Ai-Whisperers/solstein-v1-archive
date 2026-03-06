"""Performance benchmarks for data loading operations.

E6: Add loader-level performance benchmarks
Provides timing and throughput measurements for loader operations.
"""

from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable

from loguru import logger


@dataclass
class BenchmarkResult:
    """Result of a benchmark measurement."""

    operation: str
    duration_ms: float
    item_count: int = 0
    throughput_per_second: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.item_count > 0 and self.duration_ms > 0:
            self.throughput_per_second = (self.item_count / self.duration_ms) * 1000


@dataclass
class LoaderBenchmark:
    """Benchmark data for loader operations."""

    total_duration_ms: float = 0.0
    discovery_duration_ms: float = 0.0
    normalization_duration_ms: float = 0.0
    merge_duration_ms: float = 0.0
    enrichment_duration_ms: float = 0.0
    companies_loaded: int = 0
    companies_enriched: int = 0
    errors_count: int = 0
    source_results: list[BenchmarkResult] = field(default_factory=list)
    enrichment_results: list[BenchmarkResult] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert benchmark to dictionary for logging/serialization."""
        return {
            "total_duration_ms": round(self.total_duration_ms, 2),
            "discovery_duration_ms": round(self.discovery_duration_ms, 2),
            "normalization_duration_ms": round(self.normalization_duration_ms, 2),
            "merge_duration_ms": round(self.merge_duration_ms, 2),
            "enrichment_duration_ms": round(self.enrichment_duration_ms, 2),
            "companies_loaded": self.companies_loaded,
            "companies_enriched": self.companies_enriched,
            "errors_count": self.errors_count,
            "throughput_per_second": round((self.companies_loaded / self.total_duration_ms) * 1000, 2)
            if self.total_duration_ms > 0
            else 0,
        }


class PerformanceBenchmark:
    """Performance benchmark utility for loader operations.

    E6: Provides timing and throughput measurements for all loader phases.
    """

    def __init__(self) -> None:
        self.results: list[BenchmarkResult] = []
        self.loader_benchmarks: list[LoaderBenchmark] = []

    @contextmanager
    def measure(self, operation: str, item_count: int = 0, **metadata: Any):
        """Context manager for measuring operation duration.

        Args:
            operation: Name of the operation being measured
            item_count: Number of items processed (for throughput calculation)
            **metadata: Additional metadata to store with the result

        Example:
            with benchmark.measure("discovery", item_count=100):
                companies = await discover_companies()
        """
        start_time = time.perf_counter()
        try:
            yield self
        finally:
            duration_ms = (time.perf_counter() - start_time) * 1000
            result = BenchmarkResult(
                operation=operation,
                duration_ms=duration_ms,
                item_count=item_count,
                metadata=metadata,
            )
            self.results.append(result)
            logger.debug(
                "Benchmark completed",
                operation=operation,
                duration_ms=round(duration_ms, 2),
                throughput_per_second=round(result.throughput_per_second, 2),
            )

    def measure_sync(
        self,
        operation: str,
        fn: Callable[..., T],
        *args: Any,
        item_count: int = 0,
        **metadata: Any,
    ) -> T:
        """Measure a synchronous function call.

        Args:
            operation: Name of the operation
            fn: Function to measure
            *args: Arguments to pass to the function
            item_count: Number of items processed
            **metadata: Additional metadata

        Returns:
            Result of the function call
        """
        start_time = time.perf_counter()
        try:
            result = fn(*args)
            return result
        finally:
            duration_ms = (time.perf_counter() - start_time) * 1000
            benchmark_result = BenchmarkResult(
                operation=operation,
                duration_ms=duration_ms,
                item_count=item_count,
                metadata=metadata,
            )
            self.results.append(benchmark_result)

    async def measure_async(
        self,
        operation: str,
        coro: Any,
        item_count: int = 0,
        **metadata: Any,
    ) -> Any:
        """Measure an async operation.

        Args:
            operation: Name of the operation
            coro: Coroutine to measure
            item_count: Number of items processed
            **metadata: Additional metadata

        Returns:
            Result of the coroutine
        """
        import asyncio

        start_time = time.perf_counter()
        try:
            result = await coro
            return result
        finally:
            duration_ms = (time.perf_counter() - start_time) * 1000
            benchmark_result = BenchmarkResult(
                operation=operation,
                duration_ms=duration_ms,
                item_count=item_count,
                metadata=metadata,
            )
            self.results.append(benchmark_result)

    def get_summary(self) -> dict[str, Any]:
        """Get summary of all benchmark results."""
        if not self.results:
            return {"message": "No benchmarks recorded"}

        total_duration = sum(r.duration_ms for r in self.results)
        total_items = sum(r.item_count for r in self.results)

        by_operation: dict[str, list[BenchmarkResult]] = {}
        for result in self.results:
            by_operation.setdefault(result.operation, []).append(result)

        operation_stats = {}
        for op, results in by_operation.items():
            durations = [r.duration_ms for r in results]
            operation_stats[op] = {
                "count": len(results),
                "total_ms": round(sum(durations), 2),
                "avg_ms": round(sum(durations) / len(durations), 2),
                "min_ms": round(min(durations), 2),
                "max_ms": round(max(durations), 2),
            }

        return {
            "total_benchmarks": len(self.results),
            "total_duration_ms": round(total_duration, 2),
            "total_items_processed": total_items,
            "overall_throughput_per_second": round((total_items / total_duration) * 1000, 2)
            if total_duration > 0
            else 0,
            "by_operation": operation_stats,
        }

    def reset(self) -> None:
        """Clear all benchmark results."""
        self.results.clear()
        self.loader_benchmarks.clear()


# Global benchmark instance for convenience
_default_benchmark: PerformanceBenchmark | None = None


def get_benchmark() -> PerformanceBenchmark:
    """Get the global benchmark instance."""
    global _default_benchmark
    if _default_benchmark is None:
        _default_benchmark = PerformanceBenchmark()
    return _default_benchmark


def reset_benchmark() -> None:
    """Reset the global benchmark instance."""
    global _default_benchmark
    _default_benchmark = None


@contextmanager
def benchmark_operation(operation: str, item_count: int = 0, **metadata: Any):
    """Convenience context manager using global benchmark.

    Example:
        with benchmark_operation("data_load", item_count=1000):
            await load_data()
    """
    benchmark = get_benchmark()
    with benchmark.measure(operation, item_count, **metadata):
        yield benchmark


def log_benchmark_summary(level: str = "info") -> None:
    """Log the current benchmark summary.

    Args:
        level: Log level (debug, info, warning, error)
    """
    benchmark = get_benchmark()
    summary = benchmark.get_summary()

    log_fn = getattr(logger, level, logger.info)
    log_fn("Performance benchmark summary", **summary)


class LoaderPerformanceMonitor:
    """Monitor performance of loader operations.

    E6: Integrated with UnifiedLoaderOrchestrator for automatic benchmarking.
    """

    def __init__(self) -> None:
        self.benchmark = LoaderBenchmark()
        self._phase_start_times: dict[str, float] = {}

    def start_phase(self, phase: str) -> None:
        """Start timing a loader phase."""
        self._phase_start_times[phase] = time.perf_counter()

    def end_phase(self, phase: str) -> None:
        """End timing a loader phase and record duration."""
        if phase not in self._phase_start_times:
            logger.warning(f"Phase '{phase}' was not started")
            return

        duration_ms = (time.perf_counter() - self._phase_start_times[phase]) * 1000

        # Map phase names to benchmark fields
        field_map = {
            "discovery": "discovery_duration_ms",
            "normalization": "normalization_duration_ms",
            "merge": "merge_duration_ms",
            "enrichment": "enrichment_duration_ms",
            "total": "total_duration_ms",
        }

        if phase in field_map:
            setattr(self.benchmark, field_map[phase], duration_ms)

        del self._phase_start_times[phase]

    @contextmanager
    def measure_phase(self, phase: str):
        """Context manager for measuring a loader phase."""
        self.start_phase(phase)
        try:
            yield self
        finally:
            self.end_phase(phase)

    def record_source_result(self, source_name: str, duration_ms: float, item_count: int) -> None:
        """Record benchmark result for a data source."""
        result = BenchmarkResult(
            operation=f"source:{source_name}",
            duration_ms=duration_ms,
            item_count=item_count,
        )
        self.benchmark.source_results.append(result)

    def record_enrichment_result(
        self, connector_name: str, duration_ms: float, item_count: int, success_count: int
    ) -> None:
        """Record benchmark result for an enrichment connector."""
        result = BenchmarkResult(
            operation=f"enrichment:{connector_name}",
            duration_ms=duration_ms,
            item_count=item_count,
            metadata={"success_count": success_count},
        )
        self.benchmark.enrichment_results.append(result)

    def finalize(
        self,
        companies_loaded: int,
        companies_enriched: int,
        errors_count: int,
    ) -> LoaderBenchmark:
        """Finalize the benchmark with final counts."""
        self.benchmark.companies_loaded = companies_loaded
        self.benchmark.companies_enriched = companies_enriched
        self.benchmark.errors_count = errors_count

        # Calculate total if not already set
        if self.benchmark.total_duration_ms == 0:
            self.benchmark.total_duration_ms = (
                self.benchmark.discovery_duration_ms
                + self.benchmark.normalization_duration_ms
                + self.benchmark.merge_duration_ms
                + self.benchmark.enrichment_duration_ms
            )

        return self.benchmark

    def log_summary(self) -> None:
        """Log the benchmark summary."""
        summary = self.benchmark.to_dict()
        logger.info("Loader performance summary", **summary)


# Type variable for generic return type
T = Any
