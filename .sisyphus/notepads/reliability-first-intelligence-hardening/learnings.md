## 2026-02-24 Task 1: Stage contracts
- Added `src/solstein/research/contracts.py` and wired version metadata into stage artifacts.
- Ruff import sorting required after stage artifact refactor.

## 2026-02-24 Task 4: Outbox write-ahead integration
- `persist_research_run` now writes/updates `outbox_records` first using idempotent `event_key=<run_id>:research_run_persist`, commits it as `pending`, then transitions `in_progress -> succeeded/failed` around persistence.
- `attempt_count` increments once per persist attempt at `in_progress`; `last_error` stores JSON `{error_type,message,recorded_at}` on failures; `available_at` remains retry-scheduling timestamp and is refreshed on transitions.

## 2026-02-24 Task 5: Source document snapshot metadata
- `source_documents` now includes immutable snapshot fields (`status`, `fetched_at`, `content_hash`, `extract_hash`) with dual-write defaulting status to `observed` and `fetched_at` to `observed_at`.

## 2026-02-24 Task 6: Stage-level reliability telemetry
- Added per-stage telemetry via a shared append helper in `src/solstein/research/pipeline.py` so every stage artifact now carries `stage_start`, `stage_end`, monotonic `duration_ms`, `retry_count=0`, `gate_decision`, and failure-only `error_class` without changing existing business flow.

## 2026-02-24 Task 7: Deterministic artifact hashing
- Added `src/solstein/research/hashing.py` for canonical JSON serialization (sorted keys, stable separators, robust normalization for common non-JSON types) + sha256 hashing.
- `src/solstein/research/pipeline.py` now emits `artifact_hashes` into `stage_report.json` and computes deterministic hashes for major artifacts; volatile fields (`last_updated`, `analysis_date`, stage timing fields) are stripped from hash inputs.
- `src/solstein/infrastructure/research_dual_write.py` wraps persisted artifact payloads with `{artifact_hash, artifact}` when a computed hash is available, without DB schema changes.
- `tests/unit/test_research_pipeline.py` asserts `artifact_hashes` are stable across two identical runs.

## 2026-02-24 Task 8: Stable hash exclusions for identical reruns
- Hash inputs for `artifact_hashes["extracted"]`, `artifact_hashes["scored"]`, and `artifact_hashes["market_analysis"]` recursively exclude ephemeral timestamp keys `last_updated` and `analysis_date`, including nested company objects inside market analysis payloads.

## 2026-02-24 Task 9: Retry/backoff and circuit breaker primitives
- Added `src/solstein/infrastructure/retry_policy.py` with deterministic hash-based jitter (no random source), explicit retryable/terminal failure classification, and a cooldown circuit breaker based on consecutive failures.

## 2026-02-24 Task 10: Outbox retry classification details
- `persist_research_run` now maps exception heuristics to `FailureClassification` and uses `RetryPolicy.evaluate` with the post-failure attempt count to set retry delay metadata in `last_error` and `available_at` for retryable failures.

## 2026-02-24 Task 7: Outbox replay worker
- Added a dedicated outbox worker that replays `research_run_persist` events by loading JSON artifacts from `output_dir` and rehydrating relational records through a persistence-only helper.
- Refactored `persist_research_run` to share persistence logic without re-enqueueing and to include `output_dir` in outbox payloads for replay safety.

## 2026-02-24 Task 7: Outbox worker ruff cleanup
- Sorted/normalized import blocks with ruff; moved `sqlalchemy.orm.Session` into `TYPE_CHECKING`.
- Updated `typing.cast()` to use a quoted type expression to satisfy TC006.

## 2026-02-24 Task 11: Dual-write ruff cleanup
- Mechanical lint pass on `src/solstein/infrastructure/research_dual_write.py`: import block normalization + `TYPE_CHECKING` placement + black formatting, with no logic changes.

## 2026-02-24 Task 9: Contradiction lifecycle
- Added lifecycle columns + transition history table; transitions are validated with a structured error and recorded with `changed_by` and `reason` metadata.

## 2026-02-24 Task 8: Reconciliation drift report
- Added `src/solstein/infrastructure/reconcile_runs.py` with report-only reconciliation that resolves `run_id`/`output_dir` via outbox payloads, loads JSON artifacts from disk as source-of-truth, compares persisted artifact hashes, and writes deterministic `reconciliation_report.json`.
- Drift accounting is explicit and deterministic (`matched`, `missing_in_db`, `missing_in_json`, `mismatched_hash`) with sorted artifact lists and canonical JSON output.
- Added `tests/unit/test_reconciliation_report.py` covering run-id lookup, output-dir lookup, mismatch/missing scenarios, and failure when outbox cannot resolve run context.
