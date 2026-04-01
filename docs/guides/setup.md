# Solstein — Complete Setup Guide

> For quick questions, see the [Troubleshooting guide](../TROUBLESHOOTING.md).

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Database Setup (Supabase)](#database-setup-supabase)
3. [API Keys & Providers](#api-keys--providers)
4. [Configuration Files](#configuration-files)
5. [Troubleshooting](#troubleshooting)
6. [Architecture Overview](#architecture-overview)

---

## Quick Start

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager (recommended)
- Redis 6+ (required for Celery task queue and cache)
- Git

### Installation

```bash
# 1. Clone the repository
git clone <repository-url>
cd solstein

# 2. Install dependencies
uv sync

# 3. Copy environment template
cp .env.example .env
# Edit .env with your API keys and database URL

# 4. Verify configuration
PYTHONPATH=src python3 -c "from solstein.config import Settings; print('Config OK')"
```

---

## Database Setup (Supabase)

### Option A: Local PostgreSQL

```bash
# Start with Docker Compose
docker-compose up -d db

# Set connection URL
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/solstein
```

### Option B: Supabase (Recommended for teams)

1. Create a project at [supabase.com](https://supabase.com)
2. Go to **Settings → Database → Connection string → URI**
3. Copy the URI and set it in `.env`:

```bash
DATABASE_URL=postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres?sslmode=require
```

### Multi-Environment Configuration

| Environment | File | Purpose |
|-------------|------|---------|
| Development | `.env.dev` | Local development |
| Testing | `.env.test` | CI/CD test runs |
| Production | `.env.prod` | Production deployment |

### Verify Database Connection

```bash
PYTHONPATH=src python3 -c "
from solstein.infrastructure.database import db_manager
print('Database config OK')
"
```

### Run Database Tests

```bash
uv run pytest tests/unit/test_fact_repository.py \
              tests/unit/test_database.py \
              tests/unit/test_database_service.py \
              -v
```

---

## API Keys & Providers

**Security**: Never commit `.env` to git. It is already in `.gitignore`.

Add keys to your `.env` file. See `.env.example` for the complete list of supported variables.

### Required Keys

| Variable | Provider | Required |
|----------|----------|----------|
| `DATABASE_URL` | PostgreSQL/Supabase | Yes |
| `SECURITY__SECRET_KEY` | JWT signing | Yes |

### AI Provider Keys (at least one required)

| Variable | Provider | Cost |
|----------|----------|------|
| `GROQ_API_KEY` | Groq | Low |
| `FIREWORKS_API_KEY` | Fireworks | Low |
| `ANTHROPIC_API_KEY` | Anthropic | Medium |
| `OPENAI_API_KEY` | OpenAI | Medium |
| `GEMINI_API_KEY` | Google Gemini | Low |
| `MISTRAL_API_KEY` | Mistral | Medium |

### Optional Data Source Keys

| Variable | Provider |
|----------|----------|
| `GITHUB_TOKEN` | GitHub enrichment |
| `COMPANIES_HOUSE_API_KEY` | UK company data |
| `PERPLEXITY_API_KEY` | Web search enrichment |

### Provider Failover Priority

```
Groq → Fireworks → Mistral → DeepInfra → Gemini → Anthropic → OpenAI
```

The system auto-fails over to the next available provider.

---

## Configuration Files

### `.env` Template

```bash
# Database (required)
DATABASE_URL=postgresql://user:password@localhost:5432/solstein
REDIS_URL=redis://localhost:6379/0

# Security (required)
SECURITY__SECRET_KEY=generate-with-python-secrets-token-urlsafe-32

# AI Providers (add your keys)
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
GEMINI_API_KEY=
GROQ_API_KEY=
FIREWORKS_API_KEY=
MISTRAL_API_KEY=

# Optional Data Sources
GITHUB_TOKEN=
COMPANIES_HOUSE_API_KEY=

# Supabase (optional, for auth)
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
```

See `.env.example` for the full variable reference with descriptions.

---

## Troubleshooting

### Import errors: `No module named 'solstein'`

```bash
# Use PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Or use uv run (handles path automatically)
uv run pytest tests/
```

### Database connection refused

- Verify `DATABASE_URL` is correct
- For Supabase, ensure `?sslmode=require` is appended
- Check your IP is allowed in Supabase: **Database → Network**

### Missing environment variable errors at startup

Run the config validation:

```bash
PYTHONPATH=src python3 -c "from solstein.config import check_configuration; check_configuration()"
```

### Redis connection failed

```bash
# Start Redis via Docker
docker-compose up -d redis

# Verify
redis-cli ping  # should return PONG
```

See [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) for a full list of common issues.

---

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│             FastAPI Application              │
│  - Auth middleware (JWT/Supabase)           │
│  - Rate limiting                            │
│  - Tenant isolation                         │
└──────────────┬──────────────────────────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼───┐  ┌──▼───┐  ┌──▼────┐
│Worker │  │Domain│  │Infra  │
│Celery │  │Models│  │Layer  │
└───────┘  └──────┘  └───────┘
```

### Key Files

| File | Purpose |
|------|---------|
| `src/solstein/config.py` | Configuration management |
| `src/solstein/api/main.py` | FastAPI application |
| `src/solstein/worker_tasks.py` | Celery task definitions |
| `src/solstein/infrastructure/database.py` | Database connection |
| `.env.example` | All supported environment variables |

---

## Related Documentation

- [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) — Common issues and fixes
- [API Documentation](../api/) — REST API reference
- [Architecture](../architecture/) — System design
- [OIDC Setup](../OIDC_SETUP.md) — Supabase Auth / OIDC configuration
