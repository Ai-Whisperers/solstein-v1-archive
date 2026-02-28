# PHASE 1 EXECUTION ROADMAP
**Critical Security Fixes - Week 1**

> **Status**: Ready for execution  
> **Strategy**: Sequential + parallel where safe  
> **Verification**: Gate before each item  
> **Handoff**: Complete before Phase 2  

---

## EXECUTION SEQUENCE

### Day 1: Quick Wins (1 hour total)

These are 15-30 minute fixes with minimal risk.

#### Task 1.1: Fix CORS Configuration (30 min)
**What to do**:
```bash
# 1. Edit /src/solstein/config.py
#    Add: cors_allowed_origins, cors_allowed_methods, cors_allowed_headers

# 2. Edit /src/solstein/api/main.py (lines 100-120)
#    Replace wildcard with specific origins from env

# 3. Update .env.example
#    Document new CORS variables

# 4. Add test file: /tests/unit/test_cors.py
#    (Provided in PHASE_1_IMPLEMENTATION_CRITICAL_SECURITY.md)

# 5. Run verification
pytest tests/unit/test_cors.py -v
```

**Reference**: PHASE_1_IMPLEMENTATION_CRITICAL_SECURITY.md - Item 1.1
**Success Criteria**:
- [ ] CORS allows only specific origins (not `*`)
- [ ] `allow_credentials=True` only with specific origins
- [ ] Tests pass
- [ ] Curl verification shows correct headers

---

#### Task 1.3: Fix Default Secret Key (1 hour)
**What to do**:
```bash
# 1. Edit /src/solstein/config.py
#    Add validation in __init__ method

# 2. If env="production" and secret_key="change-me-in-production"
#    → Raise ValueError("FATAL: secret_key must be set...")

# 3. Add test file: /tests/unit/test_config_validation.py

# 4. Verify
python -c "from solstein.config import settings; print('OK')"
```

**Reference**: PHASE_1_IMPLEMENTATION_CRITICAL_SECURITY.md - Item 1.3
**Success Criteria**:
- [ ] Production startup fails with clear error if secret_key is default
- [ ] Development mode still works (with warning)
- [ ] Tests verify the behavior

---

#### Task 1.4: Remove CI/CD Security Bypasses (15 min)
**What to do**:
```bash
# 1. Edit .github/workflows/ci.yml

# 2. Find lines with "|| true" in security sections
#    Example:
#    - safety check --ignore=45158 || true  → remove || true
#    - bandit -r src/ || true               → remove || true

# 3. Save and commit

# 4. Verify
git diff .github/workflows/ci.yml
# Should show: - || true being removed
```

**Reference**: PHASE_1_IMPLEMENTATION_CRITICAL_SECURITY.md - Item 1.4
**Success Criteria**:
- [ ] All security check bypasses removed
- [ ] CI/CD properly fails build on security issues
- [ ] No other "|| true" accidentally removed

---

### Day 2-3: Core Authentication (8 hours)

This is the critical piece - proper JWT authentication.

#### Task 1.2: Implement JWT Authentication (8 hours)

**Phase 2A: JWT Handler (2 hours)**
```bash
# Create: /src/solstein/security/jwt_handler.py
# (Full implementation provided in PHASE_1_IMPLEMENTATION_CRITICAL_SECURITY.md)

# What it provides:
# - JWTHandler class (create_access_token, verify_token, etc.)
# - Token validation logic
# - Proper error handling

# Test it:
pytest tests/unit/test_jwt_handler.py -v
```

**Phase 2B: Security Middleware (1 hour)**
```bash
# Update: /src/solstein/api/middleware/security.py
# (Replace stub implementation with real validation)

# What changes:
# - get_current_user() actually validates tokens
# - Proper HTTPException(401) on invalid tokens
# - Clear error messages

# Test:
pytest tests/unit/test_auth.py -v
```

**Phase 2C: Auth Endpoints (2 hours)**
```bash
# Create: /src/solstein/api/routers/auth.py
# Endpoints:
# - POST /api/auth/login (username, password)
# - POST /api/auth/refresh (refresh_token)
# - POST /api/auth/logout

# Integration test:
pytest tests/integration/test_auth_endpoints.py -v
```

