# Solstein Master Fix Plan

## Executive Summary

**Goal**: Transform Solstein from a code-beautiful but data-broken system into a production-ready competitive intelligence platform with real Supabase database integration.

**Current State**: 927 tests passing, 100% type hints, fully implemented connectors (SEC EDGAR, Companies House, News API), BUT loads from JSON mock files instead of database.

**Target State**: Real-time data pipeline from Supabase → Enrichment (connectors) → Persistence → API serving real data.

**Estimated Duration**: 30-40 hours across 6 waves

---

## Critical Dependencies

**Sequential Execution Required**:
- Wave 1 (Supabase Foundation) must complete before Wave 2 (Persistence)
- Wave 2 must complete before Wave 3 (Real Data Pipeline)
- Wave 3 must complete before Wave 4 (API Integration)
- Wave 4 must complete before Wave 5 (Validation)

---

## Wave 1: Supabase Foundation (4-6 hours)

**Goal**: Deploy Supabase schema, create company/scoring tables, set up RLS policies

### Task 1.1: Deploy Supabase Schema (2h)

**What to do**:
- Run `supabase db reset` to apply all migrations
- Verify tables exist: companies, scoring_results, enrichment_data
- Check RLS policies are in place
- Run seed scripts if available

**Code References**:
- `/home/ai-whisperers/solstein/supabase/migrations/` - Migration files
- `/home/ai-whisperers/solstein/supabase/seed.sql` - Seed data

**Must NOT do**:
- Don't delete existing migrations
- Don't modify production data if connected to prod Supabase
- Don't skip RLS setup

**Acceptance Criteria**:
- [ ] All migrations apply successfully
- [ ] Tables exist in Supabase dashboard
- [ ] RLS policies prevent unauthorized access
- [ ] Can connect via psql CLI

**QA Scenario**:
```bash
supabase db reset
supabase status  # verify connected
psql $DATABASE_URL -c "\dt"  # should list companies, scoring_results tables
```

---

### Task 1.2: Create Database Models (2h)

**What to do**:
- Verify SQLAlchemy models match Supabase schema
- Add missing columns to models
- Ensure model relationships are correct
- Create Pydantic schemas for API validation

**Code References**:
- `/home/ai-whisperers/solstein/src/solstein/domain/models.py` - Domain models
- `/home/ai-whisperers/solstein/src/solstein/infrastructure/database.py` - Database config

**Must NOT do**:
- Don't change existing model structure if it breaks tests
- Don't remove backwards compatibility

**Acceptance Criteria**:
- [ ] All models have corresponding tables
- [ ] Foreign key relationships work
- [ ] Can create/read/update/delete via SQLAlchemy

**QA Scenario**:
```python
from src.solstein.infrastructure.database import DatabaseManager
from src.solstein.domain.models import Company

db = DatabaseManager(settings)
db.init_async()
async with db.session_factory() as session:
    company = await session.get(Company, "test-id")
    assert company is not None
```

---

### Task 1.3: Database Configuration Verification (1-2h)

**What to do**:
- Update `.env` with real Supabase credentials
- Test connection string
- Verify environment variables are loaded
- Test async connection pool

**Acceptance Criteria**:
- [ ] Connection string works
- [ ] Async engine initializes
- [ ] Pool size configured correctly

---

## Wave 2: Data Persistence (6-8 hours)

**Goal**: Replace JSON loaders with Supabase queries, wire enrichment to database

### Task 2.1: Create Company Repository (2h)

**What to do**:
- Create `CompanyRepository` class in `infrastructure/repositories.py`
- Implement CRUD methods: get(), list(), create(), update(), delete()
- Add query methods: get_by_ticker(), get_by_name()
- Handle async database sessions

**Code References**:
- `/home/ai-whisperers/solstein/src/solstein/infrastructure/repositories.py` - Existing repos
- `/home/ai-whisperers/solstein/src/solstein/data/loaders.py` - Current JSON loader

**Must NOT do**:
- Don't remove existing loader classes yet (backward compatibility)
- Don't break existing API contracts

**Acceptance Criteria**:
- [ ] Can get company by ID from database
- [ ] Can list all companies with pagination
- [ ] Can create new company
- [ ] Can update existing company

**QA Scenario**:
```python
repo = CompanyRepository(db)
company = await repo.get("eneve")
assert company.name == "Eneve"
```

---

### Task 2.2: Replace JSON Loader in Unified Loader (2-3h)

**What to do**:
- Modify `UnifiedCompanyLoader.load_unified_companies()` to query database first
- Fall back to JSON if company not in database (migration mode)
- Remove hardcoded `markdown_dir` path
- Add database session parameter

**Code References**:
- `/home/ai-whisperers/solstein/src/solstein/data/unified_loader.py` line 241-314

**Must NOT do**:
- Don't break existing tests - keep JSON loader as fallback
- Don't hardcode paths

