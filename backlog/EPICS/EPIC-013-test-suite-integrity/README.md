# EPIC-013: Test Suite Integrity

| Field | Value |
|-------|-------|
| Priority | **P0 — Ship Blocker** (upgraded 2026-04-03: module-scope mutations bypass auth/rate-limit gates for entire test session) |
| Status | 🔴 Open |
| Stories | 13 (5 original + 8 added 2026-04-03 from contamination audit) |
| Created | 2026-02-28 |
| Updated | 2026-04-03 |
| Depends On | None |

## Context

The test suite reports high coverage. It is not accurate.

`tests/conftest.py` contains an `autouse=True` fixture that patches the data loader across the entire test suite, replacing it with a stub. This means approximately 28% of "covered" code has never been executed against real data loading logic. The coverage metric is a fiction.

There are zero boundary tests for any scoring tier transition. The most important behavioural guarantee of the entire platform — that a score of X.XX maps to tier Y — has no automated verification. Someone could change a threshold and no test would fail.

`adapters/registry.py`, `adapters/instrumented.py`, and `core/monitoring.py` have zero test coverage. The monitoring module contains the fake health checks (see EPIC-014) and the registry is the adapter discovery mechanism — both are untested.

## Scope

### Original stories

| Story | Title | Severity | Status |
|-------|-------|----------|--------|
| [STORY-044](STORIES/STORY-044-fix-autouse-fixture-masking.md) | Fix autouse Fixture Masking in Test Suite | HIGH | 🔴 Open |
| [STORY-045](STORIES/STORY-045-add-scoring-boundary-tests.md) | Add Boundary Tests for All Scoring Tiers | HIGH | 🔴 Open |
| [STORY-046](STORIES/STORY-046-add-missing-module-tests.md) | Add Tests for Untested Core Modules | MEDIUM | 🔴 Open |
| [STORY-253](STORIES/STORY-253-replace-structural-tests-with-behavioral-contract-tests.md) | Replace Structural Source-Inspection Tests with Behavioral Contract Tests | HIGH | 🔴 Open |
| [STORY-254](STORIES/STORY-254-remove-test-collection-side-effects.md) | Remove Test Collection Side Effects and Env-Coupled Imports | HIGH | 🔴 Open |

### P0 additions — test isolation (contamination audit 2026-04-03)

Verified by direct codebase read. All READY, no dependencies.

**Factory and runtime separation:**

| Story | Title | Size | Status |
|-------|-------|------|--------|
| [STORY-371](STORIES/STORY-371.md) | Fix test factories — add `data_source_type="synthetic"` default to all CompanyFactory classes | XS | 🔴 READY |
| [STORY-372](STORIES/STORY-372.md) | Deduplicate test factory modules — one `CompanyFactory` definition, not two divergent ones | S | 🔴 READY |
| [STORY-373](STORIES/STORY-373.md) | Add CI guard: no `src/` module may import from `tests.*` or `scripts.*` | XS | 🔴 READY |

**Module-scope mutation isolation** (extends [STORY-254](STORIES/STORY-254-remove-test-collection-side-effects.md)):

| Story | Title | Size | Status |
|-------|-------|------|--------|
| [STORY-374](STORIES/STORY-374.md) | Fix `test_api_routers_coverage.py` — move module-scope `app.dependency_overrides` / settings mutations into fixtures | S | 🔴 READY |
| [STORY-375](STORIES/STORY-375.md) | Fix `test_load.py` — move `os.environ["DATABASE_URL"]` override (before imports) into monkeypatched fixture | S | 🔴 READY |
| [STORY-376](STORIES/STORY-376.md) | Remove `test_integration.db` and `test_perf.sqlite3` from git; add `.gitignore` rules | XS | 🔴 READY |
| [STORY-377](STORIES/STORY-377.md) | Add CI guard: detect module-scope `os.environ`, `app.dependency_overrides`, `get_settings()` mutations in test files | S | 🔴 READY |
| [STORY-387](STORIES/STORY-387.md) | Fix `pyproject.toml` — remove global `DeprecationWarning` suppression; add integration test separation | S | 🔴 READY |

