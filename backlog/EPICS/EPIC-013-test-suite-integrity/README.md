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

**Module-scope mutation isolation** (extends STORY-254):

| Story | Title | Size | Status |
|-------|-------|------|--------|
| [STORY-374](STORIES/STORY-374.md) | Fix `test_api_routers_coverage.py` — move module-scope `app.dependency_overrides` / settings mutations into fixtures | S | 🔴 READY |
| [STORY-375](STORIES/STORY-375.md) | Fix `test_load.py` — move `os.environ["DATABASE_URL"]` override (before imports) into monkeypatched fixture | S | 🔴 READY |
| [STORY-376](STORIES/STORY-376.md) | Remove `test_integration.db` and `test_perf.sqlite3` from git; add `.gitignore` rules | XS | 🔴 READY |
| [STORY-377](STORIES/STORY-377.md) | Add CI guard: detect module-scope `os.environ`, `app.dependency_overrides`, `get_settings()` mutations in test files | S | 🔴 READY |

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

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This epic currently carries a historical open or in-progress backlog badge.
- If `planning/QUEUE.md` does not currently schedule this epic, treat it as triage-required backlog inventory instead of self-startable work.

### Next Agent Action

- Reconcile this epic against current code reality, `planning/QUEUE.md`, and the develop autonomy audit before selecting a story.
- Do not start implementation from this README alone unless the queue or a fresh planning decision activates the epic.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`, `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`, and `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Prefer narrow, machine-checkable progress over broad narrative backlog churn.

### Minimum Verification For Future Agents

- If this epic is reactivated, update the queue or controlling planning artifact first.
- Then execute one story at a time with the relevant tests, gates, and generated references for the touched surface.
