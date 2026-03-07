# STORY-011: Name and Document All Scoring Constants

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P0 |
| Severity | MEDIUM |
| Epic | [EPIC-003: Core Product Correctness](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-009](STORY-009-unify-classification-thresholds.md), [STORY-010](STORY-010-eliminate-scoring-duplication.md) (Thresholds unified and scoring consolidated — naming constants in files about to be deleted or restructured is wasted work) |

---

## The Audit Verdict

> Scoring uses magic numbers throughout: `0.4 / 0.3 / 0.3` (component weights), `7.0` (score ceiling), `3.9` (Lead threshold), `1.0 - (d / 3.0)` (data freshness decay). None are named constants. None have explanatory comments. They exist as numeric literals dispersed across at least three files.

## Problem Statement

Magic numeric literals in scoring code make the system's behaviour opaque to anyone who did not write the original formulas. An engineer asked to adjust the "growth weight" must first determine that `0.3` is the growth weight, that the `0.3` on the next line is the competitive position weight (not a second reference to growth), and that the `0.4` before both is the financial health weight. Boundary tests cannot exist for thresholds without knowing what the thresholds represent. Formula changes cannot be audited because there is no named reference to diff against.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Maintainability** | No engineer can confidently modify scoring without risk of unintentional behavioural change |
| **Testability** | Boundary tests are impossible to write without understanding what each number means |
| **Auditability** | PE/VC clients requesting scoring methodology documentation cannot be satisfied — the methodology exists only as unnamed numbers in source code |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/analytics/scoring.py` | Modify | Replace all numeric literals with named constants |
| `src/solstein/analytics/classification.py` | Modify | Same — all threshold literals become named constants |
| `src/solstein/analytics/scorers/financial_health.py` | Modify | Same — all formula literals become named constants |
| `src/solstein/analytics/scorers/growth_momentum.py` | Modify | Same — all formula literals become named constants |
| `tests/unit/test_scoring_boundaries.py` | Add | Boundary tests using named constants |

## Architectural Requirements

*What the system must satisfy. No implementation instructions. No code. Only what — never how.*

- **REQ-1**: Every numeric literal used in scoring logic must be replaced with a named constant at module level
- **REQ-2**: Each constant must have a docstring or inline comment stating its business meaning and the rationale for its value
- **REQ-3**: The weight constants must be asserted to sum to 1.0 in a test
- **REQ-4**: Boundary tests must cover the exact score value at each tier transition

## Acceptance Criteria

- [ ] No unexplained numeric literals (values other than 0 and 1 used in arithmetic) appear in scoring logic
- [ ] Each scoring constant has a descriptive name (e.g., `FINANCIAL_HEALTH_WEIGHT` not `W1`)
- [ ] A test asserts `FINANCIAL_HEALTH_WEIGHT + GROWTH_MOMENTUM_WEIGHT + COMPETITIVE_POSITION_WEIGHT == 1.0`
- [ ] Each tier boundary has a named constant with a documented business meaning

## Definition of Done

**Tests Required:**
- [ ] Test: component weights sum to 1.0
- [ ] Test: score equal to each tier boundary produces the correct tier
- [ ] Test: score one unit above and below each tier boundary produces the correct adjacent tiers
- [ ] Test: data freshness decay formula produces expected output at known time deltas

**Documentation Required:**
- [ ] Each constant documented with: name, value, business meaning, and source of the value (who decided, when)
- [ ] Scoring methodology document referencing named constants (not numeric values)

**Code Review Gate:**
- [ ] Reviewer confirms no unexplained numeric literal exists in any scoring file
- [ ] Reviewer confirms constant names are descriptive and unambiguous

## Notes

This story must be the last in the EPIC-003 sequence. Naming constants in files that are about to be restructured (STORY-010) or that contain the wrong threshold values (STORY-009) is wasted work. Both predecessors must complete before this story begins. The story itself is lower severity than its predecessors — unnamed constants are a maintainability problem, not a correctness problem — but it remains P0 because the platform cannot ship without auditable scoring methodology.
