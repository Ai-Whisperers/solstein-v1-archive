# Solstein Repo Cleanup + Organization Plan

## TL;DR
> Reorganize the repo to reduce cognitive load and reach release-readiness by (1) fixing CI/tooling papercuts, (2) cleaning docs information architecture, (3) quarantining non-product content, and (4) clarifying backend layers with Clean Architecture while preserving compatibility via import shims and doc redirects.

**Deliverables**:
- A navigable, professional repo layout with explicit ownership boundaries.
- Clean Architecture-aligned backend structure (domain/application/infrastructure/presentation) with compatibility shims.
- Curated docs IA (mkdocs nav) + quarantined archive/proposal content with minimal broken links.
- Release-readiness gates: install, lint, typecheck, tests, docs build, package build, CI green.

**Effort**: Large
**Parallel Execution**: YES (4 waves + final verification)
**Critical Path**: CI P0 fixes 9 Layer map+compat policy 9 Module de-duplication 9 Docs IA link/redirect integrity 9 Final verification

---

## Context

### Original Request
Analyze the repo and plan cleaning/organizing to reduce cognitive load, be professional/release-ready, clean docs IA, and clarify layers.

### Confirmed Decisions
- **Primary objective**: contributor UX + release readiness + docs IA + clear layering.
- **Allowed changes**: moves + redirects/compat where possible.
- **Non-product content**: keep but quarantine (archive/examples) and exclude from primary docs navigation.
- **Backend target**: Clean Architecture.
- **Test strategy**: YES (TDD).

### Key Findings (evidence-backed)
- Major duplication/ambiguity: `src/solstein/application/` mirrors `src/solstein/*` modules (agents/analytics/exporters).
- Docs are present but not surfaced: mkdocs nav currently shows only `docs/index.md` + `docs/LORE/*` + `docs/PITCH/*`; guides/reference/architecture exist but are excluded.
- Release-readiness papercuts likely break CI: missing `test` extra mismatch; coverage target likely incorrect; duplicate version sources; orphaned Azure pipeline files.

---

## Work Objectives

### Core Objectives
- Make repo navigation intuitive: clear boundaries, consistent naming, obvious "where to put things".
- Make release readiness verifiable: CI green + deterministic local commands.
- Make docs usable: curated IA, minimal broken links, quarantined historical content.
- Make backend layering explicit: enforce dependency direction and remove duplicated/conflicting implementations.

### Guardrails (anti-scope-creep)
- No intentional behavior changes unless explicitly required for moves/shims; keep refactors mechanical.
- Preserve compatibility for moved modules via shims/re-exports (or document breaking changes explicitly).
- Quarantined content must be excluded from packaging/tests/typechecks/docs nav.

---

## Verification Strategy (MANDATORY)

### Test Decision
- **Infrastructure exists**: YES (pytest + coverage).
- **Automated tests**: YES (TDD).
- **Framework**: pytest.

### Quality Gates (must pass)
- Install: `pip install -e ".[dev,test]"` (or updated equivalent) in a clean env
- Lint: `ruff check src/ tests/`
- Format: `ruff format --check src/ tests/`
- Typecheck: `mypy src/`
- Tests: `pytest tests/` (plus any added checks)
- Docs: `mkdocs build` (prefer `--strict` if feasible)
- Package build: `python -m build` (sdist + wheel)

### QA Policy
Every task includes agent-executed QA scenarios with concrete commands and evidence outputs stored in `.sisyphus/evidence/`.

---

## Execution Strategy

### Parallel Execution Waves (high-level)

Wave 1 (Release-readiness + baseline contracts)
- CI/pip extras + coverage correctness + version source
- Define compat policy for moves (imports + docs)
- Docs nav quick-win (surface guides/reference/architecture)

Wave 2 (Docs IA + quarantine non-product)
- Restructure docs into curated sections; quarantine archive/proposal/plans
- Consolidate/relocate CI/CD docs and templates into quarantined areas

Wave 3 (Backend layering + de-duplication)
- Establish layer map; migrate modules into proper layers
- Replace duplicates with canonical implementation + shims

Wave 4 (Repo hygiene)
- Clarify tooling dirs (`opencode/`, `validation/`, `.antigravity/`, `.sisyphus/`) and add minimal READMEs
- Make generated artifacts boundaries explicit (`reports/`, data)

