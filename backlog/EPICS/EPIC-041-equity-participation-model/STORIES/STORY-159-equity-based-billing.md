# STORY-159: Equity-Based Billing & Revenue Recognition

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Epic** | EPIC-041: Equity Participation Business Model |
| **Created** | 2026-03-01 |
| **Dependencies** | STORY-157 |

## The Strategic Context

> "Equity participation, not just monthly SaaS subscriptions."

## Problem Statement

Solstein's business model is shifting from SaaS fees to equity participation. This requires different billing infrastructure: tracking equity value vs. subscription MRR, revenue recognition for equity (different from SaaS), cap table management as a "billing" system. The platform needs to treat equity positions as revenue-generating assets.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Business Model** | Support equity-based revenue |
| **Financial Reporting** | Proper equity revenue recognition |
| **Investor Reporting** | Show equity portfolio value |

## Affected Files

| File | Issue |
|------|-------|
| New: `application/billing/` | SaaS-only billing currently |
| `domain/equity/` | No equity revenue tracking |

## Architectural Requirements

- Equity value tracking: mark-to-market valuation of equity positions
- Revenue recognition: equity gains realized vs. unrealized, proper accounting treatment
- Billing hybrid model: support both SaaS (existing) and equity (new) revenue streams
- Portfolio valuation: total equity portfolio value, changes over time
- Carry calculation: if Solstein acts as GP, calculate carried interest
- Reporting: equity portfolio reports for investors/board
- Tax considerations: track tax basis, capital gains/losses
- Forecasting: project equity value based on company performance

## Acceptance Criteria

- [ ] Equity positions valued and tracked
- [ ] Revenue recognized correctly for equity gains
- [ ] Hybrid SaaS + equity billing supported
- [ ] Portfolio valuation reports generated
- [ ] Tax tracking implemented

## Definition of Done

- **Tests Required**: Revenue recognition accuracy tests
- **Documentation Required**: Equity billing accounting guide
- **Code Review Gate**: Accountant reviews revenue recognition logic

## Notes

This is venture capital infrastructure, not SaaS billing.

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
