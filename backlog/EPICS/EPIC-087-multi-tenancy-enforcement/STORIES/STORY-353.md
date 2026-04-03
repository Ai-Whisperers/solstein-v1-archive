# STORY-353: Audit and Deploy PostgreSQL RLS Policies for Tenant Isolation

| Field | Value |
|---|---|
| **Status** | 🔴 READY |
| **Priority** | P1 |
| **Size** | M (2 days) |
| **Epic** | EPIC-087 Multi-Tenancy Enforcement |
| **Created** | 2026-04-03 |
| **Risk** | High — incorrect RLS policies can either lock out all data or allow all data |

---

## Problem Statement

Migration 014 enables RLS on 16 tables and creates a `get_user_tenant_id()` helper function, but the actual `CREATE POLICY` statements are referenced as being in `supabase/migrations/014_epic019_tenant_rls_policies.sql` — a file that is NOT in the Alembic directory. It may or may not have been applied to the actual database. Without confirmed RLS policies, cross-tenant data isolation is not enforced at the database level regardless of application-layer filtering.

## Acceptance Criteria

- [ ] Audit confirms whether `CREATE POLICY` statements exist in the connected PostgreSQL database
- [ ] If policies are missing: SQL file created and applied via Alembic migration or documented manual step
- [ ] A test executes a raw SQL query as a simulated non-default tenant and confirms it returns 0 rows for another tenant's data
- [ ] `get_user_tenant_id()` function works correctly in the DB (returns the correct UUID based on session variable)
- [ ] All 16 tables with RLS enabled have at least one SELECT policy

## Tasks

- [ ] Connect to DB and run: `SELECT schemaname, tablename, policyname FROM pg_policies WHERE schemaname = 'public'`
- [ ] If policies are missing: write the `CREATE POLICY ... USING (tenant_id = get_user_tenant_id())` statements for all 16 tables
- [ ] Create Alembic migration 018 that applies any missing policy SQL
- [ ] Add integration test: set session variable to tenant A UUID, verify tenant B records not returned
- [ ] Document: how `get_user_tenant_id()` gets set per request (must be called in middleware/connection setup)

## Autonomous Continuation Notes

- **Do not drop existing RLS enablement** — only add missing policy rows
- The Supabase `set_config('app.current_tenant_id', ...)` pattern must be called at the SQLAlchemy connection level (connection event hook), not just in the application layer
- Reference: `supabase/migrations/` directory for any pre-existing policy SQL
