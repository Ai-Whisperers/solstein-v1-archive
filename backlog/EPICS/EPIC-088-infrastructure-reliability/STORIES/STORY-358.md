# STORY-358: Add Startup Check — Verify Celery Broker Reachable Before App Accepts Traffic

| Field | Value |
|---|---|
| **Status** | 🔴 READY |
| **Priority** | P2 |
| **Size** | S (half day) |
| **Epic** | EPIC-088 Infrastructure Reliability |
| **Created** | 2026-04-03 |
| **Updated** | 2026-04-03 (deep wiring audit) |
| **Risk** | Low |

---

## Exact Codebase Wiring (deep audit 2026-04-03)

### Lifespan Block (`src/solstein/api/main.py:69–154`)

```python
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:  # line 69
    # line 77:  settings.check_configuration()  ← config validation (can raise)
    # line 88:  settings.data.ensure_dirs()
    # line 93:  feature_flags = FeatureFlagManager()
    # line 94:  response_cache = ResponseCache()
    # line 103: init_tracing(...)              ← OpenTelemetry (line 103; warn-only on fail)
    # line 116: enable_profiling()             ← dev only
    # line 121: warm_cache(_cache)             ← background task (warn-only on fail)
    # line 128: start_realtime_listener()      ← Supabase (warn-only on fail)
    # line 141: yield                          ← server starts accepting traffic HERE
    # lines 142–153: shutdown block
```

**Current broker handling**: None. The `yield` at line 141 fires immediately after cache warming and realtime setup — the app starts serving requests even if Redis is down.

**Module-level flags**: No `_broker_reachable` or similar flag exists.

### Celery App Config (`src/solstein/celery_config.py:26–34`)

```python
celery_app = Celery(
    "solstein",
    broker=settings.celery_broker_url or "redis://localhost:6379/0",
    backend=settings.celery_result_backend or "redis://localhost:6379/1",
    include=["solstein.worker_tasks", "solstein.worker.export_tasks"],
)
```

Broker URL comes from `settings.celery_broker_url` (env var). Default: `redis://localhost:6379/0`.

### Existing Pattern for Non-Critical Startup Steps

```python
# lines 121–128 (cache warming — pattern to follow)
try:
    from solstein.infrastructure.cache import CacheManager as _CacheManager
    _cache = _CacheManager()
    _asyncio.create_task(warm_cache(_cache))
    logger.info("Cache warming task scheduled")
except Exception as _exc:
    logger.warning("Cache warming could not start", error=str(_exc))
```

---

## Problem Statement

The FastAPI lifespan block (`main.py:69–141`) performs no Celery broker reachability check. The application starts and begins serving API traffic even when Redis is completely unreachable. Async job submission endpoints (`POST /async/enrich/single`, etc.) will succeed at request validation then silently fail at task dispatch time — after the response has already been sent.

---

## Acceptance Criteria

- [ ] Lifespan startup block pings the Celery broker before `yield`
- [ ] If broker is reachable but no workers are connected: log WARNING, continue startup (workers may start later)
- [ ] If broker is completely unreachable (connection refused / timeout): log ERROR with broker URL; **decision required**: fail startup (raise) OR continue with degraded mode flag
- [ ] Startup check must complete in ≤ 5 seconds (use `timeout=5` on `inspect`)
- [ ] Check is async-safe (run in thread pool via `asyncio.to_thread` or use async Celery inspect)
- [ ] Test: mock broker unreachable → assert startup log contains error (and optionally raises)
- [ ] Test: mock broker reachable → assert startup proceeds normally

---

## Tasks

- [ ] Insert after `main.py:128` (after cache warming, before realtime):
  ```python
  # STORY-358: Verify Celery broker reachability on startup
  try:
      from solstein.celery_config import celery_app as _celery_app
      import asyncio as _asyncio

      def _ping_broker():
          inspect = _celery_app.control.inspect(timeout=5)
          return inspect.ping()

      ping_result = await _asyncio.to_thread(_ping_broker)
      if ping_result:
          logger.info(f"Celery broker reachable: {len(ping_result)} worker(s) connected")
      else:
          logger.warning("Celery broker reachable but no workers connected on startup")
  except Exception as _broker_exc:
      logger.error(f"Celery broker unreachable on startup: {_broker_exc}",
                   broker_url=settings.celery_broker_url)
      # Decide: raise to block startup, or continue with degraded mode
  ```
- [ ] Team decision: raise vs warn-and-continue — document in code comment
- [ ] Write tests

## Key Files

| File | Line | Note |
|------|------|------|
| `src/solstein/api/main.py` | 128 | Insert broker check after this line |
| `src/solstein/api/main.py` | 141 | `yield` — app starts serving here |
| `src/solstein/celery_config.py` | 26 | `celery_app` — broker URL from settings |
