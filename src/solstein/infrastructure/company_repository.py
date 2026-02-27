"""Unified async SQLAlchemy repository for company operations.

Provides a clean data access layer for all company-related database operations
with comprehensive CRUD functionality and search capabilities.
"""

from typing import Any, Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from .database_models import CompanyRecord


class CompanyRepository:
    """Repository for company data access and manipulation.

    Provides async methods for CRUD operations and advanced queries on company records.
    All methods are async-safe and work with SQLAlchemy's AsyncSession.
    """

    def __init__(self, session: AsyncSession):
        """Initialize repository with async database session.

        Args:
            session: AsyncSession instance for database operations.
        """
        self.session = session

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[CompanyRecord]:
        """Retrieve all companies with pagination.

        Args:
            skip: Number of records to skip (default: 0).
            limit: Maximum number of records to return (default: 100).

        Returns:
            List of CompanyRecord objects.
        """
        result = await self.session.execute(select(CompanyRecord).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def get_by_id(self, company_id: str) -> Optional[CompanyRecord]:
        """Retrieve a single company by company_id.

        Args:
            company_id: Unique company identifier.

        Returns:
            CompanyRecord if found, None otherwise.
        """
        result = await self.session.execute(select(CompanyRecord).where(CompanyRecord.company_id == company_id))
        return result.scalar_one_or_none()

    async def create(self, company_data: dict[str, Any]) -> CompanyRecord:
        """Create a new company record.

        Args:
            company_data: Dictionary containing company attributes.
                Must include 'company_id' and 'name' at minimum.

        Returns:
            Created CompanyRecord object.

        Raises:
            ValueError: If required fields are missing.
        """
        if "company_id" not in company_data or "name" not in company_data:
            raise ValueError("company_id and name are required fields")

        record = CompanyRecord(**company_data)
        self.session.add(record)
        await self.session.flush()
        return record

    async def update(self, company_id: str, company_data: dict[str, Any]) -> CompanyRecord:
        """Update an existing company record.

        Args:
            company_id: Unique company identifier.
            company_data: Dictionary of fields to update.

        Returns:
            Updated CompanyRecord object.

        Raises:
            ValueError: If company not found.
        """
        record = await self.get_by_id(company_id)
        if not record:
            raise ValueError(f"Company with id {company_id} not found")

        for key, value in company_data.items():
            if hasattr(record, key):
                setattr(record, key, value)

        self.session.add(record)
        await self.session.flush()
        return record

    async def delete(self, company_id: str) -> bool:
        """Delete a company record.

        Args:
            company_id: Unique company identifier.

        Returns:
            True if deletion was successful, False if company not found.
        """
        record = await self.get_by_id(company_id)
        if not record:
            return False

        await self.session.delete(record)
        await self.session.flush()
        return True

    async def search(self, query: str, field: str = "name") -> list[CompanyRecord]:
        """Search companies by a specific field using case-insensitive matching.

        Args:
            query: Search query string.
            field: Field to search in (default: "name").
                Supported fields: name, industry, headquarters, description.

        Returns:
            List of matching CompanyRecord objects.

        Raises:
            ValueError: If field is not supported.
        """
        supported_fields = {"name", "industry", "headquarters", "description"}
        if field not in supported_fields:
            raise ValueError(f"Field '{field}' not supported. Choose from: {supported_fields}")

        search_field = getattr(CompanyRecord, field)
        result = await self.session.execute(select(CompanyRecord).where(search_field.ilike(f"%{query}%")))
        return list(result.scalars().all())

    async def filter_by(self, **filters) -> list[CompanyRecord]:
        """Filter companies by multiple criteria.

        Args:
            **filters: Arbitrary keyword arguments for filtering.
                Supported filters: tier, classification, ai_maturity, industry, etc.

        Returns:
            List of CompanyRecord objects matching all filter criteria.

        Raises:
            ValueError: If no valid filters are provided.
        """
        if not filters:
            raise ValueError("At least one filter criterion must be provided")

        conditions = []
        for key, value in filters.items():
            if not hasattr(CompanyRecord, key):
                raise ValueError(f"CompanyRecord has no attribute '{key}'")
            conditions.append(getattr(CompanyRecord, key) == value)

        result = await self.session.execute(select(CompanyRecord).where(and_(*conditions)))
        return list(result.scalars().all())
