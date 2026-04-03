# STORY-366: Extend export gate to treat `data_source_type="unknown"` as blocked

**Epic**: EPIC-090 — Synthetic Data Gate Enforcement
**Priority**: P0
**Size**: XS (< 1 hour)
**Status**: 🔴 READY
**Blocks**: STORY-369

---

## Context

`ReportReleaseGate.evaluate()` at `src/solstein/data/report_release_gate.py:168–178` currently
only blocks `"synthetic"` and `"mixed"` data source types:

```python
if str(data_source_type).lower() in {"synthetic", "mixed"}:
    reasons.append(GateReason(code="synthetic_data", ...))
```

Every factory, fixture, and seed script that omits `data_source_type` defaults to `"unknown"`
(from `domain/models.py:294`). This creates a blind spot: synthetic data produced by
`seed_db.py` and test factories is marked `"unknown"` and passes the gate unchecked.

---

## Acceptance Criteria

- [ ] `ReportReleaseGate` appends a `GateReason(code="unknown_data_source")` for any company
      where `data_source_type not in {"real", "verified"}`
- [ ] The blocked set is at minimum `{"synthetic", "mixed", "unknown"}` — or equivalently, an
      allowlist approach: only pass if `data_source_type in {"real", "verified"}`
- [ ] Existing tests that create companies with `data_source_type="real"` continue to pass
- [ ] New unit test confirms a company with `data_source_type="unknown"` is flagged

---

## Technical Notes

**File**: `src/solstein/data/report_release_gate.py`
**Target block** (lines 168–178):
```python
if not self.allow_synthetic:
    data_source_type = getattr(company, "data_source_type", "unknown")
    if str(data_source_type).lower() in {"synthetic", "mixed"}:
        reasons.append(
            GateReason(code="synthetic_data", message="Synthetic or mixed data detected", ...)
        )
```

Change the check to an allowlist:
```python
SAFE_SOURCE_TYPES = {"real", "verified"}
if not self.allow_synthetic:
    data_source_type = getattr(company, "data_source_type", "unknown")
    if str(data_source_type).lower() not in SAFE_SOURCE_TYPES:
        reasons.append(
            GateReason(code="unverified_data_source",
                       message=f"Unverified data_source_type: {data_source_type!r}", ...)
        )
```

This is a one-line logic inversion — no schema changes required.

---

## Definition of Done

- [ ] `report_release_gate.py` uses allowlist (`{"real", "verified"}`) instead of blocklist
- [ ] Unit test: company with `data_source_type="unknown"` → gate flags it
- [ ] Unit test: company with `data_source_type="real"` → gate passes it
- [ ] `pytest` 0 failures, `ruff check` 0 errors
