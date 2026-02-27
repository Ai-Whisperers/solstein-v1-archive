# Solstein Repository Pattern Guide

## Overview

Solstein uses a unified async repository pattern for all data access. This guide explains the pattern, when to use it, and how to implement new repositories.

## Why Repository Pattern?

1. **Separation of Concerns** - Business logic separated from data access
2. **Testability** - Easy to mock repositories for testing
3. **Maintainability** - Centralized data access logic
4. **Consistency** - Same pattern across all data operations
5. **Type Safety** - Full type hints for all operations

## Core Principles

### 1. Async-First

All repository methods are async:

```python
# Good
async def get_by_id(self, id: str) -> Optional[CompanyRecord]:
    result = await self.session.execute(...)
    return result.scalar_one_or_none()

# Avoid
async def get_by_id(self, id: str) -> Optional[CompanyRecord]:
    return self.session.query(CompanyRecord).get(id)  # Old sync style
```

### 2. Session Injection

Repositories receive session via constructor:

```python
class CompanyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
```

Not via global state or singletons.

### 3. Return Type Hints

All methods have explicit return types:

```python
async def get_by_id(self, id: str) -> Optional[CompanyRecord]: ...
async def get_all(self, skip: int = 0, limit: int = 100) -> List[CompanyRecord]: ...
async def create(self, ...) -> CompanyRecord: ...
```

### 4. Transaction Boundary

Transactions managed at service layer, not repository:

```python
# Service layer manages transaction
async def create_company_with_facts(self, ...):
    async with self.session.begin():
        company = await self.company_repo.create(...)
        fact = await self.fact_repo.create(company_id=company.id, ...)
        # Both committed together
```

## Standard Repository Methods

### CRUD Operations

```python
class StandardRepository:
    # Create
    async def create(self, **kwargs) -> ModelType:
        instance = ModelType(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        return instance
    
    # Read
    async def get_by_id(self, id: str) -> Optional[ModelType]:
        result = await self.session.execute(
            select(ModelType).where(ModelType.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        result = await self.session.execute(
            select(ModelType)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    # Update
    async def update(
        self,
        id: str,
        **kwargs
    ) -> Optional[ModelType]:
        instance = await self.get_by_id(id)
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            await self.session.flush()
        return instance
    
    # Delete
    async def delete(self, id: str) -> bool:
        instance = await self.get_by_id(id)
        if instance:
            await self.session.delete(instance)
            await self.session.flush()
            return True
        return False
```

### Query Methods

```python
# Filter by field
async def get_by_company(
    self,
    company_id: str,
    status: Optional[str] = None
) -> List[ModelType]:
    query = select(ModelType).where(
        ModelType.company_id == company_id
    )
    if status:
        query = query.where(ModelType.status == status)
    result = await self.session.execute(query)
    return list(result.scalars().all())

# Search
async def search(self, query: str) -> List[ModelType]:
    result = await self.session.execute(
        select(ModelType).where(
            or_(
                ModelType.name.ilike(f"%{query}%"),
                ModelType.ticker.ilike(f"%{query}%")
            )
        )
    )
    return list(result.scalars().all())

# Count
async def count(self, **filters) -> int:
    query = select(func.count()).select_from(ModelType)
    for key, value in filters.items():
        query = query.where(getattr(ModelType, key) == value)
    result = await self.session.execute(query)
    return result.scalar()

# Exists
async def exists(self, id: str) -> bool:
    result = await self.session.execute(
        select(1).where(ModelType.id == id)
    )
    return result.scalar() is not None
```

## Example: CompanyRepository

```python
from typing import Optional, List
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.solstein.infrastructure.models import CompanyRecord


class CompanyRepository:
    """Repository for company operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(
        self,
        ticker: str,
        name: str,
        sector: Optional[str] = None,
        industry: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> CompanyRecord:
        """Create a new company."""
        company = CompanyRecord(
            ticker=ticker,
            name=name,
            sector=sector,
            industry=industry,
            metadata=metadata or {}
        )
        self.session.add(company)
        await self.session.flush()
        return company
    
    async def get_by_id(self, id: str) -> Optional[CompanyRecord]:
        """Get company by ID."""
        result = await self.session.execute(
            select(CompanyRecord).where(CompanyRecord.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_ticker(self, ticker: str) -> Optional[CompanyRecord]:
        """Get company by ticker symbol."""
        result = await self.session.execute(
            select(CompanyRecord).where(
                CompanyRecord.ticker == ticker
            )
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[CompanyRecord]:
        """Get all companies with pagination."""
        result = await self.session.execute(
            select(CompanyRecord)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def update(
        self,
        id: str,
        **kwargs
    ) -> Optional[CompanyRecord]:
        """Update company fields."""
        company = await self.get_by_id(id)
        if company:
            for key, value in kwargs.items():
                if hasattr(company, key):
                    setattr(company, key, value)
            await self.session.flush()
        return company
    
    async def delete(self, id: str) -> bool:
        """Delete company by ID."""
        company = await self.get_by_id(id)
        if company:
            await self.session.delete(company)
            await self.session.flush()
            return True
        return False
    
    async def exists(self, id: str) -> bool:
        """Check if company exists."""
        result = await self.session.execute(
            select(1).where(CompanyRecord.id == id)
        )
        return result.scalar() is not None
    
    async def search(self, query: str) -> List[CompanyRecord]:
        """Search companies by name or ticker."""
        result = await self.session.execute(
            select(CompanyRecord).where(
                or_(
                    CompanyRecord.name.ilike(f"%{query}%"),
                    CompanyRecord.ticker.ilike(f"%{query}%")
                )
            )
        )
        return list(result.scalars().all())
    
    async def update_metadata(
        self,
        id: str,
        metadata: dict
    ) -> Optional[CompanyRecord]:
        """Update company metadata."""
        company = await self.get_by_id(id)
        if company:
            company.metadata.update(metadata)
            await self.session.flush()
        return company
```

