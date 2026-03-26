# Pipeline Quality Enforcement Plan

## Objective

Reduce recurring integration failures by enforcing contracts at the actual logical boundaries of the system:

- external connectors
- enrichment and merge stages
- scoring and classification logic
- persistence adapters
- export and report generation
- worker orchestration and refresh jobs

This plan is intentionally aligned to the current repo tooling:

- `pytest`
- `pytest-asyncio`
- `ruff`
- `mypy`
- existing `Makefile`
- current `tests/unit`, `tests/integration`, and `tests/data_quality` layout

## Current State

The repo already has a large test surface, but the highest-risk failures keep recurring because the enforcement model is too permissive in the places that matter most:

- boundary tests are inconsistent
- some unit tests are stale and no longer match production contracts
- the audit markdown can drift away from the worktree
- lint and typing gates are present but not strict enough to stop semantic regressions
- API/documentation conformance is mostly manual instead of encoded into tests
- root test harness imports too much application state during collection, which prevents narrow regression execution

## Enforcement Layers

### 1. Boundary Unit Tests

Every critical pipeline node should have narrow unit tests that assert:

- accepted input schema
- output schema and field types
- null-handling behavior
- fallback behavior
- no silent degradation to empty or fake results

Critical nodes to cover first:

1. Refresh connectors under `src/solstein/infrastructure/connectors/`
2. Unified enrichment adapters under `src/solstein/adapters/enrichment/`
3. Merge and adjudication logic under `src/solstein/data/unified/`
4. Scoring and classification under `src/solstein/analytics/`
5. Worker orchestration and retry paths under `src/solstein/worker/`
6. Report/export generation under `src/solstein/intelligence/` and `src/solstein/exporters/`

Required rule:

- every bugfix in one of these folders must land with a regression test in the nearest boundary test file

### 2. Schema Validation Gates

Connector and pipeline boundaries should validate payloads explicitly instead of passing loose dicts through the system unchecked.

Enforce:

- Pydantic models for connector fact payloads
- explicit response envelopes for adapter outputs
- validation before persistence
- validation before export/report generation

Recommended implementation:

1. Introduce typed schemas for each connector fact family.
2. Validate before `store_facts()` and fail closed on malformed payloads.
3. Add tests that assert malformed payloads raise or are rejected with logged errors.

Initial enforcement started:

- `FactIngestionPayload` now validates the worker fact ingestion boundary in `src/solstein/worker/base.py`
 - `ConnectorFactPayload` now validates the shared connector fact envelope in `src/solstein/infrastructure/fact_payloads.py`
 - `BaseRefreshConnector` now validates fact envelopes before delta filtering and before persistence

### 3. Regression and Golden Dataset Gates

The project already has `tests/data_quality/`. Expand that into a true release gate.

Required checks:

- golden classification outputs for representative companies
- golden scoring envelopes and component totals
- connector-to-fact normalization snapshots
- report/export snapshot tests for critical sections

Release rule:

- no merge to protected branches if golden dataset regression fails

### 4. Integration Node Tests

Add a smaller, curated set of integration tests that cover only critical business paths:

1. tracked company refresh
2. enrichment merge
3. scoring/classification
4. persistence
5. report generation

These should be deterministic and use mocked external APIs but real internal contracts.

The current integration suite is broad. What is missing is a short list of mandatory gate tests that represent the business-critical path.

### 5. API Documentation Conformance Tests

For each official external API used in production:

- capture the expected request pattern
- capture the expected response envelope
- codify the parsing assumptions

Enforce with:

- recorded fixtures from official docs examples when license-safe
- contract tests that validate parser behavior against those fixtures
- explicit per-provider test files

Priority APIs:

1. SEC EDGAR
2. Companies House
3. OpenCorporates
4. OpenFIGI
5. NewsAPI
6. Yahoo Finance and any wrapper assumptions around it

Rule:

- every connector should have a documented contract test file under `tests/unit/data/` or `tests/integration/`

### 6. Strict Lint and Type Gates

Current state:

- `ruff` exists
- `mypy` exists
- both are not strict enough yet

Tightening sequence:

1. Keep `ruff check src tests` mandatory in CI.
2. Add targeted rules for high-risk folders first:
   - `src/solstein/infrastructure/connectors`
   - `src/solstein/adapters/enrichment`
   - `src/solstein/data/unified`
   - `src/solstein/worker`
3. Increase mypy strictness by directory instead of globally flipping the whole repo.
4. Fail CI on newly introduced `Any`-heavy contract boundaries unless explicitly justified.

### 7. Quality Gates in CI

Recommended CI stages:

1. `ruff check src tests`
2. `mypy` for high-risk directories
3. fast unit regression set for critical nodes
4. schema gate tests
5. curated integration gate tests
6. golden dataset regression

Fast-fail rule:

- stages 1 to 4 must run on every PR
- stages 5 to 6 must run on merge queue or protected branch PRs

### 8. Harness Modularity Gate

The root pytest harness must not force full app startup for unrelated unit tests.

Enforce:

- lazy imports for app-dependent fixtures
- separate app/integration fixtures from pure unit fixtures
- narrow regression files must run without broad environment provisioning

## Immediate Next Steps

### Phase 1: Stop Reintroducing Known Bugs

1. Reconcile stale audit entries with current code.
2. Replace stale connector tests with real contract tests.
3. Add regression tests for every issue fixed in the current audit batch.
4. Add a dedicated CI target for critical-node regressions.

### Phase 2: Make Contracts Explicit

1. Expand the new connector fact envelope gate into per-family fact value schemas.
2. Validate them at the edges.
3. Fail on malformed payloads instead of silently normalizing bad shapes.

### Phase 3: Tighten the Gates

1. Raise mypy strictness in high-risk directories.
2. Add golden regression gates for scoring and classification.
3. Add release-blocking integration tests for the refresh-to-report path.

## Suggested Make Targets

Add or refine these targets:

```make
test-critical:
	$(BIN)/pytest tests/unit/test_audit_regressions_march_2026.py tests/unit/data/ tests/unit/test_worker_tasks_isolated.py -x

test-contracts:
	$(BIN)/pytest tests/unit/data/ tests/unit/adapters/ -x

test-golden:
	$(BIN)/pytest tests/data_quality/ -x

lint-critical:
	$(BIN)/ruff check src/solstein/infrastructure/connectors src/solstein/adapters/enrichment src/solstein/data/unified src/solstein/worker tests

type-critical:
	$(BIN)/mypy src/solstein/infrastructure/connectors src/solstein/adapters/enrichment src/solstein/data/unified src/solstein/worker

gate-critical: lint-critical type-critical test-critical test-contracts
```

## Non-Negotiable Rule Set

1. No critical pipeline-node change without a regression test.
2. No external API connector without a contract test based on documented response shape.
3. No loose dict payload crossing a critical node without schema validation.
4. No protected-branch merge if critical-node tests or golden regressions fail.
5. No audit entry marked fixed until code, tests, and log entry all exist.
