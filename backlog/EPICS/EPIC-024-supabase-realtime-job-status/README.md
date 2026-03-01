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
