# 🔧 Solstein Troubleshooting Guide

**Diagnose and resolve common issues in Solstein development and deployment.**

---

## Quick Diagnosis Flowchart

```
Something broken?
│
├─ API not responding → Section 1
├─ Celery tasks failing → Section 2
├─ Scores seem wrong → Section 3
├─ Database connection issues → Section 4
├─ Tests failing → Section 5
├─ Docker problems → Section 6
├─ Performance issues → Section 7
└─ Other → Section 8
```

---

## Section 1: API Not Responding

### Symptom: "Connection refused" or API won't start

**Diagnostic steps:**

```bash
# 1. Check if API process is running
ps aux | grep uvicorn

# 2. Check if port 8000 is in use
lsof -i :8000

# 3. Try to connect
curl http://localhost:8000/health

# 4. Check logs
tail -f worker_output.log
```

### Root Cause 1: Port Already in Use

**Symptoms:**
- `Address already in use`
- Error during `uvicorn solstein.api.main:app --reload`

**Solutions:**

```bash
# Option A: Kill the process on port 8000
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Option B: Use a different port
uvicorn solstein.api.main:app --reload --port 8001

# Option C: Find what's using the port (macOS)
lsof -i :8000 | tail -n1
```

### Root Cause 2: Dependencies Not Installed

**Symptoms:**
- `ModuleNotFoundError: No module named 'solstein'`
- `ImportError: cannot import name 'FastAPI'`

**Solution:**

```bash
# Reinstall in editable mode
pip install -e ".[dev]"

# Verify
python -c "import solstein; print('✓ solstein imported')"
```

### Root Cause 3: Python Wrong Version

**Symptoms:**
- `SyntaxError: invalid syntax` on Python < 3.10
- Type hint errors on Python < 3.9

**Solution:**

```bash
# Check Python version
python --version  # Must be 3.10+ (3.12 recommended)

# Use virtual environment with correct Python
python3 -m venv venv  # Use python3.10, python3.11, or python3.12
source venv/bin/activate
pip install -e ".[dev]"
```

### Root Cause 4: Configuration Missing or Invalid

**Symptoms:**
- `ValidationError: SOLSTEIN_DATABASE__URL cannot be empty`
- `FileNotFoundError: data/input/ not found`

**Solutions:**

```bash
# 1. Create .env file
cp .env.example .env  # or create manually

# 2. Verify DATABASE__URL is set
echo $SOLSTEIN_DATABASE__URL

# 3. Create missing data directory
mkdir -p data/input data/output/exports

# 4. Check config.py for defaults
python -c "from solstein.config import get_settings; print(get_settings().database.url)"
```

**Expected .env:**

```env
SOLSTEIN_DATABASE__URL=postgresql://postgres:postgres@localhost:5432/solstein
SOLSTEIN_DATA__DATA_DIR=data/input
SOLSTEIN_DATA__EXPORT_DIR=data/output/exports
SOLSTEIN_REDIS__URL=redis://localhost:6379/0
SOLSTEIN_API__HOST=127.0.0.1
SOLSTEIN_API__PORT=8000
```

### Root Cause 5: API Starts but Returns Errors

**Symptoms:**
- `GET /health` returns 500 error
- Endpoint returns 422 validation error

**Diagnosis:**

```bash
# 1. Check stdout/stderr
# (look at terminal where API is running)

# 2. Enable debug logging
export SOLSTEIN_API__DEBUG=true

# 3. Enable database query logging
export SOLSTEIN_DATABASE__ECHO=true

# 4. Try endpoint with verbose curl
curl -v http://localhost:8000/companies
```

**Common 422 Errors:** Schema validation failed. Check:
- Request body matches schema
- All required fields present
- No extra fields with strict validation

**Common 500 Errors:** Check logs for:
- Database connection failure
- Missing environment variable
- Unhandled exception in route handler

---

## Section 2: Celery Tasks Failing

### Symptom: "Task crashed" or tasks not executing

**Diagnostic steps:**

```bash
# 1. Check if Redis is running
redis-cli ping  # Should return PONG

# 1b. Check Python Redis client
.venv/bin/python3 -c "import redis"  # Should exit 0

# 2. Check if Celery worker is running
ps aux | grep celery

# 3. Check worker logs
# (look at terminal where celery worker is running)

# 4. Monitor active tasks
celery -A solstein.worker inspect active

# 5. Check worker stats
celery -A solstein.worker inspect stats
```

