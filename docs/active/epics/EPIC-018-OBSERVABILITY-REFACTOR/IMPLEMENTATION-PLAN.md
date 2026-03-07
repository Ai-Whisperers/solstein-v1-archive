# EPIC-018 Implementation Plan: Complete Observability Refactor

> **Status**: Implementation in Progress
> **Last Updated**: 2026-03-05
> **Owner**: Engineering Team
> **Estimated Duration**: 2-3 weeks

---

## Overview

This plan addresses all gaps, issues, and improvements identified in the EPIC-018 observability refactor. Work is organized into 4 phases:

1. **Critical Fixes** - Blockers for production use
2. **Integration & Wiring** - Connect all components properly
3. **Testing & Validation** - Ensure everything works
4. **Cleanup & Documentation** - Polish and finalize

---

## Phase 1: Critical Fixes (Week 1)

### 1.1 Celery Context Propagation Wiring
**Priority**: 🔴 Critical
**Story**: 18.2
**Files**: `celery_config.py`

**Problem**: `celery_context.py` exists but signals aren't registered.

**Task**:
```python
# Add to celery_config.py after line 33
from . import celery_context  # noqa: F401 - registers signals
```

**Verification**:
```bash
python3 -c "from src.solstein.celery_config import celery_app; print('Celery context signals registered')"
```

**Acceptance Criteria**:
- [ ] `before_task_publish` signal fires when task is queued
- [ ] `task_prerun` restores context from headers
- [ ] `task_postrun` clears context after completion
- [ ] Context propagates from web request → Celery task

---

### 1.2 Remove Duplicate Middleware File
**Priority**: 🔴 Critical
**Story**: 18.1
**Files**: `api/middleware.py`

**Problem**: Old `LoggingMiddleware` in `middleware.py` conflicts with new implementation.

**Task**:
1. Check if `middleware.py` is imported anywhere:
   ```bash
   grep -rn "from.*middleware import" src/solstein --include="*.py" | grep -v "middleware\."
   grep -rn "api.middleware import" src/solstein --include="*.py"
   ```

2. If not used, delete `api/middleware.py`

3. If used, migrate imports to `api/middleware/logging.py`

**Acceptance Criteria**:
- [ ] No references to old `LoggingMiddleware` class
- [ ] `api/middleware.py` file removed or deprecated
- [ ] All imports use `api.middleware.logging`

---

### 1.3 Exception Handler Registration Order
**Priority**: 🔴 Critical
**Story**: 18.4
**Files**: `api/main.py`

**Problem**: `setup_exception_handlers` called after middleware, might miss middleware errors.

**Current Order**:
```python
setup_logging_middleware(app)      # Line 137
setup_rate_limiting(app)           # Line 140
setup_exception_handlers(app)      # Line 143
```

**Fix Order**:
```python
setup_exception_handlers(app)      # MUST BE FIRST
setup_logging_middleware(app)      # Then middleware
setup_rate_limiting(app)
```

**Acceptance Criteria**:
- [ ] Exception handlers registered before any middleware
- [ ] Middleware exceptions caught by global handler
- [ ] Error responses include request_id even for middleware errors

---

### 1.4 Environment Configuration Documentation
**Priority**: 🟡 High
**Story**: 18.4
**Files**: `.env.example`, `.env.production`, `.env.staging`

**Problem**: New `DEBUG_ERRORS` setting not documented.

**Tasks**:
1. Add to `.env.example`:
   ```bash
   # SECURITY: Never enable DEBUG_ERRORS in production!
   # When enabled, error responses include stack traces (information disclosure risk)
   DEBUG_ERRORS=false
   ```

2. Add to `.env.production`:
   ```bash
   DEBUG_ERRORS=false
   ```

3. Verify `.env.staging` has `DEBUG_ERRORS=false`

**Acceptance Criteria**:
- [ ] All environment templates include `DEBUG_ERRORS`
- [ ] Security warning present in all files
- [ ] Production config explicitly sets `false`

---

## Phase 2: Integration & Wiring (Week 1-2)

### 2.1 Remaining Stdlib Logging Migration
**Priority**: 🟡 High
**Story**: 18.1
**Files**: Multiple (see list)

**Problem**: Several modules still use stdlib `logging`.

**Modules to Migrate**:
- `infrastructure/outbox_worker.py`
- `infrastructure/research_dual_write.py`
- `core/error_handler.py`
- `data/error_logging.py`

**Migration Pattern**:
```python
# BEFORE
import logging
logger = logging.getLogger(__name__)
logger.info("message", extra={"key": "value"})

# AFTER
from loguru import logger
logger.bind(key="value").info("message")
```

**Acceptance Criteria**:
- [ ] No `import logging` in production code (except `utils/logging.py`)
- [ ] All `logger = logging.getLogger()` removed
- [ ] All `extra={...}` converted to `.bind()`
- [ ] Audit log still works (either keep stdlib or migrate to Loguru sink)

