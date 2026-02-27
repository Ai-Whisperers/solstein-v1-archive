# Planning Cycle 5: Risk Mitigation & Contingency Planning

**Date**: Feb 26, 2026  
**Status**: IN PROGRESS  
**Agent**: Prometheus (Plan Builder)

---

## Risk Assessment

### Critical Risks (Block Plan Success)

#### RISK 1: Test Collection Failures (Async/Pytest Configuration)
**Severity**: CRITICAL  
**Probability**: HIGH (already occurred once)  
**Impact**: Cannot run test suite, blocks all validation

**Root Cause**:  
- `pytest-asyncio` not configured with `asyncio_mode = "auto"`
- Tests marked with `@pytest.mark.asyncio` fail without proper configuration

**Mitigation**:
```toml
# FIX BEFORE WAVE 1 STARTS - Add to pyproject.toml [tool.pytest.ini_options]
asyncio_mode = "auto"
```

**Contingency**:
- IF setup fails: Use `pytest-trio` as alternative async testing
- IF that fails: Refactor async tests as synchronous with `asyncio.run()`
- IF all fails: Skip async tests, test only sync code paths (loss of coverage)

**Acceptance Criteria**:
- [ ] `pytest tests/unit/ -v` runs without collection errors
- [ ] All 887+ tests collected and executable
- [ ] `@pytest.mark.asyncio` tests run successfully

---

#### RISK 2: Mock/Patch Strategy Incompatibilities
**Severity**: HIGH  
**Probability**: MEDIUM (async mocking tricky)  
**Impact**: Tests pass with wrong/incomplete mocks, false coverage

**Root Cause**:
- AsyncMock vs MagicMock confusion
- Mocking async context managers incorrectly
- External connector mocking incomplete

**Mitigation**:
```python
# Correct pattern for async mocks
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def mock_github_connector():
    """Correct async connector mock"""
    connector = AsyncMock(spec=GitHubConnector)
    connector.get_user_repositories = AsyncMock(return_value=[...])
    return connector

@pytest.mark.asyncio
async def test_with_async_mock(mock_github_connector):
    result = await mock_github_connector.get_user_repositories("user")
    assert mock_github_connector.get_user_repositories.called
```

**Contingency**:
- IF AsyncMock fails: Use `unittest.mock.patch` decorator instead
- IF patch fails: Create wrapper test double classes (more verbose but reliable)
- IF all fails: Test only non-async code paths

---

#### RISK 3: Coverage Regression (New Tests Break Existing Code)
**Severity**: HIGH  
**Probability**: MEDIUM  
**Impact**: Existing code breaks, coverage drops or introduces bugs

**Root Cause**:
- Tests modify shared state
- Mocks not isolated between tests
- Fixtures have side effects

**Mitigation**:
```python
# Use pytest-cov with regression detection
pytest tests/ --cov=src/solstein \
  --cov-fail-under=80 \
  --cov-report=html \
  --cov-report=term-missing
```

**Contingency**:
- IF coverage drops: Investigate which test broke it (use git bisect)
- IF test faulty: Revert test, re-implement with isolation
- IF code faulty: Fix code, don't lower coverage bar

**Pre-Wave Checklist**:
- [ ] Run full test suite before starting: `pytest tests/ -v` → all pass
- [ ] Check baseline coverage: `pytest --cov=src/solstein --cov-report=term`
- [ ] Document baseline (e.g., "56% before Wave 1")

---

### High Risks (Slow Progress)

#### RISK 4: Test Data Fixture Maintenance
**Severity**: HIGH  
**Probability**: LOW (if done right first)  
**Impact**: Tests fail, require constant fixture updates

**Root Cause**:
- Fixtures use hardcoded IDs, timestamps
- Domain models change, fixtures become invalid
- Multiple test files share brittle fixtures

**Mitigation**:
```python
# Use factory fixtures instead of hardcoded data
@pytest.fixture
def company_factory():
    """Factory to create valid test companies"""
    def _create(name="TestCorp", industry="Software", **kwargs):
        data = {
            "name": name,
            "industry": industry,
            "founded": datetime.now().year - 5,
            **kwargs
        }
        return CompanyFactory(**data)
    return _create

def test_with_factory(company_factory):
    company = company_factory(name="UniqueTestCorp")
    # Much less brittle than hardcoded data
```

