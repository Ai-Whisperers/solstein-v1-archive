# Epic: Database Optimization & Migration Strategy (EPIC-025)

## Overview
Optimize database performance through query optimization, strategic indexing, connection pooling, and migration tooling. Ensure the database layer can scale with the application's growth while maintaining data integrity.

## Background
Current database concerns:
- 18 tables with unknown query performance
- No formal migration strategy documentation
- Connection pooling not optimized
- Missing indexes on frequently queried columns
- No query performance monitoring
- Database schema changes manual and error-prone

## Goals
- [ ] All queries execute in <50ms (p95)
- [ ] Zero N+1 query patterns
- [ ] Proper indexing on all foreign keys and search fields
- [ ] Connection pool optimized for load
- [ ] Automated migration testing
- [ ] Database monitoring and alerting

## Success Metrics
| Metric | Current | Target |
|--------|---------|--------|
| Query Time (p95) | Unknown | <50ms |
| Slow Queries | Unknown | 0 |
| Connection Pool Usage | Unknown | <80% |
| Migration Time | Unknown | <5 min |
| Index Coverage | Unknown | 100% |

---

## Stories

### Story 1: Database Query Audit & Analysis
**Points:** 5
**Priority:** P0

Comprehensive audit of all database queries.

**Tasks:**
- [ ] Enable SQL query logging
- [ ] Run representative workload
- [ ] Identify slow queries (>100ms)
- [ ] Detect N+1 query patterns
- [ ] Document query patterns by endpoint
- [ ] Create query performance baseline

**Tools:**
- PostgreSQL `log_min_duration_statement = 100`
- `pg_stat_statements` extension
- Custom query logger middleware

**Deliverable:**
```markdown
# Query Performance Report

## Slow Queries (>100ms)
1. `SELECT * FROM companies WHERE ...` - 450ms avg
2. `UPDATE scoring_records ...` - 320ms avg

## N+1 Patterns Found
- `/api/companies` - Loads metrics separately
- Research pipeline - Iterative updates

## Recommendations
- Add index on companies.industry
- Batch update scoring_records
```

---

### Story 2: Strategic Index Implementation
**Points:** 8
**Priority:** P0

Add indexes based on query analysis.

**Index Categories:**

**Primary Indexes (Must Have):**
```sql
-- Foreign key indexes
CREATE INDEX idx_company_record_tenant_id ON company_records(tenant_id);
CREATE INDEX idx_scoring_record_company_id ON scoring_records(company_id);
CREATE INDEX idx_signal_record_scoring_id ON signal_records(scoring_id);

-- Search indexes
CREATE INDEX idx_company_record_name ON company_records(name);
CREATE INDEX idx_company_record_industry ON company_records(industry);
CREATE INDEX idx_company_record_classification ON company_records(classification);

-- Date range queries
CREATE INDEX idx_scoring_record_created_at ON scoring_records(created_at);
CREATE INDEX idx_research_run_created_at ON research_runs(created_at);
```

**Composite Indexes:**
```sql
-- Common filter combinations
CREATE INDEX idx_company_tenant_industry ON company_records(tenant_id, industry);
CREATE INDEX idx_company_tenant_classification ON company_records(tenant_id, classification);

-- Sorting + filtering
CREATE INDEX idx_scoring_company_created ON scoring_records(company_id, created_at DESC);
```

**Full-Text Search:**
```sql
-- For company name/description search
CREATE INDEX idx_company_search ON company_records 
USING gin(to_tsvector('english', name || ' ' || COALESCE(description, '')));
```

**Tasks:**
- [ ] Create migration for all indexes
- [ ] Measure query improvement
- [ ] Document index usage
- [ ] Add index maintenance job

**Acceptance Criteria:**
- [ ] All foreign keys indexed
- [ ] All WHERE clause columns indexed
- [ ] All ORDER BY columns indexed
- [ ] Query time reduced by 50%

---

### Story 3: N+1 Query Elimination
**Points:** 8
**Priority:** P0

Eliminate all N+1 query patterns.

**Common N+1 Patterns:**

**Pattern 1: Loading Related Data**
```python
# BEFORE (N+1)
companies = await db.fetch_all("SELECT * FROM companies")
for company in companies:
    metrics = await db.fetch_one(
        "SELECT * FROM metrics WHERE company_id = $1", 
        company.id
    )  # N queries

# AFTER (Single query)
companies_with_metrics = await db.fetch_all("""
    SELECT c.*, m.* 
    FROM companies c
    LEFT JOIN metrics m ON c.id = m.company_id
""")  # 1 query
```

