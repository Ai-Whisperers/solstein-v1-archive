# EPIC-024: Supabase Realtime for Research Job Status

| Field | Value |
|-------|-------|
| Priority | **P2** |
| Status | 🔴 Open |
| Stories | 2 |
| Created | 2026-02-28 |
| Depends On | [EPIC-019](../EPIC-019-multi-tenancy-data-isolation/README.md), [EPIC-020](../EPIC-020-supabase-auth-migration/README.md) |

## Context

Research jobs are long-running operations. A comprehensive enrichment job for a portfolio company can take minutes. Currently, there is no mechanism for the client to know when a job completes — no WebSocket endpoint, no server-sent events, no polling endpoint with meaningful job status. Clients must poll the research endpoint repeatedly and hope the job finishes.

Supabase Realtime broadcasts PostgreSQL row changes via WebSocket. A research job status update in the `research_jobs` table is instantly pushed to any connected client subscribed to that job's channel. No polling. No separate WebSocket server. No additional infrastructure. It works with the existing PostgreSQL database, scoped to the authenticated tenant via RLS.

## Scope

| Story | Title | Severity |
|-------|-------|----------|
| [STORY-083](STORIES/STORY-083-research-job-status-table.md) | Define Research Job Status Table with Realtime Replication | HIGH |
| [STORY-084](STORIES/STORY-084-realtime-subscription.md) | Replace Polling Pattern with Supabase Realtime Subscriptions | HIGH |

## Definition of Done

- [ ] A `research_jobs` table tracks job status with Realtime enabled
- [ ] Job status changes are pushed to connected clients without polling
- [ ] Job status is tenant-scoped — clients only receive updates for their tenant's jobs
- [ ] The Next.js dashboard receives job status updates via Supabase Realtime client SDK

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This epic currently carries a historical open or in-progress backlog badge.
- If `planning/QUEUE.md` does not currently schedule this epic, treat it as triage-required backlog inventory instead of self-startable work.

### Next Agent Action

- Reconcile this epic against current code reality, `planning/QUEUE.md`, and the develop autonomy audit before selecting a story.
- Do not start implementation from this README alone unless the queue or a fresh planning decision activates the epic.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`, `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`, and `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Prefer narrow, machine-checkable progress over broad narrative backlog churn.

### Minimum Verification For Future Agents

- If this epic is reactivated, update the queue or controlling planning artifact first.
- Then execute one story at a time with the relevant tests, gates, and generated references for the touched surface.
