# Epic: Developer Experience (DX) Improvements (EPIC-028)

## Overview
Enhance developer productivity through improved tooling, documentation, and local development environment. Reduce onboarding time and make development enjoyable.

## Background
Current pain points:
- Complex local setup process
- No hot reload for development
- Debugging difficult
- Documentation scattered
- IDE support limited
- Testing slow and cumbersome

## Goals
- [ ] One-command local setup
- [ ] Hot reload for all services
- [ ] Comprehensive debugging tools
- [ ] IDE autocomplete and navigation
- [ ] Fast test execution
- [ ] Developer happiness score >4/5

## Success Metrics
| Metric | Current | Target |
|--------|---------|--------|
| Onboarding Time | 2-3 weeks | <1 day |
| Local Setup Time | 4+ hours | <15 min |
| Test Execution | Slow | <5 min |
| Developer Satisfaction | Unknown | >4/5 |

---

## Stories

### Story 1: Docker Compose Development Environment
**Points:** 5
**Priority:** P0

One-command local development setup.

**docker-compose.dev.yml:**
```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.dev
    volumes:
      - .:/app
      - /app/.venv  # Don't overwrite venv
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=development
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/solstein
      - REDIS_URL=redis://redis:6379
    command: uvicorn solstein.api.main:app --reload --host 0.0.0.0
    depends_on:
      - db
      - redis
      - elasticsearch

  db:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: solstein
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  elasticsearch:
    image: elasticsearch:8.5.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"

  celery-worker:
    build:
      context: .
      dockerfile: Dockerfile.dev
    volumes:
      - .:/app
    command: celery -A solstein.celery_config worker --loglevel=info
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
```

**Makefile:**
```makefile
.PHONY: dev setup test lint

dev: ## Start development environment
	docker-compose -f docker-compose.dev.yml up

setup: ## Initial setup
	cp .env.example .env
	docker-compose -f docker-compose.dev.yml build
	docker-compose -f docker-compose.dev.yml run --rm api alembic upgrade head

dev-shell: ## Open shell in dev container
	docker-compose -f docker-compose.dev.yml exec api bash

test: ## Run tests
	docker-compose -f docker-compose.dev.yml exec api pytest

lint: ## Run linters
	docker-compose -f docker-compose.dev.yml exec api black .
	docker-compose -f docker-compose.dev.yml exec api ruff check --fix .
```

**README Setup Instructions:**
```markdown
## Quick Start

```bash
# 1. Clone repository
git clone https://github.com/Ai-Whisperers/solstein.git
cd solstein

# 2. Start development environment
make dev

# 3. Open browser
open http://localhost:8000/docs
```

That's it! 🎉
```

---

### Story 2: Hot Reload for All Services
**Points:** 3
**Priority:** P0

Implement hot reload for development.

**API Hot Reload:**
```python
# Already supported by uvicorn --reload
```

**Celery Worker Hot Reload:**
```python
# watchfiles for Celery
# scripts/watch_celery.py
import subprocess
from watchfiles import run_process

def celery_worker():
    subprocess.run([
        "celery", "-A", "solstein.celery_config",
        "worker", "--loglevel=info"
    ])

if __name__ == "__main__":
    run_process("src", target=celery_worker)
```

**Frontend Hot Reload (if applicable):**
- Vite for fast HMR
- React/Vue dev server

**Docker Sync (macOS):**
```yaml
# docker-compose.dev.yml (macOS optimized)
services:
  api:
    volumes:
      - .:/app:cached  # Use cached mount for macOS
```

---

### Story 3: Debugging Tools & IDE Integration
**Points:** 5
**Priority:** P0

Improve debugging experience.

**VS Code Configuration:**
```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "solstein.api.main:app",
        "--reload",
        "--host", "0.0.0.0"
      ],
      "jinja": true
    },
    {
      "name": "Python: Celery Worker",
      "type": "python",
      "request": "launch",
      "module": "celery",
      "args": [
        "-A", "solstein.celery_config",
        "worker",
        "--loglevel=debug"
      ]
    },
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal"
    }
  ]
}
```

**PyCharm Configuration:**
```
# .idea/runConfigurations/
# FastAPI.run.xml
# Celery Worker.run.xml
```

**Debugging Middleware:**
```python
# solstein/api/middleware/debug.py
@app.middleware("http")
async def debug_middleware(request: Request, call_next):
    if DEBUG:
        start_time = time.time()
        
        # Add debug headers
        response = await call_next(request)
        
        process_time = time.time() - start_time
        response.headers["X-Debug-Process-Time"] = str(process_time)
        response.headers["X-Debug-Query-Count"] = str(get_query_count())
        
        return response
    
    return await call_next(request)
```

**IPython Integration:**
```python
# Drop into IPython shell for debugging
import ipdb; ipdb.set_trace()

# Or:
breakpoint()  # Python 3.7+
```

---

### Story 4: IDE Autocomplete & Type Hints
**Points:** 3
**Priority:** P0

Improve type hints for better IDE support.

**Type Hint Coverage:**
```python
# Add type hints to ALL functions
from typing import Optional, List, Dict, Any

async def get_company(
    company_id: str,
    include_metrics: bool = False
) -> Optional[Company]:
    """Get company by ID.
    
    Args:
        company_id: Unique company identifier
        include_metrics: Whether to include financial metrics
        
    Returns:
        Company object or None if not found
    """
    ...

# Use generics
T = TypeVar('T')

async def get_or_create(
    model: Type[T],
    id: str,
    defaults: Dict[str, Any]
) -> Tuple[T, bool]:
    ...
```

