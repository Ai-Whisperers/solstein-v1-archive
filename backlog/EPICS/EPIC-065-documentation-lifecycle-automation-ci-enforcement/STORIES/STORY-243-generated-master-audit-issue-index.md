# STORY-243: Generate Master Audit Issue Index and Keep It Current

| Field | Value |
|---|---|
| **Status** | 🟡 In Progress |
| **Priority** | P1 - High |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-065 Documentation Lifecycle Automation and CI Enforcement |
| **Created** | 2026-03-26 |
| **Risk** | High |

---

## Problem Statement

The master audit is the historical source of truth, but it is expensive to re-read and unsafe to manually duplicate. The repo needs a generated issue index that preserves the source audit while making the full inventory cheaply queryable.

## Acceptance Criteria

- [x] A generated markdown issue index exists under `docs/audit/generated/`.
- [x] A generated JSON issue index exists for machine consumers.
- [x] The generator deduplicates repeated issue table rows by issue identifier.
- [x] The generated artifact records the source line count and declared tracker totals.
- [ ] The generated artifact is cross-linked from future fix-verification audits.

## Definition of Done

- [x] The master audit remains unedited by the generator.
- [x] `docs-generated-check` fails when the committed index is stale.
- [ ] Fix-verification audits explicitly reconcile against the generated issue index.
