# STORY-009: Unify Classification Thresholds Across All Files

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P0 |
| Severity | CRITICAL |
| Epic | [EPIC-003: Core Product Correctness](../README.md) |
| Created | 2026-02-28 |
| Dependencies | None |

---

## The Audit Verdict

> Three separate locations define the numerical threshold that separates "Lead" from "Prospect": `analytics/scoring.py` uses ≤ 3.9, `analytics/classification.py` uses < 5.5, and router handlers contain their own hardcoded values. The platform's primary output — company tier — is non-deterministic.

## Problem Statement

Classification thresholds are defined independently in at least three code locations with different numerical values. Depending on which function is called, the same composite score can yield different tier assignments. This is not a display difference — it is a correctness failure in the platform's core output. A PE/VC client querying the same company via different API paths receives different tier classifications.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Product Correctness** | The same company can be classified as different tiers by different code paths |
| **Trust** | PE/VC clients receiving inconsistent classifications cannot rely on the platform's output |
| **Debugging** | Inconsistent outputs are difficult to diagnose without knowing which code path executed |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/analytics/classification.py` | Modify | Designate as single source of truth; ensure all threshold values are defined here |
| `src/solstein/analytics/scoring.py` | Modify | Remove local threshold definitions; import from classification.py |
| `src/solstein/api/routers/scoring.py` | Modify | Remove hardcoded threshold values; import from classification.py |
| `tests/unit/test_classification_boundaries.py` | Add | Parametrized boundary tests |

## Architectural Requirements

*What the system must satisfy. No implementation instructions. No code. Only what — never how.*

- **REQ-1**: One module must be the designated single source of truth for all classification threshold values
- **REQ-2**: No other module may define numeric threshold literals for classification — they must import from the single source
- **REQ-3**: The threshold values must be documented with the business rationale: who defined them, when, and based on what calibration
- **REQ-4**: The boundary between each tier must be unambiguous — the use of `≥` vs `>` must be explicit and consistent across all tiers

## Acceptance Criteria

- [ ] Grep for the Lead threshold numeric value shows it defined in exactly one file
- [ ] All code paths that perform classification import thresholds from the same module
- [ ] The same input score produces the same tier output regardless of which function is called
- [ ] Each threshold value has a comment documenting its business meaning
- [ ] The boundary operator (inclusive vs exclusive) is documented for each tier transition

## Definition of Done

**Tests Required:**
- [ ] Parametrized test: for each tier boundary value, verify tier assignment above and below the threshold
- [ ] Test: invoke classification via multiple code paths with identical input; assert identical output
- [ ] Test: boundary values at exact threshold produce the documented tier (not the adjacent one)

**Documentation Required:**
- [ ] Each threshold value documented with business rationale and calibration source
- [ ] Tier boundary table showing: tier name, lower bound (inclusive/exclusive), upper bound (inclusive/exclusive)

**Code Review Gate:**
- [ ] Reviewer confirms no numeric threshold literal exists outside the designated source-of-truth module
- [ ] Reviewer confirms boundary operator consistency (no mix of `<` and `<=` for equivalent boundaries)

## Notes

This story has no dependencies and can begin immediately. It is the first story in the EPIC-003 critical path. STORY-010 (scoring deduplication) and STORY-011 (constant naming) both depend on this being resolved first — consolidating scoring logic before establishing the correct thresholds risks embedding the wrong values.
