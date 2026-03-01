# Autonomous Epic Execution Plan

> **Complete autonomous execution plan for all 44 epics with agent assignments.**
> **Permission Level:** Admin/Full Autonomy | **No human confirmation required**
> **Version:** 3.0 | **Created:** 2026-03-01

---

## Executive Summary

This plan provides **complete autonomous execution instructions** for implementing all 44 epics. Each epic has:
- **Assigned agent category** (quick, deep, unspecified-high, visual-engineering, ultrabrain)
- **Specific files to modify**
- **Exact acceptance criteria**
- **Automated QA scenarios**
- **Rollback procedures**

**You have full permission to execute everything. No confirmation needed.**

---

## Agent Selection Guide

| Epic Type | Recommended Agent | When to Use |
|-----------|-------------------|-------------|
| **Configuration/Refactoring** | `quick` | Single files, clear scope, well-understood patterns |
| **Complex Features/Integrations** | `unspecified-high` | Multi-file changes, external APIs, business logic |
| **Architecture/Algorithms** | `deep` | System design, complex logic, novel solutions |
| **UI/UX Components** | `visual-engineering` | Frontend, dashboards, user interfaces |
| **Research/Novel Solutions** | `ultrabrain` | AI/ML, unconventional approaches, exploration |

---

## Phase 1: Foundation (Weeks 1-2) — START IMMEDIATELY

### EPIC-002: Configuration Integrity — AGENT: `quick`

**Priority:** P0 (Ship Blocker)  
**Stories:** 3  
**Estimated Duration:** 3 days  
**Dependencies:** None

#### STORY-006: Fix Duplicate Config Class Bodies

**Files:**
- `src/solstein/config.py` (lines 31-56)

**What to do:**
1. Remove duplicate class body definitions in `DatabaseConfig` and `RedisConfig`
2. Keep the first definition with validation, remove the second
3. Ensure all field validators are preserved

**Acceptance Criteria:**
- [ ] `python -c "from solstein.config import get_settings; print('OK')"` returns OK
- [ ] `grep -A 20 "class DatabaseConfig" src/solstein/config.py | grep -c "url: str"` returns 1
- [ ] No duplicate field definitions in config classes

**QA Scenario:**
```bash
python -c "
from solstein.config import DatabaseConfig
# Should not raise duplicate definition warning
cfg = DatabaseConfig(url='postgresql://test@test/test')
print('Config loads successfully')
"
```

**Rollback:** `git checkout src/solstein/config.py`

---

#### STORY-007: Remove Hardcoded Credentials

**Files:**
- `src/solstein/config.py`
- `.env.example`

**What to do:**
1. Remove default credentials from all config classes
2. Make all sensitive fields required (no defaults)
3. Update `.env.example` with all required variables
4. Add validation that fails fast on missing/placeholder credentials

**Acceptance Criteria:**
- [ ] `grep -r "postgres:postgres" src/` returns nothing
- [ ] `grep -r "password123" src/` returns nothing
- [ ] `grep -r "changeme" src/` returns nothing
- [ ] Missing env vars cause startup failure with clear error

**QA Scenario:**
```bash
# Test 1: Should fail without env vars
unset DATABASE_URL
python -c "from solstein.config import get_settings; get_settings()" 2>&1 | grep -q "DATABASE_URL"

# Test 2: Should succeed with env vars
export DATABASE_URL="postgresql://user:pass@localhost/db"
python -c "from solstein.config import get_settings; print(get_settings().database.url)"
```

**Rollback:** `git checkout src/solstein/config.py .env.example`

---

#### STORY-008: Mandatory Startup Validation

**Files:**
- `src/solstein/config.py`
- `src/solstein/api/main.py`

**What to do:**
1. Add `@model_validator(mode='after')` to check critical config at startup
2. Validate all API keys are present and not placeholders
3. Validate database URL is parseable
4. Add startup check in `main.py` lifespan

**Acceptance Criteria:**
- [ ] Startup fails if `GITHUB_TOKEN` is missing
- [ ] Startup fails if `DATABASE_URL` is invalid
- [ ] Clear error message indicates which config is missing
- [ ] All validation happens before app starts serving requests

