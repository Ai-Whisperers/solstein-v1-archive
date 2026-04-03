# STORY-362: Define Workflow API Model and WorkflowRepository Over Existing DB Tables

| Field | Value |
|---|---|
| **Status** | 🔴 READY |
| **Priority** | P1 |
| **Size** | M (1-2 days) |
| **Epic** | EPIC-089 Workflow Orchestration API |
| **Created** | 2026-04-03 |
| **Updated** | 2026-04-03 (deep wiring audit completed) |
| **Risk** | Low — only adding new code over existing tables |
| **Blocked By** | EPIC-086 (DONE) |

---

## Actual Codebase State (deep audit 2026-04-03)

### What exists

**`ResearchJobRecord`** (`src/solstein/infrastructure/models/research.py:281`):
- Table: `research_jobs`
- Columns: `id` (UUID PK), `tenant_id` (String 255, NOT NULL, indexed), `company_id` (String 255, indexed), `company_name` (String 500, nullable), `status` (String 50, default `"queued"`, indexed), `progress_pct` (Integer, default 0), `current_stage` (String 100, nullable), `error_message` (Text, nullable), `job_metadata` (JSON, nullable), `created_at` (DateTime UTC), `started_at` (DateTime, nullable), `completed_at` (DateTime, nullable)
- Composite indexes (lines 343–349): `(tenant_id)`, `(company_id)`, `(status)`, `(tenant_id, status)`, `(created_at)`
- State machine built in: `VALID_TRANSITIONS` dict + `can_transition_to()` method (lines 351–370)
- Valid transitions: `queued→{running,cancelled}`, `running→{completed,failed,cancelled}`; terminal states have no exits

**`ResearchJobRepository`** (`src/solstein/infrastructure/research_job_repository.py:37`):

| Method | Signature | Lines |
|--------|-----------|-------|
| `create_job` | `(tenant_id, company_id, company_name=None) → ResearchJobRecord` | 52–83 |
| `update_status` | `(job_id, new_status, progress_pct=None, current_stage=None, error_message=None) → ResearchJobRecord \| None` | 85–152 |
| `get_job` | `(job_id: uuid.UUID) → ResearchJobRecord \| None` | 154–166 |
| `get_jobs_for_tenant` | `(tenant_id, status_filter=None, limit=50, offset=0) → list[ResearchJobRecord]` | 168–198 |
| `get_active_jobs_for_company` | `(company_id, tenant_id) → list[ResearchJobRecord]` | 200–223 |

Key query patterns:
- `get_job()` has **no built-in tenant filter** — caller must validate (`research_jobs.py:156`)
- `get_jobs_for_tenant()` always includes `.where(ResearchJobRecord.tenant_id == tenant_id)` (line 188)

**Existing job API** (`src/solstein/api/routers/research_jobs.py`):
- `ResearchJobResponse` model (lines 27–42): `id`, `tenant_id`, `company_id`, `company_name`, `status`, `progress_pct`, `current_stage`, `error_message`, `created_at`, `started_at`, `completed_at`; `model_config = {"from_attributes": True}` (line 42)
- Routes (under `/jobs` prefix, registered at `main.py:222`):
  - `GET /jobs/research-jobs` — list with `status_filter`, `limit`, `offset`
  - `GET /jobs/research-jobs/{job_id}` — single job with in-memory tenant validation

**`GET /jobs/{workflow_id}`** (`src/solstein/api/routers/jobs.py:18`):
- Returns HTTP 501: `APIError(code="NOT_IMPLEMENTED", message="Job status endpoint disabled - Temporal integration removed", status_code=501)`
- Registered at `main.py:218` under `/jobs` prefix

### What does NOT exist

- `src/solstein/domain/workflow.py` — **does not exist** (must create)
- `src/solstein/infrastructure/workflow_repository.py` — **does not exist** (must create)
- `src/solstein/api/routers/workflows.py` — **does not exist** (must create in STORY-363)

### Router registration pattern (main.py)

```python
# main.py lines 218, 222
app.include_router(jobs.router, prefix="/jobs")           # line 218 — 501 stub
app.include_router(research_jobs.router, prefix="/jobs")  # line 222 — read-only
# ADD (STORY-363/364):
app.include_router(workflows.router, prefix="/workflows") # new
```

