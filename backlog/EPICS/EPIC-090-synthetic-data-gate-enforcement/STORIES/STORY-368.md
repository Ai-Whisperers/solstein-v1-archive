# STORY-368: Add `if not gate_result.passed: raise` guard in `export.py`

**Epic**: EPIC-090 — Synthetic Data Gate Enforcement
**Priority**: P0
**Size**: XS (< 1 hour)
**Status**: 🔴 READY
**Blocks**: STORY-369

---

## Context

`ReportReleaseGate.evaluate()` returns a result object with a `passed` boolean field.
Currently in `src/solstein/api/routers/export.py`, the result is computed but the `passed`
flag is never checked — export proceeds unconditionally:

```python
gate_result = gate.evaluate(scored_companies)
export_metadata = build_export_metadata(companies, gate_result)
excel_exporter.create_dashboard(...)  # always runs
```

This must be an explicit guard, separate from STORY-367's `SyntheticDataBlocker` call.
The two checks are complementary: the blocker is a hard type check; the gate result
may capture other quality failures (confidence thresholds, provenance, etc.) that
the blocker does not catch.

---

## Acceptance Criteria

- [ ] After `gate_result = gate.evaluate(scored_companies)`, there is an explicit check:
      `if not gate_result.passed: raise` (or equivalent HTTP error)
- [ ] The raised error includes the gate reasons so callers can diagnose the block
- [ ] HTTP response for a blocked export is 422 with body containing `gate_result.reasons`
- [ ] All export paths (Excel, JSON) have the guard — not just one

---

## Technical Notes

**File**: `src/solstein/api/routers/export.py`

**Read first**: confirm `gate_result.passed` is a bool field and `gate_result.reasons` is
iterable (verify the `GateResult` model in `report_release_gate.py`).

**Pattern**:
```python
gate_result = gate.evaluate(scored_companies)
if not gate_result.passed:
    reasons = [r.model_dump() for r in gate_result.reasons]
    raise APIError(
        code="EXPORT_QUALITY_GATE_FAILED",
        message="Export blocked by quality gate",
        status_code=422,
        details={"reasons": reasons},
    )
export_metadata = build_export_metadata(companies, gate_result)
# ... export proceeds only here
```

This story is a one-function change — do not restructure export.py, just add the guard.

---

## Definition of Done

- [ ] Guard added after every `gate.evaluate()` call in `export.py`
- [ ] Test: company that fails confidence threshold → export returns 422 with reason list
- [ ] `pytest` 0 failures, `ruff check` 0 errors
