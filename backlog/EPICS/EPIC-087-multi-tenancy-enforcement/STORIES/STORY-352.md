# STORY-352: Fix TenantIsolationMiddleware._validate_api_key() Stub

| Field | Value |
|---|---|
| **Status** | ⏳ BLOCKED |
| **Priority** | P1 |
| **Size** | S (half day) |
| **Epic** | EPIC-087 Multi-Tenancy Enforcement |
| **Created** | 2026-04-03 |
| **Updated** | 2026-04-03 (reordered — blocked by STORY-353) |
| **Risk** | Medium — touches auth path |
| **Blocked By** | STORY-353 |

---

## Why Blocked by STORY-353

STORY-353 decides the tenant isolation strategy (Option A: wire PostgreSQL RLS via SQLAlchemy event, or Option B: application-layer-only). That decision directly changes what this story must implement:

- **Option B chosen**: implement exactly as specified below — fix stub, register `TenantIsolationMiddleware` to set `current_tenant_var`
- **Option A chosen**: the SQLAlchemy event listener in STORY-353 may already inject tenant context at the DB connection level, making `TenantIsolationMiddleware`'s ContextVar mechanism redundant or conflicting — this story's scope shrinks to just the stub fix without middleware registration

Do not start this story until STORY-353 is merged and the decision is recorded.

---

## Exact Codebase Wiring

### The Stub (`src/solstein/tenant/context.py`)

```
Line 21:  current_tenant_var: ContextVar[str | None] = ContextVar("current_tenant", default=None)
Line 78:  class TenantIsolationMiddleware
Line 92:      async def __call__(self, scope, receive, send)
Line 112:     async def _extract_tenant_id(request) -> str | None
Line 122:         reads X-API-Key header first
Line 127:         falls back to Authorization: Bearer <JWT>
Line 134:     async def _validate_api_key(api_key: str) -> str | None   ← STUB
Line 144:         key_hash = hashlib.sha256(api_key.encode()).hexdigest()  # computed, not used
Line 149:         return None   ← unconditionally None — the bug
Line 151:     async def _validate_jwt(token) -> str | None              ← correctly implemented
Line 169:  class TenantAwareRepository
Line 183:          self.tenant_id = tenant_id or get_current_tenant()   ← reads ContextVar
Line 210:          return query.filter_by(tenant_id=tenant_id)
```

### Working DB Lookup to Replicate (`src/solstein/api/middleware/tenant.py`)

```
Line 101:      key_hash = hashlib.sha256(api_key.encode()).hexdigest()
Line 168:      async with AsyncSession(get_async_engine()) as session:
Line 171:          select(TenantRecord).where(
Line 172:              TenantRecord.api_key_hash == key_hash,
Line 173:              TenantRecord.is_active.is_(True),
Line 176:          tenant_record = result.scalar_one_or_none()
Line 179:          return tenant_record.to_dict()
```

### TenantRecord (`src/solstein/infrastructure/models/infrastructure.py:40`, table `tenants`)

`api_key_hash`: `String(64)`, UNIQUE — SHA-256 hex of the raw key.

### Registration (`src/solstein/api/main.py`)

```
Line 207:  app.add_middleware(TenantMiddleware)   ← working; sets request.state.tenant_id
           # TenantIsolationMiddleware: NOT registered (sets current_tenant_var)
```

---

## Acceptance Criteria (if Option B chosen from STORY-353)

- [ ] `_validate_api_key(api_key)` queries `tenants` via `api_key_hash` → returns `str(record.id)` or `None`
- [ ] `TenantIsolationMiddleware` registered in `main.py` after line 207
- [ ] `get_current_tenant()` returns correct tenant_id for API-key requests
- [ ] `TenantMiddleware` stays registered — do NOT remove
- [ ] Test: valid key → `get_current_tenant()` returns tenant_id; unknown key → 401/403

## Tasks (scope confirmed by STORY-353 decision)

- [ ] Read STORY-353 decision doc first
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
- [ ] If Option B: register `TenantIsolationMiddleware` in `main.py` after line 207
- [ ] Write tests

## Key Files

| File | Line | Note |
|------|------|------|
| `src/solstein/tenant/context.py` | 134–149 | Stub to replace |
| `src/solstein/api/middleware/tenant.py` | 151–179 | Working `_lookup_tenant` to replicate |
| `src/solstein/infrastructure/models/infrastructure.py` | 40 | `TenantRecord.api_key_hash` |
| `src/solstein/api/main.py` | 207 | Register after here (if Option B) |
