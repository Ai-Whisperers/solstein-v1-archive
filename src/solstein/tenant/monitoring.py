"""Tenant usage monitoring and billing.

EPIC-030 Story 6: Track tenant metrics for billing and health.

Usage:
    from solstein.tenant.monitoring import TenantMonitor

    monitor = TenantMonitor()
    usage = await monitor.get_daily_usage(tenant_id)
    health = await monitor.get_health_status(tenant_id)
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

from solstein.infrastructure.cache import get_cache


@dataclass
class TenantMetrics:
    """Metrics for a tenant."""

    tenant_id: str
    timestamp: datetime
    api_requests: int = 0
    api_errors: int = 0
    avg_response_time_ms: float = 0.0
    active_users: int = 0
    companies_tracked: int = 0
    reports_generated: int = 0
    storage_gb: float = 0.0


@dataclass
class TenantHealth:
    """Health status for a tenant."""

    tenant_id: str
    status: str  # healthy, warning, critical
    api_error_rate: float
    avg_latency_ms: float
    quota_usage_pct: float
    last_activity: datetime | None = None
    alerts: list[str] = field(default_factory=list)


class TenantMonitor:
    """Monitor tenant usage and health."""

    def __init__(self):
        """Initialize tenant monitor."""
        self.cache = get_cache()

    async def record_api_request(self, tenant_id: str, endpoint: str, duration_ms: float, status_code: int) -> None:
        """Record an API request.

        Args:
            tenant_id: Tenant identifier.
            endpoint: API endpoint.
            duration_ms: Request duration.
            status_code: HTTP status code.
        """
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # Increment request counter
        key = f"metrics:{tenant_id}:api_requests:{today}"
        await self.cache.incr(key, 1)
        await self.cache.expire(key, 86400 * 30)

        # Track errors
        if status_code >= 400:
            error_key = f"metrics:{tenant_id}:api_errors:{today}"
            await self.cache.incr(error_key, 1)
            await self.cache.expire(error_key, 86400 * 30)

        # Track latency
        latency_key = f"metrics:{tenant_id}:latency:{today}"
        # Store in a list for aggregation
        await self.cache.append(latency_key, f"{duration_ms},")
        await self.cache.expire(latency_key, 86400 * 30)

    async def record_report_generated(self, tenant_id: str, format: str) -> None:
        """Record a report generation.

        Args:
            tenant_id: Tenant identifier.
            format: Report format.
        """
        month = datetime.now(timezone.utc).strftime("%Y-%m")
        key = f"metrics:{tenant_id}:reports:{month}"
        await self.cache.incr(key, 1)
        await self.cache.expire(key, 86400 * 60)  # 60 days

    async def get_daily_usage(self, tenant_id: str, date: str | None = None) -> dict[str, Any]:
        """Get daily usage for tenant.

        Args:
            tenant_id: Tenant identifier.
            date: Date string (YYYY-MM-DD), defaults to today.

        Returns:
            Usage dictionary.
        """
        if date is None:
            date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        api_requests = await self.cache.get(f"metrics:{tenant_id}:api_requests:{date}") or 0
        api_errors = await self.cache.get(f"metrics:{tenant_id}:api_errors:{date}") or 0

        return {
            "date": date,
            "api_requests": api_requests,
            "api_errors": api_errors,
            "error_rate": api_errors / max(api_requests, 1),
        }

    async def get_monthly_usage(self, tenant_id: str, month: str | None = None) -> dict[str, Any]:
        """Get monthly usage for tenant.

        Args:
            tenant_id: Tenant identifier.
            month: Month string (YYYY-MM), defaults to current month.

        Returns:
            Usage dictionary.
        """
        if month is None:
            month = datetime.now(timezone.utc).strftime("%Y-%m")

        reports = await self.cache.get(f"metrics:{tenant_id}:reports:{month}") or 0

        # Sum daily API calls for month
        api_calls = 0
        for day in range(1, 32):
            date = f"{month}-{day:02d}"
            calls = await self.cache.get(f"metrics:{tenant_id}:api_requests:{date}") or 0
            api_calls += calls

        return {
            "month": month,
            "api_calls": api_calls,
            "reports_generated": reports,
        }

    async def get_health_status(self, tenant_id: str) -> TenantHealth:
        """Get health status for tenant.

        Args:
            tenant_id: Tenant identifier.

        Returns:
            Health status.
        """
        # Get last 24 hours of metrics
        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        api_requests = 0
        api_errors = 0

        for date in [yesterday, today]:
            usage = await self.get_daily_usage(tenant_id, date)
            api_requests += usage["api_requests"]
            api_errors += usage["api_errors"]

        error_rate = api_errors / max(api_requests, 1)

        # Determine status
        alerts = []
        status = "healthy"

        if error_rate > 0.1:
            status = "critical"
            alerts.append(f"High error rate: {error_rate:.1%}")
        elif error_rate > 0.05:
            status = "warning"
            alerts.append(f"Elevated error rate: {error_rate:.1%}")

        return TenantHealth(
            tenant_id=tenant_id,
            status=status,
            api_error_rate=error_rate,
            avg_latency_ms=0.0,  # Would calculate from stored latencies
            quota_usage_pct=0.0,  # Would calculate from quotas
            last_activity=datetime.now(timezone.utc),
            alerts=alerts,
        )

    async def get_platform_analytics(self) -> dict[str, Any]:
        """Get platform-wide analytics (admin only).

        Returns:
            Aggregated analytics.
        """
        # In production: aggregate across all tenants
        # For now, return mock data

        return {
            "total_tenants": 0,
            "active_tenants_30d": 0,
            "total_api_calls_today": 0,
            "total_companies": 0,
            "health_summary": {
                "healthy": 0,
                "warning": 0,
                "critical": 0,
            },
        }


class UsageMeter:
    """Meter tenant usage for billing."""

    def __init__(self):
        """Initialize usage meter."""
        self.cache = get_cache()

    async def get_billing_usage(self, tenant_id: str, month: str) -> dict[str, Any]:
        """Get usage for billing period.

        Args:
            tenant_id: Tenant identifier.
            month: Billing month (YYYY-MM).

        Returns:
            Billing usage details.
        """
        monitor = TenantMonitor()
        monthly = await monitor.get_monthly_usage(tenant_id, month)

        # Get peak daily usage
        peak_api_calls = 0
        for day in range(1, 32):
            date = f"{month}-{day:02d}"
            daily = await monitor.get_daily_usage(tenant_id, date)
            peak_api_calls = max(peak_api_calls, daily["api_requests"])

        return {
            "tenant_id": tenant_id,
            "month": month,
            "api_calls": monthly["api_calls"],
            "reports_generated": monthly["reports_generated"],
            "peak_daily_api_calls": peak_api_calls,
            "storage_gb": 0.0,  # Would calculate from actual storage
        }
