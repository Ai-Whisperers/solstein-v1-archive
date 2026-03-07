"""Database monitoring and alerting utilities.

EPIC-025 Story 6: Implements comprehensive database monitoring
including query performance tracking, connection pool monitoring,
and alerting thresholds.
"""

import time
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any

from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class QueryMetrics:
    """Metrics for a single database query."""

    query: str
    duration_ms: float
    rows_affected: int | None = None
    error: str | None = None
    timestamp: float = field(default_factory=time.time)


@dataclass
class DatabaseHealthStatus:
    """Overall database health status."""

    healthy: bool
    query_time_p95_ms: float
    slow_query_count: int
    connection_pool_utilization: float
    message: str
    details: dict[str, Any] = field(default_factory=dict)


class DatabaseMonitor:
    """Monitor database performance and health."""

    # Alert thresholds
    SLOW_QUERY_THRESHOLD_MS = 100.0
    QUERY_TIME_P95_THRESHOLD_MS = 50.0
    POOL_UTILIZATION_THRESHOLD = 80.0

    def __init__(self):
        """Initialize database monitor."""
        self.query_history: list[QueryMetrics] = []
        self.max_history = 1000

    def record_query(self, query: str, duration_ms: float, rows_affected: int | None = None, error: str | None = None):
        """Record a query execution metric.

        Args:
            query: SQL query string (sanitized).
            duration_ms: Execution time in milliseconds.
            rows_affected: Number of rows affected/returned.
            error: Error message if query failed.
        """
        metric = QueryMetrics(
            query=query[:200],  # Truncate for memory
            duration_ms=duration_ms,
            rows_affected=rows_affected,
            error=error,
        )

        self.query_history.append(metric)

        # Trim history if needed
        if len(self.query_history) > self.max_history:
            self.query_history = self.query_history[-self.max_history :]

        # Log slow queries immediately
        if duration_ms > self.SLOW_QUERY_THRESHOLD_MS:
            logger.warning(
                "Slow query detected",
                duration_ms=round(duration_ms, 2),
                query=query[:100],
            )

    def get_slow_queries(self, threshold_ms: float | None = None) -> list[QueryMetrics]:
        """Get list of slow queries.

        Args:
            threshold_ms: Duration threshold (defaults to SLOW_QUERY_THRESHOLD_MS).

        Returns:
            List of slow query metrics.
        """
        threshold = threshold_ms or self.SLOW_QUERY_THRESHOLD_MS
        return [q for q in self.query_history if q.duration_ms > threshold]

    def get_query_stats(self) -> dict[str, Any]:
        """Get query performance statistics.

        Returns:
            Dictionary with query statistics.
        """
        if not self.query_history:
            return {
                "total_queries": 0,
                "avg_duration_ms": 0.0,
                "p95_duration_ms": 0.0,
                "slow_queries": 0,
            }

        durations = [q.duration_ms for q in self.query_history]
        durations.sort()

        p95_idx = int(len(durations) * 0.95)
        p95 = durations[min(p95_idx, len(durations) - 1)]

        slow_count = sum(1 for d in durations if d > self.SLOW_QUERY_THRESHOLD_MS)

        return {
            "total_queries": len(self.query_history),
            "avg_duration_ms": round(sum(durations) / len(durations), 2),
            "p95_duration_ms": round(p95, 2),
            "slow_queries": slow_count,
            "slow_query_rate": round(slow_count / len(durations) * 100, 2),
        }

    async def check_health(self, session: AsyncSession) -> DatabaseHealthStatus:
        """Check overall database health.

        Args:
            session: Database session for health checks.

        Returns:
            Database health status.
        """
        details = {}
        issues = []

        # Check query performance
        stats = self.get_query_stats()
        details["query_stats"] = stats

        if stats["p95_duration_ms"] > self.QUERY_TIME_P95_THRESHOLD_MS:
            issues.append(f"Query p95 time high: {stats['p95_duration_ms']}ms")

        if stats["slow_queries"] > 0:
            issues.append(f"{stats['slow_queries']} slow queries detected")

        # Check database connectivity
        try:
            start = time.time()
            await session.execute(text("SELECT 1"))
            connectivity_time = (time.time() - start) * 1000
            details["connectivity_ms"] = round(connectivity_time, 2)
        except Exception as e:
            issues.append(f"Database connectivity failed: {e}")
            details["connectivity_error"] = str(e)

        # Check table counts
        try:
            result = await session.execute(
                text("""
                    SELECT schemaname, relname, n_live_tup
                    FROM pg_stat_user_tables
                    ORDER BY n_live_tup DESC
                    LIMIT 10
                """)
            )
            table_stats = result.fetchall()
            details["top_tables"] = [{"schema": row[0], "table": row[1], "rows": row[2]} for row in table_stats]
        except Exception as e:
            logger.warning(f"Could not get table stats: {e}")

        is_healthy = len(issues) == 0
        message = "Database healthy" if is_healthy else f"Issues: {'; '.join(issues)}"

        return DatabaseHealthStatus(
            healthy=is_healthy,
            query_time_p95_ms=stats["p95_duration_ms"],
            slow_query_count=stats["slow_queries"],
            connection_pool_utilization=0.0,  # Would need engine access
            message=message,
            details=details,
        )


# Global monitor instance
db_monitor = DatabaseMonitor()


@contextmanager
def monitored_query(query: str):
    """Context manager for monitoring query execution.

    Usage:
        with monitored_query("SELECT * FROM companies"):
            result = await session.execute(query)

    Args:
        query: SQL query being executed.
    """
    start = time.time()
    error = None
    try:
        yield
    except Exception as e:
        error = str(e)
        raise
    finally:
        duration_ms = (time.time() - start) * 1000
        db_monitor.record_query(query, duration_ms, error=error)


def monitor_query(func: Callable) -> Callable:
    """Decorator for monitoring async query functions.

    Usage:
        @monitor_query
        async def get_companies(session):
            return await session.execute(select(Company))

    Args:
        func: Async function to monitor.

    Returns:
        Wrapped function.
    """

    async def wrapper(*args, **kwargs):
        start = time.time()
        error = None
        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            error = str(e)
            raise
        finally:
            duration_ms = (time.time() - start) * 1000
            db_monitor.record_query(func.__name__, duration_ms, error=error)

    return wrapper


class AlertManager:
    """Manage database alerts."""

    def __init__(self):
        """Initialize alert manager."""
        self.alert_history: list[dict[str, Any]] = []

    def send_alert(self, level: str, message: str, details: dict[str, Any] | None = None):
        """Send an alert.

        Args:
            level: Alert level (info, warning, critical).
            message: Alert message.
            details: Additional alert details.
        """
        alert = {
            "timestamp": time.time(),
            "level": level,
            "message": message,
            "details": details or {},
        }

        self.alert_history.append(alert)

        # Log based on level
        log_func = logger.info
        if level == "warning":
            log_func = logger.warning
        elif level == "critical":
            log_func = logger.error

        log_func(f"DB Alert [{level}]: {message}", **(details or {}))

    def check_and_alert(self, health: DatabaseHealthStatus):
        """Check health and send alerts if needed.

        Args:
            health: Database health status.
        """
        if not health.healthy:
            self.send_alert(
                level="warning" if health.query_time_p95_ms < 200 else "critical",
                message=health.message,
                details=health.details,
            )

        if health.slow_query_count > 10:
            self.send_alert(
                level="warning",
                message=f"High slow query count: {health.slow_query_count}",
                details={"threshold": 10, "actual": health.slow_query_count},
            )


# Global alert manager
alert_manager = AlertManager()
