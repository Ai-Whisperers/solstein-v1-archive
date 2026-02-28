# Solstein — Testing Guide

> Comprehensive guide to the Solstein test suite: structure, categories, patterns, and how to run tests.

---

## Overview

Solstein uses a **4-layer testing pyramid** with real Supabase PostgreSQL for database tests (no mocks in the test layer). This ensures tests verify actual behavior, not mock behavior.

| Layer | Location | Count | Purpose |
|-------|----------|-------|---------|
| Unit | `tests/unit/` | 80+ files | Domain models, scoring logic, repositories |
| Integration | `tests/integration/` | 15+ files | API endpoints, pipeline flows |
| Data Quality | `tests/data_quality/` | 3 files | Golden dataset regression |
| Performance | `tests/performance/` | 1 file | Load and throughput tests |
| **Total** | `tests/` | **1,434+ collected** | Full coverage |

**Philosophy**: Tests use real Supabase PostgreSQL. This ensures:
- Tests verify actual database behavior (FK constraints, query performance)
- No "mock drift" where tests pass but production fails
- Foreign key constraints are validated
- Query performance is realistic

---

## Test Structure

```
tests/
├── conftest.py                    # Root fixtures: db_session, db_engine, app client
├── factories.py                   # Test data factories
├── __init__.py
│
├── unit/                          # Fast, isolated tests
│   ├── __init__.py
│   ├── adapters/                  # Adapter unit tests
│   ├── agents/                    # Agent unit tests
│   ├── data/                      # Data layer unit tests
│   ├── research/                  # Research pipeline unit tests
│   │
│   ├── test_classification.py     # Company classification logic
│   ├── test_scoring.py            # Scoring engine
│   ├── test_models.py             # Domain model validation
│   ├── test_fact_repository.py    # FactRepository operations
│   ├── test_company_repository.py # CompanyRepository operations
│   ├── test_database.py           # Database connectivity
│   ├── test_database_service.py   # DatabaseService operations
│   ├── test_enrichment_repositories.py  # Enrichment repos
│   ├── test_repositories.py       # Repository layer
│   ├── test_repositories_comprehensive.py  # Extended repo tests
│   ├── test_scorers_growth.py     # Growth scorer
│   ├── test_scorers_financial.py  # Financial health scorer
│   ├── test_scorers_competitive.py # Competitive position scorer
│   ├── test_worker.py             # Celery worker tasks
│   ├── test_worker_tasks.py       # Worker task logic
│   ├── test_exporters.py          # Excel export
│   ├── test_extractors.py         # Data extractors
│   ├── test_loaders.py            # Data loaders
│   ├── test_cli.py                # CLI commands
│   └── ... (80+ test files total)
│
├── integration/                   # Multi-component tests
│   ├── __init__.py
│   ├── conftest.py                # Integration-specific fixtures
│   ├── test_api_endpoints.py      # All API endpoint contracts
│   ├── test_api_e2e.py            # End-to-end API flows
│   ├── test_full_pipeline.py      # Complete research pipeline
│   ├── test_repositories.py       # Repository integration
│   ├── test_data_migration.py     # Migration scripts
│   ├── test_enrichment_api.py     # Enrichment API
│   ├── test_connector_enrichment.py  # Connector + enrichment
│   ├── test_resilience_scenarios.py  # Error handling
│   ├── test_unified_adapters.py   # Adapter integration
│   └── ... (15+ test files total)
│
├── data_quality/                  # Regression tests
│   ├── __init__.py
│   ├── golden_dataset.py          # Golden dataset definitions
│   ├── test_golden_dataset_regression.py  # Classification regression
│   ├── test_eneve_consistency_validation.py  # Eneve market validation
│   └── test_ai_insights.py        # AI insight quality
│
└── performance/                   # Load tests
    └── test_load.py               # Throughput and latency tests
```

---

## Quick Start

### Run All Tests

```bash
# Full suite
pytest tests/ -v

# With coverage report
pytest tests/ --cov=src/solstein --cov-report=html

# Fast (skip slow tests)
pytest tests/ -m "not slow" -v
```

### Run by Category

```bash
# Unit tests only (fast)
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# Data quality / golden dataset
pytest tests/data_quality/ -v

# Performance tests
pytest tests/performance/ -v
```

### Run Specific Test File

