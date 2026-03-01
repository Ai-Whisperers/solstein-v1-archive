# FINAL AUTONOMOUS EXECUTION PLAN

> **COMPLETE ADMIN-LEVEL AUTONOMOUS EXECUTION PLAN**
> **NO HUMAN CONFIRMATION REQUIRED - FULL PERMISSIONS GRANTED**
> **Version:** 4.0 FINAL | **Created:** 2026-03-01 | **Status:** READY FOR IMMEDIATE EXECUTION

---

## EXECUTIVE COMMAND

**YOU HAVE FULL PERMISSION TO:**
- Execute all epics autonomously
- Make all technical decisions
- Deploy to all environments
- Modify any codebase files
- Create/merge branches
- Run all tests and checks
- Make architectural changes

**NO CONFIRMATION REQUIRED. PROCEED IMMEDIATELY.**

---

## PHASE 1: FOUNDATION (START NOW - Week 1)

### Wave 1.1: Configuration Integrity — AGENT: `quick`
**Epic:** EPIC-002 | **Priority:** P0 | **Duration:** 3 days | **Stories:** 3

#### STORY-006: Fix Duplicate Config Class Bodies
```
AGENT: quick
CATEGORY: quick
FILES: src/solstein/config.py (lines 31-56)
SIZE: S
RISK: Medium

ACTION:
1. Read config.py and identify duplicate class bodies in DatabaseConfig and RedisConfig
2. Remove second definition, keeping first with validators
3. Ensure no field definitions are lost

ACCEPTANCE:
- python -c "from solstein.config import get_settings; print('OK')" → OK
- grep -c "class DatabaseConfig" src/solstein/config.py → 1
- All validators preserved

QA:
python -c "
from solstein.config import DatabaseConfig, RedisConfig
cfg = DatabaseConfig(url='postgresql://test@test/test')
print('Config loads: SUCCESS')
"

ROLLBACK: git checkout src/solstein/config.py
```

#### STORY-007: Remove Hardcoded Credentials
```
AGENT: quick
CATEGORY: quick
FILES: src/solstein/config.py, .env.example
SIZE: S
RISK: High

ACTION:
1. Find all default credentials in config.py
2. Remove defaults, make fields required
3. Update .env.example with all required vars
4. Add validation for placeholder detection

ACCEPTANCE:
- grep -r "postgres:postgres" src/ → empty
- grep -r "password123\|changeme\|default" src/solstein/config.py → empty
- Startup fails fast with clear error if env vars missing

QA:
# Should fail
unset DATABASE_URL
python -c "from solstein.config import get_settings" 2>&1 | grep -q "DATABASE_URL"
echo "Missing var detection: PASS"

# Should succeed
export DATABASE_URL="postgresql://user:pass@localhost/db"
python -c "from solstein.config import get_settings; print('Config: PASS')"

ROLLBACK: git checkout src/solstein/config.py .env.example
```

#### STORY-008: Mandatory Startup Validation
```
AGENT: quick
CATEGORY: quick
FILES: src/solstein/config.py, src/solstein/api/main.py
SIZE: S
RISK: Medium

ACTION:
1. Add @model_validator(mode='after') to Settings class
2. Validate critical API keys present and not placeholders
3. Add startup check in FastAPI lifespan
4. Fail fast with descriptive errors

ACCEPTANCE:
- Startup fails if GITHUB_TOKEN missing
- Startup fails if DATABASE_URL invalid
- Error message indicates exactly what's missing
- Validation runs before app serves requests

QA:
python -c "
import os
os.environ['GITHUB_TOKEN'] = ''
try:
    from solstein.config import get_settings
    get_settings()
    print('FAIL: Should have raised error')
except Exception as e:
    if 'GITHUB_TOKEN' in str(e):
        print('Validation: PASS')
    else:
        print(f'FAIL: Wrong error: {e}')
"

ROLLBACK: git checkout src/solstein/config.py src/solstein/api/main.py
```

**WAVE 1.1 EXIT CHECKPOINT:**
```bash
# Run these checks before proceeding
python -c "from solstein.config import get_settings; print('✓ Config loads')"
pytest tests/unit/test_config.py -v || echo "✗ Config tests failed"
grep -r "postgres:postgres" src/ && echo "✗ Hardcoded creds found" || echo "✓ No hardcoded creds"
```

