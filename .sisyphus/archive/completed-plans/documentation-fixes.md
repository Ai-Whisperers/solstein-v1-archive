# Documentation Fixes Work Plan

## TL;DR

> **Quick Summary**: Fix 7 documentation accuracy issues identified in critical audit (62% failing). 3 critical code/doc bugs, 2 moderate doc gaps, 2 minor enhancements. All issues have exact remediation steps identified.
>
> **Deliverables**: 
> - Fixed `worker_tasks.py` (Dead Letter Queue timestamp)
> - Updated 6 documentation files with accurate technical content
> - Added comprehensive Redis setup guide
> - Verified all code examples match actual implementation
>
> **Estimated Effort**: Medium (60-90 minutes)
> **Parallel Execution**: YES - 4 waves, max 4 tasks in Wave 2 & 3
> **Critical Path**: Task 1 → Task 2-4 (parallel) → Task 5-6 (parallel) → Task 7-8 (final)

---

## Context

### Critical Audit Findings

The documentation created in the previous session contains **7 significant accuracy issues**:

**Critical Issues** (production-blocking):
1. **Dead Letter Queue Bug**: Timestamp set to `logger.info()` return value = `None` (worker_tasks.py:117)
2. **Rate Limiter Defaults**: Doc claims 100/min, code defaults to 60/min (rate-limiting.md)
3. **Redis Never Initialized**: Claims Redis-backed, actually always uses memory fallback (security_hardening.py:396)

**Moderate Issues** (misleading/incomplete):
4. **Health Check Misdescription**: `/ready` doesn't validate data sources but docs claim full readiness check
5. **Async Patterns Incomplete**: Missing context on performance cost and timeout strategies

**Minor Issues** (nice-to-have):
6. **Redis Setup Missing**: No docs on starting Redis or configuring URLs
7. **Exponential Backoff**: ✅ Actually correct (no changes needed)

### Full Audit Report

See: `.sisyphus/audits/CRITICAL_DOCUMENTATION_AUDIT.md` (605 lines)
- Exact line numbers and file paths
- Side-by-side code vs documentation comparison
- Developer impact analysis
- Specific fixes for each issue

---

## Work Objectives

### Core Objective
Correct all documentation inaccuracies to match actual Solstein codebase, ensuring developers can follow guides without encountering bugs or confusion.

### Concrete Deliverables
- ✅ Fixed `src/solstein/worker_tasks.py` (Dead Letter Queue timestamp)
- ✅ Updated `docs/guides/rate-limiting.md` (default values clarified)
- ✅ Updated `docs/guides/health-checks.md` (readiness probe behavior corrected)
- ✅ Updated `docs/guides/async-patterns.md` (added context on costs/tradeoffs)
- ✅ Updated `docs/guides/developer.md` (added Redis setup section)
- ✅ Updated `docs/phases/phase-13.md` (DLQ section corrected)
- ✅ Verified all code examples match actual implementation
- ✅ All tests still passing (123/123)

### Definition of Done
- [ ] Dead Letter Queue timestamp bug fixed
- [ ] All 6 documentation files updated with accurate technical content
- [ ] No files reference incorrect defaults or misleading patterns
- [ ] All code examples are real, executable, and match source
- [ ] Cross-references between docs are verified
- [ ] pytest confirms 123 tests still passing
- [ ] No breaking changes to existing functionality

### Must Have
- ✅ Fix Dead Letter Queue bug (critical code issue)
- ✅ Clarify rate limiter defaults (60 vs 100 per-minute)
- ✅ Document or acknowledge Redis initialization gap
- ✅ Explain health check endpoint behavior accurately
- ✅ Add context to async patterns (performance implications)
- ✅ Document Redis setup for developers
- ✅ All changes pass tests and linting

### Must NOT Have (Guardrails)
- ❌ Do NOT change production code beyond bug fixes
- ❌ Do NOT simplify complex patterns (keep technical depth)
- ❌ Do NOT invent new features or patterns (document what exists)
- ❌ Do NOT alter API contracts or signatures
- ❌ Do NOT break any existing tests (123/123 must pass)
- ❌ Do NOT remove existing documentation sections (only fix/expand)

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: YES (pytest with 123 tests)
- **Automated tests**: Tests-after (code change is minimal, focused documentation fixes)
- **Framework**: pytest
- **QA approach**: Agent-executed verification of each fix via:
  1. Read actual code to verify fix is correct
  2. Read updated documentation to verify accuracy
  3. Compare side-by-side to ensure alignment
  4. Run pytest to ensure no test breakage

### QA Policy

Every task includes agent-executed verification scenarios:
- **Code fixes**: Verify syntax is correct, change matches issue description, surrounding code unchanged
- **Documentation updates**: Verify accuracy against actual code, examples are real, cross-references work
- **Integration**: Verify no side effects, tests still pass

Evidence saved to `.sisyphus/evidence/task-{N}-{scenario}.txt`

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately — code bug fix):
└── Task 1: Fix Dead Letter Queue timestamp bug [critical, blocks Wave 2]

Wave 2 (After Wave 1 — critical doc fixes, MAX PARALLEL):
├── Task 2: Fix rate-limiting.md (default values) [unspecified-high]
├── Task 3: Fix phase-13.md (DLQ section) [unspecified-high]
├── Task 4: Fix developer.md (add Redis setup) [unspecified-high]
└── Task 5: Fix security_hardening.py documentation (clarify Redis usage) [quick]

Wave 3 (After Wave 1 — moderate doc fixes, MAX PARALLEL):
├── Task 6: Fix health-checks.md (readiness behavior) [unspecified-high]
└── Task 7: Fix async-patterns.md (add context/tradeoffs) [unspecified-high]

