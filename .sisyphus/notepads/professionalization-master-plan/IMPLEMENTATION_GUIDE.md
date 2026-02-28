# Professionalization Master Plan - Implementation Guide

**Status**: 7/23 tasks complete (30%)  
**Next Task**: W2-T8 (Migrate all services to async repos)  
**Token Budget**: Critical - Use this guide for efficient continuation

---

## Task 8: Migrate All Services to Async Repos

### Services to Update (5 files)
1. `src/solstein/data/connectors/lookup_service.py`
2. `src/solstein/data/enrichment_service.py`
3. `src/solstein/api/services/enrichment_service.py`
4. `src/solstein/api/services/drill_down_service.py`
5. `src/solstein/infrastructure/database_service.py`

### Migration Steps
1. **Find all repository usages** in each service
2. **Replace JsonFileRepository** with CompanyRepository or FactRepository
3. **Ensure async/await patterns** are correct
4. **Update method signatures** to be async where needed
5. **Test each service** after migration

### Key Changes
- Replace: `JsonFileRepository()` → `CompanyRepository(session)` or `FactRepository(session)`
- Add: `async def` to methods that call repository methods
- Add: `await` before all repository method calls
- Update: Dependency injection to provide async sessions

### Verification
```bash
pytest tests/ -v
mypy src/solstein --strict
```

---

## Task 9: Repository Layer Verification

### Verification Steps
1. Run full test suite: `pytest tests/ -v`
2. Check for any import errors
3. Verify all async/await patterns
4. Check data integrity with sample queries
5. Verify no synchronous calls remain

### Expected Results
- All 1434 tests pass
- No import errors
- No type errors with mypy
- All repository methods are async

---

## Wave 3: Production Code Cleanup (Tasks 10-14)

### Task 10: Remove MockTemporalClient
**File**: `src/solstein/api/services/scoring_service.py`
**Action**: Replace MockTemporalClient with real async implementation
**Impact**: Scoring service will use real async workflows

### Task 11: Remove MockAsyncWorkflowService
**File**: `src/solstein/infrastructure/workflow_service.py`
**Action**: Replace mock with real async workflow implementation
**Impact**: Workflow service will use real async patterns

### Task 12: Migrate Remaining JSON Usage
**Files**: Search for `json.load`, `json.dump` in production code
**Action**: Replace with database queries
**Impact**: Zero JSON dependency in production

### Task 13: Update API Endpoints
**Files**: `src/solstein/api/routers/*.py`
**Action**: Update all endpoints to use new repositories
**Impact**: All endpoints use async database access

### Task 14: Production Code Verification
**Action**: Run full test suite and verify no regressions
**Impact**: Production code is clean and async

---

## Wave 4: Constraints & Optimization (Tasks 15-19)

### Task 15: Add Foreign Key Constraints
**Files**: `alembic/versions/009_add_foreign_key_constraints.py`
**Action**: Add FK constraints to all tables
**Tables**: research_runs, enrichment_jobs, evidence_readiness, etc.

### Task 16: Standardize Primary Key Types
**Action**: Ensure all PKs are UUID type
**Verify**: All tables use UUID for id column

### Task 17: Add CHECK Constraints
**Action**: Add CHECK constraints for status fields, numeric ranges
**Example**: `CHECK (readiness_score >= 0 AND readiness_score <= 100)`

### Task 18: Optimize Indexes
**Action**: Add indexes for frequently queried columns
**Columns**: status, created_at, company_id, signal_id

### Task 19: Performance Verification
**Action**: Run load tests and verify performance
**Target**: <100ms for most queries

---

## Wave 5: Final Integration & Documentation (Tasks 20-23)

### Task 20: Full Test Suite Run
```bash
pytest tests/ -v --cov=src/solstein --cov-report=html
```
**Target**: 75%+ code coverage

### Task 21: Integration Testing
**Action**: Test full cascade from API to database
**Verify**: End-to-end workflows work correctly

### Task 22: Update Documentation
**Files**: README.md, FEATURE_CASCADE.md
**Action**: Document new async architecture
**Include**: Migration guide, API changes, database schema

