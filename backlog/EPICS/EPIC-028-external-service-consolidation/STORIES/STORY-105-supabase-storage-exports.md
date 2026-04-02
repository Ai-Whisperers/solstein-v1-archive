# STORY-105: Move File Exports to Supabase Storage

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | Medium |
| **Epic** | EPIC-028: External Service Consolidation |
| **Created** | 2026-03-01 |
| **Dependencies** | EPIC-019, EPIC-020 |

## The Audit Verdict

> `src/solstein/exporters/excel.py` and `src/solstein/exporters/markdown.py` write to local filesystem. Path appears to be a configured local directory. In a containerized, horizontally-scaled environment, local filesystem writes are ephemeral.

## Problem Statement

Export files written to local disk disappear when the container restarts. In a horizontally scaled deployment (2+ API replicas), a file written by replica 1 is invisible to replica 2 — a user who triggered an export on one request and tries to download it on the next gets a 404 because load balancing sent them to a different replica. Supabase Storage is already in the stack (EPIC-020 dependency), supports tenant-scoped buckets, signed URLs for secure downloads, and automatic expiry. There is no reason to use local disk.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Reliability** | Exports lost on container restart |
| **Scalability** | Horizontal scaling breaks file downloads |
| **Security** | No access control on local filesystem exports |

## Affected Files

| File | Issue |
|------|-------|
| `src/solstein/exporters/excel.py` | Writes to local disk |
| `src/solstein/exporters/markdown.py` | Writes to local disk |
| `src/solstein/exporters/llm.py` | Writes to local disk |

## Architectural Requirements

- Supabase Storage client integrated into export pipeline
- Per-tenant bucket (or tenant-prefixed path) for export isolation — users cannot access other tenants' exports
- Upload: export written to memory buffer, uploaded to Supabase Storage, local file never written to disk
- Signed download URL generated with 24-hour expiry returned to API caller
- Export metadata (filename, size, format, created_at, expires_at, tenant_id, user_id) stored in PostgreSQL `exports` table
- Old exports cleaned up: Supabase Storage lifecycle rule deletes objects after 7 days
- Local filesystem export path config (`EXPORT_DIR`) deprecated with a deprecation warning on startup if set

## Acceptance Criteria

- [ ] Export API response contains a signed Supabase Storage URL, not a local file path
- [ ] Signed URL expires after 24 hours
- [ ] Export is accessible from any API replica (not replica-local)
- [ ] Exports are scoped to tenant — cross-tenant download returns 403
- [ ] Objects deleted from Supabase Storage after 7 days

## Definition of Done

- **Tests Required**: Integration test: trigger export on replica 1, download via signed URL
- **Documentation Required**: Export storage migration guide
- **Code Review Gate**: Reviewer confirms zero `open()` or `os.path` write calls remain in exporters

## Notes

Local disk has no place in a containerized, scalable architecture.

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
