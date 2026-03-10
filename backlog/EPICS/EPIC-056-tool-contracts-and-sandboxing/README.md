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
