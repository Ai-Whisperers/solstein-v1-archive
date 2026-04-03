# EPIC-089: Workflow Orchestration API

> **Priority**: P1 – High (async job endpoint returns 501; no multi-step orchestration)
> **Stories**: 3 (STORY-362 through STORY-364)
> **Effort**: L (5–8 days total)
> **Dependencies**: EPIC-086 (pipeline must produce correct data before wiring workflows)
> **Status**: 🔴 Not Started
> **Created**: 2026-04-03

---

## Problem

The `/jobs/{workflow_id}` endpoint returns 501 Not Implemented. The existing async job infrastructure (`/async/jobs/{job_id}`) wraps individual Celery tasks but has no concept of a **workflow** — a named, multi-step sequence of tasks with state tracking, retry logic, and a retrievable final result.

For a research run to be useful as an API-driven product:
1. A client submits a workflow (e.g. "run full market intelligence for sector X")
2. The server returns a `workflow_id`
3. The client polls `GET /workflows/{workflow_id}` to see progress across stages
4. When complete, the client retrieves the final output

Currently none of this is wired. Individual pipeline stages run as a single synchronous call; there is no way to observe or interrupt a running pipeline from outside.

---

## Stories

| Story | Title | Priority | Size |
|-------|-------|----------|------|
| STORY-362 | Define Workflow model, states, and internal storage contract | P1 | M |
| STORY-363 | Implement `POST /workflows` — submit and enqueue a research workflow | P1 | M |
| STORY-364 | Implement `GET /workflows/{workflow_id}` — retrieve live status and results | P1 | M |

**Execution order**: 362 → 363 → 364 (strictly sequential)

---

## Definition of Done

- [ ] `Workflow` domain model with states: `queued → running → completed | failed | cancelled`
- [ ] `POST /workflows` accepts market + seed_company + options, enqueues pipeline, returns `workflow_id`
- [ ] `GET /workflows/{workflow_id}` returns current stage, per-stage status, and final output when done
- [ ] Existing pipeline `run_market_intelligence()` is invoked by the Celery worker backing the workflow
- [ ] No polling loop in the endpoint — state is read from DB/cache set by the worker
- [ ] Integration test: submit workflow, poll until complete, assert output present
- [ ] `pytest` passes at 0 failures, `ruff check` at 0 errors

---

## Acceptance Criteria

**AC-1**: `POST /workflows` returns `{"workflow_id": "...", "status": "queued"}` within 200ms.

**AC-2**: `GET /workflows/{id}` returns `{"status": "running", "current_stage": "gather", "progress": 0.4}` while pipeline is executing.

**AC-3**: `GET /workflows/{id}` returns `{"status": "completed", "output_url": "..."}` after pipeline finishes.

**AC-4**: `GET /workflows/{id}` for an unknown ID returns HTTP 404.

---

## Design Notes

- Use the existing `ResearchRunRecord` + `ResearchStageRecord` DB tables as the state backend — they are already written by `persist_research_run()`
- The Celery task wraps `run_market_intelligence()` and updates stage records in real time
- The GET endpoint reads from DB — no long-polling or WebSocket needed for MVP
- `workflow_id` = the existing `batch_id` from `run_market_intelligence()`

---

## Key Files

| File | Role |
|------|------|
| `src/solstein/research/pipeline.py` | `run_market_intelligence()` — the workflow body |
| `src/solstein/infrastructure/research_dual_write.py` | `persist_research_run()` — writes workflow state |
| `src/solstein/infrastructure/database_models.py` | `ResearchRunRecord`, `ResearchStageRecord` |
| `src/solstein/api/routers/async_jobs.py` | Existing async job endpoints — extend here |
| `src/solstein/worker/orchestration.py` | Worker task definitions — add workflow task here |
