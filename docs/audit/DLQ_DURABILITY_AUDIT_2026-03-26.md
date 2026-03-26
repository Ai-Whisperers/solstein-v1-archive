# DLQ Durability Audit — 2026-03-26

**Issues addressed:** `ISSUE-06`, `ISSUE-18`

**Bug class:** Permanently failed worker jobs were recorded only in an in-memory list, with incomplete failure detail and no durable audit trail or monitoring signal.

---

## Fix Applied

### 1. Structured durable DLQ records

**File:** `src/solstein/worker/base.py`

`DeadLetterQueue.record_failure(...)` now records a structured failure envelope with:

- `task_name`
- `task_id`
- `error`
- `error_type`
- `traceback`
- `final_attempt`
- `timestamp`
- `context`

The queue still keeps `failed_jobs` in memory for backward compatibility, but every record is now also appended to:

- `data/output/dead_letter_queue.jsonl`

This removes the “lost on worker restart” failure mode.

### 2. Monitoring signal added

**File:** `src/solstein/worker/base.py`

Every DLQ write now emits into the global monitoring error tracker:

- `global_error_tracker.track_error(...)`

This gives the failure class a real monitoring surface instead of a write-only list.

### 3. Traceback and error type preserved in task failure payloads

**Files:**

- `src/solstein/worker/enrichment_tasks.py`
- `src/solstein/worker/refresh_tasks.py`

Changes:

- max-retry failure paths now pass the real exception object into the DLQ
- traceback text is preserved explicitly
- enrichment task terminal return payloads now include:
  - `error_type`
  - `error_traceback`

This closes the original “string-only error” gap for the audited paths.

---

## Regression Coverage Added

**File:** `tests/unit/test_dlq_persistence.py`

Added focused coverage for:

- JSONL persistence of DLQ records
- monitoring emission through the global error tracker
- backward-compatible string error support
- structured task failure payload generation with traceback and type

---

## Verification

Commands run:

```bash
uv run python -m py_compile \
  src/solstein/worker/base.py \
  src/solstein/worker/enrichment_tasks.py \
  src/solstein/worker/refresh_tasks.py \
  tests/unit/test_dlq_persistence.py

DATABASE__URL=postgresql+asyncpg://user:pass@localhost/test \
SECURITY__SECRET_KEY=test-secret \
GITHUB_TOKEN=test-token \
uv run pytest tests/unit/test_dlq_persistence.py -q
```

Result:

- `3 passed`

---

## Residual Limit

The DLQ is now durable and queryable as an append-only JSONL audit trail, but it is not yet backed by a first-class database table or queue service. That is a later operational hardening step, not a blocker for resolving the original audit issues.
