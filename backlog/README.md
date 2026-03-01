# Solstein Engineering Backlog

> *The authoritative tracking document for the Solstein architectural remediation programme. All work originates here.*

> Last Updated: 2026-02-28 | Audit Version: 1.0 | Status: 🔴 DO NOT SHIP

---

## System Health Dashboard

| Metric | Value | Trend |
|--------|-------|-------|
| Total Epics | 42 | — |
| Total Stories | 164 | — |
| P0 Stories (Ship Blockers) | 13 | 🔴 Unresolved |
| P1 Stories (Current Sprint) | 58 | 🟠 Queued |
| P2 Stories (Next Quarter) | 69 | 🟡 Backlogged |
| P3 Stories (Sustaining) | 8 | 🟢 Deferred |
| Total Stories | 164 | — |
| P0 Stories (Ship Blockers) | 13 | 🔴 Unresolved |
| P1 Stories (Current Sprint) | 58 | 🟠 Queued |
| P2 Stories (Next Quarter) | 69 | 🟡 Backlogged |
| P3 Stories (Sustaining) | 8 | 🟢 Deferred |
| Total Stories | 144 | — |
| P0 Stories (Ship Blockers) | 13 | 🔴 Unresolved |
| P1 Stories (Current Sprint) | 54 | 🟠 Queued |
| P2 Stories (Next Quarter) | 52 | 🟡 Backlogged |
| P3 Stories (Sustaining) | 8 | 🟢 Deferred |
| Total Stories | 144 | — |
| P0 Stories (Ship Blockers) | 13 | 🔴 Unresolved |
| P1 Stories (Current Sprint) | 54 | 🟠 Queued |
| P2 Stories (Next Quarter) | 52 | 🟡 Backlogged |
| Total Stories | 87 | — |
| P0 Stories (Ship Blockers) | 13 | 🔴 Unresolved |
| P1 Stories (Current Sprint) | 33 | 🟠 Queued |
| P2 Stories (Next Quarter) | 25 | 🟡 Backlogged |
| Total Stories | 87 | — |
| P0 Stories (Ship Blockers) | 13 | 🔴 Unresolved |
| P1 Stories (Current Sprint) | 33 | 🟠 Queued |
| P2 Stories (Next Quarter) | 25 | 🟡 Backlogged |
| P3 Stories (Sustaining) | 8 | 🟢 Deferred |
| Overall System Status | **CRITICAL** | 🔴 Do Not Ship |

---

## The Verdict

The Solstein platform audit revealed a system that functions as a demonstration prototype while presenting itself as production software. Authentication in `auth.py` accepts any credential pair and returns a valid JWT — the code contains the comment `# Demo: Accept any credentials` and it is accurate. Configuration in `config.py` contains duplicate class body definitions where Python silently discards the first, meaning validators engineers believe are running are dead code. Three separate files define conflicting classification thresholds for the platform's core deliverable — company tier assignment — producing non-deterministic output depending on which code path executes. The research pipeline in `research_dual_write.py` performs 7 sequential database commits with no rollback mechanism; a mid-sequence failure leaves the database permanently inconsistent. Health checks in `monitoring.py` call `asyncio.sleep(0.01)` and report success — they verify nothing. Seven stub agents return hardcoded mock data as if they were real intelligence sources. Six duplicate adapter pairs from an incomplete migration coexist without any indication of which is canonical. This is not a system with technical debt. This is a system where the load-bearing walls are painted cardboard.

Following a strategic review, the team has adopted Path B (Migrate Directly), replacing EPIC-001 with EPIC-020 (Supabase Auth Migration) and adding six new epics that introduce a modern AI-native architecture.

---

## Path B: Strategic Modernisation

Following architectural review, the team adopted **Path B (Migrate Directly)** — replacing custom-built solutions with purpose-built modern infrastructure where the industry has already solved the problem.

| Old Approach | Modern Replacement | Epic |
|---|---|---|
| Custom password hashing + broken JWT | **Supabase Auth** | EPIC-020 |
| No multi-tenancy | **Supabase Row Level Security** | EPIC-019 |
| 661-line custom LLM client | **Anthropic SDK + Instructor** | EPIC-021 |
| Dead UsageTracker + inline prompts | **Langfuse** (open-source) | EPIC-021 |
| Custom agent coordinator + 7 stub agents | **LangGraph** | EPIC-022 |
| Filter-only company search | **pgvector** (Supabase native) | EPIC-023 |
| Job status polling | **Supabase Realtime** | EPIC-024 |

**Superseded stories**: STORY-001 through STORY-005 (by EPIC-020), STORY-017 (by STORY-078), STORY-048 (by STORY-073), STORY-055 (by STORY-073), STORY-056 (by STORY-074).

---

