# STORY-149: Energy Compliance & Control Intelligence Module

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | High |
| **Epic** | EPIC-039: Energy Sector Domain Specialization |
| **Created** | 2026-03-01 |
| **Dependencies** | None |

## The Strategic Context

> "Energy 21 covers compliance & control, forecasting, portfolio management, trading platforms — all B2B."

## Problem Statement

Energy sector companies operate under heavy regulatory burden: grid compliance, emissions reporting, safety standards, market regulations. Solstein's generic scoring misses these critical dimensions. An energy company with poor compliance posture is a liability, regardless of growth metrics. This module adds energy-specific signals: regulatory compliance status, control system sophistication, audit history, and regulatory change exposure.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Risk Assessment** | Identify compliance liabilities pre-investment |
| **Sector Differentiation** | Energy-specific intelligence vs. generic scoring |
| **Regulatory Tracking** | Monitor compliance changes affecting portfolio |

## Affected Files

| File | Issue |
|------|-------|
| `agents/` | No energy compliance agents |
| `analytics/scoring.py` | No compliance scoring dimension |

## Architectural Requirements

- Compliance signals: regulatory filings (ENTSO-E, national regulators), audit reports, violation history, certification status (ISO, SOC, etc.)
- Control system assessment: SCADA/DMS sophistication, automation level, cybersecurity posture
- Regulatory change tracking: upcoming regulations affecting energy sector, compliance deadlines
- Risk scoring: compliance risk as separate dimension (High/Medium/Low)
- Data sources: regulatory databases, company disclosures, industry reports
- Alerting: notify when portfolio companies face compliance changes
- Integration: link compliance status to overall company classification

## Acceptance Criteria

- [ ] Compliance status signals collected for energy companies
- [ ] Control system sophistication scored
- [ ] Regulatory change tracking active
- [ ] Compliance risk dimension affects overall scoring
- [ ] Alerts generated for portfolio compliance changes

## Definition of Done

- **Tests Required**: Validation against known compliant vs. non-compliant energy companies
- **Documentation Required**: Energy compliance scoring methodology
- **Code Review Gate**: Reviewer verifies data sources are authoritative

## Notes

Compliance is a make-or-break factor in energy sector investments.

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
