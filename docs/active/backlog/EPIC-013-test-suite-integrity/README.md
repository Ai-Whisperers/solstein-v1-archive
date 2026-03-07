# EPIC-013: Test Suite Integrity

| Field | Value |
|-------|-------|
| Priority | **P2** |
| Status | 🔴 Open |
| Stories | 3 |
| Created | 2026-02-28 |
| Depends On | None |

## Context

The test suite reports high coverage. It is not accurate.

`tests/conftest.py` contains an `autouse=True` fixture that patches the data loader across the entire test suite, replacing it with a stub. This means approximately 28% of "covered" code has never been executed against real data loading logic. The coverage metric is a fiction.

There are zero boundary tests for any scoring tier transition. The most important behavioural guarantee of the entire platform — that a score of X.XX maps to tier Y — has no automated verification. Someone could change a threshold and no test would fail.

`adapters/registry.py`, `adapters/instrumented.py`, and `core/monitoring.py` have zero test coverage. The monitoring module contains the fake health checks (see EPIC-014) and the registry is the adapter discovery mechanism — both are untested.

## Scope

| Story | Title | Severity |
|-------|-------|----------|
| [STORY-044](STORIES/STORY-044-fix-autouse-fixture-masking.md) | Fix autouse Fixture Masking in Test Suite | HIGH |
| [STORY-045](STORIES/STORY-045-add-scoring-boundary-tests.md) | Add Boundary Tests for All Scoring Tiers | HIGH |
| [STORY-046](STORIES/STORY-046-add-missing-module-tests.md) | Add Tests for Untested Core Modules | MEDIUM |

## Definition of Done

- [ ] No autouse fixture suppresses real module behaviour
- [ ] Every tier boundary has an automated test
- [ ] registry.py, instrumented.py, and monitoring.py have test coverage