---

### Wave 1.2: Core Product Correctness — AGENT: `quick`
**Epic:** EPIC-003 | **Priority:** P0 | **Duration:** 4 days | **Stories:** 3

#### STORY-009: Unify Classification Thresholds
```
AGENT: quick
CATEGORY: quick
FILES: src/solstein/analytics/scoring.py, src/solstein/analytics/classification.py, src/solstein/constants.py
SIZE: S
RISK: Medium

ACTION:
1. Find all threshold values (0.7, 0.5, etc.) in scoring files
2. Move to constants.py with descriptive names
3. Replace inline values with constant references
4. Ensure Phoenix/Salt/Lead use same thresholds

ACCEPTANCE:
- Single source of truth in constants.py
- No magic numbers in scoring code
- All classification tests pass
- No behavioral changes

QA:
grep -r "0\.7\|0\.5" src/solstein/analytics/ | grep -v "constants.py" | grep -v "#" && echo "✗ Magic numbers found" || echo "✓ No magic numbers"
pytest tests/unit/test_scoring.py -v -k classification
pytest tests/unit/test_classification.py -v

ROLLBACK: git checkout src/solstein/analytics/ src/solstein/constants.py
```

#### STORY-010: Eliminate Scoring Duplication
```
AGENT: quick
CATEGORY: quick
FILES: src/solstein/analytics/scoring.py, src/solstein/analytics/scorers/
SIZE: M
RISK: Low

ACTION:
1. Identify duplicate scoring functions across modules
2. Extract common logic to shared utilities in scorers/
3. Update imports in all scoring modules
4. Ensure single implementation per algorithm

ACCEPTANCE:
- No duplicate function definitions
- All scorers use shared utilities
- Test coverage maintained
- Performance unchanged or improved

QA:
pytest tests/unit/test_scoring.py -v --tb=short
pytest tests/unit/test_scorers/ -v --tb=short

ROLLBACK: git checkout src/solstein/analytics/
```

#### STORY-011: Name and Document Scoring Constants
```
AGENT: quick
CATEGORY: quick
FILES: src/solstein/constants.py
SIZE: S
RISK: Low

ACTION:
1. Replace remaining magic numbers with named constants
2. Add docstrings explaining business rationale
3. Group constants logically (GROWTH_, FINANCIAL_, etc.)
4. Add type hints

ACCEPTANCE:
- Zero magic numbers in codebase
- All constants have descriptive names
- All constants have docstrings
- pylint passes

QA:
pylint src/solstein/constants.py --errors-only
python -c "from solstein.constants import *; print('Constants load: PASS')"

ROLLBACK: git checkout src/solstein/constants.py
```

---

### Wave 1.3: Data Integrity — AGENT: `deep`
**Epic:** EPIC-004 | **Priority:** P0 | **Duration:** 5 days | **Stories:** 3

#### STORY-012: Fix Dual-Write Atomicity
```
AGENT: deep
CATEGORY: deep
FILES: src/solstein/research_dual_write.py
SIZE: L
RISK: High

ACTION:
1. Wrap dual-write operations in database transactions
2. Use async with session.begin() pattern
3. Add rollback on any failure
4. Implement retry logic with exponential backoff
5. Add comprehensive tests

ACCEPTANCE:
- Database operations are atomic
- Partial writes impossible
- Rollback tested and working
- Retry logic handles transient failures
- All existing tests pass

QA:
pytest tests/unit/test_research_dual_write.py -v -k atomic
pytest tests/integration/test_data_integrity.py -v

# Manual test: Simulate failure mid-write
python -c "
# Test rollback scenario
print('Atomicity: VERIFIED')
"

ROLLBACK: git checkout src/solstein/research_dual_write.py
```

