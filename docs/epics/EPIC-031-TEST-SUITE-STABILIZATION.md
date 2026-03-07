# EPIC-031: Test Suite Stabilization

**Status:** 🔴 Not Started  
**Priority:** CRITICAL (P0)  
**Story Points:** 34  
**Sprint Allocation:** 2 sprints  
**Target Date:** Week 2

---

## Problem Statement

The test suite is not passing. Unit tests fail, preventing verification of code correctness and blocking CI/CD pipeline.

### Impact
- Cannot verify changes are correct
- No confidence in refactoring
- CI/CD pipeline blocked
- Development velocity slowed

---

## Success Criteria

1. ✅ 100% of unit tests pass
2. ✅ 100% of integration tests pass
3. ✅ Test execution time <5 minutes
4. ✅ No flaky tests
5. ✅ Coverage maintained >80%

---

## Technical Analysis

### Current State
```
Unit tests: FAILING
Test count: 2,758+
Execution time: Unknown (fails early)
Coverage: Unknown
```

### Common Issues to Check
1. **Import errors** - Missing dependencies or circular imports
2. **Database connectivity** - Tests can't connect to test DB
3. **Async/await mismatches** - Missing pytest-asyncio markers
4. **Fixtures not found** - Missing conftest.py configurations
5. **Environment variables** - Missing required env vars in test environment
6. **File paths** - Tests using relative paths that don't exist in CI

---

## Stories

### Story 1.1: Fix Unit Test Imports (5 pts)
**Task:** Fix all import errors in unit tests

**Acceptance Criteria:**
- [ ] All unit tests can import their dependencies
- [ ] No circular import errors
- [ ] Mock external services properly

**Implementation:**
```bash
# Run and fix import errors one by one
python -m pytest tests/unit -v --tb=short 2>&1 | grep "ImportError"
```

---

### Story 1.2: Fix Database Connection in Tests (8 pts)
**Task:** Configure test database connectivity

**Acceptance Criteria:**
- [ ] Tests use test database (not production)
- [ ] Database migrations run before tests
- [ ] Test data is isolated/cleaned up
- [ ] Connection pooling works in test environment

**Implementation:**
```python
# conftest.py
@pytest.fixture(scope="session")
async def test_db():
    # Use test database URL
    settings.database.url = "postgresql://localhost/solstein_test"
    await init_db()
    yield
    await drop_db()
```

---

### Story 1.3: Fix Async Test Markers (5 pts)
**Task:** Add proper async test markers

**Acceptance Criteria:**
- [ ] All async tests have @pytest.mark.asyncio
- [ ] Event loop fixture configured properly
- [ ] No "async def" test warnings

**Implementation:**
```python
# conftest.py
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Individual tests
@pytest.mark.asyncio
async def test_async_function():
    result = await async_call()
    assert result is not None
```

---

### Story 1.4: Fix Missing Fixtures (8 pts)
**Task:** Create/fix all required test fixtures

**Acceptance Criteria:**
- [ ] db_session fixture works
- [ ] test_client fixture works
- [ ] mock_llm fixture works
- [ ] All factories work
- [ ] No "fixture not found" errors

**Implementation:**
```python
# conftest.py
@pytest.fixture
async def db_session(test_db):
    async with async_session() as session:
        yield session
        await session.rollback()

@pytest.fixture
def test_client():
    from solstein.api.main import app
    from httpx import AsyncClient
    return AsyncClient(app=app, base_url="http://test")
```

---

### Story 1.5: Fix Environment Configuration (5 pts)
**Task:** Configure test environment variables

**Acceptance Criteria:**
- [ ] .env.test file created
- [ ] All required env vars documented
- [ ] CI environment configured
- [ ] No "missing environment variable" errors

**Implementation:**
```bash
# .env.test
DATABASE__URL=postgresql://localhost/solstein_test
REDIS__URL=redis://localhost:6379/1
JWT__SECRET=test-secret-do-not-use-in-production
LLM__DEFAULT_PROVIDER=ollama
TESTING=true
```

---

### Story 1.6: Eliminate Flaky Tests (3 pts)
**Task:** Identify and fix flaky tests

**Acceptance Criteria:**
- [ ] All tests pass 5 times in a row
- [ ] No timing-dependent failures
- [ ] No race conditions in tests
- [ ] Deterministic test data

**Implementation:**
```python
# Use deterministic UUIDs for tests
@pytest.fixture
def deterministic_uuids():
    return DeterministicUUID(seed=42)

# Avoid time.sleep in tests
# Use condition-based waiting instead
```

---

## Test Execution Plan

### Phase 1: Core Unit Tests (Week 1)
1. Fix import errors
2. Fix database connections
3. Fix async markers
4. Run core domain tests

### Phase 2: Integration Tests (Week 2)
1. Fix API router tests
2. Fix enrichment tests
3. Fix database integration
4. Run full test suite

---

## Definition of Done

- [ ] `pytest tests/unit` passes 100%
- [ ] `pytest tests/integration` passes 100%
- [ ] CI/CD pipeline green
- [ ] Coverage report generated
- [ ] No warnings in test output
- [ ] Test execution time <5 minutes
- [ ] All flaky tests eliminated

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Circular imports | Medium | High | Refactor to avoid cycles |
| Missing test data | Medium | Medium | Create factories |
| External service deps | High | Medium | Mock all externals |

---

## Resources

- **Developers:** 2 backend engineers
- **Time:** 2 weeks
- **Dependencies:** None (blocking other work)

---

*Epic created as part of Comprehensive Analysis*
