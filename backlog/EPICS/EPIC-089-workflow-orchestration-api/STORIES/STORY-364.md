# STORY-364: Implement GET /workflows/{workflow_id} — Retrieve Live Status and Results

| Field | Value |
|---|---|
| **Status** | 🔴 READY |
| **Priority** | P1 |
| **Size** | M (1-2 days) |
| **Epic** | EPIC-089 Workflow Orchestration API |
| **Created** | 2026-04-03 |
| **Updated** | 2026-04-03 (deep wiring audit) |
| **Risk** | Low |
| **Blocked By** | STORY-363 |

---

## Exact Codebase Wiring (deep audit 2026-04-03)

### Current 501 stub (`src/solstein/api/routers/jobs.py:18`)

```python
@router.get("/{workflow_id}")
async def get_job_status(workflow_id: str) -> dict[str, Any]:
    raise APIError(
        code="NOT_IMPLEMENTED",
        message="Job status endpoint disabled - Temporal integration removed",
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
    )
```

Registered at `main.py:218`: `app.include_router(jobs.router, prefix="/jobs")` → `GET /jobs/{workflow_id}`.

This stub MUST be removed (or the `jobs.py` route deleted) before STORY-364 ships, otherwise `GET /jobs/{id}` would shadow `GET /workflows/{id}` for route-aware clients.

### `ResearchJobRecord` Columns Used by This Endpoint

From `src/solstein/infrastructure/models/research.py:281`:

| Column | Type | Line | Used for |
|--------|------|------|----------|
| `id` | `Uuid(as_uuid=True)` | 306–308 | Lookup key |
| `tenant_id` | `String(255)` | 309–311 | Tenant validation |
| `status` | `String(50)` | 318–320 | `Workflow.status` |
| `progress_pct` | `Integer` | 321–323 | `Workflow.progress_pct` |
| `current_stage` | `String(100)` | 324–326 | `Workflow.current_stage` |
| `error_message` | `Text` | 327–329 | `Workflow.error` |
| `job_metadata` | `JSON` | 330–332 | `job_metadata["output_dir"]` → `Workflow.output_url` |
| `started_at` | `DateTime` | 336–338 | `Workflow.started_at` |
| `completed_at` | `DateTime` | 339–341 | `Workflow.completed_at` |

**NO `output_dir` column** — it lives in `job_metadata["output_dir"]` (set by `run_workflow_task` from STORY-363).

### `ResearchJobRepository.get_job()` (`research_job_repository.py:154–166`)

```python
result = await self.session.execute(
    select(ResearchJobRecord).where(ResearchJobRecord.id == job_id)
)
return result.scalar_one_or_none()
```

**No built-in tenant filter** — caller MUST validate: `if job is None or job.tenant_id != tenant_id: raise 404`.

Pattern from `research_jobs.py:156`:
```python
if job is None or job.tenant_id != tenant_id:
    raise APIError(code="NOT_FOUND", ..., status_code=404)
```

### Tenant Extraction Pattern

From `research_jobs.py:134`:
```python
async def get_research_job(
    job_id: str,
    tenant: dict[str, Any] = Depends(get_current_tenant),
    session: Any = Depends(get_db_session),
) -> ResearchJobResponse:
    tenant_id = tenant.get("tenant_id", "")
    repo = ResearchJobRepository(session)
    ...
```

### `Workflow` Model (from STORY-362)

STORY-362 creates `src/solstein/domain/workflow.py`:
```python
class Workflow(BaseModel):
    workflow_id: str
    tenant_id: str
    status: WorkflowStatus   # "queued"|"running"|"completed"|"failed"|"cancelled"
    current_stage: str | None = None
    progress_pct: int = 0
    started_at: datetime | None = None
    completed_at: datetime | None = None
    output_url: str | None = None    # derived from job_metadata["output_dir"]
    error: str | None = None
```

### `output_url` Computation

```python
output_dir_str = (job.job_metadata or {}).get("output_dir")
if output_dir_str and Path(output_dir_str).exists():
    output_url = f"/outputs/{workflow_id}/market_analysis.xlsx"
else:
    output_url = None
```

Do NOT check filesystem at request time if it would block the event loop — use `asyncio.to_thread(Path.exists, ...)`.

### Router Registration

`POST /workflows` and `GET /workflows/{workflow_id}` both live in `workflows.py` registered at `main.py` under `/workflows` prefix (added by STORY-363).

---

## Problem Statement

`GET /jobs/{workflow_id}` returns HTTP 501. Clients can submit workflows (STORY-363) but have no way to check status or retrieve results. The system is unusable as an async API without this endpoint.

---

## Acceptance Criteria

- [ ] `GET /workflows/{workflow_id}` returns the `Workflow` model from STORY-362
- [ ] While running: `{"status": "running", "current_stage": "gather", "progress_pct": 30}`
- [ ] When completed: `{"status": "completed", "progress_pct": 100, "output_url": "/outputs/{id}/market_analysis.xlsx"}` (or `null` if file not found)
- [ ] When failed: `{"status": "failed", "error": "...", "current_stage": "scoring"}`
- [ ] Unknown or other-tenant `workflow_id` → HTTP 404 (not 403 — do not reveal existence)
- [ ] 501 stub in `jobs.py` removed
- [ ] Tests: running, completed, failed, and 404 cases — all mock the repository

---

## Tasks

- [ ] Add `GET /{workflow_id}` route to `src/solstein/api/routers/workflows.py` (created by STORY-363)
- [ ] Use `WorkflowRepository.get()` from STORY-362 — or call `ResearchJobRepository.get_job()` directly and map to `Workflow`
- [ ] Tenant validation: `if job is None or job.tenant_id != tenant_id: raise 404`
- [ ] `output_url` computation: read `job.job_metadata.get("output_dir")`, check file existence, derive URL or return `None`
- [ ] **Remove** the 501 route from `src/solstein/api/routers/jobs.py` (or delete the file if nothing else uses it)
- [ ] Write tests using mock repository for each of 4 status cases + 404

## Key Files

| File | Line | Note |
|------|------|------|
| `src/solstein/api/routers/jobs.py` | 18–36 | 501 stub — REMOVE |
| `src/solstein/api/routers/workflows.py` | — | Add `GET /{workflow_id}` here (created by STORY-363) |
| `src/solstein/infrastructure/research_job_repository.py` | 154–166 | `get_job()` — no tenant filter; caller validates |
| `src/solstein/infrastructure/models/research.py` | 330 | `job_metadata` JSON — `output_dir` key |
| `src/solstein/api/routers/research_jobs.py` | 134–160 | Tenant validation pattern to replicate |
| `src/solstein/domain/workflow.py` | — | `Workflow` model (created by STORY-362) |
