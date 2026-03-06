# Free-Source Real-Data Hardening Plan

## TL;DR

> **Quick Summary**: Harden Solstein so client exports are strictly real-data only, with deterministic free-source-first enrichment and paid escalation only for unresolved gaps under explicit policy.
>
> **Deliverables**:
> - Unified release gate used by all report entrypoints
> - Policy-driven free-pass then paid-gap orchestration
> - Deterministic gap/queue/freshness outputs with auditability
> - Post-implementation automated test wave and evidence-backed QA
>
> **Estimated Effort**: Large
> **Parallel Execution**: YES - 3 implementation waves + final verification wave
> **Critical Path**: T1 -> T3 -> T4 -> T10 -> T11/T12 -> T16 -> F1-F4

---

## Context

### Original Request
User requires real-only client reports, deep free-source-first enrichment, and paid sources only for unresolved gaps.

### Interview Summary
**Key Discussions**:
- Scope locked to `Data-first + gate`.
- Test strategy locked to `Tests after implementation`.
- User preference: proceed continuously and maximize free-source depth before paid usage.

**Research Findings**:
- Product/analytics audit: readiness controls are partly manual; queue/freshness and quality assertions need stronger enforcement.
- Architecture audit: implement policy-driven free->paid flow, standardized unresolved-gap analyzer, and unified release gate.
- Backend audit: broader platform hardening exists but is deferred unless directly required by data-release safety.

### Metis Review
**Identified Gaps (addressed in this plan)**:
- Define explicit no-fabrication rule and data-source-type semantics.
- Enforce gate parity across CLI/API exports.
- Require free->paid escalation audit reason per field.
- Add executable negative/positive acceptance tests for synthetic blocking and real-only success.
- Handle edge cases: contradictory sources, stale cache windows, numeric parsing unit/currency drift.

---

## Work Objectives

### Core Objective
Deliver a production-safe, auditable data pipeline where client reports are blocked unless completeness, confidence, provenance, and authenticity thresholds pass after a free-first acquisition pass and controlled paid escalation.

### Concrete Deliverables
- Unified report release gate service and consistent wiring across report entrypoints.
- Source policy catalog and standardized unresolved-gap analyzer output.
- Two-pass enrichment orchestration (free first, paid for unresolved fields only).
- Queue/freshness artifacts with deterministic escalation reasons.
- Automated tests and QA evidence proving no synthetic leakage and no metric fabrication.

### Definition of Done
- [x] `PYTHONPATH=src pytest tests/unit/test_synthetic_gate.py -q` passes.
- [x] `PYTHONPATH=src pytest tests/unit/test_completeness.py -q` passes.
- [x] `PYTHONPATH=src python scripts/run_data_refresh_cycle.py --input data/input/competitor_data_real_enriched.json` produces non-empty deterministic delta metadata.
- [x] `PYTHONPATH=src python scripts/run_eneve_199.py --input data/input/competitor_data_real_enriched.json` either generates export that passes gate or fails with explicit insufficiency reasons (never synthetic/fabricated pass-through).

### Must Have
- Strict real-data-only export gating across CLI and API paths.
- Free-first then paid-gap orchestration with per-field escalation logging.
- No fabricated numeric defaults in client output (missing stays explicit).
- Deterministic unresolved-gap analyzer output used by queueing/release decisions.

### Must NOT Have (Guardrails)
- No synthetic data in client export paths.
- No silent fallback swallowing enrichment/release errors.
- No blanket paid-provider calls before free-pass completion.
- No manual-only readiness checks as release authority.
- No scope expansion into unrelated platform hardening/UI productization.

### Defaults Applied (to remove ambiguity)
- **Real-data definition**: release-eligible values must be provenance-backed to a concrete source URL/canonical URI and pass source policy checks.
- **Estimate handling**: estimated values are allowed only when explicitly labeled as estimates with provenance and confidence; unlabeled inferred numerics are blocked.
- **Surface coverage**: release gate applies to CLI exports, API-triggered exports, and scripted export entrypoints.
- **Paid escalation policy**: paid calls are disabled unless configured, and when enabled they are limited to unresolved fields after free-pass completion with audit reason per field.

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** - all verification is agent-executed.

### Test Decision
- **Infrastructure exists**: YES
- **Automated tests**: Tests-after implementation
- **Framework**: pytest

### QA Policy
Every task includes runnable QA scenarios (happy + failure/edge), with evidence stored under `.sisyphus/evidence/`.