---

## TODOs

- [ ] 1. Baseline Contract: Public Surface + Compatibility Policy

  **What to do**:
  - Inventory the repo's "public surface": import paths expected to remain stable, CLI entrypoints, documented docs URLs.
  - Write a short compatibility policy describing:
    - import shims/re-exports expectations for moved modules
    - doc redirect/link policy for moved docs
    - deprecation window (default: keep shims for at least 1 minor release)
  - Add a short "where things live" map aligned to Clean Architecture.

  **Must NOT do**:
  - Do not redesign business logic; this is structure + policy only.

  **Recommended Agent Profile**:
  - **Category**: `writing`
  - **Skills**: `code-quality/codebase-documenter`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: Tasks 6-18 (provides shared rules)
  - **Blocked By**: None

  **References**:
  - `README.md` - current architecture overview and onboarding expectations
  - `pyproject.toml` - current packaging surface and dependency constraints
  - `src/solstein/cli.py` - current CLI module (even if not registered yet)
  - `mkdocs.yml` - docs navigation and implied "public" docs surface

  **Acceptance Criteria**:
  - [ ] A single policy doc exists and is linked from `README.md` or `docs/index.md`
  - [ ] Policy includes explicit rules for import shims + doc redirects

  **QA Scenarios**:
  ```
  Scenario: Policy doc is discoverable
    Tool: Bash
    Steps:
      1. Verify the policy doc path exists
      2. Verify `README.md` or `docs/index.md` links to it
    Expected Result: Link present and points to an existing file
    Evidence: .sisyphus/evidence/task-1-policy-discoverable.txt
  ```

- [ ] 2. Fix CI Install Extras + Docs Cache Path (Release-Readiness P0)

  **What to do**:
  - Make CI install step consistent with `pyproject.toml` extras:
    - Either add a `test` extra in `pyproject.toml` or update CI to install only `.[dev]`.
    - Default (unless you have a strong reason otherwise): update CI to install `.[dev]` since `pyproject.toml` currently only defines `dev`.
  - Fix docs workflow cache dependency path if it points to a non-existent file.
  - Keep changes minimal and aligned with existing tooling.

  **Must NOT do**:
  - Do not change the overall CI structure; fix correctness only.

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: `deployment/github-actions-templates`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: All later work (CI must be trustworthy)
  - **Blocked By**: None

  **References**:
  - `.github/workflows/ci.yml` - backend install step currently uses `.[dev,test]`
  - `.github/workflows/docs.yml` - docs cache dependency path
  - `pyproject.toml` - optional dependencies (currently only `dev`)

  **Acceptance Criteria**:
  - [ ] CI python install step matches defined extras
  - [ ] Docs workflow no longer references non-existent requirements path

  **QA Scenarios**:
  ```
  Scenario: Editable install works in clean env
    Tool: Bash
    Steps:
      1. Create a fresh venv
      2. Run `pip install -e ".[dev]"` (or the updated equivalent)
    Expected Result: Install succeeds
    Evidence: .sisyphus/evidence/task-2-install-extras.txt
  ```

- [ ] 3. Fix Pytest Coverage Target + Add Test Markers (Release-Readiness P0/P1)

  **What to do**:
  - Verify coverage collection is targeting the intended Python package/module tree.
    - Note: with a `src/` layout, `--cov=solstein` can still be correct if the installed package name is `solstein` (from `src/solstein`).
  - If coverage is incorrect, adjust the target to the correct import package(s) (likely `solstein`).
  - Add pytest markers to classify tests (unit/integration/data_quality/agents; plus slow/e2e if needed).
  - Update any docs or Makefile targets that reference old coverage flags.

  **Must NOT do**:
  - Do not lower test strictness; goal is correctness and clarity.

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: `testing/python-testing-patterns`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: Tasks that move modules (needs reliable tests)
  - **Blocked By**: None

  **References**:
  - `pyproject.toml` - pytest addopts and configuration
  - `tests/` - existing test directory structure

  **Acceptance Criteria**:
  - [ ] `pytest tests/ --cov` produces coverage for the intended modules under `src/solstein/`
  - [ ] Markers are defined and used (or at minimum defined for future use)

  **QA Scenarios**:
  ```
  Scenario: Coverage collection targets the correct package
    Tool: Bash
    Steps:
      1. Run `pytest tests/ --cov --cov-report=term-missing`
      2. Confirm report includes modules under `src/solstein/`
    Expected Result: Coverage report includes expected modules
    Evidence: .sisyphus/evidence/task-3-coverage-target.txt
  ```

