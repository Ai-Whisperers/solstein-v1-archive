# Reliability-First Intelligence Hardening Plan

## TL;DR

> **Quick Summary**: Harden Solstein's pipeline reliability first by adding deterministic contracts, stage observability, and resilient Supabase sync mechanics before expanding intelligence features.
>
> **Deliverables**:
> - Deterministic stage contracts and versioned artifacts
> - Outbox + retry + reconciliation for Supabase dual-write
> - Stage-level telemetry and reliability gates
> - Bounded contradiction lifecycle + source snapshot depth
>
> **Estimated Effort**: Large
> **Parallel Execution**: YES - 2 implementation waves + final verification wave
> **Critical Path**: Task 1 -> Task 4 -> Task 7 -> Task 9 -> Task F1-F4

---

## Context

### Original Request
Continue autonomously and deliver concrete next steps to improve data collection, validation, tracking, and reliability in the full intelligence pipeline.

### Interview Summary
**Key Discussions**:
- Priority selected: Reliability First.
- Preserve hybrid architecture: JSON artifacts remain first-class while Supabase persistence is hardened.
- Keep explainability/provenance central and avoid scope creep.

**Research Findings**:
- Pipeline stages are clear and artifactized (`src/solstein/research/pipeline.py`).
- Bottlenecks: sequential enrichment I/O, repeated full loads, duplicate serialization, weak caching.
- Best practice: schema-first contracts, claim-evidence traceability, contradiction lifecycle, deterministic gates.

### Metis Review
**Identified Gaps** (addressed in this plan):
- Missing explicit reliability guardrails (circuit breaker, DLQ/outbox, budget/rate limits).
- Missing quantitative acceptance criteria (latency/error/throughput targets).
- Assumptions needing validation (external provider behavior, partial-failure handling).

---

## Work Objectives

### Core Objective
Increase reliability and auditability of the end-to-end market intelligence pipeline so failures are recoverable, outputs are deterministic, and Supabase sync is resilient without degrading JSON artifact generation.

### Concrete Deliverables
- Versioned stage contract module used by all pipeline stages.
- Outbox-backed Supabase write path with retry and reconciliation reports.
- Stage observability artifacts with latency, retries, and gate decisions.
- Source snapshot and contradiction lifecycle records in persistence model.

### Definition of Done
- [ ] Deterministic rerun of same input produces identical artifact hash values.
- [ ] Simulated Supabase outage does not lose artifacts; retry/reconcile recovers.
- [ ] Stage report includes machine-readable reliability telemetry for all stages.
- [ ] Contradictions carry lifecycle status and resolution metadata.

### Must Have
- Deterministic run/artifact identity.
- Reliable dual-write with at-least-once retry semantics and idempotent upserts.
- Structured reliability telemetry per stage.
- Explicit contradiction lifecycle states.

### Must NOT Have (Guardrails)
- No schema-breaking refactor of unrelated analytics/export modules.
- No replacement of JSON artifacts with DB-only outputs.
- No LLM-only decisioning for pass/fail reliability gates.

### Operational Defaults Applied
- Enrichment latency target (p95): <= 30s per 25-candidate batch.
- Non-enrichment stage latency target (p95): <= 10s per stage.
- Retry policy default: max 5 attempts, exponential backoff with jitter.
- Snapshot retention baseline: 90 days for source snapshot metadata.

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** — all verification is agent-executed.

### Test Decision
- **Infrastructure exists**: YES
- **Automated tests**: Tests-after
- **Framework**: pytest
- **Agent-Executed QA**: Required for every task

### QA Policy
- **Backend/API**: `curl` assertions for status and payload fields
- **CLI/Pipeline**: command execution and file/content assertions
- **Data integrity**: artifact hash comparison and retry/reconciliation evidence
- **Evidence path**: `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`

---

## Execution Strategy

### Parallel Execution Waves

Wave 1 (foundation and reliability scaffolding):
- Task 1: Stage contracts + version metadata scaffold
- Task 2: Deterministic artifact hash/canonical serialization layer
- Task 3: Stage telemetry schema + structured reliability events
- Task 4: Outbox table/model + write-ahead persistence hooks
- Task 5: Retry/backoff policy + failure categorization utilities
- Task 6: Source snapshot model extension (`status/fetched_at/content_hash`)

