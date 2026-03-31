# STORY-270: Make Save-vs-Rebuild Decision from Golden-Run Evidence

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P0 - Ship Blocker |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-070 Empirical Golden Runs and Rebuild Gate |
| **Created** | 2026-03-31 |
| **Risk** | High |

---

## Problem Statement

The team needs a hard decision point: continue salvaging the legacy runtime or begin a controlled rebuild. That choice cannot be made from backlog prose alone; it must be made from the measured outcome of provider contract runs, full-market golden runs, placeholder-path checks, and the legacy contamination scorecard.

## Acceptance Criteria

- [ ] A formal decision record is written after the golden-run evidence is collected.
- [ ] The decision cites measured defect rates and failure classes.
- [ ] If salvage continues, the next backlog wave is scoped to the proven failure surfaces only.
- [ ] If rebuild is triggered, the new scope explicitly forbids compatibility patch carry-forward.

## Tasks

- [ ] Gather the evidence artifacts from EPIC-067 through EPIC-070.
- [ ] Score the legacy path against the rebuild trigger.
- [ ] Publish the decision and update backlog priorities accordingly.
