# STORY-022: Consolidate Duplicate Route Directories

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P1 |
| Severity | MEDIUM |
| Epic | [EPIC-006: Unification of Duplicates](../README.md) |
| Created | 2026-02-28 |
| Dependencies | None |

---

## The Audit Verdict

> `api/routers/` contains 10 route files. `api/routes/` contains 1 file: `refresh.py`. No documentation explains why the refresh route lives in a separate directory. The inconsistency suggests an incomplete migration or a forgotten file.

## Problem Statement

Two route directories create confusion about where new routes should be added. `api/routers/` is clearly the primary directory with 10 route files. `api/routes/` contains a single orphaned file: `refresh.py`. This is either the remnant of an incomplete naming migration (routers → routes or vice versa) or a file that was accidentally placed in the wrong directory.

The practical harm is modest but the conceptual harm is real: every new engineer must decide which directory to use, and the refresh route may be overlooked in security audits, documentation generation, or route-level middleware application that targets `api/routers/`.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Developer Experience** | Ambiguity about where to add new routes |
| **Discoverability** | Routes in `api/routes/` may be overlooked in security audits or documentation |
| **Consistency** | Two naming conventions for the same concept in the same codebase |
| **Tooling** | Automated tools scanning `api/routers/` will miss routes in `api/routes/` |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/api/routes/refresh.py` | Move | Must be moved to `api/routers/refresh.py` |
| `src/solstein/api/routes/` | Delete | Directory must be removed after the file is moved |
| `src/solstein/api/main.py` | Modify | Router registration must be updated to import from `api/routers/refresh` |
| Any imports referencing `api/routes/` | Modify | Must be updated to `api/routers/` |

## Architectural Requirements

- **REQ-1**: All route files must exist in one directory: `api/routers/`
- **REQ-2**: The `api/routes/` directory must be eliminated entirely — not left empty, not renamed
- **REQ-3**: `refresh.py` must be moved to `api/routers/` with its router registration updated accordingly in `main.py`
- **REQ-4**: A comment in `main.py` at the router registration section must document that `api/routers/` is the canonical and only route directory

## Acceptance Criteria

- [ ] `api/routes/` directory does not exist
- [ ] The refresh route is accessible via the same URL path and returns the same responses as before the move
- [ ] All routers are registered from `api/routers/`
- [ ] `grep -r "api/routes" . --include="*.py"` returns zero results (excluding this backlog)

## Definition of Done

**Tests Required:**
- [ ] Integration test confirming the refresh endpoint URL is unchanged and returns correct responses
- [ ] `grep` confirming `api/routes/` is absent from all Python source files

**Documentation Required:**
- [ ] Comment in `main.py` at the router registration block: `# All routes live in api/routers/ — do not create api/routes/`

**Code Review Gate:**
- [ ] Reviewer confirms the `api/routes/` directory is deleted
- [ ] Reviewer confirms the refresh endpoint URL has not changed

## Notes

This is the simplest story in this epic. It is a file move, an import update, and a directory deletion. It can be completed in under an hour. Do it first to build momentum and reduce the cognitive overhead of the duplicate directory for all subsequent work.

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This story currently carries a historical open or in-progress backlog badge.
- If `planning/QUEUE.md` does not currently list this story as active work, treat it as triage-required rather than immediately actionable.

### Next Agent Action

- Reconcile this story against current code reality, `planning/QUEUE.md`, and the develop autonomy audit before starting.
- Do not begin implementation from this file alone unless the queue or a fresh planning decision reactivates it.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`, `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`, and `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Preserve machine-checkable enforcement and avoid prose-only or speculative "AI slop" updates.

### Minimum Verification For Future Agents

- If this story is reactivated, update the queue or controlling planning artifact first.
- Then prove the work with the smallest relevant regression tests, gates, or generated artifacts for the touched boundary.