```bash
pytest tests/unit/test_fact_repository.py -v
pytest tests/unit/test_scoring.py -v
pytest tests/integration/test_api_endpoints.py -v
```

### Run Specific Test

```bash
pytest tests/unit/test_fact_repository.py::TestFactRepository::test_create_fact -v
pytest tests/unit/test_scoring.py::TestScoringEngine::test_phoenix_classification -v
```

### Run with Coverage

```bash
# HTML report (opens in browser)
pytest tests/unit/ --cov=src/solstein --cov-report=html
open htmlcov/index.html

# Terminal report
pytest tests/unit/ --cov=src/solstein --cov-report=term-missing

# Minimum coverage gate
pytest tests/ --cov=src/solstein --cov-fail-under=75
```

---

## Test Fixtures

### Root Fixtures (`tests/conftest.py`)

#### `db_session`
Provides a fresh `AsyncSession` for each test. Automatically rolled back after each test — no manual cleanup needed.

```python
@pytest.mark.asyncio
async def test_something(db_session):
    # db_session is an AsyncSession
    result = await db_session.execute(select(Fact))
    facts = result.scalars().all()
    # Session is rolled back after test
```

#### `db_engine`
Provides the shared async engine (session-scoped). Use when you need raw connection access.

```python
async def test_with_engine(db_engine):
    async with db_engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        assert result.scalar() == 1
```

#### `client`
Provides a `TestClient` for FastAPI endpoint testing.

```python
def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

#### `async_client`
Provides an `AsyncClient` for async endpoint testing.

```python
@pytest.mark.asyncio
async def test_companies_endpoint(async_client):
    response = await async_client.get("/companies")
    assert response.status_code == 200
```

---

## Test Factories (`tests/factories.py`)

Factories create test data in the real database. Always use factories instead of manually constructing ORM objects.

### `create_test_company(session, company_id, **overrides)`

```python
from tests.factories import create_test_company

company = await create_test_company(
    db_session,
    company_id="test-001",
    name="Test Company",
    industry="energy_software",
    country="DE",
)
```

### `create_test_batch(session, company_id, **overrides)`

```python
from tests.factories import create_test_batch

batch = await create_test_batch(
    db_session,
    company_id="test-001",
    status="in_progress",  # optional override
)
```

### `create_test_fact(session, batch_id, company_id, **overrides)`

```python
from tests.factories import create_test_fact

fact = await create_test_fact(
    db_session,
    batch_id=str(batch.batch_id),
    company_id="test-001",
    fact_type="revenue",
    value=5_000_000.0,
    confidence=0.95,
    source="sec_edgar",
)
```

### `create_test_fact_source(session, fact_id, **overrides)`

```python
from tests.factories import create_test_fact_source

source = await create_test_fact_source(
    db_session,
    fact_id=str(fact.fact_id),
    source_type="sec_edgar",
    url="https://sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=...",
    title="10-K Annual Report 2024",
)
```

### `create_test_scoring_record(session, company_id, **overrides)`

```python
from tests.factories import create_test_scoring_record

scoring = await create_test_scoring_record(
    db_session,
    company_id="test-001",
    growth_score=7.5,
    financial_health_score=6.8,
    competitive_position_score=8.2,
    overall_score=7.5,
    classification="Phoenix",
)
```

---

## Writing Tests

### Unit Test Pattern

```python
import pytest
from sqlalchemy import select
from solstein.domain.facts import Fact
from tests.factories import create_test_batch, create_test_fact


@pytest.mark.asyncio
class TestFactRepository:
    """Tests for FactRepository using real Supabase database."""

    async def test_create_fact_persists_to_database(self, db_session):
        """Test that creating a fact persists it to the database."""
        # Arrange
        batch = await create_test_batch(db_session, "comp-test-001")

        # Act
        fact = await create_test_fact(
            db_session,
            batch_id=str(batch.batch_id),
            company_id="comp-test-001",
            fact_type="revenue",
            value=1_000_000.0,
            confidence=0.92,
        )

        # Assert — query database to verify persistence
        result = await db_session.execute(
            select(Fact).where(Fact.fact_id == fact.fact_id)
        )
        persisted = result.scalar_one()
        assert persisted.value == 1_000_000.0
        assert persisted.confidence == 0.92
        assert persisted.fact_type == "revenue"

    async def test_facts_filtered_by_type(self, db_session):
        """Test querying facts filtered by type."""
        batch = await create_test_batch(db_session, "comp-test-002")

        # Create facts of different types
        await create_test_fact(db_session, batch.batch_id, "comp-test-002",
                               fact_type="revenue", value=1_000_000)
        await create_test_fact(db_session, batch.batch_id, "comp-test-002",
                               fact_type="employees", value=500)

        # Query only revenue facts
        result = await db_session.execute(
            select(Fact).where(
                Fact.company_id == "comp-test-002",
                Fact.fact_type == "revenue",
            )
        )
        revenue_facts = result.scalars().all()

        assert len(revenue_facts) == 1
        assert revenue_facts[0].fact_type == "revenue"
