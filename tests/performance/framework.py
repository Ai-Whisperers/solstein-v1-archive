"""Performance testing framework using pytest-benchmark and locust.

EPIC-029 Story 4: Performance and load testing utilities.

Usage:
    # API latency benchmark
    def test_company_endpoint_latency(benchmark):
        benchmark.pedantic(client.get, args=("/api/v1/companies/123",), rounds=100)

    # Load testing with locust
    locust -f tests/performance/locustfile.py --host=http://localhost:8000
"""

import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import pytest


@dataclass
class PerformanceThresholds:
    """Performance thresholds for different operations."""

    api_latency_p95_ms: float = 200.0
    api_latency_p99_ms: float = 500.0
    database_query_ms: float = 50.0
    llm_request_seconds: float = 10.0
    export_generation_seconds: float = 30.0
    enrichment_per_company_seconds: float = 5.0


class PerformanceMonitor:
    """Monitor performance of operations."""

    def __init__(self, thresholds: PerformanceThresholds | None = None):
        """Initialize monitor.

        Args:
            thresholds: Performance thresholds.
        """
        self.thresholds = thresholds or PerformanceThresholds()
        self.measurements: list[dict[str, Any]] = []

    def measure(self, name: str, duration_ms: float) -> dict[str, Any]:
        """Record a performance measurement.

        Args:
            name: Operation name.
            duration_ms: Duration in milliseconds.

        Returns:
            Measurement result with threshold check.
        """
        threshold = self._get_threshold(name)
        passed = duration_ms <= threshold if threshold else True

        measurement = {
            "name": name,
            "duration_ms": duration_ms,
            "threshold_ms": threshold,
            "passed": passed,
            "timestamp": time.time(),
        }

        self.measurements.append(measurement)
        return measurement

    def _get_threshold(self, name: str) -> float | None:
        """Get threshold for operation.

        Args:
            name: Operation name.

        Returns:
            Threshold or None.
        """
        thresholds = {
            "api_latency": self.thresholds.api_latency_p95_ms,
            "db_query": self.thresholds.database_query_ms,
            "llm_request": self.thresholds.llm_request_seconds * 1000,
            "export": self.thresholds.export_generation_seconds * 1000,
            "enrichment": self.thresholds.enrichment_per_company_seconds * 1000,
        }
        return thresholds.get(name)

    def get_summary(self) -> dict[str, Any]:
        """Get performance summary.

        Returns:
            Summary statistics.
        """
        if not self.measurements:
            return {"total": 0, "passed": 0, "failed": 0}

        passed = sum(1 for m in self.measurements if m["passed"])
        failed = len(self.measurements) - passed

        return {
            "total": len(self.measurements),
            "passed": passed,
            "failed": failed,
            "pass_rate": passed / len(self.measurements),
        }


@pytest.fixture
def performance_monitor():
    """Fixture providing performance monitor.

    Yields:
        PerformanceMonitor instance.
    """
    monitor = PerformanceMonitor()
    yield monitor
    # Print summary after test
    summary = monitor.get_summary()
    if summary["failed"] > 0:
        pytest.warn(f"Performance check: {summary['failed']} measurements failed threshold")


def benchmark_with_threshold(benchmark, func: Callable, threshold_ms: float, *args, **kwargs) -> Any:
    """Benchmark function with threshold check.

    Args:
        benchmark: pytest-benchmark fixture.
        func: Function to benchmark.
        threshold_ms: Maximum acceptable duration.
        *args: Function arguments.
        **kwargs: Function keyword arguments.

    Returns:
        Function result.
    """
    result = benchmark.pedantic(func, args=args, kwargs=kwargs, rounds=10)

    # Check if benchmark exceeded threshold
    stats = benchmark.stats
    if stats["max"] > threshold_ms:
        pytest.warn(f"Benchmark {func.__name__} exceeded threshold: {stats['max']:.2f}ms > {threshold_ms}ms")

    return result


