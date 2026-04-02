# EPIC-020: Supabase Auth Migration

| Field | Value |
|-------|-------|
| Priority | **P1 — Ship Blocker** |
| Status | 🔴 Open |
| Stories | 4 |
| Created | 2026-02-28 |
| Supersedes | [EPIC-001: Security Restoration](../EPIC-001-security-restoration/README.md) |
| Depends On | [EPIC-002: Configuration Integrity](../EPIC-002-configuration-integrity/README.md) |

## Why This Supersedes EPIC-001

EPIC-001 proposed building correct authentication from scratch: implement real password hashing, fix the broken refresh token, rotate the JWT secret. That is the right remediation if you are committed to a custom auth stack.

This codebase is already using Supabase (supabase client exists in the codebase). Supabase Auth is a production-grade, battle-tested authentication system that delivers every security requirement from EPIC-001 — correct password hashing (bcrypt), proper JWT lifecycle management, refresh token rotation, MFA, and magic links — without requiring the team to build and maintain any of it.

**Path B decision**: Do not build what Supabase already provides. Migrate to Supabase Auth and redirect the engineering effort saved toward the business logic that actually differentiates this platform.

**STORY-001 through STORY-005 are marked Superseded.** Their outcomes are delivered by STORY-067 through STORY-070.

## Scope

| Story | Title | Supersedes | Severity |
|-------|-------|-----------|----------|
| [STORY-067](STORIES/STORY-067-migrate-to-supabase-auth.md) | Migrate Authentication to Supabase Auth | STORY-001, STORY-003 | CRITICAL |
| [STORY-068](STORIES/STORY-068-supabase-jwt-middleware.md) | Remove Auth Bypass and Wire Supabase JWT Middleware | STORY-002 | CRITICAL |
| [STORY-069](STORIES/STORY-069-error-handling-sanitization.md) | Migrate Error Handling and Input Sanitization | STORY-004, STORY-005 | HIGH |
| [STORY-070](STORIES/STORY-070-ssrf-prevention.md) | Fix SSRF Vulnerability in Web and Website Agents | — (new gap) | CRITICAL |

## Definition of Done

- [ ] All authentication flows handled by Supabase Auth — no custom password hashing in this codebase
- [ ] JWT validation delegated to Supabase JWT verification — no custom JWT logic
- [ ] No endpoint bypasses authentication
- [ ] No stack traces in HTTP error responses
- [ ] Web agents do not fetch arbitrary user-supplied URLs

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This epic currently carries a historical open or in-progress backlog badge.
- If `planning/QUEUE.md` does not currently schedule this epic, treat it as triage-required backlog inventory instead of self-startable work.

### Next Agent Action

- Reconcile this epic against current code reality, `planning/QUEUE.md`, and the develop autonomy audit before selecting a story.
- Do not start implementation from this README alone unless the queue or a fresh planning decision activates the epic.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`, `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`, and `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Prefer narrow, machine-checkable progress over broad narrative backlog churn.

### Minimum Verification For Future Agents

- If this epic is reactivated, update the queue or controlling planning artifact first.
- Then execute one story at a time with the relevant tests, gates, and generated references for the touched surface.