**pyright Configuration:**
```json
// pyrightconfig.json
{
  "include": ["src"],
  "exclude": ["**/__pycache__"],
  "venvPath": ".",
  "venv": ".venv",
  "pythonVersion": "3.11",
  "strict": ["src/solstein"]
}
```

**Stub Files:**
```python
# stubs/external_lib.pyi
def complex_function(data: bytes) -> dict[str, Any]: ...
```

---

### Story 5: Fast Test Execution
**Points:** 5
**Priority:** P0

Optimize test suite for speed.

**Current Issues:**
- Tests take too long to run
- Database setup/teardown for each test
- No parallelization

**Optimizations:**

**1. Database Transactions:**
```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="function")
async def db_session():
    """Fast database rollback after each test."""
    connection = await engine.begin()
    transaction = await connection.begin_nested()
    
    yield connection
    
    await transaction.rollback()
    await connection.close()
```

**2. Parallel Test Execution:**
```bash
# pytest-xdist for parallelization
pytest -n auto  # Use all available cores
pytest -n 4     # Use 4 cores
```

**3. Test Categorization:**
```python
# Mark slow tests
@pytest.mark.slow
async def test_full_pipeline():
    pass

# Run only fast tests during development
pytest -m "not slow"

# Run all tests in CI
pytest
```

**4. Fixture Caching:**
```python
@pytest.fixture(scope="session")
def test_data():
    """Load test data once per session."""
    return load_test_data()
```

**Target:** All tests complete in <5 minutes

---

### Story 6: Development Documentation
**Points:** 3
**Priority:** P1

Comprehensive developer documentation.

**Documentation Structure:**
```
docs/developers/
├── README.md              # Getting started
├── setup.md              # Environment setup
├── architecture.md       # System architecture
├── database.md           # Database guide
├── testing.md            # Testing guide
├── debugging.md          # Debugging tips
├── deployment.md         # Deployment guide
├── api-development.md    # Adding new endpoints
├── troubleshooting.md    # Common issues
└── contributing.md       # Contribution guidelines
```

**Architecture Decision Records (ADRs):**
```markdown
# docs/adrs/001-why-fastapi.md

# Why FastAPI?

## Status
Accepted

## Context
We needed a modern Python web framework for our API.

## Decision
Use FastAPI.

## Consequences
- ✅ Async support
- ✅ Automatic OpenAPI docs
- ✅ Type hints
- ⚠️ Team learning curve
```

**Code Tour (VS Code extension):**
```json
// .tours/welcome.tour
{
  "title": "Welcome to Solstein",
  "steps": [
    {
      "file": "src/solstein/api/main.py",
      "line": 1,
      "description": "This is the entry point of the API."
    },
    {
      "file": "src/solstein/domain/models.py",
      "line": 1,
      "description": "Core domain models are defined here."
    }
  ]
}
```

---

### Story 7: CLI Development Tools
**Points:** 3
**Priority:** P1

Custom CLI commands for development.

**CLI Tools:**
```python
# solstein/cli/dev.py
import typer

app = typer.Typer()

@app.command()
def reset_db():
    """Reset development database."""
    typer.confirm("This will delete all data. Continue?", abort=True)
    # Reset logic
    typer.echo("✅ Database reset complete")

@app.command()
def seed_db(count: int = 100):
    """Seed database with test data."""
    # Seed logic
    typer.echo(f"✅ Seeded {count} companies")

@app.command()
def generate_api_client():
    """Generate API client from OpenAPI spec."""
    # Generation logic
    typer.echo("✅ API client generated")

@app.command()
def lint():
    """Run all linters."""
    run_black()
    run_ruff()
    run_mypy()
    typer.echo("✅ All checks passed")
```

**Usage:**
```bash
solstein-dev reset-db
solstein-dev seed-db --count 50
solstein-dev generate-api-client
solstein-dev lint
```

---

### Story 8: Local SSL/TLS
**Points:** 2
**Priority:** P2

Enable HTTPS for local development.

**mkcert Setup:**
```bash
# Install mkcert
brew install mkcert
mkcert -install

# Create certificates
mkcert localhost 127.0.0.1 ::1

# Docker Compose with HTTPS
services:
  api:
    volumes:
      - ./localhost+2.pem:/app/cert.pem
      - ./localhost+2-key.pem:/app/key.pem
    command: uvicorn solstein.api.main:app --host 0.0.0.0 --ssl-keyfile key.pem --ssl-certfile cert.pem
```

**Benefits:**
- Test OAuth redirects
- Test service workers
- Test secure cookies
- Production-like environment

---

## Developer Onboarding Checklist

### Day 1
- [ ] Clone repo
- [ ] Run `make setup`
- [ ] Verify http://localhost:8000/docs works
- [ ] Run first test: `make test`

### Week 1
- [ ] Complete architecture walkthrough
- [ ] Make first PR
- [ ] Set up IDE debugging
- [ ] Join team Slack channel

### Month 1
- [ ] Ship feature to production
- [ ] Update documentation
- [ ] Mentor next new hire

---

## Definition of Done
- [ ] One-command setup works
- [ ] Hot reload operational
- [ ] IDE debugging configured
- [ ] All tests <5 min
- [ ] Documentation complete
- [ ] Team trained

## Estimated Effort
- **Total Points:** 29
- **Duration:** 5-6 weeks
- **Team:** 1 developer

## Dependencies
- EPIC-024 (API Documentation) - For OpenAPI spec
- EPIC-012 (Testing) - Test infrastructure

---

*Created: 2026-03-06*  
*Target Release: Q3 2026*
