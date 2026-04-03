# STORY-361: Add Classification Threshold Consistency Regression Test

| Field | Value |
|---|---|
| **Status** | 🔴 READY |
| **Priority** | P3 |
| **Size** | S (half day) |
| **Epic** | EPIC-003 Core Product Correctness |
| **Created** | 2026-04-03 |
| **Risk** | Low |
| **Blocked By** | STORY-360 |

---

## Problem Statement

Even after STORY-360 consolidates thresholds, there is no test that would catch a future PR that changes a threshold in one place but not another, or that documents the intended scoring boundaries with an executable specification.

## Acceptance Criteria

- [ ] `tests/unit/test_classification_thresholds.py` asserts:
  - Score 7.0 → Phoenix
  - Score 6.99 → Salt
  - Score 4.5 → Salt
  - Score 4.49 → Lead
  - Score 0.0 → Lead
  - Score `None` → Salt (default)
- [ ] Test imports thresholds only from `constants.py` (no literals in test)
- [ ] Test passes with current implementation

## Tasks

- [ ] Write `tests/unit/test_classification_thresholds.py` using `classify_company()` from `scoring.py`
- [ ] Parametrize with boundary and interior values for all three tiers
- [ ] Add to CI fast-test gate
