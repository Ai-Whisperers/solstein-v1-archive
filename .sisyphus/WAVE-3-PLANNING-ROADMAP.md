# 📈 WAVE 3 PLANNING ROADMAP
**Code Coverage Improvements - 56% → 80%+ Target**

**Date**: 2026-02-26  
**Status**: Planning Phase  
**Effort Estimate**: 5-8 hours  
**Priority**: Medium (after Wave 2 completion)

---

## Current State

### Coverage Metrics
- **Overall Coverage**: 56% (13,382 lines, 5,906 covered)
- **Target**: 80%+
- **Gap**: 24 percentage points
- **Lines Needed**: ~2,500 additional lines of coverage

### Zero-Coverage Modules (10 modules, 1,000+ lines)

| Module | Lines | Priority | Effort | Impact |
|--------|-------|----------|--------|--------|
| `worker_tasks.py` | 467 | HIGH | 3-4h | Critical (async jobs) |
| `research/signals.py` | 167 | HIGH | 2-3h | Important (signal detection) |
| `infrastructure/confidence_adjustment.py` | 115 | MEDIUM | 1-2h | Moderate (scoring) |
| `infrastructure/unified_registry.py` | 80 | MEDIUM | 1-2h | Moderate (registry) |
| `api/services/enrichment_service.py` | 50 | MEDIUM | 1h | Moderate (API service) |
| `api/middleware.py` | 25 | LOW | 30m | Low (middleware) |
| `adapters/enrichment/funding.py` | 18 | LOW | 30m | Low (adapter) |
| `adapters/enrichment/news.py` | 19 | LOW | 30m | Low (adapter) |
| `adapters/enrichment/web_search_news.py` | 14 | LOW | 30m | Low (adapter) |
| `adapters/discovery/web_search.py` | 23 | LOW | 30m | Low (adapter) |

---

## Wave 3 Strategy

### Phase 1: High-Impact Modules (3-4 hours)
**Goal**: Add 500+ lines of coverage, reach 65%+

#### 1.1 Worker Tasks (`worker_tasks.py` - 467 lines)
**What it does**: Celery async job handlers for research pipeline

**Test Strategy**:
- Mock Celery task execution
- Test job queuing and result handling
- Test error handling and retries
- Test task state transitions

**Expected Coverage**: 80%+ of module

**Effort**: 3-4 hours

**Files to Create**:
- `tests/unit/test_worker_tasks_coverage.py` (200+ lines)

#### 1.2 Research Signals (`research/signals.py` - 167 lines)
**What it does**: Signal detection and analysis for competitive intelligence

**Test Strategy**:
- Test signal extraction from various sources
- Test signal scoring and weighting
- Test signal aggregation
- Test edge cases (missing data, invalid signals)

**Expected Coverage**: 75%+ of module

**Effort**: 2-3 hours

**Files to Create**:
- `tests/unit/test_research_signals_coverage.py` (150+ lines)

---

### Phase 2: Medium-Impact Modules (2-3 hours)
**Goal**: Add 300+ lines of coverage, reach 72%+

#### 2.1 Confidence Adjustment (`infrastructure/confidence_adjustment.py` - 115 lines)
**What it does**: Adjusts confidence scores based on data quality and source reliability

**Test Strategy**:
- Test confidence score calculations
- Test adjustment algorithms
- Test edge cases (zero confidence, perfect confidence)
- Test source weighting

**Expected Coverage**: 85%+ of module

**Effort**: 1-2 hours

**Files to Create**:
- `tests/unit/test_confidence_adjustment_coverage.py` (100+ lines)

#### 2.2 Unified Registry (`infrastructure/unified_registry.py` - 80 lines)
**What it does**: Central registry for unified data sources and configurations

**Test Strategy**:
- Test registry initialization
- Test source registration and lookup
- Test configuration management
- Test error handling

**Expected Coverage**: 80%+ of module

**Effort**: 1-2 hours

**Files to Create**:
- `tests/unit/test_unified_registry_coverage.py` (80+ lines)

---

### Phase 3: Low-Impact Modules (2-3 hours)
**Goal**: Add 200+ lines of coverage, reach 75%+

#### 3.1 API Services & Middleware (150+ lines)
- `api/services/enrichment_service.py` (50 lines)
- `api/middleware.py` (25 lines)

