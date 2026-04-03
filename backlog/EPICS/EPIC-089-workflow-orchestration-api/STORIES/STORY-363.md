# STORY-363: Implement POST /workflows — Submit and Enqueue a Research Workflow

| Field | Value |
|---|---|
| **Status** | 🔴 READY |
| **Priority** | P1 |
| **Size** | M (2 days) |
| **Epic** | EPIC-089 Workflow Orchestration API |
| **Created** | 2026-04-03 |
| **Risk** | Medium |
| **Blocked By** | STORY-362 |

---

## Problem Statement

There is no API endpoint to submit a research workflow. Clients cannot start a pipeline run via HTTP and receive a trackable `workflow_id`. The existing async job endpoints wrap individual tasks, not the full pipeline.

## Acceptance Criteria

- [ ] `POST /workflows` accepts `{"market": str, "seed_company": str, "options": {...}}` and returns `{"workflow_id": "...", "status": "queued"}`
- [ ] Response is returned in < 200ms (enqueue only, do not wait for pipeline)
- [ ] A Celery task `run_workflow_task` is enqueued that calls `run_market_intelligence()` with the provided arguments
- [ ] The workflow `batch_id` is the `workflow_id` returned to the client
- [ ] `ResearchRunRecord` is created with `state=queued` before the Celery task is dispatched
- [ ] Input validation: `market` and `seed_company` are required; return HTTP 422 if missing
- [ ] Tests: valid submission returns 202 and a workflow_id; missing fields return 422

## Tasks

- [ ] Add `WorkflowSubmitRequest` Pydantic model (market, seed_company, options)
- [ ] Add `POST /workflows` route in `src/solstein/api/routers/async_jobs.py` (or new `workflows.py`)
- [ ] Create `run_workflow_task` Celery task in `src/solstein/worker/orchestration.py`
- [ ] Task body: create output_dir, call `run_market_intelligence()`, update `ResearchRunRecord` on complete/fail
- [ ] Create `ResearchRunRecord` with `state=queued` in the POST handler before task dispatch
- [ ] Register router in `src/solstein/api/main.py`
- [ ] Write tests
