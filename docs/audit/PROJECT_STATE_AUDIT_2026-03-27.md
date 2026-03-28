# PROJECT STATE AUDIT - Solstein - 2026-03-27

## Scope

This audit reviews the current local repository state on `master`, the fetched remote state on `origin/develop`, and the newly published branch `origin/feature/STORY-181-fix-report-path-nesting`.

This is a project-state audit, not a full line-by-line code audit. The goal is to answer:

1. What changed upstream?
2. Is the fetched state materially healthier or riskier?
3. What is verifiably working?
4. What concrete issues still need action?

## Local Repository State

- Local branch: `master`
- Remote tracking branch: `origin/master`
- Pull result on 2026-03-27: `Already up to date`
- Local branch divergence from `origin/master`: `0 ahead / 0 behind`

Dirty local worktree items were present before this audit and were left untouched:

- Modified: `docs/sessions/DEV_LOG_2026-03.md`
- Untracked: `backlog/EPICS/EPIC-067-agentic-development-workflow-hardening/`
- Untracked: `docs/active/backlog/EPIC-067-agentic-development-workflow-hardening/`
- Untracked: `docs/audit/AGENTIC_WORKFLOW_BACKLOG_REVIEW_2026-03-27.md`

## Remote Branch State

Fetched remote state showed no new commits on `master`, but meaningful movement on other branches:

- `origin/master` -> `58bef0e` `audit: append recursive structural findings`
- `origin/develop` -> `bf4f6a2` `Housekeeping: Work checker run [2026-03-28 11:00]`
- `origin/feature/STORY-181-fix-report-path-nesting` -> `4d60a08` `STORY-181: Fix report output path nesting and clean filenames`

Recent upstream history:

- `bf4f6a2` `Housekeeping: Work checker run [2026-03-28 11:00]`
- `ae99049` `Housekeeping: Mark STORY-181 as DONE (PR #161), STORY-182 as IN_PROGRESS`
- `4d60a08` `STORY-181: Fix report output path nesting and clean filenames`
- `480bace` merge of PR #160 for STORY-180 field-mapping parity

## Delta Summary

Relative to local `master`, `origin/develop` introduces:

- `661` files changed
- `52,053` insertions
- `7,775` deletions

Relative to local `master`, the Story 181 feature branch introduces:

- `670` files changed
- `52,540` insertions
- `7,803` deletions

The Story 181 branch is effectively `develop` plus the report-path fix and related housekeeping.

Highest-change directories in `master..origin/develop` by file share:

- `tests/unit/` -> `15.7%`
- `docs/agent-cycles/2026-03-27/` -> `4.6%`
- `src/solstein/data/` -> `3.1%`
- `src/solstein/research/` -> `2.8%`
- `src/solstein/intelligence/` -> `2.8%`
- `src/solstein/infrastructure/` -> `2.8%`
- `src/solstein/api/routers/` -> `2.4%`
- `src/solstein/llm/` -> `1.9%`

Interpretation: this is not a narrow patch set. It is a broad platform expansion with a very large amount of accompanying test and documentation churn.

## What Upstream Adds

The fetched upstream state contains substantial new or expanded capability in these areas:

- Multi-tenancy and API key handling
  - new tenant migrations
  - tenant services and isolation helpers
- Semantic search / embeddings
  - pgvector migration and vector-store related code
- Research graph and checkpointing
  - graph topology, node modules, checkpoint DB defaults
- Async export and job tracking
  - export status fields, async export API docs, worker export tasks
- Worker reliability
  - DLQ support, idempotency support, tenant-isolated worker paths
- CI / engineering guardrails
  - new scripts under `scripts/ci/`
  - stronger Makefile target surface
  - expanded test inventory

## Verification Performed

Verification was run in temporary detached worktrees so the dirty local `master` checkout was not modified.

### Verified on `origin/develop`

- Python bytecode compilation:
  - `python -m compileall -q src/solstein`
  - Result: passed

- Focused regression slice:
  - `tests/unit/test_story180_field_mapping_parity.py`
  - `tests/unit/test_loader_parity.py`
  - `tests/unit/test_story097_migrations.py`
  - `tests/unit/test_story098_makefile_targets.py`
  - `tests/test_pgvector_schema.py`
  - Result: `86 passed`

### Verified on `origin/feature/STORY-181-fix-report-path-nesting`

- Story-specific regression slice:
  - `tests/unit/test_report_paths.py`
  - Result: `6 passed`

- Ruff on Story 181 touched files:
  - `src/solstein/exporters/markdown/client.py`
  - `src/solstein/exporters/markdown/company.py`
  - `src/solstein/exporters/markdown/report_strategies/base.py`
  - `tests/unit/test_report_paths.py`
  - Result: passed

## Findings

### 1. Broken developer workflow targets: Makefile still assumes a missing `dashboard/` directory

Severity: High

Evidence:

- `Makefile:20` -> `cd dashboard && npm install`
- `Makefile:28` -> `cd dashboard && npm run dev`
- `Makefile:38` -> `cd dashboard && npm run lint`
- `Makefile:74-75` remove dashboard build directories

