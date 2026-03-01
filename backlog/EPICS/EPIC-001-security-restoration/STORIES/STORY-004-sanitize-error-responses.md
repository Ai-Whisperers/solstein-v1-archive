# STORY-004: Remove Stack Traces from HTTP Error Responses

| Field | Value |
|-------|-------|
| Status | ⚫ Superseded |
| Superseded By | [STORY-069: Migrate Error Handling and Input Sanitization](../../../EPIC-020-supabase-auth-migration/STORIES/STORY-069-error-handling-sanitization.md) |
| Priority | P0 |
| Severity | HIGH |
| Epic | [EPIC-001: Security Restoration](../README.md) |
| Created | 2026-02-28 |
| Dependencies | None |

---

## The Audit Verdict

> `api/exceptions.py` line 69 includes the Python traceback in the HTTP response body. Every unhandled exception broadcasts the application's internal file paths, module hierarchy, and local variable names to any caller.

## Problem Statement

Unhandled exceptions in the FastAPI exception handler return the full Python stack trace as part of the HTTP response body. This includes absolute file system paths, Python module structure, and in some cases local variable names containing sensitive data labels. Every HTTP 500 response is a free reconnaissance report for any attacker probing the system.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Security** | Attackers receive a detailed map of the internal module structure, reducing attack surface discovery time significantly |
| **Information Disclosure** | File system paths reveal deployment environment details (OS, user, directory structure) |
| **Compliance** | Violates OWASP A05:2021 (Security Misconfiguration) — verbose error messages in production |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/api/exceptions.py` | Modify | Line 69: replace traceback inclusion with opaque error ID |
| `tests/unit/test_exceptions.py` | Add/Modify | Assert response body shape excludes traceback |

## Architectural Requirements

*What the system must satisfy. No implementation instructions. No code. Only what — never how.*

- **REQ-1**: HTTP error responses must contain only a unique error ID (UUID), a user-safe message, and an HTTP status code
- **REQ-2**: No Python traceback, file path, module name, or local variable name may appear in any HTTP response body
- **REQ-3**: The complete traceback must be logged internally (via loguru) with the same error ID, enabling correlation
- **REQ-4**: A debug mode, controlled exclusively by a `DEBUG_ERRORS` environment variable defaulting to `false`, may optionally include structured additional detail — but never raw tracebacks

## Acceptance Criteria

- [ ] A triggered HTTP 500 response body contains `error_id` and `message` only
- [ ] No `Traceback (most recent call last)` string appears in any HTTP response
- [ ] The server log contains the full traceback with the same `error_id` value
- [ ] Debug mode is disabled by default and requires explicit opt-in

## Definition of Done

**Tests Required:**
- [ ] Unit test: exception handler returns correct JSON shape (`error_id`, `message` — no `traceback`, no `detail`)
- [ ] Unit test: log output contains traceback with matching `error_id`
- [ ] Unit test: with `DEBUG_ERRORS=false`, no additional detail appears in response
- [ ] Unit test: with `DEBUG_ERRORS=true`, structured detail appears but raw traceback does not

**Documentation Required:**
- [ ] `DEBUG_ERRORS` environment variable documented in configuration reference

**Code Review Gate:**
- [ ] Reviewer confirms no code path can produce a traceback in an HTTP response body
- [ ] Reviewer confirms error correlation (response `error_id` matches log `error_id`)

## Notes

This story has no dependencies and can be implemented immediately. It is one of the few P0 items that does not require EPIC-002 to be resolved first, because it does not depend on configuration integrity — it only modifies the exception handler.
