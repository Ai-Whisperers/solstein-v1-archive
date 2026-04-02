# STORY-109: Real-Time Job Status UI via Supabase Realtime

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Epic** | EPIC-029: Frontend Dashboard |
| **Created** | 2026-03-01 |
| **Dependencies** | STORY-106, EPIC-024 |

## The Audit Verdict

> No job status UI exists. STORY-083 and STORY-084 (EPIC-024) define the backend: `research_jobs` table with Supabase Realtime enabled. This story consumes that backend.

## Problem Statement

A research pipeline that takes 5-15 minutes with no visual feedback creates the worst possible UX: users assume it failed, re-trigger it, and produce duplicate jobs. The job status page must show live progress without polling — using the Supabase Realtime subscription established in EPIC-024. A progress indicator that updates in real-time is the difference between a user who trusts the system and a user who doesn't.

## Impact

| Dimension | Impact |
|-----------|--------|
| **User Experience** | Uncertainty and re-triggers without live feedback |
| **Cost** | Duplicate jobs from impatient users |
| **Trust** | Users abandon sessions without progress visibility |

## Affected Files

| File | Issue |
|------|-------|
| New: `dashboard/app/jobs/[id]/page.tsx` | Does not exist |
| New: `dashboard/components/JobStatusCard.tsx` | Does not exist |

## Architectural Requirements

- Job status page: displays job ID, company name, current status (queued/running/completed/failed), progress percentage bar, duration, error message (if failed)
- Supabase Realtime subscription to `research_jobs` table filtered by `job_id` — status updates render without page refresh
- Progress stages visually represented: Queued → Data Collection → Signal Extraction → Scoring → Classification → Complete
- Completed state: shows summary (company name, final classification, score) with links to company detail and export
- Failed state: shows error message with "Retry" button
- All jobs list page: shows all tenant jobs, paginated, filterable by status
- Subscription cleanup on page navigation (no memory leaks)
- Fallback to polling if Supabase Realtime connection drops (EPIC-024 requirement)

## Acceptance Criteria

- [ ] Job status updates without page refresh when backend updates the research_jobs row
- [ ] Progress percentage bar advances as pipeline stages complete
- [ ] Completed jobs show company classification and score
- [ ] Failed jobs show error message and retry button
- [ ] Navigating away from page cleans up Realtime subscription

## Definition of Done

- **Tests Required**: E2E test: trigger research, verify job status page updates without polling
- **Documentation Required**: None
- **Code Review Gate**: Reviewer verifies subscription is cleaned up on unmount

## Notes

Real-time feedback builds trust.

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
