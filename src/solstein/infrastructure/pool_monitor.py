"""Database connection pool monitoring utilities.

EPIC-025 Story 4: Provides pool status monitoring and alerting
capabilities to track connection pool health.
"""

from dataclasses import dataclass
from typing import Any

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.pool import Pool


@dataclass
class PoolMetrics:
    """Metrics for database connection pool status."""

    pool_size: int
    checked_in: int
    checked_out: int
    overflow: int
    total_connections: int
    available_connections: int
    utilization_pct: float

    def to_dict(self) -> dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "pool_size": self.pool_size,
            "checked_in": self.checked_in,
            "checked_out": self.checked_out,
            "overflow": self.overflow,
            "total_connections": self.total_connections,
            "available_connections": self.available_connections,
            "utilization_pct": round(self.utilization_pct, 2),
        }


class PoolMonitor:
    """Monitor database connection pool health."""

    def __init__(self, engine: AsyncEngine):
        """Initialize pool monitor.

        Args:
            engine: SQLAlchemy async engine to monitor.
        """
        self.engine = engine

    def get_metrics(self) -> PoolMetrics | None:
        """Get current pool metrics.

        Returns:
            PoolMetrics if pool is available, None otherwise.
        """
        if not self.engine or not hasattr(self.engine, "pool"):
            return None

        pool: Pool = self.engine.pool

        # Get pool statistics
        pool_size = pool.size()
        checked_in = pool.checkedin()
        checked_out = pool.checkedout()
        overflow = getattr(pool, "overflow", lambda: 0)()

        total = checked_in + checked_out
        available = pool_size - checked_out
        utilization = (checked_out / pool_size * 100) if pool_size > 0 else 0

        return PoolMetrics(
            pool_size=pool_size,
            checked_in=checked_in,
            checked_out=checked_out,
            overflow=overflow,
            total_connections=total,
            available_connections=available,
            utilization_pct=utilization,
        )

    def is_healthy(self, warning_threshold: float = 80.0) -> tuple[bool, str]:
        """Check if pool health is acceptable.

        Args:
            warning_threshold: Percentage utilization that triggers warning.

        Returns:
            Tuple of (is_healthy, message).
        """
        metrics = self.get_metrics()
        if not metrics:
            return False, "Pool metrics unavailable"

        if metrics.utilization_pct >= warning_threshold:
            return (
                False,
                f"Pool utilization high: {metrics.utilization_pct:.1f}% "
                f"({metrics.checked_out}/{metrics.pool_size} connections)",
            )

        if metrics.available_connections < 5:
            return (
                False,
                f"Low available connections: {metrics.available_connections}",
            )

        return True, f"Pool healthy: {metrics.utilization_pct:.1f}% utilized"

    def get_status(self) -> dict[str, Any]:
        """Get comprehensive pool status for health checks.

        Returns:
            Dictionary with metrics and health status.
        """
        metrics = self.get_metrics()
        is_healthy, message = self.is_healthy()

        return {
            "healthy": is_healthy,
            "message": message,
            "metrics": metrics.to_dict() if metrics else None,
        }


async def check_pool_health(engine: AsyncEngine) -> dict[str, Any]:
    """Quick check of database pool health.

    Args:
        engine: SQLAlchemy async engine.

    Returns:
        Health status dictionary.
    """
    monitor = PoolMonitor(engine)
    return monitor.get_status()
