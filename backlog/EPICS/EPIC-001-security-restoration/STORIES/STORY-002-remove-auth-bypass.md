# STORY-002: Remove Authentication Bypass on Core Endpoints

| Field | Value |
|-------|-------|
| Status | ⚫ Superseded |
| Superseded By | [STORY-068: Remove Auth Bypass and Wire Supabase JWT Middleware](../../../EPIC-020-supabase-auth-migration/STORIES/STORY-068-supabase-jwt-middleware.md) |
| Priority | P0 |
| Severity | CRITICAL |
| Epic | [EPIC-001: Security Restoration](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-001](STORY-001-real-password-hashing.md) (Real password hashing must exist before enforcing authentication) |

---

## The Audit Verdict

> `api/middleware/security.py` lines 62–63 contain an explicit bypass list. The endpoints `/companies` and `/enrichment` — the platform's primary data surfaces — are on it. These endpoints skip the authentication middleware entirely. The bypass is not conditional, not environment-gated, and not logged.

## Problem Statement

The authentication middleware in `security.py` checks an allowlist of paths that skip token validation. `/companies` and `/enrichment` are on this list, meaning any HTTP client can retrieve all company intelligence data and trigger enrichment operations without presenting a JWT. The bypass is unconditional — it applies in every environment, including production.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Security** | Complete data exposure — no token required to access core endpoints |
| **Data Integrity** | Enrichment operations can be triggered by unauthenticated actors |
| **Audit Trail** | Unauthenticated access is not logged; there is no record of unauthorized data retrieval |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/api/middleware/security.py` | Modify | Lines 62–63: remove bypass allowlist entries for /companies and /enrichment |
| `tests/unit/test_security_middleware.py` | Add | Tests confirming each endpoint requires a valid token |

## Architectural Requirements

*What the system must satisfy. No implementation instructions. No code. Only what — never how.*

- **REQ-1**: The bypass allowlist must contain only genuinely public routes: `/health`, `/docs`, `/openapi.json`, `/auth/login`
- **REQ-2**: Each entry in the bypass allowlist must have an inline comment explicitly documenting why that route is public
- **REQ-3**: The bypass mechanism must not be re-implemented at the router or endpoint level via decorators or conditionals
- **REQ-4**: Requests to protected routes without a valid token must return HTTP 401 before any business logic executes

## Acceptance Criteria

- [ ] GET /companies without an Authorization header returns HTTP 401
- [ ] GET /enrichment without an Authorization header returns HTTP 401
- [ ] GET /health without an Authorization header returns HTTP 200
- [ ] GET /docs without an Authorization header returns HTTP 200
- [ ] POST /auth/login without an Authorization header returns HTTP 200 or 400 (not 401)

## Definition of Done

**Tests Required:**
- [ ] Integration test: each protected endpoint with no token → 401
- [ ] Integration test: each protected endpoint with valid token → not 401
- [ ] Integration test: each public endpoint with no token → 200

**Documentation Required:**
- [ ] Inline comments on bypass list entries explaining why they are public

**Code Review Gate:**
- [ ] Reviewer confirms the bypass list has no business data endpoints
- [ ] Reviewer confirms no endpoint-level auth bypass exists (no `skip_auth` decorators or similar)

## Notes

This story depends on STORY-001 because removing the bypass is pointless if the authentication it activates accepts any credentials. The two must ship together, but STORY-001 must be implemented first to avoid a window where endpoints require auth that is itself broken.
