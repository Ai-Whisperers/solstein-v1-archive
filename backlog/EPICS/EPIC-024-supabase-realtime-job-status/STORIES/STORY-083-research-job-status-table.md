# STORY-083: Define Research Job Status Table with Supabase Realtime Replication

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P2 |
| Severity | HIGH |
| Epic | [EPIC-024: Supabase Realtime Job Status](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-063](../../EPIC-019-multi-tenancy-data-isolation/STORIES/STORY-063-define-tenant-model.md) (tenant model), [STORY-087](../../EPIC-018-infrastructure-cicd/STORIES/STORY-087-celery-dead-letter-queue.md) (Celery DLQ) |

---

## The Audit Verdict

> No `research_jobs` table exists with job status tracking. The Celery task system has no user-visible job status. A client that initiates a research job has no mechanism to determine when it completes, whether it failed, or what progress has been made. The AGENTS.md mentions background tasks but no status tracking infrastructure.

## Problem Statement

Long-running research jobs with no client-visible status feedback create a poor user experience and make debugging difficult. Clients cannot distinguish a job that is running from one that silently failed. Operations teams cannot determine how many jobs are in flight, how long they take, or where they fail. The absence of a job status table is simultaneously a UX problem, an observability problem, and a reliability problem.

## Impact

| Dimension | Effect |
|-----------|--------|
| **User Experience** | No progress feedback — users stare at a spinner with no way to know if a job is running, stuck, or failed |
| **Observability** | No job telemetry — operations cannot determine job throughput, failure rates, or duration |
| **Reliability** | Silent failures go undetected — a job that dies mid-execution leaves no trace |
| **Architecture** | STORY-084 (Realtime subscriptions) is blocked without a table to subscribe to |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/infrastructure/database_models.py` | Modify | Add ResearchJob model |
| New Alembic migration | Add | Add research_jobs table |
| Supabase project | Modify | Enable Realtime replication for research_jobs table |
| `src/solstein/worker_tasks.py` | Modify | Update job tasks to write status to research_jobs table |

## Architectural Requirements

*What — never how. No code.*

- **REQ-1**: A `research_jobs` table must exist with columns: `id`, `tenant_id`, `company_id`, `status` (queued/running/completed/failed/cancelled), `progress_pct`, `error_message`, `created_at`, `started_at`, `completed_at`
- **REQ-2**: Supabase Realtime must be enabled for the `research_jobs` table — row changes must be broadcast to subscribed clients
- **REQ-3**: RLS must apply to the `research_jobs` table — clients can only subscribe to their own tenant's jobs
- **REQ-4**: Celery worker tasks must write status updates to `research_jobs` at defined checkpoints: job start, each agent completion, final success/failure
- **REQ-5**: Job records must be retained for a configurable retention period after completion — not deleted immediately

## Acceptance Criteria

- [ ] `research_jobs` table exists with all required columns
- [ ] Supabase Realtime is enabled for the table
- [ ] RLS prevents cross-tenant job status access
- [ ] A running research job updates its status record at each pipeline stage
- [ ] Job status transitions follow a valid state machine (queued → running → completed/failed)

## Definition of Done

**Tests Required:**
- [ ] Integration test: starting a research job creates a job record with `status=queued`
- [ ] Integration test: job completion updates `status=completed` with `completed_at` timestamp
- [ ] Integration test: job failure updates `status=failed` with `error_message`
- [ ] RLS test: Tenant A cannot subscribe to Tenant B's job updates

**Documentation Required:**
- [ ] Job status state machine documented (valid transitions)
- [ ] Retention policy configuration documented
- [ ] Supabase Realtime enablement procedure documented

**Code Review Gate:**
- [ ] RLS policies reviewed for correctness — no cross-tenant leakage
- [ ] Status update checkpoints reviewed for completeness — all pipeline stages represented
- [ ] Migration reviewed for backward compatibility

## Notes

- The `progress_pct` field is an approximation. Research pipelines have a variable number of stages depending on company data availability. A percentage that jumps from 20% to 80% is acceptable — a percentage that never updates is not.
- Consider adding a `metadata` JSONB column for extensibility — pipeline stage names, agent outputs, intermediate results. This avoids schema changes as the pipeline evolves.
- The retention period should default to 30 days. Completed and failed job records are valuable for debugging and analytics. Deleting them immediately is a false economy.

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