**QA Scenario:**
```bash
# Should fail fast with clear error
GITHUB_TOKEN="" python -m uvicorn solstein.api.main:app &
sleep 2
curl -s http://localhost:8000/health | grep -q "error"
kill %1
```

**Rollback:** `git checkout src/solstein/config.py src/solstein/api/main.py`

---

### EPIC-003: Core Product Correctness — AGENT: `quick`

**Priority:** P0  
**Stories:** 3  
**Estimated Duration:** 4 days  
**Dependencies:** EPIC-002

#### STORY-009: Unify Classification Thresholds

**Files:**
- `src/solstein/analytics/scoring.py`
- `src/solstein/analytics/classification.py`
- `src/solstein/constants.py`

**What to do:**
1. Find all threshold definitions across files
2. Move all thresholds to `constants.py` as named constants
3. Replace inline thresholds with constant references
4. Ensure Phoenix/Salt/Lead classification uses same thresholds everywhere

**Acceptance Criteria:**
- [ ] Single source of truth for all thresholds
- [ ] `grep -r "0.7" src/solstein/analytics/` shows only constant references
- [ ] All classification tests pass
- [ ] No behavioral changes (pure refactoring)

**QA Scenario:**
```bash
pytest tests/unit/test_scoring.py -v -k classification
pytest tests/unit/test_classification.py -v
```

---

#### STORY-010: Eliminate Scoring Duplication

**Files:**
- `src/solstein/analytics/scoring.py`
- `src/solstein/analytics/scorers/`

**What to do:**
1. Identify duplicate scoring logic across modules
2. Extract common logic to shared functions
3. Ensure single implementation of each scoring algorithm
4. Update imports

**Acceptance Criteria:**
- [ ] No duplicate scoring functions
- [ ] All scorers use shared utilities
- [ ] Test coverage maintained
- [ ] Performance unchanged

---

#### STORY-011: Name and Document Scoring Constants

**Files:**
- `src/solstein/constants.py`

**What to do:**
1. Replace all magic numbers with named constants
2. Add docstrings explaining business rationale
3. Group related constants logically
4. Add type hints

**Acceptance Criteria:**
- [ ] Zero magic numbers in scoring code
- [ ] All constants have descriptive names
- [ ] All constants have docstrings
- [ ] `pylint src/solstein/constants.py` passes

---

### EPIC-004: Data Integrity & Atomicity — AGENT: `deep`

**Priority:** P0  
**Stories:** 3  
**Estimated Duration:** 5 days  
**Dependencies:** EPIC-002

#### STORY-012: Fix Dual-Write Atomicity

**Files:**
- `src/solstein/research_dual_write.py`

**What to do:**
1. Wrap dual-write operations in database transactions
2. Use `async with session.begin():` pattern
3. Ensure rollback on any failure
4. Add retry logic with exponential backoff

**Acceptance Criteria:**
- [ ] Database operations are atomic
- [ ] Partial writes impossible
- [ ] Rollback tested and working
- [ ] Retry logic handles transient failures

**QA Scenario:**
```python
# Test atomic rollback
with mock.patch('session.commit') as mock_commit:
    mock_commit.side_effect = Exception("DB Error")
    # Should rollback, not leave partial data
```

---

#### STORY-013: Fix Conflict Resolution Logic

**Files:**
- `src/solstein/research_dual_write.py`
- `src/solstein/infrastructure/conflict_resolution.py`

**What to do:**
1. Review current conflict resolution algorithm
2. Fix edge cases in timestamp comparison
3. Add proper tie-breaking rules
4. Add comprehensive tests

**Acceptance Criteria:**
- [ ] Conflict resolution deterministic
- [ ] All edge cases handled
- [ ] Unit tests for conflict scenarios
- [ ] Documentation of resolution rules

---

#### STORY-014: Remove Hardcoded Date Path

**Files:**
- `src/solstein/data_loader.py`

**What to do:**
1. Replace hardcoded date paths with config-driven paths
2. Add path template configuration
3. Update all references
4. Add validation

**Acceptance Criteria:**
- [ ] No hardcoded dates in data paths
- [ ] Paths configurable via settings
- [ ] Backward compatibility maintained

---

## Phase 2: Security & Identity (Weeks 3-4)

### EPIC-020: Supabase Auth Migration — AGENT: `unspecified-high`

