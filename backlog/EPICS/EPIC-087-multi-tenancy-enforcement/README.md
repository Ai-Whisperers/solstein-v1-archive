# EPIC-087: Multi-Tenancy Enforcement

> **Priority**: P1 – High (cross-tenant data leakage possible today)
> **Stories**: 3 (STORY-352 through STORY-354)
> **Effort**: M (3–5 days total)
> **Dependencies**: Migrations 013–015 (already merged — schema exists)
> **Status**: 🔴 Not Started
> **Created**: 2026-04-03

---

## Problem

Multi-tenancy infrastructure (migrations, models, `TenantAwareRepository`) exists but is **not wired into the running application**. This means:

1. `TenantIsolationMiddleware` is defined but never registered in FastAPI — no tenant context is set on any request
2. RLS policies may not be deployed in PostgreSQL (migrations reference a Supabase-side file that may or may not have been applied)
3. API key validation (`_validate_api_key()`) returns `None` unconditionally — any API key is accepted

The net result: a system that looks multi-tenant but is actually a single-tenant system with no data isolation.

---

## Stories

| Story | Title | Priority | Size |
|-------|-------|----------|------|
| STORY-352 | Register TenantIsolationMiddleware and verify tenant context propagation | P1 | S |
| STORY-353 | Audit and deploy PostgreSQL RLS policies for tenant isolation | P1 | M |
| STORY-354 | Implement API key lookup and validation from api_keys table | P2 | M |

**Execution order**: 352 → 353 → 354 (352 must be first; 353 and 354 can run in parallel)

---

## Definition of Done

- [ ] `TenantIsolationMiddleware` registered in `src/solstein/api/main.py`
- [ ] Every authenticated request has a valid `tenant_id` in request scope
- [ ] RLS policy SQL confirmed deployed in PostgreSQL — cross-tenant SELECT returns 0 rows
- [ ] `_validate_api_key()` queries the `api_keys` table and returns the owning `tenant_id` or raises
- [ ] Integration test: request with tenant A credentials cannot read tenant B data
- [ ] `pytest` passes at 0 failures, `ruff check` at 0 errors

---

## Acceptance Criteria

**AC-1**: A request authenticated as tenant A cannot retrieve a company record created by tenant B.

**AC-2**: A request with an invalid API key receives HTTP 401, not HTTP 200.

**AC-3**: `TenantContext.get_current()` returns the correct `tenant_id` inside any request handler.

---

## Key Files

| File | Role |
|------|------|
| `src/solstein/api/main.py` | FastAPI app — middleware must be registered here |
| `src/solstein/worker/tenant_isolation.py` | `TenantIsolationMiddleware` definition |
| `src/solstein/tenant/context.py` | `TenantContext`, `_validate_api_key()` stub |
| `alembic/versions/014_*.py` | References Supabase-side RLS SQL — verify it was applied |
| `alembic/versions/015_*.py` | `api_keys` table schema |
