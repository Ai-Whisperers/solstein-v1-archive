# STORY-129: Eliminate Silent None Returns in enhanced_client.py

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | Critical |
| **Epic** | EPIC-034: Exception Handling Transparency |
| **Created** | 2026-03-01 |
| **Dependencies** | STORY-132 (Exception Standards Document), EPIC-021 (LLM Stack Reliability) |

---

## The Audit Verdict

> `enhanced_client.py:296` — returns `None` on ANY exception with NO logging.

---

## Problem Statement

The enhanced LLM client has a catch-all exception handler that swallows every possible error — network timeouts, authentication failures, rate limits, parsing errors — and returns `None`. The caller receives `None` and has no way to know if the LLM returned nothing, the API was down, the prompt was malformed, or the response couldn't be parsed. This is not error handling; it is error concealment. A failed LLM call looks identical to a successful call that returned no content.

The downstream consequences compound the problem. Callers that receive `None` typically have their own silent handlers: they log nothing, skip the record, and continue. By the time the missing data surfaces in a report, the original failure is five stack frames away with no trace. The analyst sees a gap. The developer sees a successful pipeline run. The truth — that the LLM client crashed on every call for the past hour — is nowhere in the logs.

This is particularly costly for an LLM-powered platform. LLM API calls are expensive, rate-limited, and latency-sensitive. A silent failure that triggers a retry loop burns quota and adds latency with no diagnostic value. A silent authentication failure means every call fails until someone notices the reports are empty — which could be hours or days. The platform cannot afford to be this blind to its own most expensive operations.

---

## Impact

| Dimension | Impact |
|-----------|--------|
| **Reliability** | Failures are completely invisible to monitoring; no circuit breaking possible without error signals |
| **Observability** | Zero diagnostic information on LLM call failures; no way to distinguish error types post-hoc |
| **Cost** | Silent failures trigger retry loops that burn API quota; authentication failures waste every call until manually discovered |
| **Debuggability** | No logs to diagnose issues; root cause analysis requires code instrumentation after the fact |
| **Data Quality** | LLM-generated content silently absent from reports; analysts cannot know which sections are AI-generated vs. missing |
| **Alerting** | Error rate monitoring impossible without error signals; SLA violations go undetected |

---

## Affected Files

| File | Issue |
|------|-------|
| `src/solstein/llm/enhanced_client.py:296` | Catch-all exception handler returns `None` with no logging on any exception type |
| `src/solstein/llm/enhanced_client.py` | Entire file lacks structured error classification by exception type |
| `src/solstein/llm/health_checker.py` | Health checker may not receive failure signals if client swallows exceptions |

---

## Architectural Requirements

- All exceptions caught in the LLM client must be logged with structured context including: provider name, model identifier, prompt ID (hashed, not raw — prompts may contain sensitive data), error type (class name), error message, and HTTP status code where applicable
- Exception types must be caught separately and classified: network/timeout errors, authentication errors (401), rate limit errors (429), quota exhaustion errors (402), response parsing errors, and unexpected errors
- The distinction between "LLM returned no content" (legitimate empty response) and "call failed" (exception) must be explicit and unambiguous in both the return value and the logs
- Error metrics must be emitted for every exception: `llm_requests_total` (by provider, model, status), `llm_errors_total` (by provider, error_type), `llm_latency_seconds` (by provider, model)
- Circuit breaker integration: the client must signal consecutive failures to the health checker so the circuit can open and stop sending calls to a failing provider
- Error rate alerting threshold: when `llm_errors_total / llm_requests_total > 0.05` over a 5-minute window, an alert must be triggerable (alert definition is out of scope; the metric emission is in scope)
- No bare `except:` or `except Exception:` clauses — all exception types must be named explicitly
- The health checker (`health_checker.py`) must receive failure signals from the client, not infer health from absence of calls

---

## Acceptance Criteria

- [ ] All exceptions in `enhanced_client.py` are logged with structured context (provider, model, prompt_id_hash, error_type, error_message, http_status)
- [ ] At minimum four distinct exception types are caught and classified separately: timeout/network, authentication, rate limit, and parse error
- [ ] A legitimate "no content" response from the LLM is distinguishable from an exception-caused `None` in both return value semantics and log output
- [ ] Metrics `llm_requests_total` and `llm_errors_total` are emitted with appropriate labels on every call outcome
- [ ] The circuit breaker (or health checker) receives a failure signal on every exception, not just on explicit health check calls
- [ ] After injecting a simulated authentication failure, a structured log entry appears with `error_type: AuthenticationError` and the provider name
- [ ] After injecting a simulated rate limit response, a structured log entry appears with `error_type: RateLimitError` and the HTTP status code
- [ ] Zero bare `except:` or `except Exception:` clauses remain in `enhanced_client.py`
- [ ] The circuit breaker opens after N consecutive failures (N to be defined in configuration, default: 5)

---

## Definition of Done

- **Tests Required**: Integration test that injects failure at the LLM HTTP call level and verifies: (1) a structured log entry appears with correct fields, (2) the correct error metric is incremented, (3) the health checker records the failure. Tests for each classified exception type (timeout, auth, rate limit, parse error).
- **Documentation Required**: Inline documentation on the exception classification strategy; update to `src/solstein/llm/README.md` (or equivalent) describing error handling behavior and what callers should expect.
- **Code Review Gate**: Reviewer verifies no bare `except` clauses remain; reviewer verifies each exception type is caught specifically; reviewer verifies log fields match the structured logging schema defined in STORY-132.

---

## Notes

The prompt ID should be hashed before logging — raw prompts may contain company names, financial data, or analyst notes that should not appear in log aggregation systems. A SHA-256 hash of the first 500 characters of the prompt is sufficient for correlation without exposing content.

The circuit breaker threshold (N consecutive failures) should be configurable via environment variable, not hardcoded. Different environments (development, staging, production) may have different tolerance for provider failures.

If EPIC-021 has not yet delivered a stable provider abstraction layer, this story should still proceed — but the exception classification may need to be revisited when the abstraction stabilizes. Document this dependency explicitly in the implementation PR.

This story is the highest-priority item in EPIC-034. LLM calls are the most expensive operations in the platform. Every silent failure here costs money and produces no data.