**Contingency**:
- IF fixtures break: Use `@pytest.fixture(autouse=True)` cleanup
- IF fixtures still fail: Revert to JSON-based fixture files
- IF still broken: Move to integration tests with real DB

---

#### RISK 5: Database Test Isolation
**Severity**: MEDIUM  
**Probability**: MEDIUM  
**Impact**: Tests interfere with each other, flaky tests

**Root Cause**:
- AsyncSession mocks don't isolate state
- Database-dependent tests affect each other
- Transaction rollback not implemented in mocks

**Mitigation**:
```python
@pytest.fixture
async def isolated_db_session():
    """Each test gets fresh mock session"""
    session = AsyncMock(spec=AsyncSession)
    
    # Track added objects per test
    added_objects = []
    
    async def mock_add(obj):
        added_objects.append(obj)
    
    session.add = mock_add
    session.added_objects = added_objects
    
    yield session
    
    # Cleanup: verify no object leaked
    assert len(added_objects) == 0 or session.commit.called
```

**Contingency**:
- IF isolation fails: Use `pytest-xdist` for test parallelization
- IF that fails: Run tests sequentially with explicit cleanup
- IF cleanup fails: Use real test database (SQLite in-memory)

---

#### RISK 6: External Connector Mocking Gaps
**Severity**: MEDIUM  
**Probability**: MEDIUM  
**Impact**: False test passes, production failures

**Root Cause**:
- Mocks don't match actual connector interfaces
- Missing error scenarios (API down, rate limits)
- Connector updates break tests silently

**Mitigation**:
```python
# Create comprehensive mock with all methods
class MockGitHubConnectorComplete:
    """Complete mock matching GitHubConnector interface"""
    
    async def get_user_repositories(self, username: str) -> List[dict]:
        return [{"name": "repo", "stars": 100}]
    
    async def get_recent_commits(self, username: str) -> List[dict]:
        return [{"hash": "abc123", "message": "fix"}]
    
    async def get_repository_activity(self, username: str) -> dict:
        return {"stars": 100, "forks": 10}
    
    async def rate_limit_exceeded(self) -> bool:
        return False  # Normal state
    
    # Add error variants for testing
    @classmethod
    def with_rate_limit(cls):
        mock = cls()
        mock.rate_limit_exceeded = lambda: True
        return mock

# Test both normal and error paths
def test_connector_rate_limit():
    connector = MockGitHubConnectorComplete.with_rate_limit()
    # Test rate limit handling
```

**Contingency**:
- IF mocks incomplete: Compare with actual connector source code
- IF mismatch found: Update mocks before deploying tests
- IF drift occurs: Auto-generate mocks from OpenAPI/interface specs

---

### Medium Risks (Reduce Efficiency)

#### RISK 7: Long-Running Tests (Performance)
**Severity**: MEDIUM  
**Probability**: LOW (async helps)  
**Impact**: Dev cycle slows, team waits for tests

**Root Cause**:
- Slow external API calls (not mocked)
- Database operations not optimized
- Inefficient test fixtures

**Mitigation**:
```bash
# Run tests with timing
pytest tests/ -v --durations=20  # Show 20 slowest tests

# Mark slow tests separately
@pytest.mark.slow
def test_large_dataset_processing():
    # This might take 10+ seconds
    pass

# Run only fast tests during development
pytest tests/ -m "not slow" -v
```

**Contingency**:
- IF tests slow: Profile with `pytest-benchmark`
- IF slow fixture creation: Use `@pytest.fixture(scope="session")`
- IF slow assertions: Reduce assertion count, batch assertions

---

#### RISK 8: Team Context/Handoff Loss
**Severity**: MEDIUM  
**Probability**: MEDIUM (if done async across days)  
**Impact**: Duplicate work, conflicting implementations

**Root Cause**:
- Parallel agents working independently
- No shared understanding of test patterns
- No quality gates between tasks

**Mitigation**:
```
PROCESS:
1. Create shared template tests first (before Wave 1)
2. Have agents review each other's first 2-3 tests
3. Establish patterns (fixtures, mocking, structure)
4. Enforce patterns with linting rules
5. Pair first tests with review

TOOLS:
- .sisyphus/templates/test_*.template.py - Reference templates
- conftest.py - Shared fixtures (single source of truth)
- pytest.ini_options - Enforced test configuration
```

**Contingency**:
- IF drift found: Run `ruff check` + `black` on all tests
- IF patterns violated: Auto-generate fixes with ast-grep
- IF review blocked: Establish 2-hour fix deadline