---

### 2.2 Silent Error Audit Remediation
**Priority**: 🟡 High
**Story**: 18.3
**Files**: Various (81 locations found)

**Problem**: 81 silent exception handlers remain in codebase.

**Approach**:
1. Run audit to get list:
   ```bash
   python scripts/audit_silent_errors.py > silent_errors.txt
   ```

2. Categorize by severity:
   - **Critical** (fix immediately): API layer, middleware, data persistence
   - **High** (fix this sprint): Agents, enrichment
   - **Medium** (fix next sprint): Utilities, tests

3. Fix pattern:
   ```python
   # BEFORE
   except Exception:
       pass

   # AFTER
   except Exception as e:
       logger.warning("Operation failed, continuing", error=str(e))
   ```

**Batch Tasks**:
- [ ] Fix 10 critical handlers
- [ ] Fix 20 high-priority handlers
- [ ] Schedule remaining 51 for next sprint

---

### 2.3 Exception Taxonomy Migration
**Priority**: 🟡 High
**Story**: 18.5
**Files**: LLM layer, data layer

**Problem**: Old custom exceptions still used, need migration to new taxonomy.

**Migration Map**:
| Old Exception | New Exception | Files |
|--------------|---------------|-------|
| `StructuredOutputError` | `LLMError` | `llm/structured_client.py` |
| `LLMGenerationError` | `LLMError` | `llm/enhanced_client.py` |
| `ConfigError` | `ConfigurationError` | `data/enrichment_config.py` |
| `ContradictionLifecycleError` | `StateError` | `infrastructure/research_dual_write.py` |

**Migration Steps**:
1. Update exception imports
2. Update raise statements with new signature
3. Update catch blocks
4. Add backwards compatibility aliases if needed

**Acceptance Criteria**:
- [ ] No old exception classes used in production code
- [ ] All exceptions inherit from `SolsteinError`
- [ ] HTTP status codes correctly mapped

---

## Phase 3: Testing & Validation (Week 2)

### 3.1 Unit Tests for Observability Modules
**Priority**: 🔴 Critical
**Story**: All
**Files**: `tests/unit/test_observability/`

**Test Files to Create**:

#### `test_context.py`
```python
# Test coverage:
- set_context / reset_context
- get_current_context
- Context isolation between concurrent requests
- Celery context propagation
```

#### `test_logging.py`
```python
# Test coverage:
- setup_logging with JSON format
- InterceptHandler routes stdlib to Loguru
- format_record includes contextvars
- Context auto-included in all logs
```

#### `test_exceptions.py`
```python
# Test coverage:
- SolsteinError base interface
- All exception types have correct status_code
- to_dict() format
- with_details() helper
- Backwards compatibility aliases
```

#### `test_tracing.py`
```python
# Test coverage:
- DependencyTracer.trace() context manager
- Metrics calculation (p50, p95, p99)
- Error tracking
- Max calls limit enforcement
```

#### `test_middleware_logging.py`
```python
# Test coverage:
- ContextMiddleware sets context
- RequestLoggingMiddleware logs requests
- ErrorLoggingMiddleware logs errors (not silent)
- Headers added to response
```

#### `test_api_exceptions.py`
```python
# Test coverage:
- Stack traces NOT in production responses
- Stack traces present when DEBUG_ERRORS=true (dev only)
- Sensitive details redacted
- Safe details included
- All error responses have request_id
```

**Acceptance Criteria**:
- [ ] 80%+ code coverage for new modules
- [ ] All tests pass
- [ ] CI pipeline includes observability tests

---

### 3.2 Integration Tests
**Priority**: 🟡 High
**Story**: All
**Files**: `tests/integration/test_observability/`

**Test Scenarios**:

#### Context Propagation End-to-End
```python
# Test: Web request → service layer → repository → response
# Verify: request_id present in all log lines
```

#### Celery Context Propagation
```python
# Test: API endpoint queues task → worker processes
# Verify: Same request_id in web logs and worker logs
```

#### Error Response Security
```python
# Test: Trigger 500 error in production mode
# Verify: Response has no traceback, no internal paths
# Verify: Server logs have full traceback
```

#### Dependency Tracing
```python
# Test: API call that uses DB + LLM + external API
# Verify: All three dependencies logged with timing
# Verify: Metrics endpoint shows latencies
```

**Acceptance Criteria**:
- [ ] Integration tests pass in CI
- [ ] Tests run against real (test) database
- [ ] Celery tests run with test broker

---

### 3.3 Security Validation
**Priority**: 🔴 Critical
**Story**: 18.4
**Files**: Security test suite

**Security Tests**:

#### Test 1: Production Error Response
```bash
curl -s http://localhost:8000/trigger-error | jq .
# Verify: NO traceback field
# Verify: NO debug field
# Verify: Generic error message
```

