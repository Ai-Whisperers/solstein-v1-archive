# STORY-039: Document Business Rationale for All Scoring Rules

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P2 |
| Severity | MEDIUM |
| Epic | [EPIC-011: Business Rules Documentation](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-009: Unify Scoring Thresholds](../../EPIC-003-core-product-correctness/STORIES/STORY-009.md), [STORY-010: Deduplicate Scoring Logic](../../EPIC-003-core-product-correctness/STORIES/STORY-010.md) |

---

## The Audit Verdict
> The scoring system uses magic numbers `0.4 / 0.3 / 0.3`, `7.0`, `3.9`, and the decay formula `1.0 - (d / 3.0)` as numeric literals with no named constants, no comments, and no documented origin. Anyone modifying these values does so without knowing what they represent or who decided them.

## Problem Statement
Scoring weights, thresholds, ceilings, and decay formulas are embedded as unexplained numeric literals. The scoring methodology cannot be communicated to clients, audited by management, or safely modified by engineers. These numbers are the core intellectual property of the platform, and they are indistinguishable from arbitrary constants to anyone reading the code.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Auditability** | PE/VC clients cannot receive a documented scoring methodology — the platform's primary deliverable is unexplainable |
| **Maintainability** | Calibration changes cannot be made with confidence — there is no way to know if a value was chosen deliberately or arbitrarily |
| **Onboarding** | New engineers cannot understand the scoring system from the code — it requires oral history from the original author |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/analytics/scoring.py` | Modify | Replace all numeric literals with named, documented constants |
| `src/solstein/analytics/classification.py` | Modify | Replace threshold literals with named constants |
| `src/solstein/analytics/scorers/financial_health.py` | Modify | Extract weight and formula constants |
| `src/solstein/analytics/scorers/growth_momentum.py` | Modify | Extract weight and formula constants |
| `src/solstein/analytics/scorers/competitive_position.py` | Modify | Extract weight and formula constants |
| `docs/scoring-methodology.md` | Add | Create: plain-language description of the scoring model |

## Architectural Requirements
*What the system must satisfy. No implementation instructions. No code. Only what — never how.*

- **REQ-1**: Every numeric literal in scoring logic must become a named module-level constant with a docstring stating its business meaning, its value, and who approved it
- **REQ-2**: Constants must use descriptive names (e.g., `FINANCIAL_HEALTH_WEIGHT` not `W1`) — the name must communicate domain meaning without requiring a comment
- **REQ-3**: A `docs/scoring-methodology.md` document must describe the scoring model in plain language: what the three components measure, how they are weighted, how tiers are defined, and how data freshness decay is applied
- **REQ-4**: The document must be accurate — it must match the actual code, verified by a reviewer who reads both the document and the code

## Acceptance Criteria
- [ ] No unexplained numeric literal (not 0.0, 1.0, or trivial arithmetic) appears in any scoring file
- [ ] Each constant has a docstring with business meaning and originating rationale
- [ ] `docs/scoring-methodology.md` exists and accurately describes the current model
- [ ] A test asserts `FINANCIAL_HEALTH_WEIGHT + GROWTH_MOMENTUM_WEIGHT + COMPETITIVE_POSITION_WEIGHT == 1.0`

## Definition of Done

**Tests Required:**
- [ ] Test: scoring weights sum to 1.0
- [ ] Test: all named constants are importable and have expected values

**Documentation Required:**
- [ ] `docs/scoring-methodology.md` reviewed by a non-engineer stakeholder

**Code Review Gate:**
- [ ] Reviewer confirms all numeric literals in scoring files have been replaced with named constants
- [ ] Reviewer reads both `docs/scoring-methodology.md` and the code and confirms they match

## Notes
This story must follow STORY-009 (threshold unification) and STORY-010 (scoring deduplication) — naming constants that are about to be changed or consolidated is wasted effort. The documentation should describe the post-unification state, not the current contradictory state.

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