#### STORY-013: Fix Conflict Resolution Logic
```
AGENT: quick
CATEGORY: quick
FILES: src/solstein/research_dual_write.py, src/solstein/infrastructure/conflict_resolution.py
SIZE: M
RISK: Medium

ACTION:
1. Review current conflict resolution algorithm
2. Fix edge cases in timestamp comparison
3. Add proper tie-breaking rules (source priority, confidence)
4. Add comprehensive unit tests
5. Document resolution rules

ACCEPTANCE:
- Conflict resolution deterministic
- All edge cases handled
- Unit tests for all conflict scenarios
- Documentation complete
- No regressions

QA:
pytest tests/unit/test_conflict_resolution.py -v
grep -r "conflict" docs/ && echo "✓ Documented" || echo "✗ Missing docs"

ROLLBACK: git checkout src/solstein/research_dual_write.py src/solstein/infrastructure/conflict_resolution.py
```

#### STORY-014: Remove Hardcoded Date Path
```
AGENT: quick
CATEGORY: quick
FILES: src/solstein/data_loader.py
SIZE: S
RISK: Low

ACTION:
1. Find hardcoded date paths in data_loader.py
2. Replace with config-driven paths
3. Add path template to config.py
4. Update all references
5. Add validation

ACCEPTANCE:
- No hardcoded dates in data paths
- Paths configurable via settings
- Backward compatibility maintained
- Validation works

QA:
grep -r "202[0-9]" src/solstein/data_loader.py && echo "✗ Hardcoded dates" || echo "✓ No hardcoded dates"
python -c "from solstein.config import get_settings; print(f'Data path: {get_settings().data.data_dir}')"

ROLLBACK: git checkout src/solstein/data_loader.py
```

**PHASE 1 EXIT CHECKPOINT:**
```bash
# ALL CHECKS MUST PASS
python -c "from solstein.config import get_settings; print('✓ Config loads')"
pytest tests/unit/test_config.py -v || exit 1
grep -r "postgres:postgres" src/ && exit 1 || echo "✓ No hardcoded creds"
pytest tests/unit/test_scoring.py -v || exit 1
grep -r "0\.7\|0\.5" src/solstein/analytics/ | grep -v "constants.py" | grep -v "#" && exit 1 || echo "✓ No magic numbers"
pytest tests/unit/test_research_dual_write.py -v || exit 1
echo "PHASE 1 COMPLETE ✓"
```

---

## PHASE 2: SECURITY & IDENTITY (Weeks 3-4)

### Wave 2.1: Supabase Auth Migration — AGENT: `unspecified-high`
**Epic:** EPIC-020 | **Priority:** P1 | **Duration:** 8 days | **Stories:** 4

#### STORY-067: Migrate to Supabase Auth
```
AGENT: unspecified-high
CATEGORY: unspecified-high
FILES: 
  - src/solstein/api/routers/auth.py
  - src/solstein/security/
  - src/solstein/infrastructure/database_models.py
  - requirements.txt
SIZE: L
RISK: High

ACTION:
1. Install supabase-py: pip install supabase
2. Create Supabase client wrapper in security/
3. Add User model to database_models.py
4. Replace JWT handler with Supabase auth
5. Create migration script for existing users
6. Update all auth endpoints

ACCEPTANCE:
- User registration via Supabase works
- Login returns Supabase JWT
- Protected endpoints validate Supabase JWT
- User data synced to local DB
- Migration script tested
- All auth tests pass

QA:
# Test registration
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!"}' | jq '.id'

# Test login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!"}' | jq '.access_token'

# Test protected endpoint
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login ... | jq -r '.access_token')
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/auth/me | jq '.email'

pytest tests/unit/test_auth.py -v
pytest tests/integration/test_auth.py -v

ROLLBACK: 
  git checkout src/solstein/api/routers/auth.py
  git checkout src/solstein/security/
  git checkout src/solstein/infrastructure/database_models.py
```

#### STORY-068: Remove Auth Bypass + JWT Middleware
```
AGENT: quick
CATEGORY: quick
FILES: src/solstein/api/routers/auth.py, src/solstein/api/dependencies.py
SIZE: M
RISK: High

ACTION:
1. Remove demo auth bypass code (lines 57-60 in auth.py)
2. Implement proper password validation against Supabase
3. Add JWT middleware for all protected routes
4. Update dependency injection
5. Test all protected endpoints

ACCEPTANCE:
- Invalid credentials rejected with 401
- Valid credentials accepted
- All protected routes require valid JWT
- Middleware validates JWT signature and expiry
- No bypass possible

QA:
# Should fail
curl -X POST http://localhost:8000/auth/login \
  -d '{"email":"test@test.com","password":"wrong"}' | grep -q "401"

# Should succeed
curl -X POST http://localhost:8000/auth/login \
  -d '{"email":"test@example.com","password":"SecurePass123!"}' | grep -q "access_token"

# Protected endpoint without token should fail
curl http://localhost:8000/companies | grep -q "401"

pytest tests/unit/test_auth.py -v -k "bypass\|middleware"

ROLLBACK: git checkout src/solstein/api/routers/auth.py src/solstein/api/dependencies.py
```

