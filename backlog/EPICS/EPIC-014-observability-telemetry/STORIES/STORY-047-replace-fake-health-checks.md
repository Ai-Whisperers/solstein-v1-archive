# STORY-047: Replace Fake Health Checks with Real Infrastructure Probes

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P2 |
| Severity | CRITICAL |
| Epic | [EPIC-014: Observability & Telemetry](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-007: Remove Hardcoded Credentials](../../EPIC-001-security-restoration/STORIES/STORY-007.md) |

---

## The Audit Verdict
> `core/monitoring.py` lines 96 and 127 implement health checks using `asyncio.sleep(0.01)` followed by returning a healthy status. No database connection is attempted. No Redis ping is performed. No LLM provider is tested. The `/health` endpoint is a lie that looks like monitoring.

## Problem Statement
A health endpoint that always returns healthy regardless of actual system state provides worse-than-no information — it actively misleads operators and load balancers. A failed database connection will not be detected until the first real request fails. A dead Redis cache will silently degrade performance with no health indication. An exhausted LLM API quota will cause request failures with no advance warning.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Operations** | Failed database or Redis connections are invisible until a production request fails — the health endpoint provides zero advance warning |
| **Load Balancing** | A dead instance continues receiving traffic because it reports healthy — load balancers route requests to broken instances |
| **Incident Response** | Health endpoint is useless for distinguishing infrastructure failures from application failures — operators cannot determine what is broken |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/core/monitoring.py` | Modify | Lines 96, 127: replace `asyncio.sleep(0.01)` with real infrastructure probes |
| `src/solstein/api/routers/health.py` | Modify | Update to surface per-component probe results |

## Architectural Requirements
*What the system must satisfy. No implementation instructions. No code. Only what — never how.*

- **REQ-1**: The `/health` endpoint must attempt a real database connection (e.g., `SELECT 1`) and report failure if it does not succeed
- **REQ-2**: The endpoint must attempt a real Redis ping and report failure if it does not succeed
- **REQ-3**: The endpoint must attempt real LLM provider reachability checks and report which providers are available
- **REQ-4**: The response must include per-component status: `{ "database": "healthy", "redis": "degraded", "llm_openai": "healthy", ... }`
- **REQ-5**: Probe failures must not crash the health endpoint — failures must be reported as component degradations, not 500 errors
- **REQ-6**: `asyncio.sleep()` must not appear anywhere in health check logic

## Acceptance Criteria
- [ ] Stopping PostgreSQL causes the health endpoint to report `"database": "unhealthy"`
- [ ] Stopping Redis causes the health endpoint to report `"redis": "unhealthy"`
- [ ] `asyncio.sleep` does not appear in monitoring.py
- [ ] The health endpoint returns 200 with component-level status detail even when components are degraded
- [ ] Individual probe failures do not crash the health endpoint

## Definition of Done

**Tests Required:**
- [ ] Integration test: stop PostgreSQL, verify health endpoint reports database unhealthy
- [ ] Integration test: stop Redis, verify health endpoint reports Redis unhealthy
- [ ] Unit test: individual probe failure is reported without crashing the endpoint

**Documentation Required:**
- [ ] Health endpoint response schema documented in API docs
- [ ] Probe configuration (timeouts, retry behaviour) documented

**Code Review Gate:**
- [ ] Reviewer confirms `asyncio.sleep` does not appear in monitoring.py
- [ ] Reviewer confirms each probe attempts a real operation, not a synthetic wait

## Notes
This is marked CRITICAL because the fake health checks actively deceive infrastructure automation. A load balancer relying on `/health` to route traffic will continue sending requests to a broken instance. This story requires STORY-007 (real database credentials) because the probes need actual connection strings to test. The LLM provider probes should align with the provider health checking already present in `llm/health_checker.py` — reuse that capability rather than reimplementing it.
