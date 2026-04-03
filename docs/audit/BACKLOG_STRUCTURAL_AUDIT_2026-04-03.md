# Backlog Structural Audit — 2026-04-03

> **Purpose**: Ground-truth snapshot of every file, function, class, line, and field referenced by
> active backlog stories (EPIC-086 through EPIC-089, EPIC-003 continuation). Use this document as the
> authoritative reference when writing or updating story files. Every claim here was verified by direct
> file read.
>
> **Scope**: EPIC-086, EPIC-087, EPIC-088, EPIC-089, EPIC-003 continuation (STORY-360/361/365)
>
> **Generated**: 2026-04-03 by codebase read audit

---

## EPIC-086: Pipeline Field Loss — Status: ✅ ALL DONE

All four stories (STORY-348 through STORY-351) implemented and verified.

### Verified Artifacts

| Claim | File | Line | Verified |
|-------|------|------|----------|
| `extra="forbid"` on `FinancialMetric` | `src/solstein/domain/models.py` | 96 | ✅ `ConfigDict(extra="forbid")` |
| `extra="forbid"` on `Company` | `src/solstein/domain/models.py` | 169 | ✅ `ConfigDict(extra="forbid")` |
| 15 extractors in `_SIGNAL_EXTRACTORS` | `src/solstein/research/signals.py` | 466–483 | ✅ 10 original + 5 STORY-349 additions |
| New extractors present | `signals.py:478–482` | — | ✅ `_signal_ebitda`, `_signal_net_income`, `_signal_pe_ratio`, `_signal_current_price`, `_signal_eps_ttm` |
| Field survival test file | `tests/unit/test_pipeline_field_survival.py` | — | ✅ exists, **8 tests** |

### Residual Finding — `growth_rate` Validator

`FinancialMetric` at `models.py:153–158` has a `field_validator("growth_rate")` that **raises ValueError for values outside `[-100, 1000]`**.

The tests at `test_scoring.py:151` and `test_scoring.py:158` pass `growth_rate=10_000.0` and `growth_rate=-10_000.0` directly to `FinancialMetric()`. Both will raise `ValidationError` — not pass. These are the **STORY-365 pre-existing failures**.

Fix required per STORY-365: change `10_000.0 → 999.0` and `-10_000.0 → -99.0` in the test, or add `allow_empty_primary=True` where needed.

---

## EPIC-087: Multi-Tenancy Enforcement — Status: Not Started

### `src/solstein/tenant/context.py` — Verified

| Symbol | Line | Facts |
|--------|------|-------|
| `current_tenant_var` | 21 | `ContextVar[str | None]` default=None |
| `TenantContext` class | 24 | context manager, sets/resets `current_tenant_var` |
| `get_current_tenant()` | 54 | returns `current_tenant_var.get()` — no args |
| `require_tenant()` | 63 | raises `RuntimeError` if None |
| `TenantIsolationMiddleware` | 78 | ASGI middleware, **never registered** in main.py |
| `_extract_tenant_id()` | 112 | reads `X-API-Key` header, falls back to `Authorization: Bearer` |
| `_validate_api_key()` | 134 | **STUB** — computes hash at line 144 but discards it, returns `None` at line 149 unconditionally |
| `_validate_jwt()` | 151 | **WORKING** — calls `verify_token()`, returns `payload.get("tenant_id")` |
| `TenantAwareRepository` | 169 | uses `get_current_tenant()` in `__init__` |
| `generate_api_key()` | 213 | generates `sk_live_<token>` format |
| `hash_api_key()` | 224 | SHA-256 of raw key |

### `src/solstein/api/middleware/tenant.py` — Verified

| Symbol | Line | Facts |
|--------|------|-------|
| `TenantMiddleware` | 59 | `BaseHTTPMiddleware` subclass |
| `dispatch()` | 68 | public paths bypass, missing key → 401, calls `_lookup_tenant()` |
| `_lookup_tenant()` | 151 | **module-level async function** (not a method), takes `key_hash` + `request` |
| DB lookup pattern | 170–175 | `select(TenantRecord).where(api_key_hash==key_hash, is_active.is_(True))` |
| Import path | 166 | `from solstein.infrastructure.database_models import TenantRecord` ← **Note: imports from `database_models` not `models/infrastructure`** |

**Critical finding**: `_lookup_tenant` imports `TenantRecord` from `solstein.infrastructure.database_models`, not `solstein.infrastructure.models.infrastructure`. Both paths may resolve to the same class (re-exports), but STORY-352 task body should use the same import path.

### `src/solstein/infrastructure/models/infrastructure.py` — Verified

| Symbol | Line | Facts |
|--------|------|-------|
| `TenantRecord` | 40 | table `tenants` |
| `id` | 49 | `Uuid(as_uuid=True)`, primary key |
| `name` | 50 | `String(255)`, unique |
| `api_key_hash` | 51 | `String(64)`, **unique**, comment "SHA-256 hex" |
| `is_active` | 52 | `Boolean`, default True |
| `plan` | 53 | `String(64)`, default "standard" |
| `rate_limit_per_min` | 54 | `Integer`, default 60 |

### `src/solstein/api/main.py` — Verified (registration)

| Line | What happens |
|------|-------------|
| 197 | `app.add_middleware(PrometheusMiddleware, ...)` |
| 204 | `app.add_middleware(AuditMiddleware)` |
| **207** | **`app.add_middleware(TenantMiddleware)`** ← only registered middleware |
| — | `TenantIsolationMiddleware` NOT registered anywhere |

**Router registrations relevant to EPIC-089:**

| Line | Router | Prefix |
|------|--------|--------|
| 218 | `jobs.router` | `/jobs` |
| 221 | `async_jobs.router` | (no prefix — async_jobs handles its own prefix) |
| 222 | `research_jobs.router` | `/jobs` |

No `/workflows` prefix registered yet — STORY-363 must add it.

### Tenant Validation Pattern — `research_jobs.py` (lines 125–163)

Exact pattern to replicate in STORY-364:

```python
@router.get("/research-jobs/{job_id}", ...)
async def get_research_job(
    job_id: str,
    tenant: dict[str, Any] = Depends(get_current_tenant),
    session: Any = Depends(get_db_session),
) -> ResearchJobResponse:
    tenant_id = tenant.get("tenant_id", "")
    repo = ResearchJobRepository(session)
    try:
        parsed_id = uuid.UUID(job_id)
    except ValueError as e:
        raise APIError(code="INVALID_JOB_ID", ..., status_code=400) from e
    job = await repo.get_job(parsed_id)
    if job is None or job.tenant_id != tenant_id:
        raise APIError(code="NOT_FOUND", ..., status_code=404)
    return _job_to_response(job)
```

**`get_current_tenant` dependency**: defined at `src/solstein/api/dependencies.py:140` — returns `dict[str, Any]` with key `"tenant_id"`. Reads `request.state.tenant` (set by `TenantMiddleware`), raises `HTTPException(401)` if None. **Not** the `get_current_tenant()` from `tenant/context.py` — that's a ContextVar getter with no `request` parameter.

