"""SQL Query Logging Middleware for EPIC-025 Story 1.

Logs all SQL queries with timing information for performance analysis.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

from loguru import logger
from sqlalchemy import event
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.sql import ClauseElement


class QueryLogger:
    """Logs SQL queries with timing information."""

    def __init__(self, slow_query_threshold_ms: float = 100.0):
        self.slow_query_threshold_ms = slow_query_threshold_ms
        self.query_stats: dict[str, dict[str, Any]] = {}

    def attach_to_engine(self, engine: Engine) -> None:
        """Attach event listeners to engine.

        For AsyncEngine, attaches to the underlying sync engine
        since DBAPI cursor events are only fired on the sync side.
        """
        # AsyncEngine wraps a sync Engine; DBAPI events fire on the sync engine
        target = engine.sync_engine if hasattr(engine, "sync_engine") else engine
        event.listen(target, "before_cursor_execute", self._before_execute)
        event.listen(target, "after_cursor_execute", self._after_execute)

    def _before_execute(
        self,
        conn: Connection,
        cursor: Any,
        statement: ClauseElement,
        parameters: tuple | dict,
        context: Any,
        executemany: bool,
    ) -> None:
        """Called before query execution."""
        context._query_start_time = time.perf_counter()

    def _after_execute(
        self,
        conn: Connection,
        cursor: Any,
        statement: ClauseElement,
        parameters: tuple | dict,
        context: Any,
        executemany: bool,
    ) -> None:
        """Called after query execution."""
        end_time = time.perf_counter()
        duration_ms = (end_time - context._query_start_time) * 1000

        # Format query for logging
        query_str = str(statement)
        if len(query_str) > 200:
            query_str = query_str[:200] + "..."

        # Track slow queries
        if duration_ms > self.slow_query_threshold_ms:
            logger.warning(
                f"Slow query ({duration_ms:.2f}ms): {query_str}",
                duration_ms=duration_ms,
                query=query_str,
            )
        else:
            logger.debug(
                f"Query ({duration_ms:.2f}ms): {query_str}",
                duration_ms=duration_ms,
            )

        # Update stats
        query_type = query_str.split()[0] if query_str else "UNKNOWN"
        if query_type not in self.query_stats:
            self.query_stats[query_type] = {
                "count": 0,
                "total_time_ms": 0,
                "slow_count": 0,
            }

        self.query_stats[query_type]["count"] += 1
        self.query_stats[query_type]["total_time_ms"] += duration_ms
        if duration_ms > self.slow_query_threshold_ms:
            self.query_stats[query_type]["slow_count"] += 1

    def get_stats(self) -> dict[str, dict[str, Any]]:
        """Get query statistics."""
        return self.query_stats.copy()

    def reset_stats(self) -> None:
        """Reset query statistics."""
        self.query_stats.clear()


# Global query logger instance
_query_logger: QueryLogger | None = None


def enable_query_logging(engine: Engine, slow_query_threshold_ms: float = 100.0) -> None:
    """Enable SQL query logging on engine."""
    global _query_logger
    _query_logger = QueryLogger(slow_query_threshold_ms)
    _query_logger.attach_to_engine(engine)
    logger.info(f"SQL query logging enabled (threshold: {slow_query_threshold_ms}ms)")


def get_query_logger() -> QueryLogger | None:
    """Get the global query logger instance."""
    return _query_logger


__all__ = ["QueryLogger", "enable_query_logging", "get_query_logger"]
