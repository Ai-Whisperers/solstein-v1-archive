# STORY-130: Add Structured Logging to All Adapter Exception Handlers

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | Critical |
| **Epic** | EPIC-034: Exception Handling Transparency |
| **Created** | 2026-03-01 |
| **Dependencies** | STORY-132 (Exception Standards Document), EPIC-014 (Observability Infrastructure) |

---

## The Audit Verdict

> `data/fetchers.py:55-57` — yfinance wrapper returns `None` on any failure. `research/signals.py` has 12+ locations returning `None` without logging. `research/gather.py`, `research/evidence.py` have multiple `None` returns without logging.

---

## Problem Statement

The research pipeline is full of black holes. An adapter fails, catches the exception, returns `None`, and the pipeline continues as if nothing happened. The analyst gets a report with missing data and no indication that anything went wrong. The logs show a successful pipeline run. This is not resilience; it is data corruption with a clean conscience.

The scope of the problem is not trivial. The audit identified 12+ silent failure locations in `research/signals.py` alone — a single file that apparently treats exception handling as an optional feature. The yfinance wrapper in `data/fetchers.py` is particularly egregious: it wraps an entire external API call in a handler that returns `None` on any failure, making it impossible to distinguish a network timeout from a delisted ticker from a malformed response. Every failure mode produces the same output: silence.

The downstream effect is a research pipeline that is structurally incapable of reporting its own health. When a data source goes down, the pipeline does not alert. When an API key expires, the pipeline does not alert. When a company's ticker is invalid, the pipeline does not alert. The analyst receives a report, notices some fields are empty, and either assumes the data doesn't exist or files a support ticket. The support ticket goes to a developer who has no logs to examine. The developer adds a print statement, deploys, and waits for the next failure. This is not a workflow; it is archaeology.

Every exception that results in missing data must be logged with enough context to diagnose the failure without re-running the pipeline: which adapter failed, which company was being researched, which endpoint was called, what the error was, and whether it is likely to be transient or persistent.

---

## Impact

| Dimension | Impact |
|-----------|--------|
| **Data Quality** | Missing data fields are indistinguishable from legitimately absent data; analysts cannot assess report completeness |
| **Observability** | No visibility into adapter health; a data source can be down for days before anyone notices |
| **Trust** | Platform presents complete-looking reports that are silently incomplete; analyst trust erodes when gaps are discovered manually |
| **Debuggability** | No diagnostic information means every investigation starts from zero; developers must instrument code to reproduce failures |
| **Reliability** | No error signals means no circuit breaking, no retry logic, no fallback triggering — all of which require knowing that a failure occurred |
| **Operational Cost** | Support tickets for "missing data" that could be self-diagnosed from logs; developer time spent on archaeology instead of features |

---

## Affected Files

| File | Issue |
|------|-------|
| `data/fetchers.py:55-57` | yfinance wrapper catches all exceptions and returns `None` with no logging |
| `research/signals.py` | 12+ exception handlers return `None` without logging; bare `except` clauses present |
| `research/gather.py` | Multiple `None` returns in exception handlers without logging |
| `research/evidence.py` | Multiple `None` returns in exception handlers without logging |
| `analytics/scorers/growth_momentum.py` | Exception handlers return `None` without logging in scoring path |
| `analytics/scorers/financial_health.py` | Exception handlers return `None` without logging in scoring path |

---

## Architectural Requirements

- Every `try/except` block that currently returns `None` must emit a structured log entry before returning; the log entry must include: `adapter_name`, `company_id`, `endpoint_url` (if applicable), `error_type` (exception class name), `error_message`, `stack_trace` (at WARNING level or above), and `trace_id` (correlation ID for the research job)
- Log level must reflect error severity: `WARNING` for transient errors expected to self-resolve (HTTP 429, 503, connection timeout), `ERROR` for persistent errors requiring intervention (HTTP 401, 403, 500, invalid ticker, schema mismatch)
- Structured logging format must be JSON-serializable for machine parsing and log aggregation; human-readable format is secondary
- All logs from a single research job (single company analysis run) must share a `trace_id` correlation identifier, enabling reconstruction of the full failure timeline for a given job
- No bare `except:` clauses — all exception handlers must name the specific exception type(s) being caught; `except Exception` is acceptable only as a final catch-all and must be accompanied by a log at `ERROR` level
- The yfinance wrapper must distinguish between: ticker not found (permanent failure, do not retry), network error (transient, may retry), rate limit (transient, back off), and data parsing error (permanent for this ticker, log and skip)
- Adapter-level error counts must be trackable: the logging format must include fields that allow aggregation by adapter name and error type in a log query
- Log aggregation visibility: errors must be visible in the monitoring dashboard within the constraints of EPIC-014's delivery timeline

