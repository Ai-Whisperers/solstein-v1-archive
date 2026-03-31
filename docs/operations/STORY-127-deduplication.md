# STORY-127: Deduplicate profit_margin and employee Fields

## Migration Summary

**Date**: 2026-03-27
**Epic**: EPIC-033 (Data Completeness & Export Integrity)
**Status**: Implemented

## What Changed

### Canonical Source Designation

`FinancialMetric` is now the **single source of truth** for:

- `profit_margin` (float)
- `employees` / `employee_count` (int)

### Company Model Changes

**Removed fields** (were duplicated across Company and FinancialMetric):

- `Company.profit_margin` (was declared twice at lines 221 and 418)
- `Company.employees` (top-level, at line 219)
- `Company.employee_count` (at line 430)

**Added computed properties** (read-only, delegate to `FinancialMetric`):

- `Company.profit_margin` -> `self.financials.profit_margin`
- `Company.employees` -> `self.financials.employees`
- `Company.employee_count` -> `self.financials.employees`

**Added before-validator**: Routes constructor kwargs (`profit_margin`, `employees`, `employee_count`) to the `financials` sub-model, preserving backward compatibility for object construction.

### Behavioral Changes

1. `Company.profit_margin = x` now raises `AttributeError` (was silently accepted)
2. `Company.employees = x` now raises `AttributeError` (was silently accepted)
3. `Company.employee_count = x` now raises `AttributeError` (was silently accepted)
4. `sync_financial_fields` no longer syncs `profit_margin` or `employees` bidirectionally

### Write Path Updates

All code that writes financial metrics must write to `FinancialMetric` directly:

```python
# Before (WRONG - will now raise)
company.profit_margin = 0.25
company.employees = 500

# After (CORRECT)
company.financials.profit_margin = 0.25
company.financials.employees = 500
```

### Files Modified

| File | Change |
|------|--------|
| `src/solstein/domain/models.py` | Removed duplicate fields, added computed_field properties, before-validator for routing |
| `src/solstein/data/web_research_pipeline.py` | Updated employee write path to go through financials |
| `tests/unit/test_story127_deduplicate_fields.py` | 29 new unit tests |
| `docs/migrations/STORY-127-deduplication.md` | This document |

### Write Path Audit

All write paths were audited. Results:

| File | Write Target | Status |
|------|-------------|--------|
| `data/unified/merger.py` | `FinancialMetric.employees`, `FinancialMetric.profit_margin` | Already correct |
| `data/unified/sec_edgar_helpers.py` | `company.financials.employees`, `company.financials.profit_margin` | Already correct |
| `data/web_research_pipeline.py` | `result.employees` | **Fixed** -> `result.financials.employees` |
| `validation/data_remediation.py` | `company.financials.employees` | Already correct |

### Database Schema

The database model `CompanyRecord` has `profit_margin_pct` and `employee_count` columns. These remain in the database schema for now (two-phase deprecation approach). The ORM layer (`infrastructure/models/company.py`) reads from these columns and maps to the domain model through the constructor, which routes to FinancialMetric via the before-validator.

**Phase 2 (future)**: Remove `profit_margin_pct` and `employee_count` columns from `CompanyRecord` after all consumers have been updated to read from the FinancialMetric path.

## Data Reconciliation

No data migration is required. The `FinancialMetric` sub-model already holds the values for `profit_margin` and `employees`. The `sync_financial_fields` model validator was previously keeping both copies in sync. Now the Company-level copies are gone and reads go directly to the canonical source.

## Backward Compatibility

- **Reads**: `company.profit_margin`, `company.employees`, `company.employee_count` all continue to work as read properties
- **Constructor**: `Company(profit_margin=0.15, employees=100)` continues to work via the before-validator
- **Serialization**: `model_dump()` includes all three computed fields
- **Deserialization**: `Company(**dump)` works because the before-validator routes the fields
- **Writes**: Direct assignment to Company-level fields now raises `AttributeError`. All writes must go through `company.financials.profit_margin` or `company.financials.employees`.
