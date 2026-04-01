# Master-Only Cherry-Pick / Port Plan

Date: 2026-04-01
Branch: `reconcile/master-into-develop-2026-04-01`
Reference assessment: `docs/audit/MASTER_DEVELOP_RECONCILIATION_ASSESSMENT_2026-04-01.md`

## Purpose

This document converts the `origin/master` vs `origin/develop` divergence into an execution plan. It is not a generic merge note. It is the concrete reference for deciding which `master`-only commits should be:

- rejected for direct cherry-pick,
- ported manually file by file,
- or treated as already absorbed by `develop`.

The goal is to avoid another compatibility-patch wave while preserving any genuinely missing production fixes.

## Verified Remote State

At review time:

- `origin/master`: `2fcea1637570c48b6f690e2c919dedfd4ccc5ce7`
- `origin/develop`: `68fe6455680ecc1ce2f0fb0f2764c38706457684`
- Divergence from `git rev-list --left-right --count origin/master...origin/develop`: `7 611`

Interpretation:

- `master` has 7 commits not present on `develop`
- `develop` has 611 commits not present on `master`

This is not a near-sync condition. It is a deeply divergent history.

## Master-Only Commits

`git log --oneline origin/develop..origin/master`:

1. `2fcea163` `docs(audit): add runtime depth and duplication ledger`
2. `16f6a5d9` `docs(backlog): add source-backed runtime evidence anchors`
3. `2de351ab` `docs(backlog): add consolidation-first runtime remediation program`
4. `80583cd8` `docs: add comprehensive update plan`
5. `01f94def` `fix: M0 emergency — add missing jwt.py shim, fix conftest env vars, correct classification thresholds`
6. `08be3278` `docs: add comprehensive audit report, action plan, and M0 emergency milestone`
7. `755eab6c` `chore(lint): enforce full ruff compliance on master`

## Triage Summary

Recommended handling:

- `2fcea163`, `16f6a5d9`, `2de351ab`, `80583cd8`, `08be3278`: documentation-only inputs; use as references, do not cherry-pick blindly into `develop`
- `01f94def`: do not cherry-pick; the substantive behavior is already present on `develop`
- `755eab6c`: do not cherry-pick whole; review only for small missing deltas and port those manually if still relevant

## Commit Assessment: `01f94def`

Commit title:

- `fix: M0 emergency — add missing jwt.py shim, fix conftest env vars, correct classification thresholds`

Files touched on `master`:

- `src/solstein/analytics/constants.py`
- `src/solstein/security/__init__.py`
- `src/solstein/security/jwt.py`
- `tests/conftest.py`
- `tests/unit/test_classification.py`

### Empirical State On `develop`

The claimed emergency fixes are already materially present on `develop`.

Evidence:

- [src/solstein/security/jwt.py](/home/gestalt/Desktop/solstein/solstein/src/solstein/security/jwt.py) already exists and provides the compatibility shim functions `verify_token(...)` and `create_token(...)`.
- [tests/conftest.py](/home/gestalt/Desktop/solstein/solstein/tests/conftest.py) already sets the expected test environment defaults including `DATABASE__URL`, `SECURITY__SECRET_KEY`, and `COMPANIES_HOUSE_API_KEY`.
- [tests/unit/test_classification.py](/home/gestalt/Desktop/solstein/solstein/tests/unit/test_classification.py) already enforces the `7.0` Phoenix boundary and the `4.49` / `4.5` Lead/Salt boundary.
- [src/solstein/analytics/constants.py](/home/gestalt/Desktop/solstein/solstein/src/solstein/analytics/constants.py) already documents and encodes:
  - `PHOENIX_SCORE_THRESHOLD = 7.0`
  - `SALT_SCORE_THRESHOLD = 4.5`
  - `LEAD_SCORE_THRESHOLD = 4.49`

### Decision

Do not cherry-pick `01f94def`.

### Rationale

- The intended runtime/test behavior is already on `develop`.
- A direct cherry-pick would add conflict risk without adding verified missing functionality.
- If any tiny delta remains, it should be confirmed by direct file diff first, not assumed from commit title.

### Allowed Follow-Up

Only one follow-up is justified:

- run a narrow diff for the five files above before closing the issue, purely to verify there is no unnoticed semantic drift

Absent a newly discovered behavioral delta, this commit should be recorded as already absorbed in substance.

## Commit Assessment: `755eab6c`

Commit title:

- `chore(lint): enforce full ruff compliance on master`

Scale:

- `282 files changed, 1547 insertions(+), 1370 deletions(-)`

