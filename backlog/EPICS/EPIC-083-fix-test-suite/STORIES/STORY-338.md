# STORY-338: Skip or conditionally run 210 database-dependent tests

| Field | Value |
|-------|-------|
| **Epic** | EPIC-083 |
| **Priority** | P1 |
| **Size** | S |
| **Status** | 🔴 READY |
| **Dependencies** | None |

## Description

210 tests require a running database and fail when no database is configured. Mark these with `@pytest.mark.db` and add a pytest option to exclude them from the default run.

## Acceptance Criteria

- [ ] All database-dependent tests marked with `@pytest.mark.db`
- [ ] Default `pytest` run excludes `@pytest.mark.db` tests
- [ ] `pytest -m db` runs only database tests
- [ ] CI has separate `test:unit` and `test:integration` jobs