Wave 2 (integration and governance):
- Task 7: Integrate outbox worker + idempotent Supabase upsert flow
- Task 8: Reconciliation job + drift report artifact
- Task 9: Contradiction lifecycle states + transitions
- Task 10: Performance pass (bounded concurrency + cache keying in enrichment path)

Wave FINAL (parallel independent review):
- Task F1: Plan compliance audit (oracle)
- Task F2: Code quality review (unspecified-high)
- Task F3: Real manual QA execution of all scenarios (unspecified-high)
- Task F4: Scope fidelity check (deep)

Critical Path: 1 -> 4 -> 7 -> 9 -> F1/F3
Parallel Speedup: ~55% faster vs strict sequential
Max Concurrent: 6 (Wave 1)

### Dependency Matrix

- **1**: blocked by none -> blocks 2, 3, 7
- **2**: blocked by 1 -> blocks 7, 8, 10
- **3**: blocked by 1 -> blocks 7, 8
- **4**: blocked by none -> blocks 7, 8
- **5**: blocked by 4 -> blocks 7, 8
- **6**: blocked by none -> blocks 8, 9
- **7**: blocked by 1, 2, 3, 4, 5 -> blocks 8, 9
- **8**: blocked by 2, 3, 4, 5, 6, 7 -> blocks F1, F3, F4
- **9**: blocked by 6, 7 -> blocks F1, F3, F4
- **10**: blocked by 2 -> blocks F2, F3

### Agent Dispatch Summary

- **Wave 1 (6 agents)**: T1 `quick`, T2 `unspecified-high`, T3 `quick`, T4 `unspecified-high`, T5 `quick`, T6 `unspecified-high`
- **Wave 2 (4 agents)**: T7 `deep`, T8 `unspecified-high`, T9 `deep`, T10 `quick`
- **Wave FINAL (4 agents)**: F1 `oracle`, F2 `unspecified-high`, F3 `unspecified-high`, F4 `deep`

---

## TODOs

- [ ] 1. Add stage contracts and version metadata

  **What to do**:
  - Create a stage-contract module with typed request/response/error envelopes for discovery, gather, reconcile, evidence, scoring, analysis, export, persist.
  - Add `artifact_schema_version`, `model_version`, `prompt_version`, and `config_hash` fields to stage artifact metadata.

  **Must NOT do**:
  - Do not redesign domain models beyond required metadata attachment.

  **Recommended Agent Profile**:
  - **Category**: `quick` - contract scaffolding and wiring updates.
  - **Skills**: `development/python-testing-patterns` (contract test coverage), `code-quality/verification-before-completion` (verification discipline).
  - **Skills Evaluated but Omitted**: `deployment/database-migration` - not DB-first task.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with 2,3,4,5,6)
  - **Blocks**: 2,3,7
  - **Blocked By**: None

  **References**:
  - `src/solstein/research/pipeline.py` - stage orchestration boundaries to contract.
  - `src/solstein/domain/models.py` - existing model payload shapes to preserve.
  - `docs/guides/data-gathering-stages.md` - intended stage semantics and artifact flow.

  **Acceptance Criteria**:
  - [ ] Contract types exist for all pipeline stages and validate at stage boundaries.
  - [ ] Every emitted artifact includes version metadata fields.

  **QA Scenarios**:
  ```
  Scenario: Contract metadata appears in stage report
    Tool: Bash (python)
    Preconditions: local env can run pipeline command
    Steps:
      1. Run pipeline once with a known seed/market test input.
      2. Open generated stage report JSON artifact.
      3. Assert fields artifact_schema_version, model_version, prompt_version, config_hash exist for each stage payload.
    Expected Result: all stage payloads include version metadata keys
    Failure Indicators: any stage payload missing one of required keys
    Evidence: .sisyphus/evidence/task-1-contract-metadata.json

  Scenario: Invalid contract payload fails fast
    Tool: Bash (pytest)
    Preconditions: unit test for malformed stage payload exists
    Steps:
      1. Execute test that injects malformed stage payload.
      2. Assert validation error type and message include failing field.
    Expected Result: deterministic validation failure before downstream stage runs
    Evidence: .sisyphus/evidence/task-1-contract-invalid.txt
  ```

  **Commit**: YES
  - Message: `feat(research): add versioned stage contracts`

