# 📁 Repository Structure

*A map of the vault.*

---

## Top-Level Layout

```
solstein/
├── src/solstein/        ← The platform (FastAPI, scoring, exporters)
├── tests/               ← Test suite (unit, integration, data quality)
├── docs/                ← All documentation (this folder)
├── data/                ← Input data + export output
├── scripts/             ← Utility and setup scripts
├── docker/              ← Docker + compose files
├── legacy/              ← Archived C# predecessor — do not develop here
├── pyproject.toml       ← Project metadata, dependencies, tool config
└── Makefile             ← Common tasks (install, test, lint, docker)
```

---

## Source Layout — `src/solstein/`

```
src/solstein/
├── api/
│   ├── main.py              ← FastAPI app entry point (CORS, lifespan, router mounts)
│   ├── dependencies.py      ← Dependency injection (auth, repository)
│   ├── schemas.py           ← Pydantic request/response schemas
│   └── routers/
│       ├── companies.py     ← GET/POST /companies
│       ├── scoring.py       ← POST /scoring/company/{id}/score, GET /scoring/stats
│       ├── market.py        ← GET /market/analysis, /market/overlap, /market/search
│       └── export.py        ← GET /export/excel, GET /export/json
├── analytics/
│   └── scoring.py           ← GrowthScorer, MarketAnalyzer, CompetitiveOverlapCalculator
├── core/
│   ├── repositories.py      ← Abstract interfaces (CompanyRepository, CompanyFilter)
│   └── scoring_config.py    ← Pydantic scoring configuration (all thresholds and weights)
├── data/
│   ├── loaders.py           ← JSON ingestion pipeline
│   ├── models.py            ← Data-layer Pydantic models (CompanyProfile, etc.)
│   └── repositories.py      ← JsonFileRepository — concrete file-backed implementation
├── domain/
│   └── models.py            ← Pure domain entities (Company, FinancialMetric, enums)
├── exporters/
│   └── excel_exporter.py    ← Excel dashboard generation (openpyxl)
├── extractors/
│   └── markdown_extractor.py ← Markdown-to-profile extraction pipeline
├── config.py                ← Application settings (Pydantic BaseSettings, .env support)
├── tasks.py                 ← Celery task definitions (batch scoring, report export)
├── worker.py                ← Celery app initialization
└── cli.py                   ← Click CLI (extract, score, export-excel, analyze-market)
```

---

## Tests Layout — `tests/`

```
tests/
├── conftest.py              ← Shared fixtures (mock_repo, mock_company, client)
├── factories.py             ← Single source of truth for test object creation
├── test_fastapi.py          ← API integration tests
├── unit/
│   ├── test_models.py       ← Domain model property and edge case tests
│   └── test_scoring.py      ← Scoring engine unit tests (parametrized, approx)
├── integration/
│   └── test_worker.py       ← Celery task tests (real scorer, mocked I/O)
└── data_quality/
    └── test_ai_insights.py  ← Golden dataset regression tests
```

---

## Quick Commands

```bash
# Install
pip install -e ".[dev]"

# Run API (hot reload)
uvicorn solstein.api.main:app --reload --port 8000

# Run Celery worker (separate terminal)
celery -A solstein.worker worker --loglevel=info

# Run tests
pytest tests/

# Run tests with coverage
pytest tests/ --cov=src/solstein --cov-report=term-missing
```

Or with Make:

```bash
make install     # Set up virtualenv + dependencies
make run         # Start API server
make test        # Run full suite
make lint        # ruff + mypy
make coverage    # Coverage report
```

---

## Data Flow

```
Input JSON              CLI / API Request
(data/input/)     →    identify market
        ↓
    CompetitorDataLoader
        ↓
    JsonFileRepository      ← swappable with PostgresRepository
        ↓
    GrowthScorer / MarketAnalyzer
        ↓
    API Response / ExcelExporter / Celery Task
        ↓
    Output (data/output/exports/)
```

---

*The legacy C# solution lives in `legacy/`. It is archived. You do not need to go there.*