- **Frontend/UI**: Playwright only if UI touched (not expected in this scope)
- **CLI/TUI**: `interactive_bash` or Bash command verification
- **API/Backend**: Bash with `curl`/Python scripts and explicit assertions
- **Library/Module**: pytest + direct module invocation

---

## Execution Strategy

### Parallel Execution Waves

Wave 1 (Foundation, can start immediately):
- T1 Source identity + provenance contract
- T2 Source policy catalog (free/paid/authority/capability)
- T3 Standard unresolved-gap analyzer output
- T6 Identifier reliability hardening
- T7 Financial metric parsing/normalization hardening
- T8 Queue builder semantics fix (`ticker OR company_number`) + derived `ai_maturity_score`
- T9 Freshness/staleness policy in refresh artifacts

Wave 2 (Core orchestration + gate wiring):
- T4 Free-source-first orchestration pass
- T5 Targeted paid-gap escalation + budget/attempt controls
- T10 Unified `ReportReleaseGate` service
- T11 CLI release-gate integration
- T12 API/export path release-gate integration
- T13 Escalation/release audit logging

Wave 3 (Validation + operationalization):
- T14 Tests-after implementation (quality and behavior)
- T15 Readiness checklist automation and runbook alignment
- T16 End-to-end Eneve dry-run with evidence pack

Wave FINAL (Independent review, parallel):
- F1 Plan compliance audit
- F2 Code quality/build/test review
- F3 Full QA scenario replay
- F4 Scope fidelity and contamination check

Critical Path: T1 -> T3 -> T4 -> T10 -> T11/T12 -> T16 -> F1-F4
Parallel Speedup Target: ~60-70% vs fully sequential
Max Concurrent Target: 7 (Wave 1)

### Dependency Matrix (full)
- **T1**: Blocked By: none | Blocks: T3, T4, T10
- **T2**: Blocked By: none | Blocks: T4, T5, T13
- **T3**: Blocked By: T1 | Blocks: T4, T5, T10, T16
- **T4**: Blocked By: T1, T2, T3 | Blocks: T5, T16
- **T5**: Blocked By: T2, T3, T4 | Blocks: T13, T16
- **T6**: Blocked By: none | Blocks: T4, T5, T8
- **T7**: Blocked By: none | Blocks: T3, T4, T10
- **T8**: Blocked By: T6 | Blocks: T3, T4, T16
- **T9**: Blocked By: none | Blocks: T15, T16
- **T10**: Blocked By: T1, T3, T7 | Blocks: T11, T12, T16
- **T11**: Blocked By: T10 | Blocks: T16
- **T12**: Blocked By: T10 | Blocks: T16
- **T13**: Blocked By: T2, T5 | Blocks: T16
- **T14**: Blocked By: T4, T5, T10, T11, T12 | Blocks: T16, F2
- **T15**: Blocked By: T9, T10 | Blocks: T16, F1
- **T16**: Blocked By: T3, T4, T5, T8, T10, T11, T12, T13, T14, T15 | Blocks: F1-F4

### Agent Dispatch Summary
- **Wave 1**: T1/T2/T3/T8/T9 -> `quick`; T6/T7 -> `unspecified-high`
- **Wave 2**: T4/T5/T10/T13 -> `unspecified-high`; T11/T12 -> `quick`
- **Wave 3**: T14 -> `unspecified-high`; T15 -> `writing`; T16 -> `deep`
- **Final**: F1 -> `oracle`; F2/F3 -> `unspecified-high`; F4 -> `deep`

---

## TODOs

- [x] T1. Define source identity + provenance contract

  **What to do**:
  - Define canonical source key semantics and provenance requirements (URL/canonical URI, retrieval timestamp, field-level linkage).
  - Normalize source labeling contract so downstream confidence and gating are deterministic.

  **Must NOT do**:
  - Do not allow free-form/ambiguous source names in release-critical paths.

  **Recommended Agent Profile**:
  - **Category**: `quick` (contract/schema-level updates)
  - **Skills**: `project-specific/api-contract-validator`, `code-quality/defense-in-depth`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: T3, T4, T10
  - **Blocked By**: None

  **References**:
  - `src/solstein/data/connectors/lookup_service.py` - current identifier/source confidence behavior to normalize.
  - `src/solstein/data/loaders.py` - ingestion point where source semantics propagate.
  - `src/solstein/data/report_readiness.py` - gate consumer expecting trustworthy provenance.

  **Acceptance Criteria**:
  - [x] Source identity schema/rules documented in code and consumed by gap/gate logic.
  - [x] Existing pipelines still execute without schema regression.

  **QA Scenarios**:
  - Scenario: valid provenance accepted
    Tool: Bash
    Steps: run enrichment on real dataset and inspect serialized source records for canonical source keys + URL/URI.
    Expected: all enriched records have normalized source identity fields.
    Evidence: `.sisyphus/evidence/task-T1-valid-provenance.txt`
  - Scenario: invalid provenance rejected
    Tool: Bash
    Steps: run a fixture with malformed source label and execute readiness validation.
    Expected: explicit validation failure reason indicates provenance contract violation.
    Evidence: `.sisyphus/evidence/task-T1-invalid-provenance-error.txt`

  **Commit**: NO