**Key verified findings driving P0 upgrade:**
- `tests/unit/test_api_routers_coverage.py:19–25` — permanently disables auth, API key check, and rate limiting at module import time for the entire pytest session
- `tests/performance/test_load.py:7–8` — overrides `DATABASE_URL` before `solstein.config` is imported, poisoning `Settings` singleton for the process; never reset
- `test_integration.db` (796KB) and `test_perf.sqlite3` (812KB) tracked in git — developers clone stale pre-seeded databases

## Definition of Done

- [ ] No autouse fixture suppresses real module behaviour
- [ ] Every tier boundary has an automated test
- [ ] registry.py, instrumented.py, and monitoring.py have test coverage
- [ ] Critical-path tests prove runtime behavior instead of only matching source text
- [ ] Targeted unit-test collection works without ad-hoc runtime env injection
- [ ] No module-scope `os.environ`, `app.dependency_overrides`, or settings mutations in any test file
- [ ] Both factory modules default to `data_source_type="synthetic"`; single canonical `CompanyFactory`
- [ ] `test_integration.db` and `test_perf.sqlite3` removed from git tracking
- [ ] CI guards enforce src/test boundary and module-scope mutation prohibition

## Autonomous Continuation Notes

### Verified Codebase State (2026-04-04)

Direct file reads confirm all P0 issues are STILL PRESENT and unresolved:

**Module-scope mutations (STORY-374, STORY-375):**
- `tests/unit/test_api_routers_coverage.py:20` — `app.dependency_overrides[get_current_user] = lambda: {"username": "test_user"}` set at module scope → auth disabled for entire session
- `tests/unit/test_api_routers_coverage.py:21` — `app.dependency_overrides[get_current_tenant]` also set at module scope
- `tests/unit/test_api_routers_coverage.py:25` — `os.environ["SOLSTEIN_DISABLE_RATE_LIMIT"] = "true"` set at module scope
- `tests/performance/test_load.py:7-8` — `os.environ["DATABASE_URL"]` and `os.environ["SYNC_DATABASE_URL"]` set before any imports → poisons Settings singleton

**Factory `data_source_type` missing (STORY-371, STORY-372):**
- `tests/factories.py:56` — `class CompanyFactory(Factory[Company])` — no `data_source_type` field default
- `tests/factories/__init__.py:64` — second `class CompanyFactory(Factory[Company])` — no `data_source_type` field default
- Two divergent factory definitions confirmed: `tests/factories.py` and `tests/factories/__init__.py`

**conftest.py (STORY-044):**
- `tests/conftest.py:20-23` — uses `os.environ.setdefault()` (safe, not module-scope mutation) — this specific file is lower risk than the others

**Files still tracked in git (STORY-376):**
- `tests/test_integration.db` (796KB) — confirmed in git status as modified
- `tests/test_perf.sqlite3` (812KB) — confirmed in git status as modified

**Execution order recommendation:**
1. STORY-376 (remove DBs from git) — XS, no code changes, immediate win
2. STORY-374 (fix test_api_routers_coverage.py) — highest blast radius auth bypass
3. STORY-375 (fix test_load.py DATABASE_URL) — Settings singleton poisoning
4. STORY-371+372 (factory data_source_type) — parallel with 374/375
5. STORY-373, STORY-377 (CI guards) — after fixes are in place
6. STORY-387 (pyproject.toml) — independent

### Current Develop Status

- All P0 stories (STORY-371-377, STORY-387) are READY — no dependencies unmet.
- This epic IS scheduled in `planning/QUEUE.md` as P0 (contamination audit 2026-04-03).
- Start with STORY-376 (no code changes, just git operations).

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md` and `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`.
- Prefer narrow, machine-checkable progress over broad narrative backlog churn.
- Each story must include tests that prove the mutation is gone.

### Minimum Verification For Future Agents

- Run `pytest tests/unit/test_api_routers_coverage.py -x` before and after STORY-374 to confirm auth is not globally bypassed.
- Run `pytest tests/performance/test_load.py -x` before and after STORY-375 to confirm DATABASE_URL is not overridden globally.
- After STORY-371/372: confirm `CompanyFactory().data_source_type == "synthetic"` in a quick test.