**Priority:** P1  
**Stories:** 4  
**Estimated Duration:** 8 days  
**Dependencies:** EPIC-002

#### STORY-067: Migrate to Supabase Auth

**Files:**
- `src/solstein/api/routers/auth.py`
- `src/solstein/security/`
- `src/solstein/infrastructure/database_models.py` (add User model)

**What to do:**
1. Install `supabase-py` dependency
2. Create Supabase client wrapper
3. Replace JWT handler with Supabase auth
4. Add user model linked to Supabase auth
5. Migration script for existing users

**Acceptance Criteria:**
- [ ] User registration via Supabase
- [ ] Login returns Supabase JWT
- [ ] Protected endpoints validate Supabase JWT
- [ ] User data synced to local DB

**QA Scenario:**
```bash
# Test full auth flow
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!"}'

# Should return JWT
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!"}' | jq '.access_token'
```

---

#### STORY-068: Remove Auth Bypass + JWT Middleware

**Files:**
- `src/solstein/api/routers/auth.py`
- `src/solstein/api/dependencies.py`

**What to do:**
1. Remove demo auth bypass code
2. Implement proper password validation
3. Add JWT middleware for all protected routes
4. Update dependency injection

**Acceptance Criteria:**
- [ ] Invalid credentials rejected
- [ ] Valid credentials accepted
- [ ] All protected routes require auth
- [ ] Middleware validates JWT signature

---

#### STORY-069: Error Handling Sanitization

**Files:**
- `src/solstein/api/exceptions.py`
- `src/solstein/api/main.py`

**What to do:**
1. Create custom exception handlers
2. Sanitize error responses (no stack traces)
3. Log full errors server-side
4. Return user-friendly messages

**Acceptance Criteria:**
- [ ] Stack traces never exposed to clients
- [ ] Error responses are generic but helpful
- [ ] Full errors logged with correlation IDs
- [ ] Different error types handled appropriately

---

#### STORY-070: Fix SSRF Vulnerability

**Files:**
- `src/solstein/agents/web_search_agent.py`
- `src/solstein/agents/website_agent.py`

**What to do:**
1. Add URL validation (whitelist/blacklist)
2. Block internal IP ranges
3. Block file:// protocol
4. Add request timeouts

**Acceptance Criteria:**
- [ ] Internal IPs blocked (10.x, 192.168.x, etc.)
- [ ] File protocol blocked
- [ ] Metadata services blocked (169.254.x)
- [ ] Valid URLs work normally

---

### EPIC-019: Multi-Tenancy — AGENT: `unspecified-high`

**Priority:** P1  
**Stories:** 4  
**Estimated Duration:** 6 days  
**Dependencies:** EPIC-020

#### STORY-063: Define Tenant Model

**Files:**
- `src/solstein/infrastructure/database_models.py`
- `src/solstein/domain/models.py`

**What to do:**
1. Create Tenant ORM model
2. Add tenant_id to all existing models
3. Create tenant-user relationship
4. Add tenant context to domain models

**Acceptance Criteria:**
- [ ] Tenant model exists
- [ ] All entities have tenant_id
- [ ] Relationships properly defined
- [ ] Migration script created

---

#### STORY-064: Supabase RLS Policies

**Files:**
- Supabase dashboard (manual)
- `supabase/migrations/`

**What to do:**
1. Create RLS policies for all tables
2. Policies enforce tenant isolation
3. Test policies with different tenants
4. Document policy rules

**Acceptance Criteria:**
- [ ] RLS enabled on all tables
- [ ] User A cannot see User B's data
- [ ] Policies tested with real queries
- [ ] Performance impact acceptable

---

#### STORY-065: Tenant-Scoped API Keys

**Files:**
- `src/solstein/security/api_keys.py`
- `src/solstein/infrastructure/database_models.py`

**What to do:**
1. Add tenant_id to API key model
2. Validate API key belongs to tenant
3. Update key generation to include tenant
4. Add key rotation

**Acceptance Criteria:**
- [ ] API keys scoped to tenant
- [ ] Cross-tenant key usage blocked
- [ ] Key rotation works
- [ ] Audit log tracks key usage

---

#### STORY-066: Tenant Isolation in Jobs

**Files:**
- `src/solstein/worker_tasks.py`
- `src/solstein/celery_config.py`

