# STORY-108: Research Pipeline Trigger UI

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Epic** | EPIC-029: Frontend Dashboard |
| **Created** | 2026-03-01 |
| **Dependencies** | STORY-106 |

## The Audit Verdict

> Research pipeline triggered via `POST /api/v1/research` — no UI exists. Currently triggered by `run_research.py` bypass script or direct API calls.

## Problem Statement

Triggering a research pipeline currently requires either running a Python script or making an authenticated API call. Neither is acceptable for a PE/VC analyst. The research trigger should be a prominent UI affordance: a search-by-company-name input, a "Research This Company" button, and immediate feedback that the job has been queued. The current state means the product's primary action is hidden behind technical tooling.

## Impact

| Dimension | Impact |
|-----------|--------|
| **User Experience** | Primary product action inaccessible to non-technical users |
| **Adoption** | Analysts cannot self-serve new company research |

## Affected Files

| File | Issue |
|------|-------|
| New: `dashboard/app/research/page.tsx` | Does not exist |
| New: `dashboard/components/ResearchTrigger.tsx` | Does not exist |

## Architectural Requirements

- Research trigger form: company name input (with autocomplete from existing companies), optional website URL, submit button
- On submit: POST to `/api/v1/research`, display job ID and link to job status
- After trigger: redirect to job status view (STORY-109) for the new job
- Recent research history: list of last 10 research jobs for the tenant with status badges
- Duplicate detection: if research is already running for a company, warn and show existing job status instead of creating duplicate
- Validation: company name required, minimum 2 characters, maximum 200 characters
- Error states: API error displayed inline (not generic "something went wrong")

## Acceptance Criteria

- [ ] Research form submits to API and receives a job ID
- [ ] After submit, user is redirected to job status for the new job
- [ ] Duplicate research detection shows existing job instead of creating new one
- [ ] Form validation prevents submission with empty company name
- [ ] API errors displayed with actionable message

## Definition of Done

- **Tests Required**: E2E test: fill form, submit, verify redirect to job status
- **Documentation Required**: None
- **Code Review Gate**: Reviewer verifies duplicate detection fires correctly

## Notes

The primary action should be a UI affordance, not a script.

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
