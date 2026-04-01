# STORY-068: Remove Auth Bypass and Wire Supabase JWT Middleware

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P1 |
| Severity | CRITICAL |
| Epic | [EPIC-020: Supabase Auth Migration](../README.md) |
| Supersedes | [STORY-002](../../../archive/superseded/STORY-002-remove-auth-bypass.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-067](STORY-067-migrate-to-supabase-auth.md) |

---

## The Audit Verdict

> `api/middleware/security.py` lines 62–63 explicitly bypass authentication for `/companies` and `/enrichment`. These are the platform's core data endpoints. The bypass must be removed and replaced with Supabase JWT verification middleware that covers all private routes.

## Problem Statement

The existing auth middleware has an allowlist that skips token validation for the most sensitive endpoints. Replacing custom JWT validation with Supabase JWT verification requires also removing this bypass, as the Supabase middleware will correctly enforce authentication on all routes not explicitly marked public.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Security** | Core data endpoints currently require no authentication whatsoever |
| **Data Exposure** | All company intelligence data is accessible to unauthenticated actors |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/api/middleware/security.py` | Modify | Remove bypass list entries; replace JWT validation logic with Supabase JWT verification |
| `src/solstein/api/main.py` | Modify | Register Supabase JWT middleware in correct order |

## Architectural Requirements

*What — never how. No code.*

- **REQ-1**: The bypass allowlist must contain only genuinely public routes: `/health`, `/docs`, `/openapi.json`, `/auth/login`, `/auth/signup`
- **REQ-2**: JWT verification must use the Supabase JWT verification mechanism — validating against Supabase's public JWKS endpoint
- **REQ-3**: The authenticated user's tenant_id claim (from the Supabase JWT) must be extracted and made available to all downstream request handlers
- **REQ-4**: Middleware ordering must be: RateLimitMiddleware → SupabaseJWTMiddleware → SanitizationMiddleware → LoggingMiddleware

## Acceptance Criteria

- [ ] GET /companies without a valid Supabase JWT returns HTTP 401
- [ ] GET /health without a token returns HTTP 200
- [ ] The tenant_id claim is accessible in request context downstream of the middleware

## Definition of Done

**Tests Required:**
- [ ] Integration test: each protected endpoint without token → 401
- [ ] Integration test: each public endpoint without token → not 401

**Documentation Required:**
- [ ] Middleware chain ordering documented
- [ ] Public route allowlist documented with justification for each entry

**Code Review Gate:**
- [ ] Reviewer confirms no business data endpoint is in the bypass allowlist
- [ ] Reviewer confirms middleware ordering matches the specified chain

## Notes

This story supersedes STORY-002. The outcome is identical — remove the auth bypass on core endpoints — but the mechanism changes from fixing the custom JWT middleware to replacing it entirely with Supabase JWT verification. The bypass was the most dangerous single line in the codebase; this story removes it permanently.
