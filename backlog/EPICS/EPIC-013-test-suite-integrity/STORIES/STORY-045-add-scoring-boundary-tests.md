# STORY-045: Add Boundary Tests for All Scoring Tiers

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P2 |
| Severity | HIGH |
| Epic | [EPIC-013: Test Suite Integrity](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-009: Unify Scoring Thresholds](../../EPIC-003-core-product-correctness/STORIES/STORY-009.md), [STORY-011: Name Scoring Constants](../../EPIC-003-core-product-correctness/STORIES/STORY-011.md) |

---

## The Audit Verdict
> The scoring system has three tier boundaries and zero automated tests verifying that a specific score maps to a specific tier. The thresholds themselves conflict across three files (see STORY-009). Even after the thresholds are unified, without boundary tests, a threshold change will go undetected until a client receives a wrong classification.

## Problem Statement
The most critical behavioural contract of the platform — that a composite score of X maps to tier Y — has no automated verification. Threshold values can be changed without any test failing. Regressions in tier classification are invisible to the CI pipeline. The platform's primary output is unguarded.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Regression Risk** | Threshold changes are undetected by CI — a single-character edit to a threshold value breaks the product with no test failure |
| **Contract** | The platform's primary output (company tier classification) has no automated quality gate |
| **Confidence** | Engineers cannot safely calibrate the scoring model — there is no way to verify that a calibration change preserves the expected tier mappings |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `tests/unit/test_scoring_boundaries.py` | Add | Create this file with comprehensive boundary tests |

## Architectural Requirements
*What the system must satisfy. No implementation instructions. No code. Only what — never how.*

- **REQ-1**: A test must exist for each tier boundary, verifying the score immediately above and immediately below each threshold produces different tiers
- **REQ-2**: Tests must use the named constants from STORY-011 (not numeric literals) so threshold changes automatically update test expectations
- **REQ-3**: Boundary tests must cover all tiers: Lead, Prospect, Monitor, and any others defined in classification.py
- **REQ-4**: Tests must exercise the classification function through the same code path used in production — not through test-only shortcuts or helper functions that bypass real logic

## Acceptance Criteria
- [ ] A test exists for score = THRESHOLD - epsilon → lower tier
- [ ] A test exists for score = THRESHOLD → correct tier (verify boundary inclusion/exclusion rule)
- [ ] A test exists for score = THRESHOLD + epsilon → upper tier
- [ ] All boundary tests use named constants, not numeric literals
- [ ] Tests cover every tier defined in the classification system

## Definition of Done

**Tests Required:**
- [ ] All boundary tests pass in CI
- [ ] Each tier transition has at least three test cases (below, at, above threshold)

**Documentation Required:**
- [ ] Add boundary test pattern to contributing guide so future scoring changes include boundary tests

**Code Review Gate:**
- [ ] Reviewer confirms tests use named constants from the scoring module
- [ ] Reviewer confirms tests exercise the production classification code path

## Notes
This story depends on STORY-009 (threshold unification) and STORY-011 (named constants). Writing boundary tests against contradictory thresholds or magic numbers would be pointless — the tests would encode the wrong values. After the thresholds are unified and named, boundary tests lock them in place and prevent regression. This is one of the highest-value test additions in the entire backlog.

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