## Critical Path (P0 — Must Resolve Before Any Release)

```
EPIC-002: Configuration Integrity
  └─► EPIC-001: Security Restoration
        ├─► EPIC-003: Core Product Correctness
        └─► EPIC-004: Data Integrity & Atomicity
```

> **Ordering rationale:** Do not begin EPIC-001 until `config.py` is clean. Authentication fixes built on broken configuration are not fixes. They are fixes that inherit the defects of their foundation and will need to be re-done when the foundation is repaired.

---

## Epic Registry

| Epic | Title | Priority | Stories | Status |
|------|-------|----------|---------|--------|
| [EPIC-001](EPICS/EPIC-001-security-restoration/README.md) | Security Restoration | P0 | 5 | ⚫ Superseded by EPIC-020 |
| [EPIC-002](EPICS/EPIC-002-configuration-integrity/README.md) | Configuration Integrity | P0 | 3 | 🔴 Open |
| [EPIC-003](EPICS/EPIC-003-core-product-correctness/README.md) | Core Product Correctness | P0 | 3 | 🔴 Open |
| [EPIC-004](EPICS/EPIC-004-data-integrity-atomicity/README.md) | Data Integrity & Atomicity | P0 | 3 | 🔴 Open |
| EPIC-005 | Dead Code Elimination | P1 | 4 | 🔴 Open |
| EPIC-006 | Unification of Duplicates | P1 | 4 | 🔴 Open |
| EPIC-007 | Domain-Driven Design Migration | P1 | 5 | 🔴 Open |
| EPIC-008 | God File Decomposition | P1 | 4 | 🔴 Open |
| EPIC-009 | Data Layer Consolidation | P1 | 4 | 🔴 Open |
| EPIC-010 | API Layer Hardening | P1 | 3 | 🔴 Open |
| EPIC-011 | Business Rules Documentation | P2 | 2 | 🔴 Open |
| EPIC-012 | Type Safety & Code Quality | P2 | 3 | 🔴 Open |
| EPIC-013 | Test Suite Integrity | P2 | 3 | 🔴 Open |
| EPIC-014 | Observability & Telemetry | P2 | 5 | 🔴 Open |
| EPIC-015 | Dependency Resilience | P3 | 1 | 🔴 Open |
| EPIC-016 | Performance & Scalability | P3 | 2 | 🔴 Open |
| EPIC-017 | Developer Experience | P2 | 4 | 🔴 Open |
| EPIC-018 | Infrastructure-as-Code & CI/CD | P1 | 4 | 🔴 Open |
| [EPIC-019](EPICS/EPIC-019-multi-tenancy-data-isolation/README.md) | Multi-Tenancy & Data Isolation | P1 | 4 | 🔴 Open |
| [EPIC-020](EPICS/EPIC-020-supabase-auth-migration/README.md) | Supabase Auth Migration | P1 | 4 | 🔴 Open |
| [EPIC-021](EPICS/EPIC-021-modern-llm-stack/README.md) | Modern LLM Stack | P1 | 5 | 🔴 Open |
| [EPIC-022](EPICS/EPIC-022-langraph-agent-orchestration/README.md) | LangGraph Agent Orchestration | P2 | 4 | 🔴 Open |
| [EPIC-023](EPICS/EPIC-023-pgvector-semantic-search/README.md) | pgvector Semantic Search | P2 | 3 | 🔴 Open |
| [EPIC-024](EPICS/EPIC-024-supabase-realtime-job-status/README.md) | Supabase Realtime Job Status | P2 | 2 | 🔴 Open |
| EPIC-025 | Worker Reliability | P1 | 5 | 🔴 Open |
| EPIC-026 | Service Topology | P1 | 4 | 🔴 Open |
| EPIC-027 | CI/CD Automation | P1 | 4 | 🔴 Open |
| EPIC-028 | External Service Consolidation | P2 | 5 | 🔴 Open |
| EPIC-029 | Frontend Dashboard | P2 | 5 | 🔴 Open |
| EPIC-030 | Export Pipeline Modernization | P2 | 5 | 🔴 Open |
| [EPIC-031](EPICS/EPIC-031-shared-library-architecture/README.md) | Shared Library & Architecture | P2 | 5 | 🔴 Open |
| [EPIC-032](EPICS/EPIC-032-complete-unified-adapter-migration/README.md) | Complete Unified Adapter Migration | P1 | 4 | 🔴 Open |
| [EPIC-033](EPICS/EPIC-033-data-completeness-export-integrity/README.md) | Data Completeness & Export Integrity | P1 | 4 | 🔴 Open |
| [EPIC-034](EPICS/EPIC-034-exception-handling-transparency/README.md) | Exception Handling Transparency | P1 | 4 | 🔴 Open |
| [EPIC-035](EPICS/EPIC-035-async-first-external-adapters/README.md) | Async-First External Adapters | P2 | 4 | 🔴 Open |
| [EPIC-036](EPICS/EPIC-036-configuration-consolidation/README.md) | Configuration Consolidation | P2 | 4 | 🔴 Open |
| [EPIC-037](EPICS/EPIC-037-dead-code-elimination-phase-2/README.md) | Dead Code Elimination Phase 2 | P2 | 4 | 🔴 Open |
| [EPIC-038](EPICS/EPIC-038-ai-readiness-assessment-framework/README.md) | AI-Readiness Assessment Framework | P1 | 4 | 🔴 Open |
| [EPIC-039](EPICS/EPIC-039-energy-sector-specialization/README.md) | Energy Sector Domain Specialization | P1 | 4 | 🔴 Open |
| [EPIC-040](EPICS/EPIC-040-multi-market-expansion/README.md) | Multi-Market Geographic Expansion | P2 | 4 | 🔴 Open |
| [EPIC-041](EPICS/EPIC-041-equity-participation-model/README.md) | Equity Participation Business Model | P2 | 4 | 🔴 Open |
| [EPIC-042](EPICS/EPIC-042-rapid-market-validation/README.md) | Rapid Market Validation Methodology | P2 | 4 | 🔴 Open |

