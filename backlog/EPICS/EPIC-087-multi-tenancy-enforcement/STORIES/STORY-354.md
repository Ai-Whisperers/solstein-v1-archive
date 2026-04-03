# STORY-354: Close the TenantIsolationMiddleware._validate_api_key() Stub

| Field | Value |
|---|---|
| **Status** | 🔴 BLOCKED |
| **Priority** | P1 |
| **Size** | XS (2 hours) |
| **Epic** | EPIC-087 Multi-Tenancy Enforcement |
| **Created** | 2026-04-03 |
| **Updated** | 2026-04-03 (rewritten after codebase audit) |
| **Risk** | Low |
| **Blocked By** | STORY-352 |

---

## Actual Codebase State (verified 2026-04-03)

**Two separate API key validation implementations exist:**

1. `TenantMiddleware._lookup_tenant()` — `src/solstein/api/middleware/tenant.py:151`
   - **Fully implemented** — hashes key, queries `TenantRecord`, returns dict or None
   - Sets `request.state.tenant` and `request.state.tenant_id`
   - Used by the registered `TenantMiddleware`

2. `TenantIsolationMiddleware._validate_api_key()` — `src/solstein/tenant/context.py:134`
   - **Stub** — hashes key but `return None` unconditionally (line 149)
   - Comment: "In production, query database"
   - This is what STORY-352 must fix by importing `_lookup_tenant` from middleware

**The table is NOT called `api_keys` — it's `TenantRecord` (with column `api_key_hash`)**

---

## Problem Statement

This story is superseded by STORY-352. The actual fix (wiring `_validate_api_key` to query the DB) is tracked there as part of registering `TenantIsolationMiddleware`. This story is retained only to track the `TenantRecord` table schema, which serves as the source of truth for API key validation.

**If STORY-352 is complete, this story may be closed as DONE without separate work.**

---

## Acceptance Criteria

- [ ] Verify STORY-352 is DONE and `TenantIsolationMiddleware._validate_api_key()` now returns correct tenant ID for valid keys
- [ ] Verify `TenantRecord` table has the following columns: `id`, `name`, `api_key_hash` (SHA-256, 64 chars), `is_active`, `plan`, `rate_limit_per_min`
- [ ] Confirm no second `api_keys` table is needed — `TenantRecord` is the correct single source of truth
- [ ] Add test: invalid API key returns `None` from `_validate_api_key()`; valid active key returns the correct tenant UUID

## Key Files

| File | Line | Note |
|------|------|------|
| `src/solstein/tenant/context.py` | 134 | `_validate_api_key` stub — fixed by STORY-352 |
| `src/solstein/api/middleware/tenant.py` | 151 | `_lookup_tenant` — the working implementation |
| `src/solstein/infrastructure/models/infrastructure.py` | 40 | `TenantRecord` — the correct table (not `api_keys`) |
