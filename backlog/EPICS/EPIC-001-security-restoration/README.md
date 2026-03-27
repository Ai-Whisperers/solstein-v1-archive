> ⚫ **SUPERSEDED** — This epic has been superseded by [EPIC-020: Supabase Auth Migration](../EPIC-020-supabase-auth-migration/README.md) under Path B (Migrate Directly). The stories below are preserved for audit trail purposes. **Do not begin implementation of STORY-001 through STORY-005.** The equivalent outcomes are delivered by STORY-067 through STORY-070 via Supabase Auth.
>
> *Decision recorded: 2026-02-28. Rationale: building correct custom auth on top of broken foundations is lower ROI than migrating to Supabase Auth, which delivers the same security guarantees with a fraction of the implementation risk.*

---

# EPIC-001: Security Restoration

| Field | Value |
|-------|-------|
| Priority | **P0 — Ship Blocker** |
| Status | 🔴 Open |
| Stories | 5 |
| Created | 2026-02-28 |
| Depends On | [EPIC-002: Configuration Integrity](../EPIC-002-configuration-integrity/README.md) must complete first |

## Context

The Solstein authentication system currently accepts any username and password combination and returns a valid JWT. This is not a misconfiguration — it is intentional demo code that was never removed. The middleware layer explicitly skips authentication for `/companies` and `/enrichment` — the endpoints containing the platform's entire value proposition. JWT secrets default to `change-me-in-production`. Stack traces appear in HTTP error responses. The `security_hardening.py` module exists but is wired into fewer than 20% of the routes that need it.

This is not a security posture. This is an open warehouse with a "Security" sign on the door.

## Scope

| Story | Title | Severity |
|-------|-------|----------|
| [STORY-001](../../archive/superseded/STORY-001-real-password-hashing.md) | Implement Real Password Hashing | CRITICAL |
| [STORY-002](../../archive/superseded/STORY-002-remove-auth-bypass.md) | Remove Authentication Bypass on Core Endpoints | CRITICAL |
| [STORY-003](../../archive/superseded/STORY-003-jwt-secret-rotation.md) | Replace Default JWT Secret and Fix Token Refresh | CRITICAL |
| [STORY-004](../../archive/superseded/STORY-004-sanitize-error-responses.md) | Remove Stack Traces from HTTP Error Responses | HIGH |
| [STORY-005](../../archive/superseded/STORY-005-input-sanitization-propagation.md) | Propagate Input Sanitization to All Routers | HIGH |

## Definition of Done

- [ ] No credential pair is accepted without cryptographic hash verification
- [ ] No endpoint in the private API skips authentication middleware
- [ ] JWT secret has no hardcoded default; application fails at startup if absent
- [ ] No Python traceback, file path, or internal module name appears in HTTP error responses
- [ ] `security_hardening.py` is applied universally via a FastAPI dependency, not selectively per router

## Dependency Note

EPIC-002 (Configuration Integrity) must be resolved before beginning this epic. Authentication fixes built on top of broken configuration — duplicate class bodies, hardcoded `change-me-in-production` — will inherit those defects.
