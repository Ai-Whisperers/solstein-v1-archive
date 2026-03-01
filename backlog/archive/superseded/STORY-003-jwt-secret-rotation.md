# STORY-003: Replace Default JWT Secret and Fix Broken Token Refresh

| Field | Value |
|-------|-------|
| Status | ⚫ Superseded |
| Superseded By | [STORY-067: Migrate Authentication to Supabase Auth](../../../EPIC-020-supabase-auth-migration/STORIES/STORY-067-migrate-to-supabase-auth.md) |
| Priority | P0 |
| Severity | CRITICAL |
| Epic | [EPIC-001: Security Restoration](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-006](../../EPIC-002-configuration-integrity/STORIES/STORY-006-fix-duplicate-config-class-bodies.md) (config.py fix), [STORY-007](../../EPIC-002-configuration-integrity/STORIES/STORY-007-remove-hardcoded-credentials.md) (hardcoded credentials) |

---

## The Audit Verdict

> Two compounding failures. First: `config.py` lines 133 and 141–145 define the JWT signing secret with the default value `change-me-in-production`. Anyone who has read the source code can forge tokens for any deployment that never set this variable. Second: `api/routers/auth.py` lines 83–117 implement `/auth/refresh` by re-decoding the access token from the Authorization header — it entirely ignores the `refresh_token` field in the request body. A stolen access token grants indefinite token generation capability.

## Problem Statement

The JWT signing secret has an insecure hardcoded default. The refresh endpoint is broken by design: it accepts an access token and returns a new access token, making the refresh token irrelevant and making access token theft permanent. There is no mechanism to revoke access.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Security (Secret)** | Any party with source code access can forge valid JWTs for any deployment that did not override the default |
| **Security (Refresh)** | A stolen access token can be used to generate unlimited new access tokens; there is no revocation path |
| **Session Management** | Expired sessions cannot be reliably terminated |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/config.py` | Modify | Lines 133, 141–145: remove default value, make JWT_SECRET required |
| `src/solstein/api/routers/auth.py` | Modify | Lines 83–117: rewrite refresh endpoint to use refresh_token field |
| `tests/unit/test_auth.py` | Add/Modify | Refresh token validation, expiry, and forgery tests |

## Architectural Requirements

*What the system must satisfy. No implementation instructions. No code. Only what — never how.*

- **REQ-1**: `JWT_SECRET` must be a required configuration field with no default value; the application must fail at startup if absent
- **REQ-2**: A separate opaque refresh token must be issued at login time, stored server-side, and used exclusively by the `/auth/refresh` endpoint
- **REQ-3**: The `/auth/refresh` endpoint must validate the `refresh_token` field from the request body, not the Authorization header
- **REQ-4**: Expired or revoked refresh tokens must return HTTP 401 with no additional detail
- **REQ-5**: Refresh token rotation must be implemented — each use issues a new refresh token and invalidates the previous one

## Acceptance Criteria

- [ ] Application fails to start if `JWT_SECRET` environment variable is not set
- [ ] POST /auth/login returns both an access_token and a refresh_token
- [ ] POST /auth/refresh with a valid refresh_token returns a new access token
- [ ] POST /auth/refresh with an expired refresh_token returns HTTP 401
- [ ] POST /auth/refresh using an access token (not a refresh token) returns HTTP 401
- [ ] Grep for `change-me-in-production` returns zero results in the codebase

## Definition of Done

**Tests Required:**
- [ ] Unit test: application startup fails with missing JWT_SECRET
- [ ] Unit test: valid refresh token → new access token
- [ ] Unit test: expired refresh token → HTTP 401
- [ ] Unit test: access token presented as refresh token → HTTP 401
- [ ] Unit test: used refresh token cannot be reused (rotation)

**Documentation Required:**
- [ ] Configuration documentation updated with JWT_SECRET as a required variable
- [ ] Refresh token flow documented in API reference

**Code Review Gate:**
- [ ] Reviewer confirms no hardcoded secret value exists anywhere in the codebase
- [ ] Reviewer confirms refresh endpoint reads from request body, not Authorization header

## Notes

This story has a dual dependency on EPIC-002 stories. The JWT secret default lives in `config.py`, which has duplicate class bodies (STORY-006). Fixing the secret default without first fixing the duplicate classes risks the fix being applied to the wrong (discarded) definition. Fix config first.
