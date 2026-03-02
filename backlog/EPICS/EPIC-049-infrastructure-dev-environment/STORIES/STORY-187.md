# STORY-187: Add Docker Compose for Local Development Stack

| Field | Value |
|-------|-------|
| **Status** | 🟡 Open |
| **Priority** | P2 — Medium |
| **Size** | M (1 day) |
| **Epic** | EPIC-049 Infrastructure & Dev Environment |
| **Created** | 2026-03-01 |
| **Risk** | Low — additive, doesn't affect existing code |
| **Assigned** | — |

---

## Audit Verdict

**MISSING DEV INFRASTRUCTURE** — no `docker-compose.yml` for local development.

Developers currently need to:
1. Install PostgreSQL locally
2. Install Redis locally
3. Start them manually
4. Configure `.env` with correct ports
5. Start API server separately
6. Start Celery worker separately

This is error-prone and not documented.

---

## Problem Statement

A new developer cannot easily start the full Solstein stack. The existing `docker-compose.yml` (if any) may only define the database. A complete dev stack needs:
- PostgreSQL (with initial schema)
- Redis
- FastAPI server (auto-reload)
- Celery worker

With one command: `docker-compose up`

---

## Impact

| Dimension | Severity |
|-----------|----------|
| Developer Experience | 🟠 High — friction for new contributors |
| Onboarding | 🟠 High — time to first run is high |
| Consistency | 🟡 Medium — different devs have different local setups |
| Security | ⬜ None |
| Performance | ⬜ None |

---

## Affected Files

| File | Lines | Change Type |
|------|-------|-------------|
| `docker-compose.yml` | New or rewrite | Full dev stack definition |
| `docker/Dockerfile` | Existing | May need update for dev mode |
| `.env.example` | Existing | Add Docker-specific vars |
| `docs/development.md` | Existing | Document docker-compose usage |

---

## Dependencies

- **Hard**: STORY-186 (Redis module must be installed in image)
- **Soft**: None
- **Supersedes**: Nothing

---

## Architectural Requirements

**REQ-1**: `docker-compose.yml` defines 4 services:
```yaml
services:
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: solstein
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  api:
    build: .
    command: uvicorn solstein.api.main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      - DATABASE__URL=postgresql+asyncpg://postgres:postgres@db:5432/solstein
      - REDIS__URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  worker:
    build: .
    command: celery -A solstein.celery_config worker --loglevel=info
    volumes:
      - .:/app
    environment:
      - DATABASE__URL=postgresql+asyncpg://postgres:postgres@db:5432/solstein
      - REDIS__URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
```

**REQ-2**: `docker-compose up` starts all services without errors.

**REQ-3**: API health endpoint returns 200: `curl http://localhost:8000/health`

**REQ-4**: Celery worker shows "Connected to redis" in logs.

---

## Acceptance Criteria

- [ ] `docker-compose up -d` starts all 4 services
- [ ] `curl http://localhost:8000/health` returns `{"status": "healthy"}`
- [ ] `docker-compose logs worker` shows Celery connected to Redis
- [ ] `docker-compose down` stops all services cleanly
- [ ] Changes to source code trigger auto-reload in API container
- [ ] Documentation updated with `docker-compose` commands

---

## Definition of Done

- [ ] `docker-compose.yml` created and tested
- [ ] README or development docs updated
- [ ] New developer can start full stack in < 5 minutes

---

## Change Log

| Date | Author | Note |
|------|--------|------|
| 2026-03-01 | Analysis Run | Identified gap: no easy way to start full stack |
