"""
Comprehensive repository test suite.

Tests all repository methods with real database operations.
"""

import os
import sys
import pytest
import pytest_asyncio
from datetime import datetime, timezone
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.solstein.infrastructure.models import (
    CompanyRecord, ResearchRunRecord, FactRecord, SignalRecord,
    ScoringRecord, SignalRecord as SignalRecordModel, EnrichmentJobRecord
)
from src.solstein.infrastructure.repositories import FactRepository
from src.solstein.infrastructure.company_repository import CompanyRepository


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    """Provide database session."""
    from src.solstein.infrastructure.database import DatabaseManager
    db_manager = DatabaseManager()
    session = await db_manager.get_session().__aenter__()
    transaction = await session.begin_nested()
    yield session
    await transaction.rollback()
    await session.close()
    await db_manager.engine.dispose()


@pytest_asyncio.fixture
async def company_repo(db_session: AsyncSession) -> CompanyRepository:
    """Provide CompanyRepository instance."""
    return CompanyRepository(db_session)


@pytest_asyncio.fixture
async def fact_repo(db_session: AsyncSession) -> FactRepository:
    """Provide FactRepository instance."""
    return FactRepository(db_session)


@pytest_asyncio.fixture
async def sample_company(db_session: AsyncSession) -> CompanyRecord:
    """Create and return a sample company."""
    company = CompanyRecord(
        id="test-company",
        ticker="TEST",
        name="Test Company",
        status="active",
        sector="Technology"
    )
    db_session.add(company)
    await db_session.flush()
    return company


class TestCompanyRepository:
    """Test suite for CompanyRepository."""
    
    @pytest.mark.asyncio
    async def test_create_company(self, company_repo: CompanyRepository):
        """Test creating a new company."""
        company = await company_repo.create(
            ticker="NEW",
            name="New Company",
            sector="Finance",
            metadata={"employees": 500}
        )
        
        assert company.id is not None
        assert company.ticker == "NEW"
        assert company.name == "New Company"
        assert company.metadata == {"employees": 500}
    
    @pytest.mark.asyncio
    async def test_get_by_id(self, company_repo: CompanyRepository, sample_company: CompanyRecord):
        """Test retrieving company by ID."""
        result = await company_repo.get_by_id(sample_company.id)
        
        assert result is not None
        assert result.id == sample_company.id
        assert result.ticker == sample_company.ticker
    
    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, company_repo: CompanyRepository):
        """Test retrieving non-existent company."""
        result = await company_repo.get_by_id("non-existent-id")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_by_ticker(self, company_repo: CompanyRepository, sample_company: CompanyRecord):
        """Test retrieving company by ticker."""
        result = await company_repo.get_by_ticker("TEST")
        
        assert result is not None
        assert result.ticker == "TEST"
        assert result.id == sample_company.id
    
    @pytest.mark.asyncio
    async def test_get_all(self, company_repo: CompanyRepository, db_session: AsyncSession):
        """Test retrieving all companies with pagination."""
        # Create multiple companies
        for i in range(5):
            company = CompanyRecord(
                id=f"company-{i}",
                ticker=f"TICK{i}",
                name=f"Company {i}",
                status="active"
            )
            db_session.add(company)
        await db_session.flush()
        
        results = await company_repo.get_all(skip=0, limit=10)
        assert len(results) >= 5
    
    @pytest.mark.asyncio
    async def test_update(self, company_repo: CompanyRepository, sample_company: CompanyRecord):
        """Test updating company."""
        updated = await company_repo.update(
            sample_company.id,
            name="Updated Company",
            status="inactive"
        )
        
        assert updated is not None
        assert updated.name == "Updated Company"
        assert updated.status == "inactive"
        assert updated.ticker == sample_company.ticker  # Unchanged
    
    @pytest.mark.asyncio
    async def test_delete(self, company_repo: CompanyRepository, db_session: AsyncSession):
        """Test deleting company."""
        company = CompanyRecord(
            id="delete-test",
            ticker="DEL",
            name="Delete Test",
            status="active"
        )
        db_session.add(company)
        await db_session.flush()
        
        result = await company_repo.delete(company.id)
        assert result is True
        
        # Verify deletion
        deleted = await db_session.get(CompanyRecord, company.id)
        assert deleted is None
    
    @pytest.mark.asyncio
    async def test_exists(self, company_repo: CompanyRepository, sample_company: CompanyRecord):
        """Test checking company existence."""
        assert await company_repo.exists(sample_company.id) is True
        assert await company_repo.exists("non-existent") is False
    
    @pytest.mark.asyncio
    async def test_search(self, company_repo: CompanyRepository, db_session: AsyncSession):
        """Test searching companies."""
        companies = [
            CompanyRecord(id="c1", ticker="AAPL", name="Apple Inc", status="active"),
            CompanyRecord(id="c2", ticker="MSFT", name="Microsoft", status="active"),
            CompanyRecord(id="c3", ticker="APPX", name="App Corp", status="active"),
        ]
        db_session.add_all(companies)
        await db_session.flush()
        
        results = await company_repo.search("app")
        assert len(results) >= 2  # Apple and App Corp
    
    @pytest.mark.asyncio
    async def test_update_metadata(self, company_repo: CompanyRepository, sample_company: CompanyRecord):
        """Test updating company metadata."""
        updated = await company_repo.update_metadata(
            sample_company.id,
            {"revenue": 1000000, "employees": 100}
        )
        
        assert updated is not None
        assert updated.metadata == {"revenue": 1000000, "employees": 100}


