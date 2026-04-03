# STORY-363: Implement POST /workflows — Submit and Enqueue a Research Workflow

| Field | Value |
|---|---|
| **Status** | 🔴 READY |
| **Priority** | P1 |
| **Size** | M (2 days) |
| **Epic** | EPIC-089 Workflow Orchestration API |
| **Created** | 2026-04-03 |
| **Updated** | 2026-04-03 (corrected after codebase audit) |
| **Risk** | Medium |
| **Blocked By** | STORY-362 |

---

## Actual Codebase State (verified 2026-04-03)

- `src/solstein/worker/orchestration.py` exists but only contains `refresh_all_sources` — **no `run_workflow_task`**
- `run_market_intelligence()` is in `src/solstein/research/pipeline.py:211` — signature: `(seed_company, market, output_dir: Path, options=None)` — caller must supply `output_dir`
- `src/solstein/api/routers/async_jobs.py` handles enrichment jobs at `/async` prefix — separate from workflow submission
- `ResearchJobRecord` (preferred for Workflow API per STORY-362) columns: `status` (not `state`), `progress_pct`, `current_stage`, `error_message`, `job_metadata` (JSONB for extensible fields like `output_dir`)
- There is **no `output_dir` column** in `ResearchJobRecord` — must be stored in `job_metadata` JSON

---

## Problem Statement

There is no API endpoint to submit a research workflow. Clients cannot start a pipeline run via HTTP and receive a trackable `workflow_id`. The existing async job endpoints wrap individual tasks, not the full pipeline.

## Acceptance Criteria

- [ ] `POST /workflows` accepts `{"market": str, "seed_company": str, "options": {...}}` and returns `{"workflow_id": "...", "status": "queued"}`
- [ ] Response is returned in < 200ms (enqueue only, do not wait for pipeline)
- [ ] A Celery task `run_workflow_task` is enqueued that calls `run_market_intelligence()` with the provided arguments
- [ ] The workflow `batch_id` is the `workflow_id` returned to the client
- [ ] `ResearchJobRecord` is created with `status="queued"` before the Celery task is dispatched (NOT `ResearchRunRecord`)
- [ ] Input validation: `market` and `seed_company` are required; return HTTP 422 if missing
- [ ] Tests: valid submission returns 202 and a workflow_id; missing fields return 422

## Tasks

- [ ] Add `WorkflowSubmitRequest` Pydantic model (market, seed_company, options) — in new `src/solstein/api/routers/workflows.py`
- [ ] Add `POST /workflows` route in `src/solstein/api/routers/workflows.py` (separate from `async_jobs.py` which handles enrichment)
- [ ] Create `run_workflow_task` Celery task in `src/solstein/worker/orchestration.py` (add to existing file)
- [ ] Task body: generate `output_dir` from `workflow_id`, call `run_market_intelligence(output_dir=output_dir, ...)`, store `output_dir` path in `ResearchJobRecord.job_metadata`, update `status` on complete/fail
- [ ] Create `ResearchJobRecord` with `status="queued"` and store `output_dir` path in `job_metadata` before task dispatch
- [ ] Register `workflows.router` in `src/solstein/api/main.py` under `/workflows` prefix
- [ ] Write tests