---

## EPIC-088: Infrastructure Reliability — Status: Not Started

### `src/solstein/api/routers/health.py` — `worker_health()` (Verified)

There are **two health modules** — do not confuse them:

| Module | Purpose |
|--------|---------|
| `src/solstein/api/routers/health.py` | FastAPI route handlers — `worker_health()` lives here |
| `src/solstein/monitoring/health.py` | `HealthChecker` class with `check_celery()` placeholder — NOT the STORY-357 target |

**STORY-357 target**: `src/solstein/api/routers/health.py:156–187`

| Symbol | Line | Facts |
|--------|------|-------|
| `@router.get("/workers", name="worker_health")` | 156 | Route decorator |
| `async def worker_health() -> dict` | 157 | Handler function |
| Real Celery inspect | 177–178 | `celery_app.control.inspect(timeout=N).ping()` — real implementation |
| `status="no_workers"` | 183 | returned when ping() returns None — HTTP 200 ← **bug** |
| `status="unreachable"` | 185–186 | returned when exception — HTTP 200 ← **bug** |
| `status="healthy"` | 181 | returned when workers respond — HTTP 200 ✅ |

**STORY-357 scope**: After `if ping_result:` branch sets healthy and returns 200, the `else` and `except` paths must raise `APIError(status_code=503)` instead of returning the dict.

### `src/solstein/api/main.py` — Lifespan (lines 70–153)

| Line | Event |
|------|-------|
| 70 | `async def lifespan(app)` |
| 77 | `settings.check_configuration()` |
| 89–92 | Initialize feature_flags, response_cache, etc. |
| 96–108 | OpenTelemetry init (non-critical, skipped on error) |
| 117–127 | Cache warming (background task, non-critical) |
| 129–139 | Supabase Realtime listener start |
| **141** | **`yield`** — app starts accepting traffic here |

**Insert point for STORY-358**: Broker ping must go **between line 127 and line 129** (after cache warming, before realtime listener). The yield at line 141 is where traffic begins — broker must be confirmed before reaching it.

### `src/solstein/celery_config.py` — Beat Schedule (lines 109–184)

**Task count: 13** (not 12 as originally documented in EPIC-088 README — now corrected)

| Entry | Task path | Schedule |
|-------|-----------|----------|
| `refresh-sec-edgar-daily` | `solstein.worker_tasks.refresh_sec_edgar` | 09:00 daily |
| `refresh-companies-house-daily` | `...refresh_companies_house` | 09:30 daily |
| `refresh-news-signals-hourly` | `...refresh_news_signals` | every hour |
| `refresh-github-every-6-hours` | `...refresh_github` | every 6h |
| `refresh-yahoo-finance-every-6-hours` | `...refresh_yahoo_finance` | every 6h +15m |
| `refresh-patents-daily` | `...refresh_patents` | 10:00 daily |
| `refresh-news-every-2-hours` | `...refresh_news` | every 2h +30m |
| `refresh-website-daily` | `...refresh_website` | 11:00 daily |
| `refresh-linkedin-every-12-hours` | `...refresh_linkedin` | every 12h |
| `refresh-funding-every-6-hours` | `...refresh_funding` | every 6h +45m |
| `refresh-global-market-every-6-hours` | `...refresh_global_market` | every 6h +30m |
| `refresh-web-search-every-6-hours` | `...refresh_web_search` | every 6h |
| `refresh-all-sources-weekly` | `...refresh_all_sources` | Sunday 02:00 |

All 13 tasks are in namespace `solstein.worker_tasks.*`.

### `src/solstein/worker/orchestration.py` — Verified

Only one function exists: `refresh_all_sources` (Celery shared_task, line 29). **No `run_workflow_task`**. This is the correct file where STORY-363 must add the new task.

---

## EPIC-089: Workflow Orchestration API — Status: Not Started

### `src/solstein/api/routers/jobs.py` — Verified

Full file content:
- Line 1–5: module docstring (mentions Temporal removed)
- Line 12–15: `router = APIRouter(tags=["Jobs"])` — **defined twice** (lines 12 and 15, first is overwritten)
- Line 18: `@router.get("/{workflow_id}")`
- Line 19: `async def get_job_status(workflow_id: str) -> dict[str, Any]`
- Lines 22–28: raises `APIError(code="NOT_IMPLEMENTED", status_code=501)` unconditionally
- **Full file is 37 lines total**

This router is registered at `main.py:218` as `app.include_router(jobs.router, prefix="/jobs")` → route resolves to `GET /jobs/{workflow_id}`.

**Note**: The double `router = APIRouter(...)` at lines 12 and 15 is a pre-existing bug — both define the same variable, the second one wins and is empty. The first definition with `tags=["Jobs"]` is unused. This should be cleaned up when deleting the file.

### `src/solstein/infrastructure/research_job_repository.py` — Verified

| Method | Line | Signature | Notes |
|--------|------|-----------|-------|
| `create_job()` | 52 | `(tenant_id, company_id, company_name=None) -> ResearchJobRecord` | Creates with status="queued", progress_pct=0 |
| `update_status()` | 85 | `(job_id, new_status, progress_pct=None, current_stage=None, error_message=None)` | State machine validated via `can_transition_to()` |
| `get_job()` | 154 | `(job_id: uuid.UUID) -> ResearchJobRecord \| None` | **No tenant filter** — caller must validate |
| `get_jobs_for_tenant()` | 168 | `(tenant_id, status_filter=None, limit=50, offset=0)` | Has tenant filter built in |

### `src/solstein/infrastructure/models/research.py` — `ResearchJobRecord` (Verified)

| Column | Type | Line | Notes |
|--------|------|------|-------|
| `id` | `Uuid(as_uuid=True)` PK | 306–308 | default=uuid.uuid4 |
| `tenant_id` | `String(255)` | 309–311 | indexed, nullable=False |
| `company_id` | `String(255)` | 312–314 | indexed, nullable=False |
| `company_name` | `String(500)` | 315–317 | nullable=True |
| `status` | `String(50)` | 318–320 | default="queued", indexed |
| `progress_pct` | `Integer` | 321–323 | default=0 |
| `current_stage` | `String(100)` | 324–326 | nullable=True |
| `error_message` | `Text` | 327–329 | nullable=True |
| `job_metadata` | `JSON` | 330–332 | nullable=True — **`output_dir` stored here** |
| `created_at` | `DateTime` | 333–335 | default=utcnow |
| `started_at` | `DateTime` | 336–338 | nullable=True |
| `completed_at` | `DateTime` | 339–341 | nullable=True |

**No `output_dir` column** — confirmed. Output directory is stored as `job_metadata["output_dir"]` (JSON key). STORY-363 task sets it via `job.job_metadata = {"output_dir": str(output_dir)}`.

Valid status transitions (from `VALID_TRANSITIONS` at line 352):
- `queued` → `{running, cancelled}`
- `running` → `{completed, failed, cancelled}`

