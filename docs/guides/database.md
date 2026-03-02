# 📚 Database Setup & Configuration Guide

**Managing Data, Migrations, and Seed Data in Solstein**

---

## Overview

Solstein uses a **dual-database architecture**:

| Layer | Technology | Purpose | When to Use |
|-------|-----------|---------|------------|
| **Data Store** | PostgreSQL via Supabase | Production data, scores, financials | Cloud deployments, shared data |
| **Local Dev** | PostgreSQL (local) | Development and testing | Offline development, fast iteration |
| **Cache** | Redis | Temporary results, task queue | Celery task broker, response caching |

This guide covers both cloud (Supabase) and local PostgreSQL setups.

---

## Prerequisites

- Python 3.10+ (from main setup)
- `psycopg2-binary` (included in `requirements.txt`)
- PostgreSQL 14+ **or** Supabase account
- Redis 5.0+ (for Celery tasks)

---

## Architecture

```
┌─────────────┐
│  FastAPI    │
│  API Layer  │
└──────┬──────┘
       │ (SQL queries, Pydantic models)
       │
┌──────▼──────────────────┐
│  Repository Pattern      │
│ (CompanyRepository)      │
└──────┬──────────────────┘
       │ (swappable implementations)
       │
   ┌───┴────┬─────────────┐
   │        │             │
┌──▼─┐  ┌──▼──┐  ┌─────▼──┐
│JSON│  │ SQL │  │ Supabase│
│File│  │Local│  │  Cloud  │
└────┘  └─────┘  └────────┘
```

> **Key Insight:** The `CompanyRepository` abstract interface allows swapping implementations without changing API code.

---

## Part 1: Local PostgreSQL Setup (Development)

### Option A: Using Docker

**Fastest option** — no local PostgreSQL installation needed.

```bash
# Start PostgreSQL in Docker
docker run --name solstein-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=solstein \
  -p 5432:5432 \
  -v solstein-postgres-data:/var/lib/postgresql/data \
  postgres:15-alpine

# In another terminal, verify connection
psql -h localhost -U postgres -d solstein -c "SELECT 1;"
```

### Option B: Using Homebrew (macOS)

```bash
# Install PostgreSQL
brew install postgresql@15

# Start the service
brew services start postgresql@15

# Create database
createdb solstein

# Create tables (see schema section below)
psql -d solstein -f supabase/migrations/001_companies.sql
psql -d solstein -f supabase/migrations/002_relationalize_financials.sql
```

### Option C: Native PostgreSQL (Linux)

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Start service
sudo systemctl start postgresql

# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE solstein;
CREATE USER solstein_user WITH PASSWORD 'solstein_password';
ALTER ROLE solstein_user SET client_encoding TO 'utf8';
ALTER ROLE solstein_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE solstein_user SET default_transaction_deferrable TO ON;
ALTER ROLE solstein_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE solstein TO solstein_user;
EOF
```

### Configuration for Local Dev

Add to `.env`:

```env
# PostgreSQL Connection
SOLSTEIN_DATABASE__URL=postgresql://postgres:postgres@localhost:5432/solstein
SOLSTEIN_DATABASE__POOL_SIZE=10
SOLSTEIN_DATABASE__ECHO=false  # Set to true for SQL query logging

# (Or if using Homebrew/native on macOS)
SOLSTEIN_DATABASE__URL=postgresql://solstein_user:solstein_password@localhost:5432/solstein
```

### Verify Connection

```bash
# From Python
python -c "from solstein.config import get_settings; print(get_settings().database.url)"

