# STORY-237: Reconcile Mirrored Drift and Publish Delta Changelog

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P1 - High |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-064 Markdown Integrity and Registry Correctness |
| **Created** | 2026-03-11 |
| **Risk** | Medium |

---

## Problem Statement

Mirrored files have started to drift, but reconciliation history and rationale are not documented.

## Acceptance Criteria

- [ ] Drift inventory is generated with file-by-file deltas.
- [ ] Reconciliation decisions are recorded with owner and timestamp.
- [ ] A changelog entry is published for each reconciled drift set.
- [ ] Drift-detection automation is added if mirrors remain; otherwise mirror retirement record is published.

## Definition of Done

- [ ] Known drifted files are reconciled and verified identical when mirrors remain.
- [ ] Drift report artifact is attached to PR/worklog.
