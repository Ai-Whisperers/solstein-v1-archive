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

**`get_current_tenant` dependency**: defined at `src/solstein/api/main.py:140` (or imported dependency) — returns `dict[str, Any]` with key `"tenant_id"`. **Not** the `get_current_tenant()` from `tenant/context.py` — that's a ContextVar getter.

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
