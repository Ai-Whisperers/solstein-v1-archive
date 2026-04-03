# STORY-376: Remove leaked test DB files from git; add `.gitignore` rules

**Epic**: EPIC-092 — Test Isolation
**Priority**: P0
**Size**: XS (< 30 minutes)
**Status**: 🔴 READY

---

## Context

Two SQLite database files exist at the repo root and are currently tracked in git:

```
test_integration.db    — 796KB — created by tests/integration/test_data_migration.py
test_perf.sqlite3      — 812KB — created by tests/performance/test_load.py
```

These files:
1. Contain schema + data written by previous test runs
2. Are checked out by every developer cloning the repo
3. May be used by CI runs if the cleanup fixture fails (test_load.py tries to drop tables in teardown but only if the fixture completes cleanly)
4. Accumulate across test runs — they are in `git status` as "modified" today

`test_integration.db` also appeared as modified in the git status at the start of this session,
confirming it is being mutated by test runs and committed/tracked.

---

## Acceptance Criteria

- [ ] `test_integration.db` removed from git tracking (`git rm --cached`)
- [ ] `test_perf.sqlite3` removed from git tracking (`git rm --cached`)
- [ ] Both files added to `.gitignore` with pattern `test_*.db` and `test_*.sqlite3`
      (or more specific patterns if broad exclusion is undesirable)
- [ ] Verify no test hardcodes the path `test_integration.db` as a fixture expectation
      (tests should create the DB fresh each run, not rely on a checked-in copy)
- [ ] Commit removes both files from git history going forward

---

## Technical Notes

```bash
git rm --cached test_integration.db test_perf.sqlite3
echo "test_*.db" >> .gitignore
echo "test_*.sqlite3" >> .gitignore
```

**Verify before removing**: Run `grep -r "test_integration.db\|test_perf.sqlite3" tests/ --include="*.py"`
to confirm which tests create these files and that they don't rely on a pre-existing file
(i.e., they must call `create_tables()` themselves rather than expecting the file to already exist).

Files found:
- `tests/integration/test_data_migration.py` — creates `test_integration.db`
- `tests/performance/test_load.py` — creates `test_perf.sqlite3`

Both should create fresh databases via `create_tables()` at fixture start.

---

## Definition of Done

- [ ] Neither `test_integration.db` nor `test_perf.sqlite3` in `git ls-files`
- [ ] Both patterns in `.gitignore`
- [ ] `pytest` still passes (tests recreate DB files on demand)
- [ ] `ruff check` at 0 errors
