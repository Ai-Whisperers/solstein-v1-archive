# M1: Safe Foundation

> Clean configuration, eliminate dead code, establish repository standards.

| Field | Value |
|-------|-------|
| **Target Date** | 2026-03-15 |
| **Duration** | 2 weeks |
| **Epics** | 4 |
| **Stories** | 15 |
| **Status** | 🔴 Not Started |

---

## Goal

Establish a solid foundation by cleaning up configuration, removing dead code, and organizing the repository. This milestone prepares the ground for all subsequent work. Without a clean foundation, every future change inherits technical debt.

---

## Included Epics

| Epic | Title | Stories | Priority |
|------|-------|---------|----------|
| [EPIC-002](../EPICS/EPIC-002-configuration-integrity/README.md) | Configuration Integrity | 3 | P0 |
| [EPIC-036](../EPICS/EPIC-036-configuration-consolidation/README.md) | Configuration Consolidation | 4 | P2 |
| [EPIC-037](../EPICS/EPIC-037-dead-code-elimination-phase-2/README.md) | Dead Code Elimination Phase 2 | 4 | P2 |
| [EPIC-043](../EPICS/EPIC-043-repository-cleanup/README.md) | Repository Cleanup & Organization | 4 | P2 |

---

## Story Breakdown

### EPIC-002: Configuration Integrity (P0)

| Story | Title | Size | Risk |
|-------|-------|------|------|
| STORY-006 | Fix Duplicate Class Body Definitions in config.py | S | Medium |
| STORY-007 | Remove All Hardcoded Credentials | M | High |
| STORY-008 | Add Mandatory Startup Validation for All API Keys | M | Medium |

### EPIC-036: Configuration Consolidation

| Story | Title | Size | Risk |
|-------|-------|------|------|
| STORY-137 | Centralize All Environment Variables in config.py | M | Low |
| STORY-138 | Replace Hardcoded Paths with Config-Driven Paths | S | Low |
| STORY-139 | Centralize Timeouts and Magic Numbers | S | Low |
| STORY-140 | Fix .env.example with All Required Variables | S | Low |

### EPIC-037: Dead Code Elimination Phase 2

| Story | Title | Size | Risk |
|-------|-------|------|------|
| STORY-141 | Delete Disconnected Refresh Router | S | Low |
| STORY-142 | Delete Orphaned worker_tasks_v2.py | S | Low |
| STORY-143 | Audit and Delete Orphaned Data Layer Files | M | Medium |
| STORY-144 | Create Dead Code Detection CI Job | M | Low |

### EPIC-043: Repository Cleanup & Organization

| Story | Title | Size | Risk |
|-------|-------|------|------|
| STORY-165 | Archive Historical Professionalization Documents | S | Low |
| STORY-166 | Consolidate Setup Documentation | S | Low |
| STORY-167 | Organize Strategic Documents | S | Low |
| STORY-168 | Create Repository Organization Standards | S | Low |

---

## Dependencies

**No hard dependencies** — this is the first milestone.

**Soft dependencies:**
- M2 (Secure Identity) cannot start until EPIC-002 is complete

---

## Exit Criteria

- [ ] Zero P0 security vulnerabilities in configuration
- [ ] Config validation at startup (100% coverage)
- [ ] Dead code <10% of codebase
- [ ] All tests passing
- [ ] Repository root clean (no clutter)
- [ ] Documentation organized and current

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Config validation coverage | 0% | 100% |
| Hardcoded credentials | 5+ | 0 |
| Dead code percentage | ~15% | <10% |
| Repository root files | 25+ | <15 |

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Dead code removal breaks something | Medium | Medium | Comprehensive test coverage first |
| Config changes break local dev | Medium | Medium | Update setup docs, test with fresh clone |
| Hidden dependencies on "dead" code | Medium | High | Code review, static analysis |

---

## Definition of Done

- [ ] All stories in Done status
- [ ] Exit criteria met
- [ ] Demo to team
- [ ] Retrospective completed
- [ ] M2 planning ready

---

## Related

- [M2: Secure Identity](M2-Secure-Identity.md) — Next milestone
- [Epic Registry](../README.md#epic-registry) — Full epic list
