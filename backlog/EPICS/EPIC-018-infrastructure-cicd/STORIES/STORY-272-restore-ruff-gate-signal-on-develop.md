# STORY-272: Restore Ruff Gate Signal Integrity on Current Develop

| Field | Value |
|-------|-------|
| Status | 🟡 In Progress |
| Priority | P1 |
| Size | M |
| Epic | [EPIC-018: Infrastructure-as-Code & CI/CD](../README.md) |
| Created | 2026-04-01 |
| Risk | Medium |
| Assigned | @codex |

---

## Audit Verdict

> The canonical `develop` branch still carries invalid lint suppressions and broad unresolved Ruff debt. Exact active-file evidence from the 2026-04-01 review:
>
> - [tests/conftest.py](/home/gestalt/Desktop/solstein/solstein/tests/conftest.py) used `# noqa: lazy-import` on deferred imports.
> - [tests/unit/test_behavioral_contracts.py](/home/gestalt/Desktop/solstein/solstein/tests/unit/test_behavioral_contracts.py) used the same invalid `# noqa: lazy-import` pattern.
> - [src/solstein/api/routers/scoring.py](/home/gestalt/Desktop/solstein/solstein/src/solstein/api/routers/scoring.py) used `# noqa: broad-except` on active API exception handlers.
> - [scripts/ci/agent_precommit_hook.py](/home/gestalt/Desktop/solstein/solstein/scripts/ci/agent_precommit_hook.py) used invalid `# noqa: broad-except` labels inside the quality hook itself.
>
> After correcting that suppression noise in a bounded branch pass, `ruff check . --output-format concise` reported `260` repo-wide errors on `develop`. A second bounded cleanup pass made `scripts/ci/` Ruff-clean and reduced the repo-wide count to `207`. The problem is not "missing one config tweak"; the problem is that lint-signal integrity and actual debt have to be separated and then burned down in owned slices.

---

## Problem Statement

The repository cannot truthfully claim "ruff clean" or rely on existing CI/pre-commit quality gates while active files contain invalid suppressions and the canonical branch still has hundreds of real lint failures. Until the signal is trustworthy, backlog claims about quality gates and clean enforcement are overstated and remediation work will continue to drift toward broad ignores or compatibility-style patching.

---

## Impact

| Dimension | Effect |
|-----------|--------|
| **Quality** | Lint output contains tool-noise and real debt together, making regressions harder to isolate |
| **Reliability** | Developers may interpret invalid suppressions as accepted policy, weakening future guardrails |
| **Maintainability** | Broad ignore expansion becomes tempting when the actual issue is unowned debt on `develop` |
| **Velocity** | CI and local hooks cannot serve as trustworthy go/no-go signals until suppression hygiene is repaired |

---

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|------------------|
| [tests/conftest.py](/home/gestalt/Desktop/solstein/solstein/tests/conftest.py) | Modify | Replace invalid suppression labels with valid rule codes on lazy imports |
| [tests/unit/test_behavioral_contracts.py](/home/gestalt/Desktop/solstein/solstein/tests/unit/test_behavioral_contracts.py) | Modify | Replace invalid suppression labels and keep file Ruff-clean |
| [src/solstein/api/routers/scoring.py](/home/gestalt/Desktop/solstein/solstein/src/solstein/api/routers/scoring.py) | Modify | Replace invalid broad-except suppressions with recognized rule codes |
| [scripts/ci/agent_precommit_hook.py](/home/gestalt/Desktop/solstein/solstein/scripts/ci/agent_precommit_hook.py) | Modify | Make the local gate itself lint-valid |
| [pyproject.toml](/home/gestalt/Desktop/solstein/solstein/pyproject.toml) | Review only | Do not add new global ignores without current-file evidence |
| `planning/QUEUE.md` | Modify | Queue the bounded develop-side lint-signal remediation work explicitly |

---

## Dependencies

### Hard Dependencies (Must Complete First)
- None

### Soft Dependencies (Preferred Order)
- [STORY-061](STORY-061-ci-pipeline-quality-gates.md) — CI should enforce trustworthy lint signal, not noisy or invalid suppressions
- [STORY-062](STORY-062-pre-commit-hooks.md) — local hooks should use valid, machine-recognized suppressions

