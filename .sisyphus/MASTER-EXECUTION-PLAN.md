# Master Execution Plan: Complete Testing Overhaul
## Solstein Test Suite Transformation

**Version:** 2.0  
**Date:** February 28, 2026  
**Status:** IN PROGRESS  
**Estimated Duration:** 3-4 weeks full-time  
**Current:** 1,030 tests passing, 39 failing, 114 DB errors  
**Target:** 1,200+ tests passing, 0 failing, 85%+ coverage

---

## Executive Summary

This is the **complete, actionable plan** to transform Solstein's testing from C- to A grade. Every task is broken down with exact commands, file paths, and verification steps.

**Current Grade:** C- (1,030 passing, broken isolation, 33% mocking)  
**Target Grade:** A (1,200+ passing, true isolation, <10% mocking)

---

## Phase 1: Critical Fixes (Days 1-3) - 24 hours

### 1.1 Fix All Syntax Errors 🔴 CRITICAL

**Files to fix:**
- [x] `src/solstein/api/middleware/rate_limit.py` - Extra quotes (DONE)
- [ ] Check all Python files for syntax errors

**Commands:**
```bash
# Find all syntax errors
find src tests -name "*.py" -type f -exec python3 -m py_compile {} \; 2>&1 | grep "SyntaxError"

# Fix any found errors
```

**Verification:**
```bash
python3 -c "import solstein"  # Should not raise SyntaxError
```

### 1.2 Standardize Imports 🔴 CRITICAL

**Problem:** Inconsistent import patterns across codebase

**Tasks:**
- [ ] Standardize all imports to use absolute imports
- [ ] Remove circular dependencies
- [ ] Create `__init__.py` files where missing

**Files to check:**
```bash
grep -r "from \. import\|from \.\." src/ --include="*.py" | head -20
```

### 1.3 Create Testing Infrastructure 🔴 CRITICAL

**Create directories:**
```bash
mkdir -p tests/factories
mkdir -p tests/fixtures
mkdir -p tests/mocks
mkdir -p tests/integration
```

**Create base files:**
- [ ] `tests/factories/__init__.py` - Factory Boy factories
- [ ] `tests/fixtures/__init__.py` - Shared pytest fixtures
- [ ] `tests/mocks/__init__.py` - Mock utilities
- [ ] `tests/conftest.py` - Updated with new fixtures

---

## Phase 2: Architecture Refactoring (Days 4-10) - 56 hours

### 2.1 Implement Dependency Injection 🔴 CRITICAL

**Goal:** Remove 368 mocking occurrences by 80%

**Step 1: Create Ports (Interfaces)**

Create `src/solstein/core/ports.py`:
```python
"""Dependency injection ports (interfaces)."""

from abc import ABC, abstractmethod
from typing import Any, Protocol


class DataConnector(Protocol):
    """Protocol for data connectors."""
    
    async def fetch_facts(self, company_ids: list[str]) -> list[dict]:
        ...


class CompanyRepository(Protocol):
    """Protocol for company repositories."""
    
    async def get_by_id(self, company_id: str) -> Any:
        ...
    
    async def save(self, company: Any) -> Any:
        ...
```

**Step 2: Refactor Worker Tasks**

Refactor `src/solstein/worker_tasks.py`:

Current (BAD):
```python
from solstein.infrastructure.connectors.sec_edgar_refresh import SECEDGARRefreshConnector

@shared_task
def refresh_sec_edgar(self):
    connector = SECEDGARRefreshConnector()  # Hard to test!
    ...
```

Target (GOOD):
```python
from typing import Optional
from solstein.core.ports import DataConnector

@shared_task(bind=True)
def refresh_sec_edgar(
    self,
    connector: Optional[DataConnector] = None
):
    """Refresh SEC EDGAR data.
    
    Args:
        connector: DataConnector instance. If None, uses SECEDGARRefreshConnector.
    """
    connector = connector or SECEDGARRefreshConnector()
    ...
```

**Step 3: Update All Connector Tests**

