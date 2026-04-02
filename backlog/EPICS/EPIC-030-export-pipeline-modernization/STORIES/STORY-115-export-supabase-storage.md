# STORY-115: Store Exports in Supabase Storage

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Epic** | EPIC-030: Export Pipeline Modernization |
| **Created** | 2026-03-01 |
| **Dependencies** | STORY-111, EPIC-028/STORY-105 |

## The Audit Verdict

> All exporters write to local filesystem. In a containerized environment, files are lost on restart. In a horizontally scaled environment, files written by one replica are inaccessible from another.

## Problem Statement

Every export file lives and dies with the container that generated it. When a Celery worker container restarts — a normal operational event — every in-progress or recently completed export on that worker is lost. When two workers run in parallel — a normal scaling event — download URLs tied to filesystem paths become routing puzzles. The solution is object storage with signed URLs. Supabase Storage is already in the stack (EPIC-020). This story wires the export pipeline to it.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Reliability** | Exports lost on container restart |
| **Scalability** | Multi-worker deployments break file routing |
| **Security** | No access control on local filesystem exports |

## Affected Files

| File | Issue |
|------|-------|
| `src/solstein/exporters/excel.py` | Writes to local disk |
| `src/solstein/exporters/pdf.py` | Writes to local disk |
| `src/solstein/exporters/markdown.py` | Writes to local disk |
| `src/solstein/exporters/llm.py` | Writes to local disk |

## Architectural Requirements

- All exporters write to `io.BytesIO` buffer (never to disk)
- Buffer uploaded to Supabase Storage on completion: bucket `exports/{tenant_id}/{date}/{job_id}.{ext}`
- Signed URL with 7-day expiry returned from upload operation
- Upload failure: retry 3 times, then mark export_job as failed and write to DLQ
- Local `EXPORT_DIR` config deprecated — startup warning if set, ignored in new code path
- Exports bucket has server-side encryption enabled (Supabase default)
- Objects auto-deleted after 7 days via Supabase Storage lifecycle policy
- Export pipeline can run correctly with zero local filesystem writes (verified in integration test)

## Acceptance Criteria

- [ ] No export file is written to local disk
- [ ] Generated export is accessible via signed Supabase Storage URL
- [ ] URL is tenant-scoped — cross-tenant access returns 403
- [ ] URL expires after 7 days
- [ ] Container restart does not affect accessibility of completed exports

## Definition of Done

- **Tests Required**: Integration test: generate export, delete worker container, verify download URL still works
- **Documentation Required**: Export storage configuration guide
- **Code Review Gate**: Reviewer confirms zero `open()` write calls in exporters

## Notes

Coordinated with STORY-105 in EPIC-028.

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
