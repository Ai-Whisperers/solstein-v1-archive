# STORY-364: Implement GET /workflows/{workflow_id} — Retrieve Live Status and Results

| Field | Value |
|---|---|
| **Status** | 🔴 READY |
| **Priority** | P1 |
| **Size** | M (1-2 days) |
| **Epic** | EPIC-089 Workflow Orchestration API |
| **Created** | 2026-04-03 |
| **Updated** | 2026-04-03 (corrected after codebase audit) |
| **Risk** | Low |
| **Blocked By** | STORY-363 |

---

## Actual Codebase State (verified 2026-04-03)

- `GET /jobs/{workflow_id}` in `src/solstein/api/routers/jobs.py:18` returns HTTP 501 (Temporal integration was removed)
- `ResearchJobRecord` columns (line 281 of `models/research.py`): `status`, `progress_pct`, `current_stage`, `error_message`, `job_metadata` (JSONB), `started_at`, `completed_at`
- **No `output_dir` column exists** — `output_dir` path must be read from `job_metadata` JSONB (stored there by `run_workflow_task` from STORY-363)
- `ResearchRunRecord` does NOT have `output_dir` — do NOT read state from `ResearchRunRecord`; use `ResearchJobRecord`

---

## Problem Statement

`GET /jobs/{workflow_id}` returns HTTP 501. There is no way to check the status of a running or completed pipeline from the API. This makes the system unusable as an async API — clients submit work but have no way to retrieve results.

## Acceptance Criteria

- [ ] `GET /workflows/{workflow_id}` returns the `Workflow` model from STORY-362
- [ ] While running: `{"status": "running", "current_stage": "gather", "progress_pct": 30}`
- [ ] When completed: `{"status": "completed", "progress_pct": 100, "output_url": "/outputs/{workflow_id}/market_analysis.xlsx"}`
- [ ] When failed: `{"status": "failed", "error": "...", "current_stage": "scoring"}`
- [ ] Unknown workflow_id returns HTTP 404
- [ ] No polling or WebSocket — reads state from `ResearchJobRecord` DB table only
- [ ] Tests: running, completed, failed, and 404 cases

## Tasks

- [ ] Add `GET /workflows/{workflow_id}` route using `WorkflowRepository.get()` from STORY-362
- [ ] Map `ResearchJobRecord` fields to `Workflow` response model (`status`, `progress_pct`, `current_stage`, `error_message`)
- [ ] Add `output_url` computation: read `output_dir` path from `job_metadata` JSONB; if file exists, return download URL; otherwise `null`
- [ ] Return 404 if no `ResearchJobRecord` found for the given workflow_id
- [ ] Write tests mocking the repository for each state

## Autonomous Continuation Notes

- `output_dir` path is stored in `ResearchJobRecord.job_metadata["output_dir"]` (written there by `run_workflow_task` from STORY-363) — there is NO `output_dir` column on either `ResearchJobRecord` or `ResearchRunRecord`
- Do not re-run the pipeline in the GET handler; only read state
- If the Celery task is still running but the DB shows `queued`, return `running` (task may not have written its first stage yet)
- Use `ResearchJobRecord` only — do NOT read from `ResearchRunRecord` or `ResearchStageRecord` for this endpoint
