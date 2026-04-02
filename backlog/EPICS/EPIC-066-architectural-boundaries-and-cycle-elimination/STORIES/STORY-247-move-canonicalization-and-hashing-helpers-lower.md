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

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- `planning/QUEUE.md` marks this story `BLOCKED` on `STORY-245` and EPIC-031 progress.

### Next Agent Action

- Wait for blockers to move, then relocate only the truly shared helpers.

### Required Working Style

- Keep behavior identical while lowering ownership.
- Do not move unrelated research or persistence logic with the helpers.

### Minimum Verification For Future Agents

- Prove the new lower-layer helper is used by both sides.
- Run focused regression tests around canonicalization and hashing behavior.