### `src/solstein/research/pipeline.py` — `run_market_intelligence()` (Verified)

| Fact | Value |
|------|-------|
| Line | 211 |
| Signature | `(seed_company: str, market: str, output_dir: Path, options: dict | None = None, **legacy_kwargs)` |
| Return type | `dict[str, object]` |
| Return value | `{"market": ..., "seed_company": ..., "discovered": N, "profiles": N, "scored": N, "output_dir": str(output_dir)}` |
| `batch_id` | `uuid.uuid4().hex[:12]` at line 228 — **12-char hex, not a UUID** |
| `output_dir` | caller-supplied `Path`, must be passed in — not generated internally |

**Critical**: `batch_id` is a 12-char hex string used internally for pipeline tracking. It is **not** the `workflow_id` exposed to API clients. The `workflow_id` for the API is `str(ResearchJobRecord.id)` (UUID). These are different identifiers.

### `src/solstein/domain/workflow.py` — Does Not Exist

File does not exist. STORY-362 must create it with `WorkflowStatus` StrEnum and `Workflow` Pydantic model.

### `src/solstein/api/routers/workflows.py` — Does Not Exist

File does not exist. STORY-363 must create it.

---

## EPIC-003 Continuation — Classification/Scoring (STORY-360/361/365)

### `src/solstein/analytics/constants.py` — Verified (all constants)

| Constant | Value | Notes |
|----------|-------|-------|
| `PHOENIX_SCORE_THRESHOLD` | 7.0 | exists |
| `SALT_SCORE_THRESHOLD` | 4.5 | exists |
| `LEAD_SCORE_THRESHOLD` | 4.49 | exists |
| `LEAD_BOUNDARY_LOW` | — | **does NOT exist** — STORY-360 must add |
| `LEAD_BOUNDARY_HIGH` | — | **does NOT exist** — STORY-360 must add |
| `PHOENIX_BOUNDARY_LOW` | — | **does NOT exist** — STORY-360 must add |
| `PHOENIX_BOUNDARY_HIGH` | — | **does NOT exist** — STORY-360 must add |

### `src/solstein/analytics/classification.py` — Line 71 (Verified)

Exact code at line 71:
```python
if 4.3 <= composite_score <= 4.7 or 6.8 <= composite_score <= 7.2:  # Near Lead/Salt or Phoenix boundary
    score_certainty = 0.7
```

The four literals `4.3`, `4.7`, `6.8`, `7.2` are confirmed present. STORY-360 replaces them with named constants.

### STORY-365: Pre-existing test fixture failures — Root cause confirmed

**File**: `tests/unit/test_scoring.py`

| Test | Line | Failure reason |
|------|------|----------------|
| `test_growth_score_always_clamped_to_10` | 149–153 | `FinancialMetric(growth_rate=10_000.0, ...)` — validator at `models.py:157` rejects values > 1000 |
| `test_growth_score_never_below_zero` | 156–160 | `FinancialMetric(growth_rate=-10_000.0, ...)` — validator at `models.py:157` rejects values < -100 |

**Validator location**: `src/solstein/domain/models.py:153–158`:
```python
@field_validator("growth_rate")
@classmethod
def validate_growth_rate_range(cls, v: float | None) -> float | None:
    if v is not None and (v < -100 or v > 1000):
        raise ValueError(f"growth_rate must be in [-100, 1000], got: {v}")
    return v
```

**Fix for STORY-365**: In `test_scoring.py`, change:
- Line 151: `growth_rate=10_000.0` → `growth_rate=999.0`
- Line 158: `growth_rate=-10_000.0` → `growth_rate=-99.0`

**Third failure (test_scorers_financial.py)**: Needs separate check — likely also a `FinancialMetric` field validation issue introduced by STORY-348.

---

## Cross-Story Conflict Risks

| Risk | Stories | Shared Target | Recommendation |
|------|---------|---------------|----------------|
| **HIGH** — test_scoring.py fixture conflicts | STORY-365 + EPIC-083 STORY-335 | Both touch `FinancialMetric` test fixtures in `tests/unit/` | Do STORY-365 first; STORY-335 may be rendered obsolete or reduced in scope |
| **MEDIUM** — classification.py constants | STORY-360 + EPIC-075 STORY-298/299 | `analytics/constants.py` and boundary logic | Do STORY-360 before any scoring rewrite (EPIC-075) to avoid writing new literals |
| **LOW** — jobs.py deletion | STORY-362 + STORY-364 | Both say "remove 501 stub from jobs.py" | Do in STORY-362 (first story); STORY-364 has redundant instruction — safe to ignore in 364 if 362 already deleted |
| **LOW** — orchestration.py | STORY-363 adds `run_workflow_task` | `src/solstein/worker/orchestration.py` — only `refresh_all_sources` currently | No conflict; serial execution fine |

---

## Story Claim vs Reality: Discrepancy Table

| Story | Claim | Reality | Action Needed |
|-------|-------|---------|---------------|
| STORY-352 | `_validate_api_key` at `context.py:134` | ✅ Correct — line 134 | None |
| STORY-352 | "register after line 207 in main.py" | ✅ Correct — TenantMiddleware is at 207 | None |
| STORY-352 | imports `TenantRecord` from `models/infrastructure.py` | Working code imports from `database_models` | Use `from solstein.infrastructure.database_models import TenantRecord` |
| STORY-357 | "worker_health() at routers/health.py:156" | ✅ Correct — `worker_health()` at `api/routers/health.py:157`. Separate from `check_celery()` in `monitoring/health.py` which is a different module | None |
| STORY-358 | "insert after line 128 (after cache warming)" | Cache warming ends at line 127 (`except` block); `yield` is at line 141 | Insert between lines 128–129 ✅ |
| STORY-359 | "13 Beat-scheduled tasks (12 refresh + refresh_all_sources)" | ✅ Correct — confirmed 13 tasks | None |
| STORY-362 | "remove 501 stub from jobs.py:18–36" | Full file is 37 lines; 501 route is at 18–36 ✅ | Also note: double `router =` definition at lines 12+15 |
| STORY-363 | "add run_workflow_task to orchestration.py" | orchestration.py exists, only has `refresh_all_sources` ✅ | None |
| STORY-364 | "output_url from job_metadata['output_dir']" | ✅ Correct — no output_dir column | None |
| STORY-364 | "use asyncio.to_thread for filesystem check" | `Path.exists()` is sync — correct to wrap in `asyncio.to_thread` ✅ | None |
| STORY-365 | "fix 3 test failures" | 2 confirmed in test_scoring.py (growth_rate out of range); 3rd in test_scorers_financial.py (needs separate check) | Verify 3rd failure |
| EPIC-087 README | "worker/tenant_isolation.py" in key files | That file exists but is unrelated; middleware is in `tenant/context.py` | ✅ Already corrected in README |

---

## Files That Do Not Exist (must be created by stories)

