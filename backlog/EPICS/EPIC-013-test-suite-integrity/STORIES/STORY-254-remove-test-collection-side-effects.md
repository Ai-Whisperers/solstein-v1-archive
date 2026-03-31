# STORY-254: Remove Test Collection Side Effects and Env-Coupled Imports

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P1 - High |
| **Size** | S (1-2 days) |
| **Epic** | EPIC-013 Test Suite Integrity |
| **Created** | 2026-03-31 |
| **Risk** | High |

---

## Problem Statement

Targeted pytest runs currently fail during collection unless `DATABASE__URL` is injected manually. The root cause is eager runtime imports in `tests/conftest.py` and module-level singleton initialization that pulls configuration during import. This blocks isolated QA, slows agent iteration, and makes the suite environment-fragile.

## Acceptance Criteria

- [ ] Targeted unit-test collection succeeds in a minimal test environment without manually exporting `DATABASE__URL`.
- [ ] `tests/conftest.py` avoids eager imports that force database/config loading for tests that do not need it.
- [ ] Module-level singleton or loader initialization that requires runtime settings is made lazy, injectable, or otherwise test-safe.
- [ ] A regression test or documented smoke command proves collection remains hermetic.

## Tasks

- [ ] Remove or defer import-time configuration access from the unit-test bootstrap path.
- [ ] Audit module-level loader singletons that trigger settings/database access at import time.
- [ ] Update fixtures to import expensive/runtime-bound dependencies lazily.
- [ ] Add a minimal collection/bootstrap verification command to prevent regressions.

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This story was added from the 2026-03-31 audit after isolated pytest runs failed during collection without env overrides.

### Next Agent Action

- Fix collection-time side effects first so later remediation stories can run their targeted tests cleanly.

### Required Working Style

- Change import behavior narrowly. Do not redesign configuration loading broadly unless the import-time trap cannot be removed otherwise.
- Preserve production startup behavior while making test collection hermetic.

### Minimum Verification For Future Agents

- Demonstrate a targeted pytest invocation collecting without manual `DATABASE__URL`.
- Show the fix does not rely on hidden local shell state.
