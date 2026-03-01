# STORY-127: Deduplicate profit_margin and employee Fields

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | Critical |
| **Epic** | EPIC-033: Data Completeness & Export Integrity |
| **Created** | 2026-03-01 |
| **Dependencies** | None |

## The Audit Verdict

> profit_margin exists in BOTH FinancialMetric AND Company top-level. employees (FinancialMetric) vs employee_count (Company) — no synchronization.

## Problem Statement

The same data lives in two places. When profit_margin is updated in FinancialMetric but not in Company, the Excel export (which pulls from both) shows different values for the same metric. This isn't just duplication; it's a consistency hazard. The platform has no single source of truth for basic financial metrics. The fix is to pick one canonical location and derive the other, or eliminate the duplication entirely.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Data Integrity** | Same metric can have different values |
| **Reliability** | Analysts see inconsistent data |
| **Maintainability** | Updates must touch two places |

## Affected Files

| File | Issue |
|------|-------|
| `src/solstein/domain/models.py` | Duplicated fields |
| `src/solstein/infrastructure/database_models.py` | Duplicated columns |
| `src/solstein/exporters/excel.py` | Pulls from both sources |

## Architectural Requirements

- Canonical source identified: FinancialMetric is the source of truth for profit_margin, employees
- Company model profit_margin becomes a @property that reads from FinancialMetric
- Company model employee_count becomes a @property that reads from FinancialMetric
- Database migration to remove duplicated columns (or mark deprecated)
- All writes go to FinancialMetric; Company properties are read-only
- Export updated to pull from canonical source only
- Data reconciliation: verify existing data consistency, flag discrepancies

## Acceptance Criteria

- [ ] Company.profit_margin is a property reading from FinancialMetric
- [ ] Company.employee_count is a property reading from FinancialMetric
- [ ] No duplicated columns in database (or marked deprecated)
- [ ] Export pulls from single source
- [ ] Data reconciliation report shows any existing discrepancies

## Definition of Done

- **Tests Required**: Unit tests for property behavior
- **Documentation Required**: Data model documentation update
- **Code Review Gate**: Reviewer verifies no write paths to duplicated fields

## Notes

Single source of truth for financial metrics.
