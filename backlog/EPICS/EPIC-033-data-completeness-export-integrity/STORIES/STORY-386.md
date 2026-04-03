# STORY-386: Fix `load_competitor_data.py` — remove `get_database_url(test=True)` from production migration

| Field | Value |
|-------|-------|
| **Epic** | EPIC-033 — Data Completeness & Export Integrity |
| **Priority** | P0 |
| **Size** | XS |
| **Status** | 🔴 READY |
| **Created** | 2026-04-03 |
| **Source** | Third-pass contamination audit (same file as STORY-381) |

## Problem

`src/solstein/migrations/load_competitor_data.py:179`:

```python
db_url = settings.get_database_url(test=True) or "postgresql+asyncpg://solstein:solstein@localhost:5432/solstein"
```

This production migration script unconditionally requests the **test database URL** via
`test=True`. Any operator running this migration believes they are loading competitor data
into the production database. Depending on how `get_database_url(test=True)` is implemented:

- If it returns a test/SQLite URL: data is inserted into the test database and silently lost
- If it returns `None`: the fallback targets `localhost:5432` — a local dev database, not prod
- Either way: no data reaches the actual production database

The script is named `load_competitor_data.py` and lives in `migrations/` — it is clearly
intended as a data loading operation on the real database. The `test=True` argument is
a latent bug that has existed without being caught because the script likely runs infrequently.

**This is the same file addressed by STORY-381** (which fixes missing `data_source_type`
on the `CompanyRecord` inserts). Both fixes should be applied together.

## Fix

```python
# Before (line 179)
db_url = settings.get_database_url(test=True) or "postgresql+asyncpg://..."

# After
db_url = settings.get_database_url() or raise ValueError(
    "DATABASE_URL not configured. Set the DATABASE_URL environment variable before running migrations."
)
```

1. Remove `test=True` argument.
2. Replace the hardcoded localhost fallback with an explicit error — a migration with no
   configured target database should fail loudly, not silently target localhost.
3. Add a pre-flight check that logs the resolved URL (masked for credentials) and prompts
   for confirmation before inserting if running interactively.

## Acceptance Criteria

- [ ] `get_database_url()` called without `test=True`
- [ ] No hardcoded localhost fallback URL
- [ ] Script raises a clear error if `DATABASE_URL` is not set
- [ ] Script logs the target database URL (masked) before connecting

## Files

- `src/solstein/migrations/load_competitor_data.py` — line 179
- Coordinate with STORY-381 (same file) — both fixes should land in the same PR

## Notes

Verify that `settings.get_database_url()` (without `test`) correctly resolves to the
production database URL in the deployment environment. If `get_database_url` has no
non-test path, that is a separate bug to fix in the settings module.
