# M5: Production Ready

> Worker reliability, service topology, CI/CD automation, and observability.

| Field | Value |
|-------|-------|
| **Target Date** | 2026-05-15 |
| **Duration** | 2 weeks |
| **Epics** | 4 |
| **Stories** | 19 |
| **Status** | 🔴 Not Started |
| **Depends On** | [M4: Intelligent Agents](M4-Intelligent-Agents.md) |

---

## Goal

Make the platform production-ready with reliable workers, proper service topology, automated CI/CD, and comprehensive observability. This milestone transforms the system from "it works on my machine" to "it works at scale, 24/7."

---

## Included Epics

| Epic | Title | Stories | Priority |
|------|-------|---------|----------|
| [EPIC-025](../EPICS/EPIC-025-worker-reliability/README.md) | Worker Reliability | 5 | P1 |
| [EPIC-026](../EPICS/EPIC-026-service-topology/README.md) | Service Topology | 4 | P1 |
| [EPIC-027](../EPICS/EPIC-027-cicd-automation/README.md) | CI/CD Automation | 4 | P1 |
| [EPIC-014](../EPICS/EPIC-014-observability-telemetry/README.md) | Observability & Telemetry | 6 | P2 |

---

## Story Breakdown

### EPIC-025: Worker Reliability

| Story | Title | Size | Risk |
|-------|-------|------|------|
| STORY-088 | Fix In-Memory DLQ — Persist to PostgreSQL | M | Medium |
| STORY-089 | Set task_acks_late and task_reject_on_worker_lost | S | Low |
| STORY-090 | Implement Task Idempotency via Deduplication Lock | M | Medium |
| STORY-091 | Set Result Expiry TTL to Prevent Redis Bloat | S | Low |
| STORY-092 | Merge worker_tasks_v2.py — Eliminate Duplicate Task Files | M | Medium |

### EPIC-026: Service Topology

| Story | Title | Size | Risk |
|-------|-------|------|------|
| STORY-093 | Add Celery Worker Service to docker-compose | S | Low |
| STORY-094 | Add Celery Beat Service to docker-compose | S | Low |
| STORY-095 | Add Flower Monitoring Service to docker-compose | S | Low |
| STORY-096 | Multi-Stage Dockerfile for Production | M | Medium |

### EPIC-027: CI/CD Automation

| Story | Title | Size | Risk |
|-------|-------|------|------|
| STORY-097 | Automate Alembic Migrations Pre-Deploy | M | Medium |
| STORY-098 | Add migrate, seed, deploy Makefile Targets | S | Low |
| STORY-099 | Add Staging Deploy + Post-Deploy Smoke Test Workflow | M | Medium |
| STORY-100 | Delete Root Bypass Scripts | S | Low |

### EPIC-014: Observability & Telemetry

| Story | Title | Size | Risk |
|-------|-------|------|------|
| STORY-047 | Replace Fake Health Checks with Real Probes | M | Medium |
| STORY-049 | Add Structured Logging with Correlation IDs | M | Low |
| STORY-050 | Implement OpenTelemetry Distributed Tracing | L | Medium |
| STORY-051 | Add Prometheus Metrics Endpoints | M | Low |
| STORY-086 | Enforce Universal Audit Trail Across All Endpoints | M | Medium |
| STORY-087 | Implement Celery Dead Letter Queue | M | Medium |

---

## Dependencies

**Hard:**
- [M4: Intelligent Agents](M4-Intelligent-Agents.md) — Core functionality must be stable

**Soft:**
- EPIC-025 should complete before EPIC-027 (workers before automation)

---

## Exit Criteria

- [ ] 99.9% uptime achieved
- [ ] MTTR <30 minutes
- [ ] Automated rollback tested and documented
- [ ] Monitoring coverage >95%
- [ ] All deployments automated
- [ ] Health checks verify actual system health
- [ ] Distributed tracing in place

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Uptime | N/A | 99.9% |
| MTTR | Unknown | <30 min |
| Deploy time | Manual | <10 min |
| Deploy frequency | Weekly | On-demand |
| Failed deploy rollback | Manual | <5 min |
| Monitoring coverage | ~20% | >95% |
| Alert false positive rate | N/A | <10% |

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Docker complexity | Medium | Medium | Test locally, document thoroughly |
| CI/CD pipeline failures | Medium | High | Staging environment, smoke tests |
| Monitoring noise | Medium | Medium | Tune thresholds, review alerts |
| Migration failures | Medium | High | Test migrations, rollback scripts |
| Worker reliability issues | Medium | High | Comprehensive testing, DLQ monitoring |

---

## Definition of Done

- [ ] All stories in Done status
- [ ] Production deployment successful
- [ ] Runbook created
- [ ] On-call rotation established
- [ ] Demo to stakeholders
- [ ] M6 planning ready

---

## Related

- [M4: Intelligent Agents](M4-Intelligent-Agents.md) — Previous milestone
- [M6: Business Value](M6-Business-Value.md) — Next milestone