- [ ] 4. Single Source of Truth for Version + Release Metadata

  **What to do**:
  - Choose the authoritative version source (default: `pyproject.toml`).
  - Remove/align duplicate version definitions in code.
  - Ensure any release tooling reads the same source.

  **Must NOT do**:
  - Do not change the actual version number unless release strategy requires it.

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: `development/python-packaging`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: Package build/release verification
  - **Blocked By**: None

  **References**:
  - `pyproject.toml` - project version field
  - `src/solstein/__init__.py` - likely duplicate version constant

  **Acceptance Criteria**:
  - [ ] Exactly one authoritative version source is documented
  - [ ] `python -m build` produces artifacts with the intended version

  **QA Scenarios**:
  ```
  Scenario: Build artifacts reflect the expected version
    Tool: Bash
    Steps:
      1. Run `python -m build`
      2. Inspect wheel/sdist metadata for version
    Expected Result: Version matches `pyproject.toml`
    Evidence: .sisyphus/evidence/task-4-build-version.txt
  ```

- [ ] 5. Make CLI an Explicit Product Surface (Entrypoint + Smoke Tests)

  **What to do**:
  - Register the CLI as an explicit entrypoint (or explicitly decide it is internal-only).
  - Add a minimal CLI smoke test(s) to protect moves/renames.

  **Must NOT do**:
  - Do not add new CLI functionality; only make the existing surface explicit and testable.

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: `development/python-packaging`, `testing/python-testing-patterns`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: Later file moves that might break CLI
  - **Blocked By**: Task 2 (install correctness)

  **References**:
  - `src/solstein/cli.py` - current CLI implementation
  - `pyproject.toml` - place to define `[project.scripts]`
  - `tests/unit/test_cli_coverage.py` - existing CLI-related test patterns

  **Acceptance Criteria**:
  - [ ] CLI is invokable via a documented command (entrypoint or `python -m ...`)
  - [ ] New/updated CLI smoke tests pass

  **QA Scenarios**:
  ```
  Scenario: CLI help works
    Tool: Bash
    Steps:
      1. Run the CLI help command (entrypoint or module)
      2. Assert exit code 0 and expected help text contains "Solstein" or command list
    Expected Result: Help prints and exit code is 0
    Evidence: .sisyphus/evidence/task-5-cli-help.txt
  ```

- [ ] 6. MkDocs IA Quick Win: Surface Guides/Reference/Architecture

  **What to do**:
  - Update `mkdocs.yml` nav so the docs site surfaces:
    - developer/operator guides (`docs/guides/*`)
    - API reference (`docs/api/reference.md`)
    - architecture docs (`docs/architecture/*`)
  - Keep LORE and PITCH sections.
  - Ensure quarantined docs are excluded from nav.

  **Must NOT do**:
  - Do not rewrite doc content; navigation only.

  **Recommended Agent Profile**:
  - **Category**: `writing`
  - **Skills**: `code-quality/codebase-documenter`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: Task 7/8 (IA restructure)
  - **Blocked By**: None

  **References**:
  - `mkdocs.yml` - current nav only surfaces LORE/PITCH
  - `docs/guides/developer.md` - core dev guide to surface
  - `docs/api/reference.md` - API reference
  - `docs/architecture/decisions.md` - architecture section

  **Acceptance Criteria**:
  - [ ] `mkdocs build` succeeds
  - [ ] Site nav includes at minimum:
    - `docs/guides/developer.md`
    - `docs/guides/operator.md`
    - `docs/api/reference.md`
    - `docs/architecture/decisions.md`

  **QA Scenarios**:
  ```
  Scenario: Docs build + nav includes Guides
    Tool: Bash
    Steps:
      1. Run `mkdocs build`
      2. Verify build output contains the expected pages (or inspect generated site nav)
    Expected Result: Build succeeds; guides pages are included
    Evidence: .sisyphus/evidence/task-6-mkdocs-nav.txt
  ```

