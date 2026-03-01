# Epic Implementation Master Plan

> Comprehensive autonomous execution plan for all 44 epics across 6 milestones.
> **Version:** 2.0 | **Created:** 2026-03-01 | **Estimated Duration:** 12 weeks

---

## Executive Summary

This plan provides a complete roadmap for implementing all 44 epics (165 stories) in the Solstein backlog. The plan is structured for **autonomous execution** by Sisyphus agents with minimal human intervention.

### Key Principles

1. **Foundation First** — No work on dependent epics until foundations are solid
2. **Parallel Execution** — Maximize throughput by grouping independent work
3. **Verification at Every Step** — Each task includes automated QA scenarios
4. **Rollback Safety** — Every change is reversible; database migrations are backward-compatible
5. **Documentation as Code** — All decisions recorded in ADRs

---

## Current State Analysis

### Critical Issues Found

| Issue | Location | Impact | Epic |
|-------|----------|--------|------|
| **Duplicate class bodies in config.py** | Lines 31-56 | First definition silently ignored | EPIC-002 |
| **Auth bypass** | `api/routers/auth.py:57` | Any credentials accepted | EPIC-020 |
| **661-line custom LLM client** | `llm/enhanced_client.py` | Unmaintainable, no structured outputs | EPIC-021 |
| **7 stub agents** | `agents/` directory | Return hardcoded mock data | EPIC-022 |
| **In-memory DLQ** | `worker_tasks.py` | Lost on restart | EPIC-025 |
| **No multi-tenancy** | Database models | Data isolation risk | EPIC-019 |

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        API Layer (FastAPI)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Routers    │  │  Middleware  │  │ Dependencies │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Agents     │    │   Services   │    │  Repository  │
│  (7 stubs)   │    │  (Business)  │    │   (SQLAlch)  │
└──────────────┘    └──────────────┘    └──────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Infrastructure Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  PostgreSQL  │  │    Redis     │  │  Celery      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

## Execution Waves

### Wave 1: Foundation (Weeks 1-2) — CRITICAL PATH

**Goal:** Establish clean, working foundation. All subsequent work depends on this.

#### Parallel Group A: Configuration (MUST COMPLETE FIRST)

- [ ] **1.1** STORY-006: Fix Duplicate Config Class Bodies
  - **Agent:** quick
  - **Files:** `src/solstein/config.py`
  - **QA:** Run `python -c "from solstein.config import get_settings; print('OK')"`
  - **Risk:** Medium — Config is loaded everywhere

- [ ] **1.2** STORY-007: Remove Hardcoded Credentials  
  - **Agent:** quick
  - **Files:** `src/solstein/config.py`, `.env.example`
  - **QA:** `grep -r "postgres:postgres" src/` returns nothing
  - **Risk:** High — Must not break local dev

- [ ] **1.3** STORY-008: Mandatory Startup Validation
  - **Agent:** quick
  - **Files:** `src/solstein/config.py`, `src/solstein/api/main.py`
  - **QA:** Start without env vars → fails fast with clear error
  - **Risk:** Medium — Add to startup sequence

#### Parallel Group B: Core Product Correctness

- [ ] **1.4** STORY-009: Unify Classification Thresholds
  - **Agent:** quick
  - **Files:** `src/solstein/analytics/`, `src/solstein/domain/scoring/`
  - **QA:** All scoring tests pass; thresholds consistent
  - **Risk:** Medium — Business logic change

- [ ] **1.5** STORY-010: Eliminate Scoring Duplication
  - **Agent:** quick
  - **Files:** Scoring modules
  - **QA:** Single source of truth for scoring
  - **Risk:** Low — Refactoring only

- [ ] **1.6** STORY-011: Name and Document Scoring Constants
  - **Agent:** quick
  - **Files:** `src/solstein/constants.py`
  - **QA:** All magic numbers named
  - **Risk:** Low — Documentation

#### Parallel Group C: Data Integrity

- [ ] **1.7** STORY-012: Fix Dual-Write Atomicity
  - **Agent:** unspecified-high
  - **Files:** `src/solstein/research_dual_write.py`
  - **QA:** Database transactions rollback on failure
  - **Risk:** High — Data integrity critical