- [ ] 2. Implement deterministic artifact hashing and canonical serialization

  **What to do**:
  - Add canonical JSON serialization utility for stable key ordering and numeric representation.
  - Compute per-artifact hash and persist into stage artifacts + persistence payload.

  **Must NOT do**:
  - Do not alter business scoring formulas.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high` - correctness-sensitive deterministic logic.
  - **Skills**: `code-quality/defense-in-depth`, `code-quality/verification-before-completion`.
  - **Skills Evaluated but Omitted**: `testing/test-driven-development` - tests-after strategy selected.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: 7,8,10
  - **Blocked By**: 1

  **References**:
  - `src/solstein/research/pipeline.py` - where artifacts are assembled and dumped.
  - `src/solstein/research/sources.py` - canonicalization precedent for deterministic normalization.
  - `src/solstein/infrastructure/research_dual_write.py` - persistence payload injection point.

  **Acceptance Criteria**:
  - [ ] Same input/config run twice yields identical artifact hash values.
  - [ ] Hash values are stored in stage artifacts and dual-write payload.

  **QA Scenarios**:
  ```
  Scenario: Stable hash across repeated runs
    Tool: Bash
    Preconditions: deterministic test input fixture available
    Steps:
      1. Run pipeline twice with same seed/market and fixed config.
      2. Extract artifact hash list from both stage reports.
      3. Compare lists byte-for-byte.
    Expected Result: hash lists are identical
    Failure Indicators: any hash mismatch between runs
    Evidence: .sisyphus/evidence/task-2-stable-hash.txt

  Scenario: Hash changes when payload changes
    Tool: Bash (pytest)
    Preconditions: test mutates one payload field
    Steps:
      1. Generate baseline hash for payload A.
      2. Mutate one value to payload B and recompute.
      3. Assert hash A != hash B.
    Expected Result: mutation changes hash deterministically
    Evidence: .sisyphus/evidence/task-2-hash-mutation.txt
  ```

  **Commit**: YES
  - Message: `feat(research): add deterministic artifact hashing`

- [ ] 3. Add stage-level reliability telemetry

  **What to do**:
  - Add structured per-stage telemetry fields: `stage_start`, `stage_end`, `duration_ms`, `retry_count`, `gate_decision`, `error_class`.
  - Emit telemetry to stage report and persistent run-stage records.

  **Must NOT do**:
  - Do not introduce non-structured free-form logs as primary telemetry output.

  **Recommended Agent Profile**:
  - **Category**: `quick` - instrumentation additions across known code points.
  - **Skills**: `code-quality/error-handling-patterns`, `code-quality/verification-before-completion`.
  - **Skills Evaluated but Omitted**: `infrastructure/prometheus-configuration` - no stack migration in this task.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: 7,8
  - **Blocked By**: 1

  **References**:
  - `src/solstein/research/pipeline.py` - stage execution timeline source.
  - `src/solstein/infrastructure/research_dual_write.py` - stage record write target.
  - `src/solstein/infrastructure/database_models.py` - stage record schema fields.

  **Acceptance Criteria**:
  - [ ] Each stage has duration and retry telemetry in stage report.
  - [ ] Gate decisions are machine-readable values, not prose-only strings.

  **QA Scenarios**:
  ```
  Scenario: Telemetry emitted for all stages
    Tool: Bash (python)
    Preconditions: pipeline run completed
    Steps:
      1. Parse stage report JSON.
      2. Assert all stages include duration_ms and gate_decision fields.
      3. Assert duration_ms is non-negative integer.
    Expected Result: complete telemetry coverage per stage
    Failure Indicators: missing telemetry keys or invalid duration values
    Evidence: .sisyphus/evidence/task-3-stage-telemetry.json

  Scenario: Error class captured on forced failure
    Tool: Bash (pytest)
    Preconditions: test fixture triggers known gate failure
    Steps:
      1. Run test causing source-volume/provenance failure.
      2. Assert `error_class` and `gate_decision=failed` recorded.
    Expected Result: failure is structured and attributable
    Evidence: .sisyphus/evidence/task-3-stage-error.txt
  ```

  **Commit**: YES
  - Message: `feat(research): add stage reliability telemetry`

- [ ] 4. Introduce outbox-backed write-ahead records for dual-write

  **What to do**:
  - Add outbox entity/table and enqueue events before external Supabase persistence.
  - Persist event state transitions (`pending`, `in_progress`, `succeeded`, `failed`) and error payload.

  **Must NOT do**:
  - Do not remove direct JSON artifact writes.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high` - persistence reliability patterns and state transitions.
  - **Skills**: `deployment/database-migration`, `code-quality/defense-in-depth`.
  - **Skills Evaluated but Omitted**: `database/sql-optimization-patterns` - tuning is secondary here.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: 7,8
  - **Blocked By**: None

  **References**:
  - `src/solstein/infrastructure/research_dual_write.py` - current write flow to wrap with outbox.
  - `src/solstein/infrastructure/database_models.py` - model definitions for new outbox record.
  - `supabase/migrations/003_research_runs.sql` - migration pattern and constraints style.

  **Acceptance Criteria**:
  - [ ] Outbox records are created before Supabase sync attempts.
  - [ ] Outbox state transitions are persisted with timestamps and last error.

  **QA Scenarios**:
  ```
  Scenario: Outbox record generated for pipeline run
    Tool: Bash (python/sql)
    Preconditions: dual-write enabled in local run
    Steps:
      1. Run pipeline with db dual-write enabled.
      2. Query outbox table by run_id.
      3. Assert at least one pending/succeeded event exists with event key.
    Expected Result: write-ahead outbox entries exist for run
    Failure Indicators: no outbox entries for run_id
    Evidence: .sisyphus/evidence/task-4-outbox-created.txt

  Scenario: Sync failure captured in outbox state
    Tool: Bash (pytest)
    Preconditions: test simulates Supabase connectivity failure
    Steps:
      1. Trigger dual-write path with forced network error.
      2. Assert outbox record transitions to failed with last_error populated.
    Expected Result: failure captured without data loss
    Evidence: .sisyphus/evidence/task-4-outbox-failure.txt
  ```

  **Commit**: YES
  - Message: `feat(infra): add dual-write outbox records`