- [ ] 7. Docs IA Cleanup: Quarantine Historical Content + Reduce Root Clutter

  **What to do**:
  - Move historical content into an explicit archive area (keep, but quarantine):
    - `docs/archive/`
    - `docs/plans/`
    - `docs/PROPOSAL/`
  - Reduce `docs/` root clutter by grouping meta docs (glossary/quick-reference/maintenance) under a dedicated folder (e.g., `docs/reference/` or `docs/meta/`).
  - Update internal relative links affected by moves.

  **Must NOT do**:
  - Do not delete historical content; move and label only.

  **Recommended Agent Profile**:
  - **Category**: `writing`
  - **Skills**: `code-quality/codebase-documenter`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 8 (redirect/link validation becomes easier after structure is stable)
  - **Blocked By**: Task 6

  **References**:
  - `docs/PROPOSAL/` - historical proposals
  - `docs/plans/` - roadmap/implementation plan docs
  - `docs/archive/` - old analyses
  - `docs/GLOSSARY.md` - example of root clutter

  **Acceptance Criteria**:
  - [ ] Quarantined content is clearly separated and labeled
  - [ ] `mkdocs build` succeeds after moves
  - [ ] No broken internal markdown links in curated docs surface

  **QA Scenarios**:
  ```
  Scenario: Curated docs still build after quarantine moves
    Tool: Bash
    Steps:
      1. Run `mkdocs build --strict` (or `mkdocs build` if strict is too noisy)
    Expected Result: Build succeeds
    Evidence: .sisyphus/evidence/task-7-mkdocs-build-after-moves.txt
  
  Scenario: Link integrity spot-check
    Tool: Bash
    Steps:
      1. Run link validation script if present (or a grep-based check for moved paths)
      2. Confirm no curated docs link to old locations
    Expected Result: No references to old moved paths in curated docs
    Evidence: .sisyphus/evidence/task-7-link-spotcheck.txt
  ```

- [ ] 8. Docs Redirect/Link Policy: Add Redirects or Equivalents for Moved Pages

  **What to do**:
  - Decide the redirect approach:
    - mkdocs redirects plugin, OR
    - alias stub pages that link to new locations.
  - Implement redirects/aliases for moved high-traffic pages so old URLs don't 404.
  - Add a lightweight link-check gate to CI or pre-commit (if not already reliable).

  **Must NOT do**:
  - Do not over-engineer; keep the mechanism simple and maintainable.

  **Recommended Agent Profile**:
  - **Category**: `writing`
  - **Skills**: `deployment/github-actions-templates`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: Final docs verification
  - **Blocked By**: Task 7

  **References**:
  - `mkdocs.yml` - plugins + site config
  - `.github/workflows/docs.yml` - docs build/deploy workflow
  - `scripts/validate-links.py` - existing link validation hook (if used)

  **Acceptance Criteria**:
  - [ ] Old key doc URLs resolve via redirects/aliases
  - [ ] Link check passes (pre-commit and/or CI)

  **QA Scenarios**:
  ```
  Scenario: Redirect/alias pages exist for moved docs
    Tool: Bash
    Steps:
      1. Build the docs
      2. Verify redirect/alias artifacts are present for moved paths
    Expected Result: Users hitting old paths are guided to new pages
    Evidence: .sisyphus/evidence/task-8-docs-redirects.txt
  ```

- [ ] 9. Consolidate CI/CD Documentation Into Primary Docs Surface

  **What to do**:
  - Move or mirror `cicd/docs/` content into a clear section under `docs/` (e.g., `docs/guides/ci-cd.md` or `docs/reference/ci-cd.md`).
  - Ensure MkDocs nav links the curated CI/CD docs (not the raw `cicd/` directory).
  - Add a short pointer from `cicd/README.md` (if present) to the canonical docs location.

  **Must NOT do**:
  - Do not keep two competing sources of truth.

  **Recommended Agent Profile**:
  - **Category**: `writing`
  - **Skills**: `code-quality/codebase-documenter`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: Final docs IA polish
  - **Blocked By**: Task 6

  **References**:
  - `cicd/docs/` - CI/CD docs currently outside docs site structure
  - `docs/guides/operator.md` - likely home for operational CI/CD notes
  - `mkdocs.yml` - nav integration

  **Acceptance Criteria**:
  - [ ] CI/CD documentation has one canonical location under `docs/`
  - [ ] `mkdocs build` succeeds and nav includes CI/CD doc

  **QA Scenarios**:
  ```
  Scenario: CI/CD docs are reachable from mkdocs nav
    Tool: Bash
    Steps:
      1. Run `mkdocs build`
      2. Confirm CI/CD page is included in built site
    Expected Result: Build succeeds and includes CI/CD page
    Evidence: .sisyphus/evidence/task-9-cicd-docs-nav.txt
  ```

