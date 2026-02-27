"""Tests for CompanyRepository - unified async SQLAlchemy repository.

This test suite validates all CRUD operations and search functionality
of the CompanyRepository against a real test database.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from solstein.infrastructure.company_repository import CompanyRepository
from solstein.infrastructure.database_models import CompanyRecord


@pytest.mark.asyncio
class TestCompanyRepository:
    """Test suite for CompanyRepository."""

    async def test_initialization(self, db_session: AsyncSession):
        """Test CompanyRepository initializes correctly with AsyncSession."""
        repo = CompanyRepository(db_session)

        assert repo is not None
        assert repo.session == db_session

    async def test_create_company(self, db_session: AsyncSession):
        """Test creating a new company record."""
        repo = CompanyRepository(db_session)

        company_data = {
            "company_id": "test-comp-001",
            "name": "Test Company Inc",
            "industry": "Energy Software",
            "website": "https://testcompany.com",
            "headquarters": "Berlin",
            "founded_year": 2015,
        }

        record = await repo.create(company_data)

        assert record is not None
        assert isinstance(record, CompanyRecord)
        assert record.company_id == "test-comp-001"
        assert record.name == "Test Company Inc"
        assert record.industry == "Energy Software"
        assert record.website == "https://testcompany.com"

    async def test_create_company_missing_required_fields(self, db_session: AsyncSession):
        """Test creating a company without required fields raises ValueError."""
        repo = CompanyRepository(db_session)

        # Missing company_id
        with pytest.raises(ValueError, match="company_id and name are required"):
            await repo.create({"name": "Test Company"})

        # Missing name
        with pytest.raises(ValueError, match="company_id and name are required"):
            await repo.create({"company_id": "test-001"})

    async def test_get_by_id(self, db_session: AsyncSession):
        """Test retrieving a company by ID."""
        repo = CompanyRepository(db_session)

        # Create a company
        company_data = {
            "company_id": "test-comp-002",
            "name": "Retrieve Test Company",
            "industry": "Energy Software",
        }
        created = await repo.create(company_data)
        await db_session.commit()

        # Retrieve it
        retrieved = await repo.get_by_id("test-comp-002")

        assert retrieved is not None
        assert retrieved.company_id == "test-comp-002"
        assert retrieved.name == "Retrieve Test Company"

    async def test_get_by_id_not_found(self, db_session: AsyncSession):
        """Test retrieving a non-existent company returns None."""
        repo = CompanyRepository(db_session)

        result = await repo.get_by_id("non-existent-id")

        assert result is None

    async def test_get_all(self, db_session: AsyncSession):
        """Test retrieving all companies with pagination."""
        repo = CompanyRepository(db_session)

        # Create multiple companies
        for i in range(5):
            await repo.create(
                {
                    "company_id": f"test-comp-all-{i}",
                    "name": f"Company {i}",
                    "industry": "Energy Software",
                }
            )
        await db_session.commit()

        # Get all with default pagination
        all_companies = await repo.get_all()

        assert len(all_companies) >= 5
        assert all(isinstance(c, CompanyRecord) for c in all_companies)

    async def test_get_all_with_pagination(self, db_session: AsyncSession):
        """Test pagination parameters work correctly."""
        repo = CompanyRepository(db_session)

        # Create 10 companies
        for i in range(10):
            await repo.create(
                {
                    "company_id": f"test-comp-page-{i}",
                    "name": f"Pagination Company {i}",
                    "industry": "Energy Software",
                }
            )
        await db_session.commit()

        # Test skip and limit
        page1 = await repo.get_all(skip=0, limit=3)
        page2 = await repo.get_all(skip=3, limit=3)

        assert len(page1) == 3
        assert len(page2) == 3
        assert page1[0].company_id != page2[0].company_id

    async def test_update_company(self, db_session: AsyncSession):
        """Test updating an existing company record."""
        repo = CompanyRepository(db_session)

        # Create a company
        await repo.create(
            {
                "company_id": "test-comp-update",
                "name": "Original Name",
                "industry": "Energy Software",
                "revenue_eur_m": 10.0,
            }
        )
        await db_session.commit()

        # Update it
        updated = await repo.update(
            "test-comp-update",
            {
                "name": "Updated Name",
                "revenue_eur_m": 15.5,
            },
        )

        assert updated.name == "Updated Name"
        assert updated.revenue_eur_m == 15.5
        assert updated.company_id == "test-comp-update"  # Unchanged

    async def test_update_company_not_found(self, db_session: AsyncSession):
        """Test updating a non-existent company raises ValueError."""
        repo = CompanyRepository(db_session)

        with pytest.raises(ValueError, match="not found"):
            await repo.update("non-existent", {"name": "New Name"})

    async def test_delete_company(self, db_session: AsyncSession):
        """Test deleting a company record."""
        repo = CompanyRepository(db_session)

        # Create a company
        await repo.create(
            {
                "company_id": "test-comp-delete",
                "name": "To Delete",
                "industry": "Energy Software",
            }
        )
        await db_session.commit()

        # Delete it
        result = await repo.delete("test-comp-delete")

        assert result is True

        # Verify it's gone
        retrieved = await repo.get_by_id("test-comp-delete")
        assert retrieved is None

    async def test_delete_company_not_found(self, db_session: AsyncSession):
        """Test deleting a non-existent company returns False."""
        repo = CompanyRepository(db_session)

        result = await repo.delete("non-existent-id")

        assert result is False

    async def test_search_by_name(self, db_session: AsyncSession):
        """Test searching companies by name."""
        repo = CompanyRepository(db_session)

        # Create companies with specific names
        await repo.create(
            {
                "company_id": "test-search-1",
                "name": "Acme Energy Solutions",
                "industry": "Energy Software",
            }
        )
        await repo.create(
            {
                "company_id": "test-search-2",
                "name": "Acme Power Systems",
                "industry": "Energy Software",
            }
        )
        await repo.create(
            {
                "company_id": "test-search-3",
                "name": "Different Company",
                "industry": "Energy Software",
            }
        )
        await db_session.commit()

        # Search for "Acme"
        results = await repo.search("Acme", field="name")

        assert len(results) >= 2
        assert all("Acme" in c.name for c in results)

    async def test_search_case_insensitive(self, db_session: AsyncSession):
        """Test that search is case-insensitive."""
        repo = CompanyRepository(db_session)

        await repo.create(
            {
                "company_id": "test-case-1",
                "name": "TestCompany",
                "industry": "Energy Software",
            }
        )
        await db_session.commit()

        # Search with different cases
        results_lower = await repo.search("testcompany", field="name")
        results_upper = await repo.search("TESTCOMPANY", field="name")
        results_mixed = await repo.search("TeStCoMpAnY", field="name")

        assert len(results_lower) >= 1
        assert len(results_upper) >= 1
        assert len(results_mixed) >= 1

    async def test_search_by_industry(self, db_session: AsyncSession):
        """Test searching companies by industry."""
        repo = CompanyRepository(db_session)

        await repo.create(
            {
                "company_id": "test-ind-1",
                "name": "Energy Company",
                "industry": "Energy Software",
            }
        )
        await repo.create(
            {
                "company_id": "test-ind-2",
                "name": "Finance Company",
                "industry": "Financial Services",
            }
        )
        await db_session.commit()

        results = await repo.search("Energy", field="industry")

        assert len(results) >= 1
        assert all("Energy" in c.industry for c in results if c.industry)

    async def test_search_invalid_field(self, db_session: AsyncSession):
        """Test searching with invalid field raises ValueError."""
        repo = CompanyRepository(db_session)

        with pytest.raises(ValueError, match="not supported"):
            await repo.search("query", field="invalid_field")

    async def test_filter_by_single_criterion(self, db_session: AsyncSession):
        """Test filtering by a single criterion."""
        repo = CompanyRepository(db_session)

        await repo.create(
            {
                "company_id": "test-filter-1",
                "name": "Phoenix Company",
                "industry": "Energy Software",
                "classification": "Phoenix",
            }
        )
        await repo.create(
            {
                "company_id": "test-filter-2",
                "name": "Salt Company",
                "industry": "Energy Software",
                "classification": "Salt",
            }
        )
        await db_session.commit()

        results = await repo.filter_by(classification="Phoenix")

        assert len(results) >= 1
        assert all(c.classification == "Phoenix" for c in results)

    async def test_filter_by_multiple_criteria(self, db_session: AsyncSession):
        """Test filtering by multiple criteria."""
        repo = CompanyRepository(db_session)

        await repo.create(
            {
                "company_id": "test-multi-1",
                "name": "Company A",
                "industry": "Energy Software",
                "classification": "Phoenix",
                "tier": "Enterprise",
            }
        )
        await repo.create(
            {
                "company_id": "test-multi-2",
                "name": "Company B",
                "industry": "Energy Software",
                "classification": "Phoenix",
                "tier": "Mid-Market",
            }
        )
        await db_session.commit()

        results = await repo.filter_by(classification="Phoenix", tier="Enterprise")

        assert len(results) >= 1
        assert all(c.classification == "Phoenix" and c.tier == "Enterprise" for c in results)

    async def test_filter_by_no_criteria(self, db_session: AsyncSession):
        """Test filtering with no criteria raises ValueError."""
        repo = CompanyRepository(db_session)

        with pytest.raises(ValueError, match="At least one filter criterion"):
            await repo.filter_by()

    async def test_filter_by_invalid_attribute(self, db_session: AsyncSession):
        """Test filtering by invalid attribute raises ValueError."""
        repo = CompanyRepository(db_session)

        with pytest.raises(ValueError, match="has no attribute"):
            await repo.filter_by(invalid_attr="value")

    async def test_filter_by_no_matches(self, db_session: AsyncSession):
        """Test filtering with no matches returns empty list."""
        repo = CompanyRepository(db_session)

        await repo.create(
            {
                "company_id": "test-nomatch-1",
                "name": "Company",
                "industry": "Energy Software",
                "classification": "Phoenix",
            }
        )
        await db_session.commit()

        results = await repo.filter_by(classification="NonExistent")

        assert results == []