- [ ] 5. Implement retry/backoff and failure categorization policy

  **What to do**:
  - Add centralized retry policy for transient failures with exponential backoff + jitter.
  - Classify failures into retryable vs terminal for outbox processing.
  - Add circuit-breaker thresholds for repeated upstream provider failures.

  **Must NOT do**:
  - Do not retry terminal schema-validation errors.

  **Recommended Agent Profile**:
  - **Category**: `quick` - policy utility plus integration points.
  - **Skills**: `code-quality/error-handling-patterns`, `code-quality/defense-in-depth`.
  - **Skills Evaluated but Omitted**: `debugging/systematic-debugging` - preemptive reliability, not bug triage.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: 7,8
  - **Blocked By**: 4

  **References**:
  - `src/solstein/infrastructure/research_dual_write.py` - retry integration point.
  - `src/solstein/config.py` - configurable retry thresholds/backoff constants.

  **Acceptance Criteria**:
  - [ ] Retryable failures are retried up to configured max attempts.
  - [ ] Terminal failures move directly to failed state without repeated retries.
  - [ ] Circuit breaker opens after threshold and records open/close events in telemetry.

  **QA Scenarios**:
  ```
  Scenario: Transient error retries then succeeds
    Tool: Bash (pytest)
    Preconditions: mocked connector fails twice then succeeds
    Steps:
      1. Execute retry policy test with transient error sequence.
      2. Assert attempt count equals 3 and final state is succeeded.
      3. Assert backoff intervals were applied.
    Expected Result: controlled retry and eventual success
    Failure Indicators: no retries or incorrect terminal state
    Evidence: .sisyphus/evidence/task-5-retry-success.txt

  Scenario: Terminal error fails once
    Tool: Bash (pytest)
    Preconditions: mocked terminal validation exception
    Steps:
      1. Run policy against terminal error.
      2. Assert zero follow-up retries and failed terminal status.
    Expected Result: immediate terminal failure classification
    Evidence: .sisyphus/evidence/task-5-terminal-failure.txt
  ```

  **Commit**: YES
  - Message: `feat(infra): add retry classification policy`

