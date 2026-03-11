# STORY-234: Repair Broken Relative Links and Establish Baseline Report

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P0 - Ship Blocker |
| **Size** | L (1 week) |
| **Epic** | EPIC-064 Markdown Integrity and Registry Correctness |
| **Created** | 2026-03-11 |
| **Risk** | Medium |

---

## Problem Statement

Broken links prevent reliable navigation and can invalidate operational runbooks.

## Acceptance Criteria

- [ ] A reproducible link-check command is documented.
- [ ] All broken relative links in scoped trees are fixed or explicitly allowlisted.
- [ ] Link exceptions require `owner`, `rationale`, and `expiry` metadata.
- [ ] Post-fix report includes before/after counts.

## Definition of Done

- [ ] CI link check passes on target branches.
- [ ] No unresolved high-severity broken links remain.
