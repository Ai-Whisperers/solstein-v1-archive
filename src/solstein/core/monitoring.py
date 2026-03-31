"""Monitoring, health checks, and metrics collection.

EPIC-022: Refactored to use Strategy Pattern for health checks.
Health checks are now modular strategies in the health_checks/ package.

Provides:
- Health status checks (database connectivity, API responsiveness)
- Readiness probes (dependencies initialized)
- Liveness probes (process running)
- Metrics collection (requests, errors, latency)
- Data quality monitoring
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .health_checks import (
    ApiHealthCheck,
    ConfigurationHealthCheck,
    DatabaseHealthCheck,
    HealthCheck,
    HealthStatus,
    LLMHealthCheck,
    RedisHealthCheck,
)


@dataclass
class MetricsSnapshot:
    """Point-in-time snapshot of metrics."""

    timestamp: datetime
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time_ms: float = 0.0
    error_rate: float = 0.0
    uptime_seconds: int = 0
    database_queries: int = 0
    cache_hits: int = 0
    cache_misses: int = 0


@dataclass
class DataQualityMetrics:
    """Data quality indicators."""

    total_companies_scored: int = 0
    companies_with_all_signals: int = 0
    companies_missing_critical_signals: int = 0
    average_signal_count_per_company: float = 0.0
    average_confidence_score: float = 0.0
    signals_with_low_confidence: int = 0
    last_update: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class HealthMonitor:
    """Monitors application health and readiness using strategy pattern.

    EPIC-022: Health checks are now implemented as separate strategy classes
    in the health_checks/ package for modularity and testability.
    """

    def __init__(self):
        """Initialize health monitor with health check strategies."""
        self.checks: dict[str, HealthCheck] = {}
        self.metrics = MetricsSnapshot(timestamp=datetime.now(timezone.utc))
        self.data_quality = DataQualityMetrics()
        self.startup_time = datetime.now(timezone.utc)
        self.request_history: list[dict[str, Any]] = []
        self.error_history: list[dict[str, Any]] = []

        # Health check strategies
        self._health_strategies = [
            DatabaseHealthCheck(),
            ApiHealthCheck(),
            RedisHealthCheck(),
            ConfigurationHealthCheck(),
            LLMHealthCheck(),
        ]

    async def run_all_checks(self) -> dict[str, HealthCheck]:
        """Run all health checks in parallel.

        Returns:
            Dictionary of check results
        """
        import asyncio

        # Run all health check strategies
        results = await asyncio.gather(*[strategy.check() for strategy in self._health_strategies])

        # Store results
        for check in results:
            self.checks[check.name] = check

        return self.checks

    def get_overall_status(self) -> str:
        """Get overall health status based on checks.

        Returns:
            Overall HealthStatus
        """
        if not self.checks:
            return HealthStatus.UNHEALTHY

        statuses = [check.status for check in self.checks.values()]

        if any(s == HealthStatus.UNHEALTHY for s in statuses):
            return HealthStatus.UNHEALTHY
        if any(s == HealthStatus.DEGRADED for s in statuses):
            return HealthStatus.DEGRADED
        return HealthStatus.HEALTHY

    def is_ready(self) -> bool:
        """Check if application is ready to serve requests.

        Returns:
            True if ready, False otherwise
        """
        if not self.checks:
            return False

        required_checks = ["database", "api", "configuration"]
        for check_name in required_checks:
            if check_name not in self.checks:
                return False
            check = self.checks[check_name]
            if check.status == HealthStatus.UNHEALTHY:
                return False

        return True

    def is_alive(self) -> bool:
        """Check if application process is alive.

        Returns:
            Always True if this method is called
        """
        return True

    def record_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
    ) -> None:
        """Record an API request."""
        self.metrics.total_requests += 1
        if 200 <= status_code < 300:
            self.metrics.successful_requests += 1
        else:
            self.metrics.failed_requests += 1

        request = {
            "timestamp": datetime.now(timezone.utc),
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": duration_ms,
        }
        self.request_history.append(request)

        if len(self.request_history) > 1000:
            self.request_history.pop(0)

    def record_error(
        self,
        error_type: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Record an error."""
        error = {
            "timestamp": datetime.now(timezone.utc),
            "error_type": error_type,
            "message": message,
            "details": details or {},
        }
        self.error_history.append(error)

        if len(self.error_history) > 100:
            self.error_history.pop(0)

    def update_metrics(self) -> None:
        """Update calculated metrics."""
        self.metrics.timestamp = datetime.now(timezone.utc)
        self.metrics.uptime_seconds = int((self.metrics.timestamp - self.startup_time).total_seconds())

        if self.metrics.total_requests > 0:
            self.metrics.error_rate = self.metrics.failed_requests / self.metrics.total_requests

            if self.request_history:
                avg_duration = sum(r["duration_ms"] for r in self.request_history) / len(self.request_history)
                self.metrics.avg_response_time_ms = avg_duration

    def get_metrics(self) -> MetricsSnapshot:
        """Get current metrics snapshot."""
        self.update_metrics()
        return self.metrics

    def get_data_quality_metrics(self) -> DataQualityMetrics:
        """Get data quality metrics."""
        return self.data_quality

    def to_dict(self) -> dict[str, Any]:
        """Convert monitor state to dictionary."""
        self.update_metrics()
        return {
            "status": self.get_overall_status(),
            "ready": self.is_ready(),
            "alive": self.is_alive(),
            "checks": {
                name: {
                    "status": check.status,
                    "message": check.message,
                    "duration_ms": check.duration_ms,
                    "details": check.details,
                    "last_checked": check.last_checked.isoformat(),
                }
                for name, check in self.checks.items()
            },
            "metrics": {
                "timestamp": self.metrics.timestamp.isoformat(),
                "total_requests": self.metrics.total_requests,
                "successful_requests": self.metrics.successful_requests,
                "failed_requests": self.metrics.failed_requests,
                "error_rate": round(self.metrics.error_rate, 4),
                "avg_response_time_ms": round(self.metrics.avg_response_time_ms, 2),
                "uptime_seconds": self.metrics.uptime_seconds,
            },
            "data_quality": {
                "total_companies_scored": self.data_quality.total_companies_scored,
                "companies_with_all_signals": self.data_quality.companies_with_all_signals,
                "companies_missing_critical_signals": self.data_quality.companies_missing_critical_signals,
                "average_signal_count_per_company": round(self.data_quality.average_signal_count_per_company, 2),
                "average_confidence_score": round(self.data_quality.average_confidence_score, 3),
            },
        }


health_monitor = HealthMonitor()
