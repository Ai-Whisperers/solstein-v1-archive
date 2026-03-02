# Solstein Engineering Backlog

> *The authoritative tracking document for the Solstein architectural remediation programme. All work originates here.*

| Last Updated: 2026-03-01 | Audit Version: 2.0 | Status: 🔴 DO NOT SHIP |

---

## System Health Dashboard

| Metric | Value | Trend |
|--------|-------|-------|
| Total Epics | 49 | +6 |
| Total Stories | 189 | +21 |
| P0 Stories (Ship Blockers) | 15 | 🔴 Unresolved (+2) |
| P1 Stories (Current Sprint) | 74 | 🟠 Queued (+12) |
| P2 Stories (Next Quarter) | 78 | 🟡 Backlogged (+5) |
| P3 Stories (Sustaining) | 22 | 🟢 Deferred (+2) |
| Total Stories | 168 | — |
| P0 Stories (Ship Blockers) | 13 | 🔴 Unresolved |
| P1 Stories (Current Sprint) | 62 | 🟠 Queued |
| P2 Stories (Next Quarter) | 73 | 🟡 Backlogged |
| P3 Stories (Sustaining) | 20 | 🟢 Deferred |
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
  └─► EPIC-020: Supabase Auth Migration
        ├─► EPIC-003: Core Product Correctness
        └─► EPIC-004: Data Integrity & Atomicity