- [x] T2. Create source policy catalog (free/paid/authority/capabilities)

  **What to do**:
  - Introduce policy structure mapping each source/adapter to tier (free/paid), base confidence, required identifiers, and field coverage.
  - Ensure orchestrator can query policy for free-first selection and paid escalation eligibility.

  **Must NOT do**:
  - Do not hardcode policy decisions in multiple modules.

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: `development/architecture-patterns`, `project-specific/import-dependency-analyzer`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: T4, T5, T13
  - **Blocked By**: None

  **References**:
  - `src/solstein/data/enrichment_config.py` - existing enrichment configuration patterns.
  - `src/solstein/data/real_data_integration.py` - integration layer for policy use.
  - `scripts/auto_enrich_real_data.py` - orchestration script where policy is applied.

  **Acceptance Criteria**:
  - [x] Single policy catalog consumed by orchestration and escalation decisions.
  - [x] Policy explicitly marks free-first order and paid-only fallback candidates.

  **QA Scenarios**:
  - Scenario: free-only mode respects policy ordering
    Tool: Bash
    Steps: run enrichment with paid keys unset and capture source selection trace.
    Expected: only free-tier sources attempted.
    Evidence: `.sisyphus/evidence/task-T2-free-policy-order.txt`
  - Scenario: paid source blocked before free exhaustion
    Tool: Bash
    Steps: run with paid keys set but with unresolved gaps not yet post-free pass.
    Expected: no paid call before free pass completion marker.
    Evidence: `.sisyphus/evidence/task-T2-paid-precheck-error.txt`

  **Commit**: NO

- [x] T3. Standardize unresolved-gap analyzer output

  **What to do**:
  - Normalize gap states by company/field: missing, low-confidence, provenance-invalid, contradiction-open.
  - Emit deterministic structure used by queueing, paid escalation, and release gate.

  **Must NOT do**:
  - Do not emit ad-hoc field names or non-deterministic ordering.

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: `project-specific/test-coverage-analyzer`, `code-quality/defense-in-depth`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: T4, T5, T10, T16
  - **Blocked By**: T1

  **References**:
  - `data/output/research_queue.json` - current unresolved-gap artifact baseline.
  - `src/solstein/data/report_readiness.py` - gate criteria consumer.
  - `scripts/run_research_queue.py` - queue execution flow requiring structured gap output.

  **Acceptance Criteria**:
  - [x] Gap analyzer emits stable machine-readable categories for all companies.
  - [x] Queue and gate consume the same schema without adapters.

  **QA Scenarios**:
  - Scenario: deterministic gap artifact
    Tool: Bash
    Steps: run queue generation twice on same input; compare normalized JSON.
    Expected: identical ordering and semantic categories.
    Evidence: `.sisyphus/evidence/task-T3-deterministic-gap.txt`
  - Scenario: malformed gap state rejected
    Tool: Bash
    Steps: inject unsupported gap status in fixture and run validator.
    Expected: explicit schema/validation failure.
    Evidence: `.sisyphus/evidence/task-T3-gap-schema-error.txt`

  **Commit**: NO