**What to do:**
1. Pass tenant context to Celery tasks
2. Ensure jobs respect tenant boundaries
3. Add tenant to job metadata
4. Isolate job results by tenant

**Acceptance Criteria:**
- [ ] Jobs run in tenant context
- [ ] Job results isolated by tenant
- [ ] Cross-tenant job access blocked
- [ ] Job queue per tenant (optional)

---

## Phase 3: Modern Data Layer (Weeks 5-6)

### EPIC-023: pgvector Semantic Search — AGENT: `unspecified-high`

**Priority:** P2  
**Stories:** 3  
**Estimated Duration:** 5 days  
**Dependencies:** EPIC-019

#### STORY-080: Add pgvector Extension

**Files:**
- `supabase/migrations/`
- `src/solstein/infrastructure/database.py`

**What to do:**
1. Create migration to enable pgvector extension
2. Add vector column to companies table
3. Create vector index
4. Update SQLAlchemy models

**Acceptance Criteria:**
- [ ] pgvector extension enabled
- [ ] Vector column exists
- [ ] Index created for performance
- [ ] SQLAlchemy can read/write vectors

---

#### STORY-081: Generate Embeddings During Research

**Files:**
- `src/solstein/research/`
- `src/solstein/llm/embeddings.py` (new)

**What to do:**
1. Create embedding service using OpenAI/Anthropic
2. Generate embeddings during company research
3. Store embeddings in pgvector
4. Batch embedding generation

**Acceptance Criteria:**
- [ ] Embeddings generated for new companies
- [ ] Embeddings stored in pgvector
- [ ] Batch processing efficient
- [ ] Fallback if embedding service fails

---

#### STORY-082: Semantic Search Endpoint

**Files:**
- `src/solstein/api/routers/market.py`

**What to do:**
1. Add semantic search endpoint
2. Convert query to embedding
3. Query pgvector for similar companies
4. Return ranked results

**Acceptance Criteria:**
- [ ] Endpoint accepts text query
- [ ] Returns semantically similar companies
- [ ] Response time <500ms
- [ ] Results ranked by similarity

---

### EPIC-024: Supabase Realtime — AGENT: `quick`

**Priority:** P2  
**Stories:** 2  
**Estimated Duration:** 3 days  
**Dependencies:** EPIC-019

#### STORY-083: Research Job Status Table

**Files:**
- `src/solstein/infrastructure/database_models.py`

**What to do:**
1. Create job status table
2. Add realtime publication
3. Link to research runs
4. Add status history

**Acceptance Criteria:**
- [ ] Table exists with proper schema
- [ ] Realtime publication enabled
- [ ] Status updates tracked
- [ ] Foreign keys properly set

---

#### STORY-084: Realtime Subscriptions

**Files:**
- `src/solstein/api/routers/jobs.py`
- Frontend (if applicable)

**What to do:**
1. Add WebSocket endpoint for job updates
2. Subscribe to Supabase realtime
3. Broadcast updates to clients
4. Handle reconnection

**Acceptance Criteria:**
- [ ] WebSocket connection works
- [ ] Job updates received in real-time
- [ ] Reconnection handled gracefully
- [ ] Multiple clients can subscribe

---

### EPIC-030: Export Pipeline — AGENT: `unspecified-high`

**Priority:** P2  
**Stories:** 5  
**Estimated Duration:** 7 days  
**Dependencies:** EPIC-025 (DLQ)

#### STORY-111: Async Export Celery Tasks

**Files:**
- `src/solstein/exporters/`
- `src/solstein/worker_tasks.py`

**What to do:**
1. Move export generation to Celery
2. Create export job tracking
3. Return job ID immediately
4. Process export in background

**Acceptance Criteria:**
- [ ] Export endpoint returns job ID
- [ ] Export runs async
- [ ] No timeout on large exports
- [ ] Job status trackable

---

#### STORY-112: Streaming Excel Export

**Files:**
- `src/solstein/exporters/excel.py`

**What to do:**
1. Implement streaming Excel generation
2. Process companies in chunks
3. Write to temp file
4. Upload to storage

**Acceptance Criteria:**
- [ ] Large exports stream successfully
- [ ] Memory usage bounded
- [ ] Progress trackable
- [ ] No OOM errors

---