- [ ] **1.8** STORY-013: Fix Conflict Resolution Logic
  - **Agent:** quick
  - **Files:** Conflict resolution module
  - **QA:** Unit tests for all conflict scenarios
  - **Risk:** Medium — Business logic

- [ ] **1.9** STORY-014: Remove Hardcoded Date Path
  - **Agent:** quick
  - **Files:** Data loader
  - **QA:** Config-driven paths work
  - **Risk:** Low — Simple change

**Wave 1 Exit Criteria:**
- [ ] Config loads without errors
- [ ] No hardcoded credentials in source
- [ ] All tests pass
- [ ] Scoring is consistent
- [ ] Database writes are atomic

---

### Wave 2: Security & Identity (Weeks 3-4) — CRITICAL PATH

**Goal:** Production-grade authentication and multi-tenancy.

**Prerequisite:** Wave 1 complete (clean config)

#### Parallel Group A: Supabase Auth Migration

- [ ] **2.1** STORY-067: Migrate to Supabase Auth
  - **Agent:** unspecified-high
  - **Files:** `src/solstein/api/routers/auth.py`, `src/solstein/security/`
  - **Dependencies:** Supabase project setup
  - **QA:** 
    - Register user via Supabase
    - Login returns valid JWT
    - Protected endpoints require auth
  - **Risk:** High — Core security

- [ ] **2.2** STORY-068: Remove Auth Bypass + JWT Middleware
  - **Agent:** quick
  - **Files:** `src/solstein/api/routers/auth.py`
  - **QA:** 
    - Invalid credentials rejected
    - Valid credentials work
    - Middleware validates JWT
  - **Risk:** High — Security critical

- [ ] **2.3** STORY-069: Error Handling Sanitization
  - **Agent:** quick
  - **Files:** Error handlers
  - **QA:** Stack traces not exposed to clients
  - **Risk:** Medium — Security

- [ ] **2.4** STORY-070: Fix SSRF Vulnerability
  - **Agent:** quick
  - **Files:** Web agents
  - **QA:** 
    - SSRF attempt blocked
    - Valid URLs work
  - **Risk:** High — Security

#### Parallel Group B: Multi-Tenancy

- [ ] **2.5** STORY-063: Define Tenant Model
  - **Agent:** quick
  - **Files:** Database models
  - **QA:** Tenant model exists, relationships correct
  - **Risk:** Medium — Schema change

- [ ] **2.6** STORY-064: Supabase RLS Policies
  - **Agent:** unspecified-high
  - **Files:** Database migrations, Supabase config
  - **QA:** 
    - User A cannot see User B's data
    - RLS policies enforced
  - **Risk:** High — Data isolation

- [ ] **2.7** STORY-065: Tenant-Scoped API Keys
  - **Agent:** quick
  - **Files:** API key management
  - **QA:** API keys scoped to tenant
  - **Risk:** Medium — Security

- [ ] **2.8** STORY-066: Tenant Isolation in Research Jobs
  - **Agent:** quick
  - **Files:** Celery tasks
  - **QA:** Jobs respect tenant boundaries
  - **Risk:** Medium — Data isolation

**Wave 2 Exit Criteria:**
- [ ] Authentication works end-to-end
- [ ] No auth bypass
- [ ] Multi-tenancy enforced
- [ ] Security audit passed

---

### Wave 3: Modern Data Layer (Weeks 5-6)

**Goal:** Vector search, realtime updates, async exports.

**Prerequisite:** Wave 2 complete (auth + tenancy)

#### Parallel Group A: pgvector Semantic Search

- [ ] **3.1** STORY-080: Add pgvector Extension
  - **Agent:** quick
  - **Files:** Database migrations
  - **QA:** `SELECT * FROM pg_extension WHERE extname = 'vector'`
  - **Risk:** Low — Infrastructure

- [ ] **3.2** STORY-081: Generate Embeddings During Research
  - **Agent:** unspecified-high
  - **Files:** Research pipeline
  - **QA:** Embeddings stored for new companies
  - **Risk:** Medium — Performance impact

- [ ] **3.3** STORY-082: Semantic Search Endpoint
  - **Agent:** quick
  - **Files:** API routers
  - **QA:** 
    - Semantic search returns results
    - Response time <500ms
  - **Risk:** Low — New feature

#### Parallel Group B: Supabase Realtime