# From psql command line
psql -h localhost -U postgres -d solstein -c "SELECT 1;"
```

---

## Part 2: Database Schema

### Schema Overview

Solstein stores two main entities:

```sql
-- companies — Profile data (market, financials, scores)
CREATE TABLE companies (
  id VARCHAR PRIMARY KEY,           -- e.g., "acme-energy-bv"
  name VARCHAR NOT NULL,             -- "Acme Energy BV"
  industry VARCHAR,                  -- "Energy Software"
  market VARCHAR,                    -- "European Energy SaaS"
  tier VARCHAR,                      -- "Tier 1", "Tier 2", etc.
  
  -- Scoring dimensions
  growth_score DECIMAL,              -- 0–10
  financial_health_score DECIMAL,    -- 0–10
  competitive_position_score DECIMAL, -- 0–10
  
  -- Classification
  classification VARCHAR,            -- "Phoenix", "Salt", "Lead"
  
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- financial_metrics — Time-series financial data
CREATE TABLE financial_metrics (
  id SERIAL PRIMARY KEY,
  company_id VARCHAR REFERENCES companies(id),
  year INT,
  
  revenue DECIMAL,                 -- in millions
  growth_rate DECIMAL,             -- percentage
  profit_margin DECIMAL,           -- percentage
  employee_count INT,
  
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Create Schema

**Option 1: From Migration Files**

```bash
# Run migrations in order
psql -d solstein -f supabase/migrations/001_companies.sql
psql -d solstein -f supabase/migrations/002_relationalize_financials.sql
```

**Option 2: Manually**

```bash
# Copy the SQL from files:
cat supabase/migrations/001_companies.sql | psql -d solstein
cat supabase/migrations/002_relationalize_financials.sql | psql -d solstein
```

### Verify Schema

```bash
# Connect and inspect
psql -d solstein << EOF
\dt                          -- List tables
\d companies                 -- Describe companies table
\d financial_metrics         -- Describe financial_metrics table
SELECT COUNT(*) FROM companies;  -- Count records
EOF
```

---

## Part 3: Supabase Cloud Setup (Production)

### Creating a Supabase Project

1. **Go to** [supabase.com/dashboard](https://supabase.com/dashboard)
2. **Sign up** if needed (free tier available)
3. **Create new project**:
   - Organization: your workspace
   - Project name: `solstein` or `solstein-production`
   - Database password: strong password (20+ chars)
   - Region: closest to your users
   - Click "Create project" (takes 2–3 minutes)

### Supabase Connection String

After project creation:

1. **Navigate to** Settings → Database
2. **Copy** the connection string (or build it manually)
3. **Add to `.env`**:

```env
# Supabase Connection (Production)
SOLSTEIN_DATABASE__URL=postgresql://postgres:YOUR_PASSWORD@db.PROJECT_ID.supabase.co:5432/postgres
SOLSTEIN_SUPABASE__URL=https://PROJECT_ID.supabase.co
SOLSTEIN_SUPABASE__KEY=YOUR_ANON_KEY
SOLSTEIN_SUPABASE__ANON_KEY=YOUR_ANON_KEY
```

> **Security:** Store these in a secure secrets manager (AWS Secrets Manager, Vault, etc.), not in `.env` committed to Git.

### Initialize Supabase Schema

```bash
# Using psql to remote database
PGPASSWORD=YOUR_PASSWORD psql -h db.PROJECT_ID.supabase.co \
  -U postgres -d postgres \
  -f supabase/migrations/001_companies.sql

PGPASSWORD=YOUR_PASSWORD psql -h db.PROJECT_ID.supabase.co \
  -U postgres -d postgres \
  -f supabase/migrations/002_relationalize_financials.sql
```

### Verify Supabase Connection

```python
# From Python
import os
from sqlalchemy import create_engine, text

db_url = os.getenv("SOLSTEIN_DATABASE__URL")
engine = create_engine(db_url)

with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM companies"))
    print(f"Companies in Supabase: {result.scalar()}")
```

---

## Part 4: Seed Data

### Loading Test Data

Solstein includes a seeding script to load test companies and financials:

```bash
# From project root
python -m solstein.data.seed_db
```

This script:
1. Loads companies from `data/input/companies.json` (or configured source)
2. Calculates scores using `GrowthScorer`
3. Inserts into the active database (local or Supabase based on `.env`)

### Seed Data Location

```
data/
├── input/
│   ├── companies.json          ← Company profiles
│   ├── financials.json         ← Time-series financial data
│   └── markets/
│       ├── european-energy.json
│       └── saas-infrastructure.json
└── output/
    └── exports/                ← Generated Excel reports
```

### Custom Seed Data

To seed custom data:

**1. Create JSON file** (e.g., `data/input/custom-market.json`):

```json
[
  {
    "id": "company-1",
    "name": "My Company",
    "industry": "Software",
    "market": "European SaaS",
    "tier": "Tier 1",
    "ai_maturity": "Strong",
    "saas_maturity": 8,
    "financials": {
      "revenue": 50.0,
      "growth_rate": 25.0,
      "profit_margin": 12.5,
      "employee_count": 45
    }
  }
]
```

**2. Load via API**:

```bash
curl -X POST http://localhost:8000/companies \
  -H "Content-Type: application/json" \
  -d @data/input/custom-market.json
```

**Or via Python:**

```python
from solstein.data.loaders import CompetitorDataLoader
from solstein.data.repositories import SupabaseRepository

loader = CompetitorDataLoader()
companies = loader.load_from_file("data/input/custom-market.json")

repo = SupabaseRepository()
for company in companies:
    repo.save(company)
```

---

## Part 5: Configuration Reference

### Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `SOLSTEIN_DATABASE__URL` | `postgresql://postgres:postgres@localhost:5432/solstein` | PostgreSQL connection string |
| `SOLSTEIN_DATABASE__POOL_SIZE` | `20` | SQLAlchemy connection pool size (1–100) |
| `SOLSTEIN_DATABASE__ECHO` | `false` | Log all SQL queries (development only) |
| `SOLSTEIN_REDIS__URL` | `redis://localhost:6379/0` | Redis connection for Celery |
| `SOLSTEIN_SUPABASE__URL` | `` | Supabase project URL |
| `SOLSTEIN_SUPABASE__KEY` | `` | Supabase API key |

### Connection String Formats

**Local PostgreSQL:**
```
postgresql://user:password@localhost:5432/solstein
postgresql://postgres:postgres@localhost:5432/solstein
```

**Supabase:**
```
postgresql://postgres:password@db.projectid.supabase.co:5432/postgres
```

**Docker (from compose):**
```
postgresql://solstein:solstein@postgres:5432/solstein
```

---

## Part 6: Migration & Backup

### Exporting Data

**Backup entire database:**

```bash
# From local PostgreSQL
pg_dump -h localhost -U postgres -d solstein > solstein_backup.sql

# From Supabase
pg_dump -h db.PROJECT_ID.supabase.co -U postgres -d postgres > solstein_backup.sql
```

**Export specific table:**

```bash
pg_dump -h localhost -U postgres -d solstein -t companies > companies_backup.sql
```

### Restoring Data

```bash
# Restore entire backup
psql -h localhost -U postgres -d solstein < solstein_backup.sql

# Restore specific table
psql -h localhost -U postgres -d solstein < companies_backup.sql
```

### Data Synchronization

**Pull from production to local dev:**

```bash
# 1. Backup production
pg_dump -h db.PROJECT_ID.supabase.co -U postgres -d postgres > prod_backup.sql

# 2. Drop local database
dropdb solstein

# 3. Create fresh database
createdb solstein

# 4. Restore production data
psql -h localhost -U postgres -d solstein < prod_backup.sql
```

---

## Part 7: Troubleshooting

### "Connection refused"

**Symptoms:** `psycopg2.OperationalError: could not connect to server`

**Diagnosis:**
```bash
# Check if PostgreSQL is running
psql -h localhost -U postgres -c "SELECT 1;" 2>&1

# Check listening port
netstat -tuln | grep 5432

# Check .env DATABASE__URL
echo $SOLSTEIN_DATABASE__URL
```

**Solutions:**
- Ensure PostgreSQL is running: `brew services start postgresql@15`
- Verify password is correct
- Check firewall rules if remote database
- Verify database exists: `psql -U postgres -l`

### "Database does not exist"

**Solution:**
```bash
# Create database
createdb -h localhost -U postgres solstein

# Or via psql
psql -h localhost -U postgres -c "CREATE DATABASE solstein;"
```

### "Tables not found"

**Symptoms:** `psycopg2.ProgrammingError: relation "companies" does not exist`

**Solution:** Run migrations:
```bash
psql -d solstein -f supabase/migrations/001_companies.sql
psql -d solstein -f supabase/migrations/002_relationalize_financials.sql
```

### Slow Queries

**Enable query logging:**
```env
SOLSTEIN_DATABASE__ECHO=true
```

Then run your operation and check stdout for slow SQL.

**Typical slowness:**
- Missing indexes on `company_id`, `market`, `industry`
- N+1 query patterns in Python code
- Connection pool exhaustion (increase `POOL_SIZE`)

---

## Part 8: Data Layer Architecture

### Repository Pattern

All data access goes through `CompanyRepository` interface:

```python
# src/solstein/core/repositories.py

class CompanyRepository(ABC):
    """Abstract interface — implementation can swap."""
    
    @abstractmethod
    def find_by_id(self, company_id: str) -> Company | None:
        """Retrieve single company."""
        pass
    
    @abstractmethod
    def find_all(self, filters: CompanyFilter) -> list[Company]:
        """Retrieve multiple companies with filtering."""
        pass
    
    @abstractmethod
    def save(self, company: Company) -> str:
        """Insert or update company."""
        pass

# Implementations
# - JsonFileRepository — reads from data/input/ JSON files
# - SupabaseRepository — reads from Supabase PostgreSQL
# - PostgresRepository — reads from local PostgreSQL (future)
```

### Dependency Injection

In API routes, repository is injected:

```python
@router.get("/companies")
def list_companies(repo: CompanyRepository = Depends(get_repository)):
    """FastAPI automatically provides the right repository."""
    return repo.find_all(CompanyFilter())
```

### Swapping Implementations

To switch from Supabase to local PostgreSQL:

```python
# In src/solstein/api/dependencies.py

def get_repository() -> CompanyRepository:
    # Currently uses Supabase
    return SupabaseRepository()
    
    # To use local PostgreSQL, change to:
    # return PostgresRepository()
```

No other code needs to change — the interface stays the same.

---

## Part 9: Health Checks

### Database Health Check

```bash
# From command line
psql -h localhost -U postgres -d solstein -c "SELECT NOW();"

# From Python
from solstein.config import get_settings
from sqlalchemy import create_engine, text

settings = get_settings()
engine = create_engine(settings.database.url)

with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM companies"))
    print(f"✓ Database healthy. Companies: {result.scalar()}")
```

### API Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2026-02-20T10:00:00Z"
}
```

> **Note:** This checks API availability only, not database connectivity. To verify full health including database, write a custom endpoint.

---

## Recommended Reading

- [Architecture Decisions → ADR-004 (JSON vs. PostgreSQL)](../architecture/decisions.md)
- [Developer Guide → Running Locally](developer.md)
- [Operator Guide → Environment Variables](operator.md)

---

*Last Updated: February 20, 2026*
*Maintainer: Data Engineering Team*

