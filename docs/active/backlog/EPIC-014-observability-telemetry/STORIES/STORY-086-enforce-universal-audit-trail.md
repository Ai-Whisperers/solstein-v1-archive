# STORY-086: Enforce Universal Audit Trail Across All Data Access Endpoints

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P1 |
| Severity | HIGH |
| Epic | [EPIC-014: Observability & Telemetry](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-067](../../EPIC-020-supabase-auth-migration/STORIES/STORY-067-migrate-to-supabase-auth.md) (Supabase Auth — need authenticated user identity) |

---

## The Audit Verdict

> `infrastructure/database_models.py` defines audit tables and `data/security_hardening.py` contains audit logging utilities, but audit logging is opt-in per router — fewer than 20% of endpoints actually log data access. A PE/VC firm's data access must be auditable: who viewed which company's intelligence, when, and from which client.

## Problem Statement

Selective audit logging is equivalent to no audit logging from a compliance perspective. A regulatory request or client dispute requires a complete, unbroken audit trail — not a partial one depending on which routers an engineer happened to add audit calls to.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Compliance** | Incomplete audit trail cannot satisfy regulatory or contractual audit requirements |
| **Forensics** | Data access incidents cannot be fully reconstructed from partial audit records |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/api/middleware/` | Add | Audit logging middleware that fires on every authenticated request |
| `src/solstein/data/security_hardening.py` | Modify | Ensure audit utility is the single implementation |
| `src/solstein/infrastructure/database_models.py` | Modify | Verify audit table schema is sufficient |

## Architectural Requirements

*What — never how. No code.*

- **REQ-1**: Every authenticated request to a data-returning endpoint must generate an audit log entry containing: tenant_id, user_id, endpoint, resource_id (if applicable), timestamp, response status
- **REQ-2**: Audit logging must be implemented as middleware — not as per-endpoint opt-in code
- **REQ-3**: Audit records must be written to a dedicated, append-only audit table — not mixed with application logs
- **REQ-4**: Audit records must not be deletable by application code — only by a designated admin procedure
- **REQ-5**: Audit logging failure must not fail the original request — log the audit failure separately

## Acceptance Criteria

- [ ] Every GET /api/v1/companies request generates an audit record
- [ ] The audit record contains tenant_id, user_id, and timestamp
- [ ] Application code cannot DELETE from the audit table
- [ ] An audit logging failure does not return HTTP 500 to the client

## Definition of Done

**Tests Required:**
- [ ] Integration test: API call produces audit record
- [ ] Security test: attempt to delete audit record fails
- [ ] Resilience test: audit write failure does not fail the original request

**Documentation Required:**
- [ ] Audit record schema documented
- [ ] Audit retention policy documented

**Code Review Gate:**
- [ ] Reviewer confirms audit logging is middleware-applied, not per-router opt-in
- [ ] Reviewer confirms audit write failures are handled gracefully

## Notes

This story depends on STORY-067 (Supabase Auth) because the audit record requires authenticated user identity (user_id, tenant_id) extracted from the Supabase JWT. Without authentication, there is nothing meaningful to audit — "anonymous user accessed data" is not an audit trail, it is a confession.