```

### Integration Test Pattern

```python
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestCompanyEndpoints:
    """Integration tests for company API endpoints."""

    async def test_get_companies_returns_list(self, async_client: AsyncClient):
        """Test that GET /companies returns a list."""
        response = await async_client.get("/companies")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_get_company_by_id(self, async_client: AsyncClient, db_session):
        """Test that GET /companies/{id} returns the correct company."""
        from tests.factories import create_test_company
        company = await create_test_company(db_session, "api-test-001", name="API Test Co")

        response = await async_client.get(f"/companies/api-test-001")
        assert response.status_code == 200
        data = response.json()
        assert data["company_id"] == "api-test-001"
        assert data["name"] == "API Test Co"

    async def test_get_nonexistent_company_returns_404(self, async_client: AsyncClient):
        """Test that requesting a nonexistent company returns 404."""
        response = await async_client.get("/companies/does-not-exist-xyz")
        assert response.status_code == 404
```

### Testing FK Constraints

```python
async def test_fact_requires_valid_batch(self, db_session):
    """Test that facts require a valid batch_id (FK constraint)."""
    from sqlalchemy.exc import IntegrityError
    from solstein.domain.facts import Fact

    fact = Fact(
        company_id="comp-test-001",
        batch_id="00000000-0000-0000-0000-000000000000",  # Non-existent batch
        fact_type="test",
        value=100,
    )
    db_session.add(fact)

    with pytest.raises(IntegrityError):
        await db_session.commit()
```

### Testing CHECK Constraints

```python
async def test_confidence_must_be_between_0_and_1(self, db_session):
    """Test that confidence values outside [0, 1] are rejected."""
    from sqlalchemy.exc import IntegrityError
    from solstein.domain.facts import Fact

    batch = await create_test_batch(db_session, "comp-test-003")
    fact = Fact(
        company_id="comp-test-003",
        batch_id=batch.batch_id,
        fact_type="test",
        value=100,
        confidence=1.5,  # Invalid: > 1.0
    )
    db_session.add(fact)

    with pytest.raises(IntegrityError):
        await db_session.commit()
```

### Testing Scoring Logic

```python
import pytest
from solstein.analytics.scoring import ScoringEngine
from solstein.domain.models import Company


class TestScoringEngine:
    """Tests for the multi-dimensional scoring engine."""

    def test_phoenix_classification_at_threshold(self):
        """Test that score >= 7.0 produces Phoenix classification."""
        engine = ScoringEngine()
        result = engine.classify(overall_score=7.0)
        assert result == "Phoenix"

    def test_salt_classification_in_range(self):
        """Test that score in [4.0, 7.0) produces Salt classification."""
        engine = ScoringEngine()
        assert engine.classify(6.9) == "Salt"
        assert engine.classify(4.0) == "Salt"

    def test_lead_classification_below_threshold(self):
        """Test that score < 4.0 produces Lead classification."""
        engine = ScoringEngine()
        assert engine.classify(3.9) == "Lead"
        assert engine.classify(0.0) == "Lead"

    def test_score_is_deterministic(self):
        """Test that same inputs always produce same score."""
        engine = ScoringEngine()
        company = Company(company_id="test", name="Test Co")
        score1 = engine.score(company, facts=[])
        score2 = engine.score(company, facts=[])
        assert score1.overall_score == pytest.approx(score2.overall_score)
```

---

## Test Categories & Markers

Use markers to categorize and filter tests:

```python
@pytest.mark.asyncio    # Required for all async tests
@pytest.mark.db         # Database test (requires Supabase connection)
@pytest.mark.slow       # Slow test (> 5 seconds)
@pytest.mark.integration # Integration test
@pytest.mark.unit       # Unit test
```

### Running by Marker

```bash
# Only database tests
pytest -m db

