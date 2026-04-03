# STORY-369: Contract tests — gate blocks synthetic/unknown, passes real

**Epic**: EPIC-090 — Synthetic Data Gate Enforcement
**Priority**: P0
**Size**: S (2–4 hours)
**Status**: 🔴 BLOCKED by STORY-366, STORY-367, STORY-368

---

## Context

STORY-366 through STORY-368 implement the gate enforcement. This story adds the regression
suite that proves the full contamination path is closed end-to-end. Without these tests,
a future change could silently re-open the path.

---

## Acceptance Criteria

- [ ] Test: `data_source_type="synthetic"` → export endpoint returns 422
- [ ] Test: `data_source_type="mixed"` → export endpoint returns 422
- [ ] Test: `data_source_type="unknown"` → export endpoint returns 422 (new — post STORY-366)
- [ ] Test: `data_source_type="real"` + sufficient confidence → export endpoint returns 200
- [ ] Test: `ReportReleaseGate.evaluate()` with "unknown" company → `gate_result.passed == False`
- [ ] Test: `SyntheticDataBlocker.ensure_safe([company_with_unknown])` → raises `SyntheticDataError`

---

## Technical Notes

**Test file location**: Create `tests/unit/test_synthetic_data_gate_enforcement.py`

**Pattern (from existing tests in `tests/unit/test_issue11_batch_enrichment_outcomes.py`)**:
- Use explicit, typed company objects (not mock factories) for these contract tests
- Test both the gate layer and the export endpoint layer independently
- For endpoint tests, use the FastAPI `TestClient` with an overridden dependency that returns
  a company list containing the synthetic record

**Do not use `tests/factories.py` for these tests** — the factories themselves are subject to
EPIC-091 remediation. Build minimal Company objects inline with explicit `data_source_type=...`.

```python
from solstein.domain.models import Company

def _make_company(data_source_type: str) -> Company:
    return Company(
        id="TEST-001",
        name="Test Co",
        data_source_type=data_source_type,
        # ... minimal required fields
    )
```

---

## Definition of Done

- [ ] `tests/unit/test_synthetic_data_gate_enforcement.py` exists with 6+ test cases
- [ ] All test cases pass in both pass and fail modes
- [ ] No production code changes — tests only
- [ ] `pytest` 0 failures, `ruff check` 0 errors
