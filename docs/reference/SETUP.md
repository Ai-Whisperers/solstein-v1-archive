> **Moved**: This guide has been consolidated into [`docs/guides/setup.md`](../guides/setup.md).
> Please update your bookmarks. This file is kept for backward compatibility.

# Solstein - Supabase Database Setup Guide

This guide walks you through setting up the Solstein project with Supabase PostgreSQL for testing.

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager
- Git
- Supabase account (free tier works)

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd solstein
```

### 2. Install Dependencies

```bash
uv sync
```

This will install all dependencies including:
- SQLAlchemy (async support)
- asyncpg (async PostgreSQL driver)
- pytest-asyncio (async test support)
- All other project dependencies

### 3. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.test .env
```

Or create `.env` with your Supabase database URL:

```bash
# .env
DATABASE_URL=postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres?sslmode=require
```

### 4. Verify Database Connection

Test that you can connect to Supabase:

```bash
export DATABASE_URL="your-supabase-url"
python3 -c "
from src.solstein.database_config import get_database_url, validate_database_url
url = get_database_url()
print(f'✅ Database URL loaded: {url[:50]}...')
print(f'✅ URL is valid: {validate_database_url(url)}')
"
```

### 5. Run Database Tests

Run the database test suite against real Supabase:

```bash
export DATABASE_URL="your-supabase-url"
uv run pytest tests/unit/test_fact_repository.py -v
```

Or run all database tests:

```bash
uv run pytest tests/unit/test_fact_repository.py \
              tests/unit/test_database.py \
              tests/unit/test_database_service.py \
              tests/unit/test_enrichment_repositories.py \
              -v
```

## Multi-Environment Configuration

The project supports three environments:

### Test Environment (`.env.test`)
Used for running tests locally or in CI/CD:
```bash
DATABASE_URL=postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres?sslmode=require
```

### Development Environment (`.env.dev`)
Used for local development:
```bash
DATABASE_URL=postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres?sslmode=require
```

### Production Environment (`.env.prod`)
**WARNING**: Only use for production deployment:
```bash
DATABASE_URL=postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres?sslmode=require
```

## Supabase Setup

### 1. Create a Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Sign up or log in
3. Create a new project
4. Note your project URL and database password

### 2. Get Your Database URL

From your Supabase dashboard:
1. Go to Settings → Database
2. Under "Connection string", select "URI"
3. Copy the connection string
4. Replace `[YOUR-PASSWORD]` with your actual database password

Example:
```
postgresql://postgres:nN79Ali1JcQydUyj@db.lpvimmncdcepgygcrsbd.supabase.co:5432/postgres?sslmode=require
```

### 3. Configure Row Level Security (Optional)

If using this in production, configure RLS policies:
1. Go to Database → Tables
2. Select your tables
3. Enable RLS and add policies

## GitHub Actions CI/CD Setup

### 1. Add Repository Secrets

Go to your GitHub repository:
1. Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add `DATABASE_URL_TEST` with your Supabase test database URL

**IMPORTANT**: Never commit database credentials to git!

### 2. Verify Workflow

Push a commit to trigger the workflow:
```bash
git commit --allow-empty -m "test: trigger CI"
git push origin main
```

Check the Actions tab in your GitHub repository for the workflow run.

## Troubleshooting

### Connection Issues

**Problem**: Can't connect to database
```
Connection refused / timeout
```

**Solution**:
- Verify your database URL is correct
- Check that SSL mode is set to `require`
- Ensure your IP is allowed in Supabase (Database → Network)

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'src'`

**Solution**:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

Or use `uv run` which handles the path automatically:
```bash
uv run pytest tests/unit/test_fact_repository.py
```

### Async Test Errors

**Problem**: `RuntimeError: Event loop is closed`

**Solution**: Ensure pytest-asyncio is installed and configured:
```bash
uv add pytest-asyncio
```

The `pytest.ini` already has `asyncio_mode = auto` configured.

## Environment Variable Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | Main database connection URL | Yes | - |
| `DATABASE_URL_TEST` | Test database URL | For tests | `DATABASE_URL` |
| `DATABASE_URL_DEV` | Development database URL | Optional | `DATABASE_URL` |
| `DATABASE_URL_PROD` | Production database URL | Optional | `DATABASE_URL` |
| `GITHUB_TOKEN` | GitHub API token | For enrichment | - |

## Next Steps

- Read [TESTING.md](TESTING.md) for test writing guidelines
- Read [DATABASE.md](DATABASE.md) for database schema documentation
- Read [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues

## Support

For issues or questions:
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Review the evidence files in `.sisyphus/evidence/`
3. Check the plan in `.sisyphus/plans/supabase-professional-setup.md`
