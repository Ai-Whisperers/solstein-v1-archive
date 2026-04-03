# STORY-364: Implement GET /workflows/{workflow_id} — Retrieve Live Status and Results

| Field | Value |
|---|---|
| **Status** | 🔴 READY |
| **Priority** | P1 |
| **Size** | M (1-2 days) |
| **Epic** | EPIC-089 Workflow Orchestration API |
| **Created** | 2026-04-03 |
| **Risk** | Low |
| **Blocked By** | STORY-363 |

---

## Problem Statement

`GET /jobs/{workflow_id}` returns HTTP 501. There is no way to check the status of a running or completed pipeline from the API. This makes the system unusable as an async API — clients submit work but have no way to retrieve results.

## Acceptance Criteria

- [ ] `GET /workflows/{workflow_id}` returns the `Workflow` model from STORY-362
- [ ] While running: `{"status": "running", "current_stage": "gather", "progress_pct": 30}`
- [ ] When completed: `{"status": "completed", "progress_pct": 100, "output_url": "/outputs/{workflow_id}/market_analysis.xlsx"}`
- [ ] When failed: `{"status": "failed", "error": "...", "current_stage": "scoring"}`
- [ ] Unknown workflow_id returns HTTP 404
- [ ] No polling or WebSocket — reads state from `ResearchRunRecord` and `ResearchStageRecord` DB tables
- [ ] Tests: running, completed, failed, and 404 cases

## Tasks

- [ ] Add `GET /workflows/{workflow_id}` route using `WorkflowRepository.get()` from STORY-362
- [ ] Map `ResearchRunRecord` state + latest `ResearchStageRecord` to `Workflow` response model
- [ ] Add `output_url` computation: file exists at `output_dir/market_analysis.xlsx` → generate download URL
- [ ] Return 404 if no `ResearchRunRecord` found for the given workflow_id
- [ ] Write tests mocking the repository for each state

## Autonomous Continuation Notes

- The `output_dir` for each run is stored in the `ResearchRunRecord` — use this to construct the output_url
- Do not re-run the pipeline in the GET handler; only read state
- If the Celery task is still running but the DB shows `queued`, return `running` (task may not have written its first stage yet)
