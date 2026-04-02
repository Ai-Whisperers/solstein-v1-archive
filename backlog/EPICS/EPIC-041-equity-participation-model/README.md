# EPIC-041: Equity Participation Business Model

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Owner** | Business Strategy |
| **Created** | 2026-03-01 |

## Context

The call revealed Solstein's long-term strategic shift: from SaaS/consulting fees to equity participation in transformed companies. This is the "Vortex" model — taking equity in portfolio companies that use Solstein's intelligence and transformation methodology. The platform needs infrastructure to track equity positions, correlate Solstein insights with portfolio company performance, and support equity-based billing (not just monthly SaaS subscriptions). This fundamentally changes Solstein from a tool vendor to a capital infrastructure partner.

## Stories

| Story | Title | Priority |
|-------|-------|----------|
| STORY-157 | Cap Table Integration & Equity Tracking | P2 |
| STORY-158 | Portfolio Company Performance Correlation | P2 |
| STORY-159 | Equity-Based Billing & Revenue Recognition | P2 |
| STORY-160 | Investment Thesis Documentation & Tracking | P2 |

## Dependencies

- EPIC-019 (Multi-Tenancy) — for portfolio company data isolation
- EPIC-014 (Observability) — for performance tracking

## Notes

This transforms Solstein from "software vendor" to "capital infrastructure partner." The platform becomes a cap table participant, not just a tool.

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
