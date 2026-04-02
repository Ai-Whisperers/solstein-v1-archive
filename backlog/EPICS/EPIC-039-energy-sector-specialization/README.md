# EPIC-039: Energy Sector Domain Specialization

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | High |
| **Owner** | Domain Engineering |
| **Created** | 2026-03-01 |

## Context

Energy 21 is the living proof case for Solstein's methodology. The call revealed four key B2B energy domains where AI transformation creates value: compliance & control, forecasting, portfolio management, and trading platforms. Solstein needs energy-sector-specific intelligence modules that understand these domains deeply — not generic company scoring, but energy-specific signals like regulatory compliance status, forecasting accuracy, trading platform sophistication, and grid integration capabilities. This positions Solstein as the definitive intelligence platform for energy sector PE deals.

## Stories

| Story | Title | Priority |
|-------|-------|----------|
| STORY-149 | Energy Compliance & Control Intelligence Module | P1 |
| STORY-150 | Energy Forecasting Capability Scoring | P1 |
| STORY-151 | Trading Platform Sophistication Assessment | P2 |
| STORY-152 | Grid Point Access & Integration Scoring | P2 |

## Dependencies

- EPIC-023 (pgvector) — for energy company similarity search
- EPIC-039 (Business Rules Documentation) — energy-specific scoring rules

## Notes

Energy sector becomes Solstein's beachhead market. Deep domain expertise is the moat that AI sharks cannot cross.

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
