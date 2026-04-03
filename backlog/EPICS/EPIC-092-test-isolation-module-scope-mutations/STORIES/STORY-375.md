# STORY-375: Fix `test_load.py` — move DB URL env overrides into monkeypatched fixtures

**Epic**: EPIC-092 — Test Isolation
**Priority**: P0
**Size**: S (2–4 hours)
**Status**: 🔴 READY

---

## Context

`tests/performance/test_load.py` has two distinct contamination patterns:

**Pattern 1 — env override before imports (lines 7–8)**:
```python
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///file:testdb?mode=memory&cache=shared"
os.environ["SYNC_DATABASE_URL"] = "sqlite:///file:testdb?mode=memory&cache=shared"

import asyncio   # line 10
...
from solstein.config import Settings   # line 23 — reads the poisoned env
```
This is the most dangerous form: the override happens before any `solstein` module is imported,
so the very first `Settings` construction in the process uses the test URL. Never reset.

**Pattern 2 — Settings singleton mutation inside fixture without monkeypatch (lines 31–45)**:
```python
@pytest_asyncio.fixture
async def db_session():
    settings = Settings.load()          # cached singleton
    settings.database.url = "sqlite+aiosqlite:///test_perf.sqlite3"   # NEVER RESTORED
    ...
    yield session
    await db_manager.drop_tables()
    # settings.database.url remains "test_perf.sqlite3" forever
```

**Pattern 3 — sys.path mutation (line 21)**:
```python
sys.path.insert(0, os.path.dirname(...))   # permanent, never removed
```

---

## Acceptance Criteria

- [ ] Lines 7–8 `os.environ` assignments are removed from module scope
- [ ] DB URL overrides are applied inside an `autouse` session or module fixture using
      `monkeypatch.setenv` (which auto-restores after the fixture scope ends)
- [ ] `settings.database.url` mutation inside `db_session` fixture uses `monkeypatch.setattr`
      so it is restored after each test function
- [ ] `sys.path.insert` at line 21 is removed (the `src/` path is already on the path via
      `pyproject.toml` or `conftest.py`; verify and remove if redundant)
- [ ] All existing performance tests still pass

---

## Technical Notes

**For env vars before imports** — the correct pattern is `conftest.py` with `autouse`:
The env override cannot be moved into the test file itself if imports need to come after it.
The standard solution is to place the override in `tests/performance/conftest.py`:
```python
@pytest.fixture(autouse=True, scope="session")
def _patch_db_url(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///file:testdb?mode=memory&cache=shared")
    monkeypatch.setenv("SYNC_DATABASE_URL", "sqlite:///file:testdb?mode=memory&cache=shared")
```

**For Settings mutation** — replace direct attribute assignment with `monkeypatch.setattr`:
```python
@pytest_asyncio.fixture
async def db_session(monkeypatch):
    settings = Settings.load()
    monkeypatch.setattr(settings.database, "url", "sqlite+aiosqlite:///test_perf.sqlite3")
    # ... monkeypatch auto-restores settings.database.url after yield
```

---

## Definition of Done

- [ ] No module-scope `os.environ` assignments in `test_load.py`
- [ ] Settings mutation is `monkeypatch`-protected and auto-restores
- [ ] `sys.path.insert` at line 21 removed (or justified with a comment if truly needed)
- [ ] `pytest tests/performance/test_load.py` passes at 0 failures
- [ ] `ruff check tests/performance/test_load.py` at 0 errors
