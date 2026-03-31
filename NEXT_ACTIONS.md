# Solstein — Next Actions Plan

**Generated:** 2026-03-31  
**Based on:** Full audit of 65 epics, 255+ stories, 550 source files, 1,058 commits

---

## Stop. Read This First.

**The system does not work.** Auth is broken (jwt.py missing), tests can't run (43 files broken by config changes), and 4 documents claim to be "source of truth" with conflicting statuses.

**Before writing any new code, fix M0-Emergency.**

---

## Priority 0: Emergency (Week 1)

| # | Action | File | Effort |
|---|--------|------|--------|
| 1 | Create `solstein/security/jwt.py` | `src/solstein/security/jwt.py` | 1h |
| 2 | Add test conftest Settings mock | `tests/conftest.py` | 2h |
| 3 | Fix classification test assertions | `tests/unit/analytics/test_classification.py` | 1h |
| 4 | Fix Company ID in test factories | `tests/factories/` | 30m |
| 5 | Archive conflicting status docs | `docs/active/` | 30m |
| 6 | Renumber duplicate stories | `backlog/EPICS/` | 2h |

**Total: ~7 hours**

---

## Priority 1: Foundation (Weeks 2-4)

| # | Epic | Stories | Why |
|---|------|---------|-----|
| 7 | Complete requests→httpx migration | 15 files | Async event loop blocked |
| 8 | Fix scoring dedup tests | 3 tests | STORY-010 regression |
| 9 | EPIC-004 remaining (STORY-013/014) | 2 stories | Data integrity incomplete |
| 10 | EPIC-005 dead code elimination | 4 stories | 7 stub agents returning fake data |
| 11 | EPIC-006 duplicate adapters | 4 stories | 6 duplicate adapter pairs |
| 12 | EPIC-043 repo cleanup | 4 stories | 39 conflicting markdown files |

**Total: ~3 weeks**

---

## Priority 2: Data Pipeline (Weeks 5-8)

| # | Epic | Stories | Why |
|---|------|---------|-----|
| 13 | EPIC-058 data conversion | 4 stories | 70% field loss in pipeline |
| 14 | EPIC-059 input validation | 5 stories | No validation on Company model |
| 15 | EPIC-046 scoring correctness | 4 stories | Silent None handling |
| 16 | EPIC-052 quality gates | 4 stories | No provenance enforcement |
| 17 | EPIC-033 export integrity | 4 stories | Release gate blocks all real data |

**Total: ~4 weeks**

---

## Priority 3: Modern Stack (Weeks 9-16)

| # | Epic | Stories | Why |
|---|------|---------|-----|
| 18 | EPIC-020 Supabase Auth | 4 stories | Replace broken auth |
| 19 | EPIC-019 Multi-tenancy | 4 stories | Business requirement |
| 20 | EPIC-021 Modern LLM | 5 stories | 661-line LLM client |
| 21 | EPIC-022 LangGraph Agents | 4 stories | Replace 7 stub agents |
| 22 | EPIC-023 pgvector Search | 3 stories | Semantic search |
| 23 | EPIC-014 Observability | 6 stories | Fake health checks |

**Total: ~8 weeks**

---

## Priority 4: Business Value (Weeks 17-24)

| # | Epic | Stories | Why |
|---|------|---------|-----|
| 24 | EPIC-029 Frontend Dashboard | 5 stories | User interface |
| 25 | EPIC-025 Worker Reliability | 5 stories | Production stability |
| 26 | EPIC-030 Export Modernization | 5 stories | Customer deliverable |
| 27 | EPIC-038 AI Readiness | 4 stories | Business differentiator |
| 28 | EPIC-039 Energy Sector | 4 stories | Market expansion |

**Total: ~8 weeks**

---

## Deprioritized (Do NOT Start)

| Epic | Reason | Revisit |
|------|--------|---------|
| EPIC-016 CQRS | Premature optimization | After M5 |
| EPIC-040 Multi-Market | No customers | Q4 2026 |
| EPIC-041 Equity Model | Business speculation | Q4 2026 |
| EPIC-042 Rapid Validation | No product-market fit | Q4 2026 |
| EPIC-054 Stateful Graph | LangGraph not ready | After EPIC-022 |
| EPIC-055 Role-Based Runtime | Premature | After EPIC-022 |
| EPIC-056 Tool Sandboxing | Premature | After EPIC-022 |
| EPIC-057 Human Review | Premature | After EPIC-022 |

---

## Recommended Framework for Each Phase

| Phase | Framework | Why |
|-------|-----------|-----|
| M0 Emergency | **Hermes Agent** | Fast code fixes, memory, skills |
| M1 Foundation | **Hermes Agent** | Refactoring, dead code removal |
| M2 Data Pipeline | **Agent Zero** | Docker-isolated data processing |
| M3 Modern Stack | **Hermes + LiteLLM** | Complex integration work |
| M4 Business Value | **OpenClaw** | Multi-channel, team-facing |

---

## Realistic Timeline

| Milestone | Duration | Cumulative |
|-----------|----------|------------|
| M0: Emergency | 1 week | 1 week |
| M1: Foundation | 3 weeks | 4 weeks |
| M2: Data Pipeline | 4 weeks | 8 weeks |
| M3: Modern Stack | 8 weeks | 16 weeks |
| M4: Business Value | 8 weeks | 24 weeks |

**Total: ~24 weeks (6 months)** — realistic for 65 epics, 255+ stories.

---

## Files Created by This Audit

| File | Purpose |
|------|---------|
| `AUDIT-REPORT.md` | Full findings and verified status |
| `NEXT_ACTIONS.md` | This file — execution plan |
| `backlog/MILESTONES/M0-Emergency.md` | Emergency milestone stories |