---

## Story Index

| Story | Title | Epic | Priority | Status |
|-------|-------|------|----------|--------|
| [STORY-001](EPICS/EPIC-001-security-restoration/STORIES/STORY-001-real-password-hashing.md) | Implement Real Password Hashing | EPIC-001 | P0 | ⚫ Superseded |
| [STORY-002](EPICS/EPIC-001-security-restoration/STORIES/STORY-002-remove-auth-bypass.md) | Remove Authentication Bypass on Core Endpoints | EPIC-001 | P0 | ⚫ Superseded |
| [STORY-003](EPICS/EPIC-001-security-restoration/STORIES/STORY-003-jwt-secret-rotation.md) | Replace Default JWT Secret and Fix Token Refresh | EPIC-001 | P0 | ⚫ Superseded |
| [STORY-004](EPICS/EPIC-001-security-restoration/STORIES/STORY-004-sanitize-error-responses.md) | Remove Stack Traces from HTTP Error Responses | EPIC-001 | P0 | ⚫ Superseded |
| [STORY-005](EPICS/EPIC-001-security-restoration/STORIES/STORY-005-input-sanitization-propagation.md) | Propagate Input Sanitization to All Routers | EPIC-001 | P0 | ⚫ Superseded |
| STORY-006 | Fix Duplicate Class Body Definitions in config.py | EPIC-002 | P0 | 🔴 Open |
| STORY-007 | Remove All Hardcoded Credentials | EPIC-002 | P0 | 🔴 Open |
| STORY-008 | Add Mandatory Startup Validation for All API Keys | EPIC-002 | P0 | 🔴 Open |
| STORY-009 | Unify Classification Thresholds Across All Files | EPIC-003 | P0 | 🔴 Open |
| STORY-010 | Eliminate Scoring Logic Duplication | EPIC-003 | P0 | 🔴 Open |
| STORY-011 | Name and Document All Scoring Constants | EPIC-003 | P0 | 🔴 Open |
| STORY-012 | Fix Dual-Write Atomicity in Research Pipeline | EPIC-004 | P0 | 🔴 Open |
| STORY-013 | Fix Conflict Resolution Logic | EPIC-004 | P0 | 🔴 Open |
| STORY-014 | Remove Hardcoded Date Path from Data Loader | EPIC-004 | P0 | 🔴 Open |
| STORY-015 | Consolidate Competing Worker Task Files | EPIC-005 | P1 | 🔴 Open |
| STORY-016 | Wire or Delete the UsageTracker Class | EPIC-005 | P1 | 🔴 Open |
| STORY-017 | Implement or Permanently Remove Stub Agents | EPIC-005 | P1 | 🔴 Open |
| STORY-018 | Remove Dead Temporal Workflow Stubs | EPIC-005 | P1 | 🔴 Open |
| STORY-019 | Eliminate Duplicate Unified Adapter Pairs | EPIC-006 | P1 | 🔴 Open |
| STORY-020 | Consolidate Three Parallel Loader Systems | EPIC-006 | P1 | 🔴 Open |
| STORY-021 | Merge Duplicate Middleware Implementations | EPIC-006 | P1 | 🔴 Open |
| STORY-022 | Consolidate Duplicate Route Directories | EPIC-006 | P1 | 🔴 Open |
| STORY-023 | Introduce Value Objects for Primitive Domain Concepts | EPIC-007 | P1 | 🔴 Open |
| STORY-024 | Migrate Company Entity to Rich Domain Model | EPIC-007 | P1 | 🔴 Open |
| STORY-025 | Define Abstract Repository Interfaces | EPIC-007 | P1 | 🔴 Open |
| STORY-026 | Define Domain Events for Research Pipeline | EPIC-007 | P1 | 🔴 Open |
| STORY-027 | Extract Domain Services from Router Handlers | EPIC-007 | P1 | 🔴 Open |
| STORY-028 | Decompose the Markdown Generator God File | EPIC-008 | P1 | 🔴 Open |
| STORY-029 | Decompose the Unified Loader God File | EPIC-008 | P1 | 🔴 Open |
| STORY-030 | Decompose the Enrichment Router God File | EPIC-008 | P1 | 🔴 Open |
| STORY-031 | Decompose the GitHub Agent God File | EPIC-008 | P1 | 🔴 Open |
| STORY-032 | Establish a Single Cache Abstraction | EPIC-009 | P1 | 🔴 Open |
| STORY-033 | Establish a Single Validation Service | EPIC-009 | P1 | 🔴 Open |
| STORY-034 | Fix N+1 Query Patterns | EPIC-009 | P1 | 🔴 Open |
| STORY-035 | Add Missing Database Indexes | EPIC-009 | P1 | 🔴 Open |
| STORY-036 | Move Business Logic Out of Routers | EPIC-010 | P1 | 🔴 Open |
| STORY-037 | Add Pagination to All Bulk Endpoints | EPIC-010 | P1 | 🔴 Open |
| STORY-038 | Add Typed Response Models to All Endpoints | EPIC-010 | P1 | 🔴 Open |
| STORY-039 | Document Business Rationale for Scoring Rules | EPIC-011 | P2 | 🔴 Open |
| STORY-040 | Replace Hardcoded FX Rate with Configurable Source | EPIC-011 | P2 | 🔴 Open |
| STORY-041 | Eliminate `: Any` Type Annotations | EPIC-012 | P2 | 🔴 Open |
| STORY-042 | Migrate stdlib logging to loguru | EPIC-012 | P2 | 🔴 Open |
| STORY-043 | Resolve Primitive Obsession in Domain Types | EPIC-012 | P2 | 🔴 Open |
| STORY-044 | Fix autouse Fixture Masking in Test Suite | EPIC-013 | P2 | 🔴 Open |
| STORY-045 | Add Boundary Tests for All Scoring Tiers | EPIC-013 | P2 | 🔴 Open |
| STORY-046 | Add Tests for Untested Core Modules | EPIC-013 | P2 | 🔴 Open |
| STORY-047 | Replace Fake Health Checks with Real Probes | EPIC-014 | P2 | 🔴 Open |
| STORY-048 | Wire LLM Cost Tracking (UsageTracker) | EPIC-014 | P2 | 🔴 Open |
| STORY-049 | Add Structured Logging with Correlation IDs | EPIC-014 | P2 | 🔴 Open |
| STORY-050 | Implement OpenTelemetry Distributed Tracing | EPIC-014 | P2 | 🔴 Open |
| STORY-051 | Add Prometheus Metrics Endpoints | EPIC-014 | P2 | 🔴 Open |
| STORY-052 | Audit and Harden External Dependencies | EPIC-015 | P3 | 🔴 Open |
| STORY-053 | Establish Unified Caching Strategy | EPIC-016 | P3 | 🔴 Open |
| STORY-054 | Implement CQRS Read/Write Separation | EPIC-016 | P3 | 🔴 Open |
| STORY-055 | Centralize LLM Prompt Templates | EPIC-017 | P2 | 🔴 Open |
| STORY-056 | Build LLM Output Evaluation Harness | EPIC-017 | P2 | 🔴 Open |
| STORY-057 | Automate Local Development Setup | EPIC-017 | P2 | 🔴 Open |
| STORY-058 | Write Developer Onboarding Documentation | EPIC-017 | P2 | 🔴 Open |
| STORY-059 | Dockerize Application with Multi-Stage Build | EPIC-018 | P1 | 🔴 Open |
| STORY-060 | Define Environment Configuration via IaC | EPIC-018 | P1 | 🔴 Open |
| STORY-061 | Build CI Pipeline with Quality Gates | EPIC-018 | P1 | 🔴 Open |
| STORY-062 | Implement Pre-commit Hooks and Linting Automation | EPIC-018 | P1 | 🔴 Open |
| [STORY-063](EPICS/EPIC-019-multi-tenancy-data-isolation/STORIES/STORY-063-tenant-model.md) | Define Tenant Model and Domain Object Scoping | EPIC-019 | P1 | 🔴 Open |
| [STORY-064](EPICS/EPIC-019-multi-tenancy-data-isolation/STORIES/STORY-064-supabase-rls.md) | Implement Supabase RLS for All Tables | EPIC-019 | P1 | 🔴 Open |
| [STORY-065](EPICS/EPIC-019-multi-tenancy-data-isolation/STORIES/STORY-065-tenant-api-keys.md) | Add Tenant-Scoped API Key Management | EPIC-019 | P1 | 🔴 Open |
| [STORY-066](EPICS/EPIC-019-multi-tenancy-data-isolation/STORIES/STORY-066-tenant-research-jobs.md) | Enforce Tenant Isolation in Research Jobs | EPIC-019 | P1 | 🔴 Open |
| [STORY-067](EPICS/EPIC-020-supabase-auth-migration/STORIES/STORY-067-supabase-auth.md) | Migrate Authentication to Supabase Auth | EPIC-020 | P1 | 🔴 Open |
| [STORY-068](EPICS/EPIC-020-supabase-auth-migration/STORIES/STORY-068-remove-auth-bypass.md) | Remove Auth Bypass and Wire Supabase JWT Middleware | EPIC-020 | P1 | 🔴 Open |
| [STORY-069](EPICS/EPIC-020-supabase-auth-migration/STORIES/STORY-069-error-handling-sanitization.md) | Migrate Error Handling and Input Sanitization | EPIC-020 | P1 | 🔴 Open |
| [STORY-070](EPICS/EPIC-020-supabase-auth-migration/STORIES/STORY-070-ssrf-fix.md) | Fix SSRF Vulnerability in Web and Website Agents | EPIC-020 | P1 | 🔴 Open |
| [STORY-071](EPICS/EPIC-021-modern-llm-stack/STORIES/STORY-071-anthropic-sdk.md) | Replace Custom LLM Client with Anthropic SDK | EPIC-021 | P1 | 🔴 Open |
| [STORY-072](EPICS/EPIC-021-modern-llm-stack/STORIES/STORY-072-instructor-structured-outputs.md) | Implement Structured LLM Outputs with Instructor | EPIC-021 | P1 | 🔴 Open |
| [STORY-073](EPICS/EPIC-021-modern-llm-stack/STORIES/STORY-073-langfuse-integration.md) | Integrate Langfuse for Cost Tracking and Prompt Management | EPIC-021 | P1 | 🔴 Open |
| [STORY-074](EPICS/EPIC-021-modern-llm-stack/STORIES/STORY-074-langfuse-evaluation.md) | Migrate LLM Evaluation to Langfuse | EPIC-021 | P2 | 🔴 Open |
| [STORY-075](EPICS/EPIC-021-modern-llm-stack/STORIES/STORY-075-multi-provider-fallback.md) | Implement Multi-Provider Fallback via SDK | EPIC-021 | P1 | 🔴 Open |
| [STORY-076](EPICS/EPIC-022-langraph-agent-orchestration/STORIES/STORY-076-langgraph-state.md) | Define LangGraph State and Research Graph Architecture | EPIC-022 | P2 | 🔴 Open |
| [STORY-077](EPICS/EPIC-022-langraph-agent-orchestration/STORIES/STORY-077-coordinator-migration.md) | Migrate Coordinator Agent to LangGraph State Machine | EPIC-022 | P2 | 🔴 Open |
| [STORY-078](EPICS/EPIC-022-langraph-agent-orchestration/STORIES/STORY-078-agent-nodes.md) | Implement Real Agent Nodes as LangGraph Graph Nodes | EPIC-022 | P2 | 🔴 Open |
| [STORY-079](EPICS/EPIC-022-langraph-agent-orchestration/STORIES/STORY-079-checkpointing-hitl.md) | Add Checkpointing and Human-in-the-Loop | EPIC-022 | P2 | 🔴 Open |
| [STORY-080](EPICS/EPIC-023-pgvector-semantic-search/STORIES/STORY-080-pgvector-schema.md) | Add pgvector Extension and Embedding Schema | EPIC-023 | P2 | 🔴 Open |
| [STORY-081](EPICS/EPIC-023-pgvector-semantic-search/STORIES/STORY-081-embed-during-research.md) | Generate Company Embeddings During Research Pipeline | EPIC-023 | P2 | 🔴 Open |
| [STORY-082](EPICS/EPIC-023-pgvector-semantic-search/STORIES/STORY-082-semantic-search-endpoint.md) | Implement Semantic Similarity Search Endpoint | EPIC-023 | P2 | 🔴 Open |
| [STORY-083](EPICS/EPIC-024-supabase-realtime-job-status/STORIES/STORY-083-research-job-status-table.md) | Define Research Job Status Table with Realtime | EPIC-024 | P2 | 🔴 Open |
| [STORY-084](EPICS/EPIC-024-supabase-realtime-job-status/STORIES/STORY-084-realtime-subscription.md) | Replace Polling with Supabase Realtime Subscriptions | EPIC-024 | P2 | 🔴 Open |
| [STORY-085](EPICS/EPIC-010-api-layer-hardening/STORIES/STORY-085-api-prefix.md) | Wire api_prefix to Route Definitions | EPIC-010 | P2 | 🔴 Open |
| [STORY-086](EPICS/EPIC-014-observability-telemetry/STORIES/STORY-086-audit-trail.md) | Enforce Universal Audit Trail Across All Endpoints | EPIC-014 | P1 | 🔴 Open |
| [STORY-087](EPICS/EPIC-018-infrastructure-cicd/STORIES/STORY-087-celery-dlq.md) | Implement Celery Dead Letter Queue | EPIC-018 | P1 | 🔴 Open |
| [STORY-088](EPICS/EPIC-025-worker-reliability/STORIES/STORY-088-persistent-dead-letter-queue.md) | Fix In-Memory DLQ — Persist to PostgreSQL | EPIC-025 | P1 | 🔴 Open |
| [STORY-089](EPICS/EPIC-025-worker-reliability/STORIES/STORY-089-task-acks-late-configuration.md) | Set task_acks_late and task_reject_on_worker_lost | EPIC-025 | P1 | 🔴 Open |
| [STORY-090](EPICS/EPIC-025-worker-reliability/STORIES/STORY-090-task-idempotency-deduplication.md) | Implement Task Idempotency via Deduplication Lock | EPIC-025 | P1 | 🔴 Open |
| [STORY-091](EPICS/EPIC-025-worker-reliability/STORIES/STORY-091-result-expiry-ttl.md) | Set Result Expiry TTL to Prevent Redis Bloat | EPIC-025 | P1 | 🔴 Open |
| [STORY-092](EPICS/EPIC-025-worker-reliability/STORIES/STORY-092-merge-duplicate-task-files.md) | Merge worker_tasks_v2.py — Eliminate Duplicate Task Files | EPIC-025 | P1 | 🔴 Open |
| [STORY-093](EPICS/EPIC-026-service-topology/STORIES/STORY-093-celery-worker-docker-service.md) | Add Celery Worker Service to docker-compose | EPIC-026 | P1 | 🔴 Open |
| [STORY-094](EPICS/EPIC-026-service-topology/STORIES/STORY-094-celery-beat-docker-service.md) | Add Celery Beat Service to docker-compose | EPIC-026 | P1 | 🔴 Open |
| [STORY-095](EPICS/EPIC-026-service-topology/STORIES/STORY-095-flower-monitoring-service.md) | Add Flower Monitoring Service to docker-compose | EPIC-026 | P1 | 🔴 Open |
| [STORY-096](EPICS/EPIC-026-service-topology/STORIES/STORY-096-multi-stage-dockerfile.md) | Multi-Stage Dockerfile for Production | EPIC-026 | P1 | 🔴 Open |
| [STORY-097](EPICS/EPIC-027-cicd-automation/STORIES/STORY-097-automate-alembic-migrations.md) | Automate Alembic Migrations Pre-Deploy | EPIC-027 | P1 | 🔴 Open |
| [STORY-098](EPICS/EPIC-027-cicd-automation/STORIES/STORY-098-makefile-targets.md) | Add migrate, seed, deploy Makefile Targets | EPIC-027 | P1 | 🔴 Open |
| [STORY-099](EPICS/EPIC-027-cicd-automation/STORIES/STORY-099-staging-smoke-test-workflow.md) | Add Staging Deploy + Post-Deploy Smoke Test Workflow | EPIC-027 | P1 | 🔴 Open |
| [STORY-100](EPICS/EPIC-027-cicd-automation/STORIES/STORY-100-delete-bypass-scripts.md) | Delete Root Bypass Scripts | EPIC-027 | P1 | 🔴 Open |
| [STORY-101](EPICS/EPIC-028-external-service-consolidation/STORIES/STORY-101-searxng-web-search.md) | Replace Google Custom Search with Self-Hosted SearXNG | EPIC-028 | P2 | 🔴 Open |
| [STORY-102](EPICS/EPIC-028-external-service-consolidation/STORIES/STORY-102-gdelt-rss-news.md) | Replace NewsAPI with GDELT + RSS Aggregation | EPIC-028 | P2 | 🔴 Open |
| [STORY-103](EPICS/EPIC-028-external-service-consolidation/STORIES/STORY-103-yahoo-finance-stability.md) | Stabilize Yahoo Finance Integration | EPIC-028 | P2 | 🔴 Open |
| [STORY-104](EPICS/EPIC-028-external-service-consolidation/STORIES/STORY-104-notification-service.md) | Add Slack and Email Notification Service | EPIC-028 | P2 | 🔴 Open |
| [STORY-105](EPICS/EPIC-028-external-service-consolidation/STORIES/STORY-105-supabase-storage-exports.md) | Move File Exports to Supabase Storage | EPIC-028 | P2 | 🔴 Open |
| [STORY-106](EPICS/EPIC-029-frontend-dashboard/STORIES/STORY-106-nextjs-bootstrap-supabase-auth.md) | Bootstrap Next.js Dashboard with Supabase Auth | EPIC-029 | P2 | 🔴 Open |
| [STORY-107](EPICS/EPIC-029-frontend-dashboard/STORIES/STORY-107-company-list-detail-pages.md) | Company List and Detail Pages | EPIC-029 | P2 | 🔴 Open |
| [STORY-108](EPICS/EPIC-029-frontend-dashboard/STORIES/STORY-108-research-trigger-ui.md) | Research Pipeline Trigger UI | EPIC-029 | P2 | 🔴 Open |
| [STORY-109](EPICS/EPIC-029-frontend-dashboard/STORIES/STORY-109-realtime-job-status-ui.md) | Real-Time Job Status UI via Supabase Realtime | EPIC-029 | P2 | 🔴 Open |
| [STORY-110](EPICS/EPIC-029-frontend-dashboard/STORIES/STORY-110-export-download-ui.md) | Export Download UI | EPIC-029 | P2 | 🔴 Open |
| [STORY-111](EPICS/EPIC-030-export-pipeline-modernization/STORIES/STORY-111-async-export-celery.md) | Move Exports to Async Celery Tasks | EPIC-030 | P2 | 🔴 Open |
| [STORY-112](EPICS/EPIC-030-export-pipeline-modernization/STORIES/STORY-112-streaming-excel-export.md) | Streaming Excel Export for Large Datasets | EPIC-030 | P2 | 🔴 Open |
| [STORY-113](EPICS/EPIC-030-export-pipeline-modernization/STORIES/STORY-113-export-status-tracking.md) | Export Status Tracking and Download Links | EPIC-030 | P2 | 🔴 Open |
| [STORY-114](EPICS/EPIC-030-export-pipeline-modernization/STORIES/STORY-114-pdf-export-format.md) | Add PDF Export Format | EPIC-030 | P2 | 🔴 Open |
| [STORY-115](EPICS/EPIC-030-export-pipeline-modernization/STORIES/STORY-115-export-supabase-storage.md) | Store Exports in Supabase Storage | EPIC-030 | P2 | 🔴 Open |
| [STORY-116](EPICS/EPIC-031-shared-library-architecture/STORIES/STORY-116-centralize-retry-policy.md) | Centralize All Retry/Backoff in core/retry_policy.py | EPIC-031 | P2 | 🔴 Open |
| [STORY-117](EPICS/EPIC-031-shared-library-architecture/STORIES/STORY-117-fix-circular-imports-shared-package.md) | Fix Circular Import Risk — Introduce shared/ Package | EPIC-031 | P2 | 🔴 Open |
| [STORY-118](EPICS/EPIC-031-shared-library-architecture/STORIES/STORY-118-formalize-cli-entrypoint.md) | Formalize CLI as Proper Package Entrypoint | EPIC-031 | P2 | 🔴 Open |
| [STORY-119](EPICS/EPIC-031-shared-library-architecture/STORIES/STORY-119-split-unified-loader.md) | Split unified_loader.py into Separate Modules | EPIC-031 | P2 | 🔴 Open |
| [STORY-120](EPICS/EPIC-031-shared-library-architecture/STORIES/STORY-120-utc-timezone-policy.md) | Enforce UTC Timezone Policy Across All Modules | EPIC-031 | P2 | 🔴 Open |
| [STORY-121](EPICS/EPIC-032-complete-unified-adapter-migration/STORIES/STORY-121-restore-news-unified-error-handling.md) | Restore Error Handling in news_unified.py | EPIC-032 | P1 | 🔴 Open |
| [STORY-122](EPICS/EPIC-032-complete-unified-adapter-migration/STORIES/STORY-122-restore-funding-unified-wrapper.md) | Restore Funding Adapter Wrapper | EPIC-032 | P1 | 🔴 Open |
| [STORY-123](EPICS/EPIC-032-complete-unified-adapter-migration/STORIES/STORY-123-restore-website-validation.md) | Restore Website Adapter Validation | EPIC-032 | P1 | 🔴 Open |
| [STORY-124](EPICS/EPIC-032-complete-unified-adapter-migration/STORIES/STORY-124-delete-old-adapters.md) | Delete Old Adapter Versions After Parity | EPIC-032 | P1 | 🔴 Open |
| [STORY-125](EPICS/EPIC-033-data-completeness-export-integrity/STORIES/STORY-125-restore-dropped-fields.md) | Restore 20 Dropped Fields to Excel Export | EPIC-033 | P1 | 🔴 Open |
| [STORY-126](EPICS/EPIC-033-data-completeness-export-integrity/STORIES/STORY-126-export-schema-validation.md) | Add Export Schema Validation | EPIC-033 | P1 | 🔴 Open |
| [STORY-127](EPICS/EPIC-033-data-completeness-export-integrity/STORIES/STORY-127-deduplicate-fields.md) | Deduplicate profit_margin and employee Fields | EPIC-033 | P1 | 🔴 Open |
| [STORY-128](EPICS/EPIC-033-data-completeness-export-integrity/STORIES/STORY-128-document-field-lineage.md) | Document Field Lineage from Ingestion to Export | EPIC-033 | P2 | 🔴 Open |
| [STORY-129](EPICS/EPIC-034-exception-handling-transparency/STORIES/STORY-129-enhanced-client-silent-failures.md) | Eliminate Silent None Returns in enhanced_client.py | EPIC-034 | P1 | 🔴 Open |
| [STORY-130](EPICS/EPIC-034-exception-handling-transparency/STORIES/STORY-130-adapter-exception-logging.md) | Add Structured Logging to All Adapter Exception Handlers | EPIC-034 | P1 | 🔴 Open |
| [STORY-131](EPICS/EPIC-034-exception-handling-transparency/STORIES/STORY-131-null-safety-division.md) | Add Null Safety Guards for Division Operations | EPIC-034 | P1 | 🔴 Open |
| [STORY-132](EPICS/EPIC-034-exception-handling-transparency/STORIES/STORY-132-exception-standards-doc.md) | Create Exception Handling Standards Document | EPIC-034 | P2 | 🔴 Open |
| [STORY-133](EPICS/EPIC-035-async-first-external-adapters/STORIES/STORY-133-github-agent-async.md) | Replace requests with httpx in GitHub Agent | EPIC-035 | P2 | 🔴 Open |
| [STORY-134](EPICS/EPIC-035-async-first-external-adapters/STORIES/STORY-134-news-funding-async.md) | Replace requests with httpx in News and Funding Adapters | EPIC-035 | P2 | 🔴 Open |
| [STORY-135](EPICS/EPIC-035-async-first-external-adapters/STORIES/STORY-135-companies-house-website-async.md) | Replace requests with httpx in Companies House and Website Agents | EPIC-035 | P2 | 🔴 Open |
| [STORY-136](EPICS/EPIC-035-async-first-external-adapters/STORIES/STORY-136-async-http-guidelines.md) | Add Async HTTP Client Guidelines and Linting | EPIC-035 | P2 | 🔴 Open |
| [STORY-137](EPICS/EPIC-036-configuration-consolidation/STORIES/STORY-137-centralize-env-vars.md) | Centralize All Environment Variables in config.py | EPIC-036 | P2 | 🔴 Open |
| [STORY-138](EPICS/EPIC-036-configuration-consolidation/STORIES/STORY-138-config-driven-paths.md) | Replace Hardcoded Paths with Config-Driven Paths | EPIC-036 | P2 | 🔴 Open |
| [STORY-139](EPICS/EPIC-036-configuration-consolidation/STORIES/STORY-139-centralize-timeouts.md) | Centralize Timeouts and Magic Numbers | EPIC-036 | P2 | 🔴 Open |
| [STORY-140](EPICS/EPIC-036-configuration-consolidation/STORIES/STORY-140-fix-env-example.md) | Fix .env.example with All Required Variables | EPIC-036 | P2 | 🔴 Open |
| [STORY-141](EPICS/EPIC-037-dead-code-elimination-phase-2/STORIES/STORY-141-delete-refresh-router.md) | Delete Disconnected Refresh Router | EPIC-037 | P2 | 🔴 Open |
| [STORY-142](EPICS/EPIC-037-dead-code-elimination-phase-2/STORIES/STORY-142-delete-worker-tasks-v2.md) | Delete Orphaned worker_tasks_v2.py | EPIC-037 | P2 | 🔴 Open |
| [STORY-143](EPICS/EPIC-037-dead-code-elimination-phase-2/STORIES/STORY-143-delete-orphaned-data-files.md) | Audit and Delete Orphaned Data Layer Files | EPIC-037 | P2 | 🔴 Open |
| [STORY-144](EPICS/EPIC-037-dead-code-elimination-phase-2/STORIES/STORY-144-dead-code-ci-job.md) | Create Dead Code Detection CI Job | EPIC-037 | P2 | 🔴 Open |