- [ ] **3.4** STORY-083: Research Job Status Table
  - **Agent:** quick
  - **Files:** Database models
  - **QA:** Table exists, schema correct
  - **Risk:** Low — Schema change

- [ ] **3.5** STORY-084: Realtime Subscriptions
  - **Agent:** quick
  - **Files:** Frontend, API
  - **QA:** 
    - Job status updates in real-time
    - No polling needed
  - **Risk:** Medium — New technology

#### Parallel Group C: Export Pipeline

- [ ] **3.6** STORY-111: Async Export Celery Tasks
  - **Agent:** unspecified-high
  - **Files:** Export service, Celery
  - **QA:** 
    - Export runs async
    - No timeout on large exports
  - **Risk:** Medium — Architecture change

- [ ] **3.7** STORY-112: Streaming Excel Export
  - **Agent:** unspecified-high
  - **Files:** Excel exporter
  - **QA:** 
    - Large exports stream successfully
    - Memory usage bounded
  - **Risk:** Medium — Performance

- [ ] **3.8** STORY-113: Export Status Tracking
  - **Agent:** quick
  - **Files:** Export service
  - **QA:** 
    - Export status visible
    - Download links work
  - **Risk:** Low — Feature

**Wave 3 Exit Criteria:**
- [ ] Semantic search functional
- [ ] Realtime job status working
- [ ] Exports async and reliable
- [ ] No timeouts on large datasets

---

### Wave 4: Intelligent Agents (Weeks 7-8)

**Goal:** Modern LLM stack with Anthropic SDK and LangGraph.

**Prerequisite:** Wave 3 complete (data layer stable)

#### Parallel Group A: Modern LLM Stack

- [ ] **4.1** STORY-071: Anthropic SDK Migration
  - **Agent:** unspecified-high
  - **Files:** `src/solstein/llm/`
  - **QA:** 
    - SDK client works
    - All providers functional
  - **Risk:** High — Core infrastructure

- [ ] **4.2** STORY-072: Instructor Structured Outputs
  - **Agent:** quick
  - **Files:** LLM client
  - **QA:** 
    - Structured outputs validated
    - Pydantic models work
  - **Risk:** Medium — New library

- [ ] **4.3** STORY-073: Langfuse Integration
  - **Agent:** quick
  - **Files:** LLM client
  - **QA:** 
    - Costs tracked
    - Prompts versioned
  - **Risk:** Low — Observability

- [ ] **4.4** STORY-075: Multi-Provider Fallback
  - **Agent:** quick
  - **Files:** LLM client
  - **QA:** 
    - Fallback works on failure
    - All providers tested
  - **Risk:** Medium — Reliability

#### Parallel Group B: LangGraph Orchestration

- [ ] **4.5** STORY-076: LangGraph Architecture
  - **Agent:** deep
  - **Files:** New `agents/langgraph/` module
  - **QA:** 
    - Graph structure defined
    - State management works
  - **Risk:** High — Architecture

- [ ] **4.6** STORY-077: Migrate Coordinator to LangGraph
  - **Agent:** unspecified-high
  - **Files:** `agents/coordinator_agent.py`
  - **QA:** 
    - Coordinator uses LangGraph
    - All existing tests pass
  - **Risk:** High — Core logic

- [ ] **4.7** STORY-078: Implement Real Agent Nodes
  - **Agent:** unspecified-high
  - **Files:** Individual agents
  - **QA:** 
    - 7 stub agents replaced
    - Real data sources used
  - **Risk:** High — Major feature

- [ ] **4.8** STORY-079: Checkpointing + Human-in-Loop
  - **Agent:** quick
  - **Files:** LangGraph config
  - **QA:** 
    - State checkpointed
    - Human approval works
  - **Risk:** Medium — UX

**Wave 4 Exit Criteria:**
- [ ] Anthropic SDK working
- [ ] Structured outputs validated
- [ ] LangGraph orchestration functional
- [ ] 7 stub agents replaced
- [ ] Human-in-the-loop working

---

### Wave 5: Production Readiness (Weeks 9-10)

**Goal:** Workers, CI/CD, observability.

**Prerequisite:** Wave 4 complete (agents stable)

#### Parallel Group A: Worker Reliability

