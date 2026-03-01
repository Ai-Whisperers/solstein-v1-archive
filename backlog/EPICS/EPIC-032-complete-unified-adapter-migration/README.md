# EPIC-032: Complete Unified Adapter Migration

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | Critical |
| **Owner** | Data Engineering |
| **Created** | 2026-03-01 |

## Context

Forensic audit found 6 "unified" adapters that are technically incomplete. They gained BaseRefreshConnector inheritance but LOST original client wrappers that handled error handling, retry, and transformation. The migration was architectural, not functional parity. Old versions still exist in parallel, creating maintenance confusion.

## Stories

| Story | Title | Priority |
|-------|-------|----------|
| STORY-121 | Restore Error Handling in news_unified.py | P1 |
| STORY-122 | Restore Funding Adapter Wrapper | P1 |
| STORY-123 | Restore Website Adapter Validation | P1 |
| STORY-124 | Delete Old Adapter Versions After Parity | P1 |

## Dependencies

- EPIC-006 (unification of duplicates)
- STORY-092 (merge task files)

## Notes

The "unified" adapters are actually regressions in functionality. This epic restores what was lost and completes the migration by deleting the old versions.
