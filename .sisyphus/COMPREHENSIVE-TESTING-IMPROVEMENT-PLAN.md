# Comprehensive Testing Improvement Plan
## Solstein Test Suite Modernization 2025-2026

**Version:** 1.0  
**Date:** February 28, 2026  
**Current Grade:** C-  
**Target Grade:** A  
**Estimated Effort:** 120-160 hours  
**Timeline:** 6-8 weeks

---

## Executive Summary

This plan transforms Solstein's testing framework from a C- grade (quantity without quality) to an A grade (fast, reliable, maintainable). Based on comprehensive analysis, we identified 8 critical issues and mapped a path to modern testing practices.

### Current State
- **1,096 tests** with 73% coverage
- **33% mocking density** (testing mocks, not code)
- **Broken test isolation** (tests pass individually, fail in suite)
- **Hybrid async/sync** (worst of both worlds)
- **114 database tests** failing (require real PostgreSQL)

### Target State
- **Fast test suite** (< 30 seconds for unit tests)
- **True test isolation** (pytest-randomly compatible)
- **Dependency injection** (minimal mocking)
- **Full async** (consistent throughout)
- **Testcontainers** (real databases in Docker)

---

## Phase 1: Foundation (Week 1-2) - 40 hours

### 1.1 Fix Test Isolation Crisis 🔴 CRITICAL

**Problem:** Tests modify `sys.modules` globally, causing pollution

**Current (Bad):**
```python
# test_worker_tasks.py - NUCLEAR OPTION
sys.modules['celery'] = MagicMock()
sys.modules['celery.exceptions'] = MagicMock()
# ... 20 more modules
```

**Target (Good):**
```python
# tests/conftest.py
@pytest.fixture
def celery_app():
    """Provide test Celery app without global mocking."""
    from celery import Celery
    app = Celery('test', broker='memory://')
    return app

# test_worker_tasks.py
def test_task(celery_app):
    task = MyTask.bind(celery_app)
    result = task.apply()
    assert result.successful()
```

**Tasks:**
- [ ] Remove all `sys.modules` manipulation (8 files)
- [ ] Create `tests/mocks/celery.py` with proper fixtures
- [ ] Add `pytest-randomly` to CI
- [ ] Verify tests pass in random order

**Effort:** 16 hours

---

### 1.2 Implement Dependency Injection 🔴 CRITICAL

**Problem:** 368 mocking occurrences due to tight coupling

**Current (Bad):**
```python
# connector uses global imports
from solstein.data.connectors.sec_edgar import SECEDGARConnector

def fetch_data():
    connector = SECEDGARConnector()  # Hard to test!
    return connector.fetch()
```

**Target (Good):**
```python
# connector accepts dependencies
def fetch_data(connector: DataConnector | None = None):
    connector = connector or SECEDGARConnector()
    return connector.fetch()

# Test with injection
def test_fetch_data():
    mock_connector = Mock(spec=DataConnector)
    mock_connector.fetch.return_value = []
    result = fetch_data(connector=mock_connector)
    assert result == []
```

**Tasks:**
- [ ] Create `src/solstein/core/ports.py` (interfaces)
- [ ] Refactor 12 connectors to accept dependencies
- [ ] Update 50+ tests to use injection
- [ ] Remove 200+ lines of mock setup

**Effort:** 24 hours

---

## Phase 2: Architecture (Week 3-4) - 40 hours

### 2.1 Standardize on Async 🟡 HIGH

**Problem:** Hybrid sync/async creates complexity with no benefit

**Current (Bad):**
```python
# activities.py - ASYNC WRAPPING SYNC
async def calculate_company_score(company_id: str):
    repo = await _get_repo()  # Async
    company = await asyncio.to_thread(repo.get_by_id, company_id)  # Sync in thread
    # ...
```

**Target (Good):**
```python
# activities.py - FULL ASYNC
async def calculate_company_score(company_id: str):
    async with db_manager.get_session() as session:
        repo = CompanyRepository(session)
        company = await repo.get_by_id(company_id)  # Truly async
        # ...
```

**Tasks:**
- [ ] Convert `src/solstein/data/` to async (20 files)
- [ ] Convert `src/solstein/analytics/` to async (5 files)
- [ ] Update repository pattern for async
- [ ] Remove all `asyncio.to_thread()` calls

**Effort:** 32 hours

---

### 2.2 Implement Testcontainers for Database Tests 🟡 HIGH

**Problem:** 114 tests require real PostgreSQL, failing in CI

**Current (Bad):**
```python
# Requires DATABASE_URL environment variable
async def test_repository_store(db_session):
    await repo.store(fact)  # Fails without real DB
```

