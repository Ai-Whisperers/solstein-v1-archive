# STORY-354: Implement API Key Lookup and Validation from api_keys Table

| Field | Value |
|---|---|
| **Status** | 🔴 READY |
| **Priority** | P2 |
| **Size** | M (2 days) |
| **Epic** | EPIC-087 Multi-Tenancy Enforcement |
| **Created** | 2026-04-03 |
| **Risk** | Medium |
| **Blocked By** | STORY-352 (tenant context must be wired first) |

---

## Problem Statement

`_validate_api_key()` in `src/solstein/tenant/context.py` unconditionally returns `None`, meaning any API key is accepted without validation. The `api_keys` table (created in migration 015) exists and has the correct schema but the application never queries it.

## Acceptance Criteria

- [ ] `_validate_api_key(key: str) -> str | None` queries the `api_keys` table and returns the owning `tenant_id` if the key is valid and active, or `None` if invalid/expired/revoked
- [ ] A request with an invalid API key receives HTTP 401
- [ ] A request with a valid API key has the correct `tenant_id` injected into `TenantContext`
- [ ] API key lookup result is cached in Redis (TTL 5 minutes) to avoid per-request DB queries
- [ ] New tests: `test_valid_api_key_sets_tenant()`, `test_invalid_api_key_returns_401()`, `test_revoked_api_key_returns_401()`

## Tasks

- [ ] Read `alembic/versions/015_*.py` to confirm `api_keys` table schema (columns: `key_hash`, `tenant_id`, `is_active`, `expires_at`)
- [ ] Implement `_validate_api_key()`: hash incoming key, query `api_keys`, check `is_active` and `expires_at`
- [ ] Add Redis cache layer: `redis.get(f"apikey:{hash}")` before DB query
- [ ] Wire result into `TenantIsolationMiddleware` — if API key header present, use key validation instead of JWT
- [ ] Add tests for valid, invalid, expired, and revoked keys

## Autonomous Continuation Notes

- Store key hash (SHA-256), never the raw key — the raw key is shown only once at creation
- Cache TTL should be short (5 min) to allow prompt key revocation propagation
- The `api_keys` table uses RLS — ensure the DB connection uses a superuser or bypass role for the validation query itself, not the request tenant role
