# STORY-353: Audit Tenant Isolation Strategy and Address PostgreSQL RLS Gap

| Field | Value |
|---|---|
| **Status** | 🔴 READY |
| **Priority** | P1 |
| **Size** | M (1-2 days) |
| **Epic** | EPIC-087 Multi-Tenancy Enforcement |
| **Created** | 2026-04-03 |
| **Updated** | 2026-04-03 (deep wiring audit) |
| **Risk** | High — potential cross-tenant data leakage |

---

## Exact Codebase Wiring (deep audit 2026-04-03)

### RLS Schema State

**Migration 014** (`alembic/versions/014_epic019_rls_helper_function.py`):
- Line 54–65: Creates `public.get_user_tenant_id()` — reads `current_setting('request.jwt.claims', true)` from PostgreSQL connection
- Line 74–75: `ALTER TABLE ... ENABLE ROW LEVEL SECURITY` on **16 tables**: `companies`, `scoring_records`, `signal_records`, `market_snapshots`, `audit_trails`, `research_runs`, `research_stages`, `research_artifacts`, `source_documents`, `metric_observations`, `evidence_readiness`, `research_contradictions`, `enrichment_audit_trail`, `enrichment_cache`, `enrichment_jobs`, `outbox_records`

**Migration 015** (`alembic/versions/015_epic019_api_keys_table.py`):
- Line 66–67: `ALTER TABLE public.api_keys ENABLE ROW LEVEL SECURITY`; same for `api_key_usage_logs`

**Supabase SQL** (`supabase/migrations/015_epic019_api_keys.sql:44–67`):
- 4 policies on `api_keys` + 2 on `api_key_usage_logs`
- All policies use `tenant_id::text = public.get_user_tenant_id()`

### Critical Gap: No Python → PostgreSQL Tenant Injection

```bash
grep -rn "SET.*app.current_tenant"   src/  →  0 results
grep -rn "SET LOCAL"                  src/  →  0 results
grep -rn "request.jwt.claims"         src/  →  0 results (only in migration SQL)
grep -rn "get_user_tenant_id"         src/  →  0 results (only in migration files)
```

**Effect**: `get_user_tenant_id()` always returns `NULL` for API-key requests. RLS policies are technically enabled but never enforced — every query runs without tenant filtering at the DB level.

### What Is Enforced at Runtime

| Mechanism | Location | Effective? |
|-----------|----------|-----------|
| API key hash validation | `api/middleware/tenant.py:101–179` | ✅ Auth gate |
| `request.state.tenant_id` | `api/middleware/tenant.py:145–146` | ✅ Set per request |
| Explicit `WHERE tenant_id = ?` | `tenant/context.py:210`, `services.py:34`, `research_job_repository.py:188` | ✅ Where explicitly coded |
| PostgreSQL RLS | 16 tables + api_keys schema-enabled | ❌ Never activated (no `SET LOCAL` from Python) |
| `current_tenant_var` ContextVar | `tenant/context.py:21` | ❌ Never set for API key auth (STORY-352) |

### Misleading Docstring

`ResearchRunRecord` at `src/solstein/infrastructure/models/research.py:34` — docstring states *"RLS ensures tenant isolation"* — **this is false**. RLS is schema-enabled but never activated by Python code.

---

## Problem Statement

RLS is deployed in the schema but inoperative at runtime. Application-layer filtering (explicit `WHERE tenant_id = ?` in repositories) is the actual isolation mechanism, but it is ad-hoc: each query must be manually scoped. Any new repository method that omits the filter silently exposes cross-tenant data.

Two implementation options must be evaluated, a decision made, and documented.

---

## Acceptance Criteria

- [ ] Audit document `docs/architecture/tenant-isolation-strategy.md` created: every DB query site catalogued with tenant-scoping status
- [ ] **Decision recorded**: Option A or Option B chosen with rationale
- [ ] **Option A (wire RLS)**: SQLAlchemy async event listener on connection checkout that executes `SET LOCAL request.jwt.claims = '{"tenant_id": "..."}'` when `current_tenant_var` is set; integration test confirms RLS blocks cross-tenant query
- [ ] **Option B (application-layer-only)**: All unscoped query paths patched with explicit `WHERE tenant_id = ?`; test confirms cross-tenant access returns empty / 404; PR description gate: new queries must be scoped
- [ ] `ResearchRunRecord` docstring corrected — `src/solstein/infrastructure/models/research.py:34` — remove or correct the RLS claim
- [ ] No regressions: existing tenant-filtered queries continue to work

---

## Tasks

- [ ] Audit: `grep -rn "session.execute\|await session" src/ --include="*.py"` — for each query, verify `tenant_id` in WHERE clause
- [ ] Write `docs/architecture/tenant-isolation-strategy.md` with decision
- [ ] Implement chosen option
- [ ] Fix docstring at `models/research.py:34`

## Key Files

| File | Line | Note |
|------|------|------|
| `alembic/versions/014_epic019_rls_helper_function.py` | 54–75 | RLS helper + 16-table ENABLE |
| `alembic/versions/015_epic019_api_keys_table.py` | 66–67 | api_keys/usage RLS |
| `supabase/migrations/015_epic019_api_keys.sql` | 44–67 | RLS policies (schema only) |
| `src/solstein/tenant/context.py` | 169–210 | `TenantAwareRepository` — application-layer filter |
| `src/solstein/infrastructure/models/research.py` | 34 | False RLS docstring |
| `src/solstein/infrastructure/research_job_repository.py` | 188 | Correct scoping example |
| `src/solstein/tenant/services.py` | 34 | Correct scoping example |