- [x] T4. Implement free-source-first orchestration pass

  **What to do**:
  - Refactor orchestration to run full free-source pass first.
  - Recompute unresolved gaps only after free pass completion and persist pass metadata.

  **Must NOT do**:
  - Do not trigger paid source calls inside free pass loop.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `development/architecture-patterns`, `code-quality/condition-based-waiting`

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2
  - **Blocks**: T5, T16
  - **Blocked By**: T1, T2, T3

  **References**:
  - `scripts/auto_enrich_real_data.py` - primary orchestration logic.
  - `src/solstein/data/web_search_client.py` - free-source retrieval path.
  - `src/solstein/data/connectors/lookup_service.py` - identifier resolution dependency.

  **Acceptance Criteria**:
  - [x] Free pass completion marker exists before any paid escalation path.
  - [x] Unresolved gaps are recomputed after free pass, not before.

  **QA Scenarios**:
  - Scenario: free pass executes fully
    Tool: Bash
    Steps: run enrichment with only free keys configured; inspect logs/artifacts.
    Expected: free pass completes and unresolved-gap artifact generated.
    Evidence: `.sisyphus/evidence/task-T4-free-pass-happy.txt`
  - Scenario: paid invoked prematurely is blocked
    Tool: Bash
    Steps: force a code path attempting paid call before free completion.
    Expected: run fails with explicit policy violation message.
    Evidence: `.sisyphus/evidence/task-T4-premature-paid-error.txt`

  **Commit**: YES
  - Message: `feat(data): enforce deterministic free-source-first orchestration`

- [x] T5. Implement targeted paid-gap escalation with cost controls

  **What to do**:
  - Escalate only unresolved fields after free-pass completion.
  - Record per-field escalation reason, source attempted, and budget/attempt counters.

  **Must NOT do**:
  - Do not run blanket paid enrichment for all companies.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `deployment/secrets-management`, `code-quality/error-handling-patterns`

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2
  - **Blocks**: T13, T16
  - **Blocked By**: T2, T3, T4

  **References**:
  - `scripts/auto_enrich_real_data.py` - escalation routing and queue integration.
  - `.env.example` - provider key toggles and environment semantics.
  - `data/output/research_queue.json` - unresolved field targeting baseline.

  **Acceptance Criteria**:
  - [x] Paid escalation only appears for unresolved fields after free pass.
  - [x] Escalation records include reason + budget metadata.

  **QA Scenarios**:
  - Scenario: paid escalation for unresolved fields only
    Tool: Bash
    Steps: run with paid key set on dataset with known unresolved subset; inspect escalation records.
    Expected: only flagged unresolved fields are escalated.
    Evidence: `.sisyphus/evidence/task-T5-targeted-paid-happy.txt`
  - Scenario: budget cap exceeded
    Tool: Bash
    Steps: run with low paid-attempt cap and unresolved-heavy input.
    Expected: escalation stops at cap with explicit budget-exceeded audit entries.
    Evidence: `.sisyphus/evidence/task-T5-budget-cap-error.txt`

  **Commit**: YES
  - Message: `feat(data): add targeted paid-gap escalation and budget governance`

- [x] T6. Harden identifier reliability and confidence thresholds

  **What to do**:
  - Strengthen identifier verification from authoritative/free sources before acceptance.
  - Reject low-confidence identifier merges from weak regex-only extraction.

  **Must NOT do**:
  - Do not treat unverified scraped identifiers as production-equivalent IDs.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `project-specific/import-dependency-analyzer`, `code-quality/root-cause-tracing`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: T4, T5, T8
  - **Blocked By**: None

  **References**:
  - `src/solstein/data/connectors/lookup_service.py` - identifier resolution and confidence model.
  - `data/output/identifier_cache.json` - current cache quality/consistency patterns.
  - `src/solstein/data/report_readiness.py` - identifier confidence impact on release decisions.

  **Acceptance Criteria**:
  - [x] Identifier acceptance requires confidence + authoritative-source conditions.
  - [x] Cache stores verification metadata and rejection reason for weak candidates.

  **QA Scenarios**:
  - Scenario: authoritative identifier accepted
    Tool: Bash
    Steps: run lookup for known company with authoritative match and inspect cache entry.
    Expected: identifier accepted with confidence over threshold and source provenance.
    Evidence: `.sisyphus/evidence/task-T6-identifier-happy.txt`
  - Scenario: weak scraped identifier rejected
    Tool: Bash
    Steps: feed ambiguous company name with regex-only candidate.
    Expected: candidate rejected or marked insufficient with clear reason.
    Evidence: `.sisyphus/evidence/task-T6-identifier-reject.txt`

  **Commit**: NO

