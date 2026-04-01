# STORY-250: Reconcile Export Schema Contract with Workbook Output

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P1 - High |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-033 Data Completeness and Export Integrity |
| **Created** | 2026-03-31 |
| **Risk** | High |

---

## Problem Statement

The 2026-03-31 audit found that the exporter currently fails its own schema gate. Required Executive Summary fields for AI readiness and transformation readiness exist in the schema contract, but the workbook emitter does not produce those headers. This is not a theoretical mismatch: real export creation fails under the current behavior-oriented tests.

## Acceptance Criteria

- [ ] `ImprovedExcelExporter.create_dashboard()` produces a workbook that passes `validate_export()` for both full-data and sparse-data fixtures.
- [ ] AI readiness and transformation fields are either emitted on the correct sheet or the schema is updated through an explicit version bump and changelog entry.
- [ ] Worksheet headers and schema field definitions are derived from a single authoritative mapping or otherwise kept drift-proof.
- [ ] Tests verify live workbook artifacts and schema validation behavior, not just static field inventories.

## Tasks

- [ ] Reconcile the required Executive Summary fields with actual workbook output.
- [ ] Remove duplicated header definitions that can drift independently.
- [ ] Update schema versioning/changelog if the contract changes.
- [ ] Add regression coverage for generated workbook headers, metadata, and schema validation.

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This story was created from the 2026-03-31 audit after the export-schema "happy path" tests failed against the current exporter.

### Next Agent Action

- Treat this as a contract repair hotfix, not a feature request.
- Use live workbook generation as the truth source for verification.

### Required Working Style

- Keep the export contract explicit and versioned.
- Do not weaken the schema merely to make the failing tests pass unless the contract reduction is intentional and documented.

### Minimum Verification For Future Agents

- Run the export schema validation tests against real generated workbooks.
- Show the exporter passes its own schema gate before closing the story.
