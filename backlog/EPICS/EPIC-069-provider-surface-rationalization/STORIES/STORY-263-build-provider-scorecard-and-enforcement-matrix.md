# STORY-263: Build Provider Scorecard and Enforcement Matrix

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P0 - Ship Blocker |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-069 Provider Surface Rationalization |
| **Created** | 2026-03-31 |
| **Risk** | Low |

---

## Problem Statement

The repo has many providers but no single enforcement matrix that states who owns each one, how IDs are resolved, what retry behavior is allowed, how long data is cached, and what confidence semantics are attached. Without that matrix, the same provider is handled differently in different code paths.

## Acceptance Criteria

- [ ] A canonical provider matrix exists for the active legacy runtime surfaces.
- [ ] Each provider row includes schema owner, retry class, cache TTL, ID rules, and confidence semantics.
- [ ] The matrix explicitly marks deprecated and replaceable providers.
- [ ] The matrix is referenced by the active backlog and implementation docs.

## Tasks

- [ ] Inventory the providers currently reachable from the canonical runtime.
- [ ] Define the enforcement columns.
- [ ] Publish the matrix in the canonical backlog/docs path.