Update all 12 connector test files to use dependency injection:
- [ ] `test_sec_edgar_refresh.py`
- [ ] `test_companies_house_refresh.py`
- [ ] `test_news_signal_refresh.py`
- [ ] etc.

**Verification:**
```bash
# Count mocking occurrences (should decrease)
grep -r "MagicMock\|@patch" tests/unit/ | wc -l
# Target: < 100 (from 368)
```

### 2.2 Standardize Async/Sync 🟡 HIGH

**Goal:** Convert all I/O operations to async

**Files to convert:**

Priority 1 (Core data layer):
- [ ] `src/solstein/data/loaders.py`
- [ ] `src/solstein/data/unified_loader.py`
- [ ] `src/solstein/data/connectors/*.py` (12 files)

Priority 2 (Analytics):
- [ ] `src/solstein/analytics/activities.py`
- [ ] `src/solstein/analytics/scoring.py`

Priority 3 (Repositories):
- [ ] `src/solstein/infrastructure/repositories.py`
- [ ] `src/solstein/infrastructure/company_repository.py`

**Pattern:**

Current (SYNC):
```python
def load_companies(self) -> list[Company]:
    with open(self.file_path) as f:
        data = json.load(f)
    return [self._convert(c) for c in data]
```

Target (ASYNC):
```python
async def load_companies(self) -> list[Company]:
    async with aiofiles.open(self.file_path) as f:
        content = await f.read()
        data = json.loads(content)
    return [self._convert(c) for c in data]
```

**Dependencies to add:**
```bash
uv add aiofiles
```

### 2.3 Fix Test Isolation 🟡 HIGH

**Goal:** Remove all sys.modules manipulation

**Files to fix:**
- [ ] `tests/unit/test_worker_tasks.py` - COMPLETE REWRITE
- [ ] `tests/unit/test_celery_config.py` - COMPLETE REWRITE
- [ ] Any other files with `sys.modules` manipulation

**New pattern for test_worker_tasks.py:**

```python
"""Tests for Celery worker tasks using dependency injection."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from solstein.worker_tasks import refresh_sec_edgar
from solstein.core.ports import DataConnector


class TestRefreshTasks:
    """Test suite using dependency injection (no sys.modules hacking)."""

    @pytest.fixture
    def mock_connector(self):
        """Provide a mock DataConnector."""
        connector = MagicMock(spec=DataConnector)
        connector.fetch_facts = AsyncMock(return_value=[])
        return connector

    @pytest.fixture
    def mock_task(self):
        """Provide a mock Celery task."""
        task = MagicMock()
        task.request.retries = 0
        return task

    @pytest.mark.asyncio
    async def test_refresh_sec_edgar_success(self, mock_task, mock_connector):
        """Test successful refresh using dependency injection."""
        result = await refresh_sec_edgar(mock_task, connector=mock_connector)
        
        assert result["status"] == "completed"
        mock_connector.fetch_facts.assert_called_once()
```

**Verification:**
```bash
# Install pytest-randomly
uv add --dev pytest-randomly

# Run tests in random order
pytest tests/unit/test_worker_tasks.py --randomly-seed=1234 -v
# Should pass consistently
```

---

## Phase 3: Test Modernization (Days 11-17) - 56 hours

### 3.1 Implement Factory Boy 🟡 HIGH

**Create `tests/factories/company.py`:**

```python
"""Factory Boy factories for creating test data."""

import factory
from factory import Faker
from solstein.domain.models import Company, CompanyTier, AIMaturity


class CompanyFactory(factory.Factory):
    """Factory for creating Company instances."""
    
    class Meta:
        model = Company
    
    id = factory.Sequence(lambda n: f"comp_{n:03d}")
    name = Faker('company')
    industry = Faker('bs')
    description = Faker('catch_phrase')
    website = Faker('url')
    founded_year = Faker('year')
    tier = factory.Iterator(CompanyTier)
    ai_maturity = factory.Iterator(AIMaturity)
    
    @factory.post_generation
    def set_defaults(obj, create, extracted, **kwargs):
        """Set default values after creation."""
        if not obj.geographic_presence:
            obj.geographic_presence = ["Germany", "France"]
```