The repository root in the audited upstream tree does not contain a `dashboard/` directory. Direct execution confirmed:

- `make dashboard` fails with `/bin/sh: 1: cd: can't cd to dashboard`

Impact:

- `make dashboard` is broken
- `make install` is broken unless the dashboard is restored
- `make lint` is broken unless the dashboard is restored
- the documented local developer path is misleading

This is a real usability failure, not a theoretical mismatch.

### 2. Runtime checkpoint databases are tracked in git

Severity: High

Tracked upstream files include:

- `data/checkpoints/research_graph.db`
- `data/checkpoints/review_queue.db`

The codebase also uses these as runtime defaults:

- `src/solstein/config.py:294`
- `src/solstein/config.py:314`
- `src/solstein/research/graph/checkpointer.py:15`
- `src/solstein/review_queue/store.py:76`

No ignore rule was found for these DB artifacts during the audit search.

Impact:

- binary runtime state is being versioned
- merges can accumulate stale or machine-specific state
- repository cleanliness and reproducibility degrade
- checkpoint behavior can become coupled to committed artifact contents rather than deterministic bootstrap

This is especially risky because these are not static fixtures; they are operational state containers.

### 3. Documentation portability is badly degraded by hard-coded absolute local paths

Severity: Medium

Evidence:

- `306` markdown files exist under `docs/agent-cycles/`
- `502` absolute path string matches were found across `310` markdown files in `docs/`
- Examples:
  - `docs/agent-cycles/2026-03-27/cycle-016.md:51`
  - `docs/agent-cycles/2026-03-27/cycle-037.md:51`
  - `docs/internal/AGENT_DEPLOYMENT_GUIDE.md:31`
  - `docs/internal/AGENT_DEPLOYMENT_GUIDE.md:241`
  - `docs/internal/AGENT_DEPLOYMENT_GUIDE.md:250`

Observed path patterns:

- `/home/ai-whisperers/solstein`
- `/home/ai-whisperers/Documents/Work/solstein`

Impact:

- docs are not portable across environments
- operator runbooks are partially user-machine specific
- generated cycle logs are introducing long-term documentation noise

This is not a blocker to runtime correctness, but it is a project-health problem and increases drift.

### 4. `origin/develop` is not lint-clean

Severity: Medium

Ruff fails on:

- `src/solstein/infrastructure/models/__init__.py:15`

Failure type:

- `I001` import block unsorted / unformatted

Impact:

- engineering gate is red on at least one file
- repository quality claims are stronger than the current verified state

This is a straightforward fix, but it matters because the project now carries strong CI/quality posture messaging.

## Story 181 Assessment

The Story 181 branch looks focused and healthy on the specific issue it addresses.

Confirmed behavior from branch metadata and tests:

- cleans report output filenames so files are not redundantly company-prefixed inside company-named directories
- adds `generate_company_reports()` on `CompanyReportGenerator`
- removes dead stub logic in `client.py`
- removes a broken `_check_data_authenticity` call
- adds focused regression coverage

Verification result:

- `tests/unit/test_report_paths.py` -> `6 passed`
- touched files pass Ruff

Conclusion:

- Story 181 itself appears sound
- the branch should be evaluated as `develop + small targeted fix`, not as an isolated patch against current `master`

## Positive Signals

Despite the findings above, the upstream state has several positive signals:

- substantial test growth rather than feature-only churn
- new migrations and tests for tenant, auth, pgvector, export, observability, and worker behavior
- focused verification slice passed cleanly on `develop`
- Story 181 has direct regression coverage and lint-clean touched files
- upstream queueing discipline is visible in `planning/QUEUE.md`

## Overall Assessment

Current local `master` is stable but behind the real active line of development.

`origin/develop` represents a significantly expanded platform state and is not obviously broken at the core level, but it is not clean enough to treat as production-ready without follow-up. The biggest practical issues found in this audit are:

1. broken Makefile/dashboard workflow
2. committed runtime checkpoint databases
3. heavy documentation path leakage
4. at least one failing lint gate

The upstream direction is productive, but repository hygiene and operational cleanliness are lagging behind feature and test velocity.

## Recommended Next Actions

1. Remove or gate the `dashboard` Make targets until the frontend actually exists again.
2. Stop tracking runtime checkpoint DB files and replace them with bootstrap creation logic plus ignore rules.
3. Normalize generated docs to repo-relative paths.
4. Fix the Ruff violation in `src/solstein/infrastructure/models/__init__.py`.
5. Before merging `develop` into `master`, run a broader gate than the focused slice used here:
   - lint
   - critical test gate
   - migration verification
   - a docs build pass

## Audit Method

This audit used:

- `git fetch origin`
- branch / divergence inspection
- diff statistics against `origin/develop` and Story 181
- temporary detached worktrees for verification
- targeted pytest runs
- Ruff on representative touched areas
- repository searches for portability, artifact tracking, and workflow mismatches

No pre-existing local changes were reverted or modified.
