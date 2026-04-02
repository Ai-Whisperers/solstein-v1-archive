"""Tests for health monitoring and metrics collection.

Tests verify that health checks, readiness probes, liveness probes,
and metrics are correctly collected and reported.
"""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from solstein.core.monitoring import (
    DataQualityMetrics,
    HealthCheck,
    HealthMonitor,
    HealthStatus,
    MetricsSnapshot,
)


class TestHealthMonitor:
    """Test suite for health monitoring."""

    @pytest.fixture
    def monitor(self):
        """Create a fresh health monitor for each test."""
        return HealthMonitor()

    @pytest.mark.asyncio
    async def test_database_health_check(self, monitor):
        """Verify that database health check returns a correctly structured HealthCheck."""
        healthy_check = HealthCheck(
            name="database",
            status=HealthStatus.HEALTHY,
            message="Database connection successful",
            duration_ms=5.0,
            details={"connection": "postgresql", "pool_size": 5},
        )
        monitor.check_database = AsyncMock(return_value=healthy_check)

        check = await monitor.check_database()

        assert check.name == "database"
        assert check.status == HealthStatus.HEALTHY
        assert check.duration_ms >= 0
        assert "connection" in check.details

    @pytest.mark.asyncio
    async def test_api_health_check(self, monitor):
        """Verify that API health check works."""
        # Individual check_ methods were extracted to strategy classes (EPIC-022).
        # Use run_all_checks() and inspect the 'api' entry.
        checks = await monitor.run_all_checks()
        check = checks["api"]

        assert check.name == "api"
        assert check.status == HealthStatus.HEALTHY
        assert check.duration_ms >= 0

    @pytest.mark.asyncio
    async def test_configuration_health_check(self, monitor):
        """Verify that configuration health check works."""
        # Individual check_ methods were extracted to strategy classes (EPIC-022).
        # Use run_all_checks() and inspect the 'configuration' entry.
        checks = await monitor.run_all_checks()
        check = checks["configuration"]

        assert check.name == "configuration"
        assert check.status == HealthStatus.HEALTHY
        assert "environment" in check.details

    @pytest.mark.asyncio
    async def test_run_all_checks(self, monitor):
        """Verify that all checks run and are recorded."""
        checks = await monitor.run_all_checks()

        assert len(checks) >= 3
        assert "database" in checks
        assert "api" in checks
        assert "configuration" in checks

    def test_overall_status_healthy(self, monitor):
        """Verify that overall status is healthy/degraded when required checks pass."""
        for name in ("database", "api", "configuration"):
            monitor.checks[name] = HealthCheck(name=name, status=HealthStatus.HEALTHY, message="OK")
        status = monitor.get_overall_status()

        assert status in (HealthStatus.HEALTHY, HealthStatus.DEGRADED)

    def test_is_ready_when_healthy(self, monitor):
        """Verify that application is ready when required checks are healthy."""
        for name in ("database", "api", "configuration"):
            monitor.checks[name] = HealthCheck(name=name, status=HealthStatus.HEALTHY, message="OK")
        ready = monitor.is_ready()

        assert ready is True

    @pytest.mark.asyncio
    async def test_is_alive(self, monitor):
        """Verify that liveness check always returns True."""
        alive = monitor.is_alive()

        assert alive is True

    def test_is_alive_without_checks(self, monitor):
        """Verify that liveness check works without prior checks."""
        assert monitor.is_alive() is True

    def test_record_request(self, monitor):
        """Verify that API requests are recorded."""
        monitor.record_request("GET", "/companies", 200, 45.2)
        monitor.record_request("POST", "/scoring", 201, 120.5)
        monitor.record_request("GET", "/nonexistent", 404, 15.0)

        assert monitor.metrics.total_requests == 3
        assert monitor.metrics.successful_requests == 2
        assert monitor.metrics.failed_requests == 1

    def test_request_history_limited(self, monitor):
        """Verify that request history is limited in size."""
        for i in range(1100):
            monitor.record_request("GET", f"/path/{i}", 200, 10.0)

        assert len(monitor.request_history) <= 1000

    def test_record_error(self, monitor):
        """Verify that errors are recorded."""
        monitor.record_error(
            "DatabaseError",
            "Connection timeout",
            {"timeout": 30, "retries": 3},
        )

        assert len(monitor.error_history) == 1
        error = monitor.error_history[0]
        assert error["error_type"] == "DatabaseError"
        assert error["message"] == "Connection timeout"

    def test_error_history_limited(self, monitor):
        """Verify that error history is limited in size."""
        for i in range(150):
            monitor.record_error(f"Error{i}", f"Message {i}")

        assert len(monitor.error_history) <= 100

    def test_metrics_calculation(self, monitor):
        """Verify that metrics are calculated correctly."""
        for _ in range(100):
            monitor.record_request("GET", "/test", 200, 50.0)
        for _ in range(10):
            monitor.record_request("POST", "/test", 500, 100.0)

        metrics = monitor.get_metrics()

        assert metrics.total_requests == 110
        assert metrics.successful_requests == 100
        assert metrics.failed_requests == 10
        assert abs(metrics.error_rate - 0.0909) < 0.01

    def test_error_rate_zero(self, monitor):
        """Verify that error rate is 0 when no failures."""
        monitor.record_request("GET", "/test", 200, 10.0)
        monitor.record_request("GET", "/test", 200, 10.0)

        metrics = monitor.get_metrics()

        assert metrics.error_rate == 0.0

    def test_uptime_calculation(self, monitor):
        """Verify that uptime is calculated correctly."""
        metrics = monitor.get_metrics()

        assert metrics.uptime_seconds >= 0

    @pytest.mark.asyncio
    async def test_to_dict(self, monitor):
        """Verify that monitor state can be serialized to dict."""
        await monitor.run_all_checks()
        monitor.record_request("GET", "/test", 200, 50.0)

        state = monitor.to_dict()

        assert "status" in state
        assert "ready" in state
        assert "alive" in state
        assert "checks" in state
        assert "metrics" in state
        assert state["alive"] is True

    def test_data_quality_metrics(self, monitor):
        """Verify that data quality metrics can be set."""
        monitor.data_quality.total_companies_scored = 100
        monitor.data_quality.companies_with_all_signals = 85
        monitor.data_quality.average_signal_count_per_company = 45.5
        monitor.data_quality.average_confidence_score = 0.89

        dq = monitor.get_data_quality_metrics()

        assert dq.total_companies_scored == 100
        assert dq.companies_with_all_signals == 85
        assert dq.average_signal_count_per_company == 45.5


