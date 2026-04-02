# EPIC-014: Observability & Telemetry

| Field | Value |
|-------|-------|
| Priority | **P2** |
| Status | 🔴 Open |
| Stories | 5 |
| Created | 2026-02-28 |
| Depends On | [EPIC-001](../EPIC-001-security-restoration/README.md), [EPIC-002](../EPIC-002-configuration-integrity/README.md) |

## Context

The platform is currently a black box.

`core/monitoring.py` lines 96 and 127 perform `asyncio.sleep(0.01)` and report a healthy status. This is not a health check — it is a health performance. The PostgreSQL connection is never tested. The Redis connection is never tested. The LLM providers are never tested. The `/health` endpoint tells operators nothing about the actual state of the system.

`llm/enhanced_client.py` defines a 70-line `UsageTracker` class (lines 591–661) that is never called. LLM API costs are entirely invisible.

No correlation IDs exist. A request that spans the enrichment router, 4 external agents, 2 LLM calls, and a database write produces log entries with no shared identifier. Debugging a production incident requires reading logs chronologically and guessing which entries belong together.

This epic implements real observability: genuine health probes, LLM cost tracking, structured logging with correlation IDs, distributed tracing with OpenTelemetry, and Prometheus metrics.

## Scope

| Story | Title | Severity |
|-------|-------|----------|
| [STORY-047](STORIES/STORY-047-replace-fake-health-checks.md) | Replace Fake Health Checks with Real Probes | CRITICAL |
| [STORY-048](STORIES/STORY-048-wire-llm-cost-tracking.md) | Wire LLM Cost Tracking (UsageTracker) | HIGH |
| [STORY-049](STORIES/STORY-049-structured-logging-correlation-ids.md) | Add Structured Logging with Correlation IDs | HIGH |
| [STORY-050](STORIES/STORY-050-opentelemetry-tracing.md) | Implement OpenTelemetry Distributed Tracing | MEDIUM |
| [STORY-051](STORIES/STORY-051-prometheus-metrics.md) | Add Prometheus Metrics Endpoints | MEDIUM |

## Definition of Done

- [ ] `/health` endpoint returns real probe results for all critical dependencies
- [ ] Every LLM call records token usage and cost estimate
- [ ] Every request carries a correlation ID across all log entries and spans
- [ ] OpenTelemetry traces are emitted for research pipeline operations
- [ ] `/metrics` endpoint exports Prometheus-compatible metrics

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This epic currently carries a historical open or in-progress backlog badge.
- If `planning/QUEUE.md` does not currently schedule this epic, treat it as triage-required backlog inventory instead of self-startable work.

### Next Agent Action

- Reconcile this epic against current code reality, `planning/QUEUE.md`, and the develop autonomy audit before selecting a story.
- Do not start implementation from this README alone unless the queue or a fresh planning decision activates the epic.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`, `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`, and `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Prefer narrow, machine-checkable progress over broad narrative backlog churn.

### Minimum Verification For Future Agents

- If this epic is reactivated, update the queue or controlling planning artifact first.
- Then execute one story at a time with the relevant tests, gates, and generated references for the touched surface.
