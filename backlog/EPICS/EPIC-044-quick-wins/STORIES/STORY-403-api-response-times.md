# STORY-403: Add API Response Time Headers

| Field | Value |
|-------|-------|
| **Status** | 🔴 Open |
| **Priority** | P1 |
| **Size** | S |
| **Epic** | [EPIC-044: Quick Wins](../README.md) |
| **Created** | 2026-03-01 |
| **Risk** | Low |

---

## Problem Statement

Users have no visibility into API response times. When a request is slow, they don't know if it's the API, their network, or their code.

---

## Impact

| Dimension | Effect |
|-----------|--------|
| **User Experience** | Users can see performance and report issues accurately |
| **Debugging** | Support can ask for response time headers instead of vague "it's slow" |

---

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|------------------|
| `src/solstein/api/middleware/timing.py` | Create | Add X-Response-Time header |
| `src/solstein/api/main.py` | Modify | Register middleware |

---

## Architectural Requirements

- **REQ-1**: All API responses include `X-Response-Time` header with milliseconds
- **REQ-2**: Timing starts at request entry, ends before response sent
- **REQ-3**: No impact on response time (measurement overhead <1ms)

---

## Acceptance Criteria

- [ ] `curl -I /health` shows `X-Response-Time: 15ms`
- [ ] All endpoints include the header
- [ ] Header format is consistent

---

## Definition of Done

- [ ] Middleware created and tested
- [ ] Deployed to staging
- [ ] Verified with curl

---

## Notes

This is a classic quick win: visible to users, easy to implement, no risk.
