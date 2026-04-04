# STORY-337: Fix API router tests (add test auth bypass for 401 failures)

| Field | Value |
|-------|-------|
| **Epic** | EPIC-083 |
| **Priority** | P1 |
| **Size** | S |
| **Status** | 🔴 READY |
| **Dependencies** | None |

## Description

API router tests fail with 401 because auth is now enforced but test clients don't provide credentials. Add proper test auth bypass fixtures to the router tests.

NOTE: This is different from STORY-374 (which fixes module-scope auth bypass). This story adds CORRECT fixture-scoped auth bypass for router tests.

## Acceptance Criteria

- [ ] All API router tests that test business logic (not auth) pass
- [ ] Auth bypass is fixture-scoped (not module-scope)
- [ ] Auth-specific tests still test real auth behavior