- [ ] 6. Extend source document persistence to immutable snapshots

  **What to do**:
  - Add source snapshot fields (`status`, `fetched_at`, `content_hash`, `extract_hash`) to persistence layer and artifacts.
  - Ensure canonical URL and raw URL are both retained for audit.

  **Must NOT do**:
  - Do not fetch full raw content bodies in this task if storage policy is undefined.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high` - schema + persistence extension with integrity concerns.
  - **Skills**: `deployment/database-migration`, `code-quality/defense-in-depth`.
  - **Skills Evaluated but Omitted**: `business/seo-optimizer` - irrelevant domain.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: 8,9
  - **Blocked By**: None

  **References**:
  - `src/solstein/infrastructure/database_models.py` - source document schema extension.
  - `src/solstein/infrastructure/research_dual_write.py` - mapping from artifacts to source document rows.
  - `supabase/migrations/003_research_runs.sql` - migration extension baseline.

  **Acceptance Criteria**:
  - [ ] Source records include immutable snapshot metadata fields.
  - [ ] Snapshot metadata persisted for all metric-backed sources in a run.

  **QA Scenarios**:
  ```
  Scenario: Snapshot metadata persisted for sources
    Tool: Bash (python/sql)
    Preconditions: pipeline run with sources present
    Steps:
      1. Run pipeline and capture run_id.
      2. Query source document records for run_id.
      3. Assert non-null fetched_at and content_hash for persisted sources.
    Expected Result: snapshot metadata present on source rows
    Failure Indicators: null/empty snapshot metadata fields
    Evidence: .sisyphus/evidence/task-6-source-snapshot.txt

  Scenario: Missing hash path handled gracefully
    Tool: Bash (pytest)
    Preconditions: fixture with source missing content_hash input
    Steps:
      1. Persist source without content hash.
      2. Assert fallback behavior is deterministic (null with explicit status, no crash).
    Expected Result: no pipeline crash, explicit incomplete snapshot marker
    Evidence: .sisyphus/evidence/task-6-source-missing-hash.txt
  ```

  **Commit**: YES
  - Message: `feat(infra): persist source snapshot metadata`

- [ ] 7. Integrate outbox worker with idempotent Supabase upserts

  **What to do**:
  - Build outbox consumer flow that reads pending events, writes to Supabase with idempotent keys, updates state.
  - Add `sync_status` visibility to run summary artifacts.

  **Must NOT do**:
  - Do not bypass outbox for direct writes in normal path.

  **Recommended Agent Profile**:
  - **Category**: `deep` - distributed reliability flow and idempotency behavior.
  - **Skills**: `deployment/database-migration`, `code-quality/defense-in-depth`.
  - **Skills Evaluated but Omitted**: `deployment/cicd-pipeline-generator` - runtime flow, not CI change.

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2
  - **Blocks**: 8,9
  - **Blocked By**: 1,2,3,4,5

  **References**:
  - `src/solstein/infrastructure/research_dual_write.py` - primary synchronization implementation.
  - `src/solstein/core/supabase_client.py` - Supabase connectivity and client behavior.
  - `scripts/supabase_dual_write_smoke_test.py` - validation pattern for dual-write flow.

  **Acceptance Criteria**:
  - [ ] Pending outbox events are consumed and upserted exactly-once logically via idempotent keys.
  - [ ] Failed attempts remain replayable without duplicate row creation.

  **QA Scenarios**:
  ```
  Scenario: Outbox event processed to success
    Tool: Bash (python)
    Preconditions: pending outbox event exists for run
    Steps:
      1. Execute outbox worker once.
      2. Assert outbox state moved to succeeded.
      3. Query Supabase target for matching run_id record count.
    Expected Result: succeeded state with single idempotent target row
    Failure Indicators: duplicate inserts or pending state not advancing
    Evidence: .sisyphus/evidence/task-7-outbox-success.txt

  Scenario: Replay same event does not duplicate
    Tool: Bash (pytest)
    Preconditions: event key replay fixture available
    Steps:
      1. Process same event key twice.
      2. Assert Supabase logical row count remains one.
    Expected Result: idempotent upsert behavior
    Evidence: .sisyphus/evidence/task-7-idempotent-replay.txt
  ```

  **Commit**: YES
  - Message: `feat(infra): wire outbox worker to supabase upserts`

- [ ] 8. Add reconciliation job and drift report artifact

  **What to do**:
  - Build reconciliation command/job comparing JSON source-of-truth artifacts with Supabase persisted state.
  - Emit drift report artifact with missing/mismatched entity counts and identifiers.

  **Must NOT do**:
  - Do not auto-delete records during first implementation; report-only mode first.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high` - cross-store verification logic and report generation.
  - **Skills**: `code-quality/verification-before-completion`, `code-quality/defense-in-depth`.
  - **Skills Evaluated but Omitted**: `database/sql-optimization-patterns` - correctness before optimization.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with 9,10)
  - **Blocks**: F1,F3,F4
  - **Blocked By**: 2,3,4,5,6,7

  **References**:
  - `src/solstein/research/pipeline.py` - JSON artifact shape and locations.
  - `src/solstein/infrastructure/research_dual_write.py` - persisted entity mapping.
  - `scripts/apply_supabase_migrations.py` - script conventions for operational commands.

  **Acceptance Criteria**:
  - [ ] Reconciliation output includes counts for matched, missing-in-db, missing-in-json, mismatched-hash.
  - [ ] Drift report is written as artifact and optionally persisted in run metadata.

  **QA Scenarios**:
  ```
  Scenario: Clean run yields zero drift
    Tool: Bash
    Preconditions: recent successful run synced to Supabase
    Steps:
      1. Execute reconciliation command for run_id.
      2. Assert drift report mismatched counts are zero.
    Expected Result: report indicates fully reconciled state
    Failure Indicators: unexpected mismatches in clean run
    Evidence: .sisyphus/evidence/task-8-reconcile-clean.json

  Scenario: Inject mismatch and detect drift
    Tool: Bash (pytest/sql)
    Preconditions: test fixture mutates one db field post-sync
    Steps:
      1. Run reconciliation for mutated run.
      2. Assert report includes mismatched-hash or mismatched-record entry.
    Expected Result: drift is detected and reported deterministically
    Evidence: .sisyphus/evidence/task-8-reconcile-drift.json
  ```

  **Commit**: YES
  - Message: `feat(infra): add json-vs-db reconciliation report`

