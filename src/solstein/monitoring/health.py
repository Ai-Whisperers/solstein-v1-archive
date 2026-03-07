"""Health check endpoints and utilities.

EPIC-026 Story 3: Implements comprehensive health checks for:
- Database connectivity
- Redis cache
- LLM provider availability
- Disk space
- External dependencies

Usage:
    from solstein.monitoring.health import HealthChecker

    health = HealthChecker(db_engine, redis_client)
    status = await health.check_all()
"""

import shutil
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine


@dataclass
class HealthCheckResult:
    """Result of a single health check."""

    name: str
    status: str  # healthy, degraded, unhealthy
    response_time_ms: float
    message: str
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "status": self.status,
            "response_time_ms": round(self.response_time_ms, 2),
            "message": self.message,
            "details": self.details,
        }


@dataclass
class HealthStatus:
    """Overall health status."""

    status: str  # healthy, degraded, unhealthy
    timestamp: str
    checks: list[HealthCheckResult]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "status": self.status,
            "timestamp": self.timestamp,
            "checks": [c.to_dict() for c in self.checks],
        }


class HealthChecker:
    """Comprehensive health checker for Solstein services."""

    def __init__(
        self,
        db_engine: AsyncEngine | None = None,
        redis_client: Any | None = None,
        llm_health_checker: Any | None = None,
    ):
        """Initialize health checker.

        Args:
            db_engine: Database engine for connectivity check.
            redis_client: Redis client for cache check.
            llm_health_checker: LLM health checker instance.
        """
        self.db_engine = db_engine
        self.redis_client = redis_client
        self.llm_health_checker = llm_health_checker

    async def check_database(self) -> HealthCheckResult:
        """Check database connectivity and performance.

        Returns:
            HealthCheckResult for database.
        """
        import time

        if not self.db_engine:
            return HealthCheckResult(
                name="database",
                status="unhealthy",
                response_time_ms=0,
                message="Database engine not configured",
            )

        start = time.time()
        try:
            async with self.db_engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
                await conn.execute(text("SELECT version()"))

            elapsed = (time.time() - start) * 1000

            return HealthCheckResult(
                name="database",
                status="healthy" if elapsed < 100 else "degraded",
                response_time_ms=elapsed,
                message="Database connection OK",
                details={"response_time_ms": round(elapsed, 2)},
            )
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            logger.error(f"Database health check failed: {e}")
            return HealthCheckResult(
                name="database",
                status="unhealthy",
                response_time_ms=elapsed,
                message=f"Database connection failed: {str(e)}",
            )

    async def check_redis(self) -> HealthCheckResult:
        """Check Redis connectivity.

        Returns:
            HealthCheckResult for Redis.
        """
        import time

        if not self.redis_client:
            return HealthCheckResult(
                name="redis",
                status="unhealthy",
                response_time_ms=0,
                message="Redis client not configured",
            )

        start = time.time()
        try:
            await self.redis_client.ping()
            elapsed = (time.time() - start) * 1000

            return HealthCheckResult(
                name="redis",
                status="healthy",
                response_time_ms=elapsed,
                message="Redis connection OK",
                details={"response_time_ms": round(elapsed, 2)},
            )
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            logger.error(f"Redis health check failed: {e}")
            return HealthCheckResult(
                name="redis",
                status="unhealthy",
                response_time_ms=elapsed,
                message=f"Redis connection failed: {str(e)}",
            )

    async def check_llm_providers(self) -> HealthCheckResult:
        """Check LLM provider availability.

        Returns:
            HealthCheckResult for LLM providers.
        """
        import time

        if not self.llm_health_checker:
            return HealthCheckResult(
                name="llm_providers",
                status="degraded",
                response_time_ms=0,
                message="LLM health checker not configured",
            )

        start = time.time()
        try:
            # Get provider statuses
            health = await self.llm_health_checker.check_all_providers()
            elapsed = (time.time() - start) * 1000

            available = sum(1 for h in health.values() if h.get("healthy", False))
            total = len(health)

            if available == 0:
                status = "unhealthy"
                message = "No LLM providers available"
            elif available < total:
                status = "degraded"
                message = f"{available}/{total} providers available"
            else:
                status = "healthy"
                message = f"All {total} providers available"

            return HealthCheckResult(
                name="llm_providers",
                status=status,
                response_time_ms=elapsed,
                message=message,
                details={
                    "available": available,
                    "total": total,
                    "providers": health,
                },
            )
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            logger.error(f"LLM health check failed: {e}")
            return HealthCheckResult(
                name="llm_providers",
                status="unhealthy",
                response_time_ms=elapsed,
                message=f"LLM check failed: {str(e)}",
            )

    def check_disk_space(self) -> HealthCheckResult:
        """Check disk space availability.

        Returns:
            HealthCheckResult for disk space.
        """
        import time

        start = time.time()
        try:
            disk = shutil.disk_usage("/")
            elapsed = (time.time() - start) * 1000

            total_gb = disk.total / (1024**3)
            used_gb = disk.used / (1024**3)
            free_gb = disk.free / (1024**3)
            usage_pct = (disk.used / disk.total) * 100

            if usage_pct > 90:
                status = "unhealthy"
                message = f"Critical disk usage: {usage_pct:.1f}%"
            elif usage_pct > 80:
                status = "degraded"
                message = f"High disk usage: {usage_pct:.1f}%"
            else:
                status = "healthy"
                message = f"Disk usage OK: {usage_pct:.1f}%"

            return HealthCheckResult(
                name="disk_space",
                status=status,
                response_time_ms=elapsed,
                message=message,
                details={
                    "total_gb": round(total_gb, 2),
                    "used_gb": round(used_gb, 2),
                    "free_gb": round(free_gb, 2),
                    "usage_percent": round(usage_pct, 2),
                },
            )
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            return HealthCheckResult(
                name="disk_space",
                status="unhealthy",
                response_time_ms=elapsed,
                message=f"Disk check failed: {str(e)}",
            )

    async def check_celery(self) -> HealthCheckResult:
        """Check Celery worker status.

        Returns:
            HealthCheckResult for Celery.
        """
        import time

        start = time.time()
        try:
            from celery import Celery

            # This would check actual Celery workers
            # For now, return a placeholder
            elapsed = (time.time() - start) * 1000

            return HealthCheckResult(
                name="celery",
                status="healthy",
                response_time_ms=elapsed,
                message="Celery workers operational (placeholder)",
                details={"workers": 0, "active_tasks": 0},
            )
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            return HealthCheckResult(
                name="celery",
                status="degraded",
                response_time_ms=elapsed,
                message=f"Celery check incomplete: {str(e)}",
            )

    async def check_all(self) -> HealthStatus:
        """Run all health checks.

        Returns:
            HealthStatus with all check results.
        """
        checks = []

        # Run async checks
        if self.db_engine:
            checks.append(await self.check_database())

        if self.redis_client:
            checks.append(await self.check_redis())

        if self.llm_health_checker:
            checks.append(await self.check_llm_providers())

        # Run sync checks
        checks.append(self.check_disk_space())
        checks.append(await self.check_celery())

        # Determine overall status
        statuses = [c.status for c in checks]
        if "unhealthy" in statuses:
            overall = "unhealthy"
        elif "degraded" in statuses:
            overall = "degraded"
        else:
            overall = "healthy"

        return HealthStatus(
            status=overall,
            timestamp=datetime.utcnow().isoformat(),
            checks=checks,
        )


class ReadinessChecker:
    """Check if service is ready to accept traffic."""

    def __init__(self, health_checker: HealthChecker):
        """Initialize readiness checker.

        Args:
            health_checker: Health checker instance.
        """
        self.health_checker = health_checker

    async def check(self) -> dict[str, Any]:
        """Check if service is ready.

        Returns:
            Readiness status dictionary.
        """
        # Critical checks that must pass for readiness
        critical_checks = ["database", "redis"]

        health = await self.health_checker.check_all()

        critical_statuses = {c.name: c.status for c in health.checks if c.name in critical_checks}

        all_critical_healthy = all(s == "healthy" for s in critical_statuses.values())

        return {
            "ready": all_critical_healthy,
            "timestamp": health.timestamp,
            "critical_checks": critical_statuses,
            "overall_status": health.status,
        }


class LivenessChecker:
    """Check if service is alive."""

    def check(self) -> dict[str, Any]:
        """Check if service is alive.

        Returns:
            Liveness status dictionary.
        """
        return {
            "alive": True,
            "timestamp": datetime.utcnow().isoformat(),
            "pid": __import__("os").getpid(),
        }
