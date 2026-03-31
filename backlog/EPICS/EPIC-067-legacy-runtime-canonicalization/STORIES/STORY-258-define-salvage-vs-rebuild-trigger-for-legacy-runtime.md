# STORY-258: Define Salvage-vs-Rebuild Trigger for the Legacy Runtime

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P1 - High |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-067 Legacy Runtime Canonicalization |
| **Created** | 2026-03-31 |
| **Risk** | Medium |

---

## Problem Statement

The team wants to save the mature legacy path first, but only if that path is not too contaminated by placeholder logic, alias drift, and silent field loss. There is currently no explicit threshold that tells us when to stop patching and rebuild instead.

## Acceptance Criteria

- [ ] A legacy-runtime scorecard exists with measurable criteria: placeholder incidence, alias incidence, field-loss rate, silent-failure rate, and golden-run pass rate.
- [ ] The scorecard defines a hard rebuild trigger.
- [ ] The decision gate is based on reproducible evidence artifacts, not narrative judgment.
- [ ] The scorecard is wired into the backlog sequencing for EPIC-070.

## Tasks

- [ ] Define the metrics and thresholds.
- [ ] Identify the files and tests that produce each metric.
- [ ] Publish the rebuild trigger in the canonical backlog docs.