class TestFactRepository:
    """Test suite for FactRepository."""
    
    @pytest.mark.asyncio
    async def test_create_fact(self, fact_repo: FactRepository, sample_company: CompanyRecord):
        """Test creating a fact."""
        fact = await fact_repo.create(
            company_id=sample_company.id,
            fact_key="revenue_2024",
            fact_value="1000000",
            confidence=0.95,
            source="financial_report"
        )
        
        assert fact.id is not None
        assert fact.fact_key == "revenue_2024"
        assert fact.confidence == 0.95
    
    @pytest.mark.asyncio
    async def test_get_facts_by_company(
        self, fact_repo: FactRepository, 
        sample_company: CompanyRecord,
        db_session: AsyncSession
    ):
        """Test retrieving facts by company."""
        # Create facts
        for i in range(3):
            fact = FactRecord(
                id=f"fact-{i}",
                company_id=sample_company.id,
                fact_key=f"metric_{i}",
                fact_value=f"value_{i}",
                status="active"
            )
            db_session.add(fact)
        await db_session.flush()
        
        results = await fact_repo.get_by_company(sample_company.id)
        assert len(results) == 3
    
    @pytest.mark.asyncio
    async def test_get_facts_by_company_with_status_filter(
        self, fact_repo: FactRepository,
        sample_company: CompanyRecord,
        db_session: AsyncSession
    ):
        """Test retrieving facts with status filter."""
        # Create active and superseded facts
        active_fact = FactRecord(
            id="fact-active",
            company_id=sample_company.id,
            fact_key="active_metric",
            fact_value="100",
            status="active"
        )
        superseded_fact = FactRecord(
            id="fact-super",
            company_id=sample_company.id,
            fact_key="old_metric",
            fact_value="50",
            status="superseded"
        )
        db_session.add_all([active_fact, superseded_fact])
        await db_session.flush()
        
        results = await fact_repo.get_by_company(sample_company.id, status="active")
        assert len(results) == 1
        assert results[0].status == "active"
    
    @pytest.mark.asyncio
    async def test_update_fact_confidence(
        self, fact_repo: FactRepository,
        sample_company: CompanyRecord,
        db_session: AsyncSession
    ):
        """Test updating fact confidence."""
        fact = FactRecord(
            id="fact-update",
            company_id=sample_company.id,
            fact_key="test_metric",
            fact_value="100",
            confidence=0.5
        )
        db_session.add(fact)
        await db_session.flush()
        
        updated = await fact_repo.update_confidence(fact.id, 0.9)
        assert updated.confidence == 0.9
    
    @pytest.mark.asyncio
    async def test_supersede_fact(
        self, fact_repo: FactRepository,
        sample_company: CompanyRecord,
        db_session: AsyncSession
    ):
        """Test superseding a fact."""
        fact = FactRecord(
            id="fact-super-1",
            company_id=sample_company.id,
            fact_key="revenue",
            fact_value="1000000",
            status="active"
        )
        db_session.add(fact)
        await db_session.flush()
        
        superseded = await fact_repo.supersede(fact.id, reason="New data available")
        assert superseded.status == "superseded"
        assert superseded.superseded_reason == "New data available"
        assert superseded.superseded_at is not None
    
    @pytest.mark.asyncio
    async def test_get_high_confidence_facts(
        self, fact_repo: FactRepository,
        sample_company: CompanyRecord,
        db_session: AsyncSession
    ):
        """Test retrieving high confidence facts."""
        facts = [
            FactRecord(
                id="high-1",
                company_id=sample_company.id,
                fact_key="high_conf",
                fact_value="100",
                confidence=0.95,
                status="active"
            ),
            FactRecord(
                id="low-1",
                company_id=sample_company.id,
                fact_key="low_conf",
                fact_value="50",
                confidence=0.4,
                status="active"
            ),
        ]
        db_session.add_all(facts)
        await db_session.flush()
        
        results = await fact_repo.get_high_confidence(sample_company.id, min_confidence=0.8)
        assert len(results) == 1
        assert results[0].id == "high-1"


