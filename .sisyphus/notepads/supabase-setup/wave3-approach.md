# Wave 3: Test Rewrite Approach (Tasks 9-12)

## Overview
Convert 4 test files from sync/mock to async/real database:
1. test_fact_repository.py
2. test_database.py
3. test_database_service.py
4. test_enrichment_repositories.py

## Key Changes Required

### 1. Async Conversion
- Change `def test_*` → `async def test_*`
- Add `@pytest.mark.asyncio` decorator
- Change `session.execute()` → `await session.execute()`
- Change `session.commit()` → `await session.commit()`

### 2. Fixture Usage
- Remove local `db_engine` and `db_session` fixtures (use conftest.py)
- Use `db_session` fixture from conftest.py (AsyncSession)
- Use `cleanup_test_database()` from test_cleanup.py

### 3. Factory Usage
- Replace manual object creation with factories
- Use `create_test_batch()`, `create_test_fact()`, etc.
- These return persisted ORM instances

### 4. Query Patterns
- Use SQLAlchemy async patterns: `await session.execute(select(...))`
- Use `scalar_one()`, `scalar_one_or_none()` for results
- Verify data persisted in database (not just return values)

### 5. Error Testing
- Test FK constraint violations (IntegrityError)
- Test validation errors
- Test cascade deletes

## Test File Breakdown

### test_fact_repository.py (11 KB, ~286 lines)
- Tests FactRepository CRUD operations
- Needs: async conversion, factory usage, real DB queries
- Key tests: create, read, update, delete, list

### test_database.py (3.6 KB, ~100 lines)
- Tests database connection and basic operations
- Needs: async conversion, fixture cleanup
- Key tests: connection, table existence, basic CRUD

### test_database_service.py (5.7 KB, ~150 lines)
- Tests DatabaseService layer
- Needs: async conversion, factory usage
- Key tests: service methods, error handling

### test_enrichment_repositories.py (4.9 KB, ~130 lines)
- Tests enrichment repository operations
- Needs: async conversion, factory usage
- Key tests: enrichment CRUD, data validation

## Execution Strategy

### Phase 1: Preparation
- ✅ Create conftest.py with db_session fixture
- ✅ Create test_cleanup.py with cleanup functions
- ✅ Create factories.py with database factories
- ✅ Create pytest.ini with asyncio_mode=auto

### Phase 2: Rewrite (Tasks 9-12)
- Task 9: test_fact_repository.py
- Task 10: test_database.py
- Task 11: test_database_service.py
- Task 12: test_enrichment_repositories.py

Each task:
1. Convert to async (add @pytest.mark.asyncio, async def)
2. Replace fixtures (use conftest.py db_session)
3. Replace factories (use create_test_* functions)
4. Replace queries (use await session.execute(select(...)))
5. Add real DB verification (query after operation)
6. Test error conditions (FK violations, etc.)

### Phase 3: Verification
- Run all 4 test files: `pytest tests/unit/test_fact_repository.py tests/unit/test_database.py tests/unit/test_database_service.py tests/unit/test_enrichment_repositories.py -v`
- Verify all tests pass with real Supabase
- Check coverage (target: 80%+)

## Common Patterns

### Before (Sync/Mock)
```python
def test_create_fact(db_session):
    company = Company(id="test-123", name="Test")
    db_session.add(company)
    db_session.commit()
    
    fact = Fact(company_id="test-123", batch_id="batch-123")
    db_session.add(fact)
    db_session.commit()
    
    assert fact.id is not None
```

### After (Async/Real)
```python
@pytest.mark.asyncio
async def test_create_fact(db_session):
    # Use factories
    batch = await create_test_batch(db_session, "company-123")
    
    # Create via repository
    repo = FactRepository(db_session)
    fact = await repo.create(batch_id=batch.batch_id, ...)
    
    # Verify in database
    result = await db_session.execute(
        select(Fact).where(Fact.fact_id == fact.fact_id)
    )
    persisted = result.scalar_one()
    assert persisted.batch_id == batch.batch_id
```

## Dependencies

### Already Available
- ✅ conftest.py with db_session fixture
- ✅ test_cleanup.py with cleanup functions
- ✅ factories.py with create_test_* functions
- ✅ pytest.ini with asyncio_mode=auto
- ✅ database_config.py with URL loading

### Required Imports
```python
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from solstein.domain.facts import Fact, GatheringBatch, FactSource
from solstein.infrastructure.repositories import FactRepository
from tests.factories import create_test_batch, create_test_fact
from solstein.infrastructure.test_cleanup import cleanup_test_database
```

## Success Criteria

- [ ] All 4 test files converted to async
- [ ] All tests use db_session fixture from conftest.py
- [ ] All tests use factories from factories.py
- [ ] All tests verify data in real database
- [ ] All tests pass with real Supabase connection
- [ ] No mock objects (all real ORM instances)
- [ ] Error conditions tested (FK violations, etc.)
- [ ] Coverage: 80%+ on database layer

## Estimated Effort

- Task 9 (test_fact_repository.py): 1-2 hours
- Task 10 (test_database.py): 30-45 minutes
- Task 11 (test_database_service.py): 1-1.5 hours
- Task 12 (test_enrichment_repositories.py): 1-1.5 hours

**Total: 4-5.5 hours**

## Notes

- All tests should be independent (no shared state)
- Each test gets fresh db_session (function-scoped fixture)
- Cleanup happens automatically via fixture
- No need for manual cleanup in tests
- Use @pytest.mark.db for database tests (optional, for filtering)
