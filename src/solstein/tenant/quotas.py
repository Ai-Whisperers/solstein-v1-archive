"""Resource quotas and limiting for tenants.

EPIC-030 Story 4: Enforce tenant resource limits.

Usage:
    from solstein.tenant.quotas import QuotaManager

    quota = QuotaManager()
    await quota.check_api_call_quota(tenant_id)
    await quota.increment_api_calls(tenant_id)
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

from loguru import logger

from solstein.infrastructure.cache import get_cache


@dataclass
class QuotaStatus:
    """Quota status for a tenant."""

    resource: str
    used: int
    limit: int
    remaining: int
    reset_at: datetime
    exceeded: bool


class QuotaManager:
    """Manage tenant resource quotas."""

    def __init__(self):
        """Initialize quota manager."""
        self.cache = get_cache()

    async def check_api_call_quota(self, tenant_id: str, limit: int = 10000) -> QuotaStatus:
        """Check API call quota for tenant.

        Args:
            tenant_id: Tenant identifier.
            limit: Daily API call limit.

        Returns:
            Quota status.
        """
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        key = f"quota:{tenant_id}:api_calls:{today}"

        used = await self.cache.get(key) or 0
        remaining = max(0, limit - used)

        # Reset at midnight UTC
        tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
        reset_at = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)

        return QuotaStatus(
            resource="api_calls", used=used, limit=limit, remaining=remaining, reset_at=reset_at, exceeded=used >= limit
        )

    async def increment_api_calls(self, tenant_id: str, count: int = 1) -> int:
        """Increment API call counter.

        Args:
            tenant_id: Tenant identifier.
            count: Number of calls to add.

        Returns:
            New total count.
        """
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        key = f"quota:{tenant_id}:api_calls:{today}"

        new_count = await self.cache.incr(key, count)

        # Set expiry to end of day
        ttl = int((datetime.now(timezone.utc).replace(hour=23, minute=59, second=59) - datetime.now(timezone.utc)).total_seconds())
        await self.cache.expire(key, ttl)

        return new_count

    async def check_report_quota(self, tenant_id: str, limit: int = 100) -> QuotaStatus:
        """Check report generation quota.

        Args:
            tenant_id: Tenant identifier.
            limit: Monthly report limit.

        Returns:
            Quota status.
        """
        month = datetime.now(timezone.utc).strftime("%Y-%m")
        key = f"quota:{tenant_id}:reports:{month}"

        used = await self.cache.get(key) or 0
        remaining = max(0, limit - used)

        # Reset at end of month
        next_month = (datetime.now(timezone.utc).replace(day=1) + timedelta(days=32)).replace(day=1)
        reset_at = next_month.replace(hour=0, minute=0, second=0, microsecond=0)

        return QuotaStatus(
            resource="reports", used=used, limit=limit, remaining=remaining, reset_at=reset_at, exceeded=used >= limit
        )

    async def increment_reports(self, tenant_id: str) -> int:
        """Increment report counter.

        Args:
            tenant_id: Tenant identifier.

        Returns:
            New total count.
        """
        month = datetime.now(timezone.utc).strftime("%Y-%m")
        key = f"quota:{tenant_id}:reports:{month}"

        new_count = await self.cache.incr(key, 1)

        # Set expiry to end of month
        next_month = (datetime.now(timezone.utc).replace(day=1) + timedelta(days=32)).replace(day=1)
        ttl = int((next_month - datetime.now(timezone.utc)).total_seconds())
        await self.cache.expire(key, ttl)

        return new_count

    async def get_all_quotas(self, tenant_id: str, config: dict) -> list[QuotaStatus]:
        """Get all quota statuses for tenant.

        Args:
            tenant_id: Tenant identifier.
            config: Tenant configuration with limits.

        Returns:
            List of quota statuses.
        """
        limits = config.get("limits", {})

        quotas = []

        # API calls
        api_quota = await self.check_api_call_quota(tenant_id, limits.get("max_api_calls_per_day", 10000))
        quotas.append(api_quota)

        # Reports
        report_quota = await self.check_report_quota(tenant_id, limits.get("max_reports_per_month", 100))
        quotas.append(report_quota)

        return quotas

    async def enforce_quota(self, tenant_id: str, resource: str, config: dict) -> bool:
        """Enforce quota, raising if exceeded.

        Args:
            tenant_id: Tenant identifier.
            resource: Resource type (api_calls, reports).
            config: Tenant configuration.

        Returns:
            True if quota available.

        Raises:
            QuotaExceeded: If quota exceeded.
        """
        limits = config.get("limits", {})

        if resource == "api_calls":
            quota = await self.check_api_call_quota(tenant_id, limits.get("max_api_calls_per_day", 10000))
        elif resource == "reports":
            quota = await self.check_report_quota(tenant_id, limits.get("max_reports_per_month", 100))
        else:
            return True

        if quota.exceeded:
            logger.warning(f"Quota exceeded for tenant {tenant_id[:8]}...: {resource}")
            raise QuotaExceeded(f"{resource} quota exceeded. Resets at {quota.reset_at}")

        return True


class QuotaExceeded(Exception):
    """Raised when tenant quota is exceeded."""

    pass


class RateLimiter:
    """Rate limiting for tenant operations."""

    def __init__(self):
        """Initialize rate limiter."""
        self.cache = get_cache()

    async def is_allowed(self, key: str, max_requests: int = 100, window_seconds: int = 60) -> bool:
        """Check if request is allowed under rate limit.

        Args:
            key: Rate limit key.
            max_requests: Maximum requests in window.
            window_seconds: Time window in seconds.

        Returns:
            True if request allowed.
        """
        current = await self.cache.get(key) or 0
        return current < max_requests

    async def record_request(self, key: str, window_seconds: int = 60) -> int:
        """Record a request for rate limiting.

        Args:
            key: Rate limit key.
            window_seconds: Time window.

        Returns:
            Current request count.
        """
        count = await self.cache.incr(key, 1)
        await self.cache.expire(key, window_seconds)
        return count

    async def get_remaining(self, key: str, max_requests: int = 100) -> int:
        """Get remaining requests in window.

        Args:
            key: Rate limit key.
            max_requests: Maximum requests.

        Returns:
            Remaining requests.
        """
        current = await self.cache.get(key) or 0
        return max(0, max_requests - current)
