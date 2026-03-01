# M2: Secure Identity

> Production-grade authentication, multi-tenancy, and data isolation.

| Field | Value |
|-------|-------|
| **Target Date** | 2026-03-31 |
| **Duration** | 2 weeks |
| **Epics** | 2 |
| **Stories** | 8 |
| **Status** | 🔴 Not Started |
| **Depends On** | [M1: Safe Foundation](M1-Safe-Foundation.md) |

---

## Goal

Replace the broken custom authentication system with Supabase Auth and implement multi-tenancy with Row Level Security. This milestone makes the platform secure and ready for multiple customers.

---

## Included Epics

| Epic | Title | Stories | Priority |
|------|-------|---------|----------|
| [EPIC-020](../EPICS/EPIC-020-supabase-auth-migration/README.md) | Supabase Auth Migration | 4 | P1 |
| [EPIC-019](../EPICS/EPIC-019-multi-tenancy-data-isolation/README.md) | Multi-Tenancy & Data Isolation | 4 | P1 |

---

## Story Breakdown

### EPIC-020: Supabase Auth Migration

| Story | Title | Size | Risk |
|-------|-------|------|------|
| STORY-067 | Migrate Authentication to Supabase Auth | L | High |
| STORY-068 | Remove Auth Bypass and Wire Supabase JWT Middleware | M | High |
| STORY-069 | Migrate Error Handling and Input Sanitization | M | Medium |
| STORY-070 | Fix SSRF Vulnerability in Web and Website Agents | M | Medium |

### EPIC-019: Multi-Tenancy & Data Isolation

| Story | Title | Size | Risk |
|-------|-------|------|------|
| STORY-063 | Define Tenant Model and Domain Object Scoping | M | Medium |
| STORY-064 | Implement Supabase RLS for All Tables | L | High |
| STORY-065 | Add Tenant-Scoped API Key Management | M | Medium |
| STORY-066 | Enforce Tenant Isolation in Research Jobs | M | Medium |

---

## Dependencies

**Hard:**
- [M1: Safe Foundation](M1-Safe-Foundation.md) — EPIC-002 must be complete

**Soft:**
- EPIC-020 should complete before EPIC-019 (auth before tenant isolation)

---

## Exit Criteria

- [ ] Authentication bypass eliminated
- [ ] JWT secrets externalized to Supabase
- [ ] Multi-tenancy isolation verified with tests
- [ ] SSRF vulnerability patched
- [ ] Security audit passed
- [ ] User migration path documented

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Auth bypass exists | Yes | No |
| JWT secret hardcoded | Yes | No |
| Multi-tenancy | None | Row Level Security |
| Security test coverage | ~20% | >80% |

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| User migration issues | Medium | High | Test migration with backup, rollback plan |
| RLS performance impact | Medium | Medium | Benchmark before/after, optimize queries |
| Supabase outage | Low | High | Document offline mode, caching strategy |
| SSRF fix breaks web agents | Medium | Medium | Comprehensive testing with real URLs |

---

## Definition of Done

- [ ] All stories in Done status
- [ ] Security penetration test passed
- [ ] User migration tested
- [ ] Performance benchmarks acceptable
- [ ] Demo to stakeholders
- [ ] M3 planning ready

---

## Related

- [M1: Safe Foundation](M1-Safe-Foundation.md) — Previous milestone
- [M3: Modern Data Layer](M3-Modern-Data-Layer.md) — Next milestone
