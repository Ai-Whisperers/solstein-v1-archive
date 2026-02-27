# Solstein Professionalization Master Plan

## Project: Complete Migration from JSON/Mocks to Professional Database Architecture

**Date**: 2026-02-27  
**Estimated Duration**: 4-6 weeks  
**Priority**: High - Critical for production readiness  

---

## TL;DR

Transform Solstein from a prototype with JSON files and mocks into a production-ready system with:
- ✅ All data in PostgreSQL (no JSON files)
- ✅ Unified async repository pattern
- ✅ No mocks in production code
- ✅ Complete test coverage with real database
- ✅ Proper foreign keys and constraints

**23 major tasks across 5 waves**

---

## Context

### Current State
- **17 database tables** with proper schema
- **Mixed repository patterns** (sync/async, SQLAlchemy/Supabase/JSON)
- **Company data in JSON file** (data/input/competitor_data.json)
- **3 test files broken** (import errors)
- **Mocks in production code** (MockTemporalClient)

### Target State
- **All data in database** (zero JSON dependency for core data)
- **Unified async SQLAlchemy repositories**
- **Zero mocks in production**
- **All tests using real database**
- **Complete foreign key constraints**

---

## Work Objectives

### Core Objective
Migrate all JSON-based and mock-based functionality to use the PostgreSQL database with proper async SQLAlchemy patterns.

### Concrete Deliverables
1. Migration script to load competitor_data.json into companies table
2. Fixed test files (3 files with import errors)
3. Unified async repository layer (5 repositories)
4. Migration of all JSON usage to database queries
5. Removal of mocks from production services
6. Complete foreign key constraints

### Definition of Done
- [ ] `pytest tests/` passes with 100% collection rate (no import errors)
- [ ] No JSON files in data/input/ (except test fixtures)
- [ ] All repositories use async SQLAlchemy pattern
- [ ] No Mock* classes instantiated in production code paths
- [ ] All foreign keys have proper database constraints
- [ ] CI/CD pipeline passes all tests

### Must Have
- Data integrity during migration
- Backward compatibility during transition
- All existing tests pass
- No production data loss

### Must NOT Have
- Breaking changes to public API without versioning
- Removal of features (only migration)
- Introduction of new bugs
- Performance degradation >20%

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: YES (pytest, async fixtures)
- **Automated tests**: TDD-style for new code, tests-after for migrations
- **Framework**: pytest-asyncio

### QA Policy
Every task includes:
- Database migration verification (data integrity checks)
- Integration tests with real database
- Regression tests for existing functionality
- Evidence capture to `.sisyphus/evidence/`

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Foundation - Week 1):
├── Task 1: Data migration script (JSON → DB)
├── Task 2: Fix broken test files (3 files)
├── Task 3: Add missing table migrations
└── Task 4: Database integrity verification

Wave 2 (Repository Unification - Week 2):
├── Task 5: Convert FactRepository to async
├── Task 6: Deprecate JsonFileRepository
├── Task 7: Create unified CompanyRepository
├── Task 8: Migrate all services to async repos
└── Task 9: Repository layer verification

Wave 3 (Production Code Cleanup - Week 3):
├── Task 10: Remove MockTemporalClient from ScoringService
├── Task 11: Remove MockAsyncWorkflowService
├── Task 12: Migrate remaining JSON usage
├── Task 13: Update API endpoints to use new repos
└── Task 14: Production code verification

Wave 4 (Constraints & Optimization - Week 4):
├── Task 15: Add foreign key constraints
├── Task 16: Standardize primary key types
├── Task 17: Add CHECK constraints
├── Task 18: Optimize indexes
└── Task 19: Performance verification

Wave 5 (Final Integration & Documentation - Week 5-6):
├── Task 20: Full test suite run
├── Task 21: Integration testing
├── Task 22: Update documentation
├── Task 23: Final verification (F1-F3)
└── Task 24: Deployment to production

