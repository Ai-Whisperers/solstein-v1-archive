# STORY-381: Fix `load_competitor_data.py` migration — set `data_source_type` on all `CompanyRecord` objects

**Epic**: EPIC-093 — Production Loader Synthetic Tagging
**Priority**: P0
**Size**: XS (< 1 hour)
**Status**: 🔴 READY

---

## Context

`src/solstein/migrations/load_competitor_data.py:53–80` builds `CompanyRecord` objects via
`_build_company_record()`. It sets `data_source="competitor_data.json"` (a free-text string in
the `data_source` column) but does NOT set `data_source_type`. If `CompanyRecord` has a
`data_source_type` column, it defaults to whatever the SQLAlchemy column default is — likely
`None` or `"unknown"`.

```python
return CompanyRecord(
    ...
    data_source="competitor_data.json",   # just a filename string
    # data_source_type NOT SET
)
```

Records inserted by this migration are indistinguishable from real data by the export gate,
which reads `data_source_type` (not `data_source`).

---

## Acceptance Criteria

- [ ] Read `src/solstein/infrastructure/models/` to confirm whether `CompanyRecord` has a
      `data_source_type` column (check `models/company.py` or `database_models.py`)
- [ ] **If the column exists**: add `data_source_type="real"` to every `CompanyRecord(...)` in
      `_build_company_record()` — the migration loads from `competitor_data.json` which is
      the production competitor dataset
- [ ] **If the column does not exist**: add it as a nullable `String(50)` column with default
      `"unknown"` in the appropriate model, create a migration for the schema change, then
      set `data_source_type="real"` in `_build_company_record()`
- [ ] The `data_source` free-text column (`"competitor_data.json"`) may be kept — it is a
      provenance string. `data_source_type` is a machine-readable enum-like tag for the gate.

---

## Technical Notes

**Read first**:
1. `src/solstein/infrastructure/database_models.py` or `src/solstein/infrastructure/models/company.py`
   — grep for `data_source_type` to see if the column exists on `CompanyRecord`
2. `src/solstein/migrations/load_competitor_data.py:35–80` — full `_build_company_record()` function

**Expected fix** (if column already exists):
```python
return CompanyRecord(
    ...
    data_source="competitor_data.json",
    data_source_type="real",    # ← add this line
    created_at=...,
    last_updated=...,
)
```

This is the smallest correct fix. Do not refactor `_build_company_record()` for any other reason.

---

## Definition of Done

- [ ] `_build_company_record()` sets `data_source_type` on every returned `CompanyRecord`
- [ ] If column was missing from `CompanyRecord`, an Alembic migration exists for the column add
- [ ] `pytest` 0 failures, `ruff check` 0 errors