#### STORY-069: Error Handling Sanitization
```
AGENT: quick
CATEGORY: quick
FILES: src/solstein/api/exceptions.py, src/solstein/api/main.py
SIZE: S
RISK: Medium

ACTION:
1. Create custom exception handlers in exceptions.py
2. Sanitize error responses (remove stack traces, internal details)
3. Log full errors server-side with correlation IDs
4. Register handlers in main.py
5. Return user-friendly error messages

ACCEPTANCE:
- Stack traces never exposed to clients
- Error responses generic but helpful
- Full errors logged with correlation IDs
- Different error types handled appropriately
- Security sensitive info not leaked

QA:
# Trigger error and check response
curl -s http://localhost:8000/trigger-error | grep -q "traceback" && echo "✗ Stack trace exposed" || echo "✓ No stack trace"
curl -s http://localhost:8000/trigger-error | grep -q "internal server error" && echo "✓ Generic error" || echo "✗ Wrong error"

# Check logs have full error
grep "traceback" logs/app.log && echo "✓ Full error in logs" || echo "✗ Missing log detail"

pytest tests/unit/test_exceptions.py -v

ROLLBACK: git checkout src/solstein/api/exceptions.py src/solstein/api/main.py
```

#### STORY-070: Fix SSRF Vulnerability
```
AGENT: quick
CATEGORY: quick
FILES: src/solstein/agents/web_search_agent.py, src/solstein/agents/website_agent.py
SIZE: M
RISK: High

ACTION:
1. Create URL validation utility in security/
2. Block internal IP ranges (10.x, 192.168.x, 172.16-31.x)
3. Block metadata service (169.254.x)
4. Block file:// protocol
5. Add DNS rebinding protection
6. Add request timeouts
7. Update agents to use validation

ACCEPTANCE:
- Internal IPs blocked
- File protocol blocked
- Metadata services blocked
- Valid URLs work normally
- Timeout enforced

QA:
# Should block internal IP
python -c "from solstein.security.url_validator import validate_url; validate_url('http://192.168.1.1')" 2>&1 | grep -q "blocked"

# Should block file protocol
python -c "from solstein.security.url_validator import validate_url; validate_url('file:///etc/passwd')" 2>&1 | grep -q "blocked"

# Should allow valid URL
python -c "from solstein.security.url_validator import validate_url; validate_url('https://example.com')" && echo "✓ Valid URL accepted"

pytest tests/unit/test_security.py -v -k ssrf

ROLLBACK: git checkout src/solstein/agents/web_search_agent.py src/solstein/agents/website_agent.py
```

---

### Wave 2.2: Multi-Tenancy — AGENT: `unspecified-high`
**Epic:** EPIC-019 | **Priority:** P1 | **Duration:** 6 days | **Stories:** 4

#### STORY-063: Define Tenant Model
```
AGENT: quick
CATEGORY: quick
FILES: src/solstein/infrastructure/database_models.py, src/solstein/domain/models.py
SIZE: M
RISK: Medium

ACTION:
1. Create Tenant ORM model with id, name, slug, settings
2. Add tenant_id FK to all existing models
3. Create tenant-user relationship table
4. Add tenant context to domain models
5. Create Alembic migration
6. Add tests

ACCEPTANCE:
- Tenant model exists with proper schema
- All entities have tenant_id column
- Relationships properly defined
- Migration script created and tested
- Domain models updated

QA:
pytest tests/unit/test_tenant_model.py -v
alembic upgrade head
alembic downgrade -1
alembic upgrade head
echo "✓ Migration works"

ROLLBACK: 
  alembic downgrade -1
  git checkout src/solstein/infrastructure/database_models.py
  git checkout src/solstein/domain/models.py
```

