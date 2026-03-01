# STORY-130: Add Structured Logging to All Adapter Exception Handlers

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | Critical |
| **Epic** | EPIC-034: Exception Handling Transparency |
| **Created** | 2026-03-01 |
| **Dependencies** | None |

## The Audit Verdict

> yfinance wrapper (data/fetchers.py:55-57) returns None on any failure. research/signals.py has 12+ locations returning None without logging. research/gather.py, research/evidence.py have multiple None returns without logging.

## Problem Statement

The research pipeline is full of black holes. An adapter fails, catches the exception, returns None, and the pipeline continues as if nothing happened. The analyst gets a report with missing data and no indication that anything went wrong. The logs show a successful pipeline run. This is not resilience; it's data corruption. Every exception that results in missing data must be logged with enough context to diagnose: which adapter, which company, which endpoint, what error.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Data Quality** | Missing data undetected |
| **Observability** | No visibility into adapter health |
| **Trust** | Platform appears healthy while failing |

## Affected Files

| File | Issue |
|------|-------|
| `data/fetchers.py` | Returns None without logging |
| `research/signals.py` | 12+ None returns without logging |
| `research/gather.py` | None returns without logging |
| `research/evidence.py` | None returns without logging |
| `analytics/scorers/growth_momentum.py` | Silent failures |
| `analytics/scorers/financial_health.py` | Silent failures |

## Architectural Requirements

- All try/except blocks that return None must log the exception with: adapter_name, company_id, endpoint_url (if applicable), error_type, error_message, stack_trace
- Log level: WARNING for transient errors (429, 503), ERROR for persistent errors (401, 403, 500)
- Structured logging format (JSON) for machine parsing
- Correlation ID: all logs from same research job share a trace_id
- Log aggregation: errors visible in monitoring dashboard
- No bare except clauses — specific exception types only

## Acceptance Criteria

- [ ] All None-returning exception handlers have logging
- [ ] Logs include adapter, company, endpoint context
- [ ] Transient vs persistent errors have appropriate log levels
- [ ] Structured JSON logging format
- [ ] grep for "except:" returns zero bare except clauses

## Definition of Done

- **Tests Required**: Inject failure in each adapter, verify structured log appears
- **Documentation Required**: None
- **Code Review Gate**: Reviewer checks each modified file for proper exception specificity

## Notes

Silent failures are data corruption.
