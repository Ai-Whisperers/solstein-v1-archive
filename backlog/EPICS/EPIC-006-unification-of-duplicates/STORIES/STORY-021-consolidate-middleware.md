# STORY-021: Merge Duplicate Middleware Implementations

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P1 |
| Severity | HIGH |
| Epic | [EPIC-006: Unification of Duplicates](../README.md) |
| Created | 2026-02-28 |
| Dependencies | None |

---

## The Audit Verdict

> `api/middleware.py` (a file) and `api/middleware/` (a directory) both exist and both define `LoggingMiddleware`. The middleware ordering is wrong: error logging middleware runs before authentication middleware, meaning unauthenticated requests are logged as if they were authorised.

## Problem Statement

Two `LoggingMiddleware` implementations exist in the codebase: one in `api/middleware.py` (a single file) and one in `api/middleware/` (a directory package). Python's import resolution makes this particularly treacherous — `from solstein.api.middleware import LoggingMiddleware` may resolve to either implementation depending on package configuration.

Beyond the duplication, the middleware ordering is incorrect. Error logging middleware runs before authentication middleware. This means:
1. Unauthenticated requests generate log entries that lack user context
2. Error logs cannot be attributed to specific users or sessions
3. The logging middleware sees the request before authentication has validated or rejected it

## Impact

| Dimension | Effect |
|-----------|--------|
| **Observability** | Authentication context missing from error logs due to incorrect middleware ordering |
| **Security Audit** | Error logs cannot reliably identify which user triggered an error |
| **Maintainability** | Middleware changes must be applied in two places with no indication of which is active |
| **Import Resolution** | `middleware.py` vs `middleware/` package resolution is a Python footgun |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/api/middleware.py` | Evaluate/Delete | Single-file middleware implementation |
| `src/solstein/api/middleware/` | Evaluate/Retain | Directory-based middleware package |
| `src/solstein/api/middleware/logging.py` | Evaluate | Contains duplicate `LoggingMiddleware` |
| `src/solstein/api/main.py` | Modify | Middleware registration order must be corrected |

## Architectural Requirements

- **REQ-1**: One `LoggingMiddleware` implementation must exist in one location — the other must be deleted
- **REQ-2**: The non-canonical implementation must be deleted, not deprecated
- **REQ-3**: Middleware must be registered in the following order (outermost to innermost):
  1. `RateLimitMiddleware` — reject abusive requests before any processing
  2. `AuthMiddleware` — authenticate the request and establish user context
  3. `SanitizationMiddleware` — sanitise input data
  4. `LoggingMiddleware` — log the request with full authentication context
  5. `ErrorHandlingMiddleware` — catch and format unhandled exceptions
- **REQ-4**: The ordering must be documented with inline comments in `main.py` explaining each middleware's position in the chain and why that order matters

## Acceptance Criteria

- [ ] One `LoggingMiddleware` exists in one location — `grep -rn "class LoggingMiddleware" . --include="*.py"` returns exactly one result
- [ ] Middleware order in `main.py` matches the documented sequence (RateLimit → Auth → Sanitization → Logging → ErrorHandling)
- [ ] Error logs include authentication context (`user_id` or `"unauthenticated"`) for every request
- [ ] The `middleware.py` file and `middleware/` directory do not coexist — one structure is chosen

## Definition of Done

**Tests Required:**
- [ ] Middleware order unit test confirming the registration sequence matches the documented order
- [ ] Integration test confirming error logs include `user_id` for authenticated requests
- [ ] Integration test confirming error logs include `"unauthenticated"` for unauthenticated requests

**Documentation Required:**
- [ ] Inline comments in `main.py` at each middleware registration line explaining its position in the chain

**Code Review Gate:**
- [ ] Reviewer confirms only one `LoggingMiddleware` exists
- [ ] Reviewer confirms middleware order matches the documented sequence
- [ ] Reviewer verifies the Python import resolution is unambiguous (no file/directory collision)

## Notes

The `middleware.py` file vs `middleware/` directory collision is a known Python import hazard. When both exist, Python's import behaviour depends on the order of entries in `sys.path` and whether the directory has an `__init__.py`. The correct fix is to choose one structure and delete the other entirely. The directory structure (`middleware/`) is generally preferred for packages with multiple middleware classes, but only if it has a proper `__init__.py` with explicit exports.
