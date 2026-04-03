# STORY-367: Wire `SyntheticDataBlocker.ensure_safe()` into `export.py`

**Epic**: EPIC-090 — Synthetic Data Gate Enforcement
**Priority**: P0
**Size**: S (2–4 hours)
**Status**: 🔴 READY
**Blocks**: STORY-369

---

## Context

`SyntheticDataBlocker.ensure_safe()` at `src/solstein/data/synthetic_data_safety.py:284–322`
exists specifically to raise `SyntheticDataError` when synthetic data is detected. It was
written as the hard enforcement layer but has **zero callers** — it is dead code.

The current export flow in `src/solstein/api/routers/export.py` (~lines 41–45):
```python
gate = ReportReleaseGate(min_confidence=0.6, allow_synthetic=False)
gate_result = gate.evaluate(scored_companies)
export_metadata = build_export_metadata(companies, gate_result)
excel_exporter.create_dashboard(companies, output_path, metadata=export_metadata)
# export proceeds regardless of gate_result
```

---

## Acceptance Criteria

- [ ] `SyntheticDataBlocker.ensure_safe(companies)` is called in `export.py` before any file
      is written to disk or returned to the client
- [ ] If `ensure_safe()` raises `SyntheticDataError`, the endpoint returns HTTP 422 with a
      structured error body: `{"error": "export_blocked", "reason": <message>}`
- [ ] `allow_synthetic=False` configuration is passed to the blocker (matches gate config)
- [ ] New test: export endpoint with synthetic company → 422 response
- [ ] Existing export tests with `data_source_type="real"` companies → still pass

---

## Technical Notes

**Files to modify**:
- `src/solstein/api/routers/export.py` (~line 41–45)
- Possibly `src/solstein/data/synthetic_data_safety.py` if `ensure_safe()` signature needs
  adjustment to accept a list of Company objects (read the method signature first)

**Read before coding**:
1. Read `src/solstein/data/synthetic_data_safety.py:284–322` for `ensure_safe()` full signature
2. Read `src/solstein/api/routers/export.py` fully to find all export code paths
   (there may be JSON and Excel export paths — both must be guarded)

**Error handling pattern** (from `error-handling.md` rules):
```python
from solstein.data.synthetic_data_safety import SyntheticDataBlocker, SyntheticDataError
from solstein.api.errors import APIError

blocker = SyntheticDataBlocker(allow_synthetic=False)
try:
    blocker.ensure_safe(scored_companies)
except SyntheticDataError as e:
    raise APIError(code="EXPORT_BLOCKED", message=str(e), status_code=422) from e
```

---

## Definition of Done

- [ ] `ensure_safe()` called before every export path (Excel, JSON, PDF if present)
- [ ] `SyntheticDataError` caught and converted to HTTP 422 with structured body
- [ ] Test: synthetic company → 422
- [ ] Test: real company → 200 (existing tests not broken)
- [ ] `pytest` 0 failures, `ruff check` 0 errors