**Test Strategy**:
- Test service initialization and methods
- Test middleware request/response handling
- Test error handling

**Effort**: 1-2 hours

#### 3.2 Adapters (100+ lines)
- `adapters/enrichment/funding.py` (18 lines)
- `adapters/enrichment/news.py` (19 lines)
- `adapters/enrichment/web_search_news.py` (14 lines)
- `adapters/discovery/web_search.py` (23 lines)

**Test Strategy**:
- Test adapter initialization
- Test data transformation
- Test error handling

**Effort**: 1-2 hours

---

## Implementation Plan

### Step 1: Analyze Module Dependencies
```bash
# Check imports and dependencies
grep -r "from.*worker_tasks" tests/
grep -r "from.*signals" tests/
```

### Step 2: Create Test Fixtures
- Mock Celery tasks
- Mock external APIs
- Create test data factories

### Step 3: Write Tests
- Start with Phase 1 (high-impact)
- Use existing test patterns
- Follow pytest conventions

### Step 4: Verify Coverage
```bash
pytest tests/unit/ --cov=src/solstein --cov-report=term-missing
```

### Step 5: Iterate
- Identify coverage gaps
- Add edge case tests
- Refactor for clarity

---

## Success Criteria

### Coverage Targets
- **Phase 1**: 65%+ overall coverage
- **Phase 2**: 72%+ overall coverage
- **Phase 3**: 75%+ overall coverage
- **Final**: 80%+ overall coverage

### Quality Metrics
- All new tests pass
- No test flakiness
- Clear test documentation
- Good test organization

### Code Quality
- No new linting issues
- Type hints in all tests
- Proper error handling
- Meaningful assertions

---

## Risk Mitigation

### Potential Issues
1. **Complex Dependencies**: Some modules may have complex dependencies
   - **Mitigation**: Use mocking and fixtures extensively

2. **Async Code**: Worker tasks are async
   - **Mitigation**: Use `pytest-asyncio` and async test patterns

3. **External APIs**: Some modules call external services
   - **Mitigation**: Mock all external calls

4. **Time Constraints**: 5-8 hours is significant
   - **Mitigation**: Prioritize high-impact modules first

---

## Recommended Execution Order

### Session 1 (3-4 hours)
1. ✅ Analyze `worker_tasks.py` structure
2. ✅ Create test fixtures and mocks
3. ✅ Write 80%+ of worker_tasks tests
4. ✅ Verify coverage (target: 60%+)

### Session 2 (2-3 hours)
1. ✅ Write `research/signals.py` tests
2. ✅ Write `confidence_adjustment.py` tests
3. ✅ Verify coverage (target: 70%+)

### Session 3 (2-3 hours)
1. ✅ Write remaining module tests
2. ✅ Refactor and optimize
3. ✅ Final verification (target: 80%+)

---

## Alternative: Focused Coverage (2-3 hours)

If time is limited, focus on **highest-impact modules only**:

1. **worker_tasks.py** (467 lines) → 60%+ coverage
2. **research/signals.py** (167 lines) → 65%+ coverage
3. **confidence_adjustment.py** (115 lines) → 70%+ coverage

**Expected Result**: 70%+ overall coverage (vs 80%+ target)

---

## Tools & Resources

### Testing Tools
- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `pytest-cov` - Coverage reporting
- `unittest.mock` - Mocking library

### Patterns to Use
- Factory fixtures for test data
- Parametrized tests for edge cases
- Async test patterns for worker tasks
- Mock decorators for external calls

### Reference Files
- `tests/conftest.py` - Existing fixtures
- `tests/factories.py` - Test data factories
- `tests/unit/test_*.py` - Existing test patterns

---

## Conclusion

**Wave 3 is achievable in 5-8 hours** with focused effort on high-impact modules.

**Recommended approach**:
1. Start with `worker_tasks.py` (highest impact)
2. Continue with `research/signals.py`
3. Add remaining modules as time permits
4. Target: 75-80% coverage

**Next Steps**:
- [ ] Analyze module dependencies
- [ ] Create test fixtures
- [ ] Write Phase 1 tests
- [ ] Verify coverage improvements
- [ ] Iterate and refine

---

**Report Generated**: 2026-02-26 07:45 UTC  
**Status**: Ready for Implementation  
**Effort**: 5-8 hours  
**Expected Outcome**: 80%+ code coverage