**Target (Good):**
```python
# tests/conftest.py
from testcontainers.postgres import PostgresContainer

@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:15") as postgres:
        yield postgres

@pytest.fixture
async def db_session(postgres_container):
    url = postgres_container.get_connection_url()
    engine = create_async_engine(url)
    async with engine.begin() as conn:
        yield conn

# Test uses real PostgreSQL in Docker
async def test_repository_store(db_session):
    await repo.store(fact)  # Works in CI!
```

**Tasks:**
- [ ] Add `testcontainers[postgresql]` to dependencies
- [ ] Create `tests/conftest.py` with container fixtures
- [ ] Migrate 114 database tests
- [ ] Update CI to use Docker

**Effort:** 24 hours

---

## Phase 3: Quality (Week 5-6) - 40 hours

### 3.1 Consolidate Test Fixtures 🟡 MEDIUM

**Problem:** 100 fixtures, many undocumented, overlapping concerns

**Current (Bad):**
```python
# 100 fixtures scattered across files
@pytest.fixture
def mock_db_manager():
    return MagicMock(spec=DatabaseManager)

@pytest.fixture
def mock_task_self():
    mock = MagicMock()
    mock.retry = MagicMock(side_effect=MaxRetriesExceededError)
    mock.request = MagicMock()
    mock.request.retries = 0
    return mock
```

**Target (Good):**
```python
# tests/factories.py - Centralized factories
from factory import Factory, Faker

class CompanyFactory(Factory):
    class Meta:
        model = Company
    
    name = Faker('company')
    id = Faker('uuid4')

class MockTaskFactory:
    """Factory for Celery task mocks."""
    
    @staticmethod
    def create(retries=0, max_retries=3):
        mock = MagicMock()
        mock.request.retries = retries
        mock.retry.side_effect = MaxRetriesExceededError("Max retries")
        return mock

# tests/conftest.py - Documented fixtures
@pytest.fixture
def company_factory():
    """
    Returns CompanyFactory for creating test companies.
    
    Usage:
        def test_company(company_factory):
            company = company_factory(name="Test Corp")
            assert company.name == "Test Corp"
    """
    return CompanyFactory
```

**Tasks:**
- [ ] Install `factory-boy` for test data
- [ ] Create `tests/factories/` directory
- [ ] Consolidate 100 fixtures into 20 factories
- [ ] Document all fixtures with docstrings

**Effort:** 20 hours

---

### 3.2 Improve Assertion Quality 🟡 MEDIUM

**Problem:** 2,239 weak assertions, only 100 exception tests

**Current (Bad):**
```python
assert len(facts) >= 0  # Always true!
assert result is not None  # Weak
assert "classification" in result  # Doesn't check value
```

**Target (Good):**
```python
# Specific assertions
assert len(facts) == 5  # Exact count
assert result.growth_score == 8.25  # Exact value
assert result.classification == CompanyClassification.PHOENIX

# Exception testing with pytest.raises
with pytest.raises(ValueError, match="Company not found"):
    await service.get_company("invalid-id")

# Snapshot testing for complex objects
assert result.to_dict() == snapshot  # Using syrupy
```

**Tasks:**
- [ ] Add `syrupy` for snapshot testing
- [ ] Replace 500+ weak assertions
- [ ] Add 200+ exception tests
- [ ] Use `pytest-assume` for multiple assertions

**Effort:** 20 hours

---

## Phase 4: Modernization (Week 7-8) - 40 hours

### 4.1 Add Property-Based Testing 🟢 NICE TO HAVE

**Problem:** Only testing expected cases, missing edge cases

**Target:**
```python
# tests/property/test_company_logic.py
from hypothesis import given, strategies as st

@given(st.lists(st.integers(min_value=0), min_size=1))
def test_revenue_calculation_preserves_total(revenues):
    """Revenue calculation should preserve total."""
    total = sum(revenues)
    company = Company(revenue_timeline=[{"eur_millions": r} for r in revenues])
    assert abs(company.total_revenue - total) < 0.01

@given(st.text(), st.text())
def test_company_merge_preserves_ids(id1, id2):
    """Merging companies should include both IDs."""
    c1 = Company(id=id1)
    c2 = Company(id=id2)
    merged = merge_companies([c1, c2])
    assert id1 in merged.source_ids
    assert id2 in merged.source_ids
```

**Tasks:**
- [ ] Install `hypothesis`
- [ ] Create `tests/property/` directory
- [ ] Write 20 property-based tests
- [ ] Integrate with CI

**Effort:** 16 hours

---

### 4.2 Implement Visual Regression Testing 🟢 NICE TO HAVE

**Problem:** No testing of Excel exports, reports

