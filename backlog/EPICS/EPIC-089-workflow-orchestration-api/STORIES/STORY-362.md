# STORY-362: Define Workflow Response Model and WorkflowStatus Enum

| Field | Value |
|---|---|
| **Status** | 🔴 READY |
| **Priority** | P1 |
| **Size** | XS (2 hours) |
| **Epic** | EPIC-089 Workflow Orchestration API |
| **Created** | 2026-04-03 |
| **Updated** | 2026-04-03 (scope cut: no WorkflowRepository class) |
| **Risk** | Low |
| **Blocked By** | EPIC-086 (DONE) |

---

## Why No WorkflowRepository

The original design had a `WorkflowRepository` wrapping `ResearchJobRepository` — a thin class that adds no logic, only delegation. `ResearchJobRepository.get_job()` already exists at `research_job_repository.py:154`. The inline tenant validation pattern (`if job is None or job.tenant_id != tenant_id: raise 404`) is already established in `research_jobs.py:156`. Adding a `WorkflowRepository` class would create a second abstraction layer over an existing abstraction for no gain, and would need to be maintained in sync with `ResearchJobRepository` as it evolves.

**Pattern for STORY-363 and STORY-364**: import `ResearchJobRepository` directly, call `get_job()`, validate tenant inline. Same as `research_jobs.py`.

---

## Exact Codebase Wiring

### What to reuse (do NOT reimplment)

**`ResearchJobRepository`** (`src/solstein/infrastructure/research_job_repository.py`):

| Method | Use in STORY | Line |
|--------|-------------|------|
| `create_job(tenant_id, company_id, company_name=None)` | STORY-363 POST | 52–83 |
| `update_status(job_id, new_status, ...)` | STORY-363 task | 85–152 |
| `get_job(job_id: uuid.UUID) → ResearchJobRecord \| None` | STORY-364 GET | 154–166 |
| `get_jobs_for_tenant(tenant_id, ...)` | Future list endpoint | 168–198 |

**Tenant validation pattern** from `research_jobs.py:134–160`:
```python
tenant_id = tenant.get("tenant_id", "")     # from Depends(get_current_tenant)
repo = ResearchJobRepository(session)
job = await repo.get_job(parsed_uuid)
if job is None or job.tenant_id != tenant_id:
    raise APIError(code="NOT_FOUND", status_code=404)
```

**`ResearchJobRecord`** columns used by workflow endpoints (`models/research.py:281`):
`status`, `progress_pct`, `current_stage`, `error_message`, `job_metadata` (JSON — `output_dir` stored here by STORY-363 task), `started_at`, `completed_at`

### What does NOT exist (create in this story)

**`src/solstein/domain/workflow.py`** — does not exist. Create:

```python
from enum import StrEnum
from datetime import datetime
from pydantic import BaseModel

class WorkflowStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Workflow(BaseModel):
    """API response model for workflow status."""
    workflow_id: str
    status: WorkflowStatus
    current_stage: str | None = None
    progress_pct: int = 0
    started_at: datetime | None = None
    completed_at: datetime | None = None
    output_url: str | None = None
    error: str | None = None
```

Note: `tenant_id` excluded from response — never expose internal IDs to the client.

### 501 stub to remove

`src/solstein/api/routers/jobs.py:18` — `GET /{workflow_id}` returns 501. Remove this route in this story (or in STORY-364 at latest) to avoid confusing coexistence with `GET /workflows/{id}`.

---

## Acceptance Criteria

- [ ] `src/solstein/domain/workflow.py` created with `WorkflowStatus` StrEnum and `Workflow` Pydantic model
- [ ] `WorkflowStatus` values exactly match `ResearchJobRecord.status` string values: `queued`, `running`, `completed`, `failed`, `cancelled`
- [ ] `Workflow` model has no `tenant_id` field (internal)
- [ ] The 501 route in `src/solstein/api/routers/jobs.py` is removed
- [ ] Unit test: `Workflow.model_validate({"workflow_id": "x", "status": "running", "progress_pct": 30})` passes
- [ ] `ruff check` 0 errors

---

## Tasks

- [ ] Create `src/solstein/domain/workflow.py` (see model above)
- [ ] Delete the 501 stub route from `src/solstein/api/routers/jobs.py:18–36` (or delete the whole file if nothing else uses it — verify with `grep -rn "jobs.router" src/`)
- [ ] Write one-line smoke test

## Key Files

| File | Line | Note |
|------|------|------|
| `src/solstein/domain/workflow.py` | — | CREATE — `Workflow` model + `WorkflowStatus` enum |
| `src/solstein/api/routers/jobs.py` | 18–36 | DELETE 501 stub |
| `src/solstein/infrastructure/research_job_repository.py` | 52–198 | REUSE — no new repo class needed |
| `src/solstein/infrastructure/models/research.py` | 281 | `ResearchJobRecord` — backing table |