### Task 23: Final Verification (F1-F3)
**F1**: Plan Compliance Audit (oracle review)
**F2**: Code Quality Review (type check, lint, tests)
**F3**: Real Manual QA (end-to-end testing)

---

## Quick Reference: Repository Classes

### CompanyRepository
**File**: `src/solstein/infrastructure/company_repository.py`
**Methods**:
- `async def get_all() → list[CompanyRecord]`
- `async def get_by_id(id: UUID) → CompanyRecord`
- `async def create(company: CompanyRecord) → CompanyRecord`
- `async def update(id: UUID, company: CompanyRecord) → CompanyRecord`
- `async def delete(id: UUID) → bool`
- `async def search(query: str) → list[CompanyRecord]`

### FactRepository
**File**: `src/solstein/infrastructure/repositories.py`
**Methods**:
- `async def get_all() → list[FactRecord]`
- `async def get_by_id(id: UUID) → FactRecord`
- `async def create(fact: FactRecord) → FactRecord`
- `async def update(id: UUID, fact: FactRecord) → FactRecord`
- `async def delete(id: UUID) → bool`
- `async def search(query: str) → list[FactRecord]`

---

## Parallelization Strategy

### Can Run in Parallel
- **Wave 3**: Tasks 10, 11, 12, 13 (independent services)
- **Wave 4**: Tasks 15, 16, 17, 18 (independent migrations)

### Must Run Sequentially
- **Wave 2**: T8 → T9 (T9 depends on T8)
- **Wave 5**: T20 → T21 → T22 → T23 (sequential testing)

### Recommended Execution
1. **Day 1**: Wave 2 (T8-T9) - 2 tasks
2. **Day 2**: Wave 3 (T10-T14) - 5 tasks in parallel
3. **Day 3**: Wave 4 (T15-T19) - 5 tasks in parallel
4. **Day 4**: Wave 5 (T20-T23) - 4 tasks sequential
5. **Day 5**: Final verification (F1-F3)

**Total**: 5 days (vs 11 days sequential)

---

## Common Patterns

### Async Service Pattern
```python
class MyService:
    def __init__(self, session: AsyncSession):
        self.company_repo = CompanyRepository(session)
    
    async def get_company(self, id: UUID) -> CompanyRecord:
        return await self.company_repo.get_by_id(id)
```

### Async Endpoint Pattern
```python
@router.get("/companies/{id}")
async def get_company(id: UUID, session: AsyncSession = Depends(get_session)):
    service = MyService(session)
    return await service.get_company(id)
```

### Async Repository Pattern
```python
class MyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, id: UUID) -> Record:
        stmt = select(RecordModel).where(RecordModel.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
```

---

## Troubleshooting

### Issue: "RuntimeError: no running event loop"
**Solution**: Ensure all async functions are called with `await`

### Issue: "AttributeError: 'NoneType' object has no attribute..."
**Solution**: Check that repository methods return proper objects, not None

### Issue: "TypeError: object is not awaitable"
**Solution**: Ensure all repository methods are async and called with `await`

### Issue: Test failures after migration
**Solution**: Check that test fixtures provide proper async sessions

---

## Success Criteria

- [x] Wave 1 complete (4/4 tasks)
- [x] Wave 2 partial (3/5 tasks)
- [ ] Wave 2 complete (T8-T9)
- [ ] Wave 3 complete (T10-T14)
- [ ] Wave 4 complete (T15-T19)
- [ ] Wave 5 complete (T20-T23)
- [ ] Final verification (F1-F3)
- [ ] All tests pass (1434 items)
- [ ] Zero JSON in production
- [ ] All code async
- [ ] Full documentation updated

---

## Resources

### Key Files
- Repositories: `src/solstein/infrastructure/repositories.py`, `company_repository.py`
- Services: `src/solstein/api/services/`, `src/solstein/data/`
- Migrations: `alembic/versions/`
- Tests: `tests/`

### Commands
```bash
# Run tests
pytest tests/ -v

# Type check
mypy src/solstein --strict

# Lint
ruff check src/solstein

# Format
black src/solstein && isort src/solstein

# Find JSON usage
grep -r "json.load\|json.dump" src/solstein

# Find mock usage
grep -r "Mock" src/solstein
```

---

**End of Implementation Guide**
