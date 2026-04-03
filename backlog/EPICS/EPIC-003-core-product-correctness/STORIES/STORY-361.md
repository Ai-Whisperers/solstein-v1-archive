# STORY-361: Add Classification Threshold Consistency Regression Test

| Field | Value |
|---|---|
| **Status** | 🔴 READY |
| **Priority** | P3 |
| **Size** | S (half day) |
| **Epic** | EPIC-003 Core Product Correctness |
| **Created** | 2026-04-03 |
| **Updated** | 2026-04-03 (deep wiring audit — exact signatures and enum values verified) |
| **Risk** | Low |
| **Blocked By** | STORY-360 (boundary literals must be constants before this test can import them) |

---

## Exact Codebase Wiring (deep audit 2026-04-03)

### `classify_company()` (`src/solstein/analytics/scoring.py:144`)

```python
from solstein.analytics.constants import (
    LEAD_SCORE_THRESHOLD,    # 4.49
    PHOENIX_SCORE_THRESHOLD, # 7.0
)
from solstein.domain.models import CompanyClassification  # ← enums are here

def classify_company(score: float | None) -> CompanyClassification:
    if score is None:
        return CompanyClassification.SALT
    if score >= PHOENIX_SCORE_THRESHOLD:   # >= 7.0  → Phoenix
        return CompanyClassification.PHOENIX
    if score <= LEAD_SCORE_THRESHOLD:      # <= 4.49 → Lead
        return CompanyClassification.LEAD
    return CompanyClassification.SALT      # 4.5 – 6.99 → Salt
```

**Note**: `SALT_SCORE_THRESHOLD = 4.5` is defined in constants.py but NOT used by `classify_company()`. The function uses `LEAD_SCORE_THRESHOLD = 4.49` (not 4.5) for the Lead boundary. This is intentional — 4.5 is the conceptual minimum for Salt, but the Lead check uses `<= 4.49` as a floating-point-safe boundary.

### `CompanyClassification` Enum (`src/solstein/domain/models/__init__.py:31`)

```python
class CompanyClassification(StrEnum):
    PHOENIX = "Phoenix"
    SALT = "Salt"
    LEAD = "Lead"
```

### Threshold Values (from `constants.py`)

```python
PHOENIX_SCORE_THRESHOLD = 7.0    # >= this → Phoenix
LEAD_SCORE_THRESHOLD    = 4.49   # <= this → Lead
# Between 4.50 and 6.99 (inclusive) → Salt
```

### Boundary Truth Table

| Score | Expected | Reason |
|-------|----------|--------|
| `7.0` | Phoenix | `7.0 >= PHOENIX_SCORE_THRESHOLD` |
| `6.99` | Salt | below Phoenix, above Lead |
| `4.50` | Salt | above `LEAD_SCORE_THRESHOLD (4.49)` |
| `4.49` | Lead | `4.49 <= LEAD_SCORE_THRESHOLD` |
| `0.0` | Lead | below Lead threshold |
| `None` | Salt | explicit `None` guard |
| `10.0` | Phoenix | above Phoenix threshold |

---

## Problem Statement

Even after STORY-360 consolidates boundary literals, no test documents the intended scoring boundaries as an executable specification. A future PR changing `LEAD_SCORE_THRESHOLD` from 4.49 to 4.5 would silently shift thousands of company classifications with no test failure.

---

## Acceptance Criteria

- [ ] `tests/unit/test_classification_thresholds.py` exists
- [ ] Test imports `PHOENIX_SCORE_THRESHOLD` and `LEAD_SCORE_THRESHOLD` from `constants.py` — no hardcoded numeric literals in the test
- [ ] All 7 boundary cases in the truth table above are covered
- [ ] Test is parametrized (`@pytest.mark.parametrize`)
- [ ] Test passes with current implementation
- [ ] `ruff check` 0 errors

---

## Tasks

- [ ] Create `tests/unit/test_classification_thresholds.py`:
  ```python
  import pytest
  from solstein.analytics.constants import PHOENIX_SCORE_THRESHOLD, LEAD_SCORE_THRESHOLD
  from solstein.analytics.scoring import classify_company
  from solstein.domain.models import CompanyClassification

  @pytest.mark.parametrize("score,expected", [
      (PHOENIX_SCORE_THRESHOLD,           CompanyClassification.PHOENIX),
      (PHOENIX_SCORE_THRESHOLD - 0.01,    CompanyClassification.SALT),
      (LEAD_SCORE_THRESHOLD + 0.01,       CompanyClassification.SALT),
      (LEAD_SCORE_THRESHOLD,              CompanyClassification.LEAD),
      (0.0,                               CompanyClassification.LEAD),
      (None,                              CompanyClassification.SALT),
      (10.0,                              CompanyClassification.PHOENIX),
  ])
  def test_classify_company_boundaries(score, expected):
      assert classify_company(score) == expected
  ```
- [ ] Add to CI fast-test gate

## Key Files

| File | Line | Note |
|------|------|------|
| `src/solstein/analytics/scoring.py` | 144–152 | `classify_company()` — the function under test |
| `src/solstein/analytics/constants.py` | 6–8 | `PHOENIX_SCORE_THRESHOLD`, `LEAD_SCORE_THRESHOLD` |
| `src/solstein/domain/models/__init__.py` | 31–35 | `CompanyClassification` enum |
