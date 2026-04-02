# STORY-050: Implement OpenTelemetry Distributed Tracing

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P2 |
| Severity | MEDIUM |
| Epic | [EPIC-014: Observability & Telemetry](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-049: Structured Logging with Correlation IDs](STORY-049-structured-logging-correlation-ids.md) |

---

## The Audit Verdict
> No distributed tracing exists. The research pipeline is a multi-stage operation spanning HTTP, LLM calls, external agent invocations, and database writes. There is no way to understand where time is spent, which operations are slow, or how the pipeline behaves under different data inputs.

## Problem Statement
Without distributed tracing, performance profiling requires inserting manual timing code and rebuilding after every investigation. There is no production visibility into pipeline stage latencies. A research job that takes 45 seconds cannot be broken down into its constituent operations — the 45 seconds is a black box. Identifying whether the bottleneck is the LLM call, the database write, or the external agent invocation requires custom instrumentation for each investigation.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Performance** | Cannot identify which pipeline stages are slow without manual instrumentation — every performance investigation starts from scratch |
| **SLA** | Cannot demonstrate research job completion times to clients — no data exists to back SLA guarantees |
| **Debugging** | Latency spikes are invisible — a slow external agent invocation looks the same as a slow database write from the API perspective |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/api/main.py` | Modify | Add OpenTelemetry middleware |
| All pipeline and service files | Modify | Add span creation for major operations |
| New OTel configuration module | Add | OpenTelemetry SDK and exporter configuration |

## Architectural Requirements
*What the system must satisfy. No implementation instructions. No code. Only what — never how.*

- **REQ-1**: OpenTelemetry spans must be created for: each HTTP request, each LLM call, each external agent invocation, each database query, and each major pipeline stage
- **REQ-2**: Spans must be exported to a configurable OTLP endpoint (Jaeger, Tempo, or any OTLP-compatible backend)
- **REQ-3**: Span attributes must include: correlation ID, company ID where applicable, provider name for LLM calls, and operation outcome (success/failure)
- **REQ-4**: The OTLP endpoint must be configurable via environment variable; if not set, tracing must be disabled gracefully (not an error)
- **REQ-5**: Tracing must not meaningfully impact request latency (overhead < 5ms per request)

## Acceptance Criteria
- [ ] A research job produces parent/child spans covering all major operations
- [ ] Spans include `company_id`, `correlation_id`, and operation outcome attributes
- [ ] Disabling `OTLP_ENDPOINT` environment variable disables tracing without startup errors
- [ ] Trace hierarchy accurately reflects the call chain (parent spans contain child spans)

## Definition of Done

**Tests Required:**
- [ ] Integration test: research job produces traces with correct span hierarchy
- [ ] Performance test: tracing overhead < 5ms per request
- [ ] Test: missing OTLP_ENDPOINT disables tracing gracefully

**Documentation Required:**
- [ ] OTLP configuration documented in `docs/environment-variables.md`
- [ ] Span naming conventions documented for contributors

**Code Review Gate:**
- [ ] Reviewer confirms span hierarchy matches the logical call chain
- [ ] Reviewer confirms no spans are created without being properly closed

## Notes
This story builds on STORY-049's correlation IDs — the correlation ID becomes the trace ID (or a span attribute) for OpenTelemetry. The tracing SDK integration with FastAPI should use the existing OpenTelemetry FastAPI instrumentation library rather than manual span creation at the HTTP layer. Manual spans are needed for LLM calls and external agent invocations where auto-instrumentation is not available. The graceful disable (REQ-4) is critical for local development where no OTLP backend is running.

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
