# EPIC-049: Infrastructure & Dev Environment

> **Discovered**: 2026-03-01 via live end-to-end run analysis  
> **Priority**: P1–P2 — Blocks full system operation  
> **Stories**: 4 ([STORY-186](STORIES/STORY-186.md) through [STORY-189](STORIES/STORY-189.md))  
> **Effort**: M (2–3 days total)

---

## Problem

The infrastructure layer is partially functional: PostgreSQL is running and reachable, but Redis is not available (Python module not installed), the FastAPI server is not started, and the full async/Celery pipeline cannot operate. These are not optional features — they're required for enrichment, caching, and the API layer.

### Infrastructure Status

| Service | Status | Impact |
|---------|--------|--------|
| PostgreSQL 14+ | ✅ Running on localhost:5432 | DB available for persistence |
| Redis | ❌ Module not installed | No cache, no Celery, no async jobs |
| FastAPI server | ❌ Not started | API endpoints unreachable |
| Celery worker | ❌ Cannot start without Redis | Background enrichment impossible |
| Ollama (local LLM) | ❌ Not checked | Privacy-first LLM option unavailable |

---

## Stories

| Story | Title | Priority | Size |
|-------|-------|----------|------|
| [STORY-186](STORIES/STORY-186.md) | Install and configure Redis Python module | P1 | S |
| [STORY-187](STORIES/STORY-187.md) | Add docker-compose for local development stack | P2 | M |
| [STORY-188](STORIES/STORY-188.md) | Create startup script for full system (API + Celery) | P2 | S |
| [STORY-189](STORIES/STORY-189.md) | Document infrastructure troubleshooting guide | P2 | S |

---

## Definition of Done

- [ ] `redis` module installed and importable
- [ ] `docker-compose up` starts PostgreSQL + Redis + API + Celery worker
- [ ] `./scripts/start-dev.sh` starts all services locally
- [ ] Infrastructure troubleshooting guide exists
- [ ] Full system runs end-to-end: API request → Celery job → Redis cache → DB write