#### Test 2: Development Error Response
```bash
DEBUG_ERRORS=true curl -s http://localhost:8000/trigger-error | jq .
# Verify: debug.traceback present
# Verify: debug.error_type present
```

#### Test 3: Sensitive Data Redaction
```python
# Raise exception with password, SQL query, file path
# Verify: Response shows [REDACTED] for sensitive fields
# Verify: Server logs have full details
```

**Acceptance Criteria**:
- [ ] Security scan passes
- [ ] No stack traces in production responses
- [ ] No sensitive data in error responses

---

## Phase 4: Cleanup & Documentation (Week 3)

### 4.1 Metrics Endpoint
**Priority**: 🟢 Medium
**Story**: 18.6
**Files**: `api/routers/metrics.py`

**Implementation**:
```python
@router.get("/metrics/dependencies")
async def get_dependency_metrics():
    tracer = get_tracer()
    return tracer.get_metrics()

@router.get("/metrics/dependencies/{service}")
async def get_service_metrics(service: str):
    tracer = get_tracer()
    return tracer.get_metrics(service=service)
```

**Acceptance Criteria**:
- [ ] Metrics endpoint accessible
- [ ] Shows p50/p95/p99 latencies
- [ ] Shows error rates
- [ ] Authenticated (admin only)

---

### 4.2 Documentation Updates
**Priority**: 🟢 Medium
**Story**: All
**Files**: `docs/`, `README.md`

**Documents to Update**:

#### `docs/observability/logging.md` (new)
- How to use Loguru in new code
- How to add context to logs
- How to configure JSON logging for production

#### `docs/observability/error-handling.md` (new)
- Exception taxonomy guide
- When to use each exception type
- Error handling patterns

#### `docs/observability/tracing.md` (new)
- How to trace dependencies
- How to view metrics
- Performance optimization guide

#### `docs/runbooks/debugging.md` (update)
- How to use request_id for tracing
- How to query logs
- How to interpret error responses

**Acceptance Criteria**:
- [ ] All new modules documented
- [ ] Examples provided
- [ ] Migration guide for old patterns

---

### 4.3 Monitoring & Alerting Setup
**Priority**: 🟢 Medium
**Story**: All
**Files**: Infrastructure config

**Tasks**:
1. Set up log aggregation (if not already)
2. Create dashboards:
   - Error rate by endpoint
   - Request latency p95/p99
   - Dependency health
3. Create alerts:
   - Error rate > 1%
   - Dependency latency > 2s
   - Silent errors detected

**Acceptance Criteria**:
- [ ] Dashboards created
- [ ] Alerts configured
- [ ] Runbook for incident response

---

## Task Checklist

### Phase 1: Critical Fixes
- [ ] 1.1 Celery context import added
- [ ] 1.2 Duplicate middleware removed
- [ ] 1.3 Exception handler order fixed
- [ ] 1.4 Environment config documented

### Phase 2: Integration
- [ ] 2.1 Stdlib logging migrated in all modules
- [ ] 2.2 Critical silent errors fixed (10)
- [ ] 2.3 High-priority silent errors fixed (20)
- [ ] 2.4 Exception taxonomy migration complete

### Phase 3: Testing
- [ ] 3.1 Unit tests for context.py
- [ ] 3.2 Unit tests for logging.py
- [ ] 3.3 Unit tests for exceptions.py
- [ ] 3.4 Unit tests for tracing.py
- [ ] 3.5 Unit tests for middleware
- [ ] 3.6 Unit tests for api/exceptions.py
- [ ] 3.7 Integration tests for context propagation
- [ ] 3.8 Integration tests for Celery
- [ ] 3.9 Security validation tests
- [ ] 3.10 All tests passing in CI

### Phase 4: Cleanup
- [ ] 4.1 Metrics endpoint implemented
- [ ] 4.2 Logging documentation
- [ ] 4.3 Error handling documentation
- [ ] 4.4 Tracing documentation
- [ ] 4.5 Debugging runbook updated
- [ ] 4.6 Dashboards created
- [ ] 4.7 Alerts configured

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Celery context doesn't work | Integration test with real task queue |
| Performance regression | Benchmark before/after, <5% threshold |
| Breaking existing code | Comprehensive test suite, staged rollout |
| Security bypass | Penetration test of error responses |
| Silent errors missed | Audit script in CI pipeline |

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Silent exception handlers | 81 | 0 |
| Stdlib logging imports | 8 | 1 |
| Test coverage (new modules) | 0% | 80%+ |
| Production error exposure | Yes | No |
| Context propagation | 30% | 95% |
| Mean time to debug | 2 hours | 15 min |

---

## Resources

- **Engineering**: 2-3 engineers
- **QA**: 1 engineer for testing
- **Security Review**: 1 security engineer (phase 3)
- **Documentation**: 1 technical writer (phase 4)

---

*Plan Version: 1.0*
*Next Review: After Phase 1 completion*