### Root Cause 1: Redis Not Running or Unreachable

**Symptoms:**
- `ConnectionRefusedError` when enqueuing task
- Celery worker can't connect to broker

**Solutions:**

```bash
# Check if Redis is running
ps aux | grep redis-server

# Start Redis (macOS with Homebrew)
brew services start redis

# Start Redis (Docker)
docker run -p 6379:6379 redis:latest

# Start Redis (Linux)
sudo systemctl start redis-server

# Verify connection
redis-cli ping  # Should return PONG
```

### Root Cause 2: Celery Worker Not Running

**Symptoms:**
- Task is enqueued but never executes
- No worker processes in `ps aux`

**Solution:**

```bash
# Start Celery worker (in separate terminal)
celery -A solstein.worker worker --loglevel=info

# Or with concurrency settings
celery -A solstein.worker worker --loglevel=info --concurrency=4
```

### Root Cause 3: Task Execution Crashes

**Symptoms:**
- Task returns failed state
- Worker shows exception trace

**Diagnosis:**

```bash
# 1. Look at worker log output (where celery is running)
# Should show traceback

# 2. Check task configuration
# Are all dependencies available in worker?

# 3. Check for import errors
# Worker needs access to all modules

# 4. Verify file paths are absolute
# Don't use relative paths in tasks
```

**Common Crashes:**
- `ImportError` — Task module not importable from worker
- `FileNotFoundError` — Relative path instead of absolute
- `Database error` — Connection pool exhausted or timeout

### Root Cause 4: Task Hangs or Timeout

**Symptoms:**
- Task running forever
- Timeout after 15 minutes

**Diagnosis:**

```bash
# 1. Check if task is actually running
celery -A solstein.worker inspect active

# 2. Kill hung task
celery -A solstein.worker revoke TASK_ID

# 3. Check for deadlocks in code
# (long-running operations without yielding)
```

**Solutions:**
- Add timeout parameter to task: `@shared_task(time_limit=300)`
- Break large operations into smaller subtasks
- Use pagination for bulk operations
- Monitor task execution time in logs

### Root Cause 5: Redis Memory Full or Keys Corrupted

**Symptoms:**
- `OOM command not allowed when used memory > 'maxmemory'`
- Celery broker gives weird errors
- Task results stored incorrectly

**Solutions:**

```bash
# Check Redis memory usage
redis-cli info memory

# Flush all data (dev only!)
redis-cli FLUSHALL

# Check broker key structure
redis-cli KEYS "celery*" | head -20

# Monitor real-time
redis-cli MONITOR
```

---

## Section 3: Scores Seem Wrong

### Symptom: "Score doesn't match expected value" or classification off

**Diagnostic checklist:**

```bash
# 1. Verify scoring config loaded correctly
python << 'EOF'
from solstein.config import get_settings
settings = get_settings()
print(f"Growth base score: {settings.scoring.growth.base_score}")
print(f"FH base score: {settings.scoring.financial_health.base_score}")
print(f"CP base score: {settings.scoring.competitive_position.base_score}")
EOF

# 2. Manually calculate score
python << 'EOF'
from solstein.analytics.scoring import GrowthScorer
from solstein.domain.models import Company, FinancialMetric

company = Company(id="test", name="Test Corp")
company.financials = FinancialMetric(revenue=100.0, growth_rate=25.0)

scorer = GrowthScorer()
result = scorer.calculate_scores(company)
print(f"Growth score: {result.growth_score}")
print(f"FH score: {result.financial_health_score}")
print(f"CP score: {result.competitive_position_score}")
print(f"Classification: {result.classification}")
EOF

# 3. Check against golden dataset
pytest tests/data_quality/test_ai_insights.py -v
```

### Root Cause 1: Stale Configuration

**Symptoms:**
- Changed `scoring_config.py` but score unchanged
- Environment variable not picked up

**Solutions:**

```bash
# 1. Restart API
# (changes to config.py require restart)

# 2. Verify environment variable is set
echo $SOLSTEIN_SCORING__GROWTH__BASE_SCORE

# 3. Override via environment
export SOLSTEIN_SCORING__GROWTH__BASE_SCORE=4.5
uvicorn solstein.api.main:app --reload
```

