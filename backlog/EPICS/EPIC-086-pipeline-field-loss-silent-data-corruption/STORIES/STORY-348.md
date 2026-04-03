# STORY-348: Change `extra="ignore"` to `extra="forbid"` on Company and FinancialMetric

| Field | Value |
|---|---|
| **Status** | 🔴 READY |
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

- [ ] `Company` model uses `extra="forbid"` in its `model_config`
- [ ] `FinancialMetric` model uses `extra="forbid"` in its `model_config`
- [ ] `pytest` is run after the change — all failures are catalogued (do not fix in this story)
- [ ] Note: `FinancialMetric` has a `@model_validator` requiring `revenue OR employees`. With `extra="forbid"`, some failures may show as ValidationError on an extra field AND a missing primary field simultaneously. Log both; fix neither in this story.
- [ ] A comment in both models explains the policy: *"extra='forbid' is intentional — if you need a new field, add it to the model; do not revert to ignore"*
- [ ] `ruff check` passes at 0 errors

---

## Tasks

- [ ] Edit `src/solstein/domain/models.py`: change `extra="ignore"` to `extra="forbid"` on `FinancialMetric`
- [ ] Edit `src/solstein/domain/models.py`: change `extra="ignore"` to `extra="forbid"` on `Company`
- [ ] Run `pytest` and collect the list of failing tests (each represents a real mapping bug)
- [ ] Document the failing tests in the PR description — they are the work list for STORY-349 and STORY-350
- [ ] Do NOT fix callers in this story — just make the breakage visible

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
