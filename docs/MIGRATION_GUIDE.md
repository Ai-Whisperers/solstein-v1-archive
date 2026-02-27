# Solstein Database Migration Guide

This guide describes how to migrate Solstein from JSON file storage to PostgreSQL.

## Overview

Solstein has been migrated from a JSON file-based storage system to a proper PostgreSQL database. This migration provides:

- **Data integrity** through constraints and foreign keys
- **Better performance** with optimized indexes
- **Scalability** for production workloads
- **Concurrent access** support
- **ACID compliance** for data consistency

## Prerequisites

Before starting the migration, ensure you have:

1. **PostgreSQL 14+** installed or access to a PostgreSQL instance
2. **Database URL** configured in environment variables
3. **Python 3.11+** with dependencies installed
4. **Backup** of any existing data

## Environment Setup

Set the following environment variables:

```bash
export DATABASE_URL="postgresql+asyncpg://user:password@host:port/database"
```

Or create a `.env` file:

```env
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
```

## Migration Steps

### Step 1: Create Database Schema

Run the migration scripts to create all tables:

```bash
# Using psql
psql $DATABASE_URL -f supabase/migrations/001_companies.sql
psql $DATABASE_URL -f supabase/migrations/002_research_runs.sql
psql $DATABASE_URL -f supabase/migrations/003_facts.sql
psql $DATABASE_URL -f supabase/migrations/004_signals.sql
psql $DATABASE_URL -f supabase/migrations/005_contradictions.sql
psql $DATABASE_URL -f supabase/migrations/006_source_documents.sql

# Additional migrations
psql $DATABASE_URL -f supabase/migrations/007_scoring_records.sql
psql $DATABASE_URL -f supabase/migrations/008_enrichment_tables.sql
psql $DATABASE_URL -f supabase/migrations/009_market_snapshots.sql
psql $DATABASE_URL -f supabase/migrations/010_audit_trails.sql

# Constraints and indexes
psql $DATABASE_URL -f supabase/migrations/011_foreign_keys.sql
psql $DATABASE_URL -f supabase/migrations/012_database_constraints.sql
psql $DATABASE_URL -f supabase/migrations/013_optimized_indexes.sql
```

Or run all migrations at once:

```bash
for f in supabase/migrations/*.sql; do
    psql $DATABASE_URL -f "$f"
done
```

### Step 2: Migrate Existing Data

If you have existing JSON data, run the migration script:

```bash
python scripts/migrate_competitor_data.py --source data/competitors/ --dry-run
```

Remove `--dry-run` to perform the actual migration:

```bash
python scripts/migrate_competitor_data.py --source data/competitors/
```

### Step 3: Verify Migration

Run the integrity verification script:

```bash
python scripts/verify_database_integrity.py
```

This checks:
- All expected tables exist
- Foreign key relationships are valid
- No orphaned records
- Data consistency

### Step 4: Run Tests

Execute the test suite to ensure everything works:

```bash
# Run all tests
pytest tests/ -v

# Run integration tests only
pytest tests/integration/ -v

# Run performance tests
pytest tests/performance/ -v
```

### Step 5: Performance Baseline

Establish performance benchmarks:

```bash
python scripts/performance_baseline.py --save
```

This creates `performance_baseline.json` for future comparisons.

## Rollback Plan

If you need to rollback, see [ROLLBACK_PLAN.md](ROLLBACK_PLAN.md).

## Troubleshooting

### Connection Issues

If you encounter connection errors:

1. Verify DATABASE_URL format
2. Check network connectivity to database
3. Ensure database user has proper permissions

### Migration Failures

If migration fails:

1. Check logs for specific error
2. Verify database schema version
3. Run verification script to identify issues
4. Consider partial migration with `--limit` flag

### Performance Issues

If queries are slow:

1. Verify indexes were created: `\di` in psql
2. Run `ANALYZE` on all tables
3. Check query plans with `EXPLAIN ANALYZE`
4. Compare with performance baseline

## Verification Checklist

- [ ] All 13 migration files applied
- [ ] 21 tables created
- [ ] Foreign key constraints active
- [ ] CHECK constraints enforced
- [ ] Indexes created for performance
- [ ] Data migrated successfully
- [ ] Integration tests passing
- [ ] Performance baseline established
- [ ] API endpoints responding correctly
- [ ] No errors in application logs

## Support

For issues or questions:

1. Check existing documentation
2. Review test suite for examples
3. Consult architecture documentation
4. Contact development team

## Migration Summary

| Component | Before | After |
|-----------|--------|-------|
| Storage | JSON files | PostgreSQL |
| Tables | N/A | 21 |
| Foreign Keys | None | 20+ |
| Constraints | None | 50+ |
| Indexes | None | 40+ |
| Repository Pattern | Sync + Async | Unified Async |
| Test Coverage | Low | High |

---

**Note**: This is a one-way migration. Ensure you have backups before proceeding.