### Root Cause 2: Input Data Missing or Invalid

**Symptoms:**
- Score is always 5.0 (base score)
- Financial metrics are None

**Diagnosis:**

```bash
# Check company data
python << 'EOF'
from solstein.data.repositories import JsonFileRepository
repo = JsonFileRepository()
companies = repo.find_all()
for c in companies[:3]:
    print(f"{c.name}:")
    print(f"  Revenue: {c.financials.revenue}")
    print(f"  Growth: {c.financials.growth_rate}")
    print(f"  Employees: {c.financials.employees}")
EOF

# Verify data in database
psql -d solstein -c "SELECT id, name, growth_rate, revenue FROM companies LIMIT 3;"
```

**Common Issues:**
- `NULL` or missing values in financials
- `0` instead of `None` for missing data
- Data in wrong units (e.g., EUR instead of millions)

### Root Cause 3: Custom Thresholds Not Applied

**Symptoms:**
- Bonus scores not appearing in breakdown
- Company should be Phoenix but is Salt

**Diagnosis:**

```bash
# Check scoring breakdown
python << 'EOF'
from solstein.data.repositories import JsonFileRepository
from solstein.analytics.scoring import GrowthScorer

repo = JsonFileRepository()
company = repo.find_by_id("company-id")

scorer = GrowthScorer()
scorer.calculate_scores(company)

# Print breakdown
import json
print(json.dumps(company.scoring_breakdown, indent=2, default=str))
EOF
```

**Look for:**
- Missing `ScoreComponent` entries in breakdown
- Bonus formula not matching config
- Threshold values in wrong units (M vs EUR)

### Root Cause 4: Double-Scoring Bug

**Symptoms:**
- Score increases each time calculated
- Classification changes on recalculation
- Bonus values stacked

**Issue:** Calling `calculate_scores()` twice on same Company instance

**Root Cause:** ADR-008 — `calculate_scores()` mutates input, doesn't copy

**Solution:**

```python
# WRONG — modifies company, scores stack on second call
company = scorer.calculate_scores(company)
company = scorer.calculate_scores(company)  # ❌ Bonuses doubled!

# CORRECT — create new instance or reset scores first
from copy import deepcopy
company_copy = deepcopy(company)
scored = scorer.calculate_scores(company_copy)

# Or reset before recalculating
company.growth_score = None
company.financial_health_score = None
company.competitive_position_score = None
scored = scorer.calculate_scores(company)
```

### Root Cause 5: Golden Dataset Boundary Drift

**Symptoms:**
- Company classified as Lead should be Salt
- Test failures: `expected Phoenix but got Salt`

**Diagnosis:**

```bash
# Run golden dataset regression
pytest tests/data_quality/test_ai_insights.py::test_classification_boundaries -v

# See which companies are misclassified
pytest tests/data_quality/test_ai_insights.py -v --tb=short
```

**Solution:** Check if scoring logic changed. If intentional:
1. Update golden dataset
2. Update ADR with new thresholds
3. Update CHANGELOG

---

## Section 4: Database Connection Issues

### Symptom: "Connection refused" or "Database does not exist"

