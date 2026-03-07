# STORY-084: Replace Polling with Supabase Realtime Job Status Subscriptions

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P2 |
| Severity | HIGH |
| Epic | [EPIC-024: Supabase Realtime Job Status](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-083](STORY-083-research-job-status-table.md) |

---

## The Audit Verdict

> No real-time job status delivery exists. The Next.js dashboard (`dashboard/`) has no WebSocket or Realtime connection for research job updates. Any client-side progress indication requires polling an API endpoint at arbitrary intervals — an approach that is both inefficient and provides poor user experience for minute-long operations.

## Problem Statement

Polling for job status wastes server resources on requests that return no new information, degrades the experience for operations that complete in unpredictable time, and requires the client to implement polling logic that must be tuned to balance responsiveness against server load. Supabase Realtime eliminates all three problems by pushing database row changes directly to subscribed clients over an existing WebSocket connection.

## Impact

| Dimension | Effect |
|-----------|--------|
| **User Experience** | No live progress feedback — users cannot see research jobs progressing in real time |
| **Server Load** | Polling generates requests proportional to (active jobs × connected clients × poll frequency) — most of which return unchanged data |
| **Reliability** | Polling misses status transitions that occur between poll intervals — a job that starts and fails within one interval is never seen as "running" |
| **Latency** | Average status update delay equals half the polling interval — Realtime reduces this to milliseconds |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `dashboard/` | Modify | Add Supabase Realtime subscription for job status in the research job UI component |
| `src/solstein/api/` | Modify | Verify job initiation response includes `job_id` for subscription targeting |
| Documentation | Add | Update integration guide with Realtime subscription example |

## Architectural Requirements

*What — never how. No code.*

- **REQ-1**: The Next.js dashboard must subscribe to Supabase Realtime changes on the `research_jobs` table, filtered by the authenticated user's tenant and the specific `job_id`
- **REQ-2**: Job status changes must be reflected in the UI within 500ms of the database update — no polling
- **REQ-3**: The subscription must be established immediately after job initiation — not after the first manual refresh
- **REQ-4**: Subscription must be automatically cleaned up when the job completes or the user navigates away
- **REQ-5**: A fallback polling mechanism (configurable) must exist for environments where WebSockets are not available — but must not be the primary path
- **REQ-6**: The Supabase client-side SDK must be the only WebSocket mechanism — no custom WebSocket implementation

## Acceptance Criteria

- [ ] Research job status updates appear in the UI without a page refresh
- [ ] Status update latency is under 500ms from database write to UI update
- [ ] Navigating away from the job page cleans up the subscription
- [ ] No polling requests appear in the browser network tab during an active Realtime subscription
- [ ] Fallback polling activates when WebSocket connection fails

## Definition of Done

**Tests Required:**
- [ ] E2E test: initiate job, observe status update in UI without refresh
- [ ] Cleanup test: navigation away cancels subscription (no orphaned subscriptions)
- [ ] Latency test: database write to UI update < 500ms
- [ ] Fallback test: WebSocket failure triggers polling fallback

**Documentation Required:**
- [ ] Supabase Realtime subscription pattern documented for other developers
- [ ] Fallback polling configuration documented
- [ ] Troubleshooting guide for WebSocket connection issues

**Code Review Gate:**
- [ ] Subscription cleanup verified — no memory leaks from orphaned subscriptions
- [ ] Supabase SDK used exclusively — no custom WebSocket code
- [ ] Fallback mechanism reviewed for correctness

## Notes

- The Supabase JavaScript client SDK handles WebSocket connection management, reconnection, and channel subscription natively. Do not reimplement any of this.
- The 500ms latency target is measured end-to-end: database `UPDATE` statement executes → Supabase Realtime broadcasts → client SDK receives → React state updates → DOM renders. This is achievable with Supabase Realtime's default configuration.
- Orphaned subscriptions are the primary risk. React component unmounting must cancel the subscription. React Strict Mode (development) will mount/unmount/remount — the subscription logic must handle this gracefully.
- The fallback polling mechanism should be opt-in via configuration, not automatic. If WebSockets work (and they will in any modern environment), polling should never activate.
