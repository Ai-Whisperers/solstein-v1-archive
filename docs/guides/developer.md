
# 📜 Developer Guide

**Setting Up, Contributing, and Understanding the Codebase**

**Phase**: 1-13 (Production-Ready)  
**Last Updated**: February 26, 2026
# 📜 Developer Guide

**Setting Up, Contributing, and Understanding the Codebase**

---

## Prerequisites

- Python 3.10+
- Redis (for Celery workers)
- Git

---

## Redis Dependency

Solstein uses Redis for:
- Celery message broker (default: redis://localhost:6379/0)
- Celery result backend (default: redis://localhost:6379/1)
- Rate limiter (when configured with Redis client)

### Starting Redis (Development)

**Option 1: Docker** (Recommended)
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

**Option 2: Homebrew (macOS)**
```bash
brew install redis
redis-server
```

**Option 3: From Source (Linux)**
```bash
git clone https://github.com/redis/redis.git
cd redis && make && ./src/redis-server
```

### Verify Redis is Running

```bash
redis-cli ping
# Expected output: PONG
```

### Configuration

Set these environment variables to use non-default Redis:

```bash
export CELERY_BROKER_URL="redis://your-redis-host:6379/0"
export CELERY_RESULT_BACKEND="redis://your-redis-host:6379/1"
```

---

## Setup

```bash
# 1. Clone
git clone <repo-url> && cd solstein

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install in editable mode with dev dependencies
pip install -e ".[dev]"

# 4. Confirm installation
python -c "import solstein; print('✓ solstein ready')"
```

---

## Running Locally

```bash
# Start the FastAPI server (hot reload)
uvicorn solstein.api.main:app --reload --port 8000

# API Docs (Swagger): http://localhost:8000/docs
# ReDoc:             http://localhost:8000/redoc
# Health check:      http://localhost:8000/health
```

```bash
# Start Celery worker (separate terminal)
celery -A solstein.worker worker --loglevel=info
```

---

## Running Tests

```bash
# Full suite
pytest tests/

# With coverage
pytest tests/ --cov=src/solstein --cov-report=term-missing

# By layer
pytest tests/unit/          # Domain model + scoring tests
pytest tests/integration/   # API endpoint + integration tests
pytest tests/data_quality/  # Golden dataset regressions

# Verbose output
pytest tests/ -v
```

**Coverage targets:**

| Layer | Target | Notes |
|-------|--------|-------|
| Domain models | > 90% | Property edge cases + boundary values |
| Scoring engine | > 80% | Use `pytest.approx` for float comparisons |
| API routers | > 70% | 404, 422, plus happy-path |
| CLI | > 50% | Untested by default — use Click's `CliRunner` |
| Overall | > 60% | Current baseline |

---

## Code Structure

```
src/solstein/
├── api/
│   ├── main.py              ← FastAPI app setup, CORS, lifespan
│   ├── dependencies.py      ← Dependency injection (auth, repo)
│   ├── schemas.py           ← Pydantic request/response schemas
│   └── routers/
│       ├── companies.py     ← CRUD endpoints
│       ├── scoring.py       ← Score calculation endpoints
│       ├── market.py        ← Market analysis + search
│       └── export.py        ← Excel export endpoints
├── analytics/
│   └── scoring.py           ← GrowthScorer, MarketAnalyzer
├── core/
│   ├── repositories.py      ← Abstract repository interfaces
│   └── scoring_config.py    ← Pydantic scoring configuration
├── data/
│   ├── loaders.py           ← JSON/Excel data ingestion
│   ├── models.py            ← Data-layer models (separate from domain)
│   └── repositories.py      ← JsonFileRepository implementation
├── domain/
│   └── models.py            ← Pure domain models (Company, FinancialMetric)
├── exporters/
│   └── excel_exporter.py    ← Excel dashboard generation
├── config.py                ← Application configuration (Pydantic Settings)
├── tasks.py                 ← Celery background tasks
└── worker.py                ← Celery app initialization
```

---

## Key Concepts

### Scoring Pipeline

```
Company → GrowthScorer.calculate_scores() → scored Company
                   ↓
    _calculate_growth_score()           [0–10]
    _calculate_financial_health_score() [0–10]
    _calculate_competitive_position_score() [0–10]
```

Classification thresholds:
- `growth_score >= 7.0` → 🔥 Phoenix
- `growth_score <= 4.0` → ⚖️ Lead
- Otherwise → 🧂 Salt

### Dependency Injection

All API routes use FastAPI's `Depends()` for:
- `get_current_user()` — JWT authentication
- `get_repository()` — Repository injection (mockable in tests)

### Testing Fixtures

All shared fixtures live in `tests/conftest.py`. Do not define `mock_company` in individual test files — use the shared fixture.

```python
# conftest.py provides these fixtures:
# mock_company          → deterministic Company instance (via factories.py)
# mock_repo             → mocked CompanyRepository
# client                → TestClient with repo override
# unauthenticated_client → TestClient without auth header (receives 'anonymous' user)
```

**Single source of truth for test objects:** `tests/factories.py`

```python
from tests.factories import make_company, make_financial_metric

# Create a company with custom overrides
c = make_company(name="Test Corp", growth_rate=45.0)
```

Always use `factories.py` rather than constructing domain objects directly in tests. This ensures correct enum usage and consistent field values.

---

## Adding a New Scoring Dimension

1. Add configuration fields to `src/solstein/core/scoring_config.py`
2. Implement `_calculate_<dimension>_score()` in `GrowthScorer`
3. Call it in `calculate_scores()` and attach to the profile
4. Update the domain model if a new score field is needed
5. Add unit tests with `pytest.approx` precision
6. Add a golden dataset test in `tests/data_quality/`

---

## Comprehensive Testing Guide

### Testing Strategy (4-Layer Pyramid)

Solstein uses **6 layers of testing** ensuring reliability without brittleness:

```
                    ▲
                   ╱ ╲
                  ╱   ╲      Data Quality
                 ╱  1  ╲    (Golden Dataset)
                ╱───────╲    ~5 tests
               ╱         ╲
              ╱─────────── ╲
             ╱   2    3    ╲  Integration & Worker
            ╱               ╲  Tests
           ╱───────────────── ╲  ~20 tests
          ╱                    ╲
         ╱──────────────────────╲
        ╱           4            ╲  Unit Tests
       ╱                          ╲  (Domain, Scoring)
      ╱────────────────────────────╲  ~50 tests
     ╱________________________________╲
```

#### Layer 1: Unit Tests (Bottom — Most Tests)

**What:** Pure logic with no I/O (no database, no filesystem, no API calls)

**Where:** `tests/unit/test_*.py`

**Examples:**
- `test_company_creation` — Domain model instantiation
- `test_growth_score_calculation` — Scoring math with known inputs
- `test_classification_boundaries` — Classification logic (Phoenix/Salt/Lead)
- `test_financial_metric_validation` — Input validation

**How to write:**

```python
# tests/unit/test_scoring.py

import pytest
from solstein.analytics.scoring import GrowthScorer
from solstein.domain.models import Company, FinancialMetric
from solstein.core.scoring_config import ScoringSettings


@pytest.fixture
def scorer():
    """Create scorer with default config."""
    return GrowthScorer(ScoringSettings())


def test_growth_score_with_zero_growth(scorer):
    """Zero growth rate should result in base score."""
    company = Company(id="test", name="Stagnant Corp")
    company.financials = FinancialMetric(revenue=100.0, growth_rate=0.0)
    
    result = scorer.calculate_scores(company)
    
    # Use pytest.approx for float comparisons
    assert result.growth_score == pytest.approx(5.0, abs=0.01)
    assert result.classification == "Salt"


def test_growth_score_with_high_growth(scorer):
    """High growth rate should increase score."""
    company = Company(id="test", name="Phoenix Corp")
    company.financials = FinancialMetric(revenue=100.0, growth_rate=50.0)
    
    result = scorer.calculate_scores(company)
    
    assert result.growth_score > 7.0
    assert result.classification == "Phoenix"


@pytest.mark.parametrize("growth_rate,expected_classification", [
    (50.0, "Phoenix"),
    (25.0, "Phoenix"),
    (10.0, "Salt"),
    (3.0, "Lead"),
    (0.0, "Salt"),
])
def test_classification_boundaries(scorer, growth_rate, expected_classification):
    """Test all classification boundaries."""
    company = Company(id="test", name="Test")
    company.financials = FinancialMetric(revenue=100.0, growth_rate=growth_rate)
    
    result = scorer.calculate_scores(company)
    
    assert result.classification == expected_classification
```

**Key rules:**
- Use `pytest.approx()` for float comparisons (not `==`)
- Use `@pytest.mark.parametrize` for multiple input scenarios
- Mock nothing — test pure logic only
- Aim for >80% coverage in domain/scoring modules

#### Layer 2: Integration Tests (API Contracts)

**What:** API endpoints with mocked repository (tests request/response contracts)

**Where:** `tests/test_fastapi.py`

**Purpose:** Verify API endpoints accept correct input, return correct output schema, handle errors

**How to write:**

```python
# tests/test_fastapi.py

import pytest
from fastapi.testclient import TestClient
from solstein.api.main import app
from tests.factories import make_company


def test_list_companies_endpoint(client: TestClient, mock_repo):
    """GET /companies should return list of companies."""
    # Arrange
    mock_repo.find_all.return_value = [
        make_company(name="Corp 1"),
        make_company(name="Corp 2"),
    ]
    
    # Act
    response = client.get("/companies")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Corp 1"
    assert data[1]["name"] == "Corp 2"


def test_score_company_endpoint(client: TestClient, mock_repo):
    """POST /scoring/company/{id}/score should calculate and return scores."""
    # Arrange
    company = make_company(name="Test Corp", growth_rate=50.0)
    mock_repo.find_by_id.return_value = company
    
    # Act
    response = client.post("/scoring/company/test-corp/score")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["growth_score"] is not None
    assert data["classification"] == "Phoenix"


def test_missing_company_returns_404(client: TestClient, mock_repo):
    """GET /companies/{id} should return 404 if not found."""
    # Arrange
    mock_repo.find_by_id.return_value = None
    
    # Act
    response = client.get("/companies/nonexistent")
    
    # Assert
    assert response.status_code == 404


def test_invalid_filter_returns_422(client: TestClient):
    """POST with invalid schema should return 422."""
    # Act
    response = client.post("/companies/score", json={"invalid": "field"})
    
    # Assert
    assert response.status_code == 422  # Unprocessable Entity
```

**Key rules:**
- Use `client` fixture (FastAPI TestClient with mocked repo)
- Mock repository at dependency injection layer
- Test happy path, error cases (404, 422, 500)
- Test response schema matches OpenAPI spec
- Aim for >70% coverage in API routers

#### Layer 3: Worker Tests (Celery Tasks)

**What:** Background job execution with mocked external services

**Where:** `tests/integration/test_worker.py`

**Purpose:** Verify Celery tasks execute correctly, handle failures, produce correct results

**How to write:**

```python
# tests/integration/test_worker.py

import pytest
from unittest.mock import patch, MagicMock
from solstein.tasks import batch_score_companies
from solstein.domain.models import Company
from tests.factories import make_company


@patch('solstein.tasks.ExcelExporter')
def test_batch_score_companies_task(mock_exporter):
    """Batch scoring task should score all companies and export Excel."""
    # Arrange
    mock_exporter_instance = MagicMock()
    mock_exporter.return_value = mock_exporter_instance
    mock_exporter_instance.export.return_value = Path("output.xlsx")
    
    companies = [
        make_company(name="Corp 1", growth_rate=50.0),
        make_company(name="Corp 2", growth_rate=5.0),
    ]
    
    # Act (tasks execute synchronously in tests)
    result = batch_score_companies(companies)
    
    # Assert
    assert result["status"] == "completed"
    assert result["companies_scored"] == 2
    assert result["file_path"] == "output.xlsx"
    mock_exporter_instance.export.assert_called_once()
```

**Key rules:**
- Don't start Redis or run real Celery worker
- Call task function directly (executes synchronously)
- Mock I/O (file exports, API calls, database writes)
- Test success and failure cases
- Aim for >70% coverage in tasks

#### Layer 4: Data Quality Tests (Golden Dataset)

**What:** Regression tests protecting classification boundaries with known data

**Where:** `tests/data_quality/test_ai_insights.py`

**Purpose:** Detect unintended changes to scoring logic (e.g., threshold drift)

**How to write:**

```python
# tests/data_quality/test_ai_insights.py

import pytest
from solstein.analytics.scoring import GrowthScorer
from solstein.domain.models import Company, FinancialMetric


# Golden dataset — known companies with expected classifications
GOLDEN_DATA = [
    {
        "id": "phoenix-corp",
        "name": "Phoenix Corp",
        "financials": {"revenue": 500.0, "growth_rate": 75.0, "profit_margin": 25.0},
        "expected_classification": "Phoenix",
        "expected_growth_score_min": 7.0,
    },
    {
        "id": "lead-corp",
        "name": "Lead Corp",
        "financials": {"revenue": 50.0, "growth_rate": -10.0, "profit_margin": -5.0},
        "expected_classification": "Lead",
        "expected_growth_score_max": 4.0,
    },
]


@pytest.fixture
def scorer():
    return GrowthScorer()


@pytest.mark.parametrize("test_case", GOLDEN_DATA)
def test_golden_dataset_classification(scorer, test_case):
    """Golden dataset should maintain consistent classifications."""
    company = Company(id=test_case["id"], name=test_case["name"])
    company.financials = FinancialMetric(**test_case["financials"])
    
    result = scorer.calculate_scores(company)
    
    assert result.classification == test_case["expected_classification"], \
        f"{test_case['name']} misclassified"
    
    if "expected_growth_score_min" in test_case:
        assert result.growth_score >= test_case["expected_growth_score_min"]
    
    if "expected_growth_score_max" in test_case:
        assert result.growth_score <= test_case["expected_growth_score_max"]
```

**Key rules:**
- Use deterministic test data (not randomized)
- Document expected outcomes
- Run on every commit (prevents drift)
- Update if scoring logic intentionally changes
- Aim for 100% coverage of classification boundaries

---

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific layer
pytest tests/unit/               # Only unit tests
pytest tests/test_fastapi.py    # Only API tests
pytest tests/integration/       # Integration tests (API, database, services)
pytest tests/data_quality/      # Only golden dataset

# Run with coverage
pytest tests/ --cov=src/solstein --cov-report=term-missing

# Run single test file
pytest tests/unit/test_scoring.py

# Run single test function
pytest tests/unit/test_scoring.py::test_growth_score_with_zero_growth

# Run with verbose output
pytest tests/ -v

# Run and show print statements
pytest tests/ -s

# Stop on first failure
pytest tests/ -x

# Run only tests matching pattern
pytest tests/ -k "classification"
```

### Test Fixtures (conftest.py)

**Shared fixtures available to all tests:**

```python
# tests/conftest.py

@pytest.fixture
def mock_company():
    """Deterministic test company from factories.py"""
    return make_company()

@pytest.fixture
def mock_repo():
    """Mocked CompanyRepository for testing."""
    return MagicMock(spec=CompanyRepository)

@pytest.fixture
def client(mock_repo):
    """FastAPI TestClient with mocked repo."""
    # Dependency override: inject mock_repo instead of real one
    app.dependency_overrides[get_repository] = lambda: mock_repo
    return TestClient(app)
    # Cleanup after test
    yield client
    app.dependency_overrides.clear()

@pytest.fixture
def unauthenticated_client(mock_repo):
    """TestClient without auth (receives 'anonymous' user)."""
    # Similar to client but simulates unauthenticated request
    # See conftest.py for implementation
    ...
```

**Do NOT create local fixtures** — use shared fixtures from `conftest.py`.

### Test Data Factories (factories.py)

**Single source of truth for test objects:**

```python
from tests.factories import (
    make_company,
    make_financial_metric,
    make_scoring_explanation,
)

# Create default company
c = make_company()

# Create company with overrides
c = make_company(
    name="Custom Corp",
    industry="Energy Software",
    growth_rate=35.0,
    employees=50,
)

# Create financial metric
fm = make_financial_metric(revenue=100.0, growth_rate=25.0)
```

**Why factories instead of constructing directly?**
- Ensures consistent defaults
- Handles enum values correctly
- Future-proof (if model changes, update factory once)
- Reduces boilerplate in tests

---

### Coverage Targets

| Module | Target | How to Check |
|--------|--------|------------|
| Domain models | > 90% | `pytest tests/unit/test_models.py --cov=src/solstein/domain` |
| Scoring engine | > 85% | `pytest tests/unit/test_scoring.py --cov=src/solstein/analytics` |
| API routers | > 75% | `pytest tests/test_fastapi.py --cov=src/solstein/api` |
| Celery tasks | > 70% | `pytest tests/integration/test_worker.py --cov=src/solstein/tasks` |
| **Overall** | > 65% | `pytest tests/ --cov=src/solstein` |

Run this to check current coverage:

```bash
pytest tests/ --cov=src/solstein --cov-report=term-missing --cov-report=html
# Open: htmlcov/index.html
```

---

### Common Testing Patterns

#### Mocking External Dependencies

```python
from unittest.mock import patch, MagicMock

# Mock a function
@patch('solstein.data.repositories.JsonFileRepository.find_all')
def test_with_mocked_repo(mock_find_all):
    mock_find_all.return_value = [make_company()]
    # ... test code ...

# Mock a class
@patch('solstein.exporters.excel_exporter.ExcelExporter')
def test_with_mocked_exporter(mock_exporter_class):
    mock_instance = MagicMock()
    mock_exporter_class.return_value = mock_instance
    mock_instance.export.return_value = Path("test.xlsx")
    # ... test code ...
```

#### Parametrized Tests (Multiple Inputs)

```python
@pytest.mark.parametrize("growth_rate,expected", [
    (50.0, "Phoenix"),
    (10.0, "Salt"),
    (3.0, "Lead"),
])
def test_classification(growth_rate, expected):
    # ... test runs 3 times, once per parameter set
    ...
```

#### Testing Async Code

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await my_async_function()
    assert result == expected
```

#### Testing Exceptions

```python
def test_invalid_input_raises_error():
    with pytest.raises(ValueError, match="Expected positive number"):
        calculate_score(-5)
```

---

## Makefile Commands

```bash
make install     # Install dependencies
make test        # Run full test suite
make lint        # Run ruff linter
make format      # Auto-format with ruff
make coverage    # Coverage report
```

---



---

## Phase 13: Production Reliability Features

### Async Patterns & Retry Logic

All async tasks now implement exponential backoff retry logic:

```python
@shared_task(bind=True, max_retries=3)
def refresh_sec_edgar(self):
    """Retry with exponential backoff: 5s → 10s → 20s"""
    try:
        result = asyncio.run(_refresh_async())
        return result
    except Exception as e:
        countdown = 5 * (2 ** self.request.retries)
        raise self.retry(exc=e, countdown=countdown)
```

**See**: [Async Patterns Guide](./async-patterns.md), [Retry Logic Guide](./retry-logic.md)

### Health Checks

The API now includes liveness and readiness probes for Kubernetes:

```bash
# Liveness probe (is process alive?)
curl http://localhost:8000/health

# Readiness probe (is system ready for traffic?)
curl http://localhost:8000/ready
```

**See**: [Health Checks Guide](./health-checks.md)

### Rate Limiting

All API endpoints (except `/health` and `/ready`) are protected by rate limiting:

```
Default: 100 requests/minute per client
Fallback: Memory-based when Redis unavailable
```

**See**: [Rate Limiting Guide](./rate-limiting.md)

### Phase Documentation

Complete documentation of all 13 phases:

- [Phase Overview](../phases/README.md) — Timeline and evolution
- [Phase 13 Deep Dive](../phases/phase-13.md) — Production reliability features

---
