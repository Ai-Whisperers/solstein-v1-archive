# Solstein - Database Documentation

This document describes the Solstein database schema and how to work with it.

## Database Overview

- **Type**: PostgreSQL (Supabase managed)
- **ORM**: SQLAlchemy 2.0 with async support
- **Driver**: asyncpg
- **Connection Pooling**: Configured in conftest.py

## Connection Configuration

### Environment Variables

```bash
# Required
DATABASE_URL=postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres?sslmode=require

# Optional (for specific environments)
DATABASE_URL_TEST=postgresql://... # Test database
DATABASE_URL_DEV=postgresql://...  # Development database  
DATABASE_URL_PROD=postgresql://... # Production database
```

### Connection Pool Settings

Configured in `tests/conftest.py`:

```python
engine = create_async_engine(
    async_url,
    pool_size=5,           # Max connections in pool
    max_overflow=10,       # Additional connections if needed
    pool_recycle=3600,     # Recycle connections after 1 hour
    pool_pre_ping=True,    # Test connections before use
)
```

## Schema Overview

### Core Tables

#### companies
Company information table.

```sql
CREATE TABLE companies (
    company_id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    industry VARCHAR,
    country VARCHAR,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### gathering_batches
Tracks data gathering operations for companies.

```sql
CREATE TABLE gathering_batches (
    batch_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id VARCHAR REFERENCES companies(company_id),
    status VARCHAR DEFAULT 'in_progress',
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);
```

#### facts
Stores extracted facts about companies.

```sql
CREATE TABLE facts (
    fact_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id VARCHAR REFERENCES companies(company_id),
    batch_id UUID REFERENCES gathering_batches(batch_id),
    fact_type VARCHAR NOT NULL,
    value NUMERIC,
    value_str VARCHAR,
    confidence NUMERIC CHECK (confidence BETWEEN 0 AND 1),
    source VARCHAR,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### fact_sources
Links facts to their original sources.

```sql
CREATE TABLE fact_sources (
    source_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fact_id UUID REFERENCES facts(fact_id) ON DELETE CASCADE,
    source_type VARCHAR,
    url VARCHAR,
    title VARCHAR,
    retrieved_at TIMESTAMP DEFAULT NOW()
);
```

### Analysis Tables

#### company_scoring_records
Stores AI-generated company scores.

```sql
CREATE TABLE company_scoring_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id VARCHAR REFERENCES companies(company_id),
    company_name VARCHAR,
    growth_score NUMERIC,
    financial_health_score NUMERIC,
    competitive_position_score NUMERIC,
    overall_score NUMERIC,
    classification VARCHAR,
    scoring_timestamp TIMESTAMP DEFAULT NOW(),
    scorer_version VARCHAR
);
```

#### signal_records
Stores extracted signals about companies.

```sql
CREATE TABLE signal_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id VARCHAR REFERENCES companies(company_id),
    signal_type VARCHAR,
    signal_value NUMERIC,
    confidence NUMERIC,
    scoring_id UUID REFERENCES company_scoring_records(id),
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### market_snapshots
Stores market segment analysis.

```sql
CREATE TABLE market_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    market_segment VARCHAR NOT NULL,
    snapshot_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### company_analysis_audit_trail
Audit trail for company analysis.

```sql
CREATE TABLE company_analysis_audit_trail (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id VARCHAR REFERENCES companies(company_id),
    company_name VARCHAR,
    scoring_timestamp TIMESTAMP,
    scorer_version VARCHAR,
    data_sources_used JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Enrichment Tables

#### enrichment_audit_records
Audit trail for data enrichment operations.

```sql
CREATE TABLE enrichment_audit_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id VARCHAR REFERENCES companies(company_id),
    operation_type VARCHAR,
    status VARCHAR,
    details JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### enrichment_cache
Caches enrichment data to avoid re-fetching.

```sql
CREATE TABLE enrichment_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id VARCHAR REFERENCES companies(company_id),
    cache_data JSONB,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Entity Relationship Diagram

```
companies
    │
    ├── gathering_batches (1:N)
    │       │
    │       └── facts (1:N)
    │               │
    │               └── fact_sources (1:N)
    │
    ├── company_scoring_records (1:N)
    │       │
    │       └── signal_records (1:N)
    │
    ├── company_analysis_audit_trail (1:N)
    │
    ├── enrichment_audit_records (1:N)
    │
    └── enrichment_cache (1:1)

market_snapshots (independent)
```

## ORM Models

### Domain Models (src/solstein/domain/facts.py)

```python
class GatheringBatch:
    batch_id: UUID
    company_id: str
    status: str  # 'in_progress', 'completed', 'failed'
    created_at: datetime

class Fact:
    fact_id: UUID
    company_id: str
    batch_id: UUID
    fact_type: str
    value: Optional[float]
    value_str: Optional[str]
    confidence: float  # 0.0 to 1.0
    source: Optional[str]
    created_at: datetime

class FactSource:
    source_id: UUID
    fact_id: UUID
    source_type: str
    url: Optional[str]
    title: Optional[str]
    retrieved_at: datetime
```

### Database Models (src/solstein/infrastructure/database_models.py)

SQLAlchemy ORM models for database tables.

## Foreign Key Constraints

1. **gathering_batches.company_id** → companies.company_id
2. **facts.company_id** → companies.company_id
3. **facts.batch_id** → gathering_batches.batch_id
4. **fact_sources.fact_id** → facts.fact_id (CASCADE delete)
5. **company_scoring_records.company_id** → companies.company_id
6. **signal_records.company_id** → companies.company_id
7. **signal_records.scoring_id** → company_scoring_records.id
8. **company_analysis_audit_trail.company_id** → companies.company_id
9. **enrichment_audit_records.company_id** → companies.company_id
10. **enrichment_cache.company_id** → companies.company_id

## Indexes

Recommended indexes for performance:

```sql
-- Fact lookups by company
CREATE INDEX idx_facts_company_id ON facts(company_id);
CREATE INDEX idx_facts_company_type ON facts(company_id, fact_type);

-- Batch lookups
CREATE INDEX idx_batches_company_id ON gathering_batches(company_id);
CREATE INDEX idx_batches_status ON gathering_batches(status);

-- Scoring lookups
CREATE INDEX idx_scoring_company_id ON company_scoring_records(company_id);
CREATE INDEX idx_scoring_timestamp ON company_scoring_records(scoring_timestamp);

-- Audit trail lookups
CREATE INDEX idx_audit_company_id ON company_analysis_audit_trail(company_id);
```

## Common Queries

### Get all facts for a company

```python
result = await session.execute(
    select(Fact).where(Fact.company_id == "comp-123")
)
facts = result.scalars().all()
```

### Get facts by type

```python
result = await session.execute(
    select(Fact).where(
        Fact.company_id == "comp-123",
        Fact.fact_type == "revenue"
    )
)
revenue_facts = result.scalars().all()
```

### Get latest scoring for company

```python
result = await session.execute(
    select(CompanyScoringRecord)
    .where(CompanyScoringRecord.company_id == "comp-123")
    .order_by(CompanyScoringRecord.scoring_timestamp.desc())
    .limit(1)
)
latest_score = result.scalar_one_or_none()
```

### Get batches with facts count

```python
from sqlalchemy import func

result = await session.execute(
    select(
        GatheringBatch,
        func.count(Fact.fact_id).label("fact_count")
    )
    .outerjoin(Fact, Fact.batch_id == GatheringBatch.batch_id)
    .group_by(GatheringBatch.batch_id)
)
batches = result.all()  # List of (batch, fact_count) tuples
```

## Testing with Database

See [TESTING.md](TESTING.md) for detailed testing documentation.

### Test Data Cleanup

```python
from solstein.infrastructure.test_cleanup import cleanup_test_database

async def test_something(db_session):
    # Test code here
    
    # Cleanup after test
    await cleanup_test_database(db_session)
```

### Creating Test Data

```python
from tests.factories import create_test_batch, create_test_fact

batch = await create_test_batch(db_session, "comp-123")
fact = await create_test_fact(
    db_session,
    batch_id=str(batch.batch_id),
    company_id="comp-123",
    fact_type="revenue",
    value=5000000.0
)
```

## Migration Notes

When changing the schema:

1. Update ORM models in `src/solstein/infrastructure/database_models.py`
2. Create migration script (if using Alembic)
3. Update factories if needed
4. Update tests to match new schema
5. Run tests to verify changes

## Backup and Restore

### Supabase Backup

Supabase provides automatic daily backups. For manual backup:

1. Go to Supabase Dashboard → Database → Backups
2. Click "Create backup"

### Export Data

```bash
pg_dump "postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres" \
  --schema-only > schema.sql

pg_dump "postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres" \
  --data-only > data.sql
```

### Import Data

```bash
psql "postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres" \
  < schema.sql

psql "postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres" \
  < data.sql
```

## Security

### Row Level Security (RLS)

Enable RLS on tables for production:

```sql
-- Enable RLS
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;

-- Create policy
CREATE POLICY "Enable read access for all users" ON companies
    FOR SELECT USING (true);
```

### Connection Security

- Always use SSL (`sslmode=require`)
- Store credentials in environment variables
- Never commit `.env` files to git
- Rotate credentials periodically

## Performance Optimization

### Query Optimization

1. Use indexes for frequently queried columns
2. Use `selectinload()` for relationships to avoid N+1 queries
3. Batch inserts when possible
4. Use connection pooling

### Connection Pool Tuning

For high-traffic scenarios:

```python
engine = create_async_engine(
    url,
    pool_size=20,        # Increase for more concurrent connections
    max_overflow=30,     # More overflow connections
    pool_timeout=30,     # Wait longer for connection
    pool_recycle=1800,   # Recycle every 30 minutes
)
```

## Troubleshooting

### Connection Issues

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common connection problems.

### Query Performance

1. Check query plan: `EXPLAIN ANALYZE`
2. Add indexes for slow queries
3. Consider partitioning for large tables
4. Monitor connection pool usage

## Related Documentation

- [SETUP.md](SETUP.md) - Project setup guide
- [TESTING.md](TESTING.md) - Testing guide
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Troubleshooting guide
