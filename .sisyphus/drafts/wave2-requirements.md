# Wave 2: Data Freshness & Quality — Requirements Draft

**Date**: February 24, 2026  
**Status**: Requirements Locked & Ready for Planning  
**Executor**: OpenClaw Agents (TBD)  
**Timeline**: No deadline (quality over speed)  

---

## REQUIREMENTS LOCKED

### Data Freshness Features (ALL INCLUDED)

1. **Automated Refresh Scheduling**
   - Scope: Event-driven + periodic
   - Details:
     - Automatic scheduled refresh (configurable per source)
     - Manual trigger API for urgent updates
     - Webhook support for external triggers
     - Health checks (alert if refresh fails)
   - Tech: Celery Beat for scheduling, FastAPI endpoint for manual trigger

2. **Incremental Updates**
   - Scope: Only fetch changed data
   - Details:
     - Track last-modified timestamps per source
     - Delta detection: compare new vs. stored values
     - Avoid re-processing unchanged facts
     - Audit trail: log all updates with timestamps
   - Tech: SQLAlchemy ORM, database migrations

3. **Multi-Source Conflict Resolution**
   - Scope: ALL strategies (smart routing)
   - Details:
     - Highest confidence: auto-resolve when clear winner exists
     - Weighted average: blend values from multiple sources
     - Flag for review: complex contradictions logged for analyst
     - Visibility: UI dashboard shows contradictions + reasoning
   - Tech: Decision tree engine, conflict record table in DB

4. **Confidence Score Tuning**
   - Scope: Learn from accuracy over time
   - Details:
     - Track prediction accuracy: actual vs. observed
     - Adjust confidence scores based on historical accuracy
     - Per-source calibration (SEC 0.95 → maybe 0.92 after tuning)
     - Bootstrap with 10 data points minimum per source
   - Tech: Statistical analysis, confidence adjustment algorithm

### Business Success Metrics (4b & 4c)

- **4b**: System handles contradictory data from 2+ sources gracefully
  - Acceptance: Contradictions logged, auto-resolved when possible, flagged when ambiguous
  
- **4c**: Confidence scores improve after 10 data points per source
  - Acceptance: Confidence adjustments visible in fact record, accuracy tracking enabled

### Quality Improvements (ALL INCLUDED EQUALLY)

1. **Testing**: Unit + integration test coverage 80%+ for Wave 2 features
2. **CI/CD Gates**: Multi-stage validation, automated versioning, deployment gates
3. **Monitoring**: Logging, metrics collection, alerting for data quality
4. **Security**: Secret scanning, audit trails, access control, SBOM

---

## SCOPE DECISIONS

### IN SCOPE
- Automated refresh for all 4 connectors (SEC, CH, News, GitHub)
- Incremental update logic with timestamp tracking
- Conflict resolution engine (3-strategy smart routing)
- Confidence adjustment algorithm with minimum thresholds
- 80%+ test coverage on all new code
- Multi-stage CI/CD pipeline (lint → test → build → deploy gates)
- Comprehensive logging and alerting
- Audit trail for all data mutations
- SBOM generation and dependency scanning

### OUT OF SCOPE (Wave 3+)
- Advanced ML-based conflict resolution
- Multi-run historical trend analysis
- Performance optimization (caching, indexing) — can wait
- User authentication/RBAC — assume trusted environment
- Paid API integration (Crunchbase, LinkedIn) — Wave 4

### CONSTRAINTS
- No paid APIs in Wave 2 (free tier only, like Wave 1)
- Backward compatible with Wave 1 (don't break existing scoring)
- No changes to REST API signatures (internal refactoring OK)
- Must maintain 673+ test passing from Wave 1

---

## EXECUTION MODEL (FOR OPENCLAW AGENTS)

**When OpenClaw executes this plan:**

1. **Parallel Wave Structure**
   - Wave 2.1 (Foundation): Data refresh infrastructure, conflict schema
   - Wave 2.2 (Features): Incremental logic, conflict resolution, confidence tuning
   - Wave 2.3 (Quality): Testing, CI/CD, monitoring setup
   - Wave 2.4 (Integration): E2E tests, validation, hardening

2. **Agent Dispatch Strategy**
   - Streams A-D (data features): Quick/unspecified-high category agents
   - Streams E-F (quality): Testing/deep category agents
   - Final verification: Oracle + performance agents

3. **Expected Effort**
   - Stream A (Refresh scheduling): 8-10 hours
   - Stream B (Incremental updates): 8-10 hours
   - Stream C (Conflict resolution): 12-15 hours (complex logic)
   - Stream D (Confidence tuning): 10-12 hours
   - Stream E (Testing): 12-15 hours
   - Stream F (CI/CD + monitoring + security): 15-20 hours
   - **Total: 65-82 hours parallel (est. 40-50 effective with parallelism)**

4. **Critical Dependencies**
   - Database schema (conflict records, accuracy tracking)
   - Celery infrastructure (scheduling)
   - FastAPI routes (manual trigger endpoint)
   - SQLAlchemy ORM updates (incremental query patterns)

---

## ACCEPTANCE CRITERIA (WAVE 2 COMPLETE)

All must pass:

- [ ] All 4 connectors refresh data automatically on schedule
- [ ] Manual trigger endpoint works: POST /api/refresh/:source_name → job queued
- [ ] Webhook support: external systems can trigger updates
- [ ] Incremental updates: only changed facts fetched/updated (audit trail logged)
- [ ] Contradictions logged when sources disagree
- [ ] Smart routing active: highest confidence auto-wins, complex cases flagged
- [ ] Confidence scores adjust based on 10+ historical data points per source
- [ ] 80%+ test coverage on all Wave 2 code
- [ ] CI/CD pipeline: lint → test → build → deploy gates working
- [ ] Comprehensive logging: every data mutation logged with timestamp/source/user
- [ ] Alerting: failures in refresh/conflict detection trigger notifications
- [ ] Audit trail: searchable log of who changed what, when, why
- [ ] SBOM generated, dependency scanning enabled
- [ ] 673+ Wave 1 tests still passing (no regressions)
- [ ] E2E integration test: 5 companies refresh successfully with conflict resolution
- [ ] Golden dataset regression: 5 companies maintain expected scores ±0.5

---

## TECHNICAL DECISIONS LOCKED

1. **Scheduling**: Celery Beat (already in system)
2. **Database**: PostgreSQL + SQLAlchemy (Wave 1 pattern)
3. **Conflict logic**: Decision tree (hardcoded, not ML)
4. **Confidence adjustment**: Bayesian-inspired (historical accuracy)
5. **Testing framework**: pytest (Wave 1 pattern)
6. **CI/CD**: GitHub Actions (existing setup)
7. **Monitoring**: Prometheus + structured logging (standard patterns)
8. **Audit trail**: Database table with immutable append-only pattern

---

## KNOWN UNKNOWNS (ASK BEFORE PLANNING)

All cleared by user requirements! Proceeding with plan generation.

---

## NEXT STEP

Generate comprehensive Wave 2 work plan to `.sisyphus/plans/solstein-wave2-data-freshness-quality.md`

Plan structure:
- 6 work streams (A-F)
- 4 execution waves
- 40+ individual tasks
- Agent dispatch recommendations
- All acceptance criteria executable
