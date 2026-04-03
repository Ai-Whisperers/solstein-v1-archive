# STORY-363: Implement POST /workflows — Submit and Enqueue a Research Workflow

| Field | Value |
|---|---|
| **Status** | 🔴 READY |
| **Priority** | P1 |
| **Size** | M (2 days) |
| **Epic** | EPIC-089 Workflow Orchestration API |
| **Created** | 2026-04-03 |
| **Updated** | 2026-04-03 (deep wiring audit) |
| **Risk** | Medium |
| **Blocked By** | STORY-362 |

---

## Exact Codebase Wiring (deep audit 2026-04-03)

### What exists

**`src/solstein/research/pipeline.py:211`** — `run_market_intelligence()`:
```python
def run_market_intelligence(
    seed_company: str,
    market: str,
    output_dir: Path,          # ← caller MUST supply; no default
    options: dict[str, object] | None = None,
    **legacy_kwargs: object,
) -> dict[str, object]:
    # batch_id = uuid.uuid4().hex[:12]   ← generated at line 228
    # output_dir.mkdir(parents=True, exist_ok=True)
    # returns {"market": str, "seed_company": str, "discovered": int,
    #          "scored": int, "output_dir": str, ...}
```

**`src/solstein/worker/orchestration.py`** — only has `refresh_all_sources` (line 29). No `run_workflow_task` exists.

**`src/solstein/api/routers/async_jobs.py`** — enrichment-only router, prefix `/async`. Do NOT add workflow routes here.

**`src/solstein/infrastructure/research_job_repository.py`** — `ResearchJobRepository`:

| Method | Signature | Line |
|--------|-----------|------|
| `create_job` | `(tenant_id, company_id, company_name=None) → ResearchJobRecord` | 52–83 |
| `update_status` | `(job_id, new_status, progress_pct=None, current_stage=None, error_message=None) → ResearchJobRecord \| None` | 85–152 |
| `get_job` | `(job_id: uuid.UUID) → ResearchJobRecord \| None` | 154–166 |

`create_job()` creates `status="queued"` row. Valid transitions: `queued→running→completed|failed|cancelled`.

**`src/solstein/api/main.py`** router registrations:
```
Line 218: app.include_router(jobs.router, prefix="/jobs")
Line 221: app.include_router(async_jobs.router)            # prefix="/async"
Line 222: app.include_router(research_jobs.router, prefix="/jobs")
# New: app.include_router(workflows.router, prefix="/workflows")
```

**Tenant extraction pattern** (from `research_jobs.py:97`):
```python
tenant_id = tenant.get("tenant_id", "")  # from Depends(get_current_tenant)
```

### What does NOT exist (must create)

- `src/solstein/api/routers/workflows.py` — does not exist
- `run_workflow_task` in `worker/orchestration.py` — does not exist
- `WorkflowSubmitRequest` Pydantic model — does not exist
- `output_dir` column in `ResearchJobRecord` — does not exist; store path in `job_metadata` JSON

### `ResearchJobRecord.job_metadata` — the output_dir store

`job_metadata: JSON` (nullable) at `models/research.py:330`. Store `output_dir` as:
```python
record.job_metadata = {"output_dir": str(output_dir)}
```
STORY-364's `GET /workflows/{id}` reads from `job.job_metadata.get("output_dir")`.

---

## Problem Statement

There is no API endpoint to submit a research workflow. Clients cannot start a pipeline run via HTTP and receive a trackable `workflow_id`. The existing async job endpoints wrap individual enrichment tasks, not the full market intelligence pipeline.

---

## Acceptance Criteria

- [ ] `POST /workflows` accepts `{"market": str, "seed_company": str, "options": {...}}` and returns `{"workflow_id": "...", "status": "queued"}` in < 200ms
- [ ] `run_workflow_task` Celery task enqueued (not executed inline)
- [ ] `ResearchJobRecord` created with `status="queued"` BEFORE task dispatch; `workflow_id` = `str(record.id)`
- [ ] Task body: generate `output_dir` from `workflow_id`, call `run_market_intelligence(seed_company, market, output_dir, options)`, store `output_dir` in `job_metadata`, call `update_status("completed")` on success or `update_status("failed", error_message=...)` on failure
- [ ] Input validation: `market` and `seed_company` required; missing → HTTP 422
- [ ] Tenant-scoped: tenant_id from `Depends(get_current_tenant)` passed to `create_job()`
- [ ] Response is HTTP 202 Accepted
- [ ] Test: valid submission → 202 + workflow_id; missing fields → 422
- [ ] `ruff check` 0 errors

---

## Tasks

- [ ] Add `run_workflow_task` to `src/solstein/worker/orchestration.py`:
  ```python
  @shared_task(name="solstein.worker_tasks.run_workflow", bind=True, max_retries=0)
  def run_workflow_task(self, workflow_id: str, tenant_id: str,
                        seed_company: str, market: str, options: dict | None = None):
      from pathlib import Path
      from solstein.research.pipeline import run_market_intelligence
      from solstein.infrastructure.research_job_repository import ResearchJobRepository
      from solstein.infrastructure.database import get_sync_session

      output_dir = Path(f"/tmp/workflows/{workflow_id}")
      with get_sync_session() as session:
          repo = ResearchJobRepository(session)
          import uuid
          job_id = uuid.UUID(workflow_id)
          repo.update_status(job_id, "running", current_stage="starting")
          try:
              run_market_intelligence(seed_company, market, output_dir, options)
              job = repo.get_job(job_id)
              job.job_metadata = {"output_dir": str(output_dir)}
              repo.update_status(job_id, "completed", progress_pct=100)
          except Exception as exc:
              repo.update_status(job_id, "failed", error_message=str(exc))
              raise
  ```
- [ ] Create `src/solstein/api/routers/workflows.py` with `POST /` endpoint:
  - `WorkflowSubmitRequest(BaseModel)`: `market: str`, `seed_company: str`, `options: dict = {}`
  - Create `ResearchJobRecord` via `ResearchJobRepository.create_job(tenant_id, company_id=seed_company)`
  - Dispatch `run_workflow_task.apply_async(args=[str(record.id), tenant_id, seed_company, market, options])`
  - Return `{"workflow_id": str(record.id), "status": "queued"}` with HTTP 202
- [ ] Register in `main.py`: `app.include_router(workflows.router, prefix="/workflows")`
- [ ] Import `workflows` in `main.py` import block (lines 44–59)
- [ ] Write tests

## Key Files

| File | Line | Note |
|------|------|------|
| `src/solstein/worker/orchestration.py` | 29 | Add `run_workflow_task` after `refresh_all_sources` |
| `src/solstein/research/pipeline.py` | 211–217 | `run_market_intelligence` signature |
| `src/solstein/infrastructure/research_job_repository.py` | 52–83 | `create_job()` |
| `src/solstein/infrastructure/research_job_repository.py` | 85–152 | `update_status()` |
| `src/solstein/infrastructure/models/research.py` | 330 | `job_metadata` JSON column |
| `src/solstein/api/main.py` | 44–59, 224 | Add import + registration |
| `src/solstein/api/routers/workflows.py` | — | CREATE (does not exist) |
