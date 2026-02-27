# Solstein - Testing Guide

This guide covers testing practices for the Solstein project with Supabase PostgreSQL.

## Overview

Solstein uses **real Supabase PostgreSQL** for database tests (not mocks). This ensures:
- Tests verify actual database behavior
- Foreign key constraints are validated
- Query performance is realistic
- No "mock drift" where tests pass but code fails in production

## Test Architecture

### Test Categories

1. **Unit Tests** - Test individual components in isolation
2. **Database Tests** - Test database operations with real Supabase
3. **Integration Tests** - Test multiple components working together

### Test Organization

```
tests/
├── conftest.py           # Shared fixtures (db_session, db_engine)
├── factories.py          # Test data factories
├── unit/
│   ├── test_fact_repository.py
│   ├── test_database.py
│   ├── test_database_service.py
│   └── test_enrichment_repositories.py
└── integration/
    └── (integration tests)
```

## Writing Database Tests

### Basic Pattern

```python
import pytest
from sqlalchemy import select
from solstein.domain.facts import Fact
from tests.factories import create_test_batch, create_test_fact

@pytest.mark.asyncio
class TestFactRepository:
    """Tests using real Supabase database."""
    
    async def test_create_fact(self, db_session):
        """Test creating a fact persists to database."""
        # Arrange - Create test data
        batch = await create_test_batch(db_session, "comp-123")
        
        # Act - Create fact
        fact = await create_test_fact(
            db_session,
            batch_id=str(batch.batch_id),
            company_id="comp-123",
            fact_type="revenue",
            value=1000000.0
        )
        
        # Assert - Verify in database
        result = await db_session.execute(
            select(Fact).where(Fact.fact_id == fact.fact_id)
        )
        persisted = result.scalar_one()
        assert persisted.value == 1000000.0
```

### Key Principles

1. **Use the `db_session` fixture** - Provides AsyncSession for database operations
2. **Use factories** - `create_test_batch()`, `create_test_fact()`, etc.
3. **Query database to verify** - Don't just assert return values
4. **Test FK constraints** - Ensure foreign keys are validated
5. **Clean up is automatic** - Each test gets fresh session (rolled back)

## Fixtures Reference

### db_session
Provides a fresh AsyncSession for each test.

```python
async def test_something(self, db_session):
    # db_session is an AsyncSession
    result = await db_session.execute(select(Fact))
    facts = result.scalars().all()
```

### db_engine
Provides the shared async engine (session-scoped).

```python
async def test_with_engine(self, db_engine):
    async with db_engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
```

## Factories Reference

### create_test_batch(session, company_id, **overrides)
Creates a GatheringBatch in the database.

```python
batch = await create_test_batch(
    db_session,
    company_id="comp-123",
    status="completed"  # optional override
)
```

### create_test_fact(session, batch_id, company_id, **overrides)
Creates a Fact in the database.

```python
fact = await create_test_fact(
    db_session,
    batch_id=str(batch.batch_id),
    company_id="comp-123",
    fact_type="revenue",
    value=5000000.0,
    confidence=0.95
)
```

### create_test_fact_source(session, fact_id, **overrides)
Creates a FactSource in the database.

```python
source = await create_test_fact_source(
    db_session,
    fact_id=str(fact.fact_id),
    source_type="sec_filing",
    url="https://sec.gov/..."
)
```

## Running Tests

### Run All Database Tests

```bash
uv run pytest tests/unit/test_fact_repository.py \
              tests/unit/test_database.py \
              tests/unit/test_database_service.py \
              tests/unit/test_enrichment_repositories.py \
              -v
```

### Run Specific Test File

```bash
uv run pytest tests/unit/test_fact_repository.py -v
```

### Run Specific Test

```bash
uv run pytest tests/unit/test_fact_repository.py::TestFactRepository::test_create_fact -v
```

### Run with Coverage

```bash
uv run pytest tests/unit/ --cov=src/solstein --cov-report=html
```