Wave 4 (After all — final verification):
├── Task 8: Cross-reference verification [deep]
├── Task 9: Code examples verification [unspecified-high]
└── Task 10: Final test run and validation [quick]
```

### Dependency Matrix

- **1**: — → 2, 3, 4, 5, 6, 7 (code fix unblocks all docs)
- **2**: 1 → 8, 10 (rate-limiting docs)
- **3**: 1 → 8, 10 (phase-13 docs)
- **4**: 1 → 8, 10 (developer guide)
- **5**: 1 → 8, 10 (security_hardening.py)
- **6**: 1 → 8, 10 (health-checks docs)
- **7**: 1 → 8, 10 (async-patterns docs)
- **8**: 2, 3, 4, 6, 7 → 10 (cross-ref verification)
- **9**: 2, 3, 4, 6, 7 → 10 (code example verification)
- **10**: 8, 9 → COMPLETE (final validation)

### Agent Dispatch Summary

- **Wave 1**: Task 1 → `quick` (1-line fix)
- **Wave 2**: Tasks 2-5 → `unspecified-high` (doc updates), Task 5 → `quick` (comments)
- **Wave 3**: Tasks 6-7 → `unspecified-high` (substantial doc rewrites)
- **Wave 4**: Task 8 → `deep` (comprehensive verification), Task 9 → `unspecified-high` (example checks), Task 10 → `quick` (test run)

---

## TODOs

### Task 1: Fix Dead Letter Queue Timestamp Bug

**What to do**:
- Read `src/solstein/worker_tasks.py` lines 103-125 (DeadLetterQueue class)
- Identify that line 117 sets `"timestamp": logger.info(...)` which returns None
- Replace with actual datetime: `"timestamp": datetime.now(timezone.utc)`
- Add missing import: `from datetime import datetime, timezone`
- Verify fix doesn't break surrounding code

**Must NOT do**:
- Don't change the record_failure method signature
- Don't alter the failed_jobs storage mechanism
- Don't add new features beyond fixing the timestamp

**Recommended Agent Profile**:
> Select category + skills based on task domain
- **Category**: `quick`
  - Reason: Single-line fix, straightforward code change, no complex logic
- **Skills**: None required
  - This is a simple syntax/logic fix

**Parallelization**:
- **Can Run In Parallel**: YES
- **Parallel Group**: Wave 1 (start immediately)
- **Blocks**: Tasks 2-7 (all docs depend on code being correct)
- **Blocked By**: None (can start immediately)

**References**:

> The executor has NO context from the interview. References are their ONLY guide.

**Pattern References** (code patterns to follow):
- `src/solstein/worker_tasks.py:1-30` — Import style and module header pattern (datetime usage)

**Code References** (where the bug is):
- `src/solstein/worker_tasks.py:103-125` — DeadLetterQueue class with timestamp bug
- `src/solstein/worker_tasks.py:178` — Where record_failure is called

**External References** (Python docs):
- `https://docs.python.org/3/library/datetime.html#datetime.datetime.now` — datetime.now() usage

**WHY Each Reference Matters**:
- Pattern reference shows import style for consistency
- Code references pinpoint exact bug location and usage
- External reference shows correct datetime API usage

**Acceptance Criteria**:

> **AGENT-EXECUTABLE VERIFICATION ONLY** — No human action permitted.

- [ ] `src/solstein/worker_tasks.py` modified: datetime import added (lines 1-30)
- [ ] `src/solstein/worker_tasks.py` modified: line 117 uses `datetime.now(timezone.utc)` not `logger.info()`
- [ ] Syntax is valid: `python -c "import src.solstein.worker_tasks"` succeeds
- [ ] No surrounding code changed: `record_failure()` method signature unchanged
- [ ] pytest run: `pytest tests/ -v` → 123/123 passing (no regressions)

**QA Scenarios**:

```
Scenario: Timestamp is correctly set to datetime object
  Tool: Bash (grep + read file)
  Preconditions: worker_tasks.py line 117 currently broken
  Steps:
    1. Read src/solstein/worker_tasks.py lines 110-125
    2. Verify line 117 contains: "timestamp": datetime.now(timezone.utc),
    3. Verify datetime import exists at top of file
    4. Verify no logger.info() on timestamp line
  Expected Result: timestamp field uses datetime.now(), not logger.info()
  Failure Indicators: logger.info still present, datetime not imported, or syntax error
  Evidence: .sisyphus/evidence/task-1-timestamp-fix.txt

Scenario: Code still compiles and tests pass
  Tool: Bash (python syntax check + pytest)
  Preconditions: Code change applied
  Steps:
    1. Run: python -c "import sys; import src.solstein.worker_tasks; print('OK')"
    2. Run: cd /home/ai-whisperers/solstein && pytest tests/ --tb=short -q
  Expected Result: No syntax errors, 123/123 tests pass
  Failure Indicators: SyntaxError, ImportError, or test failures
  Evidence: .sisyphus/evidence/task-1-tests-pass.txt
```

**Commit**: YES
- Message: `fix(worker_tasks): correct Dead Letter Queue timestamp to use datetime.now() instead of logger.info()  return value`
- Files: `src/solstein/worker_tasks.py`
- Pre-commit: `pytest tests/ -q`

---

### Task 2: Fix Rate Limiter Documentation (Defaults Mismatch)

**What to do**:
- Read `docs/guides/rate-limiting.md` section "Overview" (lines 15-24)
- Current claim: "Default: 100 requests per minute per client"
- Research the actual defaults:
  - Class default (`RedisRateLimiter.__init__`): 60/min
  - Global instance (`rate_limiter` init): 100/min
