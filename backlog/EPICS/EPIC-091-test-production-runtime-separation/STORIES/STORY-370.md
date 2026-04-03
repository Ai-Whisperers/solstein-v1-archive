# STORY-370: Fix `seed_db.py` — tag all seeded records as `data_source_type="synthetic"`

**Epic**: EPIC-091 — Test/Production Runtime Separation
**Priority**: P0
**Size**: XS (< 30 minutes)
**Status**: 🔴 READY

---

## Context

`scripts/seed_db.py` uses `Faker()` to generate company data and writes directly to the
production database via `CompanyRepository` + `get_async_session()`. The `generate_company()`
function (lines 51–90) never sets `data_source_type`, so records default to `"unknown"`.

With EPIC-090 complete, the export gate will block `"unknown"` records. But the root cause
must also be fixed: seeded records should be **explicitly tagged** at the point of creation,
not rely on a gate to catch them downstream.

---

## Acceptance Criteria

- [ ] Every `Company` object created by `generate_company()` in `seed_db.py` has
      `data_source_type="synthetic"` set explicitly
- [ ] No other changes to `seed_db.py` — only add the field assignment
- [ ] If `seed_db.py` is run, all written records are queryable with
      `data_source_type == "synthetic"`

---

## Technical Notes

**File**: `scripts/seed_db.py:51–90`

The fix is a one-line addition inside `generate_company()`. Locate the `Company(...)` constructor
call or the point where the company object is returned, and add `data_source_type="synthetic"`.

**Read first**: Confirm whether `generate_company()` creates a `Company` domain model or a
`CompanyRecord` SQLAlchemy model — the field name is the same on both but verify which is
used before adding the assignment.

Contrast with `scripts/generate_synthetic_companies.py:320` which already does this correctly:
```python
"data_source_type": "synthetic",
```

---

## Definition of Done

- [ ] `generate_company()` sets `data_source_type="synthetic"` explicitly
- [ ] `pytest` 0 failures (no prod code touched), `ruff check` 0 errors