- [ ] 10. Quarantine Templates (Keep, But Out of the Product Path)

  **What to do**:
  - Move templates into a clearly labeled quarantine area (e.g., `examples/templates/` or `archive/templates/`) separated by web vs mobile.
  - Include the root-level template directories currently in the repo (at minimum `react-native-template/` and `svelte-template/`; include `flutter-template/` if present).
  - Add a short README explaining intended use and support expectations.
  - Ensure templates are excluded from Python packaging, mypy/ruff targets, and mkdocs nav.

  **Must NOT do**:
  - Do not delete templates; keep but quarantine as decided.

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: `code-quality/codebase-documenter`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: Final repo navigation polish
  - **Blocked By**: Task 1 (policy on quarantine)

  **References**:
  - `react-native-template/` - existing template (root-level)
  - `svelte-template/` - existing template (root-level)
  - `flutter-template/` - include if present
  - `pyproject.toml` - ruff/mypy exclude patterns

  **Acceptance Criteria**:
  - [ ] Templates live under an obvious non-product directory
  - [ ] `ruff` and `mypy` do not traverse template code

  **QA Scenarios**:
  ```
  Scenario: Lint/typecheck ignores quarantined templates
    Tool: Bash
    Steps:
      1. Run `ruff check src/ tests/`
      2. Run `mypy src/`
    Expected Result: Neither tool attempts to lint/typecheck template directories
    Evidence: .sisyphus/evidence/task-10-templates-ignored.txt
  ```

- [ ] 11. Quarantine or Remove Orphaned Azure Pipelines (Reduce Confusion)

  **What to do**:
  - Confirm which pipeline system is authoritative for release readiness (default: GitHub Actions).
  - Quarantine Azure pipeline files that are clearly broken/unrelated (move under `cicd/archive/`), and add a note explaining status.
  - Update docs/badges/references if they mention Azure pipelines.

  **Must NOT do**:
  - Do not break governance unexpectedly; if Azure is still required, keep and fix instead of removing.

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: `deployment/github-actions-templates`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: Final "professional repo" signal
  - **Blocked By**: None

  **References**:
  - `cicd/azure-pipelines.yml` - appears unrelated
  - `cicd/azure-pipelines-solstein.yml` - appears broken
  - `.github/workflows/ci.yml` - active CI
  - `README.md` - badges and references

  **Acceptance Criteria**:
  - [ ] Only one CI story is presented as authoritative in docs/README
  - [ ] Orphaned pipeline configs are quarantined and clearly labeled

  **QA Scenarios**:
  ```
  Scenario: No docs reference quarantined pipelines as active
    Tool: Bash
    Steps:
      1. Search for "azure-pipelines" references in README/docs
      2. Ensure references are either removed or marked archived
    Expected Result: No active pipeline docs point to archived configs
    Evidence: .sisyphus/evidence/task-11-azure-pipeline-refs.txt
  ```

