# EPIC-087: Multi-Tenancy Enforcement

> **Priority**: P1 – High (cross-tenant data leakage possible today)
> **Stories**: 3 ([STORY-352](STORIES/STORY-352.md) through [STORY-354](STORIES/STORY-354.md))
> **Effort**: M (3–5 days total)
> **Dependencies**: Migrations 013–015 (already merged — schema exists)
> **Status**: 🔴 Not Started
> **Created**: 2026-04-03
> **Updated**: 2026-04-03 (codebase audit corrected all file/table references; [STORY-354](STORIES/STORY-354.md) cancelled; execution order inverted)

---

## Problem

Multi-tenancy infrastructure (migrations, models, `TenantAwareRepository`) exists but is **not wired into the running application**. Codebase audit (2026-04-03) confirmed:

1. `TenantIsolationMiddleware` at `src/solstein/tenant/context.py:78` is defined but **never registered** in FastAPI — no tenant context is set via ContextVar on any request
2. `_validate_api_key()` at `context.py:149` returns `None` unconditionally — the DB lookup body is a stub
3. PostgreSQL RLS: migrations 013–015 define RLS policies, but **no Python code calls `SET LOCAL`** — RLS is never activated at runtime
4. `TenantMiddleware` at `src/solstein/api/middleware/tenant.py:59` IS registered at `main.py:207` and correctly queries `TenantRecord.api_key_hash` — this must not be removed

**The working lookup to replicate** is `_lookup_tenant()` at `src/solstein/api/middleware/tenant.py:151`: queries `TenantRecord` (table: `tenants`) by SHA-256 hash of the API key, returns `tenant_id` as string.

---

## Stories

| Story | Title | Priority | Size | Status |
|-------|-------|----------|------|--------|
| [STORY-353](STORIES/STORY-353.md) | Audit tenant isolation strategy: Option A (SQLAlchemy RLS event) vs Option B (app-layer exhaustive) | P1 | M | 🔴 READY |
| [STORY-352](STORIES/STORY-352.md) | Fix `_validate_api_key()` stub and (if Option B) register `TenantIsolationMiddleware` | P1 | S | ⏳ BLOCKED by [STORY-353](STORIES/STORY-353.md) |
| [STORY-354](STORIES/STORY-354.md) | ~~Duplicate of [STORY-352](STORIES/STORY-352.md)~~ | — | — | ❌ CANCELLED |

**Execution order**: 353 first (strategy decision), then 352 (implementation — scope depends on 353's decision).

**Why 353 must precede 352**: If [STORY-353](STORIES/STORY-353.md) chooses Option A (wire PostgreSQL RLS via SQLAlchemy event listener), the `TenantIsolationMiddleware` registration in [STORY-352](STORIES/STORY-352.md) may be redundant or conflicting — scope shrinks to stub-fix only. If Option B, register and test fully.

**Why [STORY-354](STORIES/STORY-354.md) is cancelled**: Identical scope to [STORY-352](STORIES/STORY-352.md) — both target `context.py:134–149`. No distinct deliverable. Do not reopen.

---

## Definition of Done

- [ ] [STORY-353](STORIES/STORY-353.md): written ADR capturing the chosen isolation strategy (Option A or B) with concrete rationale
- [ ] `_validate_api_key(api_key)` queries `tenants` table via `api_key_hash` → returns `str(record.id)` or `None`
- [ ] If Option B: `TenantIsolationMiddleware` registered in `main.py` after line 207 (after `TenantMiddleware` — do NOT remove `TenantMiddleware`)
- [ ] `get_current_tenant()` returns correct `tenant_id` for API-key requests
- [ ] Integration test: valid key → correct tenant_id; unknown key → 401/403
- [ ] `pytest` passes at 0 failures, `ruff check` at 0 errors

---

## Acceptance Criteria

**AC-1**: A request authenticated as tenant A cannot retrieve a company record created by tenant B.

**AC-2**: A request with an invalid API key receives HTTP 401/403, not HTTP 200.

**AC-3**: `get_current_tenant()` (from `tenant/context.py`) returns the correct `tenant_id` inside any request handler when called via API key auth.

---

## Key Files (Codebase-Verified 2026-04-03)

| File | Line | Role |
|------|------|------|
| `src/solstein/tenant/context.py` | 78 | `TenantIsolationMiddleware` definition |
| `src/solstein/tenant/context.py` | 21 | `current_tenant_var: ContextVar` |
| `src/solstein/tenant/context.py` | 134–149 | `_validate_api_key()` stub — always returns None |
| `src/solstein/api/middleware/tenant.py` | 59 | `TenantMiddleware` — IS registered, works correctly |
| `src/solstein/api/middleware/tenant.py` | 151–179 | `_lookup_tenant()` — working DB lookup to replicate |
| `src/solstein/infrastructure/models/infrastructure.py` | 40 | `TenantRecord` — table `tenants`, `api_key_hash String(64)` |
| `src/solstein/api/main.py` | 207 | Registration point — `TenantMiddleware` registered here |
| `alembic/versions/014_*.py` | — | RLS policy migration (PostgreSQL side) |
| `alembic/versions/015_*.py` | — | `api_keys` table schema (separate from `tenants`) |