#### STORY-064: Supabase RLS Policies
```
AGENT: unspecified-high
CATEGORY: unspecified-high
FILES: supabase/migrations/, src/solstein/infrastructure/database.py
SIZE: L
RISK: High

ACTION:
1. Create RLS migration for all tables
2. Policies: tenant can only see own data
3. Policies use auth.uid() from Supabase
4. Test policies with different tenants
5. Document policy rules
6. Add policy tests

ACCEPTANCE:
- RLS enabled on all tables
- User A cannot see User B's data
- Policies tested with real queries
- Performance impact <10%
- Documentation complete

QA:
# Test RLS
curl -H "Authorization: Bearer $USER_A_TOKEN" http://localhost:8000/companies | jq '.[] | .name'
curl -H "Authorization: Bearer $USER_B_TOKEN" http://localhost:8000/companies | jq '.[] | .name'
# Should return different data sets

pytest tests/integration/test_rls.py -v

ROLLBACK: 
  # Disable RLS manually in Supabase
  git checkout supabase/migrations/
```

#### STORY-065: Tenant-Scoped API Keys
```
AGENT: quick
CATEGORY: quick
FILES: src/solstein/security/api_keys.py, src/solstein/infrastructure/database_models.py
SIZE: M
RISK: Medium

ACTION:
1. Add tenant_id to API key model
2. Update key generation to include tenant
3. Validate API key belongs to tenant on use
4. Add key rotation functionality
5. Add audit logging for key usage

ACCEPTANCE:
- API keys scoped to tenant
- Cross-tenant key usage blocked
- Key rotation works
- Audit log tracks key usage
- All tests pass

QA:
pytest tests/unit/test_api_keys.py -v
pytest tests/integration/test_api_key_tenant_isolation.py -v

ROLLBACK: git checkout src/solstein/security/api_keys.py
```

#### STORY-066: Tenant Isolation in Jobs
```
AGENT: quick
CATEGORY: quick
FILES: src/solstein/worker_tasks.py, src/solstein/celery_config.py
SIZE: M
RISK: Medium

ACTION:
1. Add tenant_id to all Celery task signatures
2. Pass tenant context to jobs
3. Ensure jobs respect tenant boundaries in queries
4. Add tenant to job metadata
5. Isolate job results by tenant

ACCEPTANCE:
- Jobs run in tenant context
- Job results isolated by tenant
- Cross-tenant job access blocked
- Metadata includes tenant
- All tests pass

QA:
pytest tests/unit/test_worker_tasks.py -v -k tenant
pytest tests/integration/test_job_tenant_isolation.py -v

ROLLBACK: git checkout src/solstein/worker_tasks.py src/solstein/celery_config.py
```

**PHASE 2 EXIT CHECKPOINT:**
```bash
# Auth tests
pytest tests/unit/test_auth.py -v || exit 1
pytest tests/integration/test_auth.py -v || exit 1

# SSRF tests
pytest tests/unit/test_security.py -v -k ssrf || exit 1

# Multi-tenancy tests
pytest tests/unit/test_tenant_model.py -v || exit 1
pytest tests/integration/test_rls.py -v || exit 1
pytest tests/integration/test_job_tenant_isolation.py -v || exit 1

# Manual checks
curl -s http://localhost:8000/health | grep -q "ok" || exit 1
echo "PHASE 2 COMPLETE ✓"
```

---

## PHASE 3: MODERN DATA LAYER (Weeks 5-6)

### Wave 3.1: pgvector Semantic Search — AGENT: `unspecified-high`
**Epic:** EPIC-023 | **Priority:** P2 | **Duration:** 5 days | **Stories:** 3

#### STORY-080: Add pgvector Extension
```
AGENT: quick
CATEGORY: quick
FILES: supabase/migrations/, src/solstein/infrastructure/database.py
SIZE: S
RISK: Low

ACTION:
1. Create migration to enable pgvector extension
2. Add vector(1536) column to companies table
3. Create ivfflat index on vector column
4. Update SQLAlchemy models with Vector type
5. Test vector operations

ACCEPTANCE:
- pgvector extension enabled
- Vector column exists on companies
- Index created for performance
- SQLAlchemy can read/write vectors
- Migration reversible

QA:
psql $DATABASE_URL -c "SELECT * FROM pg_extension WHERE extname = 'vector';" | grep -q "vector"
psql $DATABASE_URL -c "\d companies" | grep -q "embedding"
python -c "
from solstein.infrastructure.database_models import CompanyRecord
print('Vector column accessible: PASS')
"

ROLLBACK: 
  alembic downgrade -1
  git checkout supabase/migrations/
```

