
# 📜 Architecture Decision Records

**The reasoning behind Solstein's technical choices**

---

## ADR-001: FastAPI as the API Framework

**Date:** 2025-Q4
**Status:** Accepted

**Context:** We needed an async Python web framework that could support real-time scoring requests and background task queuing.

**Decision:** FastAPI.

**Rationale:**
- Native async/await support matches Celery's non-blocking task model
- Automatic OpenAPI documentation — critical for investor demos
- `Depends()` injection system makes testing trivial (override any dependency)
- Pydantic integration for request/response schema validation

**Consequences:** Lifespan events (`@app.on_event`) are deprecated — migrate to `lifespan=` context manager in next refactor.

---

## ADR-002: Pydantic for Domain Models and Configuration

**Date:** 2025-Q4
**Status:** Accepted

**Context:** We needed strict configuration with environment variable support and type-safe domain models.

**Decision:** Pydantic for both `ScoringSettings` (config) and the API schema layer.

**Rationale:**
- `BaseSettings` with `.env` file support out of the box
- Composable model hierarchy (`ScoringSettings` → `GrowthScoringConfig` → individual fields)
- Validation at parse time, not runtime

**Caveat:** Core domain models (`Company`, `FinancialMetric`) are Python dataclasses, not Pydantic models, to keep the domain layer pure and dependency-free.

---

## ADR-003: Celery + Redis for Background Processing

**Date:** 2025-Q4
**Status:** Accepted

**Context:** Batch scoring (29+ companies) and Excel report generation are too slow for synchronous HTTP responses.

**Decision:** Celery with Redis as the message broker.

**Rationale:**
- Industry standard for Python async task processing
- Redis is already commonly deployed in production stacks
- Celery's `@shared_task` pattern allows tasks to be imported and tested without a running broker

**Testing implication:** All worker tests patch `JsonFileRepository` and `ExcelExporter` at the `solstein.tasks` module level and call tasks synchronously (no broker needed).

---

## ADR-004: JSON Flat Files as the Data Store

**Date:** 2025-Q4
**Status:** Accepted (with upgrade path)

**Context:** The initial dataset is 29 companies. The intelligence update cycle is measured in days, not seconds.

**Decision:** JSON files in a configurable directory, loaded via `JsonFileRepository`.

**Rationale:**
- Zero infrastructure dependency for the data layer
- Full data is auditable and version-controllable in Git
- `CompanyRepository` abstract interface means swapping to PostgreSQL/MongoDB requires only a new repository implementation, not changes to any other layer

**Upgrade path:** When dataset exceeds ~500 companies or real-time refresh is needed, implement `PostgresCompanyRepository(CompanyRepository)` against the same interface.

---

## ADR-005: 4-Layer Testing Pyramid

**Date:** 2026-Q1
**Status:** Accepted

**Context:** Initial integration tests were data-dependent and non-deterministic. Running tests required a live data directory and a specific company dataset.

**Decision:** 4-layer pyramid with dependency injection overrides at every level.

**Layers:**
1. **Unit** — Pure logic, no I/O, `pytest.approx` precision
2. **Integration** — API contracts with mocked repositories
3. **Worker** — Celery task logic with mocked external services
4. **Data Quality** — Golden dataset regressions protecting classification boundaries

**Key rule:** The `client` fixture in `conftest.py` overrides `get_repository` and `get_current_user` globally. Tests never touch the filesystem.

---

## ADR-006: Scoring in Millions (Revenue Units)

**Date:** 2026-Q1
**Status:** Accepted

**Context:** Revenue values in the dataset were stored in Millions (e.g., `100.0` = EUR 100M), but the initial `FinancialHealthConfig` thresholds used absolute EUR values (e.g., `100_000_000.0`).

**Decision:** Standardize all revenue-related thresholds to use Millions as the unit.

**Impact:** `revenue_large_threshold = 100.0` (100 Million), not `100_000_000.0`. All scoring config updated accordingly.

------

## ADR-007: Permissive Authentication (demo phase)

**Date:** 2026-Q1
**Status:** Accepted (with upgrade path)

**Context:** Solstein is in an active sales and demo phase. Requiring valid JWTs for every endpoint adds friction when showing the platform to prospective PE clients.

**Decision:** `HTTPBearer(auto_error=False)` in `dependencies.py`. Requests without a token receive `{"sub": "anonymous", "role": "viewer"}`.

**Consequence:** All routes are currently publicly accessible. Production deployments must set `auto_error=True` and replace the stub token decoder with a real JWT library (e.g., `python-jose`).

**Testing implication:** The `unauthenticated_client` fixture in `conftest.py` documents this design explicitly. There is no "401 Unauthorized" test because the API never returns one.

---

## ADR-008: GrowthScorer.calculate_scores() Mutates Its Input

**Date:** 2026-Q1
**Status:** Accepted (technical debt acknowledged)

**Context:** `calculate_scores(profile)` writes scores directly onto the `Company` dataclass fields and returns the same object. It is not a pure function.

**Current behaviour:**
```python
scored = scorer.calculate_scores(company)
assert scored is company  # True — same object
```

**Known risk:** Calling `calculate_scores()` twice on the same instance stacks bonuses on the previous score rather than recalculating from scratch. Tests must not call it twice on the same fixture instance.

**Upgrade path:** Replace the mutation pattern with a copy:
```python
from dataclasses import replace
scored = replace(profile, growth_score=g, financial_health_score=f, ...)
return scored
```

This was deferred to avoid the dataclass `replace()` boilerplate until a proper mapper layer is designed.

---
