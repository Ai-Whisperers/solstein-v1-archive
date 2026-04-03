# STORY-354: Close TenantIsolationMiddleware._validate_api_key() Stub (Superseded by STORY-352)

| Field | Value |
|---|---|
| **Status** | ⏳ BLOCKED |
| **Priority** | P1 |
| **Size** | XS |
| **Epic** | EPIC-087 Multi-Tenancy Enforcement |
| **Created** | 2026-04-03 |
| **Updated** | 2026-04-03 (deep wiring audit — superseded) |
| **Blocked By** | STORY-352 |

---

## Status: Superseded by STORY-352

Deep audit (2026-04-03) confirmed this story's scope is identical to STORY-352:

- Stub: `src/solstein/tenant/context.py:134–149` — `_validate_api_key()` hashes the key but unconditionally `return None` at line 149
- Correct DB table: `TenantRecord` (table `tenants`) at `src/solstein/infrastructure/models/infrastructure.py:40`; column `api_key_hash` (String 64, SHA-256 hex of raw key)
- `ApiKeyRecord` (table `api_keys`, line 87 of same file) exists for multi-key-per-tenant (EPIC-019), but `TenantMiddleware` and STORY-352's fix both target `TenantRecord`

STORY-352 covers the full fix: replace stub body + register the middleware. This story adds no distinct scope.

---

## Acceptance Criteria

- [ ] STORY-352 is merged — this story is automatically DONE

Do not implement separately. Mark DONE when STORY-352 ships.
