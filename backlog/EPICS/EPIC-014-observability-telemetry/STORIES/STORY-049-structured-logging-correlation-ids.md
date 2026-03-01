# STORY-049: Add Structured Logging with Correlation IDs to All Requests

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P2 |
| Severity | HIGH |
| Epic | [EPIC-014: Observability & Telemetry](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-042: Migrate stdlib logging to loguru](../../EPIC-012-type-safety-code-quality/STORIES/STORY-042-migrate-stdlib-logging.md) |

---

## The Audit Verdict
> No correlation ID mechanism exists. A research request that spans the enrichment router, the agent coordinator, 4+ external agents, multiple LLM calls, and a database write produces log entries with no shared identifier. Debugging requires chronological log reading with no ability to isolate a single request's trace.

## Problem Statement
Without correlation IDs, production debugging requires manually reconstructing request sequences from timestamps and guesswork. In a highly concurrent system with multiple research jobs running simultaneously, this is effectively impossible. Two concurrent requests produce interleaved log entries that cannot be separated. The mean time to diagnose a production incident scales with the concurrency level.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Observability** | Individual request traces cannot be isolated from concurrent traffic — logs are an unsorted pile of events |
| **Incident Response** | Mean time to diagnose production incidents is high and scales with concurrency |
| **Operations** | No ability to identify which specific requests are causing elevated error rates |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/api/middleware/` | Add | Add correlation ID middleware that assigns a UUID to each incoming request |
| All service and agent files | Modify | Propagate correlation ID via loguru context binding |

## Architectural Requirements
*What the system must satisfy. No implementation instructions. No code. Only what — never how.*

- **REQ-1**: Every incoming HTTP request must be assigned a unique correlation ID (UUID) at the middleware layer
- **REQ-2**: The correlation ID must be propagated through all log calls for the duration of that request, including calls within agents, LLM clients, and database operations
- **REQ-3**: The correlation ID must be returned in the HTTP response as a header (e.g., `X-Correlation-ID`)
- **REQ-4**: The correlation ID must be included in every loguru log entry generated during request processing
- **REQ-5**: External calls (LLM providers, external agent APIs) must include the correlation ID in outbound request headers where the provider supports it

## Acceptance Criteria
- [ ] Every log entry for a given request includes the same correlation ID
- [ ] The HTTP response includes an `X-Correlation-ID` header
- [ ] Filtering logs by correlation ID returns all entries for that request and only that request
- [ ] Concurrent requests produce log entries with distinct correlation IDs

## Definition of Done

**Tests Required:**
- [ ] Integration test: single request produces log entries all sharing the same correlation ID
- [ ] Test: response headers include `X-Correlation-ID`
- [ ] Test: two concurrent requests produce logs with different correlation IDs

**Documentation Required:**
- [ ] Correlation ID propagation pattern documented for contributors adding new log statements

**Code Review Gate:**
- [ ] Reviewer confirms correlation ID is set at the middleware layer and propagated via loguru context
- [ ] Reviewer confirms the correlation ID appears in the response header

## Notes
This story requires STORY-042 (loguru migration) to be complete — correlation IDs propagated via loguru's `bind()` context will not appear in modules still using stdlib `logging`. The middleware approach ensures the correlation ID is set once and propagated automatically, rather than requiring every function to manually pass it. This is the foundation for STORY-050 (OpenTelemetry tracing), which will use the correlation ID as the trace ID.