---

#### RISK 9: Coverage Plateau (Hitting 80% is Easy, >85% is Hard)
**Severity**: MEDIUM  
**Probability**: HIGH  
**Impact**: Last 5-10% of coverage takes 50% of effort

**Root Cause**:
- Edge cases require deep knowledge
- Complex algorithms hard to test
- Integration test gaps

**Mitigation**:
```
STRATEGY:
1. Target 80% with Wave 1-2 (easy wins, 40-50 hours)
2. Reach 85-90% with Wave 3-4 (medium effort, 20-30 hours)
3. Don't obsess over 95%+ (diminishing returns)

FOCUS AREAS:
- Error paths (exceptions, edge cases) = easy coverage
- Edge cases (boundary values, nulls) = easy coverage
- Complex algorithms = hard coverage (skip if <5% uncovered)
- Deprecated code = skip coverage (mark with `# pragma: no cover`)
```

**Contingency**:
- IF stuck at 85%: Accept it and move to documentation
- IF 90% critical: Identify top 10 uncovered lines, test those
- IF impossible: Mark hard-to-test code as known gap (document it)

---

## Contingency Plans by Scenario

### Scenario A: Team Size Smaller Than Planned

**Assumption**: 5-agent parallel team  
**Actual**: 2-3 agents available

**Impact**: 
- Timeline: 2 weeks → 4 weeks
- Parallelization: No

**Response**:
```
OPTION 1: Sequential Execution (Safe but Slow)
  Wave 1 (4 days) → Wave 2 (4 days) → Wave 3 (4 days) → ...
  Total: 4 weeks

OPTION 2: Prioritize High-Value Work
  - MUST DO: Waves 1-2 (foundation + core logic) = 80% coverage
  - NICE: Waves 3-4 (API + utilities) = 95% coverage
  - SKIP: Utilities Wave if time constrained
  Total: 2-3 weeks for 80% target

OPTION 3: Hybrid (Recommended)
  - Agent A: Infrastructure (Wave 1, critical path)
  - Agent B: Analytics/Data (Waves 2A + 2B in parallel)
  - Sequential: Wave 3-4 after Waves 1-2 complete
  Total: 2.5-3 weeks for 80%+ coverage
```

---

### Scenario B: Blocker Discovered (e.g., Pytest Config Issue)

**Examples**:
- Async tests don't run without fixture
- Mock strategy fundamentally broken
- Coverage tool incompatible

**Response**:
```
IMMEDIATE (30 min):
1. Isolate blocker (which tests affected?)
2. Check if workaround exists (1-hour fix?)
3. IF fixable: Stop, fix, re-baseline
4. IF not fixable: Escalate decision

DECISION TREE:
- Affects <10% of tests? → Work around it
- Affects 10-30%? → Fix infrastructure, restart Wave 1
- Affects >30%? → Rethink test strategy, consider alternatives

ALTERNATIVES:
- Use `pytest-trio` for async instead of `pytest-asyncio`
- Use `tox` for environment isolation
- Use Docker container for clean test environment
- Use GitHub Actions for CI (different test environment)
```

---

### Scenario C: Coverage Drops Below Baseline (Regression)

**Example**: Wave 2 tests break Wave 1 code, coverage drops 56% → 52%

**Response**:
```
IMMEDIATE:
1. Run coverage report to identify broken modules
2. List which new tests caused regression
3. Check commit history (git bisect)
4. Identify root cause

REMEDIATION:
- IF new test faulty: Fix/rewrite the test
- IF new test broke old code: Revert the breaking change
- IF old code was buggy: Fix the bug, update tests
- IF fixture issue: Isolate fixture side effects

VERIFICATION:
- Run full suite: `pytest tests/ -v`
- Check coverage: `pytest --cov=src/solstein --cov-report=term`
- Verify baseline restored: coverage >= 56%
- Commit with explanation: "fix: revert regression in [module]"
```

---

### Scenario D: Agent Produces Low-Quality Tests

**Examples**:
- Tests too vague (don't actually verify behavior)
- Tests don't fail when code is broken (false positives)
- Tests have bad mocking (test the mock, not the code)

**Response**:
```
QUALITY GATES (per Wave):
1. First 3 tests of agent reviewed by lead
2. IF quality issues found:
   - Document issues (specific line + reason)
   - Ask agent to fix (with examples)
   - Re-review before continuing wave