- [x] T7. Strengthen financial parsing and unit/currency normalization

  **What to do**:
  - Improve parsing and normalization for revenue/employees/growth/margin/funding/valuation.
  - Ensure unit and currency normalization is explicit and auditable.

  **Must NOT do**:
  - Do not silently coerce parse failures into plausible-looking numeric defaults.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `code-quality/defense-in-depth`, `debugging/systematic-debugging`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: T3, T4, T10
  - **Blocked By**: None

  **References**:
  - `src/solstein/data/metric_contract.py` - normalization and metric contract logic.
  - `src/solstein/data/loaders.py` - loader integration points.
  - `src/solstein/validation/financial_sanity.py` - sanity/quality checks affected by parse outputs.

  **Acceptance Criteria**:
  - [x] Parsed metrics include explicit unit/currency context or remain missing.
  - [x] No fabricated fallback numeric values are emitted for parse failures.

  **QA Scenarios**:
  - Scenario: mixed unit/currency input normalized correctly
    Tool: Bash
    Steps: run parser on fixture containing USD/EUR and K/M/B units.
    Expected: normalized outputs carry correct canonical units and values.
    Evidence: `.sisyphus/evidence/task-T7-normalization-happy.txt`
  - Scenario: ambiguous numeric string handled safely
    Tool: Bash
    Steps: pass ambiguous value (e.g., "12,5bn? est") through parser.
    Expected: parse flagged insufficient (not coerced to arbitrary number).
    Evidence: `.sisyphus/evidence/task-T7-ambiguous-parse-error.txt`

  **Commit**: NO

- [x] T8. Fix queue semantics and derived `ai_maturity_score` population

  **What to do**:
  - Update queue logic to require `ticker OR company_number` (not both) where policy allows.
  - Ensure `ai_maturity_score` is derived/populated when missing from available signals.

  **Must NOT do**:
  - Do not over-relax identifier requirements for sources that explicitly require strict IDs.

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: `code-quality/root-cause-tracing`, `testing/python-testing-patterns`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: T3, T4, T16
  - **Blocked By**: T6

  **References**:
  - `scripts/auto_enrich_real_data.py` - queue builder and merge-back logic.
  - `src/solstein/domain/models.py` - source fields for maturity derivation.
  - `data/output/research_queue.json` - expected downstream artifact behavior.

  **Acceptance Criteria**:
  - [x] Queue inclusion logic reflects `ticker OR company_number` policy.
  - [x] Missing `ai_maturity_score` is deterministically derived or explicitly marked missing with reason.

  **QA Scenarios**:
  - Scenario: company with one identifier still queued correctly
    Tool: Bash
    Steps: run queue build on fixture where company has only ticker.
    Expected: company appears in queue when field gaps exist.
    Evidence: `.sisyphus/evidence/task-T8-or-identifier-happy.txt`
  - Scenario: no derivation signal available
    Tool: Bash
    Steps: run merge on fixture missing all maturity inputs.
    Expected: no fabricated score; explicit insufficiency reason recorded.
    Evidence: `.sisyphus/evidence/task-T8-maturity-derivation-error.txt`

  **Commit**: YES
  - Message: `fix(queue): align identifier requirement and deterministic maturity derivation`

- [x] T9. Add freshness/staleness controls to refresh artifacts

  **What to do**:
  - Add explicit freshness windows and stale-data flags to delta/report artifacts.
  - Ensure stale outputs can block release gate when policy requires.

  **Must NOT do**:
  - Do not treat all-zero delta as implicitly healthy without freshness metadata.

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: `code-quality/error-handling-patterns`, `testing/python-testing-patterns`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: T15, T16
  - **Blocked By**: None

  **References**:
  - `scripts/run_data_refresh_cycle.py` - refresh/delta artifact production.
  - `data/output/refresh/delta_report.json` - current stale-risk output.
  - `src/solstein/data/report_readiness.py` - freshness checks for release decisions.

  **Acceptance Criteria**:
  - [x] Delta artifact includes freshness timestamp/window and stale boolean.
  - [x] Gate can fail for stale data when threshold exceeded.

  **QA Scenarios**:
  - Scenario: fresh run marked valid
    Tool: Bash
    Steps: execute refresh cycle and inspect new delta metadata.
    Expected: stale flag false within configured window.
    Evidence: `.sisyphus/evidence/task-T9-freshness-happy.txt`
  - Scenario: stale artifact rejected
    Tool: Bash
    Steps: run gate check against intentionally old artifact timestamp fixture.
    Expected: gate fails with stale-data reason.
    Evidence: `.sisyphus/evidence/task-T9-stale-error.txt`

  **Commit**: NO

