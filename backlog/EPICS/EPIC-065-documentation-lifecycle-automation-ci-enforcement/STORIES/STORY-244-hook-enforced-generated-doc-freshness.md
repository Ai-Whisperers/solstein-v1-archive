# STORY-244: Enforce Generated Docs Freshness Through Git Hooks and CI

| Field | Value |
|---|---|
| **Status** | 🟡 In Progress |
| **Priority** | P1 - High |
| **Size** | S (1-2 days) |
| **Epic** | EPIC-065 Documentation Lifecycle Automation and CI Enforcement |
| **Created** | 2026-03-26 |
| **Risk** | Medium |

---

## Problem Statement

Generated docs are only useful if they stay fresh automatically. Manual regeneration is not strong enough for a commercial repository with frequent agent-driven edits.

## Acceptance Criteria

- [x] Repository-managed hooks exist in `.githooks/`.
- [x] `pre-commit` refreshes and stages generated docs.
- [x] `pre-push` blocks stale generated outputs.
- [x] A repo command configures `core.hooksPath`.
- [ ] CI uses the same freshness check so enforcement is not only local.

## Definition of Done

- [x] `make hooks-install` configures the repo hook path.
- [x] `make docs-generated-check` is blocking in the engineering gate.
- [ ] CI workflow configuration consumes the same check.
