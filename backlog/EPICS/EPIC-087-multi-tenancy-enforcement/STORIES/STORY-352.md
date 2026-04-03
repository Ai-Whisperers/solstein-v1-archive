# STORY-352: Register TenantIsolationMiddleware and Verify Tenant Context Propagation

| Field | Value |
|---|---|
| **Status** | 🔴 READY |
| **Priority** | P1 |
| **Size** | S (1 day) |
| **Epic** | EPIC-087 Multi-Tenancy Enforcement |
| **Created** | 2026-04-03 |
| **Risk** | Medium — touching middleware order can break auth |

---

## Problem Statement

`TenantIsolationMiddleware` is defined in `src/solstein/worker/tenant_isolation.py` but is never registered in the FastAPI application (`src/solstein/api/main.py`). As a result, `TenantContext.get_current()` returns `None` inside every request handler, and all `TenantAwareRepository` queries fall back to the default tenant UUID — effectively ignoring multi-tenancy entirely.

## Acceptance Criteria

- [ ] `TenantIsolationMiddleware` is registered in `src/solstein/api/main.py` after auth middleware
- [ ] A request authenticated with a valid JWT has `TenantContext.get_current()` return the correct `tenant_id` inside any route handler
- [ ] A request without a valid JWT or tenant claim receives HTTP 401
- [ ] Existing auth tests still pass (no regression)
- [ ] New test: `test_tenant_context_set_on_authenticated_request()`

## Tasks

- [ ] Read `src/solstein/api/main.py` — identify middleware registration order
- [ ] Read `src/solstein/worker/tenant_isolation.py` — confirm middleware interface (ASGI or Starlette)
- [ ] Register `TenantIsolationMiddleware` after JWT auth middleware
- [ ] Confirm `TenantContext` is a context-var based store (thread-safe for async)
- [ ] Add integration test: authenticated request → `TenantContext.get_current()` returns expected UUID

## Autonomous Continuation Notes

- Middleware order matters: JWT auth must run before tenant extraction (JWT provides the tenant claim)
- Do not break the existing Supabase auth flow — wrap, don't replace
- If `TenantIsolationMiddleware` is Starlette BaseHTTPMiddleware, add via `app.add_middleware()`; if pure ASGI, wrap at `app = TenantIsolationMiddleware(app)`