## Phase 4: Intelligent Agents (Weeks 7-8)

### EPIC-021: Modern LLM Stack — AGENT: `unspecified-high`

**Priority:** P1  
**Stories:** 5  
**Estimated Duration:** 8 days  
**Dependencies:** EPIC-003

#### STORY-071: Anthropic SDK Migration

**Files:**
- `src/solstein/llm/` (replace enhanced_client.py)

**What to do:**
1. Install `anthropic` SDK
2. Create new client wrapper
3. Replace custom LLM client
4. Maintain backward compatibility

**Acceptance Criteria:**
- [ ] Anthropic SDK integrated
- [ ] All existing tests pass
- [ ] Multi-provider support maintained
- [ ] Performance improved

---

#### STORY-072: Instructor Structured Outputs

**Files:**
- `src/solstein/llm/client.py`
- `src/solstein/domain/models.py`

**What to do:**
1. Install `instructor` library
2. Create structured output schemas
3. Integrate with LLM client
4. Validate all outputs

**Acceptance Criteria:**
- [ ] Structured outputs work
- [ ] Pydantic validation on all responses
- [ ] Retry on validation failure
- [ ] Type safety throughout

---

#### STORY-073: Langfuse Integration

**Files:**
- `src/solstein/llm/client.py`

**What to do:**
1. Install `langfuse` SDK
2. Add cost tracking
3. Add prompt versioning
4. Add tracing

**Acceptance Criteria:**
- [ ] Costs tracked per request
- [ ] Prompts versioned
- [ ] Traces visible in Langfuse
- [ ] No PII in traces

---

### EPIC-022: LangGraph Orchestration — AGENT: `deep`

**Priority:** P2  
**Stories:** 4  
**Estimated Duration:** 10 days  
**Dependencies:** EPIC-021

#### STORY-076: LangGraph Architecture

**Files:**
- `src/solstein/agents/langgraph/` (new directory)

**What to do:**
1. Design graph structure
2. Define state management
3. Create node interfaces
4. Add checkpointing support

**Acceptance Criteria:**
- [ ] Graph structure defined
- [ ] State management works
- [ ] Nodes composable
- [ ] Documentation complete

---

#### STORY-077: Migrate Coordinator to LangGraph

**Files:**
- `src/solstein/agents/coordinator_agent.py`
- `src/solstein/agents/langgraph/coordinator.py`

**What to do:**
1. Rewrite coordinator as LangGraph
2. Migrate existing logic
3. Maintain API compatibility
4. Add comprehensive tests

**Acceptance Criteria:**
- [ ] Coordinator uses LangGraph
- [ ] All existing tests pass
- [ ] Performance maintained
- [ ] New features possible

---

#### STORY-078: Implement Real Agent Nodes

**Files:**
- `src/solstein/agents/langgraph/nodes/` (new)

**What to do:**
1. Replace 7 stub agents with real implementations
2. Each agent as LangGraph node
3. Real data source integration
4. Error handling and retries

**Acceptance Criteria:**
- [ ] 7 stub agents replaced
- [ ] Real data sources used
- [ ] Nodes composable
- [ ] Comprehensive tests

---

## Phase 5: Production Readiness (Weeks 9-10)

### EPIC-025: Worker Reliability — AGENT: `quick`

**Priority:** P1  
**Stories:** 5  
**Estimated Duration:** 4 days  
**Dependencies:** None

#### STORY-088: Persistent Dead Letter Queue

**Files:**
- `src/solstein/infrastructure/database_models.py`
- `src/solstein/worker_tasks.py`

**What to do:**
1. Create DLQ table in database
2. Store failed tasks with context
3. Add retry mechanism
4. Add DLQ monitoring

**Acceptance Criteria:**
- [ ] Failed tasks persisted to DB
- [ ] Full context preserved
- [ ] Retry mechanism works
- [ ] DLQ queryable

---

#### STORY-089: Task Acks Late Configuration

**Files:**
- `src/solstein/celery_config.py`

**What to do:**
1. Set `task_acks_late = True`
2. Set `task_reject_on_worker_lost = True`
3. Test worker restart scenario
4. Document behavior

**Acceptance Criteria:**
- [ ] Tasks ack after completion
- [ ] No lost tasks on worker restart
- [ ] Configuration tested
- [ ] Documentation updated

