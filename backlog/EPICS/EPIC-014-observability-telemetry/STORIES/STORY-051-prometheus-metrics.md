# STORY-051: Add Prometheus Metrics Endpoints

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P2 |
| Severity | MEDIUM |
| Epic | [EPIC-014: Observability & Telemetry](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-047: Replace Fake Health Checks](STORY-047-replace-fake-health-checks.md), [STORY-048: Wire LLM Cost Tracking](STORY-048-wire-llm-cost-tracking.md) |

---

## The Audit Verdict
> No Prometheus metrics endpoint exists. Request rates, error rates, LLM call latency, research job queue depth, and database connection pool utilization are all invisible to any monitoring system. The platform cannot be placed behind any standard alerting infrastructure.

## Problem Statement
Without a metrics endpoint, the platform cannot be monitored by any standard infrastructure monitoring tool (Prometheus, Grafana, Datadog, CloudWatch). SLA guarantees cannot be verified because there is no measurement. Alerting on elevated error rates, latency spikes, or resource exhaustion is impossible. The platform operates entirely on faith.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Operations** | No alerting capability — errors, latency spikes, and resource exhaustion are invisible until a user reports them |
| **SLA** | Cannot verify or demonstrate performance guarantees — no measurement data exists |
| **Capacity Planning** | Resource usage (database connections, LLM API calls, memory) is invisible — scaling decisions are made by guessing |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/api/main.py` | Modify | Add `/metrics` endpoint |
| New metrics collection module | Add | Centralised metrics registry and instrumentation |

## Architectural Requirements
*What the system must satisfy. No implementation instructions. No code. Only what — never how.*

- **REQ-1**: A `/metrics` endpoint must export Prometheus-compatible metrics in the standard text exposition format
- **REQ-2**: Required metrics: HTTP request rate by endpoint and status code, HTTP request latency histogram by endpoint, LLM call count by provider, LLM call latency histogram by provider, LLM estimated cost counter by provider, research job queue depth, active research jobs count, database connection pool utilization
- **REQ-3**: The metrics endpoint must not require authentication (standard Prometheus scraping convention) — document this explicitly as a deliberate security decision
- **REQ-4**: Metric names must follow Prometheus naming conventions (snake_case, unit suffix where applicable, e.g., `solstein_http_request_duration_seconds`)

## Acceptance Criteria
- [ ] `GET /metrics` returns valid Prometheus text exposition format
- [ ] HTTP request rate metrics update in real-time when requests are made
- [ ] LLM call metrics are present and accurate after research jobs run
- [ ] Prometheus can scrape the endpoint without errors

## Definition of Done

**Tests Required:**
- [ ] Integration test: `/metrics` returns valid Prometheus format (parseable by the Prometheus client library)
- [ ] Test: making an API call increments the corresponding request counter
- [ ] Test: each required metric is present in the output

**Documentation Required:**
- [ ] Metrics catalogue documenting each metric name, type (counter/gauge/histogram), labels, and meaning
- [ ] Security note documenting that `/metrics` is unauthenticated by design

**Code Review Gate:**
- [ ] Reviewer confirms all required metrics are present
- [ ] Reviewer confirms metric names follow Prometheus naming conventions

## Notes
This story depends on STORY-047 (real health checks) and STORY-048 (LLM cost tracking) because several metrics depend on data those stories produce. The metrics endpoint should use an established Prometheus client library rather than manually formatting the text exposition format. The unauthenticated endpoint is standard for Prometheus but must be explicitly documented — it is a deliberate decision, not an oversight. Consider network-level access control (metrics endpoint only accessible from the monitoring network) rather than application-level authentication.