This is not a cherry-pick candidate. It is a mixed bulk-formatting and behavior-adjacent cleanup commit.

### Why Direct Cherry-Pick Is Rejected

The commit mixes several categories that must not be transported as one unit into `develop`:

- lint configuration changes in `pyproject.toml`
- broad auto-fix formatting across hundreds of files
- small correctness changes intermixed with style churn
- auth, API, connector, tenant, and test edits across code that has already evolved substantially on `develop`

This is exactly the type of commit that creates silent regressions during branch reconciliation because review signal is buried inside mechanical edits.

### Empirical State On `develop`

Several representative fixes from the lint commit are already present or no longer directly applicable:

- [src/solstein/api/routers/auth.py](/home/gestalt/Desktop/solstein/solstein/src/solstein/api/routers/auth.py) has already moved forward on `develop`; any `master`-side exception chaining cleanup must be re-reviewed in the current auth model, not cherry-picked.
- [src/solstein/evidence/crawler.py](/home/gestalt/Desktop/solstein/solstein/src/solstein/evidence/crawler.py) already reflects cleanup equivalent to the dead `urlparse().netloc` expression removal noted in the `master` lint commit.
- [src/solstein/infrastructure/connectors/funding_refresh.py](/home/gestalt/Desktop/solstein/solstein/src/solstein/infrastructure/connectors/funding_refresh.py) already contains the lambda loop-variable binding pattern associated with the `B023` fix.
- [tests/unit/test_scoring_constants.py](/home/gestalt/Desktop/solstein/solstein/tests/unit/test_scoring_constants.py) already includes substantial follow-on cleanup on `develop`.
- [pyproject.toml](/home/gestalt/Desktop/solstein/solstein/pyproject.toml) already carries many Ruff rules and ignore entries that overlap with `master`, but it is not identical.

### Narrow Deltas Worth Reviewing Manually

The only plausible port candidates are small, reviewable deltas, starting with lint configuration.

Potential candidates:

1. `pyproject.toml`
2. any isolated `from None` exception-chaining improvements that are still missing after direct file comparison
3. per-file Ruff ignores that match current repo structure and current policy

Current observed `pyproject.toml` differences worth review:

- `master` used `target-version = "py312"` while `develop` is still `target-version = "py310"`
- `master` added per-file ignores for:
  - `src/solstein/connectors/**/__init__.py` -> `F401`
  - `tests/factories/__init__.py` -> `F401`
- `master` added ignore entries such as `B028`, `B905`, `F403`, `F405`, `F821`, `SIM105`, `SIM110`, `SIM117`, `N818`, `UP041`, `UP046`, `UP047`, `W293`

These are not auto-approved port items. Each must be validated against:

- the actual Python runtime target for this repository,
- whether the ignore reflects intentional architecture versus technical debt masking,
- whether the file paths still exist and still need the exception.

### Decision

Do not cherry-pick `755eab6c`.

### Manual Port Policy

If anything from `755eab6c` is carried into `develop`, it must be:

- extracted manually,
- applied in a dedicated commit,
- reviewed file by file,
- and justified by current `develop` state rather than by `master` history.

## Execution Plan

The correct execution order is:

1. Treat `develop` as canonical and keep `master` as a source of candidate deltas only.
2. Close out `01f94def` as "already materially present on develop" after a final narrow file diff.
3. Open a focused follow-up review for `755eab6c` limited to:
   - [pyproject.toml](/home/gestalt/Desktop/solstein/solstein/pyproject.toml)
   - current auth/dependency files only if a real exception-chaining gap still exists
   - current connector `__init__` files only if the Ruff exceptions are still structurally justified
4. Port any approved lint/config deltas manually in small commits.
5. Run targeted validation after each manual port instead of bundling changes:
   - `ruff check` on touched files
   - targeted pytest selection for any touched runtime/test files
6. Do not merge `master` into `develop` as a branch-sync shortcut.

## Explicit Non-Goals

This plan explicitly rejects:

- blind cherry-picking of all `master`-only commits
- treating documentation commits as safe merge proof
- importing bulk lint churn to simulate synchronization
- compatibility-patch style reconciliation that hides ownership of the real runtime path

## Practical Recommendation

For reconciliation work, use this document plus the broader assessment in `docs/audit/MASTER_DEVELOP_RECONCILIATION_ASSESSMENT_2026-04-01.md` as the source of truth.

Short version:

- `01f94def`: already absorbed in substance, no cherry-pick
- `755eab6c`: manual extraction only, no cherry-pick
- docs-only `master` commits: reference material, not branch-sync evidence
- `develop` remains the only realistic reconciliation target
