# STORY-404: Replace Fake Health Check with Real DB Probe

| Field | Value |
|-------|-------|
| **Status** | 🔴 Open |
| **Priority** | P1 |
| **Size** | S |
| **Epic** | [EPIC-044: Quick Wins](../README.md) |
| **Created** | 2026-03-01 |
| **Risk** | Low |

---

## Audit Verdict

> `monitoring.py` lines 96, 127 call `asyncio.sleep(0.01)` and report success — they verify nothing.

---

## Problem Statement

The health check endpoint returns 200 OK even when the database is down. This masks outages and prevents proper alerting.

---

## Impact

| Dimension | Effect |
|-----------|--------|
| **Reliability** | Health checks actually reflect system health |
| **Operations** | Alerts fire when database is down |
| **Debugging** | Can trust health endpoint for troubleshooting |

---

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|------------------|
| `src/solstein/monitoring.py` | Modify | Replace sleep with DB query |
| `tests/unit/test_health.py` | Modify | Test failure scenarios |

---

## Architectural Requirements

- **REQ-1**: Health check performs actual database query (`SELECT 1`)
- **REQ-2**: Returns 503 if database is unreachable
- **REQ-3**: Response time <100ms (fast fail)

---

## Acceptance Criteria

- [ ] Health check returns 200 when DB is up
- [ ] Health check returns 503 when DB is down
- [ ] Response time <100ms

---

## Definition of Done

- [ ] Real DB probe implemented
- [ ] Tests for both success and failure
- [ ] Deployed and verified

---

## Notes

Also addresses STORY-047 (full implementation). This quick win is the MVP version.
