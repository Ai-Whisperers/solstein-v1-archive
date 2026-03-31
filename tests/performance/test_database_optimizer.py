"""Tests for database query optimization (EPIC-023 Story 2).

Tests cover:
- Connection pooling configuration
- Query plan analysis
- Slow query detection
- Batch operations
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from solstein.monitoring.database_optimizer import (
    BatchInserter,
    DatabaseOptimizer,
    QueryMetrics,
    optimized_transaction,
    run_in_batches,
)


class TestQueryMetrics:
    """Test QueryMetrics dataclass."""

    def test_creation(self) -> None:
        """Test QueryMetrics creation."""
        metrics = QueryMetrics(
            query="SELECT * FROM companies",
            duration_ms=50.5,
            rows_affected=10,
        )

        assert metrics.query == "SELECT * FROM companies"
        assert metrics.duration_ms == 50.5
        assert metrics.rows_affected == 10
        assert metrics.execution_plan is None

    def test_with_execution_plan(self) -> None:
        """Test QueryMetrics with execution plan."""
        plan = {"Node Type": "Seq Scan", "Relation Name": "companies"}
        metrics = QueryMetrics(
            query="SELECT * FROM companies",
            duration_ms=100.0,
            rows_affected=100,
            execution_plan=plan,
        )

        assert metrics.execution_plan == plan


class TestDatabaseOptimizer:
    """Test DatabaseOptimizer functionality."""

    @pytest.fixture
    def optimizer(self) -> DatabaseOptimizer:
        """Create optimizer instance for testing."""
        return DatabaseOptimizer(
            database_url="postgresql+asyncpg://test:test@localhost/test",
            pool_size=5,
            max_overflow=10,
            slow_query_threshold_ms=50.0,
        )

    def test_initialization(self, optimizer: DatabaseOptimizer) -> None:
        """Test optimizer initialization."""
        assert optimizer.database_url == "postgresql+asyncpg://test:test@localhost/test"
        assert optimizer.pool_size == 5
        assert optimizer.max_overflow == 10
        assert optimizer.slow_query_threshold_ms == 50.0
        assert optimizer._engine is None
        assert optimizer._query_log == []
        assert optimizer._slow_queries == []

    @patch("solstein.monitoring.database_optimizer.create_async_engine")
    @patch("solstein.monitoring.database_optimizer.event.listens_for")
    def test_create_engine(self, mock_listens_for: Mock, mock_create_engine: Mock, optimizer: DatabaseOptimizer) -> None:
        """Test engine creation with pooling config."""
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        engine = optimizer.create_engine()

        assert engine == mock_engine
        mock_create_engine.assert_called_once()

        # Verify pooling configuration
        call_kwargs = mock_create_engine.call_args[1]
        assert call_kwargs["pool_size"] == 5
        assert call_kwargs["max_overflow"] == 10
        assert call_kwargs["pool_timeout"] == 30
        assert call_kwargs["pool_pre_ping"] is True
        assert call_kwargs["pool_recycle"] == 3600

    @pytest.mark.asyncio
    async def test_get_query_plan_success(self, optimizer: DatabaseOptimizer) -> None:
        """Test successful query plan retrieval."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalar.return_value = [{"Plan": {"Node Type": "Seq Scan"}}]
        mock_session.execute.return_value = mock_result

        plan = await optimizer.get_query_plan(mock_session, "SELECT * FROM companies")

        assert plan["success"] is True
        assert "plan" in plan
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_query_plan_failure(self, optimizer: DatabaseOptimizer) -> None:
        """Test query plan retrieval failure."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.execute.side_effect = Exception("Database error")

        plan = await optimizer.get_query_plan(mock_session, "SELECT * FROM companies")

        assert plan["success"] is False
        assert "error" in plan

    @pytest.mark.asyncio
    async def test_analyze_table_stats(self, optimizer: DatabaseOptimizer) -> None:
        """Test table statistics analysis."""
        mock_session = AsyncMock(spec=AsyncSession)

        # Mock count query
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 1000

        # Mock size query
        mock_size_result = MagicMock()
        mock_size_result.scalar.return_value = "10 MB"

        mock_session.execute.side_effect = [mock_count_result, mock_size_result]

        stats = await optimizer.analyze_table_stats(mock_session, "companies")

        assert stats["success"] is True
        assert stats["table"] == "companies"
        assert stats["row_count"] == 1000
        assert stats["size"] == "10 MB"

    def test_get_slow_queries(self, optimizer: DatabaseOptimizer) -> None:
        """Test retrieving slow queries."""
        # Add some query metrics
        optimizer._slow_queries = [
            QueryMetrics("SELECT * FROM slow1", 200.0, 10),
            QueryMetrics("SELECT * FROM slow2", 150.0, 5),
            QueryMetrics("SELECT * FROM slow3", 300.0, 20),
        ]

        slow_queries = optimizer.get_slow_queries(limit=2)

        assert len(slow_queries) == 2
        # Should be sorted by duration (descending)
        assert slow_queries[0].duration_ms == 300.0
        assert slow_queries[1].duration_ms == 200.0

    def test_get_query_stats(self, optimizer: DatabaseOptimizer) -> None:
        """Test query statistics."""
        # Add query metrics
        optimizer._query_log = [
            QueryMetrics("SELECT * FROM t1", 10.0, 1),
            QueryMetrics("SELECT * FROM t2", 20.0, 2),
            QueryMetrics("SELECT * FROM t3", 100.0, 3),  # Slow query
        ]
        optimizer._slow_queries = [
            QueryMetrics("SELECT * FROM t3", 100.0, 3),
        ]

        stats = optimizer.get_query_stats()

        assert stats["total_queries"] == 3
        assert stats["slow_queries"] == 1
        assert stats["slow_query_percentage"] == pytest.approx(33.33, abs=0.01)
        assert stats["average_duration_ms"] == pytest.approx(43.33, abs=0.01)
        assert stats["max_duration_ms"] == 100.0

    def test_get_query_stats_empty(self, optimizer: DatabaseOptimizer) -> None:
        """Test query stats with no queries."""
        stats = optimizer.get_query_stats()

        assert stats["total_queries"] == 0
        assert stats["slow_queries"] == 0

    def test_reset_stats(self, optimizer: DatabaseOptimizer) -> None:
        """Test resetting statistics."""
        optimizer._query_log = [QueryMetrics("SELECT 1", 10.0, 1)]
        optimizer._slow_queries = [QueryMetrics("SELECT 2", 100.0, 1)]

        optimizer.reset_stats()

        assert optimizer._query_log == []
        assert optimizer._slow_queries == []


class TestBatchInserter:
    """Test BatchInserter functionality."""

    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        """Create mock session for testing."""
        return AsyncMock(spec=AsyncSession)

    @pytest.mark.asyncio
    async def test_add_single_record(self, mock_session: AsyncMock) -> None:
        """Test adding a single record."""
        inserter = BatchInserter(mock_session, batch_size=3)
        mock_record = Mock()

        await inserter.add(mock_record)

        # Should not flush yet (batch_size=3, only 1 record)
        mock_session.add.assert_not_called()
        mock_session.flush.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_triggers_flush(self, mock_session: AsyncMock) -> None:
        """Test that adding records triggers flush at batch size."""
        inserter = BatchInserter(mock_session, batch_size=2)

        await inserter.add(Mock())
        await inserter.add(Mock())  # Should trigger flush

        mock_session.add.assert_called()
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_many(self, mock_session: AsyncMock) -> None:
        """Test adding multiple records."""
        inserter = BatchInserter(mock_session, batch_size=5)
        records = [Mock() for _ in range(10)]

        await inserter.add_many(records)

        # Should have flushed twice (10 records / batch_size 5)
        assert mock_session.flush.call_count == 2

    @pytest.mark.asyncio
    async def test_close_flushes_remaining(self, mock_session: AsyncMock) -> None:
        """Test that close flushes remaining records."""
        inserter = BatchInserter(mock_session, batch_size=10)

        await inserter.add(Mock())
        await inserter.add(Mock())

        count = await inserter.close()

        assert count == 2
        mock_session.flush.assert_called_once()
        mock_session.commit.assert_called_once()


class TestOptimizedTransaction:
    """Test optimized transaction context manager."""

    @pytest.mark.asyncio
    async def test_successful_transaction(self) -> None:
        """Test successful transaction commits."""
        mock_session = AsyncMock(spec=AsyncSession)

        async with optimized_transaction(mock_session) as session:
            # Simulate some work
            assert session == mock_session

        mock_session.commit.assert_called_once()
        mock_session.rollback.assert_not_called()

    @pytest.mark.asyncio
    async def test_failed_transaction_rolls_back(self) -> None:
        """Test failed transaction rolls back."""
        mock_session = AsyncMock(spec=AsyncSession)

        with pytest.raises(ValueError):
            async with optimized_transaction(mock_session):
                raise ValueError("Test error")

        mock_session.rollback.assert_called_once()
        mock_session.commit.assert_not_called()


class TestRunInBatches:
    """Test batch processing utility."""

    @pytest.mark.asyncio
    async def test_process_in_batches(self) -> None:
        """Test processing items in batches."""
        processed_batches: list[list[int]] = []

        async def process_fn(batch: list[int]) -> int:
            processed_batches.append(batch)
            return sum(batch)

        items = list(range(10))
        results = await run_in_batches(items, batch_size=3, process_fn=process_fn)

        # Should create 4 batches: [0,1,2], [3,4,5], [6,7,8], [9]
        assert len(processed_batches) == 4
        assert processed_batches[0] == [0, 1, 2]
        assert processed_batches[1] == [3, 4, 5]
        assert processed_batches[2] == [6, 7, 8]
        assert processed_batches[3] == [9]

        # Results should be sums
        assert sum(results) == sum(range(10))

    @pytest.mark.asyncio
    async def test_batch_with_errors(self) -> None:
        """Test batch processing with some failures."""

        async def process_fn(batch: list[int]) -> int:
            if sum(batch) > 10:
                raise ValueError("Batch too large")
            return sum(batch)

        items = list(range(10))
        results = await run_in_batches(items, batch_size=3, process_fn=process_fn)

        # Should have some successful results
        assert len(results) < 4  # Some batches failed

    @pytest.mark.asyncio
    async def test_concurrency_limit(self) -> None:
        """Test that concurrency limit is respected."""
        running = 0
        max_running = 0

        async def process_fn(batch: list[int]) -> int:
            nonlocal running, max_running
            running += 1
            max_running = max(max_running, running)
            await asyncio.sleep(0.01)  # Small delay
            running -= 1
            return sum(batch)

        items = list(range(20))
        await run_in_batches(items, batch_size=2, process_fn=process_fn, max_concurrency=3)

        # Max concurrent batches should not exceed limit
        assert max_running <= 3


class TestGlobalOptimizer:
    """Test global optimizer functions."""

    def test_get_optimizer_none(self) -> None:
        """Test get_optimizer returns None when not initialized."""
        from solstein.monitoring import database_optimizer

        # Reset global state
        database_optimizer._optimizer = None

        assert database_optimizer.get_optimizer() is None

    @patch("solstein.monitoring.database_optimizer.create_async_engine")
    def test_init_optimizer(self, mock_create_engine: Mock) -> None:
        """Test initializing global optimizer."""
        from solstein.monitoring import database_optimizer

        # Reset global state
        database_optimizer._optimizer = None

        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        optimizer = database_optimizer.init_optimizer(
            "postgresql+asyncpg://test:test@localhost/test",
            pool_size=10,
        )

        assert optimizer is not None
        assert database_optimizer.get_optimizer() == optimizer
        assert optimizer.pool_size == 10


class TestIntegration:
    """Integration tests for database optimization components."""

    @pytest.mark.asyncio
    async def test_end_to_end_batch_insert(self) -> None:
        """Test end-to-end batch insert workflow."""
        mock_session = AsyncMock(spec=AsyncSession)
        inserter = BatchInserter(mock_session, batch_size=5, flush_every=10)

        # Add 12 records
        for i in range(12):
            await inserter.add(Mock(id=i))

        # Should have flushed twice (at 5 and 10 records)
        assert mock_session.flush.call_count == 2

        # Close should flush remaining 2
        count = await inserter.close()
        assert count == 12
        assert mock_session.flush.call_count == 3
        mock_session.commit.assert_called()

    @pytest.mark.asyncio
    async def test_optimizer_with_slow_queries(self) -> None:
        """Test optimizer correctly identifies slow queries."""
        optimizer = DatabaseOptimizer(
            "postgresql+asyncpg://test:test@localhost/test",
            slow_query_threshold_ms=50.0,
        )

        # Simulate some queries
        optimizer._query_log = [
            QueryMetrics("SELECT * FROM fast", 10.0, 1),
            QueryMetrics("SELECT * FROM medium", 40.0, 1),
            QueryMetrics("SELECT * FROM slow", 100.0, 1),
            QueryMetrics("SELECT * FROM very_slow", 200.0, 1),
        ]
        optimizer._slow_queries = [
            QueryMetrics("SELECT * FROM slow", 100.0, 1),
            QueryMetrics("SELECT * FROM very_slow", 200.0, 1),
        ]

        stats = optimizer.get_query_stats()
        assert stats["slow_queries"] == 2
        assert stats["slow_query_percentage"] == 50.0

        slow = optimizer.get_slow_queries()
        assert len(slow) == 2
        assert slow[0].duration_ms == 200.0  # Sorted by duration