---

## Acceptance Criteria

- [ ] All `try/except` blocks in the six affected files that previously returned `None` without logging now emit a structured log entry before returning
- [ ] Every log entry includes `adapter_name`, `company_id`, `error_type`, and `error_message` at minimum
- [ ] Log entries for transient errors (429, 503, timeout) use `WARNING` level; log entries for persistent errors (401, 403, 500, invalid data) use `ERROR` level
- [ ] All log entries are JSON-serializable (no raw exception objects, no non-serializable types)
- [ ] All log entries from a single research job share a `trace_id` field
- [ ] Zero bare `except:` clauses remain in any of the six affected files (verified by `grep -r "except:" <files>` returning empty)
- [ ] The yfinance wrapper classifies at least three distinct failure modes with different log messages and levels
- [ ] Injecting a network failure in `data/fetchers.py` produces a `WARNING`-level structured log entry with `adapter_name: yfinance` and the company ID
- [ ] Injecting an authentication failure in any adapter produces an `ERROR`-level structured log entry

---

## Definition of Done

- **Tests Required**: For each of the six affected files, at least one test that injects a failure at the external call boundary and asserts: (1) a log entry is emitted, (2) the log entry contains the required fields, (3) the log level is correct for the error type. Tests must use log capture (not stdout capture) to verify structured log output.
- **Documentation Required**: Update each adapter's module-level docstring to describe its error handling behavior and what callers should expect when data is unavailable. Add a section to the research pipeline documentation describing how to interpret missing data fields in reports.
- **Code Review Gate**: Reviewer checks each modified file for: (1) no bare `except:` clauses, (2) log entries present in all exception handlers, (3) correct log levels for error types, (4) `trace_id` present in all log entries, (5) JSON-serializable log fields.

---

## Notes

The `trace_id` correlation identifier requires a mechanism to propagate a job-level identifier through the research pipeline. If no such mechanism exists, this story must either create a minimal one (e.g., a context variable or thread-local) or document the gap and accept that `trace_id` will be absent until the infrastructure is in place. Do not block logging on the absence of `trace_id` — log without it rather than not logging at all.

The six files listed in Affected Files are the **confirmed** locations from the audit. Developers implementing this story should scan the full research pipeline for additional silent failure locations and include them in scope. The audit was not exhaustive.

The yfinance wrapper deserves special attention. yfinance is a third-party library with inconsistent error behavior — it sometimes raises exceptions, sometimes returns empty DataFrames, and sometimes returns DataFrames with NaN values for invalid tickers. The wrapper must handle all three cases explicitly and log appropriately for each. An empty DataFrame is not the same as an exception, and neither is the same as a DataFrame full of NaN.

This story has the broadest file coverage in EPIC-034. It should be implemented after STORY-132 (standards document) so that the logging format and exception classification conventions are established before implementation begins. Implementing before the standards are defined risks inconsistent patterns across the six files — which is exactly the problem this epic is trying to solve.

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This story currently carries a historical open or in-progress backlog badge.
- If `planning/QUEUE.md` does not currently list this story as active work, treat it as triage-required rather than immediately actionable.

### Next Agent Action

- Reconcile this story against current code reality, `planning/QUEUE.md`, and the develop autonomy audit before starting.
- Do not begin implementation from this file alone unless the queue or a fresh planning decision reactivates it.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`, `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`, and `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Preserve machine-checkable enforcement and avoid prose-only or speculative "AI slop" updates.

### Minimum Verification For Future Agents

- If this story is reactivated, update the queue or controlling planning artifact first.
- Then prove the work with the smallest relevant regression tests, gates, or generated artifacts for the touched boundary.
