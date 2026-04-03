# STORY-360: Consolidate Classification Thresholds into Single Source of Truth

| Field | Value |
|---|---|
| **Status** | 🔴 READY |
| **Priority** | P3 |
| **Size** | S (half day) |
| **Epic** | EPIC-003 Core Product Correctness |
| **Created** | 2026-04-03 |
| **Risk** | Low |

---

## Problem Statement

Classification thresholds (Phoenix ≥7.0, Salt 4.5–7.49, Lead <4.5) are referenced in three files: `constants.py`, `classification.py` docstring, and `classification_service.py`. While currently consistent, there is no guard preventing them from diverging. Adding a new threshold file or copying the values creates an invisible maintenance trap.

## Acceptance Criteria

- [ ] `src/solstein/analytics/constants.py` is the single source of truth for all threshold values
- [ ] All other files import from `constants.py` — no literal numeric thresholds in `scoring.py`, `classification_service.py`, or `domain/value_objects.py`
- [ ] A grep CI check asserts no hardcoded `7.0`, `4.5`, or `4.49` outside `constants.py`
- [ ] `pytest` passes at 0 failures

## Tasks

- [ ] Grep for literal `7.0`, `4.5`, `4.49` in `src/` and `tests/`
- [ ] Replace any found literals with imports from `constants.py`
- [ ] Add `scripts/ci/check_threshold_literals.py` that fails if literals found outside constants.py