- [ ] **5.1** STORY-088: Persistent Dead Letter Queue
  - **Agent:** quick
  - **Files:** Celery config, database
  - **QA:** 
    - Failed tasks persisted
    - DLQ queryable
  - **Risk:** Medium — Data integrity

- [ ] **5.2** STORY-089: Task Acks Late Configuration
  - **Agent:** quick
  - **Files:** `celery_config.py`
  - **QA:** 
    - Tasks ack after completion
    - No lost tasks on restart
  - **Risk:** Low — Config

- [ ] **5.3** STORY-090: Task Idempotency
  - **Agent:** quick
  - **Files:** Celery tasks
  - **QA:** 
    - Duplicate tasks detected
    - No double execution
  - **Risk:** Medium — Logic

- [ ] **5.4** STORY-091: Result Expiry TTL
  - **Agent:** quick
  - **Files:** `celery_config.py`
  - **QA:** 
    - Redis memory bounded
    - Old results cleaned
  - **Risk:** Low — Config

#### Parallel Group B: CI/CD & Infrastructure

- [ ] **5.5** STORY-059: Dockerize Application
  - **Agent:** quick
  - **Files:** `Dockerfile`, `docker-compose.yml`
  - **QA:** 
    - `docker-compose up` works
    - All services start
  - **Risk:** Medium — DevOps

- [ ] **5.6** STORY-061: CI Pipeline
  - **Agent:** quick
  - **Files:** `.github/workflows/`
  - **QA:** 
    - CI runs on PR
    - Quality gates enforced
  - **Risk:** Low — Process

- [ ] **5.7** STORY-097: Automate Migrations
  - **Agent:** quick
  - **Files:** CI workflow
  - **QA:** 
    - Migrations run automatically
    - Rollback tested
  - **Risk:** Medium — Database

#### Parallel Group C: Observability

- [ ] **5.8** STORY-047: Real Health Checks
  - **Agent:** quick
  - **Files:** `monitoring.py`
  - **QA:** 
    - Health check queries DB
    - Returns 503 on failure
  - **Risk:** Low — Monitoring

- [ ] **5.9** STORY-049: Structured Logging
  - **Agent:** quick
  - **Files:** Logging config
  - **QA:** 
    - JSON logs output
    - Correlation IDs present
  - **Risk:** Low — Observability

- [ ] **5.10** STORY-050: OpenTelemetry Tracing
  - **Agent:** quick
  - **Files:** Middleware
  - **QA:** 
    - Traces generated
    - Distributed tracing works
  - **Risk:** Low — Observability

**Wave 5 Exit Criteria:**
- [ ] Workers reliable (no lost tasks)
- [ ] CI/CD pipeline functional
- [ ] Health checks real
- [ ] Observability in place
- [ ] Docker deployment works

---

### Wave 6: Business Value (Weeks 11-12)

**Goal:** AI-readiness framework and energy sector specialization.

**Prerequisite:** Wave 5 complete (platform stable)

#### Parallel Group A: AI-Readiness Framework

- [ ] **6.1** STORY-145: Portfolio AI-Readiness Scoring
  - **Agent:** unspecified-high
  - **Files:** New scoring module
  - **QA:** 
    - Scoring model works
    - Results accurate
  - **Risk:** Medium — Business logic

- [ ] **6.2** STORY-146: Transformation Readiness Calculator
  - **Agent:** quick
  - **Files:** Calculator service
  - **QA:** 
    - Calculator functional
    - Results meaningful
  - **Risk:** Low — Feature

- [ ] **6.3** STORY-147: PE Due Diligence Integration
  - **Agent:** unspecified-high
  - **Files:** Integration module
  - **QA:** 
    - Due diligence workflow works
    - Integration tested
  - **Risk:** Medium — Integration

#### Parallel Group B: Energy Sector

- [ ] **6.4** STORY-149: Energy Compliance Module
  - **Agent:** quick
  - **Files:** Energy domain
  - **QA:** 
    - Compliance scoring works
    - Rules accurate
  - **Risk:** Medium — Domain knowledge

- [ ] **6.5** STORY-150: Energy Forecasting Scoring
  - **Agent:** quick
  - **Files:** Energy domain
  - **QA:** 
    - Forecasting integrated
    - Scores accurate
  - **Risk:** Medium — Domain knowledge

