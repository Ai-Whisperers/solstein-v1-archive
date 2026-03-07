# STORY-188: Create Startup Script for Full System (API + Celery)

| Field | Value |
|-------|-------|
| **Status** | 🟡 Open |
| **Priority** | P2 — Medium |
| **Size** | S (< half a day) |
| **Epic** | EPIC-049 Infrastructure & Dev Environment |
| **Created** | 2026-03-01 |
| **Risk** | Low — convenience script |
| **Assigned** | — |

---

## Audit Verdict

**MISSING DEV TOOL** — no single script to start the full system locally.

Currently developers must:
1. Ensure PostgreSQL is running (system service or docker)
2. Ensure Redis is running
3. Terminal 1: `uvicorn solstein.api.main:app --reload`
4. Terminal 2: `celery -A solstein.celery_config worker --loglevel=info`

This is tedious and error-prone.

---

## Problem Statement

A single script `scripts/start-dev.sh` should start all required services (or verify they're running) and launch both the API server and Celery worker in the background, with log aggregation and easy shutdown.

---

## Impact

| Dimension | Severity |
|-----------|----------|
| Developer Experience | 🟡 Medium — reduces friction |
| Onboarding | 🟡 Medium — one command to start |
| Documentation | 🟡 Medium — simpler instructions |
| Security | ⬜ None |
| Performance | ⬜ None |

---

## Affected Files

| File | Lines | Change Type |
|------|-------|-------------|
| `scripts/start-dev.sh` | New (~50 lines) | Startup script |
| `scripts/stop-dev.sh` | New (~20 lines) | Shutdown script |
| `docs/development.md` | Existing | Document scripts |

---

## Dependencies

- **Hard**: PostgreSQL and Redis must be running (script checks or starts them)
- **Soft**: STORY-187 (docker-compose) — alternative to local script
- **Supersedes**: Nothing

---

## Architectural Requirements

**REQ-1**: `scripts/start-dev.sh`:
- Checks if PostgreSQL is running (`pg_isready`)
- Checks if Redis is running (`redis-cli ping`)
- If not running, prints helpful message or starts via docker-compose
- Starts API server in background, logs to `logs/api.log`
- Starts Celery worker in background, logs to `logs/worker.log`
- Prints status: "API: http://localhost:8000", "Logs: logs/"
- Creates PID files for easy shutdown

**REQ-2**: `scripts/stop-dev.sh`:
- Reads PID files
- Gracefully stops API and worker
- Cleans up PID files

**REQ-3**: Both scripts are executable (`chmod +x`) and have shebang (`#!/bin/bash`).

---

## Acceptance Criteria

- [ ] `./scripts/start-dev.sh` starts API and worker (if DB/Redis available)
- [ ] `curl http://localhost:8000/health` returns 200 after start
- [ ] `logs/api.log` and `logs/worker.log` exist and contain startup messages
- [ ] `./scripts/stop-dev.sh` stops both processes
- [ ] Scripts handle case where services are already running (idempotent)

---

## Implementation Note

```bash
#!/bin/bash
# scripts/start-dev.sh
set -e

# Check dependencies
if ! pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
    echo "❌ PostgreSQL not running. Start with: docker-compose up -d db"
    exit 1
fi

if ! redis-cli ping >/dev/null 2>&1; then
    echo "❌ Redis not running. Start with: docker-compose up -d redis"
    exit 1
fi

mkdir -p logs

# Start API
export PYTHONPATH=src
uvicorn solstein.api.main:app --reload --host 0.0.0.0 --port 8000 > logs/api.log 2>&1 &
echo $! > .pid.api
echo "✅ API started (PID: $(cat .pid.api))"

# Start Worker
celery -A solstein.celery_config worker --loglevel=info > logs/worker.log 2>&1 &
echo $! > .pid.worker
echo "✅ Worker started (PID: $(cat .pid.worker))"

echo ""
echo "🚀 Solstein dev environment running!"
echo "   API: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo "   Logs: logs/"
echo "   Stop: ./scripts/stop-dev.sh"
```

---

## Definition of Done

- [ ] `start-dev.sh` and `stop-dev.sh` created and tested
- [ ] Scripts documented in development guide
- [ ] New developer can start full system with 2 commands

---

## Change Log

| Date | Author | Note |
|------|--------|------|
| 2026-03-01 | Analysis Run | Identified friction in manual startup process |
