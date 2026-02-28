# Waves 2-5 Execution Plan - Test Coverage Roadmap

**Current Status**: 890 PASSED, 92 FAILED, 114 ERRORS  
**Coverage**: ~62-65% (target: 80%+)  
**Gap**: +15-18% needed

---

## Failure Categories & Fix Priority

### 🔴 Category A: DATABASE_URL Errors (114 errors)
**Impact**: Large (49 repository tests, 20 company repo tests, etc.)  
**Blocker**: Requires PostgreSQL setup  
**Status**: Can skip for now or setup Docker  
**Tests Affected**:
- test_repositories_comprehensive.py (49)
- test_company_repository.py (20)
- test_fact_repository.py (13)
- test_enrichment_repositories.py (12)
- test_database_service.py (12)
- test_database.py (8)

### 🟡 Category B: Logic Failures - Fixable NOW (92 failures)
**Impact**: Medium (direct logic issues)  
**Status**: Can fix immediately  
**Breakdown**:
1. **Worker tasks** (13 failures) - Async/mock issues
2. **Scoring logic** (20 failures) - Score calculation bugs
3. **Connector mocks** (8 failures) - Error handling test setup
4. **ORM validations** (11 failures) - Model validation
5. **Data loaders** (4 failures) - File loading logic
6. **Analytics/Growth** (20 failures) - Score calculation
7. **API base** (3 failures) - Repository fallback logic
8. **Other** (13 failures) - Various

---

## Wave 2: Core Logic Layer - Detailed Tasks

### Task 2.1: Fix Scoring Logic (20 failures)
**Files**: test_scoring.py, test_scorers_*.py, test_*scorer_with_facts.py  
**Failures**:
- Growth score calculations (10 failures)
- Financial score calculations (6 failures)
- Competitive position scoring (2 failures)
- Edge cases (2 failures)

**Action**: 
1. Analyze scoring formulas in src/solstein/services/scorers/
2. Run failing tests with `-vv` to see actual vs expected
3. Fix score calculation logic
4. Verify with pytest

### Task 2.2: Fix Analytics Layer (4 failures)
**Files**: test_analytics_*.py  
**Failures**: Repository fallback, company score calculation  
**Action**: Fix async repository handling

### Task 2.3: Fix Worker Tasks (13 failures)
**Files**: test_worker_tasks.py  
**Root**: Async mock setup issues  
**Action**: Fix AsyncMock patterns for connector calls

---

## Wave 3: Integration Layer

### Task 3.1: Fix API Base Coverage (3 failures)
**Files**: test_api_base_coverage.py  
**Failures**: Repository selection logic  

### Task 3.2: Fix Data Loaders (4 failures)
**Files**: test_data_loaders_coverage.py  
**Root**: JSON file loading issues

---

## Wave 4: Reporting Layer

### Task 4.1: Exporters (0 failures visible)
Status: Likely passing, minimal work

---

## Execution Strategy

### Phase 1: Quick Wins (Scoring + Validation)
1. Fix scoring logic (20 tests) - 1-2 hours
2. Fix ORM validations (11 tests) - 30 min
3. Fix connector mocks (8 tests) - 1 hour
   **Expected gain**: +39 tests (~4% coverage)

### Phase 2: Integration Layer
1. Fix worker tasks (13 tests) - 1 hour
2. Fix analytics layer (4 tests) - 30 min
3. Fix API/loaders (7 tests) - 1 hour
   **Expected gain**: +24 tests (~3% coverage)

### Phase 3: Database Layer (If Setup Done)
1. Fix DATABASE_URL setup (Docker)
2. Run 114 repository/database tests
   **Expected gain**: +114 tests (~12% coverage)

---

## Recommended Command Sequence

```bash
# Phase 1: Scoring fixes
pytest tests/unit/test_scoring.py -v --tb=short -x
pytest tests/unit/test_scorers_*.py -v --tb=short
pytest tests/unit/test_*scorer_with_facts.py -v --tb=short

# Phase 2: Analytics + Worker tasks
pytest tests/unit/test_analytics_*.py -v --tb=short
pytest tests/unit/test_worker_tasks.py -v --tb=short

# Phase 3: Data layer
pytest tests/unit/test_data_loaders_coverage.py -v --tb=short
pytest tests/unit/test_api_base_coverage.py -v --tb=short

# Final: Full suite (with DB setup)
pytest tests/unit/ -v --tb=short
```

---

## Coverage Roadmap

| Phase | Tests Fixed | Cumulative | Est. Coverage |
|-------|------------|-----------|---|
| Start | - | 890 | 62-65% |
| Phase 1 | +39 | 929 | 67-70% |
| Phase 2 | +24 | 953 | 70-73% |
| **Phase 3** (DB) | **+114** | **1,067** | **80%+** |

---

## Success Criteria

- [ ] Phase 1: All scoring tests pass (20/20)
- [ ] Phase 1: All validations pass (11/11)
- [ ] Phase 2: All worker tasks pass (13/13)
- [ ] Phase 2: All analytics pass (4/4)
- [ ] Phase 3: All repository tests pass (114/114) *if DB setup*
- [ ] Final: 1,000+ tests passing, 80%+ coverage

