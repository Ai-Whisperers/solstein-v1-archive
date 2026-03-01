# STORY-064: Implement Supabase Row Level Security for All Tenant-Scoped Tables

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P1 |
| Severity | HIGH |
| Epic | [EPIC-019: Multi-Tenancy & Data Isolation](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-063](STORY-063-define-tenant-model.md), [STORY-067](../../EPIC-020-supabase-auth-migration/STORIES/STORY-067-migrate-to-supabase-auth.md) (Supabase Auth — RLS policies reference auth.uid()) |

---

## The Audit Verdict

> No row-level security exists on any table. All authenticated users can query all rows. The isolation between tenants exists only as an application-level convention that can be trivially bypassed.

## Problem Statement

Application-level tenant filtering (WHERE tenant_id = ?) is bypassed by any direct database access, any ORM misconfiguration, or any future engineer who forgets to add the filter. Database-layer RLS is the only isolation guarantee that cannot be bypassed by application code.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Security** | Any authenticated user can query any other tenant's data via direct DB access or application bug |
| **Compliance** | No multi-tenant data isolation guarantee can be made to clients |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| New Supabase RLS migration/policy files | Add | RLS policies for all tenant-scoped tables |
| `src/solstein/infrastructure/database_models.py` | Modify | Verify all tables have tenant_id for policy application |
| Integration tests | Add | Cross-tenant isolation verification |

## Architectural Requirements

*What — never how. No code.*

- **REQ-1**: Supabase RLS must be ENABLED on every table that contains tenant-scoped data
- **REQ-2**: A policy must exist on each table that restricts SELECT, INSERT, UPDATE, DELETE to rows where `tenant_id` matches the authenticated user's tenant claim from Supabase Auth (auth.uid() → user's tenant)
- **REQ-3**: A service-role bypass must exist for background job operations that act on behalf of a tenant
- **REQ-4**: The RLS policies must be version-controlled as SQL migration files — not applied manually via the Supabase dashboard
- **REQ-5**: An RLS-verification test must confirm that querying the database as User A does not return User B's rows

## Acceptance Criteria

- [ ] RLS is enabled on all tenant-scoped tables
- [ ] Querying companies as Tenant A returns zero results for Tenant B's companies
- [ ] RLS policies are in version-controlled migration files
- [ ] Service role can bypass RLS for legitimate background operations

## Definition of Done

**Tests Required:**
- [ ] Integration test: authenticate as Tenant A user, query companies, assert no Tenant B rows returned
- [ ] Integration test: service role can access all rows

**Documentation Required:**
- [ ] RLS policy documentation listing each table and its policy

**Code Review Gate:**
- [ ] Reviewer confirms RLS is enabled on every tenant-scoped table
- [ ] Reviewer confirms policies are in version-controlled migration files, not dashboard-applied

## Notes

RLS policies reference `auth.uid()` from Supabase Auth, which means STORY-067 (Supabase Auth migration) must be completed before RLS policies can function. The dependency is structural, not organizational.
