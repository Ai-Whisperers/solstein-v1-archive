# STORY-067: Migrate Authentication to Supabase Auth

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P1 |
| Severity | CRITICAL |
| Epic | [EPIC-020: Supabase Auth Migration](../README.md) |
| Supersedes | [STORY-001](../../EPIC-001-security-restoration/STORIES/STORY-001-real-password-hashing.md), [STORY-003](../../EPIC-001-security-restoration/STORIES/STORY-003-jwt-secret-rotation.md) |
| Created | 2026-02-28 |
| Dependencies | [EPIC-002](../../EPIC-002-configuration-integrity/README.md) (config must be clean) |

---

## The Audit Verdict

> `api/routers/auth.py` lines 57–60 accept any credential pair (`# Demo: Accept any credentials`). Lines 83–117 implement a broken refresh endpoint that ignores the provided `refresh_token`. `config.py` lines 133 and 141–145 default the JWT secret to `change-me-in-production`. Supabase Auth replaces all three failure modes with a production-grade implementation.

## Problem Statement

The custom auth stack has three compounding failures: no password verification, a broken refresh flow, and a forgeable JWT secret. Rather than fix each individually, Supabase Auth provides a correct implementation of all three, maintained by Supabase's security team.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Security** | Supabase Auth uses bcrypt, implements proper refresh token rotation, and manages JWT secrets externally |
| **Maintenance** | Zero custom auth code to audit, patch, or debug going forward |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/api/routers/auth.py` | Modify | Replace all login/refresh/logout logic with Supabase Auth SDK calls |
| `src/solstein/config.py` | Modify | Remove JWT_SECRET field; Supabase manages this |
| `src/solstein/infrastructure/database_models.py` | Modify | Remove or migrate custom User table if Supabase Auth manages user identity |
| `tests/unit/test_auth.py` | Modify | Update to test Supabase Auth integration |

## Architectural Requirements

*What — never how. No code.*

- **REQ-1**: The `/auth/login` endpoint must delegate credential verification entirely to Supabase Auth — no password hash comparison in this codebase
- **REQ-2**: The `/auth/refresh` endpoint must delegate token refresh entirely to Supabase Auth SDK
- **REQ-3**: The `JWT_SECRET` configuration field must be removed — Supabase Auth manages JWT signing externally
- **REQ-4**: The comment `# Demo: Accept any credentials` and all associated bypass logic must be entirely removed
- **REQ-5**: User identity (user_id, email, tenant_id claim) must be extracted from the Supabase JWT, not from a local database lookup on every request
- **REQ-6**: A migration path must exist for any existing user records to be migrated to Supabase Auth

## Acceptance Criteria

- [ ] Login with wrong credentials returns HTTP 401 (Supabase enforces this)
- [ ] Token refresh uses Supabase's refresh token — not the access token
- [ ] `grep -r "change-me-in-production"` returns zero results
- [ ] `grep -r "# Demo"` returns zero results
- [ ] No custom password hashing code exists in the codebase

## Definition of Done

**Tests Required:**
- [ ] Integration test: wrong password → 401
- [ ] Integration test: expired refresh token → 401
- [ ] Integration test: valid credentials → access + refresh token returned

**Documentation Required:**
- [ ] Authentication flow documented with Supabase SDK methods

**Code Review Gate:**
- [ ] Reviewer confirms no custom password hashing or JWT signing logic remains in the codebase
- [ ] Reviewer confirms all auth endpoints delegate to Supabase Auth SDK

## Notes

This story supersedes STORY-001 (password hashing) and STORY-003 (JWT secret/refresh). Supabase Auth delivers all three outcomes — correct password verification, proper token lifecycle, and externally-managed JWT secrets — as a single migration rather than three separate fixes to a broken custom stack.