---

## Architectural Requirements

- **REQ-1**: All lint suppressions added or retained in current `develop` paths must use valid Ruff rule codes.
- **REQ-2**: No new global ignore entries or per-file ignores may be added without current-file failing evidence and explicit backlog justification.
- **REQ-3**: Lint remediation must proceed in bounded, subsystem-owned slices on canonical `develop`, not by replaying `master` lint commits wholesale.
- **REQ-4**: Backlog and queue artifacts must stop claiming "ruff clean" for the repository until a verified full-branch run demonstrates it.

---

## Acceptance Criteria

- [ ] Invalid suppression labels are removed or replaced with valid Ruff rule codes in the active files identified above.
- [ ] `ruff check` passes on the touched files without introducing new global ignore entries.
- [ ] Repo-wide Ruff output is re-run and recorded as remaining debt, not silently hidden.
- [ ] A follow-up slice plan exists for the next bounded subsystem cleanup on `develop`.
- [ ] Backlog and queue references reflect the current lint state instead of stale "ruff clean" assumptions.

---

## Definition of Done

### Tests Required
- [ ] Run `ruff check` on all files modified by this story.
- [ ] Run one repo-wide `ruff check .` pass and record the remaining error count in story notes or linked audit artifacts.

### Documentation Required
- [ ] Update EPIC-018 story notes with current-file evidence.
- [ ] Update `planning/QUEUE.md` with this story's status and current branch note.

### Code Review Gate
- [ ] Reviewer confirms no new broad ignore expansion was added to `pyproject.toml`.
- [ ] Reviewer confirms suppression changes use actual Ruff rule IDs.
- [ ] Reviewer confirms remaining debt is documented explicitly rather than hidden.

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Broad lint cleanup accidentally expands scope into formatting churn | Medium | Medium | Keep this story limited to suppression hygiene and the next explicitly queued slice |
| Team interprets one clean touched-file run as full repository cleanliness | Medium | High | Record repo-wide Ruff count explicitly in backlog notes and queue |
| Global ignore expansion masks real defects | Medium | High | Require current-file evidence before any config change |

---

## Notes

Current implementation evidence exists on branch `work/develop-lint-gate-signal-2026-04-01`, starting at commit `abd3761a`, which repaired the invalid suppressions in the four active files above and proved that the remaining problem is real repo debt rather than invalid-rule noise.

The same branch then completed a bounded `scripts/ci/` cleanup slice:

- `ruff check scripts/ci --output-format concise` now passes.
- Repo-wide Ruff count dropped from `260` to `207`.
- No new global ignores or per-file ignore expansions were added to [pyproject.toml](/home/gestalt/Desktop/solstein/solstein/pyproject.toml).

The next bounded candidate slices have been planned explicitly and queued as follow-up stories:

| Story | Scope | Errors | Notes |
|-------|-------|--------|-------|
| [STORY-273](STORY-273-ruff-slice-scripts-legacy.md) | `scripts/` (non-ci) | 168 | 166 auto-fixable; 1 manual SIM201 |
| [STORY-274](STORY-274-ruff-slice-alembic-versions.md) | `alembic/versions/` | 21 | All auto-fixable |
| [STORY-275](STORY-275-ruff-slice-tooling-and-bin.md) | `.claude/`, `tests/unit/`, `bin/`, `src/research/` | 18 | 3 × E722 manual; SIM115 manual |

Completing STORY-273 + STORY-274 + STORY-275 in sequence will bring `ruff check .` to 0 errors on `develop` without any new global ignore expansions.

This story is intentionally the opposite of a compatibility patch. It improves the trustworthiness of the current canonical branch and creates a defensible baseline for future bounded cleanup slices.

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-04-01 | @codex | Created from develop-side lint gate remediation pass and queue/backlog evidence update |
| 2026-04-01 | @codex | Added scripts/ci bounded cleanup result: subsystem Ruff-clean, repo-wide Ruff count 260 -> 207 |
| 2026-04-01 | @gestalt | Added follow-up slice plan (STORY-273/274/275); satisfied AC "follow-up slice plan exists" |