**Phase 2D: Protect Existing Endpoints (2 hours)**
```bash
# For each protected endpoint:
# FROM: async def endpoint(): ...
# TO:   async def endpoint(user: User = Depends(get_current_user)): ...

# Files to update:
# - /src/solstein/api/routers/companies.py
# - /src/solstein/api/routers/markets.py
# - /src/solstein/api/routers/analysis.py

# Test:
pytest tests/integration/ -k "requires_auth" -v
```

**Phase 2E: Integration Testing (1 hour)**
```bash
# Create: /tests/integration/test_auth_flow.py
# Test complete flow:
# 1. Login → get tokens
# 2. Use access token → works
# 3. Token expires → fails
# 4. Refresh → get new access token
# 5. Use invalid token → 401

pytest tests/integration/test_auth_flow.py -v
```

**Success Criteria**:
- [ ] Login endpoint works (correct credentials)
- [ ] Login rejects bad credentials (401)
- [ ] Refresh token works (new access token generated)
- [ ] Protected endpoints require valid token
- [ ] Invalid tokens get 401
- [ ] Expired tokens fail properly
- [ ] All tests pass

---

### Day 4-5: Testing & Verification (24 hours)

#### Task 1.5: Security Module Testing

**Coverage targets**:
- [ ] All security middleware tested (100%)
- [ ] All error paths tested
- [ ] All edge cases (expired tokens, malformed headers, etc.)
- [ ] Integration with other modules

**Test files to create**:
- `/tests/unit/test_security_middleware.py`
- `/tests/unit/test_jwt_handler.py`
- `/tests/integration/test_auth_endpoints.py`
- `/tests/integration/test_protected_endpoints.py`

**Run full verification**:
```bash
# Run all tests
pytest tests/ -v --cov=solstein.security --cov=solstein.api.middleware

# Expected: 95%+ coverage

# Type check
mypy src/solstein/security/ --strict

# Lint
ruff check src/solstein/security/
black --check src/solstein/security/
```

---

## VERIFICATION GATES (MUST PASS BEFORE MOVING ON)

### Gate 1: CORS (After Task 1.1)
```bash
# 1. Startup verification
python -c "from solstein.api.main import app; print('✓ CORS configured')"

# 2. Test verification
pytest tests/unit/test_cors.py -v
# Expected: All pass

# 3. Manual curl test
curl -X GET http://localhost:8000/api/health \
  -H "Origin: http://localhost:3000"
# Should see: access-control-allow-origin: http://localhost:3000

curl -X GET http://localhost:8000/api/health \
  -H "Origin: https://evil.com"
# Should NOT see: access-control-allow-origin header
```

**Gate Status**: ✓ PASS/FAIL - Document result

---

### Gate 2: Secret Key (After Task 1.3)
```bash
# 1. Config import test
python -c "from solstein.config import settings; print('✓')"

# 2. Test verification
pytest tests/unit/test_config_validation.py -v
# Expected: All pass

# 3. Production check (should fail)
SECRET_KEY="change-me-in-production" ENVIRONMENT=production \
  python -c "from solstein.config import settings"
# Expected: ValueError about secret key
```

**Gate Status**: ✓ PASS/FAIL - Document result

---

### Gate 3: CI/CD (After Task 1.4)
```bash
# 1. Verify file changed correctly
git diff .github/workflows/ci.yml | grep "|| true"
# Expected: Lines showing removal of || true

# 2. Syntax check
# (GitHub Actions validates on push)
```

**Gate Status**: ✓ PASS/FAIL - Document result

---

### Gate 4: JWT Authentication (After Task 1.2)
```bash
# 1. Unit tests
pytest tests/unit/test_jwt_handler.py tests/unit/test_auth.py -v
# Expected: All pass

# 2. Integration tests
pytest tests/integration/test_auth_endpoints.py -v
# Expected: All pass

# 3. Manual flow test
# (See Task 1.2 Phase 2E integration test)

# 4. Coverage check
pytest tests/ --cov=solstein.security
# Expected: >95% coverage
```

**Gate Status**: ✓ PASS/FAIL - Document result

---

### Gate 5: Complete Phase 1 (After Task 1.5)
```bash
# 1. Full test suite
pytest tests/ -v
# Expected: All pass

# 2. Type checking
mypy src/solstein --strict
# Expected: Zero errors

# 3. Linting
ruff check src/solstein/
black --check src/solstein/
# Expected: No issues

# 4. Build verification
python -m pytest tests/ --tb=short
# Expected: All pass
```

