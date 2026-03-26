# STORY-247: Move Canonicalization and Hashing Helpers to a Lower Shared Boundary

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P1 - High |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-066 Architectural Boundaries and Cycle Elimination |
| **Created** | 2026-03-26 |
| **Risk** | Medium |

---

## Problem Statement

Infrastructure persistence and reconciliation currently import `canonicalize_url` and `canonical_json_dumps` from higher `research` modules even though those helpers are generic utility concerns.

## Acceptance Criteria

- [ ] URL canonicalization moves to a lower shared module consumed by both `research` and `infrastructure`.
- [ ] Canonical JSON hashing/dumps helper moves to a lower shared module consumed by both `research` and `infrastructure`.
- [ ] Infrastructure modules no longer import from `solstein.research.*` for these utilities.
- [ ] Generated docs and boundary checks reflect the cleaner dependency shape.

## Tasks

- [ ] Introduce a lower shared utility module for canonicalization/hashing.
- [ ] Update `research_dual_write.py`, `research_persistence.py`, and `reconcile_runs.py`.
- [ ] Add regression coverage around canonicalization/hashing behavior before moving the helpers.
