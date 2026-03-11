# STORY-231: Resolve Mirrored Backlog Trees with One-Way Sync or Migration

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P1 - High |
| **Size** | L (1 week) |
| **Epic** | EPIC-063 Documentation Topology and Source-of-Truth Governance |
| **Created** | 2026-03-11 |
| **Risk** | High |

---

## Problem Statement

`docs/active/backlog` and `backlog/EPICS` contain mirrored markdown content with proven drift.

## Acceptance Criteria

- [ ] Canonical tree is selected and documented.
- [ ] Non-canonical tree strategy is defined (generated mirror, one-way sync, or retirement).
- [ ] Cutover control is defined for non-canonical edits (block, redirect, or alert) during transition.
- [ ] Drift detection rule is specified, with implementation delegated to STORY-237.
- [ ] Migration/synchronization dry-run report is produced before execution.

## Definition of Done

- [ ] No unresolved design ambiguity remains on source-of-truth policy.
- [ ] Script design for sync/migration is reviewed and approved.
- [ ] Temporary anti-drift control is approved before migration starts.