**Pattern 2: Research Pipeline**
```python
# BEFORE
for company in companies:
    await enrich_company(company)  # Each does DB lookup

# AFTER
company_ids = [c.id for c in companies]
all_data = await db.fetch_all(
    "SELECT * FROM enrichment_data WHERE company_id = ANY($1)",
    company_ids
)
```

**Implementation:**
- [ ] Audit all repository methods
- [ ] Add `select_related` style joins
- [ ] Implement batch loading
- [ ] Add eager loading options

**Repository Pattern:**
```python
class CompanyRepository:
    async def get_with_relations(
        self, 
        company_id: str,
        include_metrics: bool = False,
        include_scores: bool = False
    ) -> Company:
        query = "SELECT c.* FROM companies c WHERE c.id = $1"
        
        if include_metrics:
            query = """
                SELECT c.*, m.* 
                FROM companies c
                LEFT JOIN metrics m ON c.id = m.company_id
                WHERE c.id = $1
            """
        # ...
```

---

### Story 4: Connection Pool Optimization
**Points:** 5
**Priority:** P0

Optimize database connection pooling.

**Current Configuration:**
```python
# Likely default settings - need optimization
engine = create_async_engine(
    DATABASE_URL,
    pool_size=5,           # Too small?
    max_overflow=10,       # Adjust based on load
    pool_timeout=30,
    pool_recycle=3600,
)
```

**Optimized Configuration:**
```python
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,          # Base connections
    max_overflow=30,       # Burst capacity
    pool_timeout=10,       # Fail fast
    pool_recycle=1800,     # Recycle every 30min
    pool_pre_ping=True,    # Verify connections
    echo=False,            # Disable in production
)
```

**Tasks:**
- [ ] Load test to determine optimal pool size
- [ ] Configure pool monitoring
- [ ] Set up pool exhaustion alerts
- [ ] Document pool sizing guide

**Monitoring:**
```python
# Pool metrics
pool_size = engine.pool.size()
checked_in = engine.pool.checkedin()
checked_out = engine.pool.checkedout()
overflow = engine.pool.overflow()
```

---

### Story 5: Migration Strategy & Tooling
**Points:** 5
**Priority:** P1

Improve database migration process.

**Current:** Alembic (basic usage)

**Enhancements:**

**1. Migration Testing:**
```python
# tests/integration/test_migrations.py
async def test_migration_rollback():
    """Test that migrations can be rolled back."""
    # Apply migration
    await alembic.upgrade('head')
    
    # Verify schema
    assert await table_exists('new_table')
    
    # Rollback
    await alembic.downgrade('-1')
    
    # Verify rollback
    assert not await table_exists('new_table')
```

**2. Migration Checklist:**
```markdown
## Pre-Migration Checklist
- [ ] Backup database
- [ ] Test migration on staging
- [ ] Estimate downtime
- [ ] Prepare rollback plan
- [ ] Notify stakeholders

## Post-Migration Checklist
- [ ] Verify schema changes
- [ ] Run smoke tests
- [ ] Monitor error rates
- [ ] Verify performance
```

**3. Zero-Downtime Migrations:**
```python
# Pattern: Add column -> Backfill -> Make required

# Migration 1: Add nullable column
op.add_column('companies', sa.Column('new_field', sa.String(), nullable=True))

# Migration 2: Backfill data (run separately)
# UPDATE companies SET new_field = 'default' WHERE new_field IS NULL

# Migration 3: Make required
op.alter_column('companies', 'new_field', nullable=False)
```

**4. Migration Documentation:**
- Migration naming convention
- Rollback procedures
- Data migration scripts
- Environment-specific notes

---

### Story 6: Database Monitoring & Alerting
**Points:** 5
**Priority:** P1

Implement comprehensive database monitoring.

**Metrics to Track:**
```python
DATABASE_METRICS = {
    # Performance
    'query_duration': Histogram('db_query_duration_seconds'),
    'queries_per_second': Gauge('db_queries_per_second'),
    'slow_queries': Counter('db_slow_queries_total'),
    
    # Connection Pool
    'pool_size': Gauge('db_pool_size'),
    'pool_in_use': Gauge('db_pool_connections_in_use'),
    'pool_available': Gauge('db_pool_connections_available'),
    
    # Errors
    'connection_errors': Counter('db_connection_errors_total'),
    'query_errors': Counter('db_query_errors_total'),
}
```