# Load testing with locust
LOCUSTFILE_TEMPLATE = '''
"""Locust load testing configuration."""

from locust import HttpUser, task, between


class APIUser(HttpUser):
    """Simulate API user behavior."""

    wait_time = between(1, 3)

    def on_start(self):
        """Login on start."""
        # Authenticate if needed
        pass

    @task(10)
    def get_companies(self):
        """Browse companies list."""
        self.client.get("/api/v1/companies")

    @task(5)
    def get_company_detail(self):
        """View company details."""
        self.client.get("/api/v1/companies/123")

    @task(3)
    def search_companies(self):
        """Search companies."""
        self.client.get("/api/v1/companies/search?q=test")

    @task(1)
    def create_research(self):
        """Create research run."""
        self.client.post(
            "/api/v1/research",
            json={"market": "energy", "filters": {}}
        )

    @task(1)
    def generate_export(self):
        """Generate export."""
        self.client.post(
            "/api/v1/exports",
            json={"format": "xlsx", "company_ids": ["123"]}
        )


class HeavyUser(HttpUser):
    """Simulate heavy API user."""

    wait_time = between(0.5, 1)

    @task(1)
    def bulk_operations(self):
        """Perform bulk operations."""
        for i in range(10):
            self.client.get(f"/api/v1/companies/{i}")
'''


def generate_locustfile(path: str = "tests/performance/locustfile.py"):
    """Generate locustfile for load testing.

    Args:
        path: Path to write locustfile.
    """
    with open(path, "w") as f:
        f.write(LOCUSTFILE_TEMPLATE)


class LoadTestRunner:
    """Run load tests programmatically."""

    def __init__(self, host: str, users: int = 100, spawn_rate: int = 10):
        """Initialize runner.

        Args:
            host: Target host URL.
            users: Number of concurrent users.
            spawn_rate: User spawn rate per second.
        """
        self.host = host
        self.users = users
        self.spawn_rate = spawn_rate

    async def run(self, duration_seconds: int = 60) -> dict[str, Any]:
        """Run load test.

        Args:
            duration_seconds: Test duration.

        Returns:
            Test results.
        """
        # In production, use locust's Python API
        return {
            "host": self.host,
            "users": self.users,
            "duration": duration_seconds,
            "status": "not_implemented",
        }


# Performance benchmarks
class BenchmarkSuite:
    """Suite of performance benchmarks."""

    @staticmethod
    def benchmark_company_retrieval(benchmark, client, company_id: str = "123"):
        """Benchmark company retrieval endpoint.

        Args:
            benchmark: pytest-benchmark fixture.
            client: HTTP client.
            company_id: Company ID to retrieve.
        """
        benchmark.pedantic(
            client.get,
            args=(f"/api/v1/companies/{company_id}",),
            rounds=100,
            iterations=1,
        )

    @staticmethod
    def benchmark_company_list(benchmark, client, page_size: int = 50):
        """Benchmark company list endpoint.

        Args:
            benchmark: pytest-benchmark fixture.
            client: HTTP client.
            page_size: Number of companies per page.
        """
        benchmark.pedantic(
            client.get,
            args=(f"/api/v1/companies?limit={page_size}",),
            rounds=50,
            iterations=1,
        )

    @staticmethod
    def benchmark_enrichment_pipeline(benchmark, enricher, company_ids: list[str]):
        """Benchmark enrichment pipeline.

        Args:
            benchmark: pytest-benchmark fixture.
            enricher: Enrichment service.
            company_ids: List of company IDs.
        """
        benchmark.pedantic(
            enricher.enrich_batch,
            args=(company_ids,),
            rounds=5,
            iterations=1,
        )

    @staticmethod
    def benchmark_export_generation(benchmark, exporter, company_ids: list[str]):
        """Benchmark export generation.

        Args:
            benchmark: pytest-benchmark fixture.
            exporter: Export service.
            company_ids: List of company IDs.
        """
        benchmark.pedantic(
            exporter.generate_excel,
            args=(company_ids,),
            rounds=3,
            iterations=1,
        )
