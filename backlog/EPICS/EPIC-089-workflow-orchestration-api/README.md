# EPIC-089: Workflow Orchestration API

> **Priority**: P1 – High (async job endpoint returns 501; no multi-step orchestration)
> **Stories**: 3 ([STORY-362](STORIES/STORY-362.md) through [STORY-364](STORIES/STORY-364.md))
> **Effort**: M (3–5 days total)
> **Dependencies**: EPIC-086 DONE (pipeline must produce correct data before wiring workflows)
> **Status**: 🔴 Not Started
> **Created**: 2026-04-03
> **Updated**: 2026-04-03 (codebase audit corrected all file/table/abstraction references)

---

## Problem

The `/jobs/{workflow_id}` endpoint (`src/solstein/api/routers/jobs.py:18`) returns 501 Not Implemented. There is no workflow state model, no submit endpoint, and no status endpoint. Clients cannot submit a research run via API or observe its progress.

For a research run to be useful as an API-driven product:
1. A client submits a workflow (e.g. "run full market intelligence for sector X")
2. The server returns a `workflow_id`
3. The client polls `GET /workflows/{workflow_id}` to see progress across stages
4. When complete, the client retrieves the final output URL

---

## Stories

| Story | Title | Priority | Size | Status |
|-------|-------|----------|------|--------|
| [STORY-362](STORIES/STORY-362.md) | Define `Workflow` response model + `WorkflowStatus` enum; remove 501 stub | P1 | XS | 🔴 READY |
| [STORY-363](STORIES/STORY-363.md) | Implement `POST /workflows` — new `workflows.py` router + `run_workflow_task` in `orchestration.py` | P1 | M | ⏳ BLOCKED by [STORY-362](STORIES/STORY-362.md) |
| [STORY-364](STORIES/STORY-364.md) | Implement `GET /workflows/{workflow_id}` — read `ResearchJobRecord`; `output_dir` from `job_metadata` JSON | P1 | M | ⏳ BLOCKED by [STORY-363](STORIES/STORY-363.md) |

**Execution order**: 362 → 363 → 364 (strictly sequential).

---

## Definition of Done

- [ ] `src/solstein/domain/workflow.py` created with `WorkflowStatus` StrEnum and `Workflow` Pydantic model
- [ ] `POST /workflows` accepts market + seed_company + options, creates `ResearchJobRecord`, enqueues `run_workflow_task`, returns `workflow_id`
- [ ] `GET /workflows/{workflow_id}` reads `ResearchJobRecord`, validates tenant, returns `Workflow` response
- [ ] 501 stub removed from `src/solstein/api/routers/jobs.py`
- [ ] No new repository abstraction class — `ResearchJobRepository` used directly with inline tenant validation
- [ ] `pytest` passes at 0 failures, `ruff check` at 0 errors

---

## Acceptance Criteria

**AC-1**: `POST /workflows` returns `{"workflow_id": "...", "status": "queued"}` within 200ms.

**AC-2**: `GET /workflows/{id}` returns `{"status": "running", "current_stage": "gather", "progress_pct": 40}` while pipeline is executing.

**AC-3**: `GET /workflows/{id}` returns `{"status": "completed", "output_url": "/outputs/{id}/market_analysis.xlsx"}` after pipeline finishes (or `output_url: null` if file missing).

**AC-4**: `GET /workflows/{id}` for unknown ID or other-tenant ID returns HTTP 404 (not 403 — do not reveal existence).

---

## Architecture Decisions (Codebase-Verified 2026-04-03)

- **State backend**: `ResearchJobRecord` at `src/solstein/infrastructure/models/research.py:281` (table `research_jobs`) — **not** `ResearchRunRecord`/`ResearchStageRecord`. `ResearchJobRecord` has the `status`, `progress_pct`, `current_stage`, `error_message`, `job_metadata`, `started_at`, `completed_at` columns needed.
- **No WorkflowRepository class**: `ResearchJobRepository.get_job()` at `research_job_repository.py:154` is used directly. Inline tenant validation pattern from `research_jobs.py:156` applies.
- **`output_dir` storage**: NOT a column — stored as `job_metadata["output_dir"]` (JSON key). `run_workflow_task` sets it after `run_market_intelligence()` returns.
- **`workflow_id`**: `str(ResearchJobRecord.id)` (UUID) — not the `batch_id` from `run_market_intelligence()`.
- **Router location**: `src/solstein/api/routers/workflows.py` (new file) — not `async_jobs.py` (that's for enrichment).
- **Task location**: `run_workflow_task` added to `src/solstein/worker/orchestration.py` (existing module).

---

## Key Files (Codebase-Verified 2026-04-03)

| File | Line | Role |
|------|------|------|
| `src/solstein/domain/workflow.py` | — | CREATE: `Workflow` + `WorkflowStatus` ([STORY-362](STORIES/STORY-362.md)) |
| `src/solstein/api/routers/jobs.py` | 18–36 | 501 stub — DELETE in [STORY-362](STORIES/STORY-362.md) |
| `src/solstein/api/routers/workflows.py` | — | CREATE: `POST /workflows` + `GET /workflows/{id}` |
| `src/solstein/worker/orchestration.py` | — | Add `run_workflow_task` here |
| `src/solstein/research/pipeline.py` | 211 | `run_market_intelligence()` — the workflow body |
| `src/solstein/infrastructure/research_job_repository.py` | 52–198 | `ResearchJobRepository` — reuse directly |
| `src/solstein/infrastructure/models/research.py` | 281 | `ResearchJobRecord` — state backend |
| `src/solstein/api/routers/research_jobs.py` | 134–160 | Tenant validation pattern to replicate |