- [ ] **6.6** STORY-151: Trading Platform Assessment
  - **Agent:** quick
  - **Files:** Energy domain
  - **QA:** 
    - Platform assessment works
    - Criteria correct
  - **Risk:** Low — Feature

**Wave 6 Exit Criteria:**
- [ ] AI readiness scoring deployed
- [ ] Energy sector templates live
- [ ] User acceptance testing passed
- [ ] Documentation complete

---

## Dependency Matrix

### Critical Path Dependencies

```
Wave 1 (Foundation)
  └─► Wave 2 (Security)
        └─► Wave 3 (Data Layer)
              └─► Wave 4 (Agents)
                    └─► Wave 5 (Production)
                          └─► Wave 6 (Business Value)
```

### Cross-Wave Dependencies

| Task | Depends On | Type |
|------|------------|------|
| 2.1 (Supabase Auth) | 1.1-1.3 (Clean Config) | Hard |
| 2.6 (RLS Policies) | 2.1 (Auth) | Hard |
| 3.6 (Async Exports) | 5.1 (DLQ) | Soft |
| 4.1 (Anthropic SDK) | 3.x (Data Layer) | Soft |
| 4.6 (LangGraph) | 4.1 (SDK) | Hard |
| 6.x (Business) | 5.x (Production) | Soft |

---

## Risk Mitigation

### High Risk Items

| Item | Risk | Mitigation |
|------|------|------------|
| STORY-067 (Supabase Auth) | Migration complexity | Parallel implementation, feature flags |
| STORY-064 (RLS Policies) | Data isolation failure | Extensive testing, audit queries |
| STORY-071 (Anthropic SDK) | Breaking changes | Pin versions, comprehensive tests |
| STORY-077 (LangGraph) | Learning curve | Spike story, documentation |

### Rollback Strategy

Every wave includes:
1. **Database migrations:** Backward-compatible (add only, never modify)
2. **Feature flags:** New features can be disabled
3. **Blue-green deployment:** Zero-downtime rollback
4. **Database backups:** Before each wave

---

## Success Metrics

### Wave Completion Criteria

| Wave | Metric | Target |
|------|--------|--------|
| 1 | Config errors | 0 |
| 1 | Test pass rate | >95% |
| 2 | Security audit | Pass |
| 2 | Auth bypass | None |
| 3 | Export timeout rate | 0% |
| 3 | Search response time | <500ms |
| 4 | Agent success rate | >90% |
| 4 | LLM response time | <2s |
| 5 | Worker reliability | >99% |
| 5 | Deploy time | <10min |
| 6 | User satisfaction | >4.0/5 |

---

## Execution Commands

### Start Wave

```bash
# 1. Create feature branch
git checkout -b feature/wave-X-description

# 2. Run tests before starting
pytest -xvs

# 3. Implement tasks (via Sisyphus)
/start-work epic-implementation-master-plan

# 4. Verify wave completion
pytest -xvs
make check-all

# 5. Merge to main
git checkout main
git merge --no-ff feature/wave-X-description
```

### Monitoring During Execution

```bash
# Watch test status
watch -n 5 'pytest -q --tb=no'

# Monitor backlog progress
python backlog/scripts/update-backlog-metrics.py

# Check for regressions
git diff --stat HEAD~5
```

---

## Appendix: Story-to-Agent Mapping

| Agent Category | Suitable For | Examples |
|----------------|--------------|----------|
| **quick** | Simple changes, config, docs | STORY-006, STORY-011, STORY-140 |
| **unspecified-high** | Complex features, integrations | STORY-067, STORY-071, STORY-077 |
| **deep** | Architecture, algorithms | STORY-076 (LangGraph), STORY-012 (Atomicity) |
| **visual-engineering** | UI/UX components | STORY-106-110 (Frontend) |
| **ultrabrain** | Research, novel solutions | STORY-145 (AI Scoring) |

---

## Next Steps

1. **Review this plan** with stakeholders
2. **Prioritize waves** based on business needs
3. **Start Wave 1** with `/start-work epic-implementation-master-plan`
4. **Monitor progress** via backlog dashboard
5. **Adjust plan** as learnings emerge

---

*This plan is a living document. Update as requirements change or new information emerges.*