**Target:**
```python
# tests/visual/test_exports.py
from playwright.sync_api import sync_playwright

def test_excel_export_structure(snapshot):
    exporter = ExcelExporter()
    file_path = exporter.export_companies(companies)
    
    # Compare structure
    df = pd.read_excel(file_path)
    assert df.columns.tolist() == snapshot
```

**Tasks:**
- [ ] Install `playwright`
- [ ] Create visual regression tests
- [ ] Add to CI with artifact storage

**Effort:** 12 hours

---

### 4.3 Performance Testing 🟢 NICE TO HAVE

**Target:**
```python
# tests/performance/test_load.py
import pytest
from pytest_benchmark.fixture import BenchmarkFixture

def test_company_scoring_performance(benchmark: BenchmarkFixture):
    """Company scoring should complete in < 100ms."""
    company = create_large_company()
    result = benchmark(scorer.calculate_scores, company)
    assert result.stats.mean < 0.1  # 100ms
```

**Tasks:**
- [ ] Install `pytest-benchmark`
- [ ] Add performance tests
- [ ] Set performance budgets

**Effort:** 12 hours

---

## New Tools & Frameworks to Adopt

### Essential (Must Have)

| Tool | Purpose | Current Replacement |
|------|---------|-------------------|
| **pytest-randomly** | Test isolation verification | None (broken isolation) |
| **testcontainers** | Real databases in Docker | Manual PostgreSQL setup |
| **factory-boy** | Test data generation | Manual MagicMock setup |
| **syrupy** | Snapshot testing | Manual dict comparison |
| **pytest-asyncio** | Async test support | Partial/inconsistent |

### Recommended (Should Have)

| Tool | Purpose | Benefit |
|------|---------|---------|
| **hypothesis** | Property-based testing | Catch edge cases |
| **pytest-benchmark** | Performance testing | Prevent regressions |
| **pytest-xdist** | Parallel test execution | Faster CI |
| **coverage[toml]** | Coverage reporting | Better metrics |
| **mutmut** | Mutation testing | Verify test quality |

### Optional (Nice to Have)

| Tool | Purpose | Use Case |
|------|---------|----------|
| **playwright** | Visual regression | Excel export testing |
| **vcr.py** | HTTP request recording | External API testing |
| **freezegun** | Time manipulation | Date-based logic testing |
| **responses** | HTTP mocking | Cleaner API mocking |

---

## Migration Strategy

### Step 1: Parallel Implementation (Week 1-2)
- Keep existing tests running
- Create new test structure alongside
- Gradually migrate tests

### Step 2: Feature Flags (Week 3-4)
- Use `pytest.mark.new` for new tests
- Run old and new tests in parallel
- Compare results

### Step 3: Gradual Replacement (Week 5-8)
- Migrate 10% of tests per week
- Delete old tests after verification
- Monitor coverage

### Step 4: Cleanup (Week 9)
- Remove deprecated test files
- Archive old conftest.py
- Final verification

---

## CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: &gt;-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt
          pip install pytest-randomly testcontainers factory-boy syrupy
      
      - name: Run tests with randomization
        run: |
          pytest tests/unit -v --randomly-seed=1234
      
      - name: Run tests with testcontainers
        run: |
          pytest tests/integration -v
      
      - name: Mutation testing
        run: |
          mutmut run --paths-to-mutate=src/solstein
          mutmut results
```

---

## Success Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| **Test Suite Runtime** | 120s | < 30s | pytest --durations=0 |
| **Test Isolation** | Broken | 100% | pytest-randomly |
| **Mocking Density** | 33% | < 10% | Code review |
| **Coverage** | 73% | 85% | pytest-cov |
| **Flaky Tests** | 35 | 0 | CI monitoring |
| **Test Documentation** | 10% | 90% | Docstring coverage |
| **Mutation Score** | Unknown | > 70% | mutmut |

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing tests | High | Parallel implementation, feature flags |
| Time overrun | Medium | Prioritize Phase 1-2, defer Phase 4 |
| Team resistance | Medium | Demonstrate benefits, pair programming |
| CI slowdown | Low | Parallel test execution, caching |
| Database migration | Medium | Testcontainers handles schema |

---

## Conclusion

This plan transforms Solstein's testing from a liability to an asset. The investment of 120-160 hours pays dividends in:

- **Developer velocity** (faster test feedback)
- **Code confidence** (tests that actually work)
- **Maintenance ease** (clear patterns, documentation)
- **CI reliability** (no more flaky tests)

**Start with Phase 1.1 (Test Isolation) - it's the foundation everything else builds on.**

---

*"The only way to go fast is to go well."* - Robert C. Martin
