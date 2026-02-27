"""
Load and performance testing for Solstein.

These tests verify system performance under load.
Uses pytest-benchmark if available, otherwise simple timing.
"""

import os
import sys
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

import pytest
import pytest_asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.solstein.infrastructure.database import DatabaseManager
from src.solstein.infrastructure.models import CompanyRecord, FactRecord, ResearchRunRecord
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    """Provide database session."""
    db_manager = DatabaseManager()
    session = await db_manager.get_session().__aenter__()
    transaction = await session.begin_nested()
    yield session
    await transaction.rollback()
    await session.close()
    await db_manager.engine.dispose()


class TestDatabaseLoad:
    """Test database performance under load."""
    
    @pytest.mark.asyncio
    async def test_bulk_insert_companies(self, db_session: AsyncSession):
        """Test bulk insertion performance."""
        num_records = 1000
        start_time = time.time()
        
        companies = []
        for i in range(num_records):
            company = CompanyRecord(
                id=f"load-test-{i}",
                ticker=f"LOAD{i:04d}",
                name=f"Load Test Company {i}",
                status="active"
            )
            companies.append(company)
        
        db_session.add_all(companies)
        await db_session.commit()
        
        duration = time.time() - start_time
        rate = num_records / duration
        
        print(f"\nBulk insert: {num_records} records in {duration:.2f}s ({rate:.0f} rec/s)")
        assert duration < 30, f"Bulk insert too slow: {duration:.2f}s"
        assert rate > 20, f"Insert rate too low: {rate:.0f} rec/s"
    
    @pytest.mark.asyncio
    async def test_bulk_insert_facts(self, db_session: AsyncSession):
        """Test bulk fact insertion performance."""
        # Create parent company
        company = CompanyRecord(
            id="fact-load-company",
            ticker="FLC",
            name="Fact Load Company",
            status="active"
        )
        db_session.add(company)
        await db_session.flush()
        
        num_records = 1000
        start_time = time.time()
        
        facts = []
        for i in range(num_records):
            fact = FactRecord(
                id=f"fact-load-{i}",
                company_id=company.id,
                fact_key=f"metric_{i % 100}",
                fact_value=str(i * 100),
                status="active"
            )
            facts.append(fact)
        
        db_session.add_all(facts)
        await db_session.commit()
        
        duration = time.time() - start_time
        rate = num_records / duration
        
        print(f"\nBulk fact insert: {num_records} records in {duration:.2f}s ({rate:.0f} rec/s)")
        assert rate > 50, f"Fact insert rate too low: {rate:.0f} rec/s"
    
    @pytest.mark.asyncio
    async def test_query_performance_companies(self, db_session: AsyncSession):
        """Test company query performance."""
        # Insert test data
        companies = [
            CompanyRecord(
                id=f"query-test-{i}",
                ticker=f"QRY{i:04d}",
                name=f"Query Company {i}",
                status="active" if i % 2 == 0 else "inactive"
            )
            for i in range(1000)
        ]
        db_session.add_all(companies)
        await db_session.commit()
        
        # Test queries
        queries = [
            ("SELECT * FROM companies LIMIT 100", "Simple select"),
            ("SELECT * FROM companies WHERE status = 'active' LIMIT 100", "Filtered select"),
            ("SELECT COUNT(*) FROM companies", "Count all"),
            ("SELECT * FROM companies WHERE ticker LIKE 'QRY%' LIMIT 100", "Pattern match"),
        ]
        
        for query, description in queries:
            start = time.time()
            await db_session.execute(text(query))
            await db_session.commit()
            duration = time.time() - start
            
            print(f"\n{description}: {duration*1000:.2f}ms")
            assert duration < 1.0, f"{description} too slow: {duration*1000:.2f}ms"
    
    @pytest.mark.asyncio
    async def test_query_performance_with_joins(self, db_session: AsyncSession):
        """Test query performance with joins."""
        # Create company with runs
        company = CompanyRecord(
            id="join-test-company",
            ticker="JOIN",
            name="Join Test Company",
            status="active"
        )
        db_session.add(company)
        await db_session.flush()
        
        # Add runs
        runs = [
            ResearchRunRecord(
                id=f"join-run-{i}",
                company_id=company.id,
                status="completed"
            )
            for i in range(100)
        ]
        db_session.add_all(runs)
        await db_session.commit()
        
        # Test join queries
        start = time.time()
        result = await db_session.execute(text("""
            SELECT c.*, COUNT(r.id) as run_count
            FROM companies c
            LEFT JOIN research_runs r ON c.id = r.company_id
            WHERE c.id = :company_id
            GROUP BY c.id
        """), {"company_id": company.id})
        await db_session.commit()
        duration = time.time() - start
        
        print(f"\nJoin query: {duration*1000:.2f}ms")
        assert duration < 0.5, f"Join query too slow: {duration*1000:.2f}ms"
    
    @pytest.mark.asyncio
    async def test_concurrent_reads(self, db_session: AsyncSession):
        """Test concurrent read performance."""
        # Insert test data
        companies = [
            CompanyRecord(
                id=f"concurrent-{i}",
                ticker=f"CON{i:04d}",
                name=f"Concurrent Company {i}",
                status="active"
            )
            for i in range(100)
        ]
        db_session.add_all(companies)
        await db_session.commit()
        
        async def read_query():
            result = await db_session.execute(
                text("SELECT * FROM companies WHERE status = 'active' LIMIT 10")
            )
            return result.all()
        
        # Run concurrent queries
        start = time.time()
        tasks = [read_query() for _ in range(10)]
        await asyncio.gather(*tasks)
        duration = time.time() - start
        
        print(f"\nConcurrent reads (10 queries): {duration*1000:.2f}ms")
        assert duration < 2.0, f"Concurrent reads too slow: {duration*1000:.2f}ms"