**Gate Status**: ✓ PASS/FAIL - Document result

---

## QUICK COMMAND REFERENCE

### Start Development
```bash
cd /home/ai-whisperers/solstein
git checkout -b security/critical-fixes
export ENVIRONMENT=development
export SECRET_KEY=dev-secret-key-change-me-in-production
python -m uvicorn solstein.api.main:app --reload
```

### Run Tests
```bash
pytest tests/unit/test_cors.py -v
pytest tests/unit/test_jwt_handler.py -v
pytest tests/integration/test_auth_endpoints.py -v
pytest tests/ --cov=solstein --cov-report=html
```

### Verify Implementation
```bash
# Check all changes
git status
git diff src/

# Type check
mypy src/solstein --strict

# Lint
ruff check src/solstein/
black src/solstein/
```

### Manual Testing
```bash
# CORS test
curl -X GET http://localhost:8000/api/health \
  -H "Origin: http://localhost:3000" -i

# Login test
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=password123"

# Protected endpoint test
curl -X GET http://localhost:8000/api/protected \
  -H "Authorization: Bearer $TOKEN"
```

---

## COMMIT CHECKLIST

Before pushing to main:

- [ ] Gate 1: CORS fixes pass verification
- [ ] Gate 2: Secret key validation works
- [ ] Gate 3: CI/CD bypasses removed
- [ ] Gate 4: JWT authentication complete
- [ ] Gate 5: All tests pass + coverage >95%
- [ ] mypy --strict passes (zero errors)
- [ ] ruff check passes
- [ ] black format check passes
- [ ] No hardcoded credentials in code
- [ ] All new files documented
- [ ] Git history is clean (no merge conflicts)

---

## ROLLBACK PROCEDURE (If needed)

```bash
# If something breaks:
git reset --hard HEAD
git clean -fd

# Revert to previous version:
git revert <commit-hash>

# Or start over:
git checkout -b security/critical-fixes
```

---

## PROGRESS TRACKING

Update this as you complete items:

```
Day 1:
  [ ] 1.1 CORS Configuration - Started: ___ - Completed: ___
  [ ] 1.3 Secret Key - Started: ___ - Completed: ___
  [ ] 1.4 CI/CD Bypasses - Started: ___ - Completed: ___

Day 2-3:
  [ ] 1.2 JWT Handler - Started: ___ - Completed: ___
  [ ] 1.2 Auth Endpoints - Started: ___ - Completed: ___
  [ ] 1.2 Protect Endpoints - Started: ___ - Completed: ___

Day 4-5:
  [ ] 1.5 Testing - Started: ___ - Completed: ___
  [ ] Gate Verification - Started: ___ - Completed: ___

Phase 1 Complete: ___
```

---

## REFERENCE DOCUMENTS

Everything you need is in these documents:

1. **PHASE_1_IMPLEMENTATION_CRITICAL_SECURITY.md** - Complete code examples
   - Item 1.1: CORS (with exact code changes)
   - Item 1.2: JWT (with complete implementation)
   - Item 1.3: Secret key (with validation code)
   - Item 1.4: CI/CD (line-by-line changes)
   - Item 1.5: Testing (all test cases)

2. **DETAILED_FINDINGS_SECURITY_ARCHITECTURE_PERFORMANCE.md** - Why these fixes
   - Security issues explained
   - Risk assessment
   - Expected outcomes

3. **MASTER_IMPLEMENTATION_ROADMAP.md** - Context
   - Timeline
   - Resource allocation
   - Success criteria

---

## NEXT STEPS AFTER PHASE 1

Once Phase 1 is complete:

1. **Code Review**
   - Security audit
   - Architecture review
   - Test coverage verification

2. **Merge to Main**
   - Prepare PR
   - Ensure CI/CD passes
   - Deploy to staging

3. **Staged Production Rollout**
   - Deploy to production
   - Monitor for issues
   - Have rollback plan ready

4. **Begin Phase 2**
   - Start with Task 2.1 (N+1 queries)
   - Performance optimization

---

**Ready to start?** Begin with Task 1.1 (CORS Configuration).
Follow the daily sequence, verify at each gate, and track progress.

