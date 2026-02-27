# Execution Contingency Guide: What To Do When Things Break

**Date**: Feb 26, 2026  
**Status**: READY FOR EXECUTION  
**Purpose**: Quick reference for common issues during Wave 1-5 execution

---

## 🚨 CRITICAL BLOCKERS (STOP & FIX IMMEDIATELY)

### Blocker 1: "Unknown pytest.mark.asyncio" Error

**Symptom**:
```
PytestUnknownMarkWarning: Unknown pytest.mark.asyncio - is this a typo?
```

**Root Cause**: `asyncio_mode = "auto"` not in `pyproject.toml`

**IMMEDIATE FIX** (5 minutes):
```toml
# File: pyproject.toml [tool.pytest.ini_options]
asyncio_mode = "auto"  # ← ADD THIS
```

**Verify Fix**:
```bash
pytest tests/unit/infrastructure/test_github_refresh.py -v
# Should run without warnings
```

---

### Blocker 2: "ModuleNotFoundError: No module named 'pytest_asyncio'"

**Symptom**:
```
ModuleNotFoundError: No module named 'pytest_asyncio'
```

**Root Cause**: Package not installed

**IMMEDIATE FIX** (2 minutes):
```bash
uv pip install pytest-asyncio
# or
pip install pytest-asyncio
```

**Verify Fix**:
```bash
python -c "import pytest_asyncio; print('OK')"
```

---

### Blocker 3: Database Connection Issues

**Symptom**:
```
sqlalchemy.exc.OperationalError: could not connect to database
```

**Root Cause**: Test database not configured

**IMMEDIATE FIX**:
```python
# In conftest.py - use in-memory SQLite for tests
@pytest.fixture
async def test_db_engine():
    """In-memory test database."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()
```

---

## ⚠️ HIGH-SEVERITY ISSUES (Fix within 1 hour)

### Issue 1: Test Fails with "TimeoutError"

**Symptom**: Test hangs for 30+ seconds then times out

**Probable Cause**: 
- Async function not properly awaited
- Mock not returning AsyncMock (returns MagicMock instead)
- Database session not closed

**Quick Fix**:
```python
# ❌ WRONG
connector.get_data = MagicMock(return_value=[1, 2, 3])
await connector.get_data()  # Wrong! MagicMock not awaitable

# ✅ CORRECT
connector.get_data = AsyncMock(return_value=[1, 2, 3])
result = await connector.get_data()  # Works
```

---

### Issue 2: "RuntimeError: Event loop is closed"

**Symptom**:
```
RuntimeError: Event loop is closed
```

**Probable Cause**: Async fixture not properly scoped

**Quick Fix**:
```python
# Use autouse fixture to manage event loop
@pytest.fixture(autouse=True)
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
```

---

### Issue 3: Coverage Drops (Regression)

**Symptom**: Coverage was 56%, now 52% after new tests

**Probable Cause**: New tests broke old code, or test fixture modified shared state

**Recovery Steps**:

1. **Identify which test caused drop** (5 min):
```bash
git diff HEAD~1 tests/
# See which tests were added

# Run only new tests
pytest tests/unit/infrastructure/test_github_refresh.py -v
```

2. **Run full suite to see failures** (10 min):
```bash
pytest tests/ -v --tb=short
# Shows which tests fail
```

3. **Fix the test** (30 min):
```bash
# Option A: Fix the test
# Option B: Revert the test
git checkout tests/unit/infrastructure/test_github_refresh.py

# Option C: Fix the code it exposed
# (If test revealed a real bug)
```

4. **Verify coverage restored**:
```bash
pytest tests/ --cov=src/solstein --cov-report=term
# Should be back to 56%+
```

---

## 🔧 MEDIUM-SEVERITY ISSUES (Fix within 4 hours)

### Issue 4: "AssertionError: Expected 200, got 400"

**Symptom**: API test fails with unexpected status code

**Debug Steps**:
```python
# Print response details
response = client.get("/api/endpoint")
print(f"Status: {response.status_code}")
print(f"Body: {response.json()}")
print(f"Headers: {response.headers}")

# Check what went wrong
if response.status_code == 400:
    error = response.json()
    print(f"Error: {error['detail']}")
```

**Common Causes**:
- Missing required parameter
- Invalid data type
- Database not seeded
- Dependency not mocked

---

### Issue 5: "pytest fixture 'mock_db_manager' not found"

**Symptom**:
```
fixture 'mock_db_manager' not found
```

**Root Cause**: conftest.py fixture not defined or import issue

**Fix**:
```python
# Check conftest.py exists and has fixture
cat tests/conftest.py | grep "def mock_db_manager"

# If missing, add it:
@pytest.fixture
def mock_db_manager():
    return MagicMock(spec=DatabaseManager)
```

---

### Issue 6: "Type Error: 'MagicMock' object is not awaitable"

**Symptom**:
```
TypeError: object MagicMock can't be used in 'await' expression
```

**Root Cause**: Used MagicMock instead of AsyncMock for async function

**Fix**:
```python
# ❌ WRONG
mock_func = MagicMock(return_value="result")
result = await mock_func()  # TypeError

# ✅ CORRECT
mock_func = AsyncMock(return_value="result")
result = await mock_func()  # Works
```

---

## 📋 COMMON PATTERNS FOR FIX

### Pattern A: Isolated Test Failure

```bash
# Run just the failing test
pytest tests/unit/infrastructure/test_github_refresh.py::TestGitHubRefreshConnector::test_initialization -v

# Add verbose output
pytest -vvv --tb=long

# See the actual error
# Fix the test
# Re-run
pytest tests/unit/infrastructure/test_github_refresh.py::TestGitHubRefreshConnector::test_initialization -v
```

