# STORY-113: Export Status Tracking and Download Links

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Epic** | EPIC-030: Export Pipeline Modernization |
| **Created** | 2026-03-01 |
| **Dependencies** | STORY-111 |

## The Audit Verdict

> No `export_jobs` table exists. No export status API. No download link returned to callers. Exports complete silently with no user notification.

## Problem Statement

After moving exports to async (STORY-111), the caller receives a job_id and nothing else. Without a status endpoint and a download link, the export system is equivalent to submitting a print job and having no printer tray. Users need to know: is it done? where is the file? how long until the link expires? The `export_jobs` table and its associated API endpoints are the operational interface of the async export system.

## Impact

| Dimension | Impact |
|-----------|--------|
| **User Experience** | No way to retrieve an async export result |
| **Operational** | No visibility into export pipeline health |

## Affected Files

| File | Issue |
|------|-------|
| New: `src/solstein/infrastructure/database_models.py` | Needs export_jobs table |
| New: `src/solstein/api/routers/exports.py` | Needs status endpoints |

## Architectural Requirements

- `export_jobs` PostgreSQL table: id (UUID), tenant_id, user_id, company_id, format (excel/markdown/pdf/llm), status (queued/running/completed/failed/expired), progress_pct (0-100), file_url (signed Supabase URL), file_size_bytes, error_message, requested_at, completed_at, expires_at
- GET `/api/v1/exports` — list all export jobs for tenant, paginated, filterable by status/format/date
- GET `/api/v1/exports/{job_id}` — single export status with download URL when complete
- DELETE `/api/v1/exports/{job_id}` — cancel queued/running export, mark as cancelled
- Download URL included in response only when status=completed and not expired
- Expired exports (>7 days): status=expired, no download URL, re-generate option documented
- Supabase Realtime enabled on export_jobs table (consistent with EPIC-024 pattern)

## Acceptance Criteria

- [ ] GET `/api/v1/exports/{job_id}` returns signed URL when status=completed
- [ ] Expired exports return status=expired with no URL
- [ ] DELETE cancels queued exports and terminates running Celery task (revoke)
- [ ] Supabase Realtime fires on export_jobs row update

## Definition of Done

- **Tests Required**: Integration test: trigger export, poll status until completed, verify download URL accessible
- **Documentation Required**: Export API documentation
- **Code Review Gate**: Reviewer verifies expired URL logic is correct and tenant-scoped

## Notes

The operational interface for async exports.

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
