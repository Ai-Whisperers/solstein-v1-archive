# STORY-352: Fix TenantIsolationMiddleware._validate_api_key() Stub

| Field | Value |
|---|---|
| **Status** | 🔴 READY |
| **Priority** | P1 |
| **Size** | S (half day) |
| **Epic** | EPIC-087 Multi-Tenancy Enforcement |
| **Created** | 2026-04-03 |
| **Updated** | 2026-04-03 (deep wiring audit) |
| **Risk** | Medium — touches auth path |

---

## Exact Codebase Wiring (deep audit 2026-04-03)

### The Stub

**`src/solstein/tenant/context.py`**:

```
Line 21:  current_tenant_var: ContextVar[str | None] = ContextVar("current_tenant", default=None)
Line 78:  class TenantIsolationMiddleware
Line 84:      def __init__(self, app)
Line 92:      async def __call__(self, scope, receive, send)
Line 112:     async def _extract_tenant_id(request) -> str | None
Line 122:         reads X-API-Key header first
Line 127:         falls back to Authorization: Bearer <JWT>
Line 134:     async def _validate_api_key(api_key: str) -> str | None   ← STUB
Line 144:         key_hash = hashlib.sha256(api_key.encode()).hexdigest()  # computed, not used
Line 149:         return None   ← unconditionally None — the bug
Line 151:     async def _validate_jwt(token) -> str | None              ← correctly implemented
Line 161:         from solstein.security.jwt import verify_token
Line 163:         payload = verify_token(token)
Line 164:         return payload.get("tenant_id")
Line 169:  class TenantAwareRepository
Line 175:      def __init__(self, session, tenant_id: str | None = None)
Line 183:          self.tenant_id = tenant_id or get_current_tenant()   ← reads ContextVar
Line 198:      def _apply_tenant_filter(self, query)
Line 210:          return query.filter_by(tenant_id=tenant_id)
```

### Working DB Lookup Pattern to Replicate

**`src/solstein/api/middleware/tenant.py`**:

```
Line 59:   class TenantMiddleware(BaseHTTPMiddleware)   ← registered at main.py:207
Line 68:   async def dispatch(request, call_next)
Line 101:      key_hash = hashlib.sha256(api_key.encode()).hexdigest()
Line 104:      tenant = await _lookup_tenant(key_hash, request)
Line 145:      request.state.tenant = tenant
Line 146:      request.state.tenant_id = tenant["id"]    ← sets request state (not ContextVar)

Line 151:  async def _lookup_tenant(key_hash: str, request) -> dict | None
Line 162:      # imports: select, AsyncSession, get_async_engine
Line 168:      async with AsyncSession(get_async_engine()) as session:
Line 170:          result = await session.execute(
Line 171:              select(TenantRecord).where(
Line 172:                  TenantRecord.api_key_hash == key_hash,    ← exact column to query
Line 173:                  TenantRecord.is_active.is_(True),
Line 174:              )
Line 175:          )
Line 176:          tenant_record = result.scalar_one_or_none()
Line 179:          return tenant_record.to_dict()
```

### TenantRecord Schema (`src/solstein/infrastructure/models/infrastructure.py:40`)

Table: `tenants`

| Column | SQLAlchemy Type | Constraint |
|--------|-----------------|------------|
| `id` | `Uuid(as_uuid=True)` | PK, default `uuid.uuid4()` |
| `name` | `String(255)` | NOT NULL, UNIQUE |
| `api_key_hash` | `String(64)` | NOT NULL, UNIQUE — SHA-256 hex (64 chars) |
| `is_active` | `Boolean` | NOT NULL, default `True` |
| `plan` | `String(64)` | NOT NULL, default `"standard"` |
| `rate_limit_per_min` | `Integer` | NOT NULL, default `60` |

`to_dict()` at line 72 — serializes safely (never exposes `api_key_hash`).

Indexes (lines 67–70): `api_key_hash` (unique), `is_active`.

### Registration State (`src/solstein/api/main.py`)

```
Line 43:   from .middleware.tenant import TenantMiddleware
Line 207:  app.add_middleware(TenantMiddleware)          ← registered, working
           # TenantIsolationMiddleware: NOT registered anywhere
Line 204:  app.add_middleware(AuditMiddleware)           ← outermost
```

**Effect**: `TenantMiddleware` validates the key and sets `request.state.tenant_id` — but NOT `current_tenant_var`. Downstream code that calls `get_current_tenant()` gets `None` for every API-key-authenticated request.

---

## Problem Statement

`TenantIsolationMiddleware._validate_api_key()` at `context.py:149` always returns `None`. The middleware is also never registered in `main.py`. Consequence: `current_tenant_var` is never populated for API-key requests, so any code using `get_current_tenant()` (including `TenantAwareRepository._apply_tenant_filter()`) cannot filter by tenant — silent cross-tenant data access risk.

---

## Acceptance Criteria

- [ ] `_validate_api_key(api_key)` queries `tenants` table by `api_key_hash` and returns `str(record.id)` or `None`
- [ ] SHA-256 hash pattern used (matches `TenantMiddleware` line 101)
- [ ] `TenantIsolationMiddleware` registered in `main.py` after `TenantMiddleware` — `current_tenant_var` set on every authenticated request
- [ ] `TenantMiddleware` remains registered — do NOT remove it (`request.state.tenant_id` used by many routes)
- [ ] `get_current_tenant()` returns correct tenant_id for API-key-authenticated requests
- [ ] Test: valid API key → `get_current_tenant()` returns tenant_id
- [ ] Test: unknown API key → request rejected (401 or 403)
- [ ] `ruff check` 0 errors

---

## Tasks

- [ ] Replace `context.py:134–149` stub body:
  ```python
  async def _validate_api_key(self, api_key: str) -> str | None:
      from solstein.infrastructure.models.infrastructure import TenantRecord
      from solstein.infrastructure.database import get_async_engine
      from sqlalchemy import select
      from sqlalchemy.ext.asyncio import AsyncSession
      key_hash = hashlib.sha256(api_key.encode()).hexdigest()
      async with AsyncSession(get_async_engine()) as session:
          result = await session.execute(
              select(TenantRecord).where(
                  TenantRecord.api_key_hash == key_hash,
                  TenantRecord.is_active.is_(True),
              )
          )
          record = result.scalar_one_or_none()
          return str(record.id) if record else None
  ```
- [ ] Register in `main.py` after line 207:
  ```python
  from solstein.tenant.context import TenantIsolationMiddleware
  app.add_middleware(TenantIsolationMiddleware)
  ```
- [ ] Write `tests/unit/test_tenant_isolation_middleware.py` using mock DB session

## Key Files

| File | Line | Note |
|------|------|------|
| `src/solstein/tenant/context.py` | 134–149 | Stub — replace body |
| `src/solstein/tenant/context.py` | 21 | `current_tenant_var` ContextVar |
| `src/solstein/api/middleware/tenant.py` | 101–179 | Working pattern to replicate |
| `src/solstein/infrastructure/models/infrastructure.py` | 40–84 | `TenantRecord` columns |
| `src/solstein/api/main.py` | 207 | Insert `add_middleware(TenantIsolationMiddleware)` here |
