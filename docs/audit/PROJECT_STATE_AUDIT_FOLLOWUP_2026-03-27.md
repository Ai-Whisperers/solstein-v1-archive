# PROJECT STATE AUDIT FOLLOW-UP - Solstein - 2026-03-27

## Purpose

This follow-up audit updates `PROJECT_STATE_AUDIT_2026-03-27.md` after `origin/develop` moved again during review.

It records:

- the new remote head
- what changed since the previous audit snapshot
- which earlier findings remain valid
- which earlier findings were resolved
- additional concrete failures found in the latest `develop` state

## State Change Since Prior Audit

At the time of the earlier audit, `origin/develop` was at:

- `bf4f6a2` `Housekeeping: Work checker run [2026-03-28 11:00]`

During this follow-up, `origin/develop` advanced to:

- `3db9c98` `Housekeeping: Work checker run 2026-03-28 11:48 — merged 9 PRs`

The remote feature branch for Story 181 was deleted after merge:

- fetch reported deletion of `origin/feature/STORY-181-fix-report-path-nesting`

Current remote refs observed in this follow-up:

- `origin/master` -> `58bef0e`
- `origin/develop` -> `3db9c98`

## New Upstream Movement

The new `develop` head merged these PRs on top of the earlier reviewed state:

- PR #161 - STORY-181 report path nesting fix
- PR #162 - STORY-182 round score outputs
- PR #163 - STORY-183 fix market classification counters
- PR #164 - STORY-184 signal-based deep analysis
- PR #165 - STORY-185 report quality assertions
- PR #166 - STORY-132 exception handling standards
- PR #167 - STORY-131 null-safety division guards
- PR #168 - STORY-129 classified exceptions in `EnhancedLLMClient`
- PR #169 - STORY-130 structured adapter logging

Representative merge metadata confirms these are targeted report-quality, exception-handling, and adapter-observability changes, not just housekeeping.

## Updated Delta Size

Relative to local `master`, the current `origin/develop` now introduces:

- `686` files changed
- `54,605` insertions
- `7,930` deletions

Highest-change areas remain heavily weighted toward tests and generated docs:

- `tests/unit/` -> `16.3%`
- `docs/agent-cycles/2026-03-27/` -> `5.3%`
- `src/solstein/data/` -> `3.0%`
- `src/solstein/research/` -> `2.7%`
- `src/solstein/intelligence/` -> `2.7%`
- `src/solstein/infrastructure/` -> `2.7%`

## Follow-Up Verification

Verification was performed in a fresh detached worktree at the current `origin/develop` head.

### 1. Targeted story/regression pytest slice

With required test env injected:

- `tests/unit/test_report_paths.py`
- `tests/unit/test_report_score_rounding.py`
- `tests/unit/test_market_classification_counters.py`
- `tests/unit/test_deep_analysis_signals.py`
- `tests/unit/test_report_content_quality.py`
- `tests/unit/test_story131_safe_div.py`
- `tests/unit/test_story129_classified_exceptions.py`
- `tests/unit/test_story130_adapter_logging.py`
- `tests/unit/test_lint_exception_handling.py`

Result:

- `123 passed`
- `1 failed`

Failing test:

- `tests/unit/test_lint_exception_handling.py::TestMain::test_critical_only_mode`

### 2. Focused Ruff pass on the latest touched surfaces

Checked:

- `src/solstein/exporters/markdown`
- `src/solstein/analytics`
- `src/solstein/core`
- `src/solstein/llm`
- `src/solstein/adapters`
- the new story tests listed above

Result:

- failed with `6` findings

### 3. Strict docs build

Command used:

- `mkdocs build --strict -f mkdocs.strict.yml`

Result:

- failed

Blocking warning:

- `src/solstein/worker/base.py:46: No type or annotation for parameter 'db_manager'`

## Findings

### 1. The Makefile/dashboard workflow is still broken

Severity: High

This finding from the prior audit still stands.

Direct execution still fails:

- `make dashboard` -> `/bin/sh: 1: cd: can't cd to dashboard`

Impact:

- `make dashboard` remains broken
- `make install` remains broken because it still does `cd dashboard && npm install`
- `make lint` remains broken because it still does `cd dashboard && npm run lint`

This is still a real workflow failure on the current `develop` head.

### 2. The new exception-handling standards work is not internally green

Severity: High

The latest `develop` head includes STORY-132 exception-handling standards and linting work, but the focused verification slice still fails:

- `tests/unit/test_lint_exception_handling.py::TestMain::test_critical_only_mode`

Observed behavior:

- the lint script printed a violation
- the CLI returned exit code `0`
- the test expected exit code `1`

Root cause from `scripts/lint_exception_handling.py`:

- non-critical files produce `warning` severity for bare `except:` and `except Exception:`
- `main()` only fails on warnings when `--fail-on-warning` is explicitly set

Implication:

- the script behavior and the shipped test expectation disagree
- the new policy tooling is not in a self-consistent state

This is more important than a single failing test because the story was specifically about standards and enforcement.

### 3. The latest adapter/logging work introduced fresh Ruff failures

Severity: Medium

The previous audit's Ruff issue in `src/solstein/infrastructure/models/__init__.py` is resolved. However, the latest `develop` head is still not lint-clean.

Fresh Ruff findings include:

- `src/solstein/adapters/discovery/competitor_json.py`
  - unsorted imports
  - unused `loguru.logger`