3. IF quality acceptable:
   - Allow agent to continue wave
   - Spot-check every 5th test
   - Do full review at wave end

CRITERIA FOR "PASSING" TEST:
- [ ] Assertion actually checks behavior (not just "is not None")
- [ ] Test fails when code is broken (run with intentional bug)
- [ ] Mock matches real interface (check actual connector code)
- [ ] No side effects between tests (clean state)
- [ ] Readable and maintainable (clear intent)

IF QUALITY UNACCEPTABLE:
- Reject wave, ask for redo
- Provide examples of good tests
- OR reassign to different agent
```

---

## Success Metrics & Checkpoints

### Pre-Wave Checklist (Required Before Starting)

```
INFRASTRUCTURE:
- [ ] Baseline coverage captured: pytest --cov=src/solstein --cov-report=term
- [ ] All existing tests pass: pytest tests/ -v → all passed
- [ ] Pytest config correct: asyncio_mode="auto" in pyproject.toml
- [ ] Test directory structure ready: tests/unit/infrastructure/ exists
- [ ] Conftest.py fixtures prepared: mock_db_manager, etc.

TEAM:
- [ ] Agent roles assigned (who does what)
- [ ] Communication channel ready (Slack, etc.)
- [ ] Daily standup scheduled (10 min sync)
- [ ] Review process defined (peer review workflow)

DOCUMENTATION:
- [ ] This plan reviewed by team lead
- [ ] Test patterns communicated (5 patterns explained)
- [ ] Quality expectations clear (QA scenario template)
```

### Mid-Wave Checkpoints (Every 4 Hours)

```
EVERY 4 HOURS:
- [ ] 2-3 tasks completed
- [ ] Coverage increased by ~2-3 pp
- [ ] No test failures introduced
- [ ] No blockers
```

### Wave Completion Criteria

```
BEFORE MOVING TO NEXT WAVE:
- [ ] All tasks in wave complete
- [ ] All tests pass: pytest tests/ -v
- [ ] Coverage increased as expected
- [ ] Code review passed
- [ ] Evidence collected: .sisyphus/evidence/task-N-*.txt
```

---

## Rollback & Recovery Plan

### IF Something Goes Wrong Mid-Execution

**Scenario 1: Test Fails, Can't Fix Quickly**

```bash
# Option 1: Isolate the test
pytest tests/unit/infrastructure/test_github_refresh.py --tb=short

# Option 2: Mark test as expected failure
@pytest.mark.xfail(reason="Known issue with mock")
def test_something():
    pass

# Option 3: Skip test and file issue for later
@pytest.mark.skip(reason="Blocker: async context manager not working")
def test_something():
    pass

# Continue work on other tests, come back to this
```

**Scenario 2: Coverage Drops Below Baseline**

```bash
# Revert the problematic test
git checkout tests/unit/infrastructure/test_bad_test.py

# Continue with next test
# File bug: "test_bad_test.py causes regression"
```

**Scenario 3: Need to Stop Execution Early**

```bash
# Commit what you have
git add tests/
git commit -m "chore: complete tests for Wave 1 (partial)"

# Create summary of what's left
echo "Remaining: Wave 2 (Analytics), Wave 3 (API), Wave 4 (Utilities)" > WAVE_STATUS.txt

# Next session can resume from here
```

---

## Cycle 5 Conclusions

✅ **Critical risks identified** (async, mocking, regression)  
✅ **Mitigation strategies** provided for each risk  
✅ **Contingency plans** for 4 key scenarios  
✅ **Quality gates** established (pre-wave, mid-wave, post-wave)  
✅ **Rollback procedures** documented  
✅ **Team coordination** process defined  

**The plan is now BULLETPROOF**:
- Identifies what can go wrong
- Has fixes ready for each risk
- Knows how to handle blockers
- Maintains quality throughout
- Can recover from failures

---

## Summary: 5 Cycles Complete

| Cycle | Deliverable | Status |
|-------|-------------|--------|
| 1 | Current state assessment (70 untested modules) | ✅ COMPLETE |
| 2 | Task breakdown (82 tasks, 95 hours) | ✅ COMPLETE |
| 3 | Execution waves (5 waves, parallelization strategy) | ✅ COMPLETE |
| 4 | Acceptance criteria & QA scenarios (5 patterns) | ✅ COMPLETE |
| 5 | Risk mitigation & contingency (bulletproof plan) | ✅ COMPLETE |

**READY FOR FINAL PLAN GENERATION** ✅

