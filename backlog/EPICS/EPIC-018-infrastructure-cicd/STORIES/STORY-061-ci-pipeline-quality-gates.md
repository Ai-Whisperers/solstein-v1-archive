# STORY-061: Build a CI Pipeline with Automated Quality Gates

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P1 |
| Severity | HIGH |
| Epic | [EPIC-018: Infrastructure-as-Code & CI/CD](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-059: Dockerize Application](STORY-059-dockerize-application.md), [STORY-275](STORY-275-ruff-slice-tooling-and-bin.md) (ruff gate must be clean before wiring CI lint stage) |

---

## The Audit Verdict
> No CI pipeline exists. Changes merged to the main branch are not automatically tested, type-checked, or linted. The test suite can be broken, the type checks can be failing, and the linter can be reporting errors — all without any automated gate preventing the code from being merged or deployed.

## Problem Statement
Without CI, the quality guarantees documented in this backlog (test coverage, type safety, linting compliance) have no enforcement mechanism. Every quality improvement in this backlog is advisory without a CI pipeline to enforce it. An engineer can merge code that breaks every test, introduces type errors, and violates every linting rule — and nothing will stop them except the honour system.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Quality** | Regressions introduced by any commit are undetected until someone manually runs checks — which may never happen |
| **Velocity** | Bugs caught late (in production, by clients) are 10-100x more expensive to fix than bugs caught early (in CI) |
| **Deployment Risk** | Broken code can reach production — every deployment is a gamble |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `.github/workflows/ci.yml` | Add | CI pipeline definition (or equivalent for the CI platform in use) |
| Test, lint, and type check configuration files | Modify | Ensure all quality tools are CI-compatible |

## Architectural Requirements
*What the system must satisfy. No implementation instructions. No code. Only what — never how.*

- **REQ-1**: A CI pipeline must run on every pull request and on every merge to the main branch
- **REQ-2**: The pipeline must include these stages in order: dependency installation → linting (ruff + black) → type checking (mypy --strict) → unit tests → integration tests
- **REQ-3**: Any stage failure must fail the pipeline and block merge
- **REQ-4**: Test results and coverage reports must be published as CI artifacts
- **REQ-5**: The pipeline must run in the Docker image defined in STORY-059 to ensure environment consistency
- **REQ-6**: Pipeline run time must be under 10 minutes for the unit test stage to maintain developer velocity

## Acceptance Criteria
- [ ] A CI pipeline runs on every pull request
- [ ] A linting failure blocks merge
- [ ] A type check failure blocks merge
- [ ] A test failure blocks merge
- [ ] Pipeline completes unit test stage in under 10 minutes
- [ ] Coverage report is published as a CI artifact

## Definition of Done

**Tests Required:**
- [ ] Open a PR with an intentional type error — verify CI fails and blocks merge
- [ ] Open a PR with a failing test — verify CI fails and blocks merge
- [ ] Open a PR with a linting violation — verify CI fails and blocks merge

**Documentation Required:**
- [ ] CI pipeline documented in AGENTS.md (stages, timing, artifact locations)
- [ ] Troubleshooting guide for common CI failures

**Code Review Gate:**
- [ ] Reviewer confirms all quality stages are present and blocking
- [ ] Reviewer confirms the pipeline uses the Docker image for consistency

## Notes
This is the enforcement mechanism for every other quality improvement in this backlog. Without CI, test coverage improvements (EPIC-013), type safety improvements (EPIC-012), and linting standards are all voluntary. This story should be prioritised highly — not because it delivers user-facing value directly, but because it protects every other improvement from regression. The pipeline should use the Docker image from STORY-059 to ensure CI runs in the same environment as production, eliminating "works in CI but not in production" failures.

## 2026-04-01 Empirical Update

Current `develop` evidence shows the CI/lint problem is not theoretical:

- [tests/conftest.py](/home/gestalt/Desktop/solstein/solstein/tests/conftest.py) contained invalid `# noqa: lazy-import` directives at multiple lazy-import boundaries.
- [tests/unit/test_behavioral_contracts.py](/home/gestalt/Desktop/solstein/solstein/tests/unit/test_behavioral_contracts.py) contained the same invalid suppression pattern.
- [src/solstein/api/routers/scoring.py](/home/gestalt/Desktop/solstein/solstein/src/solstein/api/routers/scoring.py) used invalid `# noqa: broad-except` labels on active API error-handling paths.
- [scripts/ci/agent_precommit_hook.py](/home/gestalt/Desktop/solstein/solstein/scripts/ci/agent_precommit_hook.py) used the same invalid `# noqa: broad-except` pattern inside the local gate itself.

As of the 2026-04-01 review, `ruff check . --output-format concise` reports 207 real repo-wide errors on `develop` after removing invalid-suppression noise and cleaning `scripts/ci/`. A three-story burn-down plan (STORY-273 → STORY-274 → STORY-275) will bring this to 0 without new global ignore expansions. This story depends on STORY-275 completing first — the CI lint stage should only be wired once the gate is trustworthy (0 errors).