**Alerting Rules:**
```yaml
# Alert when query time >100ms
- alert: SlowDatabaseQuery
  expr: histogram_quantile(0.95, db_query_duration_seconds) > 0.1
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Slow database queries detected"

# Alert when pool near exhaustion
- alert: DatabasePoolNearExhaustion
  expr: db_pool_connections_in_use / db_pool_size > 0.8
  for: 2m
  labels:
    severity: critical
```

**Dashboard:**
- Query performance over time
- Slow query log
- Connection pool status
- Lock wait events
- Cache hit ratio

---

### Story 7: Query Optimization Techniques
**Points:** 5
**Priority:** P1

Implement advanced query optimization patterns.

**Techniques:**

**1. Select Only Required Columns:**
```python
# BAD
SELECT * FROM companies WHERE id = $1

# GOOD
SELECT id, name, industry FROM companies WHERE id = $1
```

**2. Use EXISTS for Semi-Joins:**
```python
# BAD - Loads all records
SELECT * FROM companies c
WHERE c.id IN (SELECT company_id FROM scoring WHERE score > 8)

# GOOD - Stops at first match
SELECT * FROM companies c
WHERE EXISTS (
    SELECT 1 FROM scoring s 
    WHERE s.company_id = c.id AND s.score > 8
)
```

**3. Batch Operations:**
```python
# BAD - N individual inserts
for company in companies:
    await db.execute("INSERT INTO companies ...", company)

# GOOD - Single batch insert
await db.execute(
    "INSERT INTO companies (id, name) VALUES ($1, $2), ($3, $4), ...",
    flattened_values
)
```

**4. Query Plan Analysis:**
```python
async def explain_query(query: str, *args):
    """Get query execution plan."""
    plan = await db.fetch(
        f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}",
        *args
    )
    return json.loads(plan[0][0])
```

---

### Story 8: Read Replicas & Load Distribution
**Points:** 8
**Priority:** P2

Implement read replicas for query distribution.

**Architecture:**
```
Application
    ├── Write Queries ──→ Primary DB
    └── Read Queries ───→ Read Replica 1
                      ───→ Read Replica 2
```

**Implementation:**
```python
class DatabaseRouter:
    def get_engine(self, operation: str):
        if operation == 'write':
            return primary_engine
        else:
            # Round-robin between replicas
            return random.choice(replica_engines)

# Usage
@router.get("/companies")
async def list_companies():
    # Automatically uses read replica
    return await db.fetch_all("SELECT * FROM companies")

@router.post("/companies")
async def create_company():
    # Uses primary for writes
    return await db.execute("INSERT INTO companies ...")
```

**Tasks:**
- [ ] Set up read replica
- [ ] Implement query routing
- [ ] Handle replication lag
- [ ] Monitor replica lag

---

## Database Schema Improvements

### Table Partitioning
```sql
-- Partition large tables by date
CREATE TABLE scoring_records (
    id UUID,
    company_id UUID,
    created_at TIMESTAMP,
    ...
) PARTITION BY RANGE (created_at);

CREATE TABLE scoring_records_2026_q1 PARTITION OF scoring_records
    FOR VALUES FROM ('2026-01-01') TO ('2026-04-01');
```

### Archival Strategy
```python
# Archive old data
async def archive_old_data():
    """Move data older than 1 year to archive."""
    await db.execute("""
        INSERT INTO scoring_records_archive
        SELECT * FROM scoring_records
        WHERE created_at < NOW() - INTERVAL '1 year'
    """)
    
    await db.execute("""
        DELETE FROM scoring_records
        WHERE created_at < NOW() - INTERVAL '1 year'
    """)
```

---

## Definition of Done
- [ ] All queries <50ms (p95)
- [ ] Zero N+1 patterns
- [ ] 100% index coverage
- [ ] Pool optimized
- [ ] Monitoring operational
- [ ] Migration process documented

## Estimated Effort
- **Total Points:** 49
- **Duration:** 8-10 weeks
- **Team:** 1 senior developer + DBA

## Dependencies
- EPIC-020 (God functions) - Optimize queries after cleanup
- EPIC-023 (Performance) - Coordinate with performance work

---

*Created: 2026-03-06*  
*Target Release: Q3 2026*
