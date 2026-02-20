
# 📜 Operator Guide

**Deploying, Configuring, and Operating the Solstein Platform**

---

## Architecture Overview

```
                    ┌─────────────┐
   Client Requests  │  FastAPI    │  Port 8000
   ──────────────►  │  API        │
                    └──────┬──────┘
                           │ enqueues tasks
                    ┌──────▼──────┐
                    │   Redis     │  Port 6379
                    │   Broker    │
                    └──────┬──────┘
                           │ consumes tasks
                    ┌──────▼──────┐
                    │   Celery    │
                    │   Workers   │
                    └──────┬──────┘
                           │ reads/writes
                    ┌──────▼──────┐
                    │  JSON Data  │
                    │  Directory  │  data/input/
                    └─────────────┘
```

> **Note:** Only one Celery worker process is needed per deployment. Running multiple workers against the same broker is fine for scaling, but ensure tasks are idempotent — the current `batch_score_companies` task is safe to run concurrently.

---

## Prerequisites

| Service | Version | Notes |
|---------|---------|-------|
| Python | 3.12+ | |
| Redis | 5.0+ | Required for Celery task broker |
| (Optional) Docker | 24+ | For containerised deployment |

---

## Environment Variables

Create a `.env` file at the project root:

```env
# Application
SOLSTEIN_ENV=production            # development | production
SOLSTEIN_SECRET_KEY=<your-secret>  # JWT signing key (any secret string)

# Data
SOLSTEIN_DATA_DATA_DIR=data/input
SOLSTEIN_DATA_EXPORT_DIR=data/output/exports

# Redis (Celery broker)
SOLSTEIN_REDIS_URL=redis://localhost:6379/0

# Scoring (override defaults — all optional)
# SOLSTEIN_SCORING_GROWTH_BASE_SCORE=5.0
# SOLSTEIN_SCORING_GROWTH_REVENUE_GROWTH_DIVISOR=20.0
```

---

## Docker Deployment

```bash
# Build and start all services
docker compose -f docker/docker-compose.yml up -d

# Check service status
docker compose -f docker/docker-compose.yml ps

# View logs
docker compose -f docker/docker-compose.yml logs -f api
docker compose -f docker/docker-compose.yml logs -f worker

# Stop
docker compose -f docker/docker-compose.yml down
```

---

## Manual Deployment

```bash
# Terminal 1: API Server
source venv/bin/activate
uvicorn solstein.api.main:app --host 0.0.0.0 --port 8000 --workers 4

# Terminal 2: Celery Worker (one instance is sufficient)
source venv/bin/activate
celery -A solstein.worker worker --loglevel=info --concurrency=4

# Terminal 3 (optional): Celery Beat — scheduled tasks
celery -A solstein.worker beat --loglevel=info
```

---

## Health Monitoring

```bash
# API health check
curl http://localhost:8000/health
# → {"status": "healthy", "version": "0.1.0", "timestamp": "..."}

# Celery worker status
celery -A solstein.worker inspect active
celery -A solstein.worker inspect stats
```

> **Note:** The `/health` endpoint currently checks server availability only. It does not validate Redis connectivity or data directory access. A `200 OK` response confirms the API process is running, not that all downstream services are healthy.

---

## Data Management

### Loading Company Data

Place competitor data in the directory configured as `SOLSTEIN_DATA_DATA_DIR` (default: `data/input/`). The expected file is `competitor_data.json` with the following structure:

```json
{
  "competitors": [
    {
      "company_name": "Acme Energy BV",
      "folder": "acme-energy-bv",
      "revenue": {
        "timeline": [
          {"eur_millions": 12.5, "yoy_growth_pct": 34.0, "confidence": "Confirmed"}
        ]
      },
      "scorecard": {
        "composite_score": 8.2,
        "dimensions": {
          "SaaS Maturity": {"score": 9}
        }
      }
    }
  ]
}
```

### Running Bulk Scoring

```bash
# Via CLI (recommended for operator use)
solstein score data/input/companies.json --output data/output/scored.json

# Via API (async — returns task ID)
curl -X GET "http://localhost:8000/scoring/batch?industry=Energy+Software"
# → {"task_id": "abc-123", "status": "processing"}
```

### Generating Reports

```bash
# Via CLI
solstein export-excel data/input/companies.json data/output/report.xlsx

# Via API (triggers background Celery task)
curl "http://localhost:8000/export/excel?industry=Energy+Software"
# → {"task_id": "abc-123", "filename": "solstein_energy_software_20260220.xlsx"}
```

### Exporting to JSON

```bash
curl "http://localhost:8000/export/json?industry=Energy+Software"
# Returns full scored company dataset as JSON
```

---

## Backup & Recovery

All intelligence data lives as flat JSON files. Back up the data directory with standard tools:

```bash
# Backup
tar -czf solstein-data-$(date +%Y%m%d).tar.gz data/input/

# Restore
tar -xzf solstein-data-20260220.tar.gz
```

---

## Performance Tuning

| Setting | Default | Recommendation |
|---------|---------|---------------|
| API workers (`--workers`) | 1 | 4× CPU count for production |
| Celery concurrency (`--concurrency`) | 4 | Match to available cores |
| Redis `maxmemory` | default | Set `256mb` for small deployments |
| Loader cache | In-process | Cache is per-process. Scale by running more API replicas. |

---
