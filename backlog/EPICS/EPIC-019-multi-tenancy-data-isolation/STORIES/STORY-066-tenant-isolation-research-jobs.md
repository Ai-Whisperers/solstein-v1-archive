# STORY-066: Enforce Tenant Isolation in Research Pipeline and Background Jobs

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P1 |
| Severity | HIGH |
| Epic | [EPIC-019: Multi-Tenancy & Data Isolation](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-063](STORY-063-define-tenant-model.md), [STORY-064](STORY-064-supabase-rls-policies.md) |

---

## The Audit Verdict

> The Celery research pipeline in `worker_tasks.py`/`worker_tasks_v2.py` (see STORY-015) carries no tenant context. A background job initiated by Tenant A's request could, without isolation, read or write data belonging to Tenant B.

## Problem Statement

Background jobs that operate outside the HTTP request context do not inherit the authenticated user's tenant context. Without explicit tenant propagation, background jobs operate in a global namespace and can access cross-tenant data.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Data Isolation** | Background jobs can read/write across tenant boundaries |
| **Compliance** | Tenant data isolation cannot be guaranteed for async research operations |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/worker_tasks.py` | Modify | Add tenant_id parameter to all task signatures |
| `src/solstein/data/` | Modify | Pass tenant context through all data operations |
| `src/solstein/infrastructure/research_dual_write.py` | Modify | Ensure all writes are tenant-scoped |

## Architectural Requirements

*What — never how. No code.*

- **REQ-1**: Every Celery task signature must include `tenant_id` as an explicit parameter
- **REQ-2**: The `tenant_id` must be validated at task entry — tasks with missing or invalid tenant_id must be rejected
- **REQ-3**: All database writes within a background job must include the tenant_id from the task parameter, not from any ambient context
- **REQ-4**: A background job must not be able to query data outside its tenant_id, even when bypassing RLS via service role — the application must enforce this at the query-construction layer

## Acceptance Criteria

- [ ] All Celery task signatures include tenant_id
- [ ] A task with a mismatched or missing tenant_id fails with a clear error
- [ ] All database writes from background jobs carry the correct tenant_id

## Definition of Done

**Tests Required:**
- [ ] Unit test: task with invalid tenant_id rejected at entry
- [ ] Integration test: background job can only write to its own tenant's data

**Documentation Required:**
- [ ] Celery task contract documentation showing tenant_id as required parameter

**Code Review Gate:**
- [ ] Reviewer confirms no task can execute without a validated tenant_id
- [ ] Reviewer confirms all database operations within tasks are tenant-scoped

## Notes

This story closes the last gap in tenant isolation: the asynchronous boundary. HTTP requests carry tenant context via JWT claims. Background jobs must carry it explicitly. If STORY-064 (RLS) is in place, RLS provides a safety net — but the application layer must still enforce tenant scoping to avoid reliance on the service-role bypass granting global access.

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
