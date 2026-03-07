# STORY-186: Install and Configure Redis Python Module

| Field | Value |
|-------|-------|
| **Status** | 🔴 Open |
| **Priority** | P1 — High |
| **Size** | S (< half a day) |
| **Epic** | EPIC-049 Infrastructure & Dev Environment |
| **Created** | 2026-03-01 |
| **Risk** | Low — dependency addition |
| **Assigned** | — |

---

## Audit Verdict

**CONFIRMED MISSING DEPENDENCY** — verified by live execution on 2026-03-01.

```python
>>> import redis
ModuleNotFoundError: No module named 'redis'
```

The `redis` package is not in the virtual environment. This breaks:
- Celery task queue (requires Redis as broker)
- Cache layer (`src/solstein/infrastructure/cache.py`)
- Async enrichment endpoints (return 503 without Redis)

---

## Problem Statement

Redis is a required dependency for Solstein's async architecture. The `pyproject.toml` or `requirements.txt` does not include `redis`, and it's not installed in the `.venv`. Without it:
- `POST /companies/{id}/enrich` returns 503
- Celery worker cannot start
- Cache is unavailable (falls back to in-memory or fails)

---

## Impact

| Dimension | Severity |
|-----------|----------|
| Reliability | 🔴 Critical — async features 100% broken |
| Scalability | 🔴 Critical — no background job processing |
| Performance | 🟠 High — no caching layer |
| Security | ⬜ None |

---

## Affected Files

| File | Lines | Change Type |
|------|-------|-------------|
| `pyproject.toml` | `[dependencies]` | Add `redis = "^5.0"` |
| `uv.lock` | Auto-generated | Update lock file |
| `.venv/` | — | Run `uv sync` or `pip install redis` |

---

## Dependencies

- **Hard**: None
- **Soft**: STORY-187 (docker-compose) — Redis service defined there
- **Supersedes**: Nothing

---

## Architectural Requirements

**REQ-1**: Add `redis = "^5.0"` to `pyproject.toml` dependencies.

**REQ-2**: Run `uv sync` to update lock file and install in `.venv`.

**REQ-3**: Verify import works: `python -c "import redis; print(redis.__version__)"`.

**REQ-4**: Verify cache module loads without error: `python -c "from solstein.infrastructure.cache import get_cache; print('OK')"`.

---

## Acceptance Criteria

- [ ] `python -c "import redis"` succeeds in `.venv`
- [ ] `from solstein.infrastructure.cache import get_cache` succeeds
- [ ] `uv.lock` updated with redis dependency
- [ ] CI passes with new dependency

---

## Definition of Done

- [ ] Redis package added to dependencies
- [ ] Lock file updated
- [ ] Import verification passes

---

## Change Log

| Date | Author | Note |
|------|--------|------|
| 2026-03-01 | Analysis Run | Confirmed via import test in live environment |
