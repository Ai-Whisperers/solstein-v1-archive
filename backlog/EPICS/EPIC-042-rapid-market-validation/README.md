# EPIC-042: Rapid Market Validation Methodology

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | Medium |
| **Owner** | Product Strategy |
| **Created** | 2026-03-01 |

## Context

The call emphasized rapid "click and deploy" MVPs for market validation. Solstein needs infrastructure to quickly spin up market intelligence for new sectors or geographies — not 3-month implementations, but 3-day proofs of concept. This includes: automated data source discovery for new markets, template-based scoring models that can be customized quickly, and rapid export of intelligence reports for stakeholder validation. Energy 21 becomes the template for this methodology — documented, repeatable, and fast.

## Stories

| Story | Title | Priority |
|-------|-------|----------|
| STORY-161 | Automated Data Source Discovery for New Markets | P2 |
| STORY-162 | Template-Based Scoring Model Customization | P2 |
| STORY-163 | Energy 21 Case Study Documentation System | P2 |
| STORY-164 | Proof-of-Concept Metrics & Success Tracking | P2 |

## Dependencies

- EPIC-007 (DDD Migration) — for flexible domain models
- EPIC-028 (External Service Consolidation) — for rapid data source integration

## Notes

Speed to market validation is a competitive advantage. The methodology must be documented, repeatable, and fast.

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