Critical Path: Task 1 → Task 5 → Task 10 → Task 15 → Task 20 → F1-F3
Parallel Speedup: ~60% faster than sequential
Max Concurrent: 4 tasks (Wave 3-4)
```

---

## TODOs

## TODOs

> Implementation + Test = ONE Task. Never separate.
> EVERY task MUST have: Recommended Agent Profile + Parallelization info + QA Scenarios.
> **A task WITHOUT QA Scenarios is INCOMPLETE. No exceptions.**

---

### Wave 1: Foundation (Tasks 1-4) - Week 1

---

- [ ] **Task 1: Create Data Migration Script (JSON → Database)**

  **What to do**:
  1. Read data/input/competitor_data.json
  2. Parse 3 companies with all nested data (revenue timeline, funding, etc.)
  3. Insert into companies table with proper JSONB serialization
  4. Handle nested objects (revenue_timeline, funding_rounds, lead_investors)
  5. Add verification step to confirm data loaded correctly

  **File to create**: scripts/migrate_competitor_data.py
  
  **Acceptance Criteria**:
  - [ ] Script runs without errors
  - [ ] All 3 companies inserted into companies table
  - [ ] Nested JSON data properly stored in JSONB columns
  - [ ] Verification query returns 3 records
  - [ ] Script is idempotent (can run multiple times safely)

  **Commit**: YES
  - Message: "feat(migration): add script to migrate competitor data from JSON to DB"
  - Files: scripts/migrate_competitor_data.py

- [ ] **Task 2: Fix Broken Test Files (3 Files with Import Errors)**

  **What to do**:
  1. Fix tests/integration/test_repository_sync.py - NameError: CompetitorDataLoader
  2. Fix tests/unit/test_repositories.py - ImportError: CompetitorDataLoader
  3. Fix tests/unit/test_sequential_orchestrator.py - NameError: load_companies

  **Files to modify**:
  - tests/integration/test_repository_sync.py
  - tests/unit/test_repositories.py
  - tests/unit/test_sequential_orchestrator.py

  **Acceptance Criteria**:
  - [ ] pytest --collect-only runs without import errors
  - [ ] All 3 files show test count (not collection error)
  - [ ] Tests can be imported individually

  **Commit**: YES (grouped as single commit)
  - Message: "fix(tests): resolve import errors in 3 test files"

- [ ] **Task 3: Add Missing Table Migrations**

  **What to do**:
  Create migrations for tables defined in database_models.py but missing from migrations:
  
  1. **007_scoring_records.sql** - Company scoring results
  2. **008_enrichment_tables.sql** - Enrichment system
  3. **009_market_snapshot.sql** - Market analysis
  4. **010_audit_trail.sql** - Complete audit

  **Files to create**:
  - supabase/migrations/007_scoring_records.sql
  - supabase/migrations/008_enrichment_tables.sql
  - supabase/migrations/009_market_snapshot.sql
  - supabase/migrations/010_audit_trail.sql

  **Acceptance Criteria**:
  - [ ] All 4 migration files created
  - [ ] Migrations run successfully on Supabase
  - [ ] All tables appear in database schema
  - [ ] Foreign keys properly defined

  **Commit**: YES (one commit per migration file)

- [ ] **Task 4: Database Integrity Verification**

  **What to do**:
  1. Run data integrity checks
  2. Verify all foreign key relationships
  3. Check for orphaned records
  4. Validate constraint compliance
  5. Generate integrity report

  **Script to create**: scripts/verify_database_integrity.py

  **Acceptance Criteria**:
  - [ ] All integrity checks pass
  - [ ] No orphaned records found
  - [ ] No constraint violations
  - [ ] Report generated with recommendations

  **Commit**: YES
  - Message: "feat(scripts): add database integrity verification script"

---

### Wave 2: Repository Unification (Tasks 5-8) - Week 2

---

- [ ] **Task 5: Convert FactRepository to Async Pattern**

  **What to do**:
  Convert src/solstein/infrastructure/repositories.py from sync to async:
  
  1. Update FactRepository.__init__ to accept AsyncSession
  2. Convert all methods to async (9 methods)
  3. Update session operations to use await
  4. Replace query() with execute(select())

  **File to modify**: src/solstein/infrastructure/repositories.py

  **Acceptance Criteria**:
  - [ ] All methods are async
  - [ ] All session operations use await
  - [ ] Uses select() instead of query()
  - [ ] Tests updated to use async pattern
  - [ ] No sync DatabaseManager usage

  **Commit**: YES
  - Message: "refactor(repository): convert FactRepository to async pattern"

- [ ] **Task 6: Deprecate JsonFileRepository**

  **What to do**:
  1. Mark JsonFileRepository as deprecated with warnings
  2. Create migration guide for users
  3. Update all usages to use database repository
  4. Add deprecation warning on instantiation

  **Files to modify**:
  - src/solstein/data/repositories.py (add deprecation)
  - All files using JsonFileRepository (migrate to database)

  **Acceptance Criteria**:
  - [ ] DeprecationWarning added
  - [ ] All internal usages migrated
  - [ ] Migration guide created
  - [ ] No new code uses JsonFileRepository

  **Commit**: YES
  - Message: "deprecate(repository): mark JsonFileRepository as deprecated"

- [ ] **Task 7: Create Unified CompanyRepository**

  **What to do**:
  Create a unified async SQLAlchemy repository for company operations:
  
  1. Create CompanyRepository class using async SQLAlchemy
  2. Implement standard CRUD operations
  3. Support pagination and sorting
  4. Add proper error handling
  5. Include type hints and docstrings

  **Files to create**:
  - src/solstein/infrastructure/company_repository.py
  - tests/unit/test_company_repository.py

  **Acceptance Criteria**:
  - [ ] Repository class created
  - [ ] All CRUD operations implemented
  - [ ] Pagination support
  - [ ] Proper error handling
  - [ ] 100% type coverage

  **Commit**: YES
  - Message: "feat(repository): add unified CompanyRepository with async SQLAlchemy"

- [ ] **Task 8: Migrate All Services to Async Repositories**

  **What to do**:
  Update all service classes to use new async repositories:
  
  1. **ResearchService** - Update to use async CompanyRepository
  2. **ScoringService** - Update to use async repositories
  3. **EnrichmentService** - Verify compatibility
  4. **DatabaseService** - Verify compatibility

  **Files to modify**:
  - src/solstein/research/service.py
  - src/solstein/scoring/service.py
  - src/solstein/enrichment/service.py

  **Acceptance Criteria**:
  - [ ] All services use async repositories
  - [ ] No sync repository usage in services
  - [ ] Services can be instantiated with AsyncSession
  - [ ] All service tests pass

  **Commit**: YES (one commit per service)

---

### Wave 3: Production Hardening (Tasks 9-13) - Week 3

---

- [ ] **Task 9: Remove Mocks from Production Code**

  **What to do**:
  Replace mock implementations with real dependencies:
  
  1. Replace MockTemporalClient with real TemporalClient
  2. Remove default mock fallbacks
  3. Update dependency injection
  4. Ensure all production paths use real implementations

  **Files to check/modify**:
  - src/solstein/scoring/service.py (MockTemporalClient)
  - src/solstein/research/service.py (mock dependencies)
  - Any other files with mock defaults

  **Acceptance Criteria**:
  - [ ] No MockTemporalClient in production
  - [ ] No default mock fallbacks
  - [ ] All production code uses real implementations
  - [ ] Tests provide mocks explicitly where needed

  **Commit**: YES
  - Message: "refactor(production): remove mock implementations from production code"

- [ ] **Task 10: Add Missing Foreign Key Constraints**

  **What to do**:
  Add proper foreign key constraints to SQLAlchemy models:
  
  1. Audit all model relationships
  2. Add ForeignKey() constraints where missing
  3. Add ondelete behaviors (CASCADE, SET NULL, etc.)
  4. Update migrations with FK constraints
  5. Verify no orphaned records exist

  **Files to modify**:
  - src/solstein/infrastructure/database_models.py
  - Supabase migrations (if needed)

  **Acceptance Criteria**:
  - [ ] All relationships have FK constraints
  - [ ] Proper ondelete behaviors defined
  - [ ] No orphaned records in database
  - [ ] Migrations updated

  **Commit**: YES
  - Message: "feat(db): add missing foreign key constraints"

- [ ] **Task 11: Add Database Constraints and Validation**

  **What to do**:
  Add database-level constraints for data integrity:
  
  1. CHECK constraints for numeric ranges (confidence 0-1, scores 0-10)
  2. NOT NULL constraints for required fields
  3. UNIQUE constraints for business keys
  4. Default values for timestamps
  5. Enum constraints where appropriate

  **Files to modify**:
  - src/solstein/infrastructure/database_models.py
  - Supabase migrations

  **Acceptance Criteria**:
  - [ ] CHECK constraints for numeric ranges
  - [ ] NOT NULL constraints where appropriate
  - [ ] UNIQUE constraints for business keys
  - [ ] All constraints tested

  **Commit**: YES
  - Message: "feat(db): add comprehensive database constraints"

- [ ] **Task 12: Optimize Database Indexes**

  **What to do**:
  Review and optimize database indexes:
  
  1. Add indexes for frequently queried columns
  2. Add composite indexes for common query patterns
  3. Add partial indexes for filtered queries
  4. Review existing indexes for usage
  5. Remove unused indexes

  **Files to modify**:
  - Supabase migrations (new migration file)

  **Acceptance Criteria**:
  - [ ] Indexes added for search columns (name, industry)
  - [ ] Composite indexes for common filters
  - [ ] Partial indexes for filtered queries
  - [ ] Index usage verified with EXPLAIN ANALYZE

  **Commit**: YES
  - Message: "perf(db): optimize database indexes for common queries"

- [ ] **Task 13: Database Performance Baseline**

  **What to do**:
  Establish performance baseline:
  
  1. Measure current query performance
  2. Document slow queries
  3. Set performance SLAs
  4. Create performance monitoring script
  5. Generate baseline report

  **Script to create**: scripts/benchmark_database.py

  **Acceptance Criteria**:
  - [ ] Performance metrics captured
  - [ ] Slow queries identified
  - [ ] SLAs documented
  - [ ] Benchmark script created
  - [ ] Baseline report generated

  **Commit**: YES
  - Message: "perf(db): add database performance benchmarking"

---

### Wave 4: Testing and Validation (Tasks 14-17) - Week 4

---

- [ ] **Task 14: Create Integration Tests for Data Migration**

  **What to do**:
  Create comprehensive tests for migration:
  
  1. Test JSON data loading
  2. Test database insertion
  3. Test data integrity after migration
  4. Test idempotency
  5. Test rollback capability

  **Files to create**:
  - tests/integration/test_migration.py

  **Acceptance Criteria**:
  - [ ] Migration tests pass
  - [ ] Data integrity verified
  - [ ] Idempotency tested
  - [ ] Rollback tested

  **Commit**: YES
  - Message: "test(integration): add migration integration tests"

- [ ] **Task 15: Comprehensive Repository Test Suite**

  **What to do**:
  Create complete test coverage for all repositories:
  
  1. Test all CRUD operations
  2. Test edge cases (empty results, invalid IDs)
  3. Test error handling
  4. Test FK constraint violations
  5. Test pagination
  6. Test filtering and sorting

  **Files to create/update**:
  - tests/unit/test_company_repository.py
  - tests/unit/test_fact_repository.py (extend)
  - tests/unit/test_enrichment_repositories.py (extend)
  - tests/unit/test_research_repositories.py

  **Acceptance Criteria**:
  - [ ] 100% repository method coverage
  - [ ] All edge cases tested
  - [ ] Error conditions tested
  - [ ] FK violations tested

  **Commit**: YES
  - Message: "test(repository): add comprehensive repository test suite"

- [ ] **Task 16: End-to-End API Tests**

  **What to do**:
  Create end-to-end tests for API endpoints:
  
  1. Test company CRUD endpoints
  2. Test scoring endpoints
  3. Test enrichment endpoints
  4. Test research workflow endpoints
  5. Test error responses
  6. Test authentication/authorization

  **Files to create**:
  - tests/e2e/test_companies_api.py
  - tests/e2e/test_scoring_api.py
  - tests/e2e/test_enrichment_api.py
  - tests/e2e/test_research_api.py

  **Acceptance Criteria**:
  - [ ] All API endpoints tested
  - [ ] Happy paths tested
  - [ ] Error paths tested
  - [ ] Authentication tested

  **Commit**: YES
  - Message: "test(e2e): add end-to-end API test suite"

- [ ] **Task 17: Load and Performance Testing**

  **What to do**:
  Create load tests for critical paths:
  
  1. Load test company search
  2. Load test scoring workflow
  3. Load test enrichment workflow
  4. Test with 1000+ companies
  5. Measure response times
  6. Identify bottlenecks

  **Files to create**:
  - tests/performance/test_load.py
  - tests/performance/test_benchmarks.py

  **Acceptance Criteria**:
  - [ ] Load tests created
  - [ ] Performance benchmarks established
  - [ ] Bottlenecks identified
  - [ ] Performance requirements met

  **Commit**: YES
  - Message: "test(perf): add load and performance testing"

---

### Wave 5: Documentation and Deployment (Tasks 18-24) - Week 5

---

- [ ] **Task 18: Migration Guide Documentation**

  **What to do**:
  Create comprehensive migration guide:
  
  1. Pre-migration checklist
  2. Step-by-step migration instructions
  3. Data verification steps
  4. Rollback instructions
  5. Troubleshooting common issues
  6. Post-migration validation

  **File to create**: MIGRATION_GUIDE.md

  **Acceptance Criteria**:
  - [ ] Guide covers all migration steps
  - [ ] Checklists provided
  - [ ] Troubleshooting section included
  - [ ] Rollback instructions clear

  **Commit**: YES
  - Message: "docs: add comprehensive migration guide"

- [ ] **Task 19: Update Architecture Documentation**

  **What to do**:
  Update all architecture documentation:
  
  1. Update DATABASE.md with new schema
  2. Update TESTING.md with new patterns
  3. Update SETUP.md with new setup steps
  4. Update TROUBLESHOOTING.md with new issues
  5. Create ARCHITECTURE.md with diagrams
  6. Document repository patterns

  **Files to update**:
  - DATABASE.md
  - TESTING.md
  - SETUP.md
  - TROUBLESHOOTING.md
  - ARCHITECTURE.md (new)

  **Acceptance Criteria**:
  - [ ] All docs updated with new schema
  - [ ] Repository patterns documented
  - [ ] Architecture diagrams created
  - [ ] Cross-references verified

  **Commit**: YES (one commit per doc)

- [ ] **Task 20: API Documentation**

  **What to do**:
  Create comprehensive API documentation:
  
  1. Document all endpoints
  2. Document request/response schemas
  3. Document error responses
  4. Create OpenAPI spec
  5. Add code examples
  6. Document authentication

  **Files to create**:
  - API.md
  - openapi.yaml

  **Acceptance Criteria**:
  - [ ] All endpoints documented
  - [ ] Schemas documented
  - [ ] OpenAPI spec valid
  - [ ] Code examples provided

  **Commit**: YES
  - Message: "docs: add comprehensive API documentation"

- [ ] **Task 21: Developer Onboarding Guide**

  **What to do**:
  Create developer onboarding guide:
  
  1. Environment setup
  2. Database setup
  3. Running tests
  4. Development workflow
  5. Code standards
  6. Deployment process

  **File to create**: CONTRIBUTING.md

  **Acceptance Criteria**:
  - [ ] Setup instructions clear
  - [ ] Workflow documented
  - [ ] Standards documented
  - [ ] New developer can onboard in < 1 hour

  **Commit**: YES
  - Message: "docs: add developer onboarding guide"

- [ ] **Task 22: Staging Deployment**

  **What to do**:
  Deploy to staging environment:
  
  1. Set up staging database
  2. Run migrations on staging
  3. Deploy application code
  4. Run smoke tests
  5. Verify functionality
  6. Performance test

  **Acceptance Criteria**:
  - [ ] Staging database provisioned
  - [ ] Migrations run successfully
  - [ ] Application deployed
  - [ ] Smoke tests pass
  - [ ] Performance acceptable

  **Commit**: NO (deployment task)

- [ ] **Task 23: Production Deployment Preparation**

  **What to do**:
  Prepare for production deployment:
  
  1. Backup production database
  2. Create deployment checklist
  3. Prepare rollback plan
  4. Schedule maintenance window
  5. Notify stakeholders
  6. Prepare monitoring

  **Files to create**:
  - deployment/production-checklist.md
  - deployment/rollback-plan.md

  **Acceptance Criteria**:
  - [ ] Backup completed
  - [ ] Checklist created
  - [ ] Rollback plan ready
  - [ ] Stakeholders notified
  - [ ] Monitoring ready

  **Commit**: YES
  - Message: "docs: add production deployment preparation docs"

- [ ] **Task 24: Production Deployment**

  **What to do**:
  Execute production deployment:
  
  1. Run database migrations
  2. Deploy application code
  3. Verify deployment
  4. Run smoke tests
  5. Monitor for issues
  6. Communicate completion

  **Acceptance Criteria**:
  - [ ] Migrations run successfully
  - [ ] Application deployed and running
  - [ ] Smoke tests pass
  - [ ] No critical errors
  - [ ] Stakeholders notified

  **Commit**: NO (deployment task)

---

## Final Verification Wave (F1-F3)

---

- [ ] **F1: Oracle Compliance Audit**

  **What to do**:
  Have oracle agent verify plan compliance:
  
  1. Review all changes against plan
  2. Verify architectural consistency
  3. Check for technical debt
  4. Verify security best practices
  5. Generate compliance report

  **Acceptance Criteria**:
  - [ ] Plan compliance > 95%
  - [ ] No critical issues
  - [ ] Architecture consistent
  - [ ] Security best practices followed

- [ ] **F2: Comprehensive Test Run**

  **What to do**:
  Run full test suite:
  
  1. Run all unit tests
  2. Run all integration tests
  3. Run all e2e tests
  4. Run all performance tests
  5. Verify coverage > 80%
  6. Generate test report

  **Acceptance Criteria**:
  - [ ] All tests pass
  - [ ] Coverage > 80%
  - [ ] No test collection errors
  - [ ] Performance within SLA

- [ ] **F3: Final Code Review**

  **What to do**:
  Comprehensive code review:
  
  1. Review all modified files
  2. Check for code quality
  3. Verify type safety
  4. Check for security issues
  5. Verify documentation
  6. Generate review report

  **Acceptance Criteria**:
  - [ ] No critical issues
  - [ ] Code quality acceptable
  - [ ] Type safety 100%
  - [ ] No security issues
  - [ ] Documentation complete

---

## Commit Strategy

### Week 1 (Foundation)
1. `feat(migration): add script to migrate competitor data from JSON to DB`
2. `fix(tests): resolve import errors in 3 test files`
3. `feat(db): add scoring records migration`
4. `feat(db): add enrichment tables migration`
5. `feat(db): add market snapshot migration`
6. `feat(db): add audit trail migration`
7. `feat(scripts): add database integrity verification script`

### Week 2 (Repository Unification)
8. `refactor(repository): convert FactRepository to async pattern`
9. `deprecate(repository): mark JsonFileRepository as deprecated`
10. `feat(repository): add unified CompanyRepository`
11. `refactor(services): update ResearchService to use async repositories`
12. `refactor(services): update ScoringService to use async repositories`

### Week 3 (Production Hardening)
13. `refactor(production): remove mock implementations from production code`
14. `feat(db): add missing foreign key constraints`
15. `feat(db): add comprehensive database constraints`
16. `perf(db): optimize database indexes for common queries`
17. `perf(db): add database performance benchmarking`

### Week 4 (Testing)
18. `test(integration): add migration integration tests`
19. `test(repository): add comprehensive repository test suite`
20. `test(e2e): add end-to-end API test suite`
21. `test(perf): add load and performance testing`

### Week 5 (Documentation and Deployment)
22. `docs: add comprehensive migration guide`
23. `docs: update architecture documentation`
24. `docs: add comprehensive API documentation`
25. `docs: add developer onboarding guide`
26. `docs: add production deployment preparation docs`

---

## Success Criteria

### Verification Commands
```bash
# All tests pass
uv run pytest tests/ -v --tb=short

