# STORY-126: Add Export Schema Validation

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | Critical |
| **Epic** | EPIC-033: Data Completeness & Export Integrity |
| **Created** | 2026-03-01 |
| **Dependencies** | STORY-125 |

## The Audit Verdict

> No validation exists to ensure exported fields match domain model. Silent drops go undetected.

## Problem Statement

The export pipeline has no contract. It can drop fields, rename fields, or change data types and nothing fails. The tests pass because they test what the export currently produces, not what it should produce. A field can disappear for months and the only way to notice is a user complaining that data they saw in the UI isn't in their Excel. The fix is a schema validation layer that asserts the export contains expected fields with expected types.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Data Integrity** | No detection of field drops |
| **Reliability** | Schema drift unnoticed |
| **Testability** | Tests validate current behavior, not correct behavior |

## Affected Files

| File | Issue |
|------|-------|
| `src/solstein/exporters/excel.py` | No schema validation |
| `tests/` | Tests don't catch missing fields |

## Architectural Requirements

- Export schema defined as Pydantic model: ExportSchema with fields, types, required/optional
- Validation runs after export generation: exported data must match schema
- Schema mismatch raises ValidationError with specific field names
- Schema versioned — changes to export structure require explicit schema version bump
- CI gate: export schema validation runs on every build
- Schema documentation auto-generated from Pydantic model

## Acceptance Criteria

- [ ] ExportSchema Pydantic model exists
- [ ] Validation runs on every export and catches missing fields
- [ ] Schema version bump required for structural changes
- [ ] CI fails if export doesn't match schema
- [ ] Schema documentation auto-generated

## Definition of Done

- **Tests Required**: Deliberately remove a field from export, verify CI fails
- **Documentation Required**: Schema documentation
- **Code Review Gate**: Reviewer verifies schema covers all 20 previously-dropped fields

## Notes

Prevent future silent field drops.
