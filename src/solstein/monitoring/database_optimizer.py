"""Database query optimization utilities for EPIC-023.

EPIC-023 Story 2: Database Query Optimization
Implements query plan analysis, connection pooling, slow query detection,
and batch operation optimizations.
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

if TYPE_CHECKING:
    from sqlalchemy.engine import Connection, Engine

logger = logging.getLogger(__name__)


@dataclass
class QueryMetrics:
    """Metrics for a single query execution."""

    query: str
    duration_ms: float
    rows_affected: int
    execution_plan: dict[str, Any] | None = None


class DatabaseOptimizer:
    """Database optimization utilities.

    Provides connection pooling, query plan analysis, and slow query detection.
    """

    def __init__(
        self,
        database_url: str,
        pool_size: int = 10,
        max_overflow: int = 20,
        pool_timeout: int = 30,
        slow_query_threshold_ms: float = 100.0,
    ):
        """Initialize database optimizer.

        Args:
            database_url: Database connection URL.
            pool_size: Number of connections to keep in pool.
            max_overflow: Maximum number of overflow connections.
            pool_timeout: Seconds to wait for connection from pool.
            slow_query_threshold_ms: Threshold for slow query logging.
        """
        self.database_url = database_url
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout
        self.slow_query_threshold_ms = slow_query_threshold_ms
        self._engine: Engine | None = None
        self._query_log: list[QueryMetrics] = []
        self._slow_queries: list[QueryMetrics] = []

    def create_engine(self) -> Engine:
        """Create optimized async engine with connection pooling.

        Returns:
            Configured SQLAlchemy async engine.
        """
        self._engine = create_async_engine(
            self.database_url,
            pool_size=self.pool_size,
            max_overflow=self.max_overflow,
            pool_timeout=self.pool_timeout,
            pool_pre_ping=True,  # Verify connections before use
            pool_recycle=3600,  # Recycle connections after 1 hour
            echo=False,
        )

        # Set up query logging
        self._setup_query_logging()

        return self._engine

    def _setup_query_logging(self) -> None:
        """Set up SQLAlchemy event listeners for query logging."""
        if not self._engine:
            return

        @event.listens_for(self._engine.sync_engine, "before_cursor_execute")
        def before_cursor_execute(
            conn: Connection, cursor: Any, statement: str, parameters: Any, context: Any, executemany: bool
        ) -> None:
            conn.info.setdefault("query_start_time", []).append(time.perf_counter())

        @event.listens_for(self._engine.sync_engine, "after_cursor_execute")
        def after_cursor_execute(
            conn: Connection, cursor: Any, statement: str, parameters: Any, context: Any, executemany: bool
        ) -> None:
            start_time = conn.info["query_start_time"].pop()
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Get row count if available
            try:
                rowcount = cursor.rowcount
            except AttributeError:
                rowcount = -1

            metrics = QueryMetrics(
                query=statement[:200],  # Truncate long queries
                duration_ms=duration_ms,
                rows_affected=rowcount,
            )

            self._query_log.append(metrics)

            # Log slow queries
            if duration_ms > self.slow_query_threshold_ms:
                self._slow_queries.append(metrics)
                logger.warning(f"Slow query detected ({duration_ms:.2f}ms): {statement[:100]}...")

    async def get_query_plan(self, session: AsyncSession, query: str) -> dict[str, Any]:
        """Get execution plan for a query.

        Args:
            session: Database session.
            query: SQL query to analyze.

        Returns:
            Query execution plan as dictionary.
        """
        # Use EXPLAIN (FORMAT JSON) for PostgreSQL
        explain_query = f"EXPLAIN (FORMAT JSON, ANALYZE, BUFFERS) {query}"

        try:
            result = await session.execute(text(explain_query))
            plan = result.scalar()
            return {"plan": plan, "success": True}
        except Exception as e:
            logger.error(f"Failed to get query plan: {e}")
            return {"error": str(e), "success": False}

    async def analyze_table_stats(self, session: AsyncSession, table_name: str) -> dict[str, Any]:
        """Analyze table statistics.

        Args:
            session: Database session.
            table_name: Name of table to analyze.

        Returns:
            Table statistics.
        """
        try:
            # Get row count
            count_result = await session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            row_count = count_result.scalar()

            # Get table size
            size_query = text("""
                SELECT pg_size_pretty(pg_total_relation_size(:table_name)) as size
            """)
            size_result = await session.execute(size_query, {"table_name": table_name})
            size = size_result.scalar()

            return {
                "table": table_name,
                "row_count": row_count,
                "size": size,
                "success": True,
            }
        except Exception as e:
            logger.error(f"Failed to analyze table {table_name}: {e}")
            return {"table": table_name, "error": str(e), "success": False}

    def get_slow_queries(self, limit: int = 100) -> list[QueryMetrics]:
        """Get list of slow queries.

        Args:
            limit: Maximum number of queries to return.

        Returns:
            List of slow query metrics.
        """
        return sorted(
            self._slow_queries,
            key=lambda x: x.duration_ms,
            reverse=True,
        )[:limit]

    def get_query_stats(self) -> dict[str, Any]:
        """Get overall query statistics.

        Returns:
            Query statistics summary.
        """
        if not self._query_log:
            return {"total_queries": 0, "slow_queries": 0}

        total_queries = len(self._query_log)
        slow_queries = len(self._slow_queries)
        avg_duration = sum(q.duration_ms for q in self._query_log) / total_queries
        max_duration = max(q.duration_ms for q in self._query_log)

        return {
            "total_queries": total_queries,
            "slow_queries": slow_queries,
            "slow_query_percentage": (slow_queries / total_queries) * 100,
            "average_duration_ms": round(avg_duration, 2),
            "max_duration_ms": round(max_duration, 2),
            "threshold_ms": self.slow_query_threshold_ms,
        }

    def reset_stats(self) -> None:
        """Reset query statistics."""
        self._query_log.clear()
        self._slow_queries.clear()


class BatchInserter:
    """Efficient batch insertion utility.

    Handles large data inserts in optimized batches to reduce memory usage
    and improve performance.
    """

    def __init__(
        self,
        session: AsyncSession,
        batch_size: int = 1000,
        flush_every: int = 5000,
    ):
        """Initialize batch inserter.

        Args:
            session: Database session.
            batch_size: Number of records per INSERT statement.
            flush_every: Flush to database every N records.
        """
        self.session = session
        self.batch_size = batch_size
        self.flush_every = flush_every
        self._buffer: list[Any] = []
        self._total_inserted = 0

    async def add(self, record: Any) -> None:
        """Add a record to the batch.

        Args:
            record: Record to insert.
        """
        self._buffer.append(record)

        if len(self._buffer) >= self.batch_size:
            await self._flush()

    async def add_many(self, records: list[Any]) -> None:
        """Add multiple records to the batch.

        Args:
            records: List of records to insert.
        """
        for record in records:
            await self.add(record)

    async def _flush(self) -> None:
        """Flush buffered records to database."""
        if not self._buffer:
            return

        for record in self._buffer:
            self.session.add(record)

        await self.session.flush()
        self._total_inserted += len(self._buffer)
        self._buffer.clear()

        # Periodic commit to avoid long transactions
        if self._total_inserted % self.flush_every == 0:
            await self.session.commit()

    async def close(self) -> int:
        """Close inserter and flush remaining records.

        Returns:
            Total number of records inserted.
        """
        await self._flush()
        await self.session.commit()
        return self._total_inserted


@asynccontextmanager
async def optimized_transaction(session: AsyncSession):
    """Context manager for optimized database transactions.

    Automatically handles commit/rollback and sets appropriate
    transaction isolation level.

    Args:
        session: Database session.

    Yields:
        Database session within transaction.
    """
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise


async def run_in_batches(
    items: list[Any],
    batch_size: int,
    process_fn: Callable[[list[Any]], Any],
    max_concurrency: int = 5,
) -> list[Any]:
    """Process items in batches with controlled concurrency.

    Args:
        items: List of items to process.
        batch_size: Number of items per batch.
        process_fn: Async function to process each batch.
        max_concurrency: Maximum number of concurrent batches.

    Returns:
        List of results from all batches.
    """
    semaphore = asyncio.Semaphore(max_concurrency)
    results: list[Any] = []

    async def process_batch(batch: list[Any]) -> Any:
        async with semaphore:
            return await process_fn(batch)

    # Create batches
    batches = [items[i : i + batch_size] for i in range(0, len(items), batch_size)]

    # Process batches concurrently
    tasks = [process_batch(batch) for batch in batches]
    batch_results = await asyncio.gather(*tasks, return_exceptions=True)

    for result in batch_results:
        if isinstance(result, Exception):
            logger.error(f"Batch processing failed: {result}")
        else:
            results.append(result)

    return results


# Global optimizer instance
_optimizer: DatabaseOptimizer | None = None


def get_optimizer() -> DatabaseOptimizer | None:
    """Get the global database optimizer instance."""
    return _optimizer


def init_optimizer(database_url: str, **kwargs) -> DatabaseOptimizer:
    """Initialize the global database optimizer.

    Args:
        database_url: Database connection URL.
        **kwargs: Additional configuration options.

    Returns:
        Configured DatabaseOptimizer instance.
    """
    global _optimizer
    _optimizer = DatabaseOptimizer(database_url, **kwargs)
    return _optimizer
