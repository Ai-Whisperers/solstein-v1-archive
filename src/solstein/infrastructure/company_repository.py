"""Unified async SQLAlchemy repository for company operations.

Provides a clean data access layer for all company-related database operations
with comprehensive CRUD functionality and search capabilities.
"""

from typing import Any

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from .cache import cache_manager, company_key
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

    async def get_by_id(self, company_id: str) -> CompanyRecord | None:
        """Retrieve a single company by company_id with caching.

        Args:
            company_id: Unique company identifier.

        Returns:
            CompanyRecord if found, None otherwise.
        """
        # Check cache first
        cache_key = company_key(company_id)
        cached_data = await cache_manager.get(cache_key)
        if cached_data:
            # Convert cached dict back to CompanyRecord
            return CompanyRecord(**cached_data)

        # Fetch from database
        result = await self.session.execute(select(CompanyRecord).where(CompanyRecord.company_id == company_id))
        record = result.scalar_one_or_none()

        # Cache the result
        if record:
            await cache_manager.set(
                cache_key,
                {
                    "company_id": record.company_id,
                    "name": record.name,
                    "industry": record.industry,
                    "headquarters": record.headquarters,
                    "revenue_eur_m": record.revenue_eur_m,
                    "employees": record.employees,
                    "growth_rate_pct": record.growth_rate_pct,
                    "ai_score": record.ai_score,
                    "tier": record.tier,
                    "classification": record.classification,
                    "market_position": record.market_position,
                    "strategic_position": record.strategic_position,
                    "ai_maturity": record.ai_maturity,
                    "description": record.description,
                    "website": record.website,
                    "founded_year": record.founded_year,
                    "last_updated": str(record.last_updated) if record.last_updated else None,
                },
                ttl=3600,
            )

        return record

    async def create(self, company_data: dict[str, Any] | None = None, **kwargs) -> CompanyRecord:
        """Create a new company record.

        Handles both a single dictionary argument or keyword arguments.

        Args:
            company_data: Optional dictionary containing company attributes.
            **kwargs: Company attributes passed as keyword arguments.

        Returns:
            Created CompanyRecord object.

        Raises:
            ValueError: If required fields are missing.
        """
        # Merge dictionary and keyword arguments
        data = company_data.copy() if company_data else {}
        data.update(kwargs)

        if "company_id" not in data or "name" not in data:
            raise ValueError("company_id and name are required fields")

        record = CompanyRecord(**data)
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
        result = await self.session.execute(select(CompanyRecord).where(CompanyRecord.company_id == company_id))
        record = result.scalar_one_or_none()

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
        result = await self.session.execute(select(CompanyRecord).where(CompanyRecord.company_id == company_id))
        record = result.scalar_one_or_none()

        if not record:
            return False

        await self.session.delete(record)
        await self.session.flush()
        return True

    async def search(self, query: str, field: str = "name", skip: int = 0, limit: int = 100) -> list[CompanyRecord]:
        """Search companies by a specific field using case-insensitive matching.

        Args:
            query: Search query string.
            field: Field to search in (default: "name").
                Supported fields: name, industry, headquarters, description.
            skip: Number of records to skip (default: 0).
            limit: Maximum number of records to return (default: 100).

        Returns:
            List of matching CompanyRecord objects.

        Raises:
            ValueError: If field is not supported.
        """
        supported_fields = {"name", "industry", "headquarters", "description"}
        if field not in supported_fields:
            raise ValueError(f"Field '{field}' not supported. Choose from: {supported_fields}")

        search_field = getattr(CompanyRecord, field)
        result = await self.session.execute(
            select(CompanyRecord)
            .where(search_field.ilike(f"%{query}%"))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
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

    async def filter_by(self, skip: int = 0, limit: int = 100, **filters) -> list[CompanyRecord]:
        """Filter companies by multiple criteria.

        Args:
            skip: Number of records to skip (default: 0).
            limit: Maximum number of records to return (default: 100).
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

        result = await self.session.execute(
            select(CompanyRecord)
            .where(and_(*conditions))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
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

    async def get_all_filtered(
        self,
        industry: str | None = None,
        region: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[CompanyRecord]:
        """Retrieve companies with database-level filtering.

        Args:
            industry: Filter by industry (case-insensitive partial match).
            region: Filter by region/headquarters (case-insensitive partial match).
            skip: Number of records to skip (default: 0).
            limit: Maximum number of records to return (default: 100).

        Returns:
            List of CompanyRecord objects matching filters.
        """
        query = select(CompanyRecord)

        if industry:
            query = query.where(CompanyRecord.industry.ilike(f"%{industry}%"))

        if region:
            query = query.where(CompanyRecord.headquarters.ilike(f"%{region}%"))

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())