- Rewrite section to clarify the discrepancy
- Add subsection with code example showing when to use each default
- Verify all examples are accurate

**Must NOT do**:
- Don't change the implementation (just document what exists)
- Don't remove existing sections
- Don't simplify the explanation (keep technical depth)

**Recommended Agent Profile**:
- **Category**: `unspecified-high`
  - Reason: Requires reading code, understanding discrepancy, writing clear technical documentation
- **Skills**: None required
  - Documentation writing + code understanding

**Parallelization**:
- **Can Run In Parallel**: YES (with Task 3-5)
- **Parallel Group**: Wave 2 (after code fix in Wave 1)
- **Blocks**: Task 8 (cross-reference verification)
- **Blocked By**: Task 1 (needs code fix first for context)

**References**:

**Code References** (source of truth):
- `src/solstein/data/security_hardening.py:207` — RedisRateLimiter default parameter
- `src/solstein/data/security_hardening.py:266` — SimpleRateLimiter default parameter
- `src/solstein/data/security_hardening.py:396` — Global rate_limiter instance init

**Documentation References** (what needs fixing):
- `docs/guides/rate-limiting.md:1-100` — Overview section with incorrect default claim

**WHY Each Reference Matters**:
- Code refs show the actual default values (60 vs 100)
- Doc ref shows what claim needs to be corrected

**Acceptance Criteria**:

- [ ] `docs/guides/rate-limiting.md` section "Overview" updated with accurate defaults
- [ ] Section clarifies: class default (60/min) vs global instance (100/min)
- [ ] Includes code example showing correct instantiation
- [ ] All claims about defaults match actual code
- [ ] No breaking changes to existing sections
- [ ] Markdown is valid (no syntax errors)

**QA Scenarios**:

```
Scenario: Documentation accurately describes both default values
  Tool: Read file + comparison
  Preconditions: Updated rate-limiting.md exists
  Steps:
    1. Read docs/guides/rate-limiting.md "Overview" section
    2. Search for "60" and "100" mentions related to defaults
    3. Read src/solstein/data/security_hardening.py lines 207, 266, 396
    4. Verify documentation mentions both values correctly
  Expected Result: Doc explains class default (60/min), global instance (100/min), how to use each
  Failure Indicators: Only one default mentioned, or values don't match code
  Evidence: .sisyphus/evidence/task-2-defaults-accuracy.txt

Scenario: Code examples match actual implementation
  Tool: Read file + comparison
  Preconditions: Code examples in documentation
  Steps:
    1. Read all code examples in updated rate-limiting.md
    2. Compare each example against actual code in security_hardening.py
    3. Verify imports, method names, parameter names match
  Expected Result: All examples are real, executable code from codebase
  Failure Indicators: Examples use wrong class name, method, or parameter
  Evidence: .sisyphus/evidence/task-2-code-examples.txt
```

**Commit**: YES
- Message: `docs(rate-limiting): clarify default request limits (60/min class vs 100/min instance)`
- Files: `docs/guides/rate-limiting.md`
- Pre-commit: `grep -n "100\|60" docs/guides/rate-limiting.md`

---

### Task 3: Fix Phase 13 Documentation (Dead Letter Queue Section)

**What to do**:
- Read `docs/phases/phase-13.md` Dead Letter Queue section
- Find all claims about DLQ that reference timestamp tracking
- Update to clarify that DLQ was implemented but had a timestamp bug (now fixed)
- Add note that timestamp field is now correctly set to datetime
- Verify this aligns with the fixed code from Task 1
- Check that other Phase 13.4 claims are accurate (exponential backoff, retry logging)

**Must NOT do**:
- Don't claim features that don't exist
- Don't remove other Phase 13 sections
- Don't add new features beyond documenting what's implemented

**Recommended Agent Profile**:
- **Category**: `unspecified-high`
  - Reason: Requires understanding the bug, documenting the fix, ensuring accuracy
- **Skills**: None required

**Parallelization**:
- **Can Run In Parallel**: YES (with Task 2, 4-5)
- **Parallel Group**: Wave 2
- **Blocks**: Task 8 (cross-reference verification)
- **Blocked By**: Task 1 (needs code fix for context)

**References**:

**Code References**:
- `src/solstein/worker_tasks.py:103-125` — Fixed DeadLetterQueue class
- `src/solstein/worker_tasks.py:133-180` — Retry logic with DLQ integration

**Documentation References**:
- `docs/phases/phase-13.md` — Phase 13 overview (find DLQ section)

**WHY Each Reference Matters**:
- Code refs show what DLQ actually does (after fix)
- Doc ref shows what needs updating

**Acceptance Criteria**:

- [ ] `docs/phases/phase-13.md` DLQ section updated with accurate timestamp handling
- [ ] Documentation reflects the bug fix (datetime.now() instead of logger.info())
- [ ] All other Phase 13.4 claims (exponential backoff, retry logging) verified against code
- [ ] No breaking changes to other sections

**QA Scenarios**:

```
Scenario: DLQ documentation matches fixed implementation
  Tool: Read file + code comparison
  Preconditions: phase-13.md has DLQ section
  Steps:
    1. Read docs/phases/phase-13.md DLQ section
    2. Read fixed src/solstein/worker_tasks.py:103-125
    3. Verify doc describes timestamp as datetime object
    4. Verify doc mentions record_failure() method
    5. Verify doc shows example DLQ entry structure
  Expected Result: Docs accurately describe fixed DLQ with datetime timestamp
  Failure Indicators: Docs still claim logger.info() timestamp, or don't mention fix
  Evidence: .sisyphus/evidence/task-3-dlq-accuracy.txt

Scenario: Exponential backoff claims are verified against code
  Tool: Code comparison
  Preconditions: phase-13.md makes claims about backoff
  Steps:
    1. Read docs/phases/phase-13.md exponential backoff section
    2. Read src/solstein/worker_tasks.py lines 172, 217, 265, etc. (countdown calculations)
    3. Verify formula: 5 * (2 ** self.request.retries)
    4. Verify timing: Attempt 1=5s, 2=10s, 3=20s
  Expected Result: All backoff claims match actual code implementation
  Failure Indicators: Formula or timing don't match actual code
  Evidence: .sisyphus/evidence/task-3-backoff-verify.txt
```

