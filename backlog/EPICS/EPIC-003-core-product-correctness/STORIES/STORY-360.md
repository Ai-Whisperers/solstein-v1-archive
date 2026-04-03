# STORY-360: Consolidate Classification Boundary Literals into Constants

| Field | Value |
|---|---|
| **Status** | 🔴 READY |
| **Priority** | P3 |
| **Size** | XS (2 hours) |
| **Epic** | EPIC-003 Core Product Correctness |
| **Created** | 2026-04-03 |
| **Updated** | 2026-04-03 (deep wiring audit — scope narrowed to 4 boundary literals) |
| **Risk** | Low |

---

## Exact Codebase Wiring (deep audit 2026-04-03)

### Current State: Core thresholds already use constants

**`src/solstein/analytics/constants.py`** (all relevant constants):

```python
PHOENIX_SCORE_THRESHOLD = 7.0   # High-growth companies (top ~20%)
SALT_SCORE_THRESHOLD = 4.5      # Stable companies (middle 60-70%)
LEAD_SCORE_THRESHOLD = 4.49     # Legacy/opportunity (bottom 15-20%)
```

**`src/solstein/analytics/scoring.py:144`** — `classify_company()` already uses these:

```python
def classify_company(score: float | None) -> CompanyClassification:
    if score is None:
        return CompanyClassification.SALT
    if score >= PHOENIX_SCORE_THRESHOLD:    # line 148
        return CompanyClassification.PHOENIX
    if score <= LEAD_SCORE_THRESHOLD:       # line 150
        return CompanyClassification.LEAD
    return CompanyClassification.SALT
```

### Remaining Literals: `classification.py:71`

**`src/solstein/analytics/classification.py` (lines ~66–75)**:

```python
# Score certainty: higher scores are more certain
# Scores near boundaries are less certain
score_certainty = 1.0
if 4.3 <= composite_score <= 4.7 or 6.8 <= composite_score <= 7.2:
    score_certainty = 0.7
```

**The 4 boundary literals**:
- `4.3` = `LEAD_SCORE_THRESHOLD - 0.19` (Lead/Salt boundary lower margin)
- `4.7` = `LEAD_SCORE_THRESHOLD + 0.21` (Lead/Salt boundary upper margin)
- `6.8` = `PHOENIX_SCORE_THRESHOLD - 0.2` (Phoenix boundary lower margin)
- `7.2` = `PHOENIX_SCORE_THRESHOLD + 0.2` (Phoenix boundary upper margin)

These represent "uncertainty zones" around the classification boundaries — scores near these ranges get lower confidence (0.7 vs 1.0). They should be named constants in `constants.py`.

**`CompanyClassification`** (`src/solstein/domain/models/__init__.py:31`):
```python
class CompanyClassification(StrEnum):
    PHOENIX = "Phoenix"
    SALT = "Salt"
    LEAD = "Lead"
```

---

## Problem Statement

The core classification thresholds (7.0, 4.5, 4.49) already use named constants. The remaining 4 literals (4.3, 4.7, 6.8, 7.2) in `classification.py:71` represent the confidence uncertainty zone around boundaries. If a threshold changes, someone must remember to update 6 places instead of 2.

---

## Acceptance Criteria

- [ ] `constants.py` gains 4 new constants for boundary uncertainty margins:
  ```python
  LEAD_BOUNDARY_LOW = 4.3      # Lower edge of Lead/Salt uncertainty zone
  LEAD_BOUNDARY_HIGH = 4.7     # Upper edge of Lead/Salt uncertainty zone
  PHOENIX_BOUNDARY_LOW = 6.8   # Lower edge of Phoenix uncertainty zone
  PHOENIX_BOUNDARY_HIGH = 7.2  # Upper edge of Phoenix uncertainty zone
  ```
- [ ] `classification.py:71` uses these constants instead of literals
- [ ] No change to computed values — this is pure name substitution
- [ ] `ruff check` 0 errors; all existing tests pass

---

## Tasks

- [ ] Add 4 constants to `src/solstein/analytics/constants.py`
- [ ] Import them in `src/solstein/analytics/classification.py`
- [ ] Replace literals at line 71

## Key Files

| File | Line | Note |
|------|------|------|
| `src/solstein/analytics/classification.py` | ~71 | 4 literals to replace |
| `src/solstein/analytics/constants.py` | — | Add 4 constants here |
| `src/solstein/analytics/scoring.py` | 26–29 | Already imports correctly — reference |
