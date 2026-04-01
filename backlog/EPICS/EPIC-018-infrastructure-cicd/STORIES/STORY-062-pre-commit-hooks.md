# STORY-062: Implement Pre-commit Hooks for Local Quality Enforcement

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P1 |
| Severity | MEDIUM |
| Epic | [EPIC-018: Infrastructure-as-Code & CI/CD](../README.md) |
| Created | 2026-02-28 |
| Dependencies | None |

---

## The Audit Verdict
> The AGENTS.md lists manual commands for linting and type checking (`make check-all`), but there is no mechanism that automatically runs these before a commit. Developers must remember to run quality checks manually, and many will not.

## Problem Statement
Manual quality checks that require developer discipline are less reliable than automated hooks. Pre-commit hooks catch issues at the earliest possible point — before they reach the repository — reducing CI pipeline failures and code review friction. Without them, the feedback loop is: write code → push → wait for CI → see failure → fix → push again. With them, the feedback loop is: write code → commit → see failure immediately → fix → commit.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Quality** | Lint and type errors reach the repository because checks are optional — the main branch accumulates quality debt |
| **CI** | CI pipeline time is consumed by failures that could have been caught locally in seconds |
| **Code Review** | Reviewers spend time on formatting issues instead of logic — pre-commit hooks eliminate this waste |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `.pre-commit-config.yaml` | Add | Create at repository root: hook definitions |
| `Makefile` | Modify | Add `make install-hooks` target |

## Architectural Requirements
*What the system must satisfy. No implementation instructions. No code. Only what — never how.*

- **REQ-1**: Pre-commit hooks must run: black (formatting), ruff (linting), mypy (type checking on changed files), and a check for secrets/credentials (`detect-secrets` or equivalent)
- **REQ-2**: Hook installation must be documented and automatable — `make install-hooks` must install all hooks
- **REQ-3**: Hooks must run only on changed files to minimise latency — full codebase checks should remain in CI
- **REQ-4**: The secrets detection hook must fail on any committed file containing patterns matching API keys, passwords, or tokens
- **REQ-5**: Hook configuration must be version-controlled in `.pre-commit-config.yaml`

## Acceptance Criteria
- [ ] Attempting to commit a file with a type error is blocked by the pre-commit hook
- [ ] Attempting to commit a file with a linting violation is blocked
- [ ] Attempting to commit a file containing a string matching `AKIA` (AWS key prefix) is blocked
- [ ] `make install-hooks` installs all hooks from a clean clone
- [ ] Hooks run in under 10 seconds for a typical single-file change

## Definition of Done

**Tests Required:**
- [ ] Test each hook independently with a known violation (type error, lint error, embedded secret)
- [ ] Verify hooks run only on changed files (not full codebase)

**Documentation Required:**
- [ ] Pre-commit setup documented in AGENTS.md
- [ ] Pre-commit setup documented in `docs/contributing.md`

**Code Review Gate:**
- [ ] Reviewer confirms all four hook types are present (format, lint, type, secrets)
- [ ] Reviewer confirms hooks run on changed files only

## Notes
This story has no dependencies and can be started immediately — it is one of the earliest-deliverable improvements in the backlog. Pre-commit hooks complement CI (STORY-061) but do not replace it: hooks run on changed files for speed, CI runs on the full codebase for thoroughness. The secrets detection hook is particularly important given the hardcoded credentials found in STORY-007 — preventing future credential commits is as important as removing existing ones.

## 2026-04-01 Empirical Update

The current local guardrails are themselves carrying invalid lint suppressions, so "hook exists" is not the same as "hook signal is trustworthy":

- [scripts/ci/agent_precommit_hook.py](/home/gestalt/Desktop/solstein/solstein/scripts/ci/agent_precommit_hook.py) contained multiple `# noqa: broad-except` directives, which Ruff does not recognize as valid rule suppressions.
- That means the local quality gate can appear cleaner than it is while still accumulating rule-noise and inconsistent enforcement semantics.

This story should now be read together with STORY-272. Before expanding hook coverage, the repository needs valid, machine-recognized suppressions and a bounded plan to reduce current `develop` lint debt without broad ignore-file expansion.
