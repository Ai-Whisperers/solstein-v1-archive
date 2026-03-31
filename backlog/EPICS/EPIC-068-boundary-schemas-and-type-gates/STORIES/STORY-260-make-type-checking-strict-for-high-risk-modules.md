# STORY-260: Make Type Checking Strict for High-Risk Modules

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P0 - Ship Blocker |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-068 Boundary Schemas and Type Gates |
| **Created** | 2026-03-31 |
| **Risk** | Medium |

---

## Problem Statement

`pyproject.toml` still keeps `mypy` in non-strict mode and explicitly allows untyped defs across large parts of the codebase. That makes it too easy for alias-heavy and placeholder-heavy code to compile while violating the intended contract boundaries.

## Acceptance Criteria

- [ ] Strict typing is enabled for the canonical runtime modules first.
- [ ] High-risk modules fail CI on new `Any` leakage or missing annotations.
- [ ] Type-checking scope and suppressions are documented with owners.
- [ ] The new gate is narrow enough to be maintainable but strict enough to matter.

## Tasks

- [ ] Pick the first strict-scope modules on the canonical path.
- [ ] Tighten `mypy`/`basedpyright` config for that scope.
- [ ] Add a blocking CI target for the strict scope.
