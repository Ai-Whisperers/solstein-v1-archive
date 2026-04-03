# STORY-384: Add `data_source_type` column to `CompanyRecord` DB schema + Alembic migration

| Field | Value |
|-------|-------|
| **Epic** | EPIC-033 — Data Completeness & Export Integrity |
| **Priority** | P0 |
| **Size** | S |
| **Status** | 🔴 READY |
| **Created** | 2026-04-03 |
| **Source** | Third-pass contamination audit |

## Problem

The domain `Company` model has a `data_source_type: str` field that drives export gates, quality
gates, and provenance tracking. The SQLAlchemy `CompanyRecord` — the persistence layer — does
**not have a corresponding column**:

```python
# src/solstein/infrastructure/models/company.py:77
data_source = Column(String(100), nullable=True)   # free-text filename/string only
# NO data_source_type column exists
```

**Consequence**: The gating field is never persisted to the database. When a `CompanyRecord` is
loaded and converted back to a domain `Company`, the converter at
`src/solstein/data/converters/company.py:341–344` falls back to `"real"` for the missing field:

```python
data_source_type=raw_data.get(
    "data_source_type",
    "synthetic" if raw_data.get("is_synthetic", False) else "real",
),
```

Every company loaded from the database gets `data_source_type="real"` and passes all gates
unconditionally. Synthetic, competitor, and migration-loaded records that were once correctly
tagged lose their provenance type on the round-trip through the database.

## Fix

1. Add `data_source_type = Column(String(50), nullable=False, server_default="unknown")` to
   `CompanyRecord` in `src/solstein/infrastructure/models/company.py`.
2. Create an Alembic migration that:
   - Adds the column with `server_default="unknown"`
   - Backfills existing rows using `data_source = "competitor_data.json"` → `"competitor"`,
     seed-DB records → `"synthetic"`, else `"unknown"`
3. Update `to_dict()` on `CompanyRecord` (line 152 area) to include `data_source_type`.
4. Update `convert_to_domain_company()` at `converters/company.py:341–344` to read from the
   now-populated field (see STORY-385 for the companion converter fix).
5. Update any `CompanyRecord` factory or builder that creates records without `data_source_type`.

## Acceptance Criteria

- [ ] `CompanyRecord` has `data_source_type` column (String, non-null, default `"unknown"`)
- [ ] Alembic migration applies cleanly on an existing database
- [ ] `to_dict()` includes `data_source_type` in the serialised output
- [ ] A `CompanyRecord` saved with `data_source_type="synthetic"` round-trips back as `"synthetic"`
- [ ] A `CompanyRecord` with no explicit type gets `data_source_type="unknown"` (not `"real"`)
- [ ] Existing gate tests still pass after the schema change

## Files

- `src/solstein/infrastructure/models/company.py` — add column (~line 77)
- `alembic/versions/` — new migration file
- `src/solstein/data/converters/company.py` — read new field (companion to STORY-385)
- `tests/factories/` or `tests/factories.py` — update `CompanyRecord` factory

## Notes

- **Blocks STORY-366**: The gate's `"unknown"` allowlist change is only meaningful once DB
  records carry a real `data_source_type` value.
- **Pairs with STORY-385**: The converter fix should land in the same PR or immediately after.
- The `server_default="unknown"` ensures existing rows without provenance are treated as
  unverified (blocked by gate) rather than trusted.