- [ ] 9. Implement contradiction lifecycle states and transitions

  **What to do**:
  - Add contradiction state model: `open`, `resolved`, `ignored` with timestamps and resolver metadata.
  - Enforce valid transitions and persist lifecycle history for each contradiction record.

  **Must NOT do**:
  - Do not introduce human approval UI in this task.

  **Recommended Agent Profile**:
  - **Category**: `deep` - state machine integrity and persistence behavior.
  - **Skills**: `code-quality/defense-in-depth`, `code-quality/error-handling-patterns`.
  - **Skills Evaluated but Omitted**: `visual-engineering` - no UI scope.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with 8,10)
  - **Blocks**: F1,F3,F4
  - **Blocked By**: 6,7

  **References**:
  - `src/solstein/research/reconcile.py` - contradiction generation logic to extend with lifecycle anchors.
  - `src/solstein/infrastructure/database_models.py` - contradiction persistence schema.
  - `src/solstein/infrastructure/research_dual_write.py` - write/update flow for contradiction records.

  **Acceptance Criteria**:
  - [ ] New contradictions default to `open` state.
  - [ ] Valid transitions (`open->resolved`, `open->ignored`) persist with metadata.
  - [ ] Invalid transition attempts fail with structured error.

  **QA Scenarios**:
  ```
  Scenario: Open contradiction transitions to resolved
    Tool: Bash (pytest)
    Preconditions: contradiction fixture created in open state
    Steps:
      1. Invoke transition action to resolved with resolver metadata.
      2. Read contradiction record and lifecycle history.
      3. Assert state=resolved and transition audit fields present.
    Expected Result: valid transition recorded with metadata
    Failure Indicators: state unchanged or missing transition history
    Evidence: .sisyphus/evidence/task-9-transition-resolved.txt

  Scenario: Invalid transition is rejected
    Tool: Bash (pytest)
    Preconditions: contradiction already in resolved state
    Steps:
      1. Attempt transition resolved->open.
      2. Assert structured validation error and no state change.
    Expected Result: invalid transition blocked deterministically
    Evidence: .sisyphus/evidence/task-9-transition-invalid.txt
  ```

  **Commit**: YES
  - Message: `feat(research): add contradiction lifecycle states`