class TestRepositoryTransactions:
    """Test transaction handling across repositories."""
    
    @pytest.mark.asyncio
    async def test_atomic_operations(self, db_session: AsyncSession):
        """Test that repository operations are atomic."""
        company_repo = CompanyRepository(db_session)
        
        # Create company
        company = await company_repo.create(
            ticker="ATOMIC",
            name="Atomic Test",
            status="active"
        )
        
        # Verify it exists in same session
        exists = await company_repo.exists(company.id)
        assert exists is True
        
        # Delete it
        deleted = await company_repo.delete(company.id)
        assert deleted is True
        
        # Verify it no longer exists
        exists = await company_repo.exists(company.id)
        assert exists is False
    
    @pytest.mark.asyncio
    async def test_cascading_operations(self, db_session: AsyncSession):
        """Test cascading operations with relationships."""
        # Create company with related data
        company = CompanyRecord(
            id="cascade-test",
            ticker="CASC",
            name="Cascade Test",
            status="active"
        )
        db_session.add(company)
        await db_session.flush()
        
        # Create facts
        fact_repo = FactRepository(db_session)
        for i in range(3):
            await fact_repo.create(
                company_id=company.id,
                fact_key=f"metric_{i}",
                fact_value=str(i * 100)
            )
        
        # Verify facts exist
        facts = await fact_repo.get_by_company(company.id)
        assert len(facts) == 3


class TestRepositoryPerformance:
    """Test repository performance characteristics."""
    
    @pytest.mark.asyncio
    async def test_bulk_create_performance(self, db_session: AsyncSession):
        """Test bulk create performance."""
        import time
        
        company_repo = CompanyRepository(db_session)
        
        # Bulk create 100 companies
        start = time.time()
        for i in range(100):
            await company_repo.create(
                ticker=f"BULK{i:03d}",
                name=f"Bulk Company {i}",
                status="active"
            )
        
        duration = time.time() - start
        assert duration < 30  # Should complete in under 30 seconds
    
    @pytest.mark.asyncio
    async def test_query_with_pagination(self, company_repo: CompanyRepository, db_session: AsyncSession):
        """Test paginated queries."""
        # Create 50 companies
        for i in range(50):
            company = CompanyRecord(
                id=f"page-company-{i}",
                ticker=f"PAGE{i:02d}",
                name=f"Page Company {i}",
                status="active"
            )
            db_session.add(company)
        await db_session.flush()
        
        # Test pagination
        page1 = await company_repo.get_all(skip=0, limit=10)
        page2 = await company_repo.get_all(skip=10, limit=10)
        
        assert len(page1) == 10
        assert len(page2) == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
