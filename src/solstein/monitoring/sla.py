"""SLA monitoring and compliance tracking.

EPIC-026 Story 5: Monitors SLA compliance including:
- Availability (99.9% uptime target)
- Latency (95% of requests < 200ms)
- Error rate (< 0.1% 5xx errors)
- Monthly SLA reports

Usage:
    from solstein.monitoring.sla import SLAMonitor, SLAReport

    monitor = SLAMonitor()
    report = await monitor.generate_report(start, end)
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class SLAMetric:
    """Single SLA metric result."""

    name: str
    target: float
    actual: float
    compliant: bool
    unit: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "target": self.target,
            "actual": round(self.actual, 4),
            "compliant": self.compliant,
            "unit": self.unit,
        }


@dataclass
class SLAReport:
    """Complete SLA compliance report."""

    period_start: datetime
    period_end: datetime
    availability: SLAMetric
    latency: SLAMetric
    error_rate: SLAMetric
    generated_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def overall_compliant(self) -> bool:
        """Check if all SLAs are met."""
        return all(
            [
                self.availability.compliant,
                self.latency.compliant,
                self.error_rate.compliant,
            ]
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "period": {
                "start": self.period_start.isoformat(),
                "end": self.period_end.isoformat(),
            },
            "generated_at": self.generated_at.isoformat(),
            "overall_compliant": self.overall_compliant,
            "metrics": {
                "availability": self.availability.to_dict(),
                "latency": self.latency.to_dict(),
                "error_rate": self.error_rate.to_dict(),
            },
        }


class SLAMonitor:
    """Monitor SLA compliance."""

    # SLA Targets
    AVAILABILITY_TARGET = 0.999  # 99.9%
    LATENCY_TARGET_MS = 200  # 95% under 200ms
    ERROR_RATE_TARGET = 0.001  # 0.1%

    def __init__(self, metrics_store: Any | None = None):
        """Initialize SLA monitor.

        Args:
            metrics_store: Prometheus metrics store or similar.
        """
        self.metrics_store = metrics_store

    async def calculate_availability(self, start: datetime, end: datetime) -> float:
        """Calculate availability for the period.

        Args:
            start: Period start.
            end: Period end.

        Returns:
            Availability as fraction (0.0-1.0).
        """
        # In production, this would query Prometheus/Grafana
        # For now, return placeholder based on health checks
        duration = (end - start).total_seconds()

        # Simulate 99.95% availability
        downtime_seconds = duration * 0.0005
        return 1.0 - (downtime_seconds / duration)

    async def calculate_latency_p95(self, start: datetime, end: datetime) -> float:
        """Calculate P95 latency for the period.

        Args:
            start: Period start.
            end: Period end.

        Returns:
            P95 latency in milliseconds.
        """
        # In production, query Prometheus
        # histogram_quantile(0.95, http_request_duration_seconds_bucket)
        return 150.0  # Placeholder

    async def calculate_error_rate(self, start: datetime, end: datetime) -> float:
        """Calculate error rate for the period.

        Args:
            start: Period start.
            end: Period end.

        Returns:
            Error rate as fraction (0.0-1.0).
        """
        # In production, query Prometheus
        # rate(http_requests_total{status=~"5.."}[5m])
        return 0.0005  # Placeholder 0.05%

    async def generate_report(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> SLAReport:
        """Generate SLA compliance report.

        Args:
            start: Report period start (defaults to 30 days ago).
            end: Report period end (defaults to now).

        Returns:
            SLAReport with compliance status.
        """
        if end is None:
            end = datetime.utcnow()
        if start is None:
            start = end - timedelta(days=30)

        # Calculate metrics
        availability = await self.calculate_availability(start, end)
        latency_p95 = await self.calculate_latency_p95(start, end)
        error_rate = await self.calculate_error_rate(start, end)

        return SLAReport(
            period_start=start,
            period_end=end,
            availability=SLAMetric(
                name="Availability",
                target=self.AVAILABILITY_TARGET,
                actual=availability,
                compliant=availability >= self.AVAILABILITY_TARGET,
                unit="percentage",
            ),
            latency=SLAMetric(
                name="Latency P95",
                target=self.LATENCY_TARGET_MS,
                actual=latency_p95,
                compliant=latency_p95 <= self.LATENCY_TARGET_MS,
                unit="milliseconds",
            ),
            error_rate=SLAMetric(
                name="Error Rate",
                target=self.ERROR_RATE_TARGET,
                actual=error_rate,
                compliant=error_rate <= self.ERROR_RATE_TARGET,
                unit="percentage",
            ),
        )

    def generate_monthly_report(self, year: int, month: int) -> SLAReport:
        """Generate report for specific month.

        Args:
            year: Year number.
            month: Month number (1-12).

        Returns:
            SLAReport for the month.
        """
        import calendar

        # Calculate month boundaries
        _, last_day = calendar.monthrange(year, month)
        start = datetime(year, month, 1)
        end = datetime(year, month, last_day, 23, 59, 59)

        # Use async method
        import asyncio

        return asyncio.run(self.generate_report(start, end))


class SLAAlertManager:
    """Manage SLA-based alerts."""

    def __init__(self, sla_monitor: SLAMonitor):
        """Initialize SLA alert manager.

        Args:
            sla_monitor: SLA monitor instance.
        """
        self.sla_monitor = sla_monitor

    async def check_sla_breach(self) -> list[dict[str, Any]]:
        """Check for SLA breaches in current period.

        Returns:
            List of SLA breach alerts.
        """
        # Check last 24 hours
        end = datetime.utcnow()
        start = end - timedelta(hours=24)

        report = await self.sla_monitor.generate_report(start, end)
        alerts = []

        if not report.availability.compliant:
            alerts.append(
                {
                    "type": "sla_breach",
                    "metric": "availability",
                    "severity": "critical",
                    "message": f"Availability SLA breach: {report.availability.actual:.3f} "
                    f"(target: {report.availability.target:.3f})",
                    "actual": report.availability.actual,
                    "target": report.availability.target,
                }
            )

        if not report.latency.compliant:
            alerts.append(
                {
                    "type": "sla_breach",
                    "metric": "latency",
                    "severity": "warning",
                    "message": f"Latency SLA breach: {report.latency.actual:.1f}ms "
                    f"(target: {report.latency.target:.1f}ms)",
                    "actual": report.latency.actual,
                    "target": report.latency.target,
                }
            )

        if not report.error_rate.compliant:
            alerts.append(
                {
                    "type": "sla_breach",
                    "metric": "error_rate",
                    "severity": "warning",
                    "message": f"Error rate SLA breach: {report.error_rate.actual:.4f} "
                    f"(target: {report.error_rate.target:.4f})",
                    "actual": report.error_rate.actual,
                    "target": report.error_rate.target,
                }
            )

        return alerts


# SLA Definitions for reference
SLA_DEFINITIONS = {
    "availability": {
        "target": "99.9%",
        "measurement": "up{job='solstein-api'}",
        "calculation": "(total_time - downtime) / total_time",
        "allowed_downtime_monthly": "43.8 minutes",
    },
    "latency": {
        "target": "95% of requests < 200ms",
        "measurement": "http_request_duration_seconds",
        "calculation": "histogram_quantile(0.95, ...)",
    },
    "error_rate": {
        "target": "< 0.1%",
        "measurement": "rate(http_requests_total{status=~'5..'}[5m])",
        "calculation": "5xx_requests / total_requests",
    },
}