**Commit**: YES
- Message: `docs(phase-13): update Dead Letter Queue section with correct timestamp handling`
- Files: `docs/phases/phase-13.md`
- Pre-commit: `grep -A5 "Dead Letter\|DLQ" docs/phases/phase-13.md`

---

### Task 4: Add Redis Setup Documentation to Developer Guide

**What to do**:
- Read `docs/guides/developer.md` (find installation/setup section)
- Add new subsection: "Redis Dependency & Setup"
- Document:
  - What Redis is used for (Celery broker, result backend, optional for rate limiting)
  - How to start Redis (Docker, Homebrew, from source)
  - Environment variables to configure Redis URL
  - What happens if Redis is unavailable (graceful degradation)
  - How to verify Redis is running
- Verify all commands are accurate and tested
- Ensure tone matches existing guide

**Must NOT do**:
- Don't change existing setup instructions
- Don't require Redis (keep it as dependency but note optional aspects)
- Don't add unrelated sections

**Recommended Agent Profile**:
- **Category**: `unspecified-high`
  - Reason: Documentation writing + technical setup knowledge
- **Skills**: None required

**Parallelization**:
- **Can Run In Parallel**: YES (with Task 2-3, 5)
- **Parallel Group**: Wave 2
- **Blocks**: Task 8 (cross-reference verification)
- **Blocked By**: Task 1 (needs code understanding for context)

**References**:

**Code References**:
- `src/solstein/celery_config.py:28-29` — Redis broker/backend URL defaults
- `src/solstein/data/security_hardening.py:396` — Rate limiter with optional Redis

**Documentation References**:
- `docs/guides/developer.md` — Where to add Redis section

**External References**:
- Redis official docs: https://redis.io/docs/getting-started/
- Docker Redis: https://hub.docker.com/_/redis

**WHY Each Reference Matters**:
- Code refs show actual Redis configuration used
- Doc ref shows where to place new section
- External refs provide authoritative setup instructions

**Acceptance Criteria**:

- [ ] `docs/guides/developer.md` has new "Redis Dependency" section
- [ ] Section covers Docker, Homebrew, and source installation options
- [ ] Environment variables documented (CELERY_BROKER_URL, CELERY_RESULT_BACKEND)
- [ ] Includes verification command (redis-cli ping)
- [ ] Tone matches existing guide
- [ ] All commands are accurate

**QA Scenarios**:

```
Scenario: Docker installation instructions are correct
  Tool: Bash (docker command verification)
  Preconditions: Docker is installed on system
  Steps:
    1. Read docs/guides/developer.md Redis section
    2. Extract Docker command exactly as documented
    3. Run: docker ps --filter "image=redis*" (check if any redis running)
    4. Verify command format is correct: docker run -d -p 6379:6379 redis:7-alpine
  Expected Result: Docker command syntax is valid, uses correct Redis image
  Failure Indicators: Invalid docker syntax or wrong image name
  Evidence: .sisyphus/evidence/task-4-docker-syntax.txt

Scenario: Environment variable names match actual config
  Tool: Code + doc comparison
  Preconditions: Developer guide has env var section
  Steps:
    1. Read docs/guides/developer.md environment variables listed
    2. Read src/solstein/celery_config.py lines 28-29
    3. Search for "CELERY_BROKER_URL" and "CELERY_RESULT_BACKEND" in config
    4. Verify variable names in docs match code exactly
  Expected Result: All env var names match actual config code
  Failure Indicators: Wrong variable name or missing variables
  Evidence: .sisyphus/evidence/task-4-env-vars.txt
```

**Commit**: YES
- Message: `docs(developer): add Redis setup and configuration guide`
- Files: `docs/guides/developer.md`
- Pre-commit: `grep -n "Redis\|redis" docs/guides/developer.md | head -10`

---

### Task 5: Add Documentation Comments to security_hardening.py

**What to do**:
- Read `src/solstein/data/security_hardening.py` lines 204-250 (RedisRateLimiter class)
- Add docstring comments explaining:
  - Redis is optional (redis_client parameter defaults to None)
  - When redis_client=None, memory fallback is used automatically
  - Memory fallback is per-server (not distributed)
  - For distributed rate limiting, Redis client must be provided
- Don't change code logic, just add clarifying comments
- Ensure comments explain the design decision

**Must NOT do**:
- Don't change the code logic
- Don't modify method signatures
- Don't add new features

**Recommended Agent Profile**:
- **Category**: `quick`
  - Reason: Only adding documentation comments, no code logic changes
- **Skills**: None required

**Parallelization**:
- **Can Run In Parallel**: YES (with Task 2-4)
- **Parallel Group**: Wave 2
- **Blocks**: Task 8 (cross-reference verification)
- **Blocked By**: Task 1 (context from audit)

**References**:

**Code References**:
- `src/solstein/data/security_hardening.py:204-250` — RedisRateLimiter class
- `src/solstein/data/security_hardening.py:263-305` — SimpleRateLimiter class

**WHY Each Reference Matters**:
- Shows the classes that need clarifying comments

