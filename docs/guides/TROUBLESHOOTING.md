# Solstein Troubleshooting Guide

> **Last Updated**: 2026-03-01
> **Scope**: Common issues and their solutions

---

## Quick Diagnostics

Run these commands to check system health:

```bash
# Check PostgreSQL
pg_isready -h localhost -p 5432

# Check Redis
redis-cli ping

# Check API (if running)
curl http://localhost:8000/health

# Check all services
./scripts/check-services.sh  # (create this if needed)
```

---

## Installation Issues

### Error: `ModuleNotFoundError: No module named 'redis'`

**Symptom**: Import error when running CLI or starting API
**Cause**: Redis Python package not installed
**Fix**:
```bash
# The package should be installed via uv sync
uv sync

# Or manually:
uv add redis
```

---

### Error: `ModuleNotFoundError: No module named 'solstein.exporters.report_generator'`

**Symptom**: `generate-llm-report` command crashes
**Cause**: Module was moved to `exporters.markdown.generator`
**Fix**: Already fixed in codebase. If you see this, update to latest version.

---

## Database Issues

### Error: `pg_isready` fails

**Symptom**: PostgreSQL connection refused
**Cause**: PostgreSQL not running
**Fix**:
```bash
# Using Docker
docker-compose up -d postgres

# Or system service
sudo systemctl start postgresql
```

---

### Warning: "Database URL may contain default credentials"

**Symptom**: Warning on startup
**Cause**: Using default postgres/postgres credentials
**Fix**: Update `.env` with secure credentials:
```env
DATABASE__URL=postgresql+asyncpg://user:secure_password@localhost:5432/solstein
```

---

## Redis Issues

### Error: `redis-cli ping` fails

**Symptom**: Redis connection refused
**Cause**: Redis not running
**Fix**:
```bash
# Using Docker
docker-compose up -d redis

# Or system service
sudo systemctl start redis
```

---

### Error: 503 Service Unavailable on async endpoints

**Symptom**: POST /companies/{id}/enrich returns 503
**Cause**: Celery/Redis not available
**Fix**:
```bash
# Start Redis
docker-compose up -d redis

# Start Celery worker
./scripts/start-dev.sh
```

---

## CLI Issues

### Error: `score` command crashes with "argument after ** must be a mapping"

**Symptom**: TypeError when running score/analyze-market/compare/export-excel
**Cause**: JSON format mismatch (expects list, got dict)
**Fix**: Already fixed in codebase. The CLI now handles both formats:
- `{"competitors": [...]}` (wrapped)
- `[...]` (flat list)

---

### Error: `generate-llm-report` crashes

**Symptom**: ModuleNotFoundError for report_generator
**Cause**: Import path was wrong
**Fix**: Already fixed. The command now imports from correct location.

---

### DeprecationWarning: CompetitorDataLoader is deprecated

**Symptom**: Warning about deprecated loader
**Cause**: Using old data loader
**Fix**: This is a warning, not an error. The system still works. Full migration to UnifiedCompanyLoader is planned.

---

## API Issues

### Error: Cannot connect to localhost:8000

**Symptom**: Connection refused when accessing API
**Cause**: API server not running
**Fix**:
```bash
# Start full dev environment
./scripts/start-dev.sh

# Or manually:
export PYTHONPATH=src
uvicorn solstein.api.main:app --reload --host 0.0.0.0 --port 8000
```

---

### Error: 401 Unauthorized

**Symptom**: API returns 401
**Cause**: Missing or invalid API key
**Fix**: Include X-API-Key header:
```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/companies
```

---

## Report Generation Issues

### Reports in wrong location (double-nested)

**Symptom**: Reports appear in `output/eneve/eneve/` instead of `output/eneve/`
**Cause**: Both CLI and generator creating company directories
**Fix**: Already fixed. CLI now passes base directory to generator.

---

### Unrounded scores (7.138888...)

**Symptom**: Scores show many decimal places
**Cause**: No formatting applied
**Fix**: Already fixed. Reports now use `format_score()` for 2-decimal formatting.

---

### Market overview shows all zeros

**Symptom**: Phoenix/Salt/Lead counts all show 0
**Cause**: Counting wrong field (tier instead of classification)
**Fix**: Already fixed. Now counts classification field correctly.

---

### "No critical weaknesses identified" boilerplate

**Symptom**: Deep analysis shows generic text
**Cause**: Weakness detection not implemented
**Fix**: Already fixed. Now generates actual weaknesses based on company data.

---

## Getting Help

If issues persist:

1. Check logs: `tail -f logs/api.log logs/worker.log`
2. Run diagnostics: `python -m solstein.cli --help`
3. Verify environment: `python -c "from solstein.config import get_settings; print(get_settings())"`
4. Check system status: `docker-compose ps`

---

*This guide covers issues discovered during the 2026-03-01 live analysis run.*