- [ ] 10. Optimize enrichment throughput with bounded concurrency and cache keys

  **What to do**:
  - Replace strictly sequential enrichment loop with bounded concurrency for external I/O operations.
  - Add cache keying for repeated ticker/profile fetches within and across runs (bounded TTL).

  **Must NOT do**:
  - Do not remove provenance and gate checks for speed gains.

  **Recommended Agent Profile**:
  - **Category**: `quick` - targeted performance optimization in constrained modules.
  - **Skills**: `debugging/debugging-strategies`, `code-quality/verification-before-completion`.
  - **Skills Evaluated but Omitted**: `deployment/performance-optimizer` - local pipeline optimization is scoped.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with 8,9)
  - **Blocks**: F2,F3
  - **Blocked By**: 2

  **References**:
  - `src/solstein/research/gather.py` - blocking external calls and enrichment logic.
  - `src/solstein/research/pipeline.py` - sequential build profile loop currently executed.
  - `src/solstein/data/fetchers.py` - caching and batch fetching patterns to align.

  **Acceptance Criteria**:
  - [ ] Enrichment stage supports configured max concurrency.
  - [ ] Baseline benchmark run shows measurable latency reduction for 20+ candidates.
  - [ ] Cache hit/miss counters are exposed in stage telemetry.

  **QA Scenarios**:
  ```
  Scenario: Concurrent enrichment reduces wall time
    Tool: Bash
    Preconditions: benchmark fixture with 20+ candidates
    Steps:
      1. Run baseline sequential benchmark and capture duration.
      2. Run bounded-concurrency benchmark with same input.
      3. Assert improved duration and successful completion count matches baseline.
    Expected Result: lower wall time without loss of processed records
    Failure Indicators: slower runtime or dropped records
    Evidence: .sisyphus/evidence/task-10-concurrency-benchmark.txt

  Scenario: Cache fallback on miss/hard failure
    Tool: Bash (pytest)
    Preconditions: forced fetch miss and transient provider error fixture
    Steps:
      1. Execute enrichment for uncached ticker with injected transient error.
      2. Assert retry/caching behavior and no uncaught exception leak.
    Expected Result: graceful handling with recorded miss/retry metrics
    Evidence: .sisyphus/evidence/task-10-cache-fallback.txt
  ```

  **Commit**: YES
  - Message: `perf(research): add bounded enrichment concurrency and caching`

---

## Final Verification Wave (MANDATORY)

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Verify all Must Have/Must NOT Have conditions against implementation and evidence files.

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Run lint/tests/type checks and inspect anti-patterns (`as any`, empty catches, dead code, noisy logs).

- [ ] F3. **Real Manual QA** — `unspecified-high`
  Execute all QA scenarios from all tasks, collect evidence under `.sisyphus/evidence/final-qa/`.

- [ ] F4. **Scope Fidelity Check** — `deep`
  Compare task specs to actual diffs; flag scope creep and unaccounted changes.

---

## Commit Strategy

- **1**: `feat(research): add deterministic stage contracts and telemetry`
- **2**: `feat(infra): add outbox retry reconciliation for dual-write`
- **3**: `feat(research): add contradiction lifecycle and source snapshots`
- **4**: `perf(research): optimize enrichment concurrency and caching`

---

## Success Criteria

### Verification Commands
```bash
pytest tests/unit/test_research_pipeline.py
pytest tests/unit/test_markdown_extractor_coverage.py
pytest tests/unit/test_cli_coverage.py
ruff check src/solstein
black --check src/solstein
```

### Final Checklist
- [ ] All Must Have conditions satisfied
- [ ] All Must NOT Have conditions satisfied
- [ ] All task-level QA evidence files captured
- [ ] Final verification wave approved by all 4 reviewers
