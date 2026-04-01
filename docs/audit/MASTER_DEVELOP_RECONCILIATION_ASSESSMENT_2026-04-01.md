# Master vs Develop Reconciliation Assessment

> **Date**: 2026-04-01
> **Assessed Branches**: `origin/master` vs `origin/develop`
> **Assessment Branch**: `reconcile/master-into-develop-2026-04-01`
> **Method**: `git fetch --all --prune`, remote divergence review, non-committing merge trial of `origin/master` into `develop`

---

## Executive Verdict

`master` and `develop` are **not fully synced** and should be treated as **structurally divergent** branches rather than near-neighbors.

Remote divergence at assessment time:

- `origin/master`: 7 commits not in `origin/develop`
- `origin/develop`: 611 commits not in `origin/master`

The attempted merge of `origin/master` into `develop` did **not** merge cleanly. It produced widespread conflicts across docs/backlog, runtime/auth/config, connectors, analytics, workers, and tests. This is a reconciliation program, not a routine merge.

---

## Exact Heads

- `origin/master`: `2fcea1637570c48b6f690e2c919dedfd4ccc5ce7`
- `origin/develop`: `68fe6455680ecc1ce2f0fb0f2764c38706457684`

---

## Master-Only Commits

The 7 commits unique to `master` at assessment time were:

1. `2fcea163` `docs(audit): add runtime depth and duplication ledger`
2. `16f6a5d9` `docs(backlog): add source-backed runtime evidence anchors`
3. `2de351ab` `docs(backlog): add consolidation-first runtime remediation program`
4. `80583cd8` `docs: add comprehensive update plan`
5. `01f94def` `fix: M0 emergency — add missing jwt.py shim, fix conftest env vars, correct classification thresholds`
6. `08be3278` `docs: add comprehensive audit report, action plan, and M0 emergency milestone`
7. `755eab6c` `chore(lint): enforce full ruff compliance on master`

### Interpretation

- The `master`-only set is small, but it is not purely documentation.
- `01f94def` and `755eab6c` indicate `master` still carries code and lint changes that must be reviewed before any branch retirement or forced sync.
- Several documentation/backlog changes from `master` have already been reintroduced or superseded in different form on `develop`, which is part of why merge conflicts appear despite apparent topical overlap.

---

## Develop-Only Direction

`develop` contains the active evolution of the project, including:

- backlog and planning reorganization
- runtime-canonicalization story work
- strict boundary schema work
- export schema reconciliation
- test collection and CI fixes
- security and dependency updates
- adapter retirement and canonicalization changes
- major docs topology cleanup

This means any sync strategy should treat `develop` as the forward-moving integration branch and reconcile `master` into it intentionally.

---

## Merge Trial Result

Command used:

```bash
git merge --no-commit --no-ff origin/master
```

Result:

- merge failed with many conflicts
- merge was aborted after assessment

### Representative Conflict Areas

#### Backlog / planning / audit

- `backlog/EPICS/EPIC-067-legacy-runtime-canonicalization/STORIES/STORY-255-freeze-graph-runtime-and-declare-legacy-canonical.md`
- `docs/audit/VALIDATION_SCHEMA_STRICTNESS_AUDIT_2026-03-31.md`
- `planning/QUEUE.md`

#### Configuration / auth / middleware

- `pyproject.toml`
- `src/solstein/api/dependencies.py`
- `src/solstein/api/middleware/security.py`
- `src/solstein/api/routers/auth.py`
- `src/solstein/security/auth.py`
- `tests/conftest.py`

#### Runtime / connectors / agents

- `src/solstein/agents/github/client.py`
- `src/solstein/agents/web_search_agent.py`
- `src/solstein/connectors/base.py`
- `src/solstein/connectors/financial/__init__.py`
- `src/solstein/connectors/government/__init__.py`
- `src/solstein/connectors/product/__init__.py`
- `src/solstein/connectors/product/npm.py`
- `src/solstein/connectors/social/__init__.py`
- `src/solstein/data/connectors/news_signal_detector.py`

#### Analytics / scoring / data contracts

- `src/solstein/analytics/scorers/growth_momentum.py`
- `src/solstein/api/schemas/validation.py`
- `src/solstein/data/safe_defaults.py`
- `src/solstein/infrastructure/models/company.py`
- `src/solstein/infrastructure/models/infrastructure.py`
- `src/solstein/infrastructure/models/research.py`
- `src/solstein/research/ai_research_orchestrator.py`

#### Tests

- `tests/unit/test_classification_service.py`
- `tests/unit/test_data_quality_extended.py`
- `tests/unit/test_error_envelope.py`
- `tests/unit/test_error_taxonomy.py`
- `tests/unit/test_exporter_snapshots.py`
- `tests/unit/test_golden_dataset_story_205.py`
- `tests/unit/test_observability/test_exceptions.py`
- `tests/unit/test_scoring_constants.py`
- `tests/unit/test_scoring_deduplication.py`
- `tests/unit/test_synthetic_data_safety.py`

#### Modify/delete conflicts

- `src/solstein/api/routes/refresh.py`
- `src/solstein/data/eneve_enrichment.py`
- `src/solstein/llm/usage_tracker.py`

### Assessment

This conflict spread is strong evidence that the branch gap is architectural and organizational, not just chronological.

---

## Recommended Reconciliation Strategy

1. Treat `develop` as the target branch for reconciliation.
2. Isolate the 7 `master`-only commits into categories:
   - docs-only
   - lint-only
   - code/runtime relevant
3. Cherry-pick or reimplement the genuinely missing code fixes first:
   - especially the JWT/conftest/classification fix in `01f94def`
   - and any safe lint/config improvements from `755eab6c`
4. Do not perform a blind full merge from `master` into `develop`.
5. Once the unique `master` fixes are ported intentionally, reassess whether `master` should:
   - be fast-forwarded from `develop`,
   - be merged with a narrow curated merge,
   - or be retired as the primary release branch in favor of a cleaner release flow.

---

## Immediate Next Actions

- Review `01f94def` file-by-file and decide which changes are still missing on `develop`.
- Review `755eab6c` for any strict lint/config adjustments still worth porting.
- Do not start a broad merge until those two code-bearing commits are understood and either ported or superseded.
- Keep this branch as the audit branch for any future reconciliation notes or cherry-pick plan.