# Skip slow tests
pytest -m "not slow"

# Only unit tests
pytest -m unit

# Integration tests only
pytest -m integration
```

### Marker Configuration (`pytest.ini`)

```ini
[pytest]
markers =
    asyncio: async test
    db: requires database connection
    slow: slow test (> 5 seconds)
    integration: integration test
    unit: unit test
```

---

## Data Quality Tests

### Golden Dataset Regression (`tests/data_quality/`)

The golden dataset protects classification boundaries. It contains known companies with expected classifications.

```python
# tests/data_quality/golden_dataset.py
GOLDEN_DATASET = [
    {
        "company_id": "eneve-001",
        "name": "Eneve Energy",
        "expected_classification": "Phoenix",
        "expected_score_min": 7.0,
    },
    {
        "company_id": "legacy-corp-001",
        "name": "Legacy Corp",
        "expected_classification": "Lead",
        "expected_score_max": 4.0,
    },
    # ... more companies
]
```

Running golden dataset tests:

```bash
pytest tests/data_quality/test_golden_dataset_regression.py -v
```

If a golden dataset test fails, it means a code change altered the scoring behavior for a known company. This is a **regression** — investigate before merging.

---

## Performance Tests

### Load Tests (`tests/performance/test_load.py`)

Performance tests verify throughput and latency targets.

```bash
# Run performance tests
pytest tests/performance/ -v -m "not slow"

# Run with timing output
pytest tests/performance/ -v --durations=10
```

**Performance Targets**:

| Operation | Target | Test |
|-----------|--------|------|
| Company lookup | <10ms | `test_company_lookup_latency` |
| Facts query | <50ms | `test_facts_query_latency` |
| Scoring insert | <20ms | `test_scoring_insert_latency` |
| Full pipeline (1 company) | <2s | `test_single_company_pipeline` |
| Batch scoring (10 companies) | <15s | `test_batch_scoring_throughput` |

---

## CI/CD Integration

Tests run automatically on GitHub Actions:

```yaml
# .github/workflows/test-supabase.yml
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -e ".[dev]"
      - run: pytest tests/ --cov=src/solstein --cov-fail-under=75
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL_TEST }}
```

**CI Requirements**:
- All tests must pass
- Coverage must be ≥ 75%
- No import errors
- Type checking passes (`mypy src/solstein`)
- Linting passes (`ruff check src/solstein`)

---

## Environment Setup for Tests

### Required Environment Variables

```bash
# .env.test
DATABASE_URL=postgresql+asyncpg://postgres:[password]@db.[project].supabase.co:5432/postgres?sslmode=require
DATABASE_URL_TEST=postgresql+asyncpg://...  # Separate test database recommended
```

### Connection Pool (Test Configuration)

Configured in `tests/conftest.py`:

```python
engine = create_async_engine(
    async_url,
    pool_size=5,        # Smaller pool for tests
    max_overflow=10,
    pool_recycle=3600,
    pool_pre_ping=True, # Verify connections before use
)
```

### Using a Separate Test Database

**Recommended**: Use a separate Supabase project for tests to avoid polluting production data.

```bash
# Run tests against test database
DATABASE_URL=$DATABASE_URL_TEST pytest tests/ -v

# Or set in .env.test and use:
pytest tests/ --env-file=.env.test -v
```

---

## Troubleshooting Tests

### Import Errors

**Problem**: `ImportError` or `ModuleNotFoundError` when collecting tests.

**Solution**:
```bash
# Verify package is installed in editable mode
pip install -e ".[dev]"

