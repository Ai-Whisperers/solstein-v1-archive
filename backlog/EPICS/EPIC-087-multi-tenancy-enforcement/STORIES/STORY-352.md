# STORY-352: Wire TenantIsolationMiddleware._validate_api_key() to the database

| Field | Value |
|---|---|
| **Status** | 🔴 READY |
| **Priority** | P1 |
| **Size** | S (half day) |
| **Epic** | EPIC-087 Multi-Tenancy Enforcement |
| **Created** | 2026-04-03 |
| **Updated** | 2026-04-03 (rewritten after codebase audit) |
| **Risk** | Low — isolated to one method in one class |

---

## Actual Codebase State (verified 2026-04-03)

Two middleware implementations exist and serve different purposes:

**`TenantMiddleware`** — `src/solstein/api/middleware/tenant.py:59`
- IS registered at `src/solstein/api/main.py:207` via `app.add_middleware(TenantMiddleware)`
- Validates `X-API-Key`, hashes with SHA-256, queries `TenantRecord` table via `_lookup_tenant()` (line 151)
- On success: sets `request.state.tenant` (dict) and `request.state.tenant_id` (string)
- Correctly implemented and working

**`TenantIsolationMiddleware`** — `src/solstein/tenant/context.py:78`
- **NOT registered** — not in `main.py`
- Sets `current_tenant_var` (ContextVar) which is what `TenantAwareRepository` reads (line 183)
- `_validate_api_key()` (line 134): hashes key but **returns `None` unconditionally** — comment says "In production, query database"
- `_validate_jwt()` (line 149): correctly calls `verify_token()` and extracts `tenant_id`

**The gap**: `TenantAwareRepository` reads `current_tenant_var` (set by `TenantIsolationMiddleware`), but `TenantIsolationMiddleware._validate_api_key()` always returns `None`. So API-key requests get no tenant context even though `TenantMiddleware` correctly validates the key. JWT requests work correctly because `_validate_jwt` is implemented.

---

## Problem Statement

`TenantIsolationMiddleware._validate_api_key()` (line 134 of `src/solstein/tenant/context.py`) always returns `None`. It hashes the API key but never queries the database. This means all API-key authenticated requests have no tenant context in `current_tenant_var`, so `TenantAwareRepository` queries are not tenant-scoped.

**Do NOT register `TenantIsolationMiddleware` in main.py** — `TenantMiddleware` is already registered and handles the DB lookup. Instead, fix `_validate_api_key` to query the DB or delegate to `TenantMiddleware`'s lookup function.

---

## Acceptance Criteria

- [ ] `TenantIsolationMiddleware._validate_api_key()` queries the `TenantRecord` table and returns the tenant `id` for a valid active key, `None` otherwise
- [ ] Reuses `_lookup_tenant()` from `src/solstein/api/middleware/tenant.py` (import it) — do not duplicate the DB query logic
- [ ] `TenantIsolationMiddleware` is registered in `src/solstein/api/main.py` (pure ASGI wrap: `app = TenantIsolationMiddleware(app)`) — after `TenantMiddleware` so both run
- [ ] A request with a valid `X-API-Key` has `get_current_tenant()` return the correct `tenant_id` inside route handlers
- [ ] Existing auth tests pass (no regression)
- [ ] New test: `test_tenant_context_var_set_by_api_key_request()` in `tests/unit/`

---

## Tasks

- [ ] Read `src/solstein/tenant/context.py:134` — confirm `_validate_api_key` stub
- [ ] Import and call `_lookup_tenant` from `solstein.api.middleware.tenant` inside `_validate_api_key()` to avoid duplicate DB logic
- [ ] Register `TenantIsolationMiddleware` in `src/solstein/api/main.py` after line 207 (after `TenantMiddleware`) as a pure ASGI wrap
- [ ] Write a unit test using a mock DB that validates `current_tenant_var` is set correctly on a valid API key request
- [ ] Run `pytest tests/unit/test_classification_service.py tests/unit/test_story063_tenant_model.py` to confirm no regressions

## Key Files

| File | Line | Note |
|------|------|------|
| `src/solstein/tenant/context.py` | 134 | `_validate_api_key` — fix here |
| `src/solstein/api/middleware/tenant.py` | 151 | `_lookup_tenant()` — reuse this |
| `src/solstein/api/main.py` | 207 | Add `TenantIsolationMiddleware` wrap after this line |
| `src/solstein/tenant/context.py` | 21 | `current_tenant_var` — the ContextVar being set |