class TestConnectionPool:
    """Test database connection pool behavior."""
    
    @pytest.mark.asyncio
    async def test_connection_pool_size(self):
        """Test that connection pool works correctly."""
        db_manager = DatabaseManager()
        
        # Create multiple sessions
        sessions = []
        for _ in range(5):
            session = await db_manager.get_session().__aenter__()
            sessions.append(session)
        
        # Use each session
        for session in sessions:
            await session.execute(text("SELECT 1"))
        
        # Clean up
        for session in sessions:
            await session.close()
        
        await db_manager.engine.dispose()
    
    @pytest.mark.asyncio
    async def test_connection_reuse(self, db_session: AsyncSession):
        """Test connection reuse."""
        # Multiple queries on same session
        for i in range(10):
            result = await db_session.execute(text("SELECT 1"))
            row = result.scalar()
            assert row == 1


class TestMemoryUsage:
    """Test memory usage patterns."""
    
    @pytest.mark.asyncio
    async def test_large_result_set_handling(self, db_session: AsyncSession):
        """Test handling of large result sets."""
        # Create many records
        companies = [
            CompanyRecord(
                id=f"large-{i}",
                ticker=f"LRG{i:05d}",
                name=f"Large Dataset Company {i}",
                status="active"
            )
            for i in range(10000)
        ]
        
        # Insert in batches
        batch_size = 1000
        for i in range(0, len(companies), batch_size):
            batch = companies[i:i+batch_size]
            db_session.add_all(batch)
            await db_session.commit()
        
        # Query with pagination
        start = time.time()
        result = await db_session.execute(
            text("SELECT * FROM companies WHERE status = 'active' LIMIT 100")
        )
        rows = result.all()
        duration = time.time() - start
        
        print(f"\nLarge dataset query: {len(rows)} rows in {duration*1000:.2f}ms")
        assert len(rows) == 100
        assert duration < 1.0


class TestStressTests:
    """Stress tests for the system."""
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_sustained_load(self, db_session: AsyncSession):
        """Test sustained load over time."""
        # Create test company
        company = CompanyRecord(
            id="stress-test",
            ticker="STRS",
            name="Stress Test",
            status="active"
        )
        db_session.add(company)
        await db_session.flush()
        
        # Run many operations
        start = time.time()
        num_operations = 100
        
        for i in range(num_operations):
            # Mix of reads and writes
            if i % 2 == 0:
                # Write
                fact = FactRecord(
                    id=f"stress-fact-{i}",
                    company_id=company.id,
                    fact_key=f"stress_{i}",
                    fact_value=str(i),
                    status="active"
                )
                db_session.add(fact)
            else:
                # Read
                await db_session.execute(
                    text("SELECT * FROM facts WHERE company_id = :cid LIMIT 10"),
                    {"cid": company.id}
                )
            
            if i % 10 == 0:
                await db_session.commit()
        
        await db_session.commit()
        duration = time.time() - start
        
        rate = num_operations / duration
        print(f"\nSustained load: {num_operations} ops in {duration:.2f}s ({rate:.0f} ops/s)")
        assert rate > 10, f"Sustained load rate too low: {rate:.0f} ops/s"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
