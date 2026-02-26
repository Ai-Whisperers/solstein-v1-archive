# Solstein Wave 2: Data Freshness & Quality

## TL;DR

> **Quick Summary**: Build automated data refresh infrastructure with conflict resolution, confidence tuning, and comprehensive quality gates. Transform Wave 1 (static facts) into Wave 2 (living, self-improving data pipeline).
> 
> **Deliverables**:
> - Automated refresh scheduling (event-driven + periodic + webhook)
> - Incremental update logic (delta detection, timestamp tracking)
> - Conflict resolution engine (smart routing: highest confidence → weighted average → flag for review)
> - Confidence score tuning (learn from 10+ data points per source)
> - 80%+ test coverage with multi-stage CI/CD pipeline
> - Comprehensive monitoring, logging, audit trails, SBOM generation
> 
> **Estimated Effort**: 65-82 hours parallel (40-50 effective with OpenClaw agents)  
> **Parallel Execution**: YES — 6 streams, 4 waves, max 8 tasks per wave  
> **Critical Path**: Wave 2.1 (schema) → Wave 2.2 (features) → Wave 2.3 (quality) → Wave 2.4 (integration)

---

## Context

### Original Request
User wants Wave 2 to include:
- All 4 data freshness features (scheduling, incremental, conflict, confidence)
- All quality improvements equally (testing, CI/CD, monitoring, security)
- No deadline (quality over speed)
- Designed for OpenClaw agent execution

### Interview Summary
**Key Discussions**:
- Refresh cadence: Event-driven + periodic (automatic schedule + manual trigger + webhook)
- Conflict strategy: Smart routing (highest confidence auto-wins, complex cases flagged, weighted average available)
- Quality focus: All equally (testing 80%+ + CI/CD gates + monitoring + security)
- Business metrics: Handle contradictions gracefully (4b) + confidence improves over time (4c)

**Technical Stack**:
- Scheduling: Celery Beat (existing)
- Database: PostgreSQL + SQLAlchemy ORM
- Testing: pytest (Wave 1 pattern)
- CI/CD: GitHub Actions
- Monitoring: Prometheus + structured logging

### Wave 1 Foundation
- 673 tests passing ✅
- 4 data connectors integrated (SEC, CH, News, GitHub) ✅
- Fact ORM with confidence scores ✅
- Ready for refresh infrastructure

---

## Work Objectives

### Core Objective
Build a **self-improving data pipeline** that:
1. Automatically refreshes data on schedule with manual override capability
2. Fetches only changed data (incremental updates)
3. Gracefully handles contradictions from multiple sources
4. Learns from accuracy: adjusts confidence scores based on historical performance
5. Maintains full audit trail and observability
6. Passes comprehensive test suite (80%+ coverage)
7. Integrates into existing scoring engine without breaking changes

### Concrete Deliverables
- `src/solstein/infrastructure/refresh.py` — Refresh orchestration + scheduling
- `src/solstein/infrastructure/conflict_resolver.py` — Conflict resolution engine
- `src/solstein/infrastructure/confidence_adjuster.py` — Confidence score calibration
- `src/solstein/api/routes/refresh.py` — Manual trigger endpoint + webhook
- Database migrations E2a–E2e: Conflict records, accuracy tracking, audit trail
- `tests/integration/test_refresh_pipeline.py` — E2E refresh tests
- `tests/integration/test_conflict_resolution.py` — Conflict scenarios
- `tests/integration/test_confidence_tuning.py` — Confidence adjustment verification
- CI/CD pipeline configuration: lint → test → build → deploy gates
- Monitoring setup: Prometheus metrics, structured logging, alerting rules
- SBOM generation and dependency scanning

### Definition of Done
- [ ] All 4 connectors refresh data automatically on configurable schedule
- [ ] Manual refresh endpoint: `POST /api/refresh/{source_name}` queues job
- [ ] Webhook support: External systems can trigger refreshes
- [ ] Incremental updates: Only changed facts fetched (delta detection working)
- [ ] Contradictions logged and resolved per smart routing strategy
- [ ] Confidence scores adjust after 10+ data points per source (visible in fact record)
- [ ] 80%+ test coverage on all Wave 2 code
- [ ] CI/CD pipeline: All gates passing (lint, test, build, deploy)
- [ ] Comprehensive logging: Every mutation logged with context
- [ ] Alerting: Failures trigger notifications (Slack/email)
- [ ] Audit trail: Searchable, immutable, includes who/what/when/why
- [ ] SBOM generated, dependency scanning enabled
- [ ] Zero regressions: 673+ Wave 1 tests still passing
- [ ] E2E verification: 5 companies refresh with conflict resolution
- [ ] Golden dataset regression: 5 companies maintain scores ±0.5

### Must Have
- Event-driven + periodic refresh (both required)
- Smart conflict routing (all 3 strategies available)
- Confidence tuning with minimum bootstrap threshold (10 points)
- 80%+ test coverage (not optional)
- Multi-stage CI/CD (not just local testing)
- Audit trail (immutable append-only)