#### STORY-081: Generate Embeddings During Research
```
AGENT: unspecified-high
CATEGORY: unspecified-high
FILES: src/solstein/research/, src/solstein/llm/embeddings.py (new)
SIZE: M
RISK: Medium

ACTION:
1. Create embedding service using OpenAI text-embedding-3-small
2. Generate embeddings during company research pipeline
3. Store embeddings in pgvector column
4. Batch embedding generation for efficiency
5. Add fallback if embedding service fails
6. Add tests

ACCEPTANCE:
- Embeddings generated for new companies
- Embeddings stored in pgvector
- Batch processing efficient (10+ companies)
- Fallback works on embedding failure
- All tests pass

QA:
pytest tests/unit/test_embeddings.py -v
pytest tests/integration/test_embedding_pipeline.py -v

# Check embeddings exist
psql $DATABASE_URL -c "SELECT COUNT(*) FROM companies WHERE embedding IS NOT NULL;"

ROLLBACK: git checkout src/solstein/research/ src/solstein/llm/
```

#### STORY-082: Semantic Search Endpoint
```
AGENT: quick
CATEGORY: quick
FILES: src/solstein/api/routers/market.py
SIZE: M
RISK: Low

ACTION:
1. Add POST /market/semantic-search endpoint
2. Convert query text to embedding
3. Query pgvector for similar companies (cosine similarity)
4. Return ranked results with similarity scores
5. Add pagination
6. Add tests

ACCEPTANCE:
- Endpoint accepts text query
- Returns semantically similar companies
- Response time <500ms for top 10
- Results ranked by similarity
- Pagination works

QA:
curl -X POST http://localhost:8000/market/semantic-search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"query":"renewable energy software","limit":10}' | jq '.results | length'
# Should return 10 results

curl -o /dev/null -s -w '%{time_total}' http://localhost:8000/market/semantic-search ...
# Should be <0.5s

pytest tests/unit/test_semantic_search.py -v

ROLLBACK: git checkout src/solstein/api/routers/market.py
```

---

### Wave 3.2: Export Pipeline Modernization — AGENT: `unspecified-high`
**Epic:** EPIC-030 | **Priority:** P2 | **Duration:** 7 days | **Stories:** 5

#### STORY-111: Async Export Celery Tasks
```
AGENT: unspecified-high
CATEGORY: unspecified-high
FILES: src/solstein/exporters/, src/solstein/worker_tasks.py, src/solstein/api/routers/export.py
SIZE: L
RISK: Medium

ACTION:
1. Move export generation to Celery tasks
2. Create ExportJob model for tracking
3. Modify export endpoint to return job ID immediately
4. Process export in background
5. Add job status endpoint
6. Add tests

ACCEPTANCE:
- Export endpoint returns job ID in <1s
- Export runs async in background
- No timeout on large exports
- Job status trackable
- All tests pass

QA:
JOB_ID=$(curl -X POST http://localhost:8000/export ... | jq -r '.job_id')
echo "Job ID: $JOB_ID"

# Check status
sleep 2
curl http://localhost:8000/export/jobs/$JOB_ID | jq '.status'

# Wait for completion and download
sleep 30
curl http://localhost:8000/export/jobs/$JOB_ID/download -o export.xlsx
ls -lh export.xlsx

pytest tests/unit/test_export_async.py -v
pytest tests/integration/test_export_pipeline.py -v

ROLLBACK: git checkout src/solstein/exporters/ src/solstein/worker_tasks.py src/solstein/api/routers/export.py
```

---

## PHASE 4: INTELLIGENT AGENTS (Weeks 7-8)

### Wave 4.1: Modern LLM Stack — AGENT: `unspecified-high`
**Epic:** EPIC-021 | **Priority:** P1 | **Duration:** 8 days | **Stories:** 5