- [x] T10. Implement unified `ReportReleaseGate` service

  **What to do**:
  - Consolidate release checks (authenticity, completeness, confidence, provenance, freshness, contradiction thresholds) into one service.
  - Return deterministic pass/fail payload with machine-readable reasons.

  **Must NOT do**:
  - Do not maintain divergent gate logic across entrypoints.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `development/architecture-patterns`, `code-quality/verification-before-completion`

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2
  - **Blocks**: T11, T12, T16
  - **Blocked By**: T1, T3, T7

  **References**:
  - `src/solstein/data/report_readiness.py` - existing gate utility baseline.
  - `src/solstein/exceptions.py` - consistent failure semantics.
  - `docs/client-data-readiness-checklist.md` - policy items to make executable.

  **Acceptance Criteria**:
  - [x] Single service performs all release-critical checks.
  - [x] Structured fail reasons are consistent across CLI/API usage.

  **QA Scenarios**:
  - Scenario: complete high-confidence dataset passes gate
    Tool: Bash
    Steps: run gate service on enriched fixture meeting thresholds.
    Expected: pass=true with empty critical failures.
    Evidence: `.sisyphus/evidence/task-T10-gate-happy.txt`
  - Scenario: low-confidence dataset blocked
    Tool: Bash
    Steps: run gate on fixture with confidence below threshold.
    Expected: pass=false with reason code for confidence insufficiency.
    Evidence: `.sisyphus/evidence/task-T10-gate-low-confidence-error.txt`

  **Commit**: YES
  - Message: `feat(gate): unify release validation into single service`

- [x] T11. Integrate unified gate into CLI report commands

  **What to do**:
  - Route CLI export/report commands through `ReportReleaseGate` prior to generation.
  - Ensure fail-closed behavior with explicit insufficiency output.

  **Must NOT do**:
  - Do not allow any CLI report command to bypass gate checks.

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: `development/nodejs-backend-patterns`, `code-quality/error-handling-patterns`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: T16
  - **Blocked By**: T10

  **References**:
  - `src/solstein/cli.py` - CLI entrypoints for report generation.
  - `src/solstein/exporters/markdown/generator.py` - downstream exporter behavior.
  - `tests/unit/test_synthetic_gate.py` - expected synthetic-fail semantics.

  **Acceptance Criteria**:
  - [x] CLI paths call gate before export writing.
  - [x] Failures return actionable reason summary and non-zero exit.

  **QA Scenarios**:
  - Scenario: CLI export succeeds on passing dataset
    Tool: Bash
    Steps: run Eneve CLI export with passing fixture.
    Expected: export file created and gate pass logged.
    Evidence: `.sisyphus/evidence/task-T11-cli-happy.txt`
  - Scenario: CLI export blocked on synthetic/invalid data
    Tool: Bash
    Steps: run CLI export on synthetic fixture.
    Expected: command exits non-zero with explicit gate failure reason.
    Evidence: `.sisyphus/evidence/task-T11-cli-gate-error.txt`

  **Commit**: NO

- [x] T12. Integrate unified gate into API/export service paths

  **What to do**:
  - Ensure API-triggered exports and service-layer report paths use the same gate service.
  - Standardize API error payload for gate failures.

  **Must NOT do**:
  - Do not keep separate API-only gate branches.

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: `development/api-design-principles`, `code-quality/error-handling-patterns`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: T16
  - **Blocked By**: T10

  **References**:
  - `src/solstein/api/routers/` - API paths invoking report/export flows.
  - `src/solstein/api/services/` - service-layer orchestration points.
  - `src/solstein/exceptions.py` - shared exception mapping.

  **Acceptance Criteria**:
  - [x] API export endpoints invoke the same gate as CLI.
  - [x] API responses include structured gate failure codes/reasons.

  **QA Scenarios**:
  - Scenario: API export endpoint passes valid dataset
    Tool: Bash
    Steps: call export endpoint with valid input via `curl`.
    Expected: 2xx response and export created.
    Evidence: `.sisyphus/evidence/task-T12-api-happy.txt`
  - Scenario: API export endpoint blocks invalid dataset
    Tool: Bash
    Steps: call export endpoint with low-confidence/synthetic fixture.
    Expected: 4xx/5xx (policy-defined) with gate reason payload.
    Evidence: `.sisyphus/evidence/task-T12-api-gate-error.txt`

  **Commit**: NO