### Pattern B: Flaky Test (Passes Sometimes, Fails Sometimes)

```bash
# Run test 10 times
for i in {1..10}; do
    pytest tests/unit/infrastructure/test_github_refresh.py::TestGitHubRefreshConnector::test_fetch_facts_success -v
done

# If test fails sometimes:
# - Check for race conditions
# - Check for shared state between tests
# - Verify mock isolation (fresh mock per test)
# - Add pytest.mark.flaky if needed
```

### Pattern C: Coverage Gap Identified

```bash
# Generate HTML coverage report
pytest tests/ --cov=src/solstein --cov-report=html

# Open report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows

# See which lines aren't covered
# Write test to cover them
```

---

## 🛟 ESCALATION PATH (When Stuck)

### Step 1: Check Plan (5 min)
- Read `.sisyphus/plans/solstein-complete-roadmap.md`
- Check task acceptance criteria
- Review QA scenarios from Cycle 4

### Step 2: Check Examples (10 min)
- Look at similar passing tests
- Copy pattern, adapt for current task
- Reference enhanced code examples

### Step 3: Debug (30 min)
- Add print statements / logging
- Run with `-vvv --tb=long` flags
- Check mock setup (AsyncMock vs MagicMock)
- Verify conftest.py fixtures loaded

### Step 4: Consult Cycle 5 (15 min)
- Read `.sisyphus/drafts/planning-cycle-5-risk-mitigation.md`
- Find similar risk/issue
- Apply suggested mitigation

### Step 5: Last Resort (30 min)
- Mark test with `@pytest.mark.skip(reason="...")`
- Document issue in `.sisyphus/evidence/BLOCKERS.txt`
- Move to next task
- File bug: "Test [name] blocked by [issue]"
- Continue with independent tasks

---

## ✅ VERIFICATION CHECKPOINTS (After Each Task)

### Checkpoint 1: Task Complete
```bash
# Run the new test
pytest tests/unit/infrastructure/test_github_refresh.py -v

# MUST PASS: All tests pass
# MUST PASS: No warnings/errors in output
# MUST PASS: Coverage increases
```

### Checkpoint 2: No Regression
```bash
# Run full suite
pytest tests/ -v

# Check no previously passing tests now fail
# Check coverage didn't drop
```

### Checkpoint 3: Evidence Collected
```bash
# Create evidence file
cat > .sisyphus/evidence/task-1-1-1-github-refresh.txt << 'EOF'
Task: 1.1.1 Test GitHubRefreshConnector
Status: COMPLETE
Date: 2026-02-26

Evidence:
- pytest output: [copy from terminal]
- Coverage gain: +1 pp (56% → 57%)
- Files created: tests/unit/infrastructure/test_github_refresh.py
- Lines covered: 221 (100% of github_refresh.py)

Acceptance Criteria Met:
- [x] test_initialization passes
- [x] test_fetch_facts_success passes
- [x] test_api_failure passes
- [x] test_delta_detection passes
- [x] Coverage >= 85%

EOF
```

---

## 📊 DECISION TREE: What To Do

```
TEST FAILS
├─ Is it a known issue from Cycle 5?
│  └─ YES → Apply mitigation from this guide
└─ Is it a test problem?
   ├─ YES → Fix test, re-run
   └─ Is it a code problem?
      ├─ YES → Fix code, re-run
      └─ Mark SKIP, document, move to next task

COVERAGE DROPS
├─ Is it > 2 percentage points?
│  ├─ YES → Find cause (git diff), revert/fix
│  └─ Is it 1-2 pp?
│     └─ Accept it, continue (variance is normal)

TEST HANGS
├─ Is it timeout?
│  ├─ YES → Check mock is AsyncMock
│  └─ Set explicit timeout
├─ Is it deadlock?
│  └─ Check for circular awaits

MOCK ISN'T WORKING
├─ Check Mock type: MagicMock vs AsyncMock
├─ Check return_value vs side_effect
├─ Check fixture scope (function vs session)
└─ Verify conftest.py loaded
```

---

## 🎯 SUCCESS METRICS (Per Task)

**Task is DONE when**:
- ✅ All QA scenarios pass (4-5 per task)
- ✅ Coverage increases by expected amount
- ✅ No regression in other tests
- ✅ Evidence documented to `.sisyphus/evidence/task-N-*`
- ✅ Code matches pattern from enhancement guide
- ✅ No warnings/errors in pytest output

**Wave is DONE when**:
- ✅ All tasks complete
- ✅ Coverage increases by expected amount (e.g., +17 pp for Wave 1)
- ✅ All evidence collected
- ✅ Ready to move to next wave

---

## 📞 QUICK REFERENCE

| Issue | Fix | Time |
|-------|-----|------|
| asyncio_mode error | Add to pyproject.toml | 5 min |
| ModuleNotFoundError | `uv pip install pytest-asyncio` | 2 min |
| TimeoutError | Check AsyncMock vs MagicMock | 10 min |
| Coverage drops | git diff, identify cause | 30 min |
| Test fails | Run with `-vvv --tb=long` | 15 min |
| Fixture not found | Check conftest.py | 5 min |
| Type errors | Check async/await patterns | 20 min |

---

## 🚀 KEEP GOING!

**Remember**:
- Each task is independent (can restart if needed)
- Patterns are reusable (copy-paste from enhancement guide)
- Evidence is tracked (helps diagnose future issues)
- No task is blocked for > 1 hour (move to next if stuck)
- Coverage increases ~1-2% per task (visible progress)

You got this! 💪

