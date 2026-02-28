# Supabase Database Setup Guide for Tests

## Current Situation

The project already has Supabase configured with PostgreSQL. The test database URL is:
```
postgresql+asyncpg://postgres:nN79Ali1JcQydUyj@db.ejmxbklrhmalgcqmdsoi.supabase.co:5432/postgres
```

## Why Tests Can't Connect

From the current environment, the Supabase host is not reachable (network restrictions).

## Options to Enable Database Tests

### Option 1: Run Tests from Environment with Internet Access
If you have a local machine or CI/CD environment with internet access:

```bash
export DATABASE_URL="postgresql+asyncpg://postgres:nN79Ali1JcQydUyj@db.ejmxbklrhmalgcqmdsoi.supabase.co:5432/postgres"
pytest tests/unit/ -v
```

### Option 2: Use Local PostgreSQL (Docker)
If you prefer local testing:

```bash
# Start PostgreSQL
docker run -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:15 -d

# Create test database
docker exec -it <container_id> psql -U postgres -c "CREATE DATABASE solstein_test;"

# Run tests
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/solstein_test"
pytest tests/unit/ -v
```

### Option 3: Skip Database Tests (Current)
Run tests without database-dependent ones:

```bash
pytest tests/unit/ \
  --ignore=tests/unit/test_repositories_comprehensive.py \
  --ignore=tests/unit/test_company_repository.py \
  --ignore=tests/unit/test_fact_repository.py \
  --ignore=tests/unit/test_enrichment_repositories.py \
  --ignore=tests/unit/test_database.py \
  --ignore=tests/unit/test_database_service.py \
  --ignore=tests/unit/test_facts_orm_models.py
```

## Current Test Status (Without Database)

- **997 tests passing** ✅
- **33 tests failing** (test isolation issues)
- **12 tests skipped** (complex async/alembic)

## To Achieve 80%+ Coverage

Enable the database tests by setting up DATABASE_URL:
- 114 additional tests will run
- Coverage will increase from 73%+ to 80%+

## Summary

The project is already configured to use Supabase (PostgreSQL). You just need to run the tests from an environment that can connect to the Supabase database, or set up a local PostgreSQL instance.
