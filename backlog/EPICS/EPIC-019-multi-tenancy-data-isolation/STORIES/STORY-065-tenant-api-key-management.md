# STORY-065: Add Tenant-Scoped API Key Management

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P1 |
| Severity | HIGH |
| Epic | [EPIC-019: Multi-Tenancy & Data Isolation](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-063](STORY-063-define-tenant-model.md), [STORY-067](../../EPIC-020-supabase-auth-migration/STORIES/STORY-067-migrate-to-supabase-auth.md) |

---

## The Audit Verdict

> There is no API key management system. Authentication is binary — a user is authenticated or not. There is no concept of programmatic access tokens for tenant systems, no key rotation, no per-key scope limitation.

## Problem Statement

PE/VC firms integrating Solstein into their workflows need programmatic API access. Personal JWT tokens are not suitable for system-to-system integration. Without API key management, clients cannot safely integrate the platform into automated workflows.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Business** | No safe path for client system integrations without exposing personal credentials |
| **Security** | Clients using personal tokens for automation cannot rotate credentials without disrupting workflows |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/domain/models.py` | Modify | Add ApiKey entity |
| `src/solstein/infrastructure/database_models.py` | Modify | Add api_keys table |
| `src/solstein/api/routers/` | Add | API key management endpoints |
| `src/solstein/api/middleware/` | Modify | Add API key authentication path alongside Supabase JWT |

## Architectural Requirements

*What — never how. No code.*

- **REQ-1**: Each tenant must be able to create, list, rotate, and revoke API keys
- **REQ-2**: API keys must be scoped — read-only, read-write, or admin — and the scope must be enforced at the middleware layer
- **REQ-3**: API key hashes (not plaintext values) must be stored; the full key is shown only once at creation
- **REQ-4**: API key authentication must go through the same RLS context as Supabase Auth — keys must carry the tenant_id claim
- **REQ-5**: Key usage must be logged (timestamp, endpoint, response status) for audit purposes

## Acceptance Criteria

- [ ] POST /api-keys creates a key shown once in full
- [ ] A read-only key cannot call mutating endpoints
- [ ] A revoked key returns HTTP 401 immediately
- [ ] Key plaintext is not stored in the database

## Definition of Done

**Tests Required:**
- [ ] Unit test: key scoping enforcement
- [ ] Integration test: revoked key rejected
- [ ] Security test: key hash stored, not plaintext

**Documentation Required:**
- [ ] API key management endpoint documentation
- [ ] Key rotation procedure documented

**Code Review Gate:**
- [ ] Reviewer confirms no plaintext key value is stored or logged
- [ ] Reviewer confirms API key auth path sets the same tenant context as Supabase JWT auth

## Notes

API key management is a prerequisite for any enterprise integration. Without it, firms either share personal tokens (insecure) or build workarounds (fragile). This is a revenue-enabling story, not just a security one.

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