```

> **Ordering rationale:** Do not begin EPIC-020 until `config.py` is clean. Authentication migration built on broken configuration is not a migration. It is a migration that inherits the defects of its foundation and will need to be re-done when the foundation is repaired.

---

## Milestone Roadmap

| Milestone | Focus | Epics | Target Date |
|-----------|-------|-------|-------------|
| [M1: Safe Foundation](MILESTONES/M1-Safe-Foundation.md) | Config, cleanup, dead code | EPIC-002, EPIC-036, EPIC-037, EPIC-043 | 2026-03-15 |
| [M2: Secure Identity](MILESTONES/M2-Secure-Identity.md) | Authentication, multi-tenancy | EPIC-020, EPIC-019 | 2026-03-31 |
| [M3: Modern Data Layer](MILESTONES/M3-Modern-Data-Layer.md) | Vector search, realtime, exports | EPIC-023, EPIC-024, EPIC-030, EPIC-033 | 2026-04-15 |
| [M4: Intelligent Agents](MILESTONES/M4-Intelligent-Agents.md) | LLM stack, agent orchestration | EPIC-021, EPIC-022 | 2026-04-30 |
| [M5: Production Ready](MILESTONES/M5-Production-Ready.md) | Workers, CI/CD, observability | EPIC-025, EPIC-026, EPIC-027, EPIC-014 | 2026-05-15 |
| [M6: Business Value](MILESTONES/M6-Business-Value.md) | AI readiness, energy sector | EPIC-038, EPIC-039 | 2026-06-01 |

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
| EPIC-010 | API Layer Hardening | P1 | 4 | 🔴 Open |
| EPIC-011 | Business Rules Documentation | P2 | 2 | 🔴 Open |
| EPIC-012 | Type Safety & Code Quality | P2 | 3 | 🔴 Open |
| EPIC-013 | Test Suite Integrity | P2 | 3 | 🔴 Open |
| EPIC-014 | Observability & Telemetry | P2 | 6 | 🔴 Open |
| EPIC-015 | Dependency Resilience | P3 | 1 | 🔴 Open |
| EPIC-016 | Performance & Scalability | P3 | 2 | 🔴 Open |
| EPIC-017 | Developer Experience | P2 | 4 | 🔴 Open |
| EPIC-018 | Infrastructure-as-Code & CI/CD | P1 | 5 | 🔴 Open |
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
| [EPIC-043](EPICS/EPIC-043-repository-cleanup/README.md) | Repository Cleanup & Organization | P2 | 4 | 🔴 Open |
| [EPIC-044](EPICS/EPIC-044-quick-wins/README.md) | Quick Wins — High Impact, Low Effort | P1 | 10 | 🔴 Open |
|| [EPIC-045](EPICS/EPIC-045-cli-runtime-correctness/README.md) | CLI Runtime Correctness | P0 | 4 | 🔴 Open |
|| [EPIC-046](EPICS/EPIC-046-scoring-engine-correctness/README.md) | Scoring Engine Correctness | P0 | 4 | 🔴 Open |
|| [EPIC-047](EPICS/EPIC-047-data-loading-fidelity/README.md) | Data Loading Fidelity | P1 | 4 | 🔴 Open |
|| [EPIC-048](EPICS/EPIC-048-report-generation-quality/README.md) | Report Generation Quality | P1 | 5 | 🔴 Open |
|| [EPIC-049](EPICS/EPIC-049-infrastructure-dev-environment/README.md) | Infrastructure & Dev Environment | P1 | 4 | 🔴 Open |

---

## Story Index

<details>
<summary>Click to expand full story index (189 stories)</summary>

### P0 — Ship Blockers (15 stories)

| Story | Title | Epic | Status |
|-------|-------|------|--------|
| [STORY-006](EPICS/EPIC-002-configuration-integrity/STORIES/STORY-006-fix-duplicate-config-class-bodies.md) | Fix Duplicate Class Body Definitions in config.py | EPIC-002 | 🔴 Open |
| [STORY-007](EPICS/EPIC-002-configuration-integrity/STORIES/STORY-007-remove-hardcoded-credentials.md) | Remove All Hardcoded Credentials | EPIC-002 | 🔴 Open |
| [STORY-008](EPICS/EPIC-002-configuration-integrity/STORIES/STORY-008-mandatory-startup-validation.md) | Add Mandatory Startup Validation for All API Keys | EPIC-002 | 🔴 Open |
| [STORY-009](EPICS/EPIC-003-core-product-correctness/STORIES/STORY-009-unify-classification-thresholds.md) | Unify Classification Thresholds Across All Files | EPIC-003 | 🔴 Open |
| [STORY-010](EPICS/EPIC-003-core-product-correctness/STORIES/STORY-010-eliminate-scoring-duplication.md) | Eliminate Scoring Logic Duplication | EPIC-003 | 🔴 Open |
| [STORY-011](EPICS/EPIC-003-core-product-correctness/STORIES/STORY-011-name-scoring-constants.md) | Name and Document All Scoring Constants | EPIC-003 | 🔴 Open |
| [STORY-012](EPICS/EPIC-004-data-integrity-atomicity/STORIES/STORY-012-dual-write-atomicity.md) | Fix Dual-Write Atomicity in Research Pipeline | EPIC-004 | 🔴 Open |
| [STORY-013](EPICS/EPIC-004-data-integrity-atomicity/STORIES/STORY-013-fix-conflict-resolution-logic.md) | Fix Conflict Resolution Logic | EPIC-004 | 🔴 Open |
| [STORY-014](EPICS/EPIC-004-data-integrity-atomicity/STORIES/STORY-014-remove-hardcoded-date-path.md) | Remove Hardcoded Date Path from Data Loader | EPIC-004 | 🔴 Open |
| [STORY-067](EPICS/EPIC-020-supabase-auth-migration/STORIES/STORY-067-migrate-to-supabase-auth.md) | Migrate Authentication to Supabase Auth | EPIC-020 | 🔴 Open |
| [STORY-068](EPICS/EPIC-020-supabase-auth-migration/STORIES/STORY-068-remove-auth-bypass.md) | Remove Auth Bypass and Wire Supabase JWT Middleware | EPIC-020 | 🔴 Open |
| [STORY-069](EPICS/EPIC-020-supabase-auth-migration/STORIES/STORY-069-error-handling-sanitization.md) | Migrate Error Handling and Input Sanitization | EPIC-020 | 🔴 Open |
| [STORY-070](EPICS/EPIC-020-supabase-auth-migration/STORIES/STORY-070-ssrf-fix.md) | Fix SSRF Vulnerability in Web and Website Agents | EPIC-020 | 🔴 Open |

### P1 — Current Sprint (62 stories)

| Story | Title | Epic | Status |
|-------|-------|------|--------|
| STORY-015 | Consolidate Competing Worker Task Files | EPIC-005 | 🔴 Open |
| STORY-016 | Wire or Delete the UsageTracker Class | EPIC-005 | 🔴 Open |
| STORY-018 | Remove Dead Temporal Workflow Stubs | EPIC-005 | 🔴 Open |
| STORY-019 | Eliminate Duplicate Unified Adapter Pairs | EPIC-006 | 🔴 Open |
| STORY-020 | Consolidate Three Parallel Loader Systems | EPIC-006 | 🔴 Open |
| STORY-021 | Merge Duplicate Middleware Implementations | EPIC-006 | 🔴 Open |
| STORY-022 | Consolidate Duplicate Route Directories | EPIC-006 | 🔴 Open |
| STORY-023 | Introduce Value Objects for Primitive Domain Concepts | EPIC-007 | 🔴 Open |
| STORY-024 | Migrate Company Entity to Rich Domain Model | EPIC-007 | 🔴 Open |
| STORY-025 | Define Abstract Repository Interfaces | EPIC-007 | 🔴 Open |
| STORY-026 | Define Domain Events for Research Pipeline | EPIC-007 | 🔴 Open |
| STORY-027 | Extract Domain Services from Router Handlers | EPIC-007 | 🔴 Open |
| STORY-028 | Decompose the Markdown Generator God File | EPIC-008 | 🔴 Open |
| STORY-029 | Decompose the Unified Loader God File | EPIC-008 | 🔴 Open |
| STORY-030 | Decompose the Enrichment Router God File | EPIC-008 | 🔴 Open |
| STORY-031 | Decompose the GitHub Agent God File | EPIC-008 | 🔴 Open |
| STORY-032 | Establish a Single Cache Abstraction | EPIC-009 | 🔴 Open |
| STORY-033 | Establish a Single Validation Service | EPIC-009 | 🔴 Open |
| STORY-034 | Fix N+1 Query Patterns | EPIC-009 | 🔴 Open |
| STORY-035 | Add Missing Database Indexes | EPIC-009 | 🔴 Open |
| STORY-036 | Move Business Logic Out of Routers | EPIC-010 | 🔴 Open |
| STORY-037 | Add Pagination to All Bulk Endpoints | EPIC-010 | 🔴 Open |
| STORY-038 | Add Typed Response Models to All Endpoints | EPIC-010 | 🔴 Open |
| STORY-059 | Dockerize Application with Multi-Stage Build | EPIC-018 | 🔴 Open |
| STORY-060 | Define Environment Configuration via IaC | EPIC-018 | 🔴 Open |
| STORY-061 | Build CI Pipeline with Quality Gates | EPIC-018 | 🔴 Open |
| STORY-062 | Implement Pre-commit Hooks and Linting Automation | EPIC-018 | 🔴 Open |
| [STORY-063](EPICS/EPIC-019-multi-tenancy-data-isolation/STORIES/STORY-063-tenant-model.md) | Define Tenant Model and Domain Object Scoping | EPIC-019 | 🔴 Open |
| [STORY-064](EPICS/EPIC-019-multi-tenancy-data-isolation/STORIES/STORY-064-supabase-rls.md) | Implement Supabase RLS for All Tables | EPIC-019 | 🔴 Open |
| [STORY-065](EPICS/EPIC-019-multi-tenancy-data-isolation/STORIES/STORY-065-tenant-api-keys.md) | Add Tenant-Scoped API Key Management | EPIC-019 | 🔴 Open |
| [STORY-066](EPICS/EPIC-019-multi-tenancy-data-isolation/STORIES/STORY-066-tenant-research-jobs.md) | Enforce Tenant Isolation in Research Jobs | EPIC-019 | 🔴 Open |
| [STORY-071](EPICS/EPIC-021-modern-llm-stack/STORIES/STORY-071-anthropic-sdk.md) | Replace Custom LLM Client with Anthropic SDK | EPIC-021 | 🔴 Open |
| [STORY-072](EPICS/EPIC-021-modern-llm-stack/STORIES/STORY-072-instructor-structured-outputs.md) | Implement Structured LLM Outputs with Instructor | EPIC-021 | 🔴 Open |
| [STORY-073](EPICS/EPIC-021-modern-llm-stack/STORIES/STORY-073-langfuse-integration.md) | Integrate Langfuse for Cost Tracking and Prompt Management | EPIC-021 | 🔴 Open |
| [STORY-075](EPICS/EPIC-021-modern-llm-stack/STORIES/STORY-075-multi-provider-fallback.md) | Implement Multi-Provider Fallback via SDK | EPIC-021 | 🔴 Open |
| [STORY-086](EPICS/EPIC-014-observability-telemetry/STORIES/STORY-086-audit-trail.md) | Enforce Universal Audit Trail Across All Endpoints | EPIC-014 | 🔴 Open |
| [STORY-087](EPICS/EPIC-018-infrastructure-cicd/STORIES/STORY-087-celery-dlq.md) | Implement Celery Dead Letter Queue | EPIC-018 | 🔴 Open |
| [STORY-088](EPICS/EPIC-025-worker-reliability/STORIES/STORY-088-persistent-dead-letter-queue.md) | Fix In-Memory DLQ — Persist to PostgreSQL | EPIC-025 | 🔴 Open |
| [STORY-089](EPICS/EPIC-025-worker-reliability/STORIES/STORY-089-task-acks-late-configuration.md) | Set task_acks_late and task_reject_on_worker_lost | EPIC-025 | 🔴 Open |
| [STORY-090](EPICS/EPIC-025-worker-reliability/STORIES/STORY-090-task-idempotency-deduplication.md) | Implement Task Idempotency via Deduplication Lock | EPIC-025 | 🔴 Open |
| [STORY-091](EPICS/EPIC-025-worker-reliability/STORIES/STORY-091-result-expiry-ttl.md) | Set Result Expiry TTL to Prevent Redis Bloat | EPIC-025 | 🔴 Open |
| [STORY-092](EPICS/EPIC-025-worker-reliability/STORIES/STORY-092-merge-duplicate-task-files.md) | Merge worker_tasks_v2.py — Eliminate Duplicate Task Files | EPIC-025 | 🔴 Open |
| [STORY-093](EPICS/EPIC-026-service-topology/STORIES/STORY-093-celery-worker-docker-service.md) | Add Celery Worker Service to docker-compose | EPIC-026 | 🔴 Open |
| [STORY-094](EPICS/EPIC-026-service-topology/STORIES/STORY-094-celery-beat-docker-service.md) | Add Celery Beat Service to docker-compose | EPIC-026 | 🔴 Open |
| [STORY-095](EPICS/EPIC-026-service-topology/STORIES/STORY-095-flower-monitoring-service.md) | Add Flower Monitoring Service to docker-compose | EPIC-026 | 🔴 Open |
| [STORY-096](EPICS/EPIC-026-service-topology/STORIES/STORY-096-multi-stage-dockerfile.md) | Multi-Stage Dockerfile for Production | EPIC-026 | 🔴 Open |
| [STORY-097](EPICS/EPIC-027-cicd-automation/STORIES/STORY-097-automate-alembic-migrations.md) | Automate Alembic Migrations Pre-Deploy | EPIC-027 | 🔴 Open |
| [STORY-098](EPICS/EPIC-027-cicd-automation/STORIES/STORY-098-makefile-targets.md) | Add migrate, seed, deploy Makefile Targets | EPIC-027 | 🔴 Open |
| [STORY-099](EPICS/EPIC-027-cicd-automation/STORIES/STORY-099-staging-smoke-test-workflow.md) | Add Staging Deploy + Post-Deploy Smoke Test Workflow | EPIC-027 | 🔴 Open |
| [STORY-100](EPICS/EPIC-027-cicd-automation/STORIES/STORY-100-delete-bypass-scripts.md) | Delete Root Bypass Scripts | EPIC-027 | 🔴 Open |
| [STORY-121](EPICS/EPIC-032-complete-unified-adapter-migration/STORIES/STORY-121-restore-news-unified-error-handling.md) | Restore Error Handling in news_unified.py | EPIC-032 | 🔴 Open |
| [STORY-122](EPICS/EPIC-032-complete-unified-adapter-migration/STORIES/STORY-122-restore-funding-unified-wrapper.md) | Restore Funding Adapter Wrapper | EPIC-032 | 🔴 Open |
| [STORY-123](EPICS/EPIC-032-complete-unified-adapter-migration/STORIES/STORY-123-restore-website-validation.md) | Restore Website Adapter Validation | EPIC-032 | 🔴 Open |
| [STORY-124](EPICS/EPIC-032-complete-unified-adapter-migration/STORIES/STORY-124-delete-old-adapters.md) | Delete Old Adapter Versions After Parity | EPIC-032 | 🔴 Open |
| [STORY-125](EPICS/EPIC-033-data-completeness-export-integrity/STORIES/STORY-125-restore-dropped-fields.md) | Restore 20 Dropped Fields to Excel Export | EPIC-033 | 🔴 Open |
| [STORY-126](EPICS/EPIC-033-data-completeness-export-integrity/STORIES/STORY-126-export-schema-validation.md) | Add Export Schema Validation | EPIC-033 | 🔴 Open |
| [STORY-127](EPICS/EPIC-033-data-completeness-export-integrity/STORIES/STORY-127-deduplicate-fields.md) | Deduplicate profit_margin and employee Fields | EPIC-033 | 🔴 Open |
| [STORY-129](EPICS/EPIC-034-exception-handling-transparency/STORIES/STORY-129-enhanced-client-silent-failures.md) | Eliminate Silent None Returns in enhanced_client.py | EPIC-034 | 🔴 Open |
| [STORY-130](EPICS/EPIC-034-exception-handling-transparency/STORIES/STORY-130-adapter-exception-logging.md) | Add Structured Logging to All Adapter Exception Handlers | EPIC-034 | 🔴 Open |
| [STORY-131](EPICS/EPIC-034-exception-handling-transparency/STORIES/STORY-131-null-safety-division.md) | Add Null Safety Guards for Division Operations | EPIC-034 | 🔴 Open |
| [STORY-137](EPICS/EPIC-036-configuration-consolidation/STORIES/STORY-137-centralize-env-vars.md) | Centralize All Environment Variables in config.py | EPIC-036 | 🔴 Open |
| [STORY-138](EPICS/EPIC-036-configuration-consolidation/STORIES/STORY-138-config-driven-paths.md) | Replace Hardcoded Paths with Config-Driven Paths | EPIC-036 | 🔴 Open |
| [STORY-139](EPICS/EPIC-036-configuration-consolidation/STORIES/STORY-139-centralize-timeouts.md) | Centralize Timeouts and Magic Numbers | EPIC-036 | 🔴 Open |
| [STORY-140](EPICS/EPIC-036-configuration-consolidation/STORIES/STORY-140-fix-env-example.md) | Fix .env.example with All Required Variables | EPIC-036 | 🔴 Open |
| [STORY-145](EPICS/EPIC-038-ai-readiness-assessment-framework/STORIES/STORY-145-portfolio-ai-readiness-scoring.md) | Portfolio Company AI-Readiness Scoring Model | EPIC-038 | 🔴 Open |
| [STORY-146](EPICS/EPIC-038-ai-readiness-assessment-framework/STORIES/STORY-146-transformation-readiness-calculator.md) | AI Transformation Readiness Calculator | EPIC-038 | 🔴 Open |
| [STORY-147](EPICS/EPIC-038-ai-readiness-assessment-framework/STORIES/STORY-147-pe-due-diligence-integration.md) | PE Due Diligence Integration Module | EPIC-038 | 🔴 Open |
| [STORY-149](EPICS/EPIC-039-energy-sector-specialization/STORIES/STORY-149-energy-compliance-module.md) | Energy Compliance & Regulatory Scoring Module | EPIC-039 | 🔴 Open |
| [STORY-150](EPICS/EPIC-039-energy-sector-specialization/STORIES/STORY-150-energy-forecasting-scoring.md) | Energy Market Forecasting & Demand Scoring | EPIC-039 | 🔴 Open |
| [STORY-151](EPICS/EPIC-039-energy-sector-specialization/STORIES/STORY-151-trading-platform-assessment.md) | Trading Platform & Digital Infrastructure Assessment | EPIC-039 | 🔴 Open |
| [STORY-152](EPICS/EPIC-039-energy-sector-specialization/STORIES/STORY-152-grid-integration-scoring.md) | Grid Integration & Smart Infrastructure Scoring | EPIC-039 | 🔴 Open |

### P2 — Next Quarter (73 stories)

[See full list in EPICS directories]

### P3 — Sustaining (20 stories)

[See full list in EPICS directories]

</details>

---

## Quick Links

- [System Map & Target Architecture](SYSTEM_MAP.md)
- [Story Template](.backlog/templates/story.md)
- [Milestones](MILESTONES/)
- [Estimation Framework](GUIDELINES/ESTIMATION.md)
- [Risk Assessment](GUIDELINES/RISK-ASSESSMENT.md)
- [Success Metrics](GUIDELINES/SUCCESS-METRICS.md)
- [NOT DOING List](GUIDELINES/NOT-DOING.md)
- [Story Status Workflow](GUIDELINES/WORKFLOW.md)
- [Dependency Visualization](MILESTONES/dependency-graph.md)
- [Archived/Superseded Stories](archive/superseded/)

---

## Contributing to the Backlog

1. Use the [story template](.backlog/templates/story.md) for all new stories
2. Assign T-shirt size estimation using the [estimation framework](GUIDELINES/ESTIMATION.md)
3. Assess risk using the [risk matrix](GUIDELINES/RISK-ASSESSMENT.md)
4. Update this README if adding new epics or changing priorities
5. Run `python scripts/update-backlog-metrics.py` to refresh dashboard counts