## Example: FactRepository

```python
from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.solstein.infrastructure.models import FactRecord


class FactRepository:
    """Repository for fact operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(
        self,
        company_id: str,
        fact_key: str,
        fact_value: str,
        confidence: float = 1.0,
        source: Optional[str] = None,
        run_id: Optional[str] = None
    ) -> FactRecord:
        """Create a new fact."""
        fact = FactRecord(
            company_id=company_id,
            run_id=run_id,
            fact_key=fact_key,
            fact_value=fact_value,
            confidence=confidence,
            source=source,
            status="active"
        )
        self.session.add(fact)
        await self.session.flush()
        return fact
    
    async def get_by_company(
        self,
        company_id: str,
        status: Optional[str] = None
    ) -> List[FactRecord]:
        """Get facts by company."""
        query = select(FactRecord).where(
            FactRecord.company_id == company_id
        )
        if status:
            query = query.where(FactRecord.status == status)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def update_confidence(
        self,
        fact_id: str,
        confidence: float
    ) -> Optional[FactRecord]:
        """Update fact confidence."""
        fact = await self.get_by_id(fact_id)
        if fact:
            fact.confidence = confidence
            await self.session.flush()
        return fact
    
    async def supersede(
        self,
        fact_id: str,
        reason: str
    ) -> Optional[FactRecord]:
        """Mark fact as superseded."""
        fact = await self.get_by_id(fact_id)
        if fact:
            fact.status = "superseded"
            fact.superseded_at = datetime.utcnow()
            fact.superseded_reason = reason
            await self.session.flush()
        return fact
    
    async def get_high_confidence(
        self,
        company_id: str,
        min_confidence: float = 0.8
    ) -> List[FactRecord]:
        """Get high confidence facts."""
        result = await self.session.execute(
            select(FactRecord).where(
                and_(
                    FactRecord.company_id == company_id,
                    FactRecord.confidence >= min_confidence,
                    FactRecord.status == "active"
                )
            )
        )
        return list(result.scalars().all())
```

## Service Layer Integration

```python
class CompanyService:
    """Service for company operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.company_repo = CompanyRepository(session)
        self.fact_repo = FactRepository(session)
    
    async def create_company_with_facts(
        self,
        ticker: str,
        name: str,
        facts: List[dict]
    ) -> CompanyRecord:
        """Create company with initial facts."""
        async with self.session.begin():
            # Create company
            company = await self.company_repo.create(
                ticker=ticker,
                name=name
            )
            
            # Create facts
            for fact_data in facts:
                await self.fact_repo.create(
                    company_id=company.id,
                    **fact_data
                )
            
            return company
```

## Testing Repositories

```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_company_repository(db_session: AsyncSession):
    """Test company repository."""
    repo = CompanyRepository(db_session)
    
    # Create
    company = await repo.create(
        ticker="TEST",
        name="Test Company"
    )
    assert company.id is not None
    
    # Read
    found = await repo.get_by_id(company.id)
    assert found is not None
    assert found.ticker == "TEST"
    
    # Update
    updated = await repo.update(
        company.id,
        name="Updated Name"
    )
    assert updated.name == "Updated Name"
    
    # Delete
    deleted = await repo.delete(company.id)
    assert deleted is True
    
    # Verify deletion
    not_found = await repo.get_by_id(company.id)
    assert not_found is None
```

## Anti-Patterns to Avoid

### Don't Use Global Session

```python
# Bad
global_session = get_session()

class BadRepository:
    async def get(self, id: str):
        return global_session.query(Model).get(id)

# Good
class GoodRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
```

### Don't Manage Transactions in Repository

```python
# Bad
class BadRepository:
    async def create(self, data):
        async with self.session.begin():  # Don't do this
            ...

# Good
class GoodRepository:
    async def create(self, data):
        # Just add to session
        self.session.add(instance)
        await self.session.flush()
```

### Don't Return ORM Objects Outside Transaction

```python
# Bad
async def get_company(id: str):
    async with get_session() as session:
        repo = CompanyRepository(session)
        return await repo.get_by_id(id)
    # Session closed, ORM object detached!

# Good
async def get_company_dto(id: str):
    async with get_session() as session:
        repo = CompanyRepository(session)
        company = await repo.get_by_id(id)
        return CompanyDTO.from_orm(company)  # Convert to DTO
```

## Migration from Sync to Async

If you're migrating existing sync repositories:

1. Add `async` to all methods
2. Replace `session.query()` with `select()`
3. Add `await` before all session operations
4. Replace `session.commit()` with `await session.flush()`
5. Update return types to use proper async types

---

**See Also:**
- [Architecture Documentation](ARCHITECTURE.md)
- [Database Schema](DATABASE_SCHEMA.md)
- [API Documentation](API_DOCUMENTATION.md)