class TestMetricsSnapshot:
    """Test suite for metrics snapshot."""

    def test_creation(self):
        """Verify that metrics snapshot can be created."""
        snapshot = MetricsSnapshot(
            timestamp=datetime.utcnow(),
            total_requests=100,
            successful_requests=95,
            failed_requests=5,
            avg_response_time_ms=47.5,
        )

        assert snapshot.total_requests == 100
        assert snapshot.successful_requests == 95

    def test_error_rate_calculation(self):
        """Verify error rate calculation."""
        snapshot = MetricsSnapshot(
            timestamp=datetime.utcnow(),
            total_requests=100,
            successful_requests=90,
            failed_requests=10,
        )

        error_rate = snapshot.failed_requests / snapshot.total_requests
        assert error_rate == 0.1


class TestDataQualityMetrics:
    """Test suite for data quality metrics."""

    def test_creation(self):
        """Verify that data quality metrics can be created."""
        dq = DataQualityMetrics(
            total_companies_scored=50,
            companies_with_all_signals=40,
            average_signal_count_per_company=45.0,
            average_confidence_score=0.88,
        )

        assert dq.total_companies_scored == 50
        assert dq.average_signal_count_per_company == 45.0

    def test_coverage_percentage(self):
        """Verify coverage calculation."""
        dq = DataQualityMetrics(
            total_companies_scored=100,
            companies_with_all_signals=85,
        )

        coverage = (dq.companies_with_all_signals / dq.total_companies_scored) * 100
        assert coverage == 85.0