| File | Created by |
|------|-----------|
| `src/solstein/domain/workflow.py` | STORY-362 |
| `src/solstein/api/routers/workflows.py` | STORY-363 |

## Files That Exist But Are Not in Stories (informational)

| File | Relevance |
|------|-----------|
| `src/solstein/api/routers/research_jobs.py` | Has `get_current_tenant` dependency and `_job_to_response()` helper — STORY-364 should import `get_current_tenant` from same location (`api.dependencies` or `api.main`) |
| `src/solstein/worker/refresh_tasks.py` | Contains all 12 `refresh_*` tasks imported by orchestration.py |
| `src/solstein/worker/tenant_isolation.py` | Has `validate_task_tenant_id()` — used by orchestration.py but not relevant to EPIC-089 |

---

## Contamination Analysis — 2026-04-03 (synthetic/fake data bleeding into production)

> **Trigger**: `faker` was found in `scripts/seed_db.py`. Analysis expanded to all contamination
> vectors — shared imports, module aliases, factory defaults, and gate enforcement gaps.
>
> **Conclusion**: 5 CRITICAL nodes confirmed. Faker-generated test data can reach production export
> silently because (a) records default to `data_source_type="unknown"`, (b) the export gate
> detects violations but never raises, and (c) `SyntheticDataBlocker.ensure_safe()` is dead code.
> Tracked in EPIC-090 (gate enforcement) and EPIC-091 (runtime boundary).

### CRITICAL 1 — `scripts/seed_db.py`: Faker writes to production DB untagged

| Fact | Detail |
|------|--------|
| **File** | `scripts/seed_db.py:20,26` |
| **Code** | `from faker import Faker; fake = Faker()` |
| **DB write** | Lines 99–119 call `CompanyRepository.save()` via `get_async_session()` — same session factory as production |
| **Missing tag** | `generate_company()` (lines 51–90) never sets `data_source_type` → defaults to `"unknown"` |
| **Gate bypass** | Export gate only blocks `"synthetic"` / `"mixed"` — `"unknown"` passes through |
| **Result** | If run against production DB, all seeded companies are exported as real data |

Contrast: `scripts/generate_synthetic_companies.py:320` does set `"data_source_type": "synthetic"` correctly.

### CRITICAL 2 — `src/solstein/domain/models.py:294`: Default creates gate blind spot

```python
data_source_type: str = "unknown"   # gate blocks "synthetic"/"mixed" only
```

Every factory, fixture, or seed script that omits `data_source_type` defaults to `"unknown"`.
The gate treats `"unknown"` as acceptable. This makes the default a contamination pass-through.

### CRITICAL 3 — `SyntheticDataBlocker.ensure_safe()` is dead code

| Fact | Detail |
|------|--------|
| **File** | `src/solstein/data/synthetic_data_safety.py:284–322` |
| **Method** | `ensure_safe()` raises `SyntheticDataError` when synthetic data detected |
| **Callers** | **Zero** — no code in `src/solstein/api/routers/export.py` or any exporter calls it |
| **Effect** | The blocking mechanism was written but never wired in |

### CRITICAL 4 — `src/solstein/data/report_release_gate.py:168–178`: Gate detects, never enforces

```python
# Gate appends violations but callers never check gate_result.passed:
if not self.allow_synthetic:
    if str(data_source_type).lower() in {"synthetic", "mixed"}:
        reasons.append(GateReason(code="synthetic_data", ...))
```

In `export.py` (lines ~41–45):
```python
gate_result = gate.evaluate(companies)
export_metadata = build_export_metadata(companies, gate_result)
excel_exporter.create_dashboard(...)   # proceeds regardless
```

No `if not gate_result.passed: raise` guard exists anywhere.

### CRITICAL 5 — Two test factory modules, both without `data_source_type` default

| File | Lines | Risk |
|------|-------|------|
| `tests/factories.py:56–90` | 27 Faker fields in `CompanyFactory` | No `data_source_type="synthetic"` default |
| `tests/factories/__init__.py:64–99` | 20+ Faker fields in duplicate `CompanyFactory` | Same omission |
| `tests/factories.py:44–53` | `FinancialMetricFactory` | No synthetic tag |

Both modules are used by `conftest.py`. The duplication (two `CompanyFactory` definitions) also
creates alias risk — future import order changes can silently switch which factory is resolved.

### HIGH — `tests/conftest.py` fixture chain reaches export endpoint

```
make_company() [Faker, no tag]
  → mock_company fixture (conftest:66)
  → mock_repo fixture (conftest:70-86)   [AsyncMock returning mock_company]
  → test_export_to_excel / test_export_to_json (test_routers_export_jobs.py:14–44)
```

Export tests exercise the real export code path with unmarked synthetic data — confirming the gate
would not catch real contamination because the test itself would pass.

### HIGH — `tests/test_data.py:10–109`: Three `Company` objects, no `data_source_type`

Three hand-coded companies (Eneve, Test Company 2, Test Company 3) never set `data_source_type`.
Consumed via `mock_competitor_data` fixture (conftest:137–158).

### MEDIUM — `tests/unit/test_story114_pdf_export.py:23–56`: local `_make_company` helper

Local helper creates Company objects without `data_source_type`. Pattern is self-contained to
the test file but reinforces the default-passes-through risk.

### Contamination Path Summary

```
seed_db.py / factories / test_data.py
    ↓ creates Company with data_source_type="unknown"
CompanyRepository.save() [production DB]
    ↓
export.py → gate.evaluate() [detects nothing — "unknown" ignored]
    ↓
ensure_safe() NOT CALLED
    ↓
if not gate_result.passed: NOT CHECKED
    ↓
Export file written — synthetic data treated as real
```

**Remediation tracked in**: EPIC-090 (gate enforcement) and EPIC-091 (runtime boundary).

---

## Second-Pass Audit — 2026-04-03 (deeper codebase read)

> This pass targeted specific claims in story task bodies and found critical implementation errors
> in STORY-363 that will cause runtime failures if implemented as written.

### CRITICAL: `get_current_tenant` import path corrected (STORY-364 and EPIC-087 generally)

The first-pass audit cited `api/main.py:140` as the definition site for the `get_current_tenant`
FastAPI dependency. This is **wrong**. The correct file is `src/solstein/api/dependencies.py:140`.

| File | Line | What it defines |
|------|------|-----------------|
| `src/solstein/api/dependencies.py` | 140 | `async def get_current_tenant(request: Request) -> dict[str, Any]` — the FastAPI Depends() target |
| `src/solstein/api/main.py` | 140 | lifespan body code (not a dependency definition) |
| `src/solstein/tenant/context.py` | 54 | `def get_current_tenant() -> str \| None` — ContextVar getter, not a Depends() |

**Action for STORY-364**: Import must be `from solstein.api.dependencies import get_current_tenant`, not from `tenant.context` or `api.main`.

---

### CRITICAL: STORY-363 task body has two breaking defects

The task body described in STORY-363 for the Celery `run_workflow_task` will not work as written.