**Create `tests/factories/__init__.py`:**

```python
"""Test data factories."""

from .company import CompanyFactory

__all__ = ['CompanyFactory']
```

**Update tests to use factories:**

Current (BAD):
```python
def test_company():
    company = Company(
        id="test_001",
        name="Test Corp",
        industry="Software",
        # ... 20 more fields
    )
```

Target (GOOD):
```python
def test_company():
    company = CompanyFactory()
    # Or with specific values:
    company = CompanyFactory(name="Test Corp", tier=CompanyTier.TIER_1)
```

**Update 50+ test files to use factories**

### 3.2 Implement Snapshot Testing 🟡 HIGH

**Install syrupy:**
```bash
uv add --dev syrupy
```

**Create snapshot tests:**

```python
# tests/snapshots/test_company_scoring.py
import pytest
from syrupy import snapshot


def test_company_scoring_result(snapshot):
    """Test that company scoring produces consistent results."""
    company = CompanyFactory()
    scorer = GrowthScorer()
    result = scorer.calculate_scores(company)
    
    assert result.to_dict() == snapshot
```

**Update 100+ assertions to use snapshots**

### 3.3 Improve Assertion Quality 🟡 HIGH

**Replace weak assertions:**

Current (WEAK):
```python
assert len(facts) >= 0
assert result is not None
assert "classification" in result
```

Target (STRONG):
```python
assert len(facts) == 5
assert result.growth_score == 8.25
assert result.classification == CompanyClassification.PHOENIX
```

**Add exception testing:**

```python
with pytest.raises(ValueError, match="Company not found"):
    await service.get_company("invalid-id")
```

**Target: Replace 500+ weak assertions**

---

## Phase 4: Infrastructure (Days 18-21) - 32 hours

### 4.1 Implement Testcontainers 🔴 CRITICAL

**Install testcontainers:**
```bash
uv add --dev testcontainers[postgresql]
```

**Create `tests/conftest.py`:**

```python
"""Shared pytest fixtures."""

import pytest
from testcontainers.postgres import PostgresContainer
from sqlalchemy.ext.asyncio import create_async_engine


@pytest.fixture(scope="session")
def postgres_container():
    """Provide PostgreSQL container for integration tests."""
    with PostgresContainer("postgres:15") as postgres:
        yield postgres


@pytest.fixture
async def db_engine(postgres_container):
    """Provide async database engine."""
    url = postgres_container.get_connection_url()
    engine = create_async_engine(url)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine):
    """Provide database session."""
    from solstein.infrastructure.database import DatabaseManager
    
    manager = DatabaseManager()
    manager.engine = db_engine
    
    async with manager.get_session() as session:
        yield session
```

**Update 114 database tests to use testcontainers**

### 4.2 Update CI/CD Pipeline 🔴 CRITICAL

**Create `.github/workflows/test.yml`:**

```yaml
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
        options: >-
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
      
      - name: Install uv
        run: pip install uv
      
      - name: Install dependencies
        run: uv sync
      
      - name: Run tests with randomization
        run: |
          uv run pytest tests/unit -v --randomly-seed=1234
      
      - name: Run tests with coverage
        run: |
          uv run pytest tests/unit --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

### 4.3 Add Performance Testing 🟢 NICE TO HAVE

**Install pytest-benchmark:**
```bash
uv add --dev pytest-benchmark
```

**Create performance tests:**

```python
# tests/performance/test_scoring.py
import pytest


def test_company_scoring_performance(benchmark):
    """Benchmark company scoring performance."""
    from tests.factories import CompanyFactory
    from solstein.analytics.scoring import GrowthScorer
    
    company = CompanyFactory()
    scorer = GrowthScorer()
    
    result = benchmark(scorer.calculate_scores, company)
    assert result.stats.mean < 0.1  # 100ms max