- [ ] 12. Move Safety Net: Scan for Dynamic Imports/Entrypoints and Protect Them

  **What to do**:
  - Search for dynamic import patterns (`importlib`, `__import__`, string-based registries) that could break on moves.
  - Search for entrypoint-style references (CLI module paths, FastAPI app import strings, Celery app paths).
  - Add a small set of regression tests that fail if key dynamic import strings become invalid.

  **Must NOT do**:
  - Do not attempt to refactor the dynamic import mechanisms; just protect and document.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `debugging/systematic-debugging`, `testing/python-testing-patterns`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (can start immediately; produces safety map)
  - **Blocks**: Tasks 13-16 (moving modules safely)
  - **Blocked By**: None

  **References**:
  - `src/solstein/api/main.py` - FastAPI app import path usage
  - `src/solstein/worker.py` - worker entrypoint and task wiring
  - `scripts/run_api.py` - may reference app module strings

  **Acceptance Criteria**:
  - [ ] A test file exists that validates key dynamic import strings still resolve
  - [ ] `pytest` fails before refactor (RED) when a deliberate path is invalid, and passes after fixes (GREEN)

  **QA Scenarios**:
  ```
  Scenario: Dynamic import strings resolve
    Tool: Bash
    Steps:
      1. Run the new regression tests
    Expected Result: Tests pass and cover app/worker import strings
    Evidence: .sisyphus/evidence/task-12-dynamic-import-tests.txt
  ```

- [ ] 13. Establish Clean Architecture Map in Code (Package-Level, With Shims)

  **What to do**:
  - Define the target package map:
    - `solstein.domain` (pure models/validators/ports)
    - `solstein.application` (use-cases, orchestration, scoring workflows)
    - `solstein.infrastructure` (DB, external clients, data loaders)
    - `solstein.presentation` (FastAPI + CLI surfaces)
  - Implement this as directory/package structure, but preserve existing import paths via shims (re-export modules) so downstream code doesn’t break.
  - Add a basic architecture doc page that names each layer and gives examples.

  **Must NOT do**:
  - Do not perform deep refactors; keep movement mechanical.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `development/architecture-patterns`, `testing/python-testing-patterns`

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3 (foundation for de-dup work)
  - **Blocks**: Tasks 14-16
  - **Blocked By**: Tasks 1, 12

  **References**:
  - `src/solstein/domain/` - existing domain layer
  - `src/solstein/infrastructure/` - existing infrastructure layer
  - `src/solstein/presentation/` - existing presentation directory (if present)
  - `src/solstein/api/` - current API layer to map into presentation

  **Acceptance Criteria**:
  - [ ] Target layer map exists in code structure
  - [ ] Back-compat shims exist for moved packages
  - [ ] At least one test verifies old imports still work (RED->GREEN)

  **QA Scenarios**:
  ```
  Scenario: Old imports still resolve
    Tool: Bash
    Steps:
      1. Run `python -c "import solstein; import solstein.api; import solstein.analytics"` (or the key legacy imports)
    Expected Result: Imports succeed
    Evidence: .sisyphus/evidence/task-13-legacy-imports.txt
  
  Scenario: Layer map doc exists
    Tool: Bash
    Steps:
      1. Build mkdocs
      2. Confirm architecture page is included in nav
    Expected Result: Page exists and is visible
    Evidence: .sisyphus/evidence/task-13-layer-doc.txt
  ```

- [ ] 14. Resolve Analytics Duplication (Canonical + Shim)

  **What to do**:
  - Compare `src/solstein/analytics/` vs `src/solstein/application/analytics/` and select a canonical implementation per submodule.
  - If implementations are substantially different (rule of thumb: >20% divergence), stop and record a short decision note before choosing canonical.
  - Consolidate into the correct layer (`solstein.application.analytics`), and replace the non-canonical path with a shim.
  - Add tests around scoring/workflows most likely to break due to import moves.

  **Must NOT do**:
  - Do not change scoring behavior; focus on module wiring and paths.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `testing/python-testing-patterns`, `debugging/systematic-debugging`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 15-16)
  - **Blocks**: Final verification
  - **Blocked By**: Task 13

  **References**:
  - `src/solstein/analytics/` - existing analytics module tree
  - `src/solstein/application/analytics/` - duplicate analytics tree
  - `tests/unit/test_scorers_competitive.py` - representative scoring tests

  **Acceptance Criteria**:
  - [ ] Only one canonical analytics implementation exists
  - [ ] Legacy import path still works (shim)
  - [ ] Unit tests for analytics pass

  **QA Scenarios**:
  ```
  Scenario: Analytics scoring tests pass
    Tool: Bash
    Steps:
      1. Run `pytest tests/unit/ -k scorers`
    Expected Result: Tests pass
    Evidence: .sisyphus/evidence/task-14-analytics-tests.txt
  ```

