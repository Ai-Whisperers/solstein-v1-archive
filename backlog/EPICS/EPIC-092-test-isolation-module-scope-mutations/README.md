# EPIC-092: Test Isolation — Module-Scope Mutation Prevention

> **Priority**: P0 — Ship Blocker (module-scope mutations bypass security gates across entire test session)
> **Stories**: 4 (STORY-374 through STORY-377)
> **Effort**: S (2–3 days total)
> **Dependencies**: None
> **Status**: 🔴 READY
> **Created**: 2026-04-03
> **Audit source**: `docs/audit/BACKLOG_STRUCTURAL_AUDIT_2026-04-03.md` (Third-Pass section)

---

## Problem

Three test files execute mutations at **module import time** that persist for the entire pytest
session, silently bypassing security controls for all subsequently-loaded test modules:

1. **`tests/unit/test_api_routers_coverage.py:19–25`** sets `app.dependency_overrides` (auth bypass),
   `_settings.api.require_api_key = False`, and `os.environ["SOLSTEIN_DISABLE_RATE_LIMIT"] = "true"`
   at module scope — never cleaned up. Any test loaded after this file runs with permanently
   disabled authentication and rate limiting on the production FastAPI app object.

2. **`tests/performance/test_load.py:7–8`** sets `os.environ["DATABASE_URL"]` and
   `os.environ["SYNC_DATABASE_URL"]` to in-memory SQLite **before** `solstein.config` is imported,
   poisoning `Settings` for the remainder of the process. Also mutates the Settings singleton
   inside a fixture without `monkeypatch` — the mutation survives fixture teardown.

3. **Two test DB files** (`test_integration.db` at 796KB, `test_perf.sqlite3` at 812KB) exist at
   the repo root and are tracked in git. They contain schema + data written by test runs and are
   checked out by every developer, providing stale pre-populated databases to CI runs.

Additionally, `src/solstein/data/security_hardening.py` exposes `rate_limiter` and `audit_logger`
as module-level singletons with mutable state that tests directly manipulate.

---

## Stories

| Story | Title | Priority | Size | Status |
|-------|-------|----------|------|--------|
| STORY-374 | Fix `test_api_routers_coverage.py` — move module-scope app/settings mutations into fixtures | P0 | S | 🔴 READY |
| STORY-375 | Fix `test_load.py` — move DB URL env overrides and Settings mutation into monkeypatched fixtures | P0 | S | 🔴 READY |
| STORY-376 | Remove leaked test DB files from git; add `.gitignore` rules for `test_*.db` / `test_*.sqlite*` | P0 | XS | 🔴 READY |
| STORY-377 | Add CI guard detecting module-scope `os.environ`, `app.dependency_overrides`, `get_settings()` in test files | P0 | S | 🔴 READY |

All four stories are independent.

---

## Key Files (Codebase-Verified 2026-04-03)

| File | Line | Issue |
|------|------|-------|
| `tests/unit/test_api_routers_coverage.py` | 19–25 | Three module-scope mutations — auth bypass, settings, env var |
| `tests/performance/test_load.py` | 7–8, 21, 31–45 | DB URL env override before imports; sys.path mutation; Settings mutation without monkeypatch |
| `test_integration.db` | repo root | 796KB test DB tracked in git |
| `test_perf.sqlite3` | repo root | 812KB test DB tracked in git |
| `src/solstein/data/security_hardening.py` | 404–406 | `rate_limiter`, `audit_logger` module-level singletons with mutable public state |

---

## Definition of Done

- [ ] `test_api_routers_coverage.py` has no module-scope mutations — all overrides inside fixtures with cleanup
- [ ] `test_load.py` DB URL overrides are inside an `autouse` fixture using `monkeypatch.setenv`
- [ ] `test_load.py` Settings mutation uses `monkeypatch` and is restored after each test
- [ ] `test_integration.db` and `test_perf.sqlite3` removed from git tracking and added to `.gitignore`
- [ ] CI script fails if any test file under `tests/` contains module-scope `os.environ[`, `app.dependency_overrides[`, or `get_settings()` outside a function/class body
- [ ] `pytest` passes at 0 failures, `ruff check` at 0 errors