**Acceptance Criteria**:
- [ ] Loads companies from database
- [ ] Falls back to JSON if not in DB
- [ ] All existing tests still pass

---

### Task 2.3: Wire Enrichment to Database Persistence (2-3h)

**What to do**:
- After `enrich_from_connectors()`, save enriched company to database
- Add UPSERT logic (update if exists, create if not)
- Save enrichment metadata (sources, timestamps, errors)
- Track data provenance per field

**Code References**:
- `/home/ai-whisperers/solstein/src/solstein/data/unified_loader.py` line 515-557

**Acceptance Criteria**:
- [ ] Enriched data saves to database
- [ ] Enrichment sources tracked
- [ ] Error logs persisted
- [ ] Data provenance recorded

---

## Wave 3: Real Data Pipeline (8-10 hours)

**Goal**: Activate all connector integrations, wire to database persistence

### Task 3.1: Wire SEC EDGAR Connector to Database (2-3h)

**What to do**:
- In `fill_nulls_from_sec_edgar()`, after enriching, save to database
- Add retry logic for database writes
- Log enrichment results
- Handle API failures gracefully

**Code References**:
- `/home/ai-whisperers/solstein/src/solstein/data/unified_loader.py` line 632-846

**Acceptance Criteria**:
- [ ] SEC data fills NULL financial fields
- [ ] Enriched data saved to database
- [ ] Errors logged but don't crash

---

### Task 3.2: Wire Companies House Connector (2-3h)

**What to do**:
- In `fill_nulls_from_companies_house()`, save enriched data
- Handle UK company numbers
- Save SIC codes, incorporation dates
- Handle API rate limits

**Code References**:
- `/home/ai-whisperers/solstein/src/solstein/data/unified_loader.py` line 849-1019

**Acceptance Criteria**:
- [ ] UK company data enriched
- [ ] Company number lookups work
- [ ] Data persisted to database

---

### Task 3.3: Wire News Signal Detector (2-3h)

**What to do**:
- In `attach_news_signals()`, save signals to database
- Create news_signals table if needed
- Deduplicate signals by (company, type, date)
- Save confidence scores

**Code References**:
- `/home/ai-whisperers/solstein/src/solstein/data/unified_loader.py` line 1022-1139

**Acceptance Criteria**:
- [ ] News signals attached to companies
- [ ] Signals saved to database
- [ ] Deduplication works

---

### Task 3.4: Schedule Refresh Jobs (2-3h)

**What to do**:
- Configure Celery tasks for periodic data refresh
- Set up schedules: daily, weekly, monthly
- Add job monitoring and error alerting
- Test job execution

**Code References**:
- `/home/ai-whisperers/solstein/src/solstein/worker.py`
- `/home/ai-whisperers/solstein/src/solstein/infrastructure/refresh.py`

**Acceptance Criteria**:
- [ ] Celery workers start
- [ ] Scheduled jobs run
- [ ] Jobs complete successfully
- [ ] Errors logged and alerted

---

## Wave 4: API Integration (4-6 hours)

**Goal**: Update endpoints to query Supabase instead of JSON

### Task 4.1: Update Company Endpoints (2h)

**What to do**:
- Update `GET /companies` to query database with pagination
- Update `GET /companies/{id}` to query database
- Update `POST /companies` to save to database
- Add filtering: by industry, tier, score range

**Code References**:
- `/home/ai-whisperers/solstein/src/solstein/api/companies.py`

**Must NOT do**:
- Don't change response schemas (backward compatibility)

**Acceptance Criteria**:
- [ ] List companies from database
- [ ] Get single company from database
- [ ] Create company saves to database
- [ ] Filtering works

---

### Task 4.2: Update Scoring Endpoints (2h)

**What to do**:
- Update `POST /scoring/company/{id}/score` to save results to database
- Update `GET /scoring/stats` to aggregate from database
- Cache recent scores

**Code References**:
- `/home/ai-whisperers/solstein/src/solstein/api/scoring.py`

**Acceptance Criteria**:
- [ ] Scores saved to database
- [ ] Stats aggregated from database
- [ ] Caching works

---

### Task 4.3: Update Market Analysis Endpoints (1-2h)

**What to do**:
- Update market endpoints to query database
- Optimize queries for performance
- Add pagination to large datasets

**Code References**:
- `/home/ai-whisperers/solstein/src/solstein/api/market.py`

**Acceptance Criteria**:
- [ ] Market analysis from database
- [ ] Search works
- [ ] Performance < 500ms for typical queries

---

## Wave 5: Validation & Testing (6-8 hours)

**Goal**: Integration tests against real database, data quality checks

### Task 5.1: Database Integration Tests (3h)

**What to do**:
- Create `tests/integration/test_database.py`
- Test CRUD operations
- Test connector enrichment persistence
- Test transaction rollback on errors

**Acceptance Criteria**:
- [ ] 80%+ coverage on database layer
- [ ] Tests run against test database
- [ ] All CRUD operations tested

