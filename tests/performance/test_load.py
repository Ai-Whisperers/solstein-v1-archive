"""
Performance and load tests for database operations.
"""

import os
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///file:testdb?mode=memory&cache=shared"
os.environ["SYNC_DATABASE_URL"] = "sqlite:///file:testdb?mode=memory&cache=shared"

import asyncio
import os
import sys
import time

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from solstein.config import Settings
from solstein.infrastructure.database import DatabaseManager
from solstein.infrastructure.database_models import CompanyRecord


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    """Provide database session."""
    settings = Settings.load()
    if not hasattr(settings, 'database'):
        from pydantic import BaseModel
        class DBConf(BaseModel):
            url: str = "sqlite+aiosqlite:///test_perf.sqlite3"
            pool_size: int = 5
            echo: bool = False
        settings.database = DBConf()
    else:
        if hasattr(settings.database, "model_copy"):
            settings.database = settings.database.model_copy(update={"url": "sqlite+aiosqlite:///test_perf.sqlite3"})
        else:
            settings.database.url = "sqlite+aiosqlite:///test_perf.sqlite3"
    db_manager = DatabaseManager(settings)
    from sqlalchemy.pool import StaticPool
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    db_manager.engine = create_async_engine("sqlite+aiosqlite:///:memory:", poolclass=StaticPool)
    db_manager.session_factory = async_sessionmaker(db_manager.engine)
    await db_manager.create_tables()
    async with db_manager.get_session() as session:
        yield session
    await db_manager.drop_tables()
    await db_manager.engine.dispose()


class TestDatabaseLoad:
    """Tests for database performance under load."""

    @pytest.mark.asyncio
    async def test_bulk_insert_companies(self, db_session: AsyncSession):
        """Test performance of bulk inserting company records."""
        num_records = 100
        start_time = time.time()

        companies = []
        for i in range(num_records):
            company = CompanyRecord(
                company_id=f"load-test-{i}", name=f"Load Test Company {i}"
            )
            companies.append(company)

        db_session.add_all(companies)
        await db_session.commit()

        duration = time.time() - start_time
        print(f"\nBulk insert {num_records} companies took {duration:.4f}s")
        assert duration < 5.0  # Should be fast



    @pytest.mark.asyncio
    async def test_query_performance_companies(self, db_session: AsyncSession):
        """Test performance of querying many company records."""
        # Ensure we have data
        result = await db_session.execute(text("SELECT COUNT(*) FROM companies"))
        count = result.scalar()
        if count < 100:
            companies = [CompanyRecord(company_id=f"perf-co-{i}", name=f"Company {i}") for i in range(100)]
            db_session.add_all(companies)
            await db_session.commit()

        start_time = time.time()
        for _ in range(50):
            await db_session.execute(text("SELECT * FROM companies LIMIT 10"))

        duration = time.time() - start_time
        print(f"\n50 queries for companies took {duration:.4f}s")
        assert duration < 2.0

    @pytest.mark.asyncio
    async def test_query_performance_with_joins(self, db_session: AsyncSession):
        """Test performance of complex queries with joins."""
        start_time = time.time()
        # Query companies with their latest facts (simplified)
        query = text("""
            SELECT c.name, f.fact_type, f.value 
            FROM companies c
            LEFT JOIN facts f ON c.company_id = f.company_id
            LIMIT 100
        """)
        for _ in range(20):
            await db_session.execute(query)

        duration = time.time() - start_time
        print(f"\n20 join queries took {duration:.4f}s")
        assert duration < 2.0

    @pytest.mark.asyncio
    async def test_concurrent_reads(self, db_session: AsyncSession):
        """Test performance of concurrent database reads."""
        settings = Settings.load()
        if hasattr(settings.database, "model_copy"):
            settings.database = settings.database.model_copy(update={"url": "sqlite+aiosqlite:///test_perf.sqlite3"})
        else:
            settings.database.url = "sqlite+aiosqlite:///test_perf.sqlite3"
        db_manager = DatabaseManager(settings)
        from sqlalchemy.pool import StaticPool
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    db_manager.engine = create_async_engine("sqlite+aiosqlite:///:memory:", poolclass=StaticPool)
    db_manager.session_factory = async_sessionmaker(db_manager.engine)

        async def run_query():
            async with db_manager.get_session() as session:
                await session.execute(text("SELECT 1"))

        start_time = time.time()
        tasks = [run_query() for _ in range(20)]
        await asyncio.gather(*tasks)

        duration = time.time() - start_time
        print(f"\n20 concurrent queries took {duration:.4f}s")
        assert duration < 2.0
        await db_manager.engine.dispose()


class TestStressTests:
    """More aggressive load and stress tests."""

    @pytest.mark.asyncio
    async def test_sustained_load(self, db_session: AsyncSession):
        """Test the system under sustained database load."""
        start_time = time.time()
        end_at = start_time + 5  # Run for 5 seconds

        count = 0
        while time.time() < end_at:
            await db_session.execute(text("SELECT 1"))
            count += 1

        duration = time.time() - start_time
        print(f"\nExecuted {count} queries in {duration:.2f}s ({count / duration:.1f} qps)")
        assert count > 10


class TestMemoryUsage:
    """Tests for memory efficiency during large operations."""

    @pytest.mark.asyncio
    async def test_large_result_set_handling(self, db_session: AsyncSession):
        """Test handling of large result sets without memory exhaustion."""
        # This is a basic check - in real use we'd monitor process memory
        start_time = time.time()

        # Query a lot of data but use scalars().all() vs chunking
        result = await db_session.execute(text("SELECT * FROM companies"))
        rows = result.fetchall()

        duration = time.time() - start_time
        print(f"\nFetching all {len(rows)} companies took {duration:.4f}s")
        assert duration < 5.0


class TestConnectionPool:
    """Tests for connection pool management."""

    @pytest.mark.asyncio
    async def test_connection_reuse(self):
        """Test that the connection pool works correctly."""
        settings = Settings.load()
        if hasattr(settings.database, "model_copy"):
            settings.database = settings.database.model_copy(update={"url": "sqlite+aiosqlite://"})
        else:
            settings.database.url = "sqlite+aiosqlite://"
        db_manager = DatabaseManager(settings)
        from sqlalchemy.pool import StaticPool
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    db_manager.engine = create_async_engine("sqlite+aiosqlite:///:memory:", poolclass=StaticPool)
    db_manager.session_factory = async_sessionmaker(db_manager.engine)

        # Create multiple sessions
        sessions = []
        for _ in range(5):
            session = await db_manager.get_session().__aenter__()
            sessions.append(session)

        # Use each session
        for session in sessions:
            await session.execute(text("SELECT 1"))

        # Close all sessions
        for session in sessions:
            await session.close()

        await db_manager.engine.dispose()
        assert True  # Reached here without error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