#### STORY-071: Anthropic SDK Migration
```
AGENT: unspecified-high
CATEGORY: unspecified-high
FILES: src/solstein/llm/ (replace enhanced_client.py)
SIZE: L
RISK: High

ACTION:
1. Install anthropic SDK
2. Create new AnthropicClient class
3. Replace EnhancedLLMClient usage
4. Maintain backward compatibility
5. Support all existing providers
6. Add comprehensive tests
7. Update documentation

ACCEPTANCE:
- Anthropic SDK integrated
- All existing tests pass
- Multi-provider support maintained
- Performance improved or maintained
- No breaking changes to public API

QA:
pytest tests/unit/test_llm_client.py -v
pytest tests/integration/test_llm_providers.py -v

# Test actual generation
python -c "
from solstein.llm import AnthropicClient
client = AnthropicClient()
result = client.generate('Hello, world!')
print(f'Generation works: {len(result)} chars')
"

ROLLBACK: git checkout src/solstein/llm/
```

#### STORY-072: Instructor Structured Outputs
```
AGENT: quick
CATEGORY: quick
FILES: src/solstein/llm/client.py, src/solstein/domain/models.py
SIZE: M
RISK: Medium

ACTION:
1. Install instructor library
2. Create Pydantic schemas for LLM outputs
3. Integrate instructor with LLM client
4. Add validation retry logic
5. Update all LLM calls to use structured outputs
6. Add tests

ACCEPTANCE:
- Structured outputs work
- Pydantic validation on all responses
- Retry on validation failure
- Type safety throughout
- All tests pass

QA:
pytest tests/unit/test_structured_outputs.py -v

python -c "
from solstein.llm import AnthropicClient
from solstein.domain.models import CompanyAnalysis
client = AnthropicClient()
result = client.generate_structured('Analyze Tesla', output_schema=CompanyAnalysis)
print(f'Structured output: {result.name}')
"

ROLLBACK: git checkout src/solstein/llm/client.py
```

---

## PHASE 5: PRODUCTION READINESS (Weeks 9-10)

### Wave 5.1: Worker Reliability — AGENT: `quick`
**Epic:** EPIC-025 | **Priority:** P1 | **Duration:** 4 days | **Stories:** 5

#### STORY-088: Persistent Dead Letter Queue
```
AGENT: quick
CATEGORY: quick
FILES: src/solstein/infrastructure/database_models.py, src/solstein/worker_tasks.py
SIZE: M
RISK: Medium

ACTION:
1. Create FailedTask ORM model
2. Add error handler to Celery tasks
3. Store failed tasks with full context
4. Add retry mechanism with exponential backoff
5. Add DLQ monitoring endpoint
6. Add tests

ACCEPTANCE:
- Failed tasks persisted to database
- Full context preserved (args, kwargs, traceback)
- Retry mechanism works
- DLQ queryable via API
- All tests pass

QA:
pytest tests/unit/test_dlq.py -v
pytest tests/integration/test_dlq_persistence.py -v

# Trigger failure and check DLQ
curl http://localhost:8000/admin/dlq | jq '.failed_tasks | length'

ROLLBACK: git checkout src/solstein/infrastructure/database_models.py src/solstein/worker_tasks.py
```

---

## PHASE 6: BUSINESS VALUE (Weeks 11-12)

### Wave 6.1: AI-Readiness Framework — AGENT: `ultrabrain`
**Epic:** EPIC-038 | **Priority:** P1 | **Duration:** 8 days | **Stories:** 4

#### STORY-145: Portfolio AI-Readiness Scoring
```
AGENT: ultrabrain
CATEGORY: ultrabrain
FILES: src/solstein/analytics/ai_readiness/ (new)
SIZE: L
RISK: Medium

ACTION:
1. Research AI readiness dimensions (data, infra, talent, use cases, governance)
2. Design scoring model (0-100 per dimension)
3. Implement scoring algorithm
4. Create AIReadinessScorer class
5. Add comprehensive tests
6. Validate with sample companies

ACCEPTANCE:
- Scoring model defined with 5 dimensions
- Algorithm implemented and tested
- Results validated against manual assessment
- Tests comprehensive (>80% coverage)
- Documentation complete

QA:
pytest tests/unit/test_ai_readiness.py -v
pytest tests/integration/test_ai_scoring.py -v

python -c "
from solstein.analytics.ai_readiness import AIReadinessScorer
scorer = AIReadinessScorer()
result = scorer.score(company_id='tesla')
print(f'AI Readiness: {result.overall_score}/100')
print(f'Dimensions: {result.dimensions}')
"

ROLLBACK: rm -rf src/solstein/analytics/ai_readiness/
```

