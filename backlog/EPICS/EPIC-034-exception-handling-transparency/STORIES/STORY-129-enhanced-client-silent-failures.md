# STORY-129: Eliminate Silent None Returns in enhanced_client.py

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | Critical |
| **Epic** | EPIC-034: Exception Handling Transparency |
| **Created** | 2026-03-01 |
| **Dependencies** | None |

## The Audit Verdict

> enhanced_client.py:296 — returns None on ANY exception with NO logging.

## Problem Statement

The enhanced LLM client has a catch-all exception handler that swallows every possible error — network timeouts, authentication failures, rate limits, parsing errors — and returns None. The caller receives None and has no way to know if the LLM returned nothing, the API was down, the prompt was malformed, or the response couldn't be parsed. This is not error handling; it's error concealment. A failed LLM call looks identical to a successful call that returned no content.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Reliability** | Failures invisible to monitoring |
| **Debuggability** | No logs to diagnose issues |
| **Cost** | Silent failures trigger retries that also fail silently |

## Affected Files

| File | Issue |
|------|-------|
| `src/solstein/llm/enhanced_client.py:296` | Returns None on any exception |

## Architectural Requirements

- All exceptions logged with structured context: provider, model, prompt_id (hashed), error type, error message
- Specific exception types caught separately: TimeoutError, AuthenticationError, RateLimitError, ParseError
- None returned ONLY for legitimate "no content" responses (distinguished from errors)
- Metrics emitted: llm_requests_total, llm_errors_total (by error type)
- Circuit breaker integration: consecutive failures open circuit
- Alerting: error rate >5% triggers alert

## Acceptance Criteria

- [ ] All exceptions logged with context
- [ ] Error types distinguished in logs
- [ ] Metrics emitted for all error types
- [ ] Circuit breaker opens after N consecutive failures
- [ ] Alert fires on elevated error rate

## Definition of Done

- **Tests Required**: Inject failure at LLM call, verify structured log entry appears
- **Documentation Required**: None
- **Code Review Gate**: Reviewer verifies no bare except clauses remain

## Notes

Error concealment is worse than no error handling.
