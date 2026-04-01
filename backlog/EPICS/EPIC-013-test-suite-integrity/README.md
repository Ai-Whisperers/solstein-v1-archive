# EPIC-013: Test Suite Integrity

| Field | Value |
|-------|-------|
| Priority | **P2** |
| Status | 🔴 Open |
| Stories | 5 |
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
| [STORY-253](STORIES/STORY-253-replace-structural-tests-with-behavioral-contract-tests.md) | Replace Structural Source-Inspection Tests with Behavioral Contract Tests | HIGH |
| [STORY-254](STORIES/STORY-254-remove-test-collection-side-effects.md) | Remove Test Collection Side Effects and Env-Coupled Imports | HIGH |

## Definition of Done

- [ ] No autouse fixture suppresses real module behaviour
- [ ] Every tier boundary has an automated test
- [ ] registry.py, instrumented.py, and monitoring.py have test coverage
- [ ] Critical-path tests prove runtime behavior instead of only matching source text
- [ ] Targeted unit-test collection works without ad-hoc runtime env injection

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