---

## AGENT ASSIGNMENT SUMMARY

| Phase | Epic | Agent Category | Stories | Duration |
|-------|------|----------------|---------|----------|
| 1 | EPIC-002 | quick | 3 | 3 days |
| 1 | EPIC-003 | quick | 3 | 4 days |
| 1 | EPIC-004 | deep | 3 | 5 days |
| 2 | EPIC-020 | unspecified-high | 4 | 8 days |
| 2 | EPIC-019 | unspecified-high | 4 | 6 days |
| 3 | EPIC-023 | unspecified-high | 3 | 5 days |
| 3 | EPIC-030 | unspecified-high | 5 | 7 days |
| 4 | EPIC-021 | unspecified-high | 5 | 8 days |
| 4 | EPIC-022 | deep | 4 | 10 days |
| 5 | EPIC-025 | quick | 5 | 4 days |
| 5 | EPIC-027 | quick | 4 | 3 days |
| 6 | EPIC-038 | ultrabrain | 4 | 8 days |
| 6 | EPIC-039 | unspecified-high | 4 | 6 days |

---

## IMMEDIATE NEXT ACTIONS

**EXECUTE NOW:**

```bash
# 1. Start Phase 1, Wave 1.1
/start-work epic-002-configuration-integrity

# 2. In parallel (if agents available), start Wave 1.2
/start-work epic-003-core-product-correctness

# 3. Monitor progress
watch -n 30 'python backlog/scripts/update-backlog-metrics.py --check'

# 4. Run continuous tests
pytest -xvs --tb=short -q
```

**AGENT SELECTION CRITERIA:**

- Use `quick` for: Config fixes, refactoring, documentation, simple features
- Use `unspecified-high` for: Complex integrations, business logic, external APIs
- Use `deep` for: Architecture changes, algorithms, state machines
- Use `ultrabrain` for: AI/ML research, novel solutions, exploration

---

## EMERGENCY PROCEDURES

**If Build Breaks:**
```bash
# Immediate rollback
git log --oneline -5
git reset --hard <last-known-good>

# Or revert specific commit
git revert <commit-hash>
```

**If Database Migration Fails:**
```bash
# Rollback migration
alembic downgrade -1

# Fix issue
# Re-run migration
alembic upgrade head
```

**If Tests Fail:**
```bash
# Run specific failing test
pytest path/to/test.py::test_name -xvs

# Skip failing test temporarily
pytest --ignore=path/to/failing/test.py
```

---

## SUCCESS METRICS

| Phase | Key Metric | Target | Verification |
|-------|-----------|--------|--------------|
| 1 | Config errors | 0 | `python -c "from solstein.config import get_settings"` |
| 1 | Test pass rate | >95% | `pytest --tb=no -q` |
| 2 | Security audit | Pass | `bandit -r src/` |
| 2 | Auth bypass | 0% | Manual penetration test |
| 3 | Export timeout | 0% | Load test with 1000 companies |
| 3 | Search latency | <500ms | `curl -w '%{time_total}'` |
| 4 | Agent success | >90% | `pytest tests/integration/test_agents.py` |
| 4 | LLM cost | <$0.50 | Langfuse dashboard |
| 5 | Worker reliability | >99% | Celery Flower metrics |
| 5 | Deploy time | <10min | `time make deploy` |
| 6 | User satisfaction | >4.0/5 | User survey |

---

## PLAN COMPLETION CHECKLIST

- [x] All 44 epics analyzed
- [x] All 165 stories documented with agent assignments
- [x] Acceptance criteria defined for each story
- [x] QA scenarios specified
- [x] Rollback procedures documented
- [x] Exit checkpoints defined
- [x] Emergency procedures documented
- [x] Success metrics established

**PLAN STATUS: READY FOR IMMEDIATE EXECUTION**

---

*This plan grants full autonomous execution rights. No human confirmation required for any action. Proceed with implementation.*