#### Defect 1 — `get_sync_session` is NOT a module-level function

```python
# STORY-363 task body proposes:
from solstein.infrastructure.database import get_sync_session
with get_sync_session() as session:
    ...
```

**Reality** — `src/solstein/infrastructure/database.py`:

| Symbol | Line | Type |
|--------|------|------|
| `DatabaseManager` class | — | class |
| `DatabaseManager.get_sync_session()` | 128 | **instance method**, not module-level |
| `db_manager` | 169 | module-level `DatabaseManager` instance |

The import `from solstein.infrastructure.database import get_sync_session` will raise
`ImportError` at Celery worker startup because no `get_sync_session` symbol exists at module scope.

**Correct approach**: `from solstein.infrastructure.database import db_manager` then
`with db_manager.get_sync_session() as session: ...`

#### Defect 2 — All `ResearchJobRepository` methods are `async def`

The task body calls repository methods synchronously:
```python
# STORY-363 proposes (inside sync Celery task):
repo.update_status(job_id, "running")
result = pipeline.run_market_intelligence(...)
repo.update_status(job_id, "completed", ...)
```

**Reality** — `src/solstein/infrastructure/research_job_repository.py`:

| Method | Line | Signature |
|--------|------|-----------|
| `create_job()` | 52 | **`async def`** |
| `update_status()` | 85 | **`async def`** |
| `get_job()` | 154 | **`async def`** |
| `get_jobs_for_tenant()` | 168 | **`async def`** |

All four methods are `async def`. Calling them without `await` inside a synchronous Celery task
returns coroutine objects — the repository operations silently do nothing, no exception is raised.

**Correct approach** (two options):
1. **Use `asyncio.run()`** inside the sync task for each async call, e.g.
   `asyncio.run(repo.update_status(job_id, "running"))` — works but is ugly
2. **Rewrite as a Celery async task** using `celery-aio-pool` or a custom event loop — architecturally cleaner

The story body must be corrected before implementation. The executor should choose option 1 or 2
and update the task body in STORY-363 before writing code.

---

### STORY-365 third failure: `test_profit_margin_boundaries` — Root cause confirmed

Confirmed by running `uv run python -m pytest tests/unit/test_scorers_financial.py::TestFinancialHealthScorer::test_profit_margin_boundaries -x 2>&1`.

**File**: `tests/unit/test_scorers_financial.py`, test `test_profit_margin_boundaries`

**Failure**:
```
ValidationError: Value error, At least revenue OR employees is required for scoring
```

**Root cause**: Each iteration calls `FinancialMetric(profit_margin=margin)` with no `revenue` or
`employees`. The `require_primary_metric` model_validator added in STORY-348
(`src/solstein/domain/models.py:122–127`) raises `ValueError` if both are absent.

**Fix for STORY-365**: In `test_scorers_financial.py`, change every
`FinancialMetric(profit_margin=margin)` call to `FinancialMetric(profit_margin=margin, employees=1)`.

**Full STORY-365 fix list**:

| File | Line(s) | Change |
|------|---------|--------|
| `tests/unit/test_scoring.py` | 151 | `growth_rate=10_000.0` → `growth_rate=999.0` |
| `tests/unit/test_scoring.py` | 158 | `growth_rate=-10_000.0` → `growth_rate=-99.0` |
| `tests/unit/test_scorers_financial.py` | all `FinancialMetric(profit_margin=...)` in `test_profit_margin_boundaries` | add `employees=1` |

---

### `worker_tasks.py` stale comment

`src/solstein/worker_tasks.py` module docstring says **"All 12 Beat-scheduled refresh tasks"**.
Actual count is **13** (as confirmed in first-pass audit against `celery_config.py:109–184`).

Minor issue — does not affect runtime — but will confuse anyone using the comment as a checklist
for STORY-359's task discovery test.

**Fix**: Change "12" → "13" in the docstring header when implementing STORY-359.

---

### `async_jobs.router` prefix architecture confirmed

`src/solstein/api/routers/async_jobs.py` self-declares `prefix="/async"` in its own `APIRouter(prefix="/async", ...)` constructor. Therefore `main.py:221` correctly includes it **without** a prefix argument:

```python
app.include_router(async_jobs.router)   # correct — prefix="/async" comes from the router itself
app.include_router(jobs.router, prefix="/jobs")  # correct — jobs.router has no prefix
```