- `src/solstein/adapters/discovery/web_search.py`
  - unused `loguru.logger`
- `src/solstein/adapters/enrichment/patents_unified.py`
  - unsorted imports
- `tests/unit/test_story129_classified_exceptions.py`
  - unsorted imports
- `tests/unit/test_story131_safe_div.py`
  - unused `math`

Impact:

- the repo is still not lint-clean even after the earlier lint issue was fixed
- the newest merged PRs are contributing quality-gate failures immediately

### 4. Strict docs build currently fails on API-reference generation

Severity: Medium

`mkdocs build --strict -f mkdocs.strict.yml` aborts with warnings in strict mode.

Concrete blocking warning:

- `src/solstein/worker/base.py:46: No type or annotation for parameter 'db_manager'`

Impact:

- the strict docs gate is currently red
- published engineering-reference claims are ahead of the current verified state

This matters because the repo now includes explicit documentation and standards posture work.

### 5. Import-time settings loading makes pure unit-test collection fragile

Severity: Medium

The first pytest attempt on the current `develop` head failed during test collection until a fake `DATABASE__URL` was injected.

Observed import chain:

- `src/solstein/exporters/__init__.py` imports `.llm`
- `src/solstein/llm/__init__.py` imports `.enhanced_client`
- `src/solstein/llm/fallback.py` imports `CircuitBreaker` from `agents.resilience`
- `src/solstein/agents/resilience.py` builds retry configs at module import time
- `src/solstein/agents/resilience.py:311` calls `get_settings()`
- `src/solstein/agents/resilience.py:337` executes `_build_retry_configs()` at module scope

Impact:

- importing exporters / llm / adapters can require full settings validation
- nominally isolated unit tests become environment-sensitive at collection time
- import-time side effects increase coupling and reduce test ergonomics

The issue is not that tests need env vars in general. The issue is that a module-level import path is forcing settings validation long before runtime behavior needs it.

### 6. Runtime checkpoint DB artifacts are still tracked in git

Severity: High

This finding from the prior audit still stands.

Tracked files remain:

- `data/checkpoints/research_graph.db`
- `data/checkpoints/review_queue.db`

These are still referenced as runtime defaults in config and store/checkpointer code.

### 7. Documentation path leakage is still widespread

Severity: Medium

This finding from the prior audit still stands.

The docs tree still contains hundreds of absolute path references under:

- `/home/ai-whisperers/solstein`
- `/home/ai-whisperers/Documents/Work/solstein`

The current `develop` tree still carries:

- `306` markdown files under `docs/agent-cycles/`
- `502` absolute-path matches across `310` markdown files in `docs/`

## Resolved Since Prior Audit

One prior concrete finding is now resolved on the current `develop` head:

- the Ruff import-ordering failure in `src/solstein/infrastructure/models/__init__.py` no longer reproduces

This is a real improvement, but it was replaced by new lint issues in the latest merged story surfaces.

## Current Assessment

The current `origin/develop` head is better than the earlier snapshot in one respect:

- the previous `infrastructure/models/__init__.py` lint failure was fixed

However, the latest upstream movement also added fresh quality problems:

- one failing policy/lint test
- fresh Ruff failures in newly merged files
- a red strict-docs build
- continued import-time configuration coupling

The overall trajectory is still productive, but the project remains in a state where feature and standards work are landing faster than the repository is being kept green.

## Recommended Next Actions

1. Fix `scripts/lint_exception_handling.py` or the corresponding test so the policy tool and the test suite agree on exit semantics.
2. Clean the new Ruff findings in adapter/story files before claiming the latest develop head is gate-clean.
3. Fix the strict docs warning in `src/solstein/worker/base.py` and rerun the docs build.
4. Remove import-time settings resolution from `src/solstein/agents/resilience.py`; build retry configs lazily or behind a function call.
5. Remove or gate `dashboard` Makefile targets until the frontend actually exists again.
6. Stop tracking runtime checkpoint DB files.
7. Continue path normalization work for generated docs and runbooks.

## Method

This follow-up used:

- a fresh `git fetch origin`
- a fresh detached worktree at the current `origin/develop`
- merge-history inspection
- focused pytest verification
- focused Ruff verification
- strict MkDocs build verification
- targeted source inspection of the failing policy/lint and import-time config paths

No existing local user changes were reverted or modified.

## Addendum - Commit/Push Summary

This follow-up review should be treated as the current audit snapshot for the remote state observed on 2026-03-27.

Key update over the prior audit:

- `origin/develop` advanced again to `3db9c98`
- the previous Ruff failure in `src/solstein/infrastructure/models/__init__.py` no longer reproduces
- the repo is still not merge-clean because fresh gate failures replaced it

Current high-signal conclusions:

1. `make dashboard`, `make install`, and `make lint` remain broken because `dashboard/` is still absent.
2. STORY-132 exception-handling enforcement is inconsistent because the lint CLI returns success for warning-only findings while the shipped test expects failure.
3. Current `develop` is still not gate-clean:
   - focused pytest slice: `123 passed, 1 failed`
   - focused Ruff slice: `6` findings
   - strict docs build: failed
4. Import-time settings resolution in `src/solstein/agents/resilience.py` still makes test collection environment-sensitive.
5. Tracked runtime checkpoint databases and absolute-path-heavy generated docs are still open repository-health issues.

If this audit is committed, it should be committed together with `PROJECT_STATE_AUDIT_2026-03-27.md` so the cross-reference in this file remains valid.
