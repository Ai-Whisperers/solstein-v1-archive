# STORY-360: Consolidate Classification Thresholds into Single Source of Truth

| Field | Value |
|---|---|
| **Status** | 🟡 VERIFY |
| **Priority** | P3 |
| **Size** | XS (1 hour) |
| **Epic** | EPIC-003 Core Product Correctness |
| **Created** | 2026-04-03 |
| **Updated** | 2026-04-03 (revised after codebase audit — mostly done) |
| **Risk** | Low |

---

## Actual Codebase State (verified 2026-04-03)

**Constants are already defined:**
- `src/solstein/analytics/constants.py:7`: `PHOENIX_SCORE_THRESHOLD = 7.0`
- `src/solstein/analytics/constants.py:8`: `SALT_SCORE_THRESHOLD = 4.5`
- `src/solstein/analytics/constants.py:9`: `LEAD_SCORE_THRESHOLD = 4.49`

**Classification logic uses constants correctly:**
- `src/solstein/analytics/scoring.py:148`: `if score >= PHOENIX_SCORE_THRESHOLD:` — ✅ uses constant
- `src/solstein/analytics/scoring.py:150`: `if score <= LEAD_SCORE_THRESHOLD:` — ✅ uses constant
- `src/solstein/analytics/classification_service.py:45-47`: assigns constants to class attributes — ✅

**Remaining literal values:**
- `src/solstein/analytics/classification.py:9`: docstring says "4.5 - 7.49" — **7.49 is not a constant, it's a boundary description**
- `src/solstein/analytics/classification.py:71`: `if 4.3 <= composite_score <= 4.7 or 6.8 <= composite_score <= 7.2:` — **these uncertainty ranges are hardcoded literals**, not covered by existing constants

---

## Problem Statement

The core classification thresholds (7.0, 4.5, 4.49) are already imported from `constants.py`. However, the boundary uncertainty ranges (4.3, 4.7, 6.8, 7.2 in `classification.py:71`) are hardcoded literals. These are not business-critical but create a maintenance risk — if thresholds change, the uncertainty bands won't update automatically.

---

## Acceptance Criteria

- [ ] `src/solstein/analytics/constants.py` adds constants for boundary uncertainty bands:
  - `LEAD_SALT_BOUNDARY_LOW = 4.3`
  - `LEAD_SALT_BOUNDARY_HIGH = 4.7`
  - `SALT_PHOENIX_BOUNDARY_LOW = 6.8`
  - `SALT_PHOENIX_BOUNDARY_HIGH = 7.2`
- [ ] `src/solstein/analytics/classification.py:71` uses these constants instead of literals
- [ ] A grep CI check (or test) asserts no literal `7.0`, `4.5`, `4.49`, `4.3`, `4.7`, `6.8`, `7.2` appear outside `constants.py`
- [ ] `pytest` passes at 0 failures
- [ ] `ruff check` at 0 errors

---

## Tasks

- [ ] Read `src/solstein/analytics/classification.py:71` — confirm hardcoded boundary literals
- [ ] Add 4 new boundary constants to `src/solstein/analytics/constants.py`
- [ ] Replace literals in `classification.py:71` with the new constants
- [ ] Add CI assertion or test to catch future literal threshold usage

## Key Files

| File | Line | Note |
|------|------|------|
| `src/solstein/analytics/constants.py` | 7–9 | Core thresholds already here — add boundary constants |
| `src/solstein/analytics/classification.py` | 71 | `4.3, 4.7, 6.8, 7.2` literals — replace with constants |