# No import errors
uv run pytest tests/ --collect-only 2>&1 | grep -c "ERROR" # Should be 0

# Type checking passes
uv run mypy src/solstein --ignore-missing-imports

# No lint errors
uv run ruff check src/solstein tests

# Database integrity
uv run python scripts/verify_database_integrity.py

# Repository verification
uv run python scripts/verify_repositories.py

# Performance baseline
uv run python scripts/benchmark_database.py
```

### Final Checklist
- [ ] All 24 tasks complete
- [ ] 100% test collection rate (no import errors)
- [ ] Zero JSON files for core company data
- [ ] All repositories use async pattern
- [ ] Zero mocks in production code
- [ ] All foreign keys constrained
- [ ] All database constraints added
- [ ] Performance within SLA
- [ ] CI/CD pipeline green
- [ ] Documentation updated
- [ ] Migration guide published
- [ ] Staging deployment verified
- [ ] Production deployment successful
- [ ] All verification waves passed

---

## Appendix

### A. Database Schema Reference
See DATABASE.md and MIGRATION_GUIDE.md for complete schema documentation.

### B. Rollback Procedures

#### Rollback Data Migration
```sql
-- Delete migrated data
DELETE FROM companies WHERE created_at > '2026-02-27';
```

#### Rollback Repository Changes
```bash
git revert <commit-hash>
```

#### Rollback Deployment
```bash
# Restore database from backup
# Deploy previous version
# Verify functionality
```

### C. Emergency Contacts
- Database issues: DBA team
- Deployment issues: DevOps team
- Code issues: Development team

---

**Plan Version**: 1.0  
**Last Updated**: 2026-02-27  
**Total Tasks**: 24 implementation + 3 verification  
**Estimated Duration**: 5 weeks  
**Next Review**: Weekly during execution