**Acceptance Criteria**:

- [ ] RedisRateLimiter class has docstring explaining optional Redis
- [ ] Comments explain memory fallback behavior
- [ ] Comments mention distributed vs per-server implications
- [ ] No code logic changed
- [ ] Syntax is valid Python
- [ ] pytest still passes

**QA Scenarios**:

```
Scenario: Docstrings clearly explain Redis optionality
  Tool: Read file
  Preconditions: Comments added to security_hardening.py
  Steps:
    1. Read src/solstein/data/security_hardening.py lines 204-220
    2. Check for docstring explaining redis_client parameter
    3. Verify docstring mentions None default and fallback behavior
  Expected Result: Docstring explains redis_client is optional, fallback behavior clear
  Failure Indicators: No docstring, or docstring doesn't mention optionality
  Evidence: .sisyphus/evidence/task-5-docstrings.txt

Scenario: No code logic changed
  Tool: Bash (git diff)
  Preconditions: Comments added
  Steps:
    1. Run: git diff src/solstein/data/security_hardening.py
    2. Verify changes are only comment/docstring additions
    3. Verify method implementations unchanged
  Expected Result: Only docstring/comment lines changed, no logic altered
  Failure Indicators: Code logic modifications present
  Evidence: .sisyphus/evidence/task-5-git-diff.txt
```

**Commit**: YES
- Message: `docs(security_hardening): clarify Redis optionality in rate limiter docstrings`
- Files: `src/solstein/data/security_hardening.py`
- Pre-commit: `python -c "import src.solstein.data.security_hardening; print('OK')"`

---

### Task 6: Fix Health Checks Documentation (Readiness Behavior)

**What to do**:
- Read `docs/guides/health-checks.md` section "Readiness Probe" (lines 213-255 or similar)
- Find claim: "Is ready for traffic? ... all critical components operational"
- Research actual behavior in `src/solstein/api/routers/enrichment.py` (health check implementation)
- Discover: `/ready` checks only DB + cache, NOT data sources
- Rewrite section to accurately describe what readiness actually validates
- Add explanation: Readiness = infrastructure ready, but data sources may be unavailable
- Add subsection explaining how to check data source health separately
- Provide clear guidance on when each endpoint should be used

**Must NOT do**:
- Don't change the actual endpoint behavior (only document correctly)
- Don't remove existing sections
- Don't claim readiness validates more than it does

**Recommended Agent Profile**:
- **Category**: `unspecified-high`
  - Reason: Requires understanding API behavior, rewriting docs for accuracy
- **Skills**: None required

**Parallelization**:
- **Can Run In Parallel**: YES (with Task 7)
- **Parallel Group**: Wave 3
- **Blocks**: Task 8 (cross-reference verification)
- **Blocked By**: Task 1 (context)

**References**:

**Code References** (source of truth):
- `src/solstein/api/routers/enrichment.py:213-255` — Actual /ready endpoint implementation
- `src/solstein/api/routers/enrichment.py:238-240` — Readiness logic (DB + cache check)
- `src/solstein/api/routers/enrichment.py:101-138` — Individual health check functions

**Documentation References**:
- `docs/guides/health-checks.md` — Readiness section (needs correction)

**WHY Each Reference Matters**:
- Code refs show exact readiness logic to document accurately
- Doc ref shows what needs fixing

**Acceptance Criteria**:

- [ ] `docs/guides/health-checks.md` "Readiness Probe" section updated
- [ ] Documentation clearly states readiness checks DB + cache only
- [ ] Section notes that data sources are NOT part of readiness
- [ ] Includes guidance on checking data source health separately
- [ ] Explains developer use case (load balancer readiness gates)
- [ ] Markdown is valid

**QA Scenarios**:

```
Scenario: Readiness documentation accurately describes endpoint behavior
  Tool: Code + doc comparison
  Preconditions: health-checks.md has been updated
  Steps:
    1. Read docs/guides/health-checks.md readiness section
    2. Read src/solstein/api/routers/enrichment.py lines 238-240
    3. Extract what endpoints are actually checked in readiness
    4. Verify doc mentions DB and cache, but NOT sources
  Expected Result: Doc accurately lists DB + cache as readiness components, not sources
  Failure Indicators: Doc claims sources are checked in readiness
  Evidence: .sisyphus/evidence/task-6-readiness-accuracy.txt

Scenario: Guidance explains load balancer use case
  Tool: Read file
  Preconditions: Updated health-checks.md
  Steps:
    1. Read readiness section completely
    2. Check for explanation of why readiness matters to load balancers
    3. Verify section explains partial availability (DB up, sources down) scenario
  Expected Result: Docs explain practical use (load balancer traffic routing)
  Failure Indicators: Only technical description, no practical guidance
  Evidence: .sisyphus/evidence/task-6-use-case.txt
```

**Commit**: YES
- Message: `docs(health-checks): clarify readiness probe validates infrastructure (DB+cache), not data sources`
- Files: `docs/guides/health-checks.md`
- Pre-commit: `grep -i "readiness\|ready" docs/guides/health-checks.md | wc -l`

---

### Task 7: Enhance Async Patterns Documentation

**What to do**:
- Read `docs/guides/async-patterns.md` (entire file)
- Find section on `asyncio.run()` pattern
- Current state: Shows the pattern but lacks context
- Add new subsection: "Performance Implications & Tradeoffs"
  - Explain that `asyncio.run()` creates new event loop per execution (expensive)
  - Connection pooling across task runs is difficult
  - Adds complexity to error handling
- Add new subsection: "Soft vs Hard Celery Timeouts"
  - Explain difference between task_soft_time_limit and task_time_limit
  - Show example of catching SoftTimeLimitExceeded
  - Demonstrate graceful shutdown pattern