### Must NOT Have (Guardrails)
- No ML-based conflict resolution (hardcoded decision tree only)
- No paid APIs (free tier only, like Wave 1)
- No changes to existing API signatures (backward compatible)
- No authentication/RBAC (assume trusted environment)
- No performance optimization (caching, indexing wait for Wave 3)
- No changes to scoring logic (Wave 2 is infrastructure, not algorithm)

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: YES (pytest, conftest, fixtures)
- **Automated tests**: TDD (tests first, then implementation)
- **Framework**: pytest + pytest-asyncio (async support for Celery/FastAPI)
- **Pattern**: Unit (component logic) + Integration (end-to-end refresh)

### QA Policy
Every task MUST include agent-executed QA scenarios (see TODO template below).
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Refresh scheduling**: Use tmux + Celery to verify scheduler triggers
- **Conflict resolution**: Use pytest to verify decision logic
- **API endpoints**: Use curl to verify manual trigger endpoint
- **Monitoring**: Use grep to verify logs contain expected entries

---

## Execution Strategy

### Parallel Execution Waves

Wave structure for maximum parallelism. Each wave completes before the next.
Target: 6-8 tasks per wave. Total: 4 waves, 30-40 tasks.

```
Wave 2.1 (START IMMEDIATELY — Foundation & Schema):
├── Task 1: Database schema design (refresh metadata, conflict records, accuracy tracking)
├── Task 2: Celery Beat scheduler configuration
├── Task 3: Refresh base class + connector interface
├── Task 4: Manual trigger endpoint (FastAPI route)
├── Task 5: Conflict record data model (ORM)
└── Task 6: Accuracy tracking data model (ORM)

Wave 2.2 (After Wave 2.1 — Core Features, MAX PARALLEL):
├── Task 7: SEC refresh implementation (incremental detection)
├── Task 8: Companies House refresh implementation
├── Task 9: News Signal refresh implementation
├── Task 10: GitHub refresh implementation
├── Task 11: Incremental update logic (delta detection, timestamps)
├── Task 12: Conflict resolution engine (decision tree)
└── Task 13: Confidence adjustment algorithm (Bayesian tuning)

Wave 2.3 (After Wave 2.2 — Testing & Quality):
├── Task 14: Unit tests for refresh logic (80%+ coverage)
├── Task 15: Unit tests for conflict resolution
├── Task 16: Unit tests for confidence adjustment
├── Task 17: Integration test: full refresh pipeline
├── Task 18: Integration test: conflict handling scenarios
├── Task 19: Integration test: confidence tuning verification
├── Task 20: Performance test: refresh time for 50+ companies
└── Task 21: Load test: concurrent refresh requests

Wave 2.4 (After Wave 2.3 — Quality Gates & Hardening):
├── Task 22: CI/CD pipeline: lint stage
├── Task 23: CI/CD pipeline: test stage
├── Task 24: CI/CD pipeline: build stage
├── Task 25: CI/CD pipeline: deploy gates
├── Task 26: Prometheus metrics setup (refresh latency, conflicts, etc.)
├── Task 27: Structured logging configuration
├── Task 28: Alerting rules (refresh failure, conflict spike, etc.)
├── Task 29: Audit trail implementation (immutable append-only)
├── Task 30: SBOM generation + dependency scanning
├── Task 31: Security hardening (secret scanning, access control)
├── Task 32: E2E golden dataset regression test
└── Task 33: Wave 2 acceptance verification

Critical Path: 1 → 2 → 3 → 7-13 → 17-19 → 22-25 → 32-33
Parallel speedup: ~65% faster than sequential (estimated 40-50 effective hours from 80+ parallel)
```

### Dependency Matrix

| Wave | Tasks | Dependencies | Blocked By | Next |
|------|-------|--------------|-----------|------|
| 2.1 | 1-6 | None | — | 2.2 |
| 2.2 | 7-13 | Schema (1,5,6), Celery (2), API (4) | 2.1 | 2.3 |
| 2.3 | 14-21 | Features (7-13) | 2.2 | 2.4 |
| 2.4 | 22-33 | Tests (14-21) | 2.3 | ✅ Complete |

---

## TODOs

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Rejection → fix → re-run.