No route conflict: `research_jobs` routes at `/jobs/research-jobs/*` do not collide with `jobs` catch-all `GET /jobs/{workflow_id}`.

---

## Problem Statement

The `GET /jobs/{workflow_id}` route returns HTTP 501. A read-capable `ResearchJobRepository` exists but there is no `Workflow` domain model, no `WorkflowRepository` abstraction, and no unified API response type. STORY-363 and STORY-364 depend on this story's domain contract.

---

## Acceptance Criteria

- [ ] `WorkflowStatus` StrEnum defined: `queued | running | completed | failed | cancelled` (matches `ResearchJobRecord.status` values exactly)
- [ ] `Workflow` Pydantic response model: `workflow_id` (str), `tenant_id` (str), `status` (WorkflowStatus), `current_stage` (str | None), `progress_pct` (int), `started_at` (datetime | None), `completed_at` (datetime | None), `output_url` (str | None), `error` (str | None)
- [ ] `WorkflowRepository.get(workflow_id: str, tenant_id: str) -> Workflow | None` — queries `ResearchJobRecord` by `id` (parse to UUID first), validates `tenant_id` in-memory (following `research_jobs.py:156` pattern), maps to `Workflow`
- [ ] `output_url` derived from `job_metadata["output_dir"]` if present (no column; stored as JSON key by STORY-363's Celery task)
- [ ] The 501 route in `src/solstein/api/routers/jobs.py` is **removed** — `GET /jobs/{workflow_id}` must not coexist once `/workflows/{id}` works (avoids confusion)
- [ ] Unit test: given a mock `ResearchJobRecord` at each of 5 statuses, `WorkflowRepository.get()` returns correct `WorkflowStatus`
- [ ] Unit test: `workflow_id` belonging to different tenant returns `None` (not 403 — 404 behavior)
- [ ] `ruff check` at 0 errors

---

## Tasks

- [ ] Create `src/solstein/domain/workflow.py`:
  ```python
  from enum import StrEnum
  class WorkflowStatus(StrEnum):
      QUEUED = "queued"
      RUNNING = "running"
      COMPLETED = "completed"
      FAILED = "failed"
      CANCELLED = "cancelled"

  class Workflow(BaseModel):
      workflow_id: str
      tenant_id: str
      status: WorkflowStatus
      current_stage: str | None = None
      progress_pct: int = 0
      started_at: datetime | None = None
      completed_at: datetime | None = None
      output_url: str | None = None
      error: str | None = None
  ```
- [ ] Create `src/solstein/infrastructure/workflow_repository.py`:
  - Import `ResearchJobRecord` from `models/research.py:281`
  - Import `ResearchJobRepository` from `research_job_repository.py:37`
  - `WorkflowRepository.get(workflow_id: str, tenant_id: str, session: AsyncSession) -> Workflow | None`
  - Parse `workflow_id` → `uuid.UUID`; call `ResearchJobRepository(session).get_job(uuid_val)`; check `job.tenant_id == tenant_id`; map to `Workflow`
  - `output_url`: `job.job_metadata.get("output_dir")` if `job.job_metadata` else `None`
- [ ] Remove or replace the 501 route in `src/solstein/api/routers/jobs.py` — it must be gone before STORY-364 ships
- [ ] Write unit tests in `tests/unit/test_workflow_repository.py`

## Key Files

| File | Line | Note |
|------|------|------|
| `src/solstein/infrastructure/models/research.py` | 281 | `ResearchJobRecord` — columns, indexes, state machine |
| `src/solstein/infrastructure/research_job_repository.py` | 37 | `ResearchJobRepository` — reuse `get_job()` at line 154 |
| `src/solstein/api/routers/research_jobs.py` | 27 | `ResearchJobResponse` — reference for field naming |
| `src/solstein/api/routers/jobs.py` | 18 | 501 stub — remove this |
| `src/solstein/api/main.py` | 218, 222 | Router registrations under `/jobs` |
| `src/solstein/domain/workflow.py` | — | CREATE (does not exist) |
| `src/solstein/infrastructure/workflow_repository.py` | — | CREATE (does not exist) |
