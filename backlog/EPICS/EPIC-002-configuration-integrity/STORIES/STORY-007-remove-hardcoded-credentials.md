# STORY-007: Remove All Hardcoded Credentials from config.py

| Field | Value |
|-------|-------|
| Status | ✅ Complete |
| Priority | P0 |
| Severity | CRITICAL |
| Epic | [EPIC-002: Configuration Integrity](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-006](STORY-006-fix-duplicate-config-class-bodies.md) (Duplicate class bodies must be resolved first — otherwise the credential removal may target the discarded definition) |

---

## The Audit Verdict

> `config.py` lines 42 and 379 hardcode the PostgreSQL connection string as `postgresql://postgres:postgres@localhost:5432/solstein`. Lines 133 and 141–145 hardcode the JWT signing secret as `change-me-in-production`. Both are used as fallback defaults. Any deployment where environment variables are not set runs with publicly known credentials.

## Problem Statement

Default credential values in configuration files mean the application functions with insecure credentials when environment variables are not set. This is particularly dangerous in container orchestration environments where environment variable injection can silently fail, in CI/CD pipelines that inherit ambient credentials, and in staging environments that are often less carefully configured than production. The system provides no signal that it is running with default credentials.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Security (Database)** | PostgreSQL accessible with publicly known credentials (`postgres:postgres`) in any misconfigured deployment |
| **Security (JWT)** | JWT tokens forgeable by anyone with source code access if `JWT_SECRET` is not overridden |
| **Operational** | No startup failure indicates the misconfiguration — the system operates silently with broken security, indistinguishable from a correctly configured deployment |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/config.py` | Modify | Lines 42, 133, 141–145, 379: remove defaults, mark fields required |

## Architectural Requirements

*What the system must satisfy. No implementation instructions. No code. Only what — never how.*

- **REQ-1**: `DATABASE_URL` must have no default value; the application must raise a startup error naming the missing variable if it is absent
- **REQ-2**: `JWT_SECRET` must have no default value; same behavior
- **REQ-3**: Startup error messages must name the missing environment variable explicitly — generic "configuration error" messages are not acceptable
- **REQ-4**: No string literal in `config.py` may contain a username, password, hostname, or secret value

## Acceptance Criteria

- [ ] Starting the application without `DATABASE_URL` set produces a startup error naming `DATABASE_URL`
- [ ] Starting the application without `JWT_SECRET` set produces a startup error naming `JWT_SECRET`
- [ ] Grep for `postgres:postgres` returns zero results in the codebase
- [ ] Grep for `change-me-in-production` returns zero results in the codebase
- [ ] No string literal in `config.py` resembles a connection string, password, or secret

## Definition of Done

**Tests Required:**
- [ ] Unit test: config loads without error when all required variables are set
- [ ] Unit test: config raises `ValidationError` when `DATABASE_URL` is absent, and the error message contains the string `DATABASE_URL`
- [ ] Unit test: config raises `ValidationError` when `JWT_SECRET` is absent, and the error message contains the string `JWT_SECRET`

**Documentation Required:**
- [ ] `.env.example` file updated with all required variables (values set to placeholder descriptions, not actual credentials)

**Code Review Gate:**
- [ ] Reviewer confirms no string literal in config.py contains a credential, hostname, or secret value
- [ ] Reviewer confirms every security-sensitive field raises on absence, not on empty string only

## Notes

This story depends on STORY-006. The duplicate class body defect means credential defaults may exist in the discarded first definition, the active second definition, or both. Removing the default from only the discarded copy achieves nothing. Fix the structural defect first, then remove the credentials from the single, correct definition.