- Add future direction: async Celery (Celery 5.1+) as alternative
- Keep all existing sections, only expand with new context

**Must NOT do**:
- Don't remove existing patterns or examples
- Don't claim Celery 5.1+ features are available (note as future)
- Don't suggest breaking changes

**Recommended Agent Profile**:
- **Category**: `unspecified-high`
  - Reason: Requires deep understanding of async/Celery, writing comprehensive guide
- **Skills**: None required

**Parallelization**:
- **Can Run In Parallel**: YES (with Task 6)
- **Parallel Group**: Wave 3
- **Blocks**: Task 8 (cross-reference verification)
- **Blocked By**: Task 1 (context)

**References**:

**Code References** (patterns to document):
- `src/solstein/worker_tasks.py:133-180` — Actual asyncio.run() usage in Celery task
- `src/solstein/worker_tasks.py:144-150` — Example of nested async code
- `src/solstein/celery_config.py:43-44` — Soft vs hard timeout config

**Documentation References**:
- `docs/guides/async-patterns.md` — Where to add new sections

**External References**:
- Celery docs: https://docs.celeryproject.io/en/stable/userguide/tasks.html#time-limits
- asyncio docs: https://docs.python.org/3/library/asyncio-task.html#running-tasks

**WHY Each Reference Matters**:
- Code refs show actual patterns used in production
- Doc ref shows where to expand
- External refs provide authoritative context

**Acceptance Criteria**:

- [ ] `docs/guides/async-patterns.md` has new "Performance Implications" section
- [ ] Section explains asyncio.run() cost and limitations
- [ ] New "Soft vs Hard Timeouts" section added with examples
- [ ] Example code shows SoftTimeLimitExceeded catching
- [ ] Future direction (async Celery) mentioned but not suggested
- [ ] All examples are real code from codebase
- [ ] Markdown is valid

**QA Scenarios**:

```
Scenario: Performance implications section is comprehensive
  Tool: Read file
  Preconditions: async-patterns.md updated
  Steps:
    1. Read async-patterns.md "Performance Implications" section
    2. Check for explanation of event loop creation cost
    3. Verify section mentions connection pooling difficulty
    4. Check for mention of error handling complexity
  Expected Result: All 3 implications documented (event loop, pooling, error handling)
  Failure Indicators: Missing any of the 3 implications
  Evidence: .sisyphus/evidence/task-7-perf-implications.txt

Scenario: Timeout examples match actual Celery config
  Tool: Code + doc comparison
  Preconditions: Timeout section added
  Steps:
    1. Read docs/guides/async-patterns.md timeout section
    2. Read src/solstein/celery_config.py lines 43-44
    3. Extract timeout values from config (30s hard, 25s soft)
    4. Verify examples use correct values
  Expected Result: Documentation examples use actual config values (30s/25s)
  Failure Indicators: Examples use different timeout values than actual config
  Evidence: .sisyphus/evidence/task-7-timeout-accuracy.txt
```

**Commit**: YES
- Message: `docs(async-patterns): add performance implications and timeout strategy explanations`
- Files: `docs/guides/async-patterns.md`
- Pre-commit: `grep -n "Performance\|Soft\|Hard\|Timeout" docs/guides/async-patterns.md`

---

### Task 8: Cross-Reference Verification

**What to do**:
- Review all 6 updated documentation files for internal cross-references
- Verify all links point to correct file paths
- Check that cross-references between docs are bidirectional where appropriate
  - Example: rate-limiting.md mentions security_hardening.py, verify phase-13.md also mentions rate-limiting.md
- Test all relative links (docs/guides/README.md format)
- Verify all code examples reference correct source files
- Create evidence file listing all verified cross-references

**Must NOT do**:
- Don't change content, only verify accuracy
- Don't add new cross-references beyond fixing existing ones

**Recommended Agent Profile**:
- **Category**: `deep`
  - Reason: Comprehensive verification requires thorough analysis and pattern finding
- **Skills**: None required

**Parallelization**:
- **Can Run In Parallel**: NO (needs all other tasks complete)
- **Parallel Group**: Wave 4
- **Blocks**: Task 10 (final validation)
- **Blocked By**: Tasks 2-7 (all doc updates)

**References**:

**Documentation References** (all updated files):
- `docs/guides/rate-limiting.md` — Check cross-refs to other docs
- `docs/guides/health-checks.md` — Check cross-refs
- `docs/guides/async-patterns.md` — Check cross-refs
- `docs/guides/developer.md` — Check cross-refs
- `docs/phases/phase-13.md` — Check cross-refs
- `docs/DOCUMENTATION_INDEX.md` — Master index (verify all updated docs listed)

**WHY Each Reference Matters**:
- Each file should reference others appropriately
- Index should list all updated files
- Developers follow links to understand full context

**Acceptance Criteria**:

- [ ] All internal cross-references verified (links point to correct files)
- [ ] All code file references verified (lines numbers correct)
- [ ] No broken links or 404s
- [ ] Cross-references are bidirectional where appropriate
- [ ] DOCUMENTATION_INDEX.md lists all 6 updated files
- [ ] Evidence file created with complete cross-reference map

**QA Scenarios**:

```
Scenario: All file path references are correct
  Tool: Bash (find + grep)
  Preconditions: All doc files updated
  Steps:
    1. Run: grep -r "src/solstein\|docs/" docs/guides/rate-limiting.md
    2. For each file reference, verify file exists: test -f <path>
    3. Repeat for health-checks.md, async-patterns.md, developer.md, phase-13.md
  Expected Result: All referenced files exist and paths are correct
  Failure Indicators: test -f returns false for any reference
  Evidence: .sisyphus/evidence/task-8-file-refs.txt

Scenario: Cross-references between docs are consistent
  Tool: Grep + manual verification
  Preconditions: All docs updated
  Steps:
    1. Find all mentions of "rate-limiting" across all docs
    2. Find all mentions of "health-check" across all docs
    3. Find all mentions of "async-patterns" across all docs
    4. Verify these are consistent and logical
  Expected Result: Docs reference each other appropriately
  Failure Indicators: Orphaned docs (never mentioned), conflicting references
  Evidence: .sisyphus/evidence/task-8-cross-refs.txt
```

**Commit**: NO (verification only, no file changes)
- Evidence: `.sisyphus/evidence/task-8-cross-ref-verification.txt`

---

### Task 9: Code Examples Verification

**What to do**:
- Review all code examples in 6 updated documentation files
- For each example, verify it:
  - Matches actual source code (copy-paste accuracy)
  - Uses correct class/method names
  - Has correct parameters and imports
  - Would actually execute without errors
  - Is current (not outdated)
- Create evidence file documenting each example verified
- Flag any examples that are pseudo-code or simplified (note as such)

**Must NOT do**:
- Don't change content, only verify
- Don't assume examples are pseudo-code without documentation

**Recommended Agent Profile**:
- **Category**: `unspecified-high`
  - Reason: Requires code reading, verification, comparison
- **Skills**: None required

**Parallelization**:
- **Can Run In Parallel**: NO (needs all other tasks complete)
- **Parallel Group**: Wave 4
- **Blocks**: Task 10 (final validation)
- **Blocked By**: Tasks 2-7 (all doc updates)

**References**:

**Documentation References** (where examples are):
- `docs/guides/rate-limiting.md` — Lines with code blocks
- `docs/guides/health-checks.md` — Lines with code blocks
- `docs/guides/async-patterns.md` — Lines with code blocks
- `docs/guides/developer.md` — Lines with code blocks

**Code References** (source of truth):
- `src/solstein/data/security_hardening.py` — For rate limiter examples
- `src/solstein/api/routers/enrichment.py` — For health check examples
- `src/solstein/worker_tasks.py` — For async/retry examples
- `src/solstein/celery_config.py` — For Celery config examples

**Acceptance Criteria**:

- [ ] All code examples reviewed and compared to source
- [ ] Examples match actual code (not pseudo-code) OR clearly marked as pseudo
- [ ] All imports, class names, method names are accurate
- [ ] Example parameters match actual defaults
- [ ] Examples would execute without errors
- [ ] Evidence file documents each example verified
- [ ] No outdated or deprecated patterns

**QA Scenarios**:

```
Scenario: Rate limiter example matches actual implementation
  Tool: Read file + code comparison
  Preconditions: rate-limiting.md code examples reviewed
  Steps:
    1. Read first code example in rate-limiting.md
    2. Extract class name, method names, parameter names
    3. Read src/solstein/data/security_hardening.py to verify
    4. Confirm: class name matches, methods exist, parameters correct
  Expected Result: Code example is exact copy from source or clearly marked as pseudo
  Failure Indicators: Class/method names don't match actual code
  Evidence: .sisyphus/evidence/task-9-rate-limiter-example.txt

Scenario: Async pattern example matches worker_tasks.py
  Tool: Read file + code comparison
  Preconditions: async-patterns.md examples reviewed
  Steps:
    1. Read all Celery task examples in async-patterns.md
    2. Compare to src/solstein/worker_tasks.py actual tasks
    3. Verify decorator names, method signatures, exception handling
  Expected Result: Examples match actual Celery tasks (or marked as pseudo)
  Failure Indicators: Examples use wrong decorator names or outdated patterns
  Evidence: .sisyphus/evidence/task-9-async-example.txt
```

**Commit**: NO (verification only, no file changes)
- Evidence: `.sisyphus/evidence/task-9-code-examples-verification.txt`

---

### Task 10: Final Test Run and Validation

**What to do**:
- Run full pytest suite to ensure all tests still passing (123/123)
- Run linting/type checks (if configured)
- Verify no import errors or syntax issues in changed files
- Create final validation report
- Confirm all 7 issues have been addressed
- Generate summary of changes made

**Must NOT do**:
- Don't modify code beyond what previous tasks did
- Don't skip any tests or checks

**Recommended Agent Profile**:
- **Category**: `quick`
  - Reason: Running test suite, validation checks, reporting
- **Skills**: None required

**Parallelization**:
- **Can Run In Parallel**: NO (final validation)
- **Parallel Group**: Wave 4 (final)
- **Blocks**: COMPLETION
- **Blocked By**: Tasks 8-9 (all verification)

**References**:

**Code References** (all changed files):
- `src/solstein/worker_tasks.py` — Fixed timestamp bug
- `src/solstein/data/security_hardening.py` — Added docstring comments
- `docs/guides/rate-limiting.md` — Updated defaults explanation
- `docs/guides/health-checks.md` — Fixed readiness description
- `docs/guides/async-patterns.md` — Added performance context
- `docs/guides/developer.md` — Added Redis setup
- `docs/phases/phase-13.md` — Updated DLQ section

**Test References**:
- `tests/` — Full pytest suite (should have 123 passing tests)

**Acceptance Criteria**:

- [ ] `pytest tests/ -v` → 123/123 tests passing
- [ ] No import errors in changed Python files
- [ ] No syntax errors in changed Markdown files
- [ ] All 7 issues documented as addressed
- [ ] Final validation report generated
- [ ] No regressions from previous state

**QA Scenarios**:

