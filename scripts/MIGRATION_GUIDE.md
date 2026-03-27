# Script Migration Guide

This document explains the transition from root-level bypass scripts to the API-backed workflow.

## What Changed

Previously, two root-level scripts existed that called the domain layer directly, bypassing the API:

| Old Script | What It Did | Equivalent |
|------------|-------------|------------|
| `run_research.py` | Triggered research for a company or batch of companies | `POST /api/v1/research/{company_id}` or use the API directly |
| `run_market_pipeline.py` | Triggered market data refresh and pipeline runs | `POST /api/v1/market/refresh` or use the API directly |

These scripts were deleted because they bypassed authentication, rate limiting, request validation, structured logging, error handling middleware, and audit trails.

## Using the API Instead

All operations should go through the API. The API provides authentication, audit logging, rate limiting, and consistent error handling.

### Start the API

```bash
make run
# or with Docker:
make dev
```

### Common Operations

**Trigger research for a company:**
```bash
curl -X POST http://localhost:8000/api/v1/research/{company_id} \
  -H "Authorization: Bearer $API_TOKEN"
```

**List companies:**
```bash
curl http://localhost:8000/api/v1/companies \
  -H "Authorization: Bearer $API_TOKEN"
```

**Health check:**
```bash
curl http://localhost:8000/health
```

## CLI (scripts/solstein_cli.py)

The CLI currently imports domain services directly. It is being migrated to use the API as its backend (tracked separately). In the meantime, the CLI remains functional but should only be used for local development, not production operations.

To use the CLI:
```bash
PYTHONPATH=src python scripts/solstein_cli.py --help
```

## Makefile Targets

The Makefile provides the canonical interface for common operations:

```bash
make help              # List all available targets
make migrate           # Run database migrations
make seed              # Seed development database
make test              # Run all tests
make deploy            # Run deploy-readiness checks
make check-migrations  # Verify database is at head
```

## CI Enforcement

A CI check (`scripts/ci/check_root_scripts.py`) prevents new Python scripts from being added to the project root. Only configuration files (`conftest.py`, `setup.py`) are allowed.

## Questions?

If you previously relied on the root-level scripts and the API doesn't support your use case, please file an issue describing the operation you need. The API should cover all business operations.