```

---

## Phase 5: Final Verification (Days 22-24) - 24 hours

### 5.1 Run Full Test Suite 🔴 CRITICAL

```bash
# Run all tests
uv run pytest tests/ -v --tb=short

# Run with randomization
uv run pytest tests/ --randomly-seed=1234

# Run with coverage
uv run pytest tests/ --cov=src --cov-report=html
```

### 5.2 Verify Metrics 🔴 CRITICAL

**Check all metrics:**

```bash
# Test count
echo "Test count:"
uv run pytest tests/ --collect-only -q | wc -l

# Coverage
echo "Coverage:"
uv run pytest tests/ --cov=src --cov-report=term | grep "TOTAL"

# Mocking density
echo "Mocking occurrences:"
grep -r "MagicMock\|@patch" tests/ | wc -l

# Test runtime
echo "Test runtime:"
time uv run pytest tests/unit -q
```

### 5.3 Create Final Report 🔴 CRITICAL

**Create `TESTING-TRANSFORMATION-REPORT.md`:**

```markdown
# Testing Transformation Report

## Before
- Tests: 1,030 passing
- Failures: 39
- Coverage: 73%
- Mocking: 33%
- Grade: C-

## After
- Tests: 1,200+ passing
- Failures: 0
- Coverage: 85%
- Mocking: <10%
- Grade: A

## Changes Made
- [List all changes]

## New Tools
- pytest-randomly
- testcontainers
- factory-boy
- syrupy
- pytest-benchmark

## Lessons Learned
- [Document insights]
```

---

## Daily Execution Schedule

### Week 1: Foundation
- **Day 1:** Fix syntax errors, create infrastructure
- **Day 2:** Implement dependency injection (ports)
- **Day 3:** Refactor worker tasks
- **Day 4:** Continue DI refactoring
- **Day 5:** Fix test isolation (sys.modules)

### Week 2: Architecture
- **Day 6:** Convert data layer to async
- **Day 7:** Convert analytics to async
- **Day 8:** Convert repositories to async
- **Day 9:** Fix remaining async issues
- **Day 10:** Mid-point verification

### Week 3: Modernization
- **Day 11:** Implement Factory Boy
- **Day 12:** Update tests to use factories
- **Day 13:** Implement snapshot testing
- **Day 14:** Improve assertions
- **Day 15:** Continue assertion improvements

### Week 4: Infrastructure
- **Day 16:** Implement testcontainers
- **Day 17:** Update database tests
- **Day 18:** Update CI/CD
- **Day 19:** Add performance tests
- **Day 20:** Final fixes

### Week 5: Verification
- **Day 21:** Run full test suite
- **Day 22:** Fix any remaining issues
- **Day 23:** Create documentation
- **Day 24:** Final review and handoff

---

## Verification Checklist

- [ ] All syntax errors fixed
- [ ] No sys.modules manipulation remaining
- [ ] All tests pass with pytest-randomly
- [ ] Coverage >= 85%
- [ ] Mocking density < 10%
- [ ] Test runtime < 30 seconds
- [ ] All database tests use testcontainers
- [ ] CI/CD pipeline updated
- [ ] Documentation complete
- [ ] Grade: A achieved

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Time overrun | Prioritize Phase 1-2, defer Phase 4 if needed |
| Breaking changes | Maintain backward compatibility during transition |
| Team resistance | Pair programming, demonstrate benefits |
| CI slowdown | Parallel execution, caching |

---

## Success Criteria

**Must Have:**
- [ ] 1,200+ tests passing
- [ ] 0 test failures
- [ ] 85%+ coverage
- [ ] <10% mocking
- [ ] <30s test runtime

**Should Have:**
- [ ] Property-based testing
- [ ] Performance benchmarks
- [ ] Visual regression tests

**Nice to Have:**
- [ ] Mutation testing
- [ ] Fuzzing
- [ ] Chaos engineering

---

**Let's execute this plan systematically.**