```
Scenario: All tests pass with no regressions
  Tool: Bash (pytest)
  Preconditions: All tasks 1-9 complete
  Steps:
    1. Run: cd /home/ai-whisperers/solstein && pytest tests/ -v
    2. Count passing tests: grep "passed" output
    3. Verify no failed or error tests
    4. Check for regressions vs baseline (123 tests)
  Expected Result: pytest exits with 123 passed, 0 failed
  Failure Indicators: Test count < 123, or any FAILED results
  Evidence: .sisyphus/evidence/task-10-test-results.txt

Scenario: No import or syntax errors in changed files
  Tool: Bash (python -m py_compile)
  Preconditions: All Python files modified
  Steps:
    1. Run: python -m py_compile src/solstein/worker_tasks.py
    2. Run: python -m py_compile src/solstein/data/security_hardening.py
    3. Verify no syntax errors returned
  Expected Result: Both files compile without errors
  Failure Indicators: SyntaxError or CompileError returned
  Evidence: .sisyphus/evidence/task-10-syntax-check.txt
```

**Commit**: YES
- Message: `docs: final validation - all documentation fixes complete, tests passing`
- Files: (no new files, but verification of all changes)
- Pre-commit: `pytest tests/ -q && echo "✅ All tests passed"`

---

## Final Verification Wave

> 2 parallel verification tasks run after ALL implementation tasks

- [ ] **F1. Accuracy Audit** — `deep`
  Read all 6 updated documentation files. For each "claim": find it in docs, find it in code, verify they match. Check every example is real. Compare against original audit findings. VERDICT: PASS/FAIL with specific issues if any.
  Output: `Documentation accuracy verified | Issues: [N] | VERDICT: APPROVE/REJECT`

- [ ] **F2. Link & Reference Check** — `unspecified-high`
  Test all cross-references, file paths, line numbers. Run any code examples as tests. Verify nothing is broken. Check DOCUMENTATION_INDEX.md is up-to-date with all 6 files.
  Output: `Cross-refs [N/N valid] | Examples [N executable] | Index [complete] | VERDICT`

---

## Commit Strategy

**Structure**: 6 commits (one per major change) + 1 final summary commit

1. **Commit 1** (Task 1)
   - `fix(worker_tasks): correct DLQ timestamp bug`
   - 1 file: `src/solstein/worker_tasks.py`

2. **Commit 2** (Task 2)
   - `docs(rate-limiting): clarify default rate limits`
   - 1 file: `docs/guides/rate-limiting.md`

3. **Commit 3** (Task 3)
   - `docs(phase-13): update DLQ documentation`
   - 1 file: `docs/phases/phase-13.md`

4. **Commit 4** (Task 4)
   - `docs(developer): add Redis setup guide`
   - 1 file: `docs/guides/developer.md`

5. **Commit 5** (Task 5)
   - `docs(security_hardening): add Redis docstrings`
   - 1 file: `src/solstein/data/security_hardening.py`

6. **Commit 6** (Task 6)
   - `docs(health-checks): clarify readiness probe behavior`
   - 1 file: `docs/guides/health-checks.md`

7. **Commit 7** (Task 7)
   - `docs(async-patterns): enhance with performance context`
   - 1 file: `docs/guides/async-patterns.md`

8. **Final Commit** (Task 10)
   - `docs: complete documentation audit fixes - all issues resolved`
   - Multiple files (no new, but reference to changes)

---

## Success Criteria

### Verification Commands
```bash
# Test suite
pytest tests/ -v
# Output: 123 passed in X seconds

# Syntax check
python -m py_compile src/solstein/worker_tasks.py
python -m py_compile src/solstein/data/security_hardening.py
# Output: No errors

# Documentation validation
grep -r "60\|100" docs/guides/rate-limiting.md
# Output: Both values mentioned correctly

# Cross-reference check
grep "health-checks\|rate-limiting\|async-patterns" docs/DOCUMENTATION_INDEX.md
# Output: All files listed
```

### Final Checklist
- [ ] All 7 issues from audit addressed (3 critical, 2 moderate, 2 minor)
- [ ] No test regressions (123/123 passing)
- [ ] All code examples verified as real
- [ ] All cross-references verified as correct
- [ ] No broken links or 404s in documentation
- [ ] Markdown syntax is valid
- [ ] Commit messages follow Conventional Commits
- [ ] Evidence files saved to `.sisyphus/evidence/`

---

## Notes for Executor

### What This Plan Does
1. Fixes critical bug in Dead Letter Queue (timestamp)
2. Corrects 5 documentation files with technical accuracy issues
3. Adds Redis setup guide to developer documentation
4. Adds docstring comments to clarify optional Redis usage
5. Verifies all changes through comprehensive QA scenarios

### What This Plan Does NOT Do
- ❌ Change production API or behavior (only fix bugs + docs)
- ❌ Add new features or endpoints
- ❌ Modify user-facing functionality
- ❌ Break any existing tests

### Critical Success Factor
**Task 1 must complete first** — the Dead Letter Queue bug fix unblocks all documentation tasks since they all reference this fix. All other tasks can run in parallel after Task 1.

### Time Estimate
- Wave 1 (Task 1): 5 minutes
- Wave 2 (Tasks 2-5): 30-40 minutes (parallel)
- Wave 3 (Tasks 6-7): 25-35 minutes (parallel)
- Wave 4 (Tasks 8-10): 10-15 minutes (sequential)
- **Total: 70-95 minutes**

### If Anything Breaks
- Check pytest output for specific failure
- Review code change that caused it
- Verify Task 1 (bug fix) is syntactically correct first
- Ensure datetime import is present in worker_tasks.py
