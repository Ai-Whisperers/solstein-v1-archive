# STORY-348: Change `extra="ignore"` to `extra="forbid"` on Company and FinancialMetric

| Field | Value |
|---|---|
| **Status** | ✅ DONE |
| **Priority** | P0 — Must be first |
| **Size** | S (1 day) |
| **Epic** | EPIC-086 Pipeline Field Loss — Silent Data Corruption |
| **Created** | 2026-04-02 |
| **Risk** | High (will expose existing callers passing undeclared fields — each is a real bug) |
| **Execution Order** | 1 of 4 — do this first |

---

## Problem Statement

`Company` and `FinancialMetric` are both configured with `extra="ignore"`. This was set in STORY-251
to prevent unknown keys from leaking into `model_dump()` output. The unintended consequence is that
every field mapping error anywhere upstream — in `aggregate.py`, `signals.py`, or `company_builder.py` —
produces no observable signal. Fields vanish with no exception, no log line, no test failure.

This makes it structurally impossible to detect pipeline field loss. Changing to `extra="forbid"` turns
every mapping gap into an immediate, visible `ValidationError`.

---

## Acceptance Criteria

- [x] `Company` model uses `extra="forbid"` in its `model_config`
- [x] `FinancialMetric` model uses `extra="forbid"` in its `model_config`
- [x] `pytest` is run after the change — all failures catalogued (none from extra="forbid"; 3 pre-existing validator failures)
- [x] Note: zero new `extra_forbidden` errors found — all production callers already use only declared fields. Pre-existing failures: `growth_rate` out-of-range in test fixtures, `require_primary_metric` in test fixtures. Not caused by this story.
- [x] A comment in both models explains the policy (STORY-348 docstring added)
- [x] `ruff check` passes at 0 errors

---

## Tasks

- [x] Edit `src/solstein/domain/models.py`: change `extra="ignore"` to `extra="forbid"` on `FinancialMetric`
- [x] Edit `src/solstein/domain/models.py`: change `extra="ignore"` to `extra="forbid"` on `Company`
- [x] Run `pytest` — no new `extra_forbidden` errors; 3 pre-existing test fixture failures (unrelated)
- [x] Update `tests/unit/test_story251_boundary_schemas.py` to assert `== "forbid"` and expect `ValidationError` on extra fields
- [x] Pre-existing failures noted: test fixtures using `growth_rate=10_000` and `FinancialMetric(profit_margin=0.0)` without required primary fields

---

## Autonomous Continuation Notes

### Critical
This story intentionally breaks things. That is correct behavior. Do not suppress failures.
Every `ValidationError` you see is a place where a field is being passed that the model doesn't know about,
OR a place where a field should be in the model but isn't. Both are bugs.

### Next Action After This Story
Run `pytest 2>&1 | grep -E "ValidationError|FAILED" | head -50` and paste the output into the PR.
That output is the input for STORY-349 and STORY-350.

### Do Not
- Do not revert to `extra="ignore"` or `extra="allow"`
- Do not add `model_config = ConfigDict(extra="ignore")` to any test fixture
- Do not `# noqa` or suppress any ValidationError
