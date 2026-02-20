
# 📜 Developer Guide

**Setting Up, Contributing, and Understanding the Codebase**

---

## Prerequisites

- Python 3.12+
- Redis (for Celery workers)
- Git

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
pytest tests/integration/   # API endpoint + worker tests
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
- `growth_score >= 7.0` → 🚀 Rocket
- `growth_score <= 4.0` → 🦕 Dinosaur
- Otherwise → ⚖️ Neutral

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

## Makefile Commands

```bash
make install     # Install dependencies
make test        # Run full test suite
make lint        # Run ruff linter
make format      # Auto-format with ruff
make coverage    # Coverage report
```

---


