# CHANGELOG

All notable changes to Solstein are documented here.

Format: [Semantic Versioning](https://semver.org/)

---

## [1.1.0] — 2026-02-20

### Added
- **Phase 9: Quality Engineering & TDD** — Complete 4-layer testing pyramid
  - Unit tests for all domain models and scoring logic (`tests/unit/`)
  - API integration tests with deterministic mock repositories (`tests/test_fastapi.py`)
  - Worker task tests for Celery batch scoring and export (`tests/integration/test_worker.py`)
  - Golden dataset regression tests protecting classification boundaries (`tests/data_quality/`)
  - Shared `conftest.py` with fixtures for all test layers
- **Legendary Documentation Suite** — Complete docs overhaul
  - Scroll-themed README with banner imagery
  - `docs/LORE/` — Origin story and three-entity strategic architecture
  - `docs/PITCH/` — Executive brief, full proposal, case study, business model
  - `docs/guides/` — Developer and operator guides
  - `docs/api/` — Complete API reference
  - `docs/architecture/` — Architecture Decision Records (ADR-001 through ADR-006)

### Fixed
- **Double Prefix Bug in market.py** — Routes `/market/analysis` and `/market/overlap` were incorrectly prefixed, causing 404 errors
- **Missing `datetime` import in `tasks.py`** — Caused `NameError` in batch scoring task
- **Module-level `settings` in `tasks.py`** — Refactored to function-scoped for testability
- **SWOT key casing** — Standardized to Title Case (`Strengths`, not `strengths`)
- **Revenue unit mismatch** — Scoring thresholds now consistently use Millions

### Changed
- `GrowthScoringConfig` revenue thresholds now use Millions as the unit
- `FinancialHealthConfig` revenue thresholds aligned to Millions
- `batch_score_companies` and `export_marketing_report` tasks now call `get_settings()` locally

---

## [1.0.0] — 2026-02-19

### Added
- Core FastAPI application with async routing
- `GrowthScorer` — multi-dimensional company scoring engine
- `MarketAnalyzer` — market landscape analysis with SWOT generation
- `CompanyRepository` — abstract repository interface
- `JsonFileRepository` — concrete implementation for flat-file data
- `ExcelExporter` — Excel dashboard generation
- Celery worker integration with Redis broker
- `ScoringSettings` Pydantic configuration system
- Initial dataset: 29 companies in European Energy Software market
- `src/` layout with proper package structure
- Docker support (`docker/docker-compose.yml`)
- CI/CD pipeline (`.github/workflows/`)

### Architecture
- API layer: FastAPI + Pydantic schemas
- Domain layer: Pure Python dataclasses (no framework dependency)  
- Data layer: JSON file repository (swappable interface)
- Background processing: Celery + Redis
- Configuration: Pydantic Settings with `.env` support

---

*For the complete history, see `git log`.*
