"""
Comprehensive repository test suite.

Tests all repository methods with real database operations.
"""

import os
import sys

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from solstein.domain.facts import Fact
from solstein.infrastructure.company_repository import CompanyRepository
from solstein.infrastructure.database_models import CompanyRecord
from solstein.infrastructure.repositories import FactRepository


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    """Provide database session."""
    from solstein.config import Settings
    from solstein.infrastructure.database import DatabaseManager

    db_manager = DatabaseManager(Settings.load())
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
        company_id="test-company", ticker="TEST", name="Test Company", status="active", industry="Technology"
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
            company_id="new-id", ticker="NEW", name="New Company", industry="Finance", employees=500
        )

        assert company.company_id == "new-id"
        assert company.ticker == "NEW"
        assert company.name == "New Company"
        assert company.employees == 500

    @pytest.mark.asyncio
    async def test_get_by_id(self, company_repo: CompanyRepository, sample_company: CompanyRecord):
        """Test retrieving company by ID (company_id)."""
        result = await company_repo.get_by_id(sample_company.company_id)

        assert result is not None
        assert result.company_id == sample_company.company_id
        assert result.ticker == sample_company.ticker

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, company_repo: CompanyRepository):
        """Test retrieving non-existent company."""
        result = await company_repo.get_by_id("non-existent-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_all(self, company_repo: CompanyRepository, db_session: AsyncSession):
        """Test retrieving all companies with pagination."""
        # Create multiple companies
        for i in range(5):
            company = CompanyRecord(company_id=f"company-{i}", ticker=f"TICK{i}", name=f"Company {i}", status="active")
            db_session.add(company)
        await db_session.flush()

        results = await company_repo.get_all(skip=0, limit=10)
        assert len(results) >= 5

    @pytest.mark.asyncio
    async def test_update(self, company_repo: CompanyRepository, sample_company: CompanyRecord):
        """Test updating company."""
        updated = await company_repo.update(
            sample_company.company_id, {"name": "Updated Company", "status": "inactive"}
        )

        assert updated is not None
        assert updated.name == "Updated Company"
        assert updated.status == "inactive"
        assert updated.ticker == sample_company.ticker  # Unchanged

    @pytest.mark.asyncio
    async def test_delete(self, company_repo: CompanyRepository, db_session: AsyncSession):
        """Test deleting company."""
        company = CompanyRecord(company_id="delete-test", ticker="DEL", name="Delete Test", status="active")
        db_session.add(company)
        await db_session.flush()

        result = await company_repo.delete(company.company_id)
        assert result is True

        # Verify deletion
        stmt = select(CompanyRecord).where(CompanyRecord.company_id == company.company_id)
        deleted = (await db_session.execute(stmt)).scalar_one_or_none()
        assert deleted is None

    @pytest.mark.asyncio
    async def test_search(self, company_repo: CompanyRepository, db_session: AsyncSession):
        """Test searching companies."""
        companies = [
            CompanyRecord(company_id="c1", ticker="AAPL", name="Apple Inc", status="active", industry="Tech"),
            CompanyRecord(company_id="c2", ticker="MSFT", name="Microsoft", status="active", industry="Tech"),
            CompanyRecord(company_id="c3", ticker="APPX", name="App Corp", status="active", industry="Tech"),
        ]
        db_session.add_all(companies)
        await db_session.flush()

        results = await company_repo.search("app")
        assert len(results) >= 2  # Apple and App Corp


class TestFactRepository:
    """Test suite for FactRepository."""

    @pytest.mark.asyncio
    async def test_create_batch(self, fact_repo: FactRepository, sample_company: CompanyRecord):
        """Test creating a gathering batch."""
        batch = await fact_repo.create_batch(company_id=sample_company.company_id)
        assert batch.batch_id is not None
        assert batch.company_id == sample_company.company_id
        assert batch.status == "in_progress"

    @pytest.mark.asyncio
    async def test_store_fact(self, fact_repo: FactRepository, sample_company: CompanyRecord):
        """Test storing a fact."""
        batch = await fact_repo.create_batch(company_id=sample_company.company_id)

        fact = Fact(
            company_id=sample_company.company_id,
            batch_id=batch.batch_id,
            fact_type="revenue",
            value=1000000.0,
            confidence=0.9,
        )
        fact_id = await fact_repo.store(fact)
        assert fact_id is not None

    @pytest.mark.asyncio
    async def test_get_company_facts(self, fact_repo: FactRepository, sample_company: CompanyRecord):
        """Test retrieving facts by company."""
        batch = await fact_repo.create_batch(company_id=sample_company.company_id)

        for i in range(3):
            fact = Fact(
                company_id=sample_company.company_id,
                batch_id=batch.batch_id,
                fact_type=f"metric_{i}",
                value=float(i * 100),
                confidence=0.8,
            )
            await fact_repo.store(fact)

        results = await fact_repo.get_company_facts(sample_company.company_id)
        assert len(results) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