---

### EPIC-027: CI/CD Automation — AGENT: `quick`

**Priority:** P1  
**Stories:** 4  
**Estimated Duration:** 3 days  
**Dependencies:** None

#### STORY-059: Dockerize Application

**Files:**
- `Dockerfile`
- `docker-compose.yml`

**What to do:**
1. Create multi-stage Dockerfile
2. Create docker-compose with all services
3. Add health checks
4. Document usage

**Acceptance Criteria:**
- [ ] `docker-compose up` works
- [ ] All services start
- [ ] Health checks pass
- [ ] Documentation complete

---

#### STORY-061: CI Pipeline

**Files:**
- `.github/workflows/ci.yml`

**What to do:**
1. Create GitHub Actions workflow
2. Run tests on PR
3. Run linting
4. Run type checking

**Acceptance Criteria:**
- [ ] CI runs on every PR
- [ ] All checks pass
- [ ] Status reported
- [ ] Blocking on failure

---

## Phase 6: Business Value (Weeks 11-12)

### EPIC-038: AI-Readiness Framework — AGENT: `ultrabrain`

**Priority:** P1  
**Stories:** 4  
**Estimated Duration:** 8 days  
**Dependencies:** EPIC-021, EPIC-007

#### STORY-145: Portfolio AI-Readiness Scoring

**Files:**
- `src/solstein/analytics/ai_readiness/` (new)

**What to do:**
1. Research AI readiness dimensions
2. Create scoring model
3. Implement scoring algorithm
4. Add comprehensive tests

**Acceptance Criteria:**
- [ ] Scoring model defined
- [ ] Algorithm implemented
- [ ] Tests comprehensive
- [ ] Results validated

---

#### STORY-146: Transformation Readiness Calculator

**Files:**
- `src/solstein/api/routers/ai_readiness.py` (new)

**What to do:**
1. Create calculator endpoint
2. Implement calculation logic
3. Add input validation
4. Return actionable insights

**Acceptance Criteria:**
- [ ] Calculator functional
- [ ] Results meaningful
- [ ] API documented
- [ ] Tests pass

---

### EPIC-039: Energy Sector — AGENT: `unspecified-high`

**Priority:** P1  
**Stories:** 4  
**Estimated Duration:** 6 days  
**Dependencies:** EPIC-003

#### STORY-149: Energy Compliance Module

**Files:**
- `src/solstein/analytics/energy/` (new)

**What to do:**
1. Research energy compliance requirements
2. Create compliance scoring
3. Add regulatory tracking
4. Implement rules engine

**Acceptance Criteria:**
- [ ] Compliance rules defined
- [ ] Scoring implemented
- [ ] Regulations tracked
- [ ] Tests comprehensive

---

## Quick Reference: Agent Commands

### Start Work on Epic

```bash
# For quick epics
/start-work epic-002-configuration-integrity

# For complex epics  
/start-work epic-020-supabase-auth-migration

# For architectural epics
/start-work epic-022-langraph-agent-orchestration
```

### Monitor Progress

```bash
# Update backlog metrics
python backlog/scripts/update-backlog-metrics.py

# Check test status
pytest --tb=short -q

# Check code quality
make check-all
```

### Emergency Rollback

```bash
# Rollback to last known good state
git log --oneline -10
git reset --hard <commit-hash>
```

---

## Success Criteria by Phase

| Phase | Key Metric | Target |
|-------|-----------|--------|
| 1 | Config errors | 0 |
| 1 | Test pass rate | >95% |
| 2 | Security audit | Pass |
| 2 | Auth bypass attempts | 0% success |
| 3 | Export timeout rate | 0% |
| 3 | Search response time | <500ms |
| 4 | Agent success rate | >90% |
| 4 | LLM cost per request | <$0.50 |
| 5 | Worker reliability | >99% |
| 5 | Deploy time | <10 min |
| 6 | User satisfaction | >4.0/5 |

---

## Next Action

**Execute immediately:**

1. Start Phase 1 with EPIC-002
2. Run agents in parallel where possible
3. Monitor via backlog dashboard
4. Proceed through phases sequentially

**Command to begin:**
```
/start-work epic-002-configuration-integrity
```

---

*This plan is complete and ready for autonomous execution. No human confirmation required.*