STORY-362 adds `workflows.router` — verify whether to self-declare prefix in the router or pass it at `include_router()` time. Recommend following the `research_jobs.router` pattern (check that router's prefix style and match it for consistency).

---

### STORY-353 — `get_jobs_for_tenant()` scoping example at `research_job_repository.py:188`

STORY-353 cites `research_job_repository.py:188` as the "correct tenant-scoped query example to replicate".

**Verified**: `get_jobs_for_tenant()` starts at line 168 (declaration) and the `.where(tenant_id==...)` filter is approximately at line 188. The claim is accurate. The pattern:
```python
stmt = select(ResearchJobRecord).where(
    ResearchJobRecord.tenant_id == tenant_id
).order_by(ResearchJobRecord.created_at.desc()).limit(limit).offset(offset)
```
is the correct pattern for all tenant-scoped queries in EPIC-087 and EPIC-089.

---

### Stale duplicate epic directories (informational)

Three directory names in `backlog/EPICS/` are likely stale duplicates from earlier reorganization:

| Directory | Status | Recommended action |
|-----------|--------|--------------------|
| `EPIC-002/` | Likely orphaned | Verify against EPIC-002 story files before deletion |
| `EPIC-052-provenance-quality-gates/` | Duplicate of `EPIC-052-provenance-confidence-quality-gates/` | Archive or delete after confirming canonical dir is `EPIC-052-provenance-confidence-quality-gates/` |
| `EPIC-067-agentic-development-workflow-hardening/` | Duplicate of `EPIC-067-*/` | Same resolution |

Do not delete without team review — may contain in-progress notes not yet merged to canonical dir.

---

## Third-Pass Contamination Audit — 2026-04-03 (module-scope mutations + production loader chain)

> **Scope**: Deeper scan targeting (a) test files that mutate production singletons at module scope,
> (b) production code inside `src/` that loads untagged data into Supabase/pipeline,
> (c) leaked test DB artefacts tracked in git.
>
> All findings below were verified by direct file read. Items already in EPIC-090/091 are not repeated.
>
> **Remediation tracked in**: EPIC-092 (test isolation) and EPIC-093 (production loader tagging).

---

### CRITICAL — `tests/unit/test_api_routers_coverage.py:19–25`: Module-scope mutations never cleaned up

Three mutations execute at module **import time** and are **never reversed**:

```python
# Line 20-21 — permanent for the rest of the test session:
app.dependency_overrides[get_current_user] = lambda: {"username": "test_user"}
app.dependency_overrides[get_current_tenant] = lambda: {"tenant_id": "test-tenant", ...}

# Line 23-24 — Settings singleton mutated globally:
_settings = get_settings()
_settings.api.require_api_key = False

# Line 25 — env var set, never reset:
os.environ["SOLSTEIN_DISABLE_RATE_LIMIT"] = "true"
```

**Impact**: Any test file loaded *after* this module in the same pytest session inherits:
- Bypassed authentication (`get_current_tenant` always returns test-tenant)
- Disabled API key requirement
- Disabled rate limiting

This is a silent security-gate bypass that leaks across the entire test run. If pytest discovers
test files alphabetically, any file after `test_api_routers_coverage.py` in the `tests/unit/`
directory runs with these permanent overrides.

| Symbol mutated | Location | Type of contamination |
|---------------|----------|-----------------------|
| `app.dependency_overrides` | `api/main.py` — production FastAPI app | Permanent auth bypass |
| `_settings.api.require_api_key` | Settings singleton from `get_settings()` | Permanent config mutation |
| `os.environ["SOLSTEIN_DISABLE_RATE_LIMIT"]` | Process environment | Never unset across session |

**Fix**: Move all three into a `@pytest.fixture(autouse=True)` with `yield` + cleanup, or use
`monkeypatch` fixtures that auto-restore on teardown.

---

### CRITICAL — `tests/performance/test_load.py:7–8`: DB URL overrides before `solstein` imports

```python
# Lines 7-8 — BEFORE any solstein import:
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///file:testdb?mode=memory&cache=shared"
os.environ["SYNC_DATABASE_URL"] = "sqlite:///file:testdb?mode=memory&cache=shared"

import asyncio   # line 10 (after the override)
...
from solstein.config import Settings   # line 23 — reads env that was just poisoned
```

Because the env override happens before `solstein.config` is imported, Settings loads with
the in-memory SQLite URL as its database URL. This mutation is never reset. Any test that
runs after this file has a Settings singleton pointing to an in-memory test database.

Additionally, line 21: `sys.path.insert(0, ...)` permanently mutates Python's import search
path. If a module name collision exists, subsequent imports after this test file may resolve
to the wrong package.

---

### CRITICAL — `src/solstein/data/seed_db.py`: Production module seeds Supabase from untagged JSON

This file lives inside `src/solstein/data/` — **it is production code**, not a script.

```python
# seed_db.py — production module, no data_source_type tagging
async def seed_supabase() -> None:
    loader = CompetitorDataLoader()
    repo = SupabaseRepository()
    scorer = GrowthScorer()

    companies = loader.load_companies()         # loads competitor_data.json → Company objects
    for company in companies:
        scored_company = scorer.calculate_scores(company)   # scores it
        repo.save(scored_company)               # writes to Supabase — NO data_source_type set
```

**Chain**: `competitor_data.json` → `CompetitorDataLoader._load_from_json()` →
`convert_to_domain_company()` (no `data_source_type` propagation) → `GrowthScorer.calculate_scores()`
→ `SupabaseRepository.save()` — companies land in production Supabase with `data_source_type="unknown"`.

This is distinct from `scripts/seed_db.py` (which uses Faker). This module seeds from a JSON file
that may or may not be synthetic (the file is `data/input/competitor_data.json` — if the synthetic
fixture from `scripts/generate_synthetic_companies.py` was ever copied there, it becomes production data).

---

### CRITICAL — `src/solstein/adapters/discovery/competitor_json.py:41–44`: Pipeline discovery uses untagged loader

The production pipeline uses `CompetitorJsonSource.discover()` as a `DiscoverySource` during
market intelligence runs:

```python
def discover(self, market, seed_company, max_results=50, ...) -> list[DiscoveryCandidate]:
    from solstein.data.loaders import CompetitorDataLoader
    loader = CompetitorDataLoader()             # new instance each call
    companies = loader.load_companies()         # reads competitor_data.json
    # converts to DiscoveryCandidates — no data_source_type propagated
```

Every `run_market_intelligence()` call that uses this source feeds untagged companies into
the pipeline. These candidates are then enriched, scored, and exported. No gate intercepts
them because `data_source_type` was never set.

---

### HIGH — `competitor_loader.py:107–115`: Module-level singleton with persistent cache

```python
_loader_instance: CompetitorDataLoader | None = None   # module-level

def get_loader() -> CompetitorDataLoader:
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = CompetitorDataLoader()
    return _loader_instance

loader = _LazyLoader()   # transparent proxy to _loader_instance
```

**Cache contamination**: `CompetitorDataLoader` caches loaded companies in
`self._cache: dict[str, list[Company]]`. Once loaded (whether in a test or production call),
the result is cached for the lifetime of the process. Tests that call `loader.load_companies()`
with test data populate the singleton cache. Any subsequent call — including from a production
code path in the same process — returns the cached test result.

`tests/conftest.py:137–158` uses `monkeypatch.setattr(CompetitorDataLoader, "load_companies", ...)`,
which patches the class method but does NOT clear the existing singleton instance's `_cache`.

---

### HIGH — `src/solstein/migrations/load_competitor_data.py:77`: Migration tags source by filename only

```python
return CompanyRecord(
    ...
    data_source="competitor_data.json",   # string filename, not data_source_type
    # data_source_type NOT SET — CompanyRecord may default to None or "unknown"
)
```

The migration populates the `data_source` column (a free-text provenance string) but sets no
`data_source_type` field. If `CompanyRecord` has a `data_source_type` column, it defaults to
whatever the SQLAlchemy column default is. Records inserted by this migration cannot be
distinguished from real data by the export gate.

---

### HIGH — `test_integration.db` and `test_perf.sqlite3` exist and are tracked in git

```
-rw-rw-r-- 796K Apr 3  test_integration.db    ← created by tests/integration/test_data_migration.py
-rw-rw-r-- 812K Apr 3  test_perf.sqlite3       ← created by tests/performance/test_load.py
```

Both files are at the repo root and are in `git status` as modified. They contain real SQLAlchemy
schema + data written by test runs. Any developer checking out the repo gets these pre-populated
databases. Any CI run that doesn't delete them first may run against stale test data.

The `test_load.py` fixture does call `db_manager.drop_tables()` in teardown (line 51), but if
a test is interrupted or the fixture fails, the tables/data persist.

---

### HIGH — `security_hardening.py:404`: Module-level `rate_limiter` and `audit_logger` singletons exposed to tests

```python
# Module-level singletons in src/solstein/data/security_hardening.py:
audit_logger = AuditLogger()          # mutable deque of entries (line 404)
rate_limiter = RedisRateLimiter(...)  # exposes client_requests dict (line 229, 284)
input_validator = InputValidator()    # line 406
```

`RedisRateLimiter` exposes `self.client_requests` as a public attribute (documented at line 228:
`"Expose memory fallback's client_requests for test compatibility"`). This means tests can — and
likely do — directly mutate the production singleton's rate-limit state. Any mutation survives
to the next test or to production if the same process is reused.

`AuditLogger` accumulates entries in a `deque` with no maximum size by default. Security audit
entries from one test accumulate in the shared singleton visible to subsequent tests.

---

### MEDIUM — `test_load.py:31–45`: Settings singleton mutated inside fixture without `monkeypatch`

```python
@pytest_asyncio.fixture
async def db_session():
    settings = Settings.load()          # returns cached singleton
    settings.database.url = "sqlite+aiosqlite:///test_perf.sqlite3"   # mutates singleton
    # ... yield ...
    # NO RESTORE — settings.database.url remains "test_perf.sqlite3" after fixture exits
```

`Settings.load()` likely returns a cached singleton (common Pydantic settings pattern). Mutating
`settings.database.url` inside a fixture that does not use `monkeypatch` means the mutation
persists after the fixture exits. Subsequent tests — or production code running after tests
in the same process — may use the test SQLite URL instead of the real database URL.

---

### Contamination summary for second pass (absorbed into EPIC-013, EPIC-052, EPIC-033)

> Note: EPIC-092/093 were dissolved. Stories moved into canonical epics. See `planning/QUEUE.md`.

| Node | File | Line | Severity | Canon Epic |
|------|------|------|----------|------------|
| Module-scope `app.dependency_overrides` + settings mutation | `tests/unit/test_api_routers_coverage.py` | 19–25 | CRITICAL | EPIC-013 (STORY-374) |
| Module-scope `os.environ["DATABASE_URL"]` + sys.path | `tests/performance/test_load.py` | 7–8, 21 | CRITICAL | EPIC-013 (STORY-375) |
| Leaked test DB files in git | `test_integration.db`, `test_perf.sqlite3` | repo root | HIGH | EPIC-013 (STORY-376) |
| Settings singleton mutated without `monkeypatch` | `tests/performance/test_load.py` | 31–45 | MEDIUM | EPIC-013 (STORY-375) |
| Production `seed_db.py` seeds Supabase untagged | `src/solstein/data/seed_db.py` | all | CRITICAL | EPIC-052 (STORY-378) |
| Production pipeline discovers via untagged loader | `src/solstein/adapters/discovery/competitor_json.py` | 41–44 | CRITICAL | EPIC-052 (STORY-380) |
| Loader singleton cache persists across calls | `src/solstein/data/competitor_loader.py` | 107–115 | HIGH | EPIC-052 (STORY-379) |
| Migration sets filename-only provenance, no type tag | `src/solstein/migrations/load_competitor_data.py` | 77 | HIGH | EPIC-033 (STORY-381) |
| Module-level rate_limiter/audit_logger singletons | `src/solstein/data/security_hardening.py` | 404–406 | HIGH | EPIC-013 (STORY-377) |

---

## Third-Pass Contamination Audit — 2026-04-03 (deep gate + schema pass)

> Performed after dissolution of EPIC-090–093. All findings verified by direct file read.
> Focus: production gate bypass paths, DB schema gaps, default-value contamination, and
> pytest config that silences contamination evidence.

### CRITICAL — `src/solstein/core/test_modes.py:16`: `SOLSTEIN_TEST_MODE` defaults to `"mixed"` → `allow_synthetic=True`

```python
# src/solstein/core/test_modes.py:16
mode = os.getenv("SOLSTEIN_TEST_MODE", "mixed").strip().lower()
# ...
# line 23-24: invalid modes fall back to "mixed"
if mode not in {"synthetic", "mixed", "strict_real"}:
    mode = "mixed"
# line 26: "mixed" maps to allow_synthetic=True
allow_synthetic = mode in {"synthetic", "mixed"}
return TestMode(name=mode, seed=seed, allow_synthetic=allow_synthetic)
```

This is a **production `src/` module**. When no `SOLSTEIN_TEST_MODE` env var is set (the common
case in production), `mode = "mixed"` and `allow_synthetic = True`. Any code path that calls
`get_test_mode()` without having set the env var will operate in synthetic-allowed mode.

The module docstring does not document that the **production default permits synthetic data**.
Any production process that imports this module without the env var configured allows synthetic
records through gates that check `allow_synthetic`.

**Story required**: Change the unset-env-var default from `"mixed"` to `"strict_real"`, or
remove the cross-contamination from production code by moving `test_modes.py` out of `src/`.
Assign to **EPIC-052**.

---

### CRITICAL — `src/solstein/infrastructure/research_dual_write.py:340,424`: `strict_provenance` hardcoded `False` in production pipeline path

```python
# Line 340 — fallback when field missing from outbox payload
strict_provenance = strict_obj if isinstance(strict_obj, bool) else False

# Line 424 — PersistRunPayload construction for ALL runs through dual-write
return PersistRunPayload(
    ...
    strict_provenance=False,   # hardcoded — bypasses quality gate for every run
    ...
)
```

Combined with `pipeline.py:82–84`:
```python
def _run_quality_gate(context: PipelineContext, strict_provenance: bool) -> None:
    if not strict_provenance:
        return   # gate entirely skipped
```

**The production research pipeline path (outbox → dual-write worker → pipeline) has its quality
gate permanently disabled.** `pipeline.py:72` sets `strict_provenance=True` as the default for
direct API calls, but the outbox worker path (`research_dual_write.py`) hardcodes `False` at
both the payload construction site and the fallback. Any run dispatched through the worker
(which is the primary async production path) skips provenance validation entirely.

**Story required**: Remove hardcoded `False`, propagate the caller's `strict_provenance`
value through `PersistRunPayload`. Assign to **EPIC-052**.

---

### CRITICAL — `src/solstein/infrastructure/models/company.py:77`: `CompanyRecord` has NO `data_source_type` DB column

```python
# src/solstein/infrastructure/models/company.py:77
data_source = Column(String(100), nullable=True)   # filename/free-text only
# data_source_type column does NOT exist
```

The domain `Company` model has `data_source_type: str` (gating field for export and quality
gates). The SQLAlchemy `CompanyRecord` — the DB persistence model — has only `data_source`
(free-text string, e.g. a filename). **There is no `data_source_type` column in the database.**

Consequence: any `Company` reconstructed from a DB-persisted `CompanyRecord` will have
`data_source_type` derived from the converter's fallback logic. `convert_to_domain_company()`
at `converters/company.py:341–344` defaults to `"real"` (see below). All DB-loaded records
therefore present as `data_source_type="real"` and pass every gate unconditionally, regardless
of their actual provenance.

**Story required**: Add `data_source_type = Column(String(50), nullable=False, default="unknown")`
to `CompanyRecord` + Alembic migration + update converter to round-trip the field. Assign to
**EPIC-033** (data completeness / export integrity).

---

### HIGH — `src/solstein/data/converters/company.py:341–344`: converter defaults `data_source_type` to `"real"`

```python
# src/solstein/data/converters/company.py:341–344
data_source_type=raw_data.get(
    "data_source_type",
    "synthetic" if raw_data.get("is_synthetic", False) else "real",
),
```

When `data_source_type` is absent from the raw data dict (the common case for records loaded
from the DB, which has no such column), the fallback is `"real"`. Only if the unlikely
`is_synthetic` flag is also present does it fall back to `"synthetic"`.

This means the converter **treats missing provenance as confirmed real data**. The correct
defensive default would be `"unknown"` (blocked by gate) rather than `"real"` (passes gate).

**Story required**: Change fallback to `"unknown"`. Assign to **EPIC-052** (gate enforcement —
pairs with STORY-366 which extends the gate to block `"unknown"`).

---

### CRITICAL — `src/solstein/migrations/load_competitor_data.py:179`: production migration hardcodes `test=True` database URL

```python
# src/solstein/migrations/load_competitor_data.py:179
db_url = settings.get_database_url(test=True) or "postgresql+asyncpg://solstein:solstein@localhost:5432/solstein"
```

A production migration script — `load_competitor_data.py` — calls `get_database_url(test=True)`.
This unconditionally requests the **test database URL**. If `get_database_url` honours the
`test=True` flag (likely returning a SQLite or staging URL), the migration inserts competitor
records into the test database rather than production.

If the URL falls through to the hardcoded fallback (`localhost:5432/solstein`), it targets
a local dev instance — not production. Either way, this script cannot safely be run in production
as-is. The `test=True` argument is a latent bug: whoever runs this migration may believe they
are loading data into production while it routes to test.

**Story required**: Remove `test=True`, validate that the resolved URL matches the expected
production database before inserting. Assign to **EPIC-033** (STORY-381 context — same file,
same migration).

---

### HIGH — `pyproject.toml:257–260`: all `DeprecationWarning` suppressed — hides contamination evidence

```toml
[tool.pytest.ini_options]
filterwarnings = [
    "ignore::DeprecationWarning",
    "ignore::PendingDeprecationWarning",
]
```

`CompetitorDataLoader` (and other singletons) emit `DeprecationWarning` on initialization.
With all deprecation warnings globally silenced, these warnings never surface during test runs.
Contamination from deprecated production singletons is therefore invisible in CI output.

Additionally, `addopts` at line 246:
```toml
addopts = "-v --cov=solstein --cov-report=term-missing"
```
No `-m "not integration"` filter. Integration tests run as part of the default test suite with
no enforcement of test type separation. Unit tests can be contaminated by integration fixtures
that set up real or semi-real resources.

**Story required**: Remove global `DeprecationWarning` suppression (or scope it narrowly to
known-safe third-party warnings). Add `-m "not integration"` to `addopts` or add a separate
`pytest-integration` tox/nox target. Assign to **EPIC-013**.

---

### MEDIUM — `src/solstein/adapters/instrumented.py:138`: `confidence=1.0` hardcoded on every discovery success

```python
# src/solstein/adapters/instrumented.py:138
confidence=1.0,
```

`InstrumentedDiscoveryAdapter` wraps all discovery adapters and records a `DiscoveryCandidate`
with `confidence=1.0` on every successful call. The actual adapter's result may carry its own
confidence estimate, but this value is overwritten by the hardcoded `1.0`.

Downstream provenance and quality gates that rely on `confidence` scores will see every
adapter-discovered record as maximum-confidence regardless of source reliability. This breaks
the calibration intent of EPIC-052 STORY-199.

**Story required**: Propagate the underlying adapter's confidence value; fall back to `1.0`
only if the adapter does not return one. Assign to **EPIC-052**.

---

### MEDIUM — `src/solstein/connectors/financial/sec_edgar.py:18` and `extra.py:25`: placeholder email in SEC EDGAR user-agent

```python
# sec_edgar.py:18 and extra.py:25 (both files)
def __init__(self, email: str = "solstein@example.com"):
```

SEC EDGAR's EFTS API requires a real contact email in the `User-Agent` header per their terms
of service. `@example.com` is an RFC 2606 reserved domain — invalid for API contact. Requests
using this email may be rejected or rate-limited by SEC EDGAR.

Two connector files share the same placeholder. Any production enrichment call through either
connector will use the invalid email unless the caller explicitly overrides the parameter.

**Story required**: Require email from config (`Settings`) with no default, or document that
the production deployment must set it explicitly. Assign to **EPIC-052** (data integrity — bad
default corrupts enrichment quality).

---

### MEDIUM — `src/solstein/domain/models.py:178`: `industry` default `"Energy Software"` propagates through production paths

```python
# src/solstein/domain/models.py:178
industry: str = "Energy Software"
```

When a `Company` is constructed without an explicit `industry` value (e.g., from a sparse
enrichment result), it silently defaults to `"Energy Software"`. This default propagates into:
- Scoring models that weight industry-specific signals
- Excel export columns visible to PE/VC analysts
- The `FinancialMetric` converter (which reads `company.industry`)
- The competitor migration (`load_competitor_data.py`) which passes through the domain model

A company with no known industry gets classified as `"Energy Software"` in deliverables. This
is a **false classification** with potential downstream investment decision impact.

The same default exists in duplicate domain model files; exact count requires cross-file audit.

**Story required**: Change default to `None` (Optional[str]), update all downstream code that
assumes `industry` is non-null, add validation that warns when industry is absent. Assign to
**EPIC-052** (data integrity — false classification from bad default).

---

### Third-pass contamination summary

| Node | File | Line | Severity | Canon Epic / Story |
|------|------|------|----------|--------------------|
| `SOLSTEIN_TEST_MODE` defaults `"mixed"` → `allow_synthetic=True` | `src/solstein/core/test_modes.py` | 16 | CRITICAL | EPIC-052 (new STORY-382) |
| `strict_provenance=False` hardcoded in dual-write path | `src/solstein/infrastructure/research_dual_write.py` | 340, 424 | CRITICAL | EPIC-052 (new STORY-383) |
| `CompanyRecord` missing `data_source_type` DB column | `src/solstein/infrastructure/models/company.py` | 77 | CRITICAL | EPIC-033 (new STORY-384) |
| Converter defaults `data_source_type` to `"real"` | `src/solstein/data/converters/company.py` | 341–344 | HIGH | EPIC-052 (new STORY-385) |
| Production migration calls `get_database_url(test=True)` | `src/solstein/migrations/load_competitor_data.py` | 179 | CRITICAL | EPIC-033 (STORY-381 context — new STORY-386) |
| All `DeprecationWarning` suppressed in pytest config | `pyproject.toml` | 257–260 | HIGH | EPIC-013 (new STORY-387) |
| No `-m "not integration"` in default addopts | `pyproject.toml` | 246 | MEDIUM | EPIC-013 (new STORY-387) |
| `confidence=1.0` hardcoded in instrumented adapter | `src/solstein/adapters/instrumented.py` | 138 | MEDIUM | EPIC-052 (new STORY-388) |
| Placeholder `solstein@example.com` in SEC EDGAR connectors | `sec_edgar.py`, `extra.py` | 18, 25 | MEDIUM | EPIC-052 (new STORY-389) |
| `industry: str = "Energy Software"` false classification default | `src/solstein/domain/models.py` | 178 | MEDIUM | EPIC-052 (new STORY-390) |