---

### Task 5.2: End-to-End Pipeline Tests (3h)

**What to do**:
- Test full flow: Load → Enrich → Save → Query → Score
- Test connector error handling
- Test data quality validation

**Acceptance Criteria**:
- [ ] Full pipeline test passes
- [ ] Error scenarios handled
- [ ] Data quality validated

---

### Task 5.3: Performance Optimization (2h)

**What to do**:
- Add database indexes for common queries
- Optimize slow queries
- Add query result caching
- Load testing

**Acceptance Criteria**:
- [ ] Response times < 500ms for 95th percentile
- [ ] Database CPU < 50% under load
- [ ] Memory usage stable

---

## Wave 6: Deployment (2-4 hours)

**Goal**: Production deployment, migrations, secrets validation

### Task 6.1: Production Database Setup (1-2h)

**What to do**:
- Apply migrations to production Supabase
- Verify schema matches
- Run data validation
- Create database backups

**Acceptance Criteria**:
- [ ] Migrations apply cleanly
- [ ] Schema verified
- [ ] Backup created

---

### Task 6.2: Secrets and Environment Validation (1-2h)

**What to do**:
- Verify all environment variables set
- Test production connection strings
- Validate API keys (SEC, Companies House, NewsAPI)
- Test failover scenarios

**Acceptance Criteria**:
- [ ] All secrets configured
- [ ] Connections work
- [ ] Failover tested

---

## Guardrails & Constraints

### Critical MUST NOTs:
1. **Don't delete existing migrations** - append only
2. **Don't break existing tests** - maintain backward compatibility during transition
3. **Don't commit real API keys** - use environment variables
4. **Don't skip RLS policies** - security first
5. **Don't modify production without backup** - always backup first
6. **Don't remove JSON loaders immediately** - keep as fallback until fully migrated

### Testing Requirements:
- All existing 927 tests must still pass
- New database tests must achieve 80%+ coverage
- Integration tests must run against test database
- Performance tests must meet < 500ms latency target

### Rollback Strategy:
- Keep JSON loader as fallback for Wave 1-4
- Database writes are UPSERTs (idempotent)
- Feature flags can disable database mode
- Git revert available for each wave

---

## Evidence Locations

**Plan Output**: `.sisyphus/plans/solstein-master-fix.md`
**Task Tracking**: TodoWrite updates after each task
**QA Evidence**: Test output saved to `tests/output/`
**Performance Metrics**: `logs/performance.log`
**Migration History**: Supabase dashboard + `supabase/migrations/`

---

## Success Metrics

**Functional**:
- [ ] Companies load from database (not JSON)
- [ ] Enrichment saves to database
- [ ] API endpoints serve real data
- [ ] Connectors run on schedule

**Performance**:
- [ ] API response < 500ms (95th percentile)
- [ ] Database CPU < 50% under load
- [ ] Connector enrichment < 5s per company

**Quality**:
- [ ] NULL data reduced from 84% to <30%
- [ ] All 927 existing tests pass
- [ ] 80%+ new test coverage
- [ ] Zero security vulnerabilities

**Operational**:
- [ ] Automated refresh jobs running
- [ ] Error alerting configured
- [ ] Database backups scheduled
- [ ] Documentation updated

---

## Agent Execution Strategy

### Wave 1: Supabase Foundation
- **Agent Profile**: quick, ultrabrain
- **Parallelization**: Tasks 1.1, 1.2 can run in parallel
- **Dependencies**: 1.3 depends on 1.1

### Wave 2: Data Persistence
- **Agent Profile**: quick, deep
- **Parallelization**: Sequential execution required
- **Dependencies**: Each task builds on previous

### Wave 3: Real Data Pipeline
- **Agent Profile**: quick, deep
- **Parallelization**: Tasks 3.1, 3.2, 3.3 can run in parallel
- **Dependencies**: 3.4 depends on all previous

### Wave 4: API Integration
- **Agent Profile**: quick
- **Parallelization**: Tasks 4.1, 4.2, 4.3 can run in parallel
- **Dependencies**: None between tasks

### Wave 5: Validation & Testing
- **Agent Profile**: quick, deep
- **Parallelization**: Sequential execution required
- **Dependencies**: Each task builds on previous

### Wave 6: Deployment
- **Agent Profile**: quick
- **Parallelization**: Sequential execution required
- **Dependencies**: User confirmation between steps

---

## Command to Start

To begin execution:
```
/start-work solstein-master-fix
```

This will:
1. Execute Wave 1 Task 1.1 (Supabase schema deployment)
2. Progress through all waves sequentially
3. Run QA after each task
4. Generate evidence at each checkpoint
5. Complete all 40+ hours of work

---

**Plan Generated**: 2026-02-26
**Total Tasks**: 22 tasks across 6 waves
**Estimated Duration**: 30-40 hours
**Target Completion**: Production-ready Solstein with real Supabase integration
