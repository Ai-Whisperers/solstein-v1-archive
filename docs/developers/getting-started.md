# Solstein Development Guide

> **EPIC-028**: Developer Experience - One-command local development setup

## Quick Start

Get the development environment running in under 15 minutes:

```bash
# Clone and setup
git clone <repo-url>
cd solstein

# Option 1: Docker (Recommended)
make dev-setup
make dev

# Option 2: Local (if you have Python 3.11+, PostgreSQL, Redis)
uv sync
source .venv/bin/activate
export PYTHONPATH=src
make run
```

## Development Environments

### Docker Development (Recommended)

The Docker setup provides a complete, isolated environment:

```bash
# Start all services with hot reload
make dev

# Services available:
# - API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - PostgreSQL: localhost:5432
# - Redis: localhost:6379
# - PGAdmin: http://localhost:5050 (with --profile tools)
# - Redis Commander: http://localhost:8081 (with --profile tools)

# Useful commands
make dev-shell        # Enter API container
make dev-logs         # Follow all logs
make dev-stop         # Stop all services
make dev-clean        # Stop and remove volumes
make dev-tools        # Start with admin tools
make dev-test         # Run tests in container
make dev-reset-db     # Reset database
make dev-seed         # Seed with test data
```

### Local Development

If you prefer local development:

**Prerequisites:**
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- uv (package manager)

```bash
# Install dependencies
uv sync
source .venv/bin/activate

# Set environment
export PYTHONPATH=src
export ENVIRONMENT=development
export DATABASE__URL=postgresql://postgres:postgres@localhost:5432/solstein
export REDIS__URL=redis://localhost:6379/0

# Initialize database
python -c "import asyncio; from solstein.infrastructure.database import init_db; asyncio.run(init_db())"

# Start services
make run              # Start API
make worker           # Start Celery worker
make beat             # Start Celery beat

# Or start all with hot reload
make dev-local
```

## Hot Reload

Both Docker and local environments support hot reload:

- **API**: Uvicorn with `--reload` automatically restarts on code changes
- **Celery**: `watchfiles` monitors and restarts workers on changes
- **Database**: Migrations must be run manually

## VS Code Setup

Open the project in VS Code for the best experience:

```bash
code .
```

**Recommended Extensions** (auto-suggested):
- Python, Pylance
- Ruff, Mypy
- Docker
- GitLens

**Debugging** (F5 or Run > Start Debugging):
- `Python: FastAPI (Local)` - Debug local API
- `Python: FastAPI (Docker)` - Attach to Docker container
- `Python: Celery Worker` - Debug worker tasks
- `Python: Pytest Current File` - Debug tests

See `.vscode/launch.json` for all configurations.

## Testing

### Fast Test Execution

```bash
# Run all tests (parallel by default)
pytest

# Run fast tests only
make test-fast

# Run with coverage
pytest --cov=solstein --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests
pytest -m "not slow"    # Skip slow tests

# Run in parallel (4 workers)
pytest -n 4

# Run with verbose output
pytest -xvs tests/test_specific.py
```

### Test Configuration

- **pytest-xdist**: Parallel execution enabled
- **pytest-asyncio**: Async test support
- **pytest-randomly**: Randomized test order
- **5-minute timeout**: Per-test limit

## Debugging

### Local Debugging

```python
# Add breakpoint
import ipdb; ipdb.set_trace()

# Or use built-in breakpoint
breakpoint()
```

### Docker Debugging

```bash
# Attach to running container
docker-compose -f docker-compose.dev.yml exec api bash

# Check logs
docker-compose -f docker-compose.dev.yml logs api -f

# Inspect database
docker-compose -f docker-compose.dev.yml exec db psql -U postgres -d solstein
```

## Code Quality

All code must pass quality checks before committing:

```bash
# Run all checks
python scripts/ci/quality_check.py --only-required

# Check specific file
python scripts/ci/code_smell_detector.py src/solstein/your_file.py

# Format and lint
make format
make lint
make typecheck
```

See [docs/developers/code-quality.md](code-quality.md) for details.

## CLI Tools

### Solstein CLI

```bash
# Main CLI
solstein --help

# Development commands
solstein dev db-reset
solstein dev db-seed --count 100
solstein dev api-client
```

### Development Scripts

```bash
# Database
python scripts/db_manager.py reset
python scripts/db_manager.py seed --companies 1000

# API client generation
python scripts/generate_api_client.py

# Maintenance
python scripts/maintenance_tasks.py cleanup-cache
python scripts/maintenance_tasks.py vacuum-db
```

## Project Structure

```
solstein/
├── src/solstein/          # Application code
│   ├── api/               # FastAPI routes, middleware
│   ├── domain/            # Business logic, models
│   ├── infrastructure/    # Database, external services
│   └── ...
├── tests/                 # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── fixtures/          # Test data
├── scripts/               # Development scripts
├── docker-compose.dev.yml # Docker dev config
├── Dockerfile.dev         # Dev container
├── Makefile               # Development commands
└── docs/developers/       # Documentation
```

## Environment Variables

Key environment variables for development:

```bash
# Required
export PYTHONPATH=src
export ENVIRONMENT=development
export DATABASE__URL=postgresql://postgres:postgres@localhost:5432/solstein
export REDIS__URL=redis://localhost:6379/0

# API
export API__HOST=0.0.0.0
export API__PORT=8000

# LLM (at least one provider)
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...

# Optional
export LOG_LEVEL=DEBUG
export CELERY_LOG_LEVEL=info
```

## Troubleshooting

### Common Issues

**Database connection fails:**
```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Reset database
make dev-reset-db
```

**Import errors:**
```bash
# Ensure PYTHONPATH is set
export PYTHONPATH=src

# Or use editable install
pip install -e .
```

**Celery worker not starting:**
```bash
# Check Redis
redis-cli ping

# Start worker manually
celery -A solstein.celery_config worker --loglevel=debug
```

**Hot reload not working:**
```bash
# Docker: Check volume mounts
docker-compose -f docker-compose.dev.yml config

# Local: Check file watching
uvicorn solstein.api.main:app --reload --reload-dir src
```

## Performance Tips

### Fast Test Execution

1. **Use parallel execution**: `pytest -n auto`
2. **Reuse database**: Tests use transactions
3. **Skip slow tests**: `pytest -m "not slow"`
4. **Use fast fixtures**: See `tests/fixtures/`

### IDE Performance

1. **Exclude large directories**: Already configured in `.vscode/settings.json`
2. **Use Pylance**: Faster than default Python language server
3. **Disable unused extensions**: Keep only essential ones

## Contributing

### Before Committing

```bash
# Run checks
python scripts/ci/quality_check.py --only-required

# Run tests
pytest -m "not slow"

# Format code
make format
```

### PR Guidelines

- Max 500 lines changed per PR
- Max 20 functions per file
- All checks must pass
- Tests included for new features

## Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [Celery Docs](https://docs.celeryq.dev/)
- [EPIC-028 Details](../epics/EPIC-028-DEVELOPER-EXPERIENCE.md)

## Support

- **Issues**: Create GitHub issue
- **Questions**: Ask in #dev channel
- **Code Review**: Request review on PR
