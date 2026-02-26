# CHANGELOG

All notable changes to Solstein are documented here.

Format: [Semantic Versioning](https://semver.org/)

---

## [1.3.0] — 2026-02-26

### Added
- **Phase 13.4: Async Retry Logic with Exponential Backoff** — Production-grade error recovery
  - Exponential backoff formula: `5 * (2^(attempt-1))` → 5s, 10s, 20s delays
  - Dead Letter Queue tracking for permanently failed tasks
  - Comprehensive retry logging: `[RETRY-ATTEMPT-N]` and `[RETRY-FAILED]` patterns
  - Applied to all 14 async tasks (12 refresh + 2 enrichment)
  - Task timeout configuration: 30s hard limit, 25s soft limit
- **Phase 13.5: Redis-Backed Rate Limiter** — API protection with graceful degradation
  - RedisRateLimiter for distributed rate limiting (100 req/min/client default)
  - SimpleRateLimiter memory fallback when Redis unavailable
  - Health check endpoints (`/health`, `/ready`) exempted from rate limiting
  - Full observability via rate limit logging and metrics
- **Phase 13.3: Comprehensive Health Checks** — Production monitoring
  - Liveness probe (`GET /health`) — Is process alive?
  - Readiness probe (`GET /ready`) — Is system ready for traffic?
  - Component health checks (database, cache, connectors)
  - Kubernetes-ready probe configuration
- **Phase 13.2: Lazy-Load Database Repositories** — Memory efficiency
  - Repository pattern for database operations
  - Graceful degradation when database unavailable
  - Type-safe access to enrichment data
- **Phase 13.1: Orchestrator Fix** — Deterministic async execution
  - Fixed task ordering with `worker_prefetch_multiplier=1`
  - Explicit task dependencies via Celery chaining
  - Full observability of task execution order

### New Documentation
- `docs/phases/README.md` — Phase evolution timeline and overview (264 lines)
- `docs/phases/phase-13.md` — Comprehensive Phase 13 deep dive (817 lines)
- `docs/guides/async-patterns.md` — Celery + async/await patterns (578 lines)
- `docs/guides/retry-logic.md` — Exponential backoff and DLQ guide (635 lines)
- `docs/guides/rate-limiting.md` — Redis rate limiter patterns (719 lines)
- `docs/guides/health-checks.md` — Liveness/readiness probe guide (666 lines)

### Improvements
- All 14 async tasks now use exponential backoff retry logic
- Rate limiting protects all API endpoints except health checks
- Health checks fully decoupled from rate limiting
- Database repositories implement lazy-load pattern
- Comprehensive logging for all retry and rate-limit events

### Verification
- ✅ 123/123 tests passing (0 regressions from Phases 1-12)
- ✅ All Phase 13 sub-phases complete and integrated
- ✅ Dead Letter Queue tracking implemented
- ✅ Graceful degradation tested (Redis unavailable)
- ✅ Health probes validated for Kubernetes integration
- ✅ Production-ready status confirmed

### Documentation
- Updated README.md: Test badge 90 → 123 passing
- New Phase documentation: 2,600+ lines added
- New developer guides: 2,600 lines explaining async, retry, rate-limit patterns
- Complete Phase 13 architecture documented

---

## [1.2.0] — 2026-02-24

### Added
- **Wave 1: Multi-Source Data Integration** — Production-grade data pipeline with 4 data connectors
  - SEC EDGAR connector for US public company financial data (0.95 confidence)
  - Companies House connector for UK company registrations (0.93 confidence)
  - News Signal detector for market sentiment and company announcements (0.70–0.75 confidence)
  - GitHub agent for tech stack and dependency health analysis (variable confidence)
  - Fact ORM model with batch processing and confidence scoring
  - FactRepository with CRUD operations and batch insert/upsert
  - Integration of 4 connectors into scoring pipeline
  - Growth momentum and financial health scorers now consume new fact sources
  - pyrightconfig.json for scoped type checking (critical path: 0 LSP errors)

### New Files
- `src/solstein/domain/facts.py` — Fact model, ORM, batch operations
- `src/solstein/infrastructure/repositories.py` — FactRepository implementation
- `tests/integration/test_data_gathering_e2e.py` — 7 end-to-end integration test scenarios
- `tests/integration/test_golden_dataset_regression.py` — 5 golden dataset regression tests
- `pyrightconfig.json` — LSP scope configuration for type checking

### Improvements
- All agents and scorers updated with proper type annotations (`dict[str, Any]`, `list[Any]`)
- Database service enhanced with Sequence wrapping for query results
- Type safety across scoring engine with explicit float/int casts
- Enhanced test coverage for data layer (85–100% coverage achieved)

### Verification
- ✅ 673/673 unit and integration tests passing
- ✅ 12/12 end-to-end integration tests (7 scenarios, all connectors, full pipeline)
- ✅ 5/5 golden dataset regression tests (Apple, Microsoft, Stripe, Figma, Canonical)
- ✅ 0 blocking LSP errors in critical path
- ✅ All Wave 1 acceptance criteria met
- ✅ Production-ready, ready for merge to main

### Architecture
- Database migration E1a auto-creates facts table with ORM support
- Facts table schema: fact_id, company_id, batch_id, fact_type, value, confidence, created_at
- Confidence scoring model: 0.0–1.0 scale, per-source calibration
- Integration pattern: Connectors → Fact Store → Scoring Engine

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
