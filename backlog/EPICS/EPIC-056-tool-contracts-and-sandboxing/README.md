# EPIC-056: Inline Claim Adjudication and Approval Workflow

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Created** | 2026-03-10 |
| **Stories** | STORY-214, STORY-215, STORY-216, STORY-217 |
| **Dependencies** | EPIC-052 |

## Context

Contradictions and low-confidence claims are identified but not consistently escalated to explicit review decisions before scoring/export. Framework patterns from Agno approvals and CrewAI reviewer loops indicate this needs an inline adjudication workflow with auditable decisions.

This epic introduces claim-level review gates and approval handling before downstream classification and export.

## Scope

| Category | Action |
|----------|--------|
| Escalation | Route critical contradictions and low-confidence claims to review queue |
| Decisions | Add approve/reject/override decision API and persistence |
| Gating | Block scoring/export on unresolved critical claims |
| Feedback | Feed adjudication outcomes back into merge/confidence logic |

## Stories

| Story | Title | Priority | Status |
|-------|-------|----------|--------|
| STORY-214 | Detect and escalate critical contradictory claims | P1 | 🔴 Not Started |
| STORY-215 | Implement decision model and adjudication API | P1 | 🔴 Not Started |
| STORY-216 | Enforce scoring/export hold for unresolved critical claims | P1 | 🔴 Not Started |
| STORY-217 | Update merge strategy from adjudication outcomes | P2 | 🔴 Not Started |

## Success Criteria

- Critical claims (`revenue`, `employee_count`, `funding_total`, `valuation`) escalate on contradiction.
- Review decisions are persisted with actor, timestamp, reason, and claim references.
- Scoring/export is blocked until critical claim is resolved or justified override is recorded.
- Merge preferences and confidence are updated using adjudication trail.

## Risks

| Risk | Mitigation |
|------|------------|
| Contract rigidity slows new connector addition | Provide versioned optional fields and migration helpers |
| Sandboxing breaks legacy scripts | Add compatibility adapter and phased migration |
| Partial failures become noisy | Normalize failure taxonomy and severity levels |

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