**See:** [Database Setup Guide → Part 7: Troubleshooting](database.md#part-7-troubleshooting)

Quick summary:

```bash
# Test local PostgreSQL connection
psql -h localhost -U postgres -d solstein -c "SELECT 1;"

# Test from Python
python << 'EOF'
from solstein.config import get_settings
from sqlalchemy import create_engine, text

settings = get_settings()
engine = create_engine(settings.database.url)
with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM companies"))
    print(f"Companies: {result.scalar()}")
EOF

# Test Supabase connection
PGPASSWORD=YOUR_PASSWORD psql -h db.PROJECT_ID.supabase.co -U postgres -d postgres -c "SELECT 1;"
```

---

## Section 5: Tests Failing

### Symptom: "pytest fails" or "all tests broken"

**Quick fix:**

```bash
# 1. Ensure correct Python version
python --version  # Must be 3.10+ (3.12 recommended)

# 2. Install test dependencies
pip install -e ".[dev]"

# 3. Set PYTHONPATH
export PYTHONPATH=src:.

# 4. Run minimal test
pytest tests/unit/test_models.py::test_company_creation -v
```

### Root Cause 1: Import Errors in Tests

**Symptoms:**
- `ModuleNotFoundError: No module named 'solstein'`
- `ImportError` in test files

**Solution:**

```bash
# Set PYTHONPATH before running tests
export PYTHONPATH=src:.
pytest tests/

# Or use pytest.ini (already configured)
# Just run: pytest tests/
```

### Root Cause 2: Fixture Not Found

**Symptoms:**
- `fixture 'mock_company' not found`
- `fixture 'client' not found`

**Solution:**

```bash
# Fixtures are in conftest.py
ls tests/conftest.py

# Verify fixtures are defined
grep "def " tests/conftest.py | grep fixture
```

**Common issue:** Running test file directly instead of via pytest

```bash
# WRONG
python tests/unit/test_models.py

# RIGHT
pytest tests/unit/test_models.py
```

### Root Cause 3: Test Data Issues

**Symptoms:**
- Test fails due to missing data
- `FileNotFoundError: data/input/` not found

**Solution:**

```bash
# Create test data structure
mkdir -p data/input data/output/exports

# Or mock data in conftest.py (already done)
# Check how fixtures create mock data
grep -A 10 "def mock_company" tests/conftest.py
```

### Root Cause 4: Async Test Configuration

**Symptoms:**
- `asyncio.TimeoutError` or event loop issues
- Async tests hang or fail

**Solution:**

```bash
# Install pytest-asyncio
pip install pytest-asyncio

# Use @pytest.mark.asyncio decorator
@pytest.mark.asyncio
async def test_async_function():
    result = await my_async_function()
    assert result == expected

# Or configure in pyproject.toml:
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

### Root Cause 5: Race Conditions in Tests

**Symptoms:**
- Test passes sometimes, fails randomly
- "Flaky" tests
- `timeout` errors on slow machines

**Solution:**

Use `pytest.mark.asyncio` and `pytest.fixture(scope="function")` for reliable async test isolation.

Quick fix:

```python
# WRONG — arbitrary timeout
import time
time.sleep(0.5)  # Hope it's done by then

# BETTER — condition-based waiting
from unittest.mock import Mock, patch
import time

max_wait = 5
start = time.time()
while time.time() - start < max_wait:
    if mock_obj.method_called:
        break
    time.sleep(0.01)
assert mock_obj.method_called
```

---

## Section 6: Docker Problems

### Symptom: Container won't start or crashes

**Diagnostic steps:**

```bash
# Check container status
docker ps -a

# View container logs
docker logs solstein-api

# Inspect container
docker inspect solstein-api

# Try to run interactively
docker run -it solstein:latest /bin/bash
```

### Root Cause 1: Build Fails

**Symptoms:**
- `docker build` returns error
- `[ERROR] failed to solve`

**Diagnosis:**

```bash
# Rebuild with verbose output
docker build -t solstein:latest --progress=plain .

# Check Dockerfile
cat docker/Dockerfile
```

**Common issues:**
- Python version not available (line 2 of Dockerfile)
- Build dependencies missing
- `requirements.txt` has conflicting packages

### Root Cause 2: Container Starts but Exits Immediately

**Symptoms:**
- `docker run solstein:latest` exits with code 1
- No error message visible

**Solution:**

```bash
# Run with attached logs
docker run -it solstein:latest

# Check entrypoint
docker inspect solstein:latest | grep -A 5 '"Cmd"'

# Run different command
docker run -it solstein:latest /bin/bash
```

### Root Cause 3: Environment Variables Not Set

**Symptoms:**
- Container crashes with config error
- `SOLSTEIN_DATABASE__URL cannot be empty`

**Solution:**

```bash
# Pass env vars to container
docker run \
  -e SOLSTEIN_DATABASE__URL=postgresql://... \
  -e SOLSTEIN_REDIS__URL=redis://redis:6379/0 \
  solstein:latest

# Or use env file
docker run --env-file .env solstein:latest

# Or in docker-compose
# (environment: section in compose file)
```

### Root Cause 4: Volume Mounts Not Working

**Symptoms:**
- `data/input/` appears empty in container
- Files not persisting between runs

**Solution:**

```bash
# Check mount is working
docker run -v /path/to/data:/app/data solstein:latest \
  ls -la /app/data

# Use absolute paths
docker run -v $(pwd)/data:/app/data solstein:latest

# In docker-compose
volumes:
  - ./data:/app/data  # Relative to docker-compose.yml
```

### Root Cause 5: Network Issues in Docker Compose

**Symptoms:**
- API can't reach Redis or PostgreSQL
- `ConnectionRefusedError` from inside container

**Solution:**

```bash
# Use service names from docker-compose.yml
# Inside container: "redis" not "localhost"

# Check network connectivity
docker exec solstein-api ping redis
docker exec solstein-api nc -zv postgres 5432

# Verify compose network
docker network ls
docker network inspect solstein_default
```

---

## Section 7: Performance Issues

### Symptom: API responses slow or timeouts

### Root Cause 1: Slow Database Queries

**Diagnosis:**

```bash
# Enable query logging
export SOLSTEIN_DATABASE__ECHO=true
python -c "from solstein import main; ..."  # See query logs

# Or check PostgreSQL logs
psql -d solstein -c "SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"

# Use EXPLAIN ANALYZE
psql -d solstein << 'EOF'
EXPLAIN ANALYZE SELECT * FROM companies WHERE industry = 'Software';
EOF
```

**Common Issues:**
- Missing indexes on `industry`, `market`, `tier`
- N+1 query problems
- Sorting/filtering on non-indexed columns

**Solution:**

```sql
-- Add indexes
CREATE INDEX ON companies(industry);
CREATE INDEX ON companies(market);
CREATE INDEX ON companies(tier);
CREATE INDEX ON financial_metrics(company_id);
```

### Root Cause 2: Connection Pool Exhausted

**Symptoms:**
- `connection pool timeout` or `too many connections`
- Error increases under load

**Diagnosis:**

```bash
# Check current connections
psql -d solstein -c "SELECT count(*) FROM pg_stat_activity;"

# See pool size config
python -c "from solstein.config import get_settings; print(get_settings().database.pool_size)"
```

**Solution:**

```env
# Increase pool size
SOLSTEIN_DATABASE__POOL_SIZE=30

# Or check for connection leaks
# (not calling .close() or using context manager)
```

### Root Cause 3: Memory Leaks

**Symptoms:**
- Memory usage grows over time
- API becomes slower until restart

**Diagnosis:**

```bash
# Monitor memory during load test
watch -n 1 'ps aux | grep uvicorn | grep -v grep | awk "{print \$6}"'

# Profile with memory profiler
pip install memory-profiler
python -m memory_profiler solstein/api/main.py
```

**Common causes:**
- Unbounded caches (no TTL)
- Large objects not garbage collected
- Circular references

### Root Cause 4: High CPU Usage

**Symptoms:**
- CPU 100% constant
- Response times slow

**Diagnosis:**

```bash
# Profile CPU
pip install py-spy
py-spy record -o profile.svg -- uvicorn solstein.api.main:app

# Find hot functions
python -m cProfile -s cumulative solstein/api/main.py
```

**Common causes:**
- Inefficient algorithms (N² complexity)
- Spinning loops in Celery
- Unoptimized scoring calculations

---

## Section 8: Other Common Issues

### "AttributeError: Company has no attribute X"

**Cause:** Domain model schema changed; old cached instances don't have new fields

**Solution:**
```bash
# Restart Python/API process
# Clear any pickle files
rm -rf *.pickle __pycache__
```

### "KeyError in scoring breakdown"

**Cause:** Scoring dimensions renamed or removed

**Solution:** Check recent ADR or git diff for scoring changes. Update calculation code or revert.

### "Excel export contains #NAME! errors"

**Cause:** Formula uses undefined name or wrong cell reference

**Solution:** Check ExcelExporter formula generation. Verify cell references after adding new columns.

### "API returns 403 Forbidden"

**Cause:** Authentication failing or missing auth token

**Note:** Current design uses permissive auth (no real blocking). Check ADR-007.

**Solution:** Add `Authorization: Bearer token` header if token required.

---

## Getting Help

If your issue isn't here:

1. **Search the codebase:** `grep -r "error message" src/`
2. **Check logs:** Look at stdout/stderr where processes are running
3. **Enable debug mode:** Set `SOLSTEIN_API__DEBUG=true`
4. **Test in isolation:** Create minimal reproduction script
5. **Ask in code comments:** Post to GitHub issues with:
   - Exact error message
   - Steps to reproduce
   - Environment (Python version, OS, etc.)
   - Relevant logs

---

## References

- [Database Setup Guide](database.md)
- [Developer Guide](developer.md)
- [Operator Guide](operator.md)
- [Architecture Decisions](../architecture/decisions.md)

---

*Last Updated: February 20, 2026*
*Maintained by: Support & DevOps Team*


---

## Section 9: Async Task Issues (Phase 13)

### Symptom: Task Retries Endlessly

**Cause**: Task is retrying but never succeeding

**Diagnosis**:

```bash
# Check logs for retry pattern
tail -f application.log | grep RETRY-ATTEMPT

# Output should show:
# [RETRY-ATTEMPT-1] Task will retry in 5s: Connection timeout
# [RETRY-ATTEMPT-2] Task will retry in 10s: Rate limit exceeded
# [RETRY-ATTEMPT-3] Task will retry in 20s: Service unavailable
# [RETRY-FAILED] Task permanently failed after 3 attempts
```

**Solutions**:

1. **Check external service**: Is the API/service the task is calling actually available?
   ```bash
   curl https://api.example.com/health
   ```

2. **Check network connectivity**: Can the worker reach the service?
   ```bash
   ping api.example.com
   ```

3. **Check rate limiting**: Is the external service rate limiting us?
   ```bash
   # Look for 429 (Too Many Requests) in logs
   grep "429" application.log
   ```

4. **Increase max retries** (if transient issue):
   ```python
   @shared_task(bind=True, max_retries=5)  # Increase from 3
   def my_task(self):
       pass
   ```

**See**: [Retry Logic Guide](./retry-logic.md)

---

## Section 10: Rate Limiting Issues (Phase 13)

### Symptom: All Requests Return 429 (Too Many Requests)

**Cause**: Rate limiter is rejecting all requests

**Diagnosis**:

```bash
# Check if rate limiter is working
curl -i http://localhost:8000/companies/1/enrich
# If 429: Rate limit exceeded

# Check health endpoint (should NOT be rate limited)
curl -i http://localhost:8000/health
# Should return 200, not 429
```

**Solutions**:

1. **Check Redis connection**:
   ```bash
   redis-cli ping
   # Should return: PONG
   .venv/bin/python3 -c "import redis"
   ```

2. **Check rate limit configuration**:
   ```bash
   # In .env
   RATE_LIMIT_PER_MINUTE=100  # Default
   ```

3. **Check client identification**:
   - Rate limiter tracks by client IP
   - If all requests from same IP, they share the limit
   - Solution: Use different client IPs or increase limit

4. **Reset rate limiter** (if stuck):
   ```bash
   # Clear Redis rate limit keys
   redis-cli KEYS "rate_limit:*" | xargs redis-cli DEL
   ```

**See**: [Rate Limiting Guide](./rate-limiting.md)

---

## Section 11: Health Check Issues (Phase 13)

### Symptom: /health Returns 503 (Unhealthy)

**Cause**: One or more critical components are down

**Diagnosis**:

```bash
# Check health endpoint
curl http://localhost:8000/health | jq .

# Output shows which components are unhealthy:
{
  "status": "unhealthy",
  "checks": {
    "database": {"status": "disconnected", "healthy": false},
    "cache": {"status": "operational", "healthy": true}
  }
}
```

**Solutions**:

1. **Database down**: Check PostgreSQL
   ```bash
   psql -c "SELECT 1"
   ```

2. **Cache down**: Check Redis
   ```bash
   redis-cli ping
   .venv/bin/python3 -c "import redis"
   ```

3. **Connector down**: Check external API
   ```bash
   curl https://api.example.com/health
   ```

**See**: [Health Checks Guide](./health-checks.md)

### Symptom: /ready Returns 503 (Not Ready)

**Cause**: System is not ready to handle traffic (more strict than /health)

**Diagnosis**:

```bash
# Check readiness
curl http://localhost:8000/ready | jq .

# Shows which connectors are unavailable
{
  "ready": false,
  "checks": {
    "database": {"healthy": true},
    "cache": {"healthy": true},
    "sec_edgar_connector": {"healthy": false},
    "companies_house_connector": {"healthy": false},
    "news_signals_connector": {"healthy": true},
    "github_connector": {"healthy": true}
  }
}
```

**Solution**: Wait for connectors to become available, or reduce required connector count.

**See**: [Health Checks Guide](./health-checks.md)

---