- [ ] F1. **Data Quality Audit** — `oracle`
  - Read requirements vs. implementation: refresh automation, incremental logic, conflict resolution, confidence tuning all present?
  - Verify all 4 connectors have refresh implementations
  - Check: incremental logic uses timestamp-based delta detection
  - Check: conflict logic implements all 3 strategies (highest confidence, weighted average, flag)
  - Check: confidence adjustment uses 10-point bootstrap
  - Verify: no regressions in Wave 1 (673+ tests passing)
  - Output: `Features [X/X implemented] | Connectors [4/4 working] | Regressions [CLEAN] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Quality Gate Review** — `deep`
  - Run full test suite: pytest tests/ --cov=src/solstein
  - Verify: 80%+ coverage on Wave 2 code (refresh, conflict, confidence modules)
  - Verify: CI/CD pipeline stages complete (lint, test, build, deploy)
  - Verify: all acceptance criteria implemented (audit trail, logging, alerts, SBOM)
  - Output: `Coverage [80%+] | Stages [4/4 passing] | Acceptance [X/X met] | VERDICT: APPROVE/REJECT`

- [ ] F3. **Integration Verification** — `unspecified-high`
  - Execute E2E refresh test: 5 companies refresh successfully
  - Verify: conflict resolution handles contradictions gracefully
  - Verify: confidence scores adjust based on historical accuracy
  - Verify: golden dataset regression (5 companies maintain scores ±0.5)
  - Output: `E2E [PASS] | Conflicts [resolved] | Confidence [tuned] | Regression [CLEAN] | VERDICT: APPROVE/REJECT`

- [ ] F4. **Production Readiness** — `unspecified-high`
  - Verify: all error handling in place (retry logic, timeouts, fallbacks)
  - Verify: monitoring is enabled (logs, metrics, alerts)
  - Verify: audit trail is functional (every mutation logged)
  - Verify: SBOM generated, dependency scanning enabled
  - Verify: no hardcoded secrets, no vulnerable dependencies
  - Output: `Errors [handled] | Monitoring [enabled] | Audit [working] | Security [clean] | VERDICT: APPROVE/REJECT`

---

## Commit Strategy

**Commits per wave:**

**Wave 2.1:**
- `feat(infrastructure): add refresh scheduling + conflict/accuracy schema`
- Files: migrations, refresh base class, Celery config, FastAPI endpoint

**Wave 2.2:**
- `feat(connectors): implement refresh + incremental logic for all sources`
- Files: connector implementations, conflict resolver, confidence adjuster

**Wave 2.3:**
- `test(wave2): comprehensive test coverage for refresh pipeline`
- Files: test files (unit + integration), test fixtures

**Wave 2.4:**
- `ci(wave2): multi-stage CI/CD + monitoring + audit + SBOM`
- Files: GitHub Actions config, Prometheus config, logging setup, migrations

---

## Success Criteria

### Verification Commands

```bash
# Test coverage
pytest tests/ --cov=src/solstein --cov-report=term-missing | grep -E "(80%|100%)"

# Integration test
pytest tests/integration/test_refresh_pipeline.py -v

# Conflict resolution scenarios
pytest tests/integration/test_conflict_resolution.py -v

# Confidence tuning verification
pytest tests/integration/test_confidence_tuning.py -v

# CI/CD pipeline
gh workflow view solstein-ci.yml --json status

# Monitoring validation
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets | length'

# Audit trail
sqlite3 solstein.db "SELECT COUNT(*) FROM audit_log WHERE created_at > datetime('now', '-1 hour');"

# Golden dataset regression
pytest tests/integration/test_golden_dataset_regression.py::test_wave2_refresh -v
```

### Final Checklist
- [ ] All 4 connectors refresh automatically
- [ ] Manual trigger endpoint works
- [ ] Webhook support enabled
- [ ] Incremental updates (delta detection) working
- [ ] Contradictions logged and resolved
- [ ] Confidence scores adjust based on 10+ points
- [ ] 80%+ test coverage
- [ ] CI/CD pipeline passing
- [ ] Comprehensive logging enabled
- [ ] Alerting configured
- [ ] Audit trail functional
- [ ] SBOM generated
- [ ] 673+ Wave 1 tests passing
- [ ] E2E integration test passing
- [ ] Golden dataset regression passing

---

## Notes for OpenClaw Execution

**When OpenClaw agents execute this plan:**

1. **Start with Wave 2.1**: Foundation is critical. Don't skip database schema or Celery setup.
2. **Parallel execution**: Streams A-D can run in parallel during Wave 2.2. They share interfaces but not implementation.
3. **Quality first**: Wave 2.3 and 2.4 are not optional. Quality is equal priority to features.
4. **Verification gates**: Each final verification must PASS before considering Wave 2 complete.
5. **If conflicts arise**: Ask Prometheus (planner) before deviating from plan.

**Agent dispatch hints:**
- Streams A-D (connectors + logic): `quick` / `unspecified-high` agents
- Stream E (testing): `testing` agents with `javascript-testing-patterns` / `python-testing-patterns`
- Stream F (CI/CD + quality): `deep` agents with infrastructure expertise

---

## Session Continuation

If session is interrupted:
1. Read this plan file (single source of truth)
2. Check git status: see which Wave was in progress
3. Resume from next pending task in the current wave
4. All QA scenarios are executable → verify before proceeding
5. Contact Prometheus if scope clarification needed

**This plan is COMPLETE and ready for OpenClaw agent execution.**