- [x] T13. Persist escalation and release audit records

  **What to do**:
  - Record paid-escalation reasons, source decisions, and release gate decisions in auditable storage.
  - Ensure audit trail links company, field, source, confidence, and decision outcome.

  **Must NOT do**:
  - Do not log ambiguous/non-attributable release decisions.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `database/postgresql-table-design`, `code-quality/defense-in-depth`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: T16
  - **Blocked By**: T2, T5

  **References**:
  - `src/solstein/infrastructure/database_models.py` - persistence model patterns.
  - `src/solstein/infrastructure/repositories.py` - repository write conventions.
  - `scripts/auto_enrich_real_data.py` - escalation decision points to audit.

  **Acceptance Criteria**:
  - [x] Each paid escalation has persisted reason + field-level context.
  - [x] Each release decision has persisted pass/fail + reason set.

  **QA Scenarios**:
  - Scenario: successful escalation decision is audited
    Tool: Bash
    Steps: run paid escalation flow and query audit records.
    Expected: audit row includes company, field, source, reason, timestamp.
    Evidence: `.sisyphus/evidence/task-T13-audit-happy.txt`
  - Scenario: gate rejection audited
    Tool: Bash
    Steps: run export on failing dataset and inspect audit records.
    Expected: rejection event persisted with deterministic reason codes.
    Evidence: `.sisyphus/evidence/task-T13-audit-gate-error.txt`

  **Commit**: YES
  - Message: `feat(audit): persist escalation and release-gate decisions`

- [x] T14. Add tests-after wave for gate, free->paid, and no-fabrication behavior

  **What to do**:
  - Add/extend tests for: synthetic-block negative, real-only positive, no fabricated zeros, free-first then paid behavior, and stale-data gate rejection.
  - Ensure tests assert reason codes/messages, not only pass/fail.

  **Must NOT do**:
  - Do not rely on only smoke tests that validate file creation.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `testing/python-testing-patterns`, `code-quality/testing-anti-patterns`

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3
  - **Blocks**: T16, F2
  - **Blocked By**: T4, T5, T10, T11, T12

  **References**:
  - `tests/unit/test_synthetic_gate.py` - synthetic-block baseline.
  - `tests/unit/test_completeness.py` - completeness test baseline.
  - `tests/integration/` - integration pattern for end-to-end quality checks.

  **Acceptance Criteria**:
  - [x] New/updated tests cover release gate behavior and free->paid orchestration semantics.
  - [x] Test suite includes negative and edge cases for contradictory/stale/malformed inputs.

  **QA Scenarios**:
  - Scenario: targeted test subset passes
    Tool: Bash
    Steps: run relevant pytest modules for gate and orchestration.
    Expected: all added tests pass with deterministic output.
    Evidence: `.sisyphus/evidence/task-T14-tests-happy.txt`
  - Scenario: regression fixture triggers expected failure
    Tool: Bash
    Steps: run failing fixture test intentionally violating no-fabrication rule.
    Expected: test fails with expected assertion message when rule broken.
    Evidence: `.sisyphus/evidence/task-T14-regression-error.txt`

  **Commit**: YES
  - Message: `test(gate): add behavior coverage for real-only and free-paid orchestration`

- [x] T15. Automate readiness checklist and runbook alignment

  **What to do**:
  - Convert manual checklist items into executable checks or artifact verifications.
  - Align docs/runbook so operational steps reflect enforced automation.

  **Must NOT do**:
  - Do not leave manual sign-off as the sole release authority.

  **Recommended Agent Profile**:
  - **Category**: `writing`
  - **Skills**: `code-quality/codebase-documenter`, `code-quality/verification-before-completion`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocks**: T16, F1
  - **Blocked By**: T9, T10

  **References**:
  - `docs/client-data-readiness-checklist.md` - checklist to automate.
  - `scripts/run_data_refresh_cycle.py` - freshness/delta checks to surface.
  - `scripts/run_research_queue.py` - queue drain checks for readiness.

  **Acceptance Criteria**:
  - [x] Runbook references executable checks with exact commands.
  - [x] Checklist links to deterministic artifacts/evidence paths.

  **QA Scenarios**:
  - Scenario: readiness script-runbook alignment
    Tool: Bash
    Steps: execute documented commands in order from runbook.
    Expected: commands run successfully and generate listed artifacts.
    Evidence: `.sisyphus/evidence/task-T15-runbook-happy.txt`
  - Scenario: missing artifact causes readiness failure
    Tool: Bash
    Steps: remove/rename required artifact and run readiness flow.
    Expected: readiness fails with clear missing-artifact error.
    Evidence: `.sisyphus/evidence/task-T15-missing-artifact-error.txt`

  **Commit**: YES
  - Message: `docs(ops): automate readiness checklist and align runbook`

