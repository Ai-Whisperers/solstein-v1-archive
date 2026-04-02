# STORY-069: Migrate Error Handling and Input Sanitization to Supabase Patterns

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P1 |
| Severity | HIGH |
| Epic | [EPIC-020: Supabase Auth Migration](../README.md) |
| Supersedes | [STORY-004](../../../archive/superseded/STORY-004-sanitize-error-responses.md), [STORY-005](../../../archive/superseded/STORY-005-input-sanitization-propagation.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-067](STORY-067-migrate-to-supabase-auth.md), [STORY-068](STORY-068-supabase-jwt-middleware.md) |

---

## The Audit Verdict

> `api/exceptions.py` line 69 includes full Python stack traces in HTTP error responses. `data/security_hardening.py` is applied in 2 of 10+ routers. Both issues must be resolved as part of the auth migration — error responses that expose internal structure, and unsanitized inputs that bypass security controls.

## Problem Statement

Supabase Auth's error responses follow a consistent, opaque format that does not expose internal implementation details. The error handling migration should adopt this pattern. Input sanitization must be applied universally via the middleware registered in STORY-068.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Security** | Stack traces expose internal module structure, file paths, and variable names to attackers |
| **Consistency** | Sanitization coverage varies per-router, creating unpredictable attack vectors |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/api/exceptions.py` | Modify | Line 69: replace traceback inclusion with error ID + Supabase-compatible error format |
| `src/solstein/api/middleware/` | Modify | Integrate input sanitization into the unified middleware chain from STORY-068 |
| `src/solstein/data/security_hardening.py` | Modify | Wire universally via FastAPI Depends |

## Architectural Requirements

*What — never how. No code.*

- **REQ-1**: All HTTP error responses must follow the format `{ "error": { "code": "string", "message": "string", "error_id": "uuid" } }` — no traceback, no file paths
- **REQ-2**: The full traceback must be logged internally with the `error_id` for correlation
- **REQ-3**: Input sanitization must be applied universally via the middleware chain, not per-router
- **REQ-4**: The sanitization utilities in `security_hardening.py` must not be duplicated — referenced from one location

## Acceptance Criteria

- [ ] Triggered 500 error response contains only error_id and message — no traceback
- [ ] All string inputs across all routers pass through sanitization
- [ ] Full traceback is in server logs with the matching error_id

## Definition of Done

**Tests Required:**
- [ ] Unit test: exception handler response shape assertion
- [ ] Injection test: SQL and XSS payloads rejected at all endpoints

**Documentation Required:**
- [ ] Error response format documented in API reference
- [ ] Sanitization coverage matrix showing all routers covered

**Code Review Gate:**
- [ ] Reviewer confirms no traceback can appear in any HTTP response
- [ ] Reviewer confirms sanitization is middleware-applied, not per-router opt-in

## Notes

This story supersedes STORY-004 (error responses) and STORY-005 (input sanitization). The outcomes are identical — opaque error responses and universal input sanitization — but they are now delivered as part of the unified middleware chain established in STORY-068 rather than as patches to the custom auth stack.

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This story currently carries a historical open or in-progress backlog badge.
- If `planning/QUEUE.md` does not currently list this story as active work, treat it as triage-required rather than immediately actionable.

### Next Agent Action

- Reconcile this story against current code reality, `planning/QUEUE.md`, and the develop autonomy audit before starting.
- Do not begin implementation from this file alone unless the queue or a fresh planning decision reactivates it.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`, `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`, and `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Preserve machine-checkable enforcement and avoid prose-only or speculative "AI slop" updates.

### Minimum Verification For Future Agents

- If this story is reactivated, update the queue or controlling planning artifact first.
- Then prove the work with the smallest relevant regression tests, gates, or generated artifacts for the touched boundary.