- [ ] 15. Resolve Agents Duplication (Canonical + Shim)

  **What to do**:
  - Consolidate duplicated agent implementations into the correct layer (typically `application` for orchestration, `infrastructure` for external integrations).
  - If implementations are substantially different (rule of thumb: >20% divergence), stop and record a short decision note before choosing canonical.
  - Ensure the coordinator agent and its dependencies have stable, obvious import paths.
  - Add tests that import and minimally exercise agent wiring without making network calls.

  **Must NOT do**:
  - Do not introduce new external API calls; keep tests deterministic with mocks.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `testing/python-testing-patterns`, `development/architecture-patterns`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 14, 16)
  - **Blocks**: Final verification
  - **Blocked By**: Task 13

  **References**:
  - `src/solstein/agents/` - existing agents
  - `src/solstein/application/agents/` - duplicate agents
  - `src/solstein/agents/coordinator_agent.py` - key orchestration entry
  - `tests/test_agents/` - existing agent-level tests

  **Acceptance Criteria**:
  - [ ] Agents exist in one canonical location with shims for legacy imports
  - [ ] Agent tests pass without network dependencies

  **QA Scenarios**:
  ```
  Scenario: Agent tests run deterministically
    Tool: Bash
    Steps:
      1. Run `pytest tests/test_agents/`
    Expected Result: Tests pass
    Evidence: .sisyphus/evidence/task-15-agent-tests.txt
  ```

- [ ] 16. Resolve Exporters Duplication + Standardize HTTP Client (Default: httpx)

  **What to do**:
  - Consolidate exporter modules into one canonical location (likely `application.exporters`), leaving shims at old paths.
  - If implementations are substantially different (rule of thumb: >20% divergence), stop and record a short decision note before choosing canonical.
  - Standardize on one HTTP client for LLM/exporter HTTP calls (default: httpx, since it is already a dependency).
  - Add tests that validate exporter interfaces and ensure no regressions in Excel/markdown generation entrypoints.

  **Must NOT do**:
  - Do not change report semantics; keep outputs consistent.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `testing/python-testing-patterns`, `debugging/systematic-debugging`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 14-15)
  - **Blocks**: Final verification
  - **Blocked By**: Task 13

  **References**:
  - `src/solstein/exporters/` - existing exporters
  - `src/solstein/application/exporters/` - duplicate exporters
  - `src/solstein/exporters/excel.py` - Excel exporter entry
  - `tests/unit/test_excel_exporter_coverage.py` - exporter test coverage pattern

  **Acceptance Criteria**:
  - [ ] One canonical exporter implementation exists
  - [ ] Legacy imports resolve via shims
  - [ ] Exporter tests pass

  **QA Scenarios**:
  ```
  Scenario: Excel exporter tests pass
    Tool: Bash
    Steps:
      1. Run `pytest tests/unit/ -k excel`
    Expected Result: Tests pass
    Evidence: .sisyphus/evidence/task-16-exporter-tests.txt
  ```

- [ ] 17. Remove Dead/Empty Directories + Add Regression Checks

  **What to do**:
  - Remove empty/dead directories (after confirming they are not referenced):
    - `src/solstein/data_loaders/`
    - `src/solstein/application/extractors/`
  - Add a regression test that asserts key modules still import successfully (smoke test).

  **Must NOT do**:
  - Do not delete anything without confirming no references (including docs).

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: `testing/python-testing-patterns`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocks**: Final verification
  - **Blocked By**: Task 12

  **References**:
  - `src/solstein/infrastructure/data_loaders/` - appears to contain real loaders

  **Acceptance Criteria**:
  - [ ] Dead dirs removed without breaking imports
  - [ ] New smoke test passes

  **QA Scenarios**:
  ```
  Scenario: Import smoke test
    Tool: Bash
    Steps:
      1. Run `pytest tests/unit/ -k import`
    Expected Result: Tests pass
    Evidence: .sisyphus/evidence/task-17-import-smoke.txt
  ```

