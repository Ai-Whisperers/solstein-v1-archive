# STORY-111: Move Exports to Async Celery Tasks

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Epic** | EPIC-030: Export Pipeline Modernization |
| **Created** | 2026-03-01 |
| **Dependencies** | EPIC-025 |

## The Audit Verdict

> `api/routers/` export endpoint — synchronous export in request thread. `celery_config.py` task_time_limit=30s. Large exports will timeout.

## Problem Statement

The export endpoint generates the file during the HTTP request. For a company with 5 years of financial data, 200 signals, and an LLM-generated narrative, this takes longer than 30 seconds. The API returns a 500 timeout, the export is lost, and the user has no recourse. Moving exports to a Celery task decouples file generation from the HTTP request — the endpoint returns a job ID immediately, the export runs in the background, and the user is notified (STORY-104) when the file is ready.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Reliability** | Synchronous exports timeout on any real dataset |
| **User Experience** | Silent failure with no retry option |
| **Scalability** | Export load blocks API worker threads |

## Affected Files

| File | Issue |
|------|-------|
| `src/solstein/exporters/excel.py` | Synchronous |
| `src/solstein/exporters/llm.py` | Synchronous |
| `src/solstein/exporters/markdown.py` | Synchronous |
| `src/solstein/worker_tasks.py` | Needs export task |

## Architectural Requirements

- Export endpoint changes: POST `/api/v1/exports` returns `{job_id, status: "queued"}` immediately
- New Celery task: `generate_export(export_job_id, company_id, format, tenant_id)` on the `export` queue
- Export job status tracked in PostgreSQL `export_jobs` table: job_id, company_id, format, status, file_url, error_message, created_at, completed_at
- GET `/api/v1/exports/{job_id}` returns current status and signed URL when complete
- LLM exporter (`llm.py`) has a separate, higher time limit (allow 120s for LLM generation)
- Failed export jobs written to DLQ (STORY-088 dependency)
- Export Celery tasks are idempotent (STORY-090 dependency): re-triggering same export_job_id does not create duplicate file

## Acceptance Criteria

- [ ] POST `/api/v1/exports` returns 202 Accepted with job_id within 1 second
- [ ] Export Celery task completes successfully for a 100-company dataset
- [ ] GET `/api/v1/exports/{job_id}` returns signed download URL when complete
- [ ] Failed export appears in DLQ (STORY-088)
- [ ] Re-triggering same export job is idempotent

## Definition of Done

- **Tests Required**: Load test: trigger 10 concurrent exports, verify all complete without timeout
- **Documentation Required**: Export API documentation
- **Code Review Gate**: Reviewer verifies no synchronous file generation remains in API request thread

## Notes

Exports must be async to handle real data volumes.

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This story currently carries a historical open or in-progress backlog badge.
- If `planning/QUEUE.md` does not currently list this story as active work, treat it as triage-required rather than immediately actionable.

### Next Agent Action

- Reconcile this story against current code reality, `planning/QUEUE.md`, and the develop autonomy audit before starting.
- Do not begin implementation from this file alone unless the queue or a fresh planning decision reactivates it.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`, `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`, and `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Preserve machine-checkable enforcement and avoid prose-only or speculative "AI slop" updates.

### Minimum Verification For Future Agents

- If this story is reactivated, update the queue or controlling planning artifact first.
- Then prove the work with the smallest relevant regression tests, gates, or generated artifacts for the touched boundary.
