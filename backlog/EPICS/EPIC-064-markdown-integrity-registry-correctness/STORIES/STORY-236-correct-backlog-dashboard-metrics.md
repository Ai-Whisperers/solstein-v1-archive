# STORY-236: Correct Backlog Registry and Dashboard Metric Inconsistencies

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P0 - Ship Blocker |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-064 Markdown Integrity and Registry Correctness |
| **Created** | 2026-03-11 |
| **Risk** | Medium |

---

## Problem Statement

`backlog/README.md` contains conflicting dashboard rows and non-authoritative totals.

## Acceptance Criteria

- [ ] Dashboard metric definitions are documented with formulas.
- [ ] Duplicate/contradictory rows are removed.
- [ ] Metric generation is automated from epic/story source data.
- [ ] A canonical metrics artifact is published and treated as the only source for docs health consumers.
- [ ] Story and epic counts in README match generated output.

## Definition of Done

- [ ] One command regenerates metrics and updates dashboard sections.
- [ ] Validation check fails if displayed counts diverge from source-of-truth.