- [x] T16. Execute end-to-end Eneve dry-run and produce evidence pack

  **What to do**:
  - Run full enrichment -> queue -> refresh -> export pipeline on Eneve dataset.
  - Collect consolidated evidence for pass/fail outcomes and unresolved paid-gap rationale.

  **Must NOT do**:
  - Do not mark run successful without complete evidence files for gate decisions.

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: `code-quality/verification-before-completion`, `debugging/systematic-debugging`

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3
  - **Blocks**: F1, F2, F3, F4
  - **Blocked By**: T3, T4, T5, T8, T9, T10, T11, T12, T13, T14, T15

  **References**:
  - `scripts/run_eneve_199.py` - end-to-end command entrypoint.
  - `data/input/competitor_data_real_enriched.json` - target input artifact.
  - `data/output/research_queue.json` - unresolved gaps post-free pass.
  - `data/output/refresh/delta_report.json` - freshness/delta evidence.

  **Acceptance Criteria**:
  - [x] End-to-end run produces either compliant export or explicit blocked release with reasons.
  - [x] Evidence directory contains logs/artifacts for each gate and orchestration stage.

  **QA Scenarios**:
  - Scenario: compliant path succeeds end-to-end
    Tool: Bash
    Steps: run full pipeline with valid enriched input and capture outputs.
    Expected: export generated only if gate passes; all stage artifacts present.
    Evidence: `.sisyphus/evidence/task-T16-e2e-happy.txt`
  - Scenario: insufficiency path blocks export cleanly
    Tool: Bash
    Steps: run full pipeline with intentionally insufficient fixture.
    Expected: export blocked with clear unresolved-gap reason summary and audit trail.
    Evidence: `.sisyphus/evidence/task-T16-e2e-blocked-error.txt`

  **Commit**: NO

---

## Final Verification Wave (MANDATORY)

- [x] F1. **Plan Compliance Audit** - `oracle`
  - Verify each Must Have / Must NOT Have against implementation and evidence files.
  - Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT`.

- [x] F2. **Code Quality Review** - `unspecified-high`
  - Run `PYTHONPATH=src mypy .`, `ruff check .`, `pytest -q`.
  - Check for silent catches, dead code, regression indicators.
  - Output: `Typecheck | Lint | Tests | Files clean/issues | VERDICT`.

- [x] F3. **Full QA Replay** - `unspecified-high`
  - Execute every task QA scenario and verify evidence artifacts exist.
  - Output: `Scenarios [N/N] | Integration [N/N] | Edge cases tested [N] | VERDICT`.

- [x] F4. **Scope Fidelity Check** - `deep`
  - Compare task specs vs changed files and ensure no out-of-scope creep.
  - Output: `Tasks compliant [N/N] | Contamination [CLEAN/issues] | VERDICT`.

---

## Commit Strategy

- Group 1 (Wave 1): `feat(data): establish source policy, provenance contract, and queue semantics`
- Group 2 (Wave 2): `feat(gate): enforce unified release gate and paid-gap escalation controls`
- Group 3 (Wave 3): `test(quality): add gating and free-vs-paid behavior coverage`
- Group 4 (Final docs/runbook): `docs(ops): align readiness automation and execution runbook`

---

## Success Criteria

### Verification Commands
```bash
PYTHONPATH=src pytest tests/unit/test_synthetic_gate.py -q
PYTHONPATH=src pytest tests/unit/test_completeness.py -q
PYTHONPATH=src python scripts/auto_enrich_real_data.py --input data/input/competitor_data_real.json --output data/input/competitor_data_real_enriched.json
PYTHONPATH=src python scripts/run_data_refresh_cycle.py --input data/input/competitor_data_real_enriched.json
PYTHONPATH=src python scripts/run_eneve_199.py --input data/input/competitor_data_real_enriched.json
```

### Final Checklist
- [x] All exports pass through one release gate path.
- [x] No synthetic/mixed-invalid records in client export artifacts.
- [x] No fabricated numeric defaults for missing metrics.
- [x] Free-pass completes before any paid escalation call.
- [x] Paid escalation logs contain per-field reason and policy linkage.
- [x] Queue/delta/freshness artifacts are deterministic and auditable.
