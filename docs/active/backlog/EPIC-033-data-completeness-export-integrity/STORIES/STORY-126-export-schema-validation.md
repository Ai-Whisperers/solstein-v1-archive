# STORY-126: Add Export Schema Validation

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | Critical |
| **Epic** | EPIC-033: Data Completeness & Export Integrity |
| **Created** | 2026-03-01 |
| **Dependencies** | STORY-125 (Restore 20 Dropped Fields — schema must validate the complete, correct export) |

---

## The Audit Verdict

> "No validation exists to ensure exported fields match domain model. Silent drops go undetected."

---

## Problem Statement

The export pipeline has no contract. It can drop fields, rename fields, or change data types and nothing fails. The tests pass because they test what the export currently produces, not what it should produce. A field can disappear for months and the only way to notice is a user complaining that data they saw in the UI isn't in their Excel. The fix is a schema validation layer that asserts the export contains expected fields with expected types.

This is a systemic testing philosophy failure, not just a missing feature. When tests are written to describe current behavior rather than specify required behavior, they become a liability — they provide false confidence while actively concealing regressions. The export test suite currently does exactly this. It will pass whether the export contains 20 fields or 200 fields, because it never asserts which fields must be present. It is, in the most literal sense, testing the wrong thing.

The schema validation layer is the mechanism that converts the test suite from descriptive to prescriptive. Once it exists, a field cannot be silently dropped without a test failing. The CI pipeline becomes a contract enforcer rather than a rubber stamp. This is the structural fix that makes the 20-field restoration in STORY-125 durable — without it, the next developer who touches the export can silently drop fields again, and nobody will know until an analyst complains.

---

## Impact

| Dimension | Impact |
|-----------|--------|
| **Data Integrity** | No automated detection of field drops; silent data loss can persist indefinitely |
| **Reliability** | Schema drift between domain model and export goes unnoticed until user-reported |
| **Testability** | Current tests validate current (broken) behavior, not correct behavior; false confidence |
| **Developer Experience** | No feedback mechanism when export changes break the field contract; regressions are invisible |

---

## Affected Files

| File | Issue |
|------|-------|
| `src/solstein/exporters/excel.py` | No schema validation on export output; fields can be dropped without detection |
| `tests/` | Export tests describe current behavior rather than specify required behavior; no field presence assertions |

---

## Architectural Requirements

### ExportSchema Definition

- An `ExportSchema` Pydantic model must be defined that formally specifies the export contract
- The schema must enumerate every field that must appear in the export, organized by sheet
- Each field entry must specify: field name, column header label, data type, required/optional status, and target sheet
- The schema must be the single authoritative source of truth for export structure — not comments, not documentation, not tribal knowledge
- Schema definition must live in a dedicated module, not embedded in the export implementation

### Validation Mechanism

- Validation must run automatically after every export generation, before the file is returned to the caller
- Validation must compare the actual exported content against the `ExportSchema` definition
- A schema mismatch — missing field, wrong sheet, wrong data type — must raise a `ValidationError` that includes the specific field name(s) that failed
- Validation must check both presence (field exists) and placement (field is on the correct sheet)
- Optional fields that are absent due to null data must not trigger validation failures — the distinction between "field not exported" and "field has no data" must be explicit in the schema

### Schema Versioning

- The `ExportSchema` must carry an explicit version identifier (e.g., `EXPORT_SCHEMA_VERSION = "1.0"`)
- Any structural change to the export — adding a field, removing a field, moving a field to a different sheet, renaming a column header — must require an explicit version bump
- The version bump must be a deliberate act, not an automatic increment; it signals that a human has reviewed and approved the structural change
- The exported Excel file must embed the schema version in a metadata cell or sheet, enabling downstream consumers to detect version changes

### CI Integration

- Export schema validation must run as part of the CI pipeline on every build
- The CI gate must fail if the export output does not match the schema
- The CI gate must also fail if the schema version has changed without a corresponding update to the schema changelog
- A schema changelog file must be maintained alongside the schema definition, recording what changed in each version

### Documentation Generation

- Schema documentation must be auto-generated from the `ExportSchema` Pydantic model definition
- Generated documentation must list every field, its sheet, its column header, its type, and its required/optional status
- Documentation generation must run as part of the build process; stale documentation must cause a CI warning
- The generated documentation must be committed to `docs/export-schema.md` and kept in sync with the schema definition

---

## Acceptance Criteria

- [ ] `ExportSchema` Pydantic model exists in a dedicated module with all exported fields enumerated
- [ ] Schema validation runs automatically after every export generation
- [ ] Validation raises `ValidationError` with specific field names when fields are missing or misplaced
- [ ] Schema carries an explicit version identifier
- [ ] Structural changes to the export require an explicit schema version bump
- [ ] Exported Excel file embeds the schema version in metadata
- [ ] CI pipeline fails if export output does not match schema
- [ ] CI pipeline fails if schema version changes without a changelog entry
- [ ] Schema documentation is auto-generated from the Pydantic model
- [ ] Generated documentation is committed to `docs/export-schema.md`
- [ ] Schema covers all 20 fields restored in STORY-125
- [ ] Deliberately removing a field from the export causes CI to fail (verified by test)

---

## Definition of Done

- **Tests Required**: Negative test — deliberately remove one of the 20 restored fields from the export, run CI, verify it fails with a `ValidationError` naming the missing field. Positive test — complete export with all fields passes validation without error.
- **Documentation Required**: `docs/export-schema.md` auto-generated and committed. Schema changelog initialized with version 1.0 entry.
- **Code Review Gate**: Reviewer verifies the schema explicitly covers all 20 previously-dropped fields from STORY-125. Reviewer verifies the negative test actually fails (not just that it exists).

---

## Notes

**On the validation timing:** Validation runs after export generation, not during. This is intentional — the export generates the file, then validation inspects it. This separation keeps the export logic clean and makes the validation independently testable.

**On optional vs. required fields:** The schema must distinguish between fields that must always be present (e.g., `company_name`, `revenue`) and fields that are present only when data exists (e.g., `parent_company`, `notes`). A company with no parent company should not fail validation — but a company with a known parent company that is not exported should. The schema must encode this distinction explicitly.

**On the "tests describe behavior" problem:** The existing export tests are not wrong — they are just testing the wrong contract. They should be updated to assert against the `ExportSchema` rather than against hardcoded expected values. This is a test philosophy change, not just a test addition. The code review gate should verify that at least the critical export tests have been updated to use schema-based assertions.

**On schema versioning philosophy:** The version bump requirement is a forcing function for deliberate change management. It is not bureaucracy — it is the mechanism that ensures no structural change to the export happens accidentally. The version bump must be a human decision, not an automated one.
