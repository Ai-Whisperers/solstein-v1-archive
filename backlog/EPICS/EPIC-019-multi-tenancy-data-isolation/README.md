# EPIC-019: Multi-Tenancy & Data Isolation

| Field | Value |
|-------|-------|
| Priority | **P1** |
| Status | 🔴 Open |
| Stories | 4 |
| Created | 2026-02-28 |
| Depends On | [EPIC-020](../EPIC-020-supabase-auth-migration/README.md) (Supabase Auth must exist before RLS can reference authenticated users) |

## Context

Solstein serves PE/VC professionals. "PE/VC professionals" is plural — there are multiple firms, multiple teams, and multiple users. A senior partner at Firm A must never see Firm B's proprietary deal pipeline analysis.

Currently, there is no tenant model anywhere in the codebase. No `tenant_id`, no `org_id`, no row-level isolation. The database has one namespace and all authenticated users share it. If two firms were onboarded today, their data would be completely intermixed.

This is not a future problem. It is a current architectural absence that blocks any multi-firm onboarding.

The solution is Supabase Row Level Security (RLS). PostgreSQL-native, enforced at the database layer — application code cannot bypass it. Define the tenant model once, define the RLS policies, and data isolation becomes structurally guaranteed rather than application-code-dependent.

## Scope

| Story | Title | Severity |
|-------|-------|----------|
| [STORY-063](STORIES/STORY-063-define-tenant-model.md) | Define the Tenant Model and Domain Object Scoping | HIGH |
| [STORY-064](STORIES/STORY-064-supabase-rls-policies.md) | Implement Supabase Row Level Security for All Tables | HIGH |
| [STORY-065](STORIES/STORY-065-tenant-api-key-management.md) | Add Tenant-Scoped API Key Management | HIGH |
| [STORY-066](STORIES/STORY-066-tenant-isolation-research-jobs.md) | Enforce Tenant Isolation in Research Pipeline and Background Jobs | HIGH |

## Definition of Done

- [ ] A `Tenant` entity exists in the domain model
- [ ] Every company record and research result is scoped to a tenant
- [ ] RLS policies are in place — querying without a tenant context returns no rows
- [ ] Background jobs cannot access data outside the tenant that initiated them
- [ ] A new tenant can be onboarded without code changes
