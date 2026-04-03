# STORY-353: Audit Tenant Isolation Strategy and Add PostgreSQL RLS (or Document Why Not)

| Field | Value |
|---|---|
| **Status** | 🔴 READY |
| **Priority** | P1 |
| **Size** | M (1-2 days) |
| **Epic** | EPIC-087 Multi-Tenancy Enforcement |
| **Created** | 2026-04-03 |
| **Updated** | 2026-04-03 (rewritten after codebase audit) |
| **Risk** | Medium — touches DB schema and ORM layer |

---

## Actual Codebase State (verified 2026-04-03)

**Application-layer isolation exists:**
- `tenant_id` columns exist on `ResearchJobRecord` (NOT NULL, indexed), `ResearchRunRecord` (nullable, indexed)
- `TenantAwareRepository` (`src/solstein/tenant/context.py:169`) filters queries by `tenant_id` from `current_tenant_var`
- `ResearchJobRepository` scopes all queries to `tenant_id`

**Database-layer RLS does NOT exist:**
- No `CREATE POLICY`, `ALTER TABLE ENABLE ROW LEVEL SECURITY`, or `set_config('app.current_tenant_id', ...)` anywhere in source
- No SQLAlchemy connection event that calls `set_config` on connection checkout
- `ResearchJobRecord` docstring (line 285 of `models/research.py`) says "RLS ensures tenant isolation" — this is incorrect documentation

**The risk**: If application-layer filtering has any bug, raw query, or admin backdoor, cross-tenant data access is undetected because PostgreSQL has no second defence.

---

## Problem Statement

The system documents RLS as the isolation mechanism but does not implement it. Application-layer `tenant_id` filtering is the only protection. This story must either implement PostgreSQL RLS or document why application-layer-only is an acceptable architectural decision.

---

## Acceptance Criteria

**Option A — Implement RLS (preferred):**
- [ ] Alembic migration adds `ENABLE ROW LEVEL SECURITY` and `CREATE POLICY` on `researchjobrecord`, `researchrunrecord`, and `companyrecord` tables
- [ ] SQLAlchemy event listener calls `SET LOCAL app.current_tenant_id = '...'` before each query execution (on `engine.begin()` or via `SessionFactory` event)
- [ ] Test: a connection with `app.current_tenant_id = 'tenant-A'` cannot read `tenant-B` rows even via raw `SELECT *`
- [ ] Docstring in `ResearchJobRecord` updated to accurately describe the isolation mechanism

**Option B — Document and verify application-layer-only:**
- [ ] `docs/adr/ADR-001-tenant-isolation.md` created, documenting the decision and its risks
- [ ] All Repository classes confirmed to extend `TenantAwareRepository` or have an explicit bypass comment
- [ ] CI check added: no `session.execute()` without a `tenant_id` WHERE clause outside of admin-flagged files

---

## Tasks

- [ ] Grep all Repository classes for queries missing `tenant_id` filter
- [ ] Check Supabase dashboard: is RLS enabled on any table?
- [ ] Correct the misleading docstring in `ResearchJobRecord` (line 285, `src/solstein/infrastructure/models/research.py`)
- [ ] Decide and implement Option A or Option B
- [ ] Write cross-tenant isolation test

## Key Files

| File | Line | Note |
|------|------|------|
| `src/solstein/tenant/context.py` | 169 | `TenantAwareRepository` — application-layer filtering |
| `src/solstein/infrastructure/models/research.py` | 285 | Incorrect RLS claim in docstring — fix this regardless |
| `src/solstein/infrastructure/database.py` | 72 | Engine creation — add event listener here for RLS path |
| `src/solstein/infrastructure/research_job_repository.py` | — | Verify all queries are tenant-scoped |