### Run in CI Mode (no progress bars)

```bash
uv run pytest tests/unit/ -v --tb=short
```

## Test Markers

Use markers to categorize tests:

```python
@pytest.mark.asyncio  # Required for async tests
@pytest.mark.db       # Database test
@pytest.mark.slow     # Slow test (> 5 seconds)
```

Run only database tests:
```bash
uv run pytest -m db
```

Skip slow tests:
```bash
uv run pytest -m "not slow"
```

## Common Patterns

### Testing FK Constraints

```python
async def test_fact_requires_batch(self, db_session):
    """Test that facts require a valid batch_id."""
    from sqlalchemy.exc import IntegrityError
    
    fact = Fact(
        company_id="comp-123",
        batch_id="non-existent-batch",  # Invalid FK
        fact_type="test",
        value=100
    )
    
    db_session.add(fact)
    
    with pytest.raises(IntegrityError):
        await db_session.commit()
```

### Testing Query Filters

```python
async def test_get_facts_by_type(self, db_session):
    """Test querying facts filtered by type."""
    batch = await create_test_batch(db_session, "comp-123")
    
    # Create facts of different types
    await create_test_fact(db_session, batch.batch_id, "comp-123", 
                          fact_type="revenue", value=1000000)
    await create_test_fact(db_session, batch.batch_id, "comp-123", 
                          fact_type="employees", value=500)
    
    # Query only revenue facts
    result = await db_session.execute(
        select(Fact).where(
            Fact.company_id == "comp-123",
            Fact.fact_type == "revenue"
        )
    )
    revenue_facts = result.scalars().all()
    
    assert len(revenue_facts) == 1
    assert revenue_facts[0].fact_type == "revenue"
```

### Testing Error Conditions

```python
async def test_invalid_confidence_raises_error(self, db_session):
    """Test that invalid confidence values are rejected."""
    from sqlalchemy.exc import IntegrityError
    
    batch = await create_test_batch(db_session, "comp-123")
    
    # Try to create fact with invalid confidence
    fact = Fact(
        company_id="comp-123",
        batch_id=batch.batch_id,
        fact_type="test",
        value=100,
        confidence=2.0  # Invalid: should be 0-1
    )
    
    db_session.add(fact)
    
    # Should raise an error (if constraint exists)
    # or accept it (if no constraint)
    await db_session.commit()
```

## Troubleshooting Tests

### Test is Slow

**Problem**: Tests taking too long

**Solution**:
- Mark with `@pytest.mark.slow`
- Check for N+1 queries
- Verify connection pooling is working

### Database Locked

**Problem**: `asyncpg.exceptions.LockNotAvailableError`

**Solution**:
- Tests are running in parallel with conflicting transactions
- Use unique company_ids per test
- Or run with `-n 1` to disable parallelism

### Connection Pool Exhausted

**Problem**: `asyncpg.exceptions.TooManyConnectionsError`

**Solution**:
- Reduce pool size in conftest.py
- Or increase max connections in Supabase

## Best Practices

1. **Use descriptive test names** - `test_create_fact_persists_to_database`
2. **Test one thing per test** - Don't test create and delete in same test
3. **Use factories for test data** - Don't manually create ORM objects
4. **Verify in database** - Query after operations to ensure persistence
5. **Clean up is automatic** - Trust the session rollback, don't manually clean
6. **Use unique identifiers** - Avoid conflicts between tests
7. **Document expected behavior** - Add docstrings explaining what you're testing

## CI/CD Testing

Tests run automatically on GitHub Actions:
- Triggered on push to main/develop
- Triggered on pull requests to main
- Uses real Supabase test database
- Runs type checking and linting

See `.github/workflows/test-supabase.yml` for configuration.

## Related Documentation

- [SETUP.md](SETUP.md) - Project setup guide
- [DATABASE.md](DATABASE.md) - Database schema documentation
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues and solutions