# Check PYTHONPATH
export PYTHONPATH=src:$PYTHONPATH
pytest tests/ -v
```

### Database Connection Failures

**Problem**: `asyncpg.exceptions.ConnectionDoesNotExistError` or similar.

**Solution**:
1. Verify `DATABASE_URL` is set correctly in `.env` or `.env.test`
2. Check Supabase project is active (not paused)
3. Verify SSL mode: `sslmode=require`
4. Test connection: `python -c "import asyncpg; import asyncio; asyncio.run(asyncpg.connect('$DATABASE_URL'))"`

### Database Locked / Lock Conflicts

**Problem**: `asyncpg.exceptions.LockNotAvailableError`

**Solution**:
- Tests are running in parallel with conflicting transactions
- Use unique `company_id` values per test (e.g., `f"test-{uuid4()}"`)
- Or run with `-n 1` to disable parallelism: `pytest tests/ -n 1`

### Connection Pool Exhausted

**Problem**: `asyncpg.exceptions.TooManyConnectionsError`

**Solution**:
- Reduce `pool_size` in `tests/conftest.py`
- Or increase max connections in Supabase dashboard
- Check for connection leaks (sessions not closed)

### Slow Tests

**Problem**: Tests taking too long.

**Solution**:
- Mark with `@pytest.mark.slow` and skip with `-m "not slow"`
- Check for N+1 queries (use `selectinload()` for relationships)
- Verify connection pooling is working
- Profile with `pytest --durations=20`

### Test Isolation Issues

**Problem**: Tests pass individually but fail when run together.

**Solution**:
- Each test should use unique identifiers (avoid shared `company_id` values)
- Trust the session rollback — don't manually commit in tests unless testing commit behavior
- Check for shared state in class-level fixtures

---

## Best Practices

### 1. Use Descriptive Test Names
```python
# ✅ Good
async def test_create_fact_with_high_confidence_persists_to_database(self, db_session):

# ❌ Bad
async def test_fact(self, db_session):
```

### 2. Test One Thing Per Test
```python
# ✅ Good — tests only creation
async def test_create_fact_persists_value(self, db_session):
    fact = await create_test_fact(db_session, ...)
    assert fact.value == 1_000_000.0

# ❌ Bad — tests creation AND deletion in same test
async def test_fact_lifecycle(self, db_session):
    fact = await create_test_fact(db_session, ...)
    assert fact.value == 1_000_000.0
    await db_session.delete(fact)
    # ...
```

### 3. Use Factories for Test Data
```python
# ✅ Good
batch = await create_test_batch(db_session, "comp-001")

# ❌ Bad — manually constructing ORM objects
batch = GatheringBatch(batch_id=uuid4(), company_id="comp-001", status="in_progress")
db_session.add(batch)
await db_session.commit()
```

### 4. Verify in Database After Operations
```python
# ✅ Good — queries database to verify
fact = await create_test_fact(db_session, ...)
result = await db_session.execute(select(Fact).where(Fact.fact_id == fact.fact_id))
persisted = result.scalar_one()
assert persisted.value == expected_value

# ❌ Bad — only checks return value
fact = await create_test_fact(db_session, ...)
assert fact.value == expected_value  # Doesn't verify DB persistence
```

### 5. Use Unique Identifiers
```python
# ✅ Good — unique per test
from uuid import uuid4
company_id = f"test-{uuid4()}"

# ❌ Bad — shared across tests, causes conflicts
company_id = "test-company-001"
```

### 6. Add Docstrings
```python
async def test_create_fact_with_invalid_confidence_raises_error(self, db_session):
    """
    Test that creating a fact with confidence > 1.0 raises IntegrityError.
    
    The facts table has a CHECK constraint: confidence BETWEEN 0 AND 1.
    """
```

---

## Coverage Report

Generate and view coverage:

```bash
# Generate HTML report
pytest tests/ --cov=src/solstein --cov-report=html
open htmlcov/index.html

# Generate XML (for CI)
pytest tests/ --cov=src/solstein --cov-report=xml

# Show missing lines in terminal
pytest tests/ --cov=src/solstein --cov-report=term-missing

# Enforce minimum coverage
pytest tests/ --cov=src/solstein --cov-fail-under=75
```

**Coverage Targets**:
| Module | Target |
|--------|--------|
| `src/solstein/domain/` | ≥ 90% |
| `src/solstein/analytics/` | ≥ 85% |
| `src/solstein/infrastructure/` | ≥ 80% |
| `src/solstein/api/` | ≥ 75% |
| **Overall** | **≥ 75%** |

---

## Related Documentation

- [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) — Complete schema reference
- [DATABASE.md](DATABASE.md) — Connection configuration and query patterns
- [PROFESSIONALIZATION.md](PROFESSIONALIZATION.md) — How the test suite was built
- [SETUP.md](SETUP.md) — Project setup guide
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — Common issues and solutions

---

*Testing guide updated: February 2026*  
*Built by AI Whisperers — finding the diamonds nobody knew were there.*
