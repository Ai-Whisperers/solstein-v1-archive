# STORY-249: Enforce Import-Cycle and Module-Boundary Checks in Maintained Gates

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

The repo already has cycle and boundary scanners, but they are not yet part of the maintained blocking gate set. That lets architectural debt re-enter even after it is discovered.

## Acceptance Criteria

- [ ] Cycle and boundary checks have a documented maintained scope.
- [ ] Known false positives are either fixed or explicitly carved out with rationale.
- [ ] The maintained engineering gate runs these checks for the agreed scope.
- [ ] Generated docs reference the enforced structural policies.

## Tasks

- [ ] Review the current scanner outputs and eliminate or document false positives.
- [ ] Add the maintained checks to `Makefile` and the strict engineering workflow.
- [ ] Document the scope and exceptions in the engineering guardrail docs.
