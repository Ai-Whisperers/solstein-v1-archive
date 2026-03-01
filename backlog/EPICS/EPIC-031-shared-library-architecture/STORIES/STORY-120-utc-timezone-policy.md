# STORY-120: Enforce UTC Timezone Policy Across All Modules

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Epic** | EPIC-031: Shared Library & Architecture |
| **Created** | 2026-03-01 |
| **Dependencies** | None |

## The Audit Verdict

> Mix of naive and aware datetimes across modules. `unified_loader.py:226-233` has hardcoded date `'2026-02-23'`. No centralized timezone policy documented or enforced.

## Problem Statement

Naive datetimes — those without timezone information — are a reliability hazard in a platform that scrapes data from sources in multiple timezones (SEC EDGAR in US/Eastern, Companies House in UK/London, GitHub in UTC). When naive datetimes from different timezone contexts are compared or stored together, the comparison is meaningless. A naive datetime from a UK source and a naive datetime from a US source may represent times that are 5 hours apart, but Python's comparison treats them as if they're in the same timezone. The result is incorrect ordering, incorrect freshness calculations, and incorrect conflict resolution in `ConflictResolutionEngine` (which uses `newer_timestamp` as a resolution strategy). The fix is simple: all datetimes in the system are UTC-aware. No exceptions.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Reliability** | Incorrect timestamp comparisons cause wrong conflict resolution |
| **Data Integrity** | Freshness calculations wrong across timezone boundaries |
| **Maintainability** | Every new datetime operation requires timezone archaeology |

## Affected Files

| File | Issue |
|------|-------|
| `src/solstein/data/unified_loader.py` | Hardcoded date, naive datetimes |
| `src/solstein/infrastructure/conflict_resolution.py` | Uses timestamps for conflict resolution |
| All adapter files | May create naive datetimes |

## Architectural Requirements

- All datetime objects throughout the codebase are timezone-aware UTC (`datetime.now(timezone.utc)` or `datetime.fromisoformat(...).replace(tzinfo=timezone.utc)`)
- No `datetime.now()` without `tz=timezone.utc` argument — enforced by ruff rule `DTZ005`
- No `datetime.utcnow()` — deprecated, replaced by `datetime.now(timezone.utc)` — enforced by ruff rule `DTZ003`
- External source datetimes converted to UTC immediately upon ingestion (at adapter boundary)
- PostgreSQL `TIMESTAMP WITH TIME ZONE` used for all datetime columns (verify existing columns — add migration if any are `TIMESTAMP WITHOUT TIME ZONE`)
- A `shared/datetime_utils.py` module provides: `utc_now()`, `to_utc(dt)`, `parse_iso_to_utc(s)` as canonical utilities
- Ruff datetime rules (`DTZ001`–`DTZ007`) enabled in `pyproject.toml`

## Acceptance Criteria

- [ ] Ruff datetime rules pass on entire codebase with zero violations
- [ ] `grep -r "datetime.now()" src/` returns zero results (must use `datetime.now(timezone.utc)`)
- [ ] `grep -r "datetime.utcnow()" src/` returns zero results
- [ ] All PostgreSQL datetime columns use `TIMESTAMP WITH TIME ZONE`
- [ ] `shared/datetime_utils.py` module exists and is used at all ingestion boundaries

## Definition of Done

- **Tests Required**: CI ruff check passes with datetime rules enabled
- **Documentation Required**: Timezone policy documentation
- **Code Review Gate**: Reviewer runs `grep -r "datetime.now()" src/` — must return empty

## Notes

UTC everywhere. No exceptions.