- [ ] 18. Repo Hygiene: Quarantine/Explain Tooling Directories

  **What to do**:
  - For each tooling directory (`.antigravity/`, `opencode/`, `validation/`, `.sisyphus/`):
    - Decide keep-in-place vs move-to-`tools/`
    - Add a README describing purpose, ownership, and whether it affects release
  - Ensure these directories are excluded from packaging and do not interfere with CI.

  **Must NOT do**:
  - Do not break existing local tooling integrations (Claude/OpenCode rules).

  **Recommended Agent Profile**:
  - **Category**: `writing`
  - **Skills**: `code-quality/codebase-documenter`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4
  - **Blocks**: Final "professional repo" polish
  - **Blocked By**: Task 1

  **References**:
  - `opencode/` - OpenCode rules
  - `.antigravity/` - prompt/rules-like content
  - `validation/` - rule definitions
  - `.sisyphus/` - plan/draft artifacts

  **Acceptance Criteria**:
  - [ ] Each directory has a short README stating purpose + impact
  - [ ] CI/lint/typecheck do not traverse these dirs

  **QA Scenarios**:
  ```
  Scenario: Tooling dirs documented
    Tool: Bash
    Steps:
      1. Verify each directory contains a README
    Expected Result: Each has a README
    Evidence: .sisyphus/evidence/task-18-tooling-readmes.txt
  ```

- [ ] 19. Repo Hygiene: Make Artifacts and Data Boundaries Explicit

  **What to do**:
  - Classify top-level `data/` and `reports/` as source vs generated artifacts.
  - Add READMEs and `.gitignore` rules so generated outputs don’t pollute the repo.
  - Ensure sample data needed for tests remains versioned, while bulky outputs are excluded.

  **Must NOT do**:
  - Do not remove datasets that tests rely on.

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: `code-quality/codebase-documenter`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4
  - **Blocks**: Final repo cleanliness
  - **Blocked By**: None

  **References**:
  - `data/` - raw datasets
  - `reports/` - generated reports
  - `tests/data_quality/` - golden dataset tests (if present)

  **Acceptance Criteria**:
  - [ ] Generated artifacts are ignored
  - [ ] Tests still pass and can find required sample data

  **QA Scenarios**:
  ```
  Scenario: Clean git status after running tests
    Tool: Bash
    Steps:
      1. Run `pytest tests/`
      2. Run `git status --porcelain`
    Expected Result: No new large artifacts appear untracked
    Evidence: .sisyphus/evidence/task-19-clean-status.txt
  ```

- [ ] 20. Repo Indexing: Update Entry-Point Docs for “Where Do I Find X?”

  **What to do**:
  - Ensure `README.md` and the docs landing page answer:
    - how to run API, workers, tests, docs, dashboard
    - where core modules live by layer
    - where quarantined content lives
  - Add a short contributor map (1 screenful) with links.

  **Must NOT do**:
  - Do not produce verbose docs; keep it navigational.

  **Recommended Agent Profile**:
  - **Category**: `writing`
  - **Skills**: `code-quality/codebase-documenter`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4
  - **Blocks**: Perception of professionalism / onboarding
  - **Blocked By**: Tasks 6-9, 13-19

  **References**:
  - `README.md` - current architecture section
  - `docs/index.md` - docs landing page
  - `docs/guides/developer.md` - deeper setup detail

  **Acceptance Criteria**:
  - [ ] A new contributor can locate major components in <2 minutes following README/docs

  **QA Scenarios**:
  ```
  Scenario: Onboarding links are consistent
    Tool: Bash
    Steps:
      1. Build mkdocs
      2. Confirm README links point to existing docs pages
    Expected Result: No broken references
    Evidence: .sisyphus/evidence/task-20-onboarding-links.txt
  ```

---

## Final Verification Wave

- Full repo quality gate run (install/lint/typecheck/tests/docs/build)
- Import-compat audit: old import paths still resolve (or explicit migration notes exist)
- Docs link/redirect audit: mkdocs build + link check passes

---

## Commit Strategy

- Commit in small thematic chunks aligned to waves (CI fixes, docs IA, backend layering, quarantine).
- Avoid mega-commits; each commit should be revertable and keep CI green.

---

## Success Criteria

- New contributors can answer "where is X" quickly from README + folder structure.
- CI is green and local quality gate commands are documented and pass.
- mkdocs site navigation surfaces the right docs; archive/proposal content is clearly quarantined.
- Backend layering is clear; duplicated modules are resolved; compat shims exist where needed.
