# Milestone Dependency Visualization

> Visual roadmap showing execution order and critical path.

---

## Gantt Chart

```mermaid
gantt
    title Solstein Roadmap Q1-Q2 2026
    dateFormat YYYY-MM-DD
    
    section Foundation
    M1: Safe Foundation           :m1, 2026-03-01, 14d
    
    section Identity
    M2: Secure Identity           :m2, after m1, 14d
    
    section Data
    M3: Modern Data Layer         :m3, after m2, 14d
    
    section Intelligence
    M4: Intelligent Agents        :m4, after m3, 14d
    
    section Production
    M5: Production Ready          :m5, after m4, 14d
    
    section Value
    M6: Business Value            :m6, after m5, 14d
```

---

## Epic Dependency Graph

```mermaid
graph TB
    %% Foundation
    E002[EPIC-002<br/>Config Integrity<br/>P0]
    E036[EPIC-036<br/>Config Consolidation<br/>P2]
    E037[EPIC-037<br/>Dead Code Phase 2<br/>P2]
    E043[EPIC-043<br/>Repo Cleanup<br/>P2]
    
    %% Identity
    E020[EPIC-020<br/>Supabase Auth<br/>P1]
    E019[EPIC-019<br/>Multi-Tenancy<br/>P1]
    
    %% Data
    E023[EPIC-023<br/>pgvector Search<br/>P2]
    E024[EPIC-024<br/>Realtime Status<br/>P2]
    E030[EPIC-030<br/>Export Pipeline<br/>P2]
    E033[EPIC-033<br/>Data Completeness<br/>P1]
    
    %% Intelligence
    E021[EPIC-021<br/>Modern LLM Stack<br/>P1]
    E022[EPIC-022<br/>LangGraph<br/>P2]
    
    %% Production
    E025[EPIC-025<br/>Worker Reliability<br/>P1]
    E026[EPIC-026<br/>Service Topology<br/>P1]
    E027[EPIC-027<br/>CI/CD Automation<br/>P1]
    E014[EPIC-014<br/>Observability<br/>P2]
    
    %% Value
    E038[EPIC-038<br/>AI Readiness<br/>P1]
    E039[EPIC-039<br/>Energy Sector<br/>P1]
    
    %% Dependencies
    E002 --> E020
    E036 --> E020
    E020 --> E019
    E019 --> E023
    E019 --> E024
    E019 --> E030
    E025 --> E030
    E033 --> E030
    E023 --> E021
    E021 --> E022
    E022 --> E025
    E025 --> E026
    E026 --> E027
    E027 --> E014
    E014 --> E038
    E021 --> E038
    E007[EPIC-007<br/>DDD Migration<br/>P1] -.-> E038
    E014 --> E039
```

---

## Critical Path

The critical path (longest sequence of dependent work) determines the minimum project duration:

```
M1 (Safe Foundation)
  └─► M2 (Secure Identity)
        └─► M3 (Modern Data Layer)
              └─► M4 (Intelligent Agents)
                    └─► M5 (Production Ready)
                          └─► M6 (Business Value)
```

**Critical Path Duration:** 12 weeks (84 days)

**Float (slack) available on:**
- EPIC-036, EPIC-037, EPIC-043 (can run in parallel with EPIC-002)
- EPIC-014 (can run in parallel with EPIC-027)

---

## Parallel Work Streams

### Stream 1: Foundation (Weeks 1-2)
- EPIC-002 (P0) — Config Integrity
- EPIC-036, EPIC-037, EPIC-043 (P2) — Cleanup

### Stream 2: Security (Weeks 3-4)
- EPIC-020 (P1) — Supabase Auth
- EPIC-019 (P1) — Multi-Tenancy

### Stream 3: Data (Weeks 5-6)
- EPIC-023 (P2) — pgvector
- EPIC-024 (P2) — Realtime
- EPIC-030 (P2) — Exports
- EPIC-033 (P1) — Data Completeness

### Stream 4: Intelligence (Weeks 7-8)
- EPIC-021 (P1) — LLM Stack
- EPIC-022 (P2) — LangGraph

### Stream 5: Production (Weeks 9-10)
- EPIC-025 (P1) — Workers
- EPIC-026 (P1) — Services
- EPIC-027 (P1) — CI/CD
- EPIC-014 (P2) — Observability

### Stream 6: Value (Weeks 11-12)
- EPIC-038 (P1) — AI Readiness
- EPIC-039 (P1) — Energy Sector

---

## Risk Points

High-risk dependencies that could delay the critical path:

| Dependency | Risk | Mitigation |
|------------|------|------------|
| EPIC-002 → EPIC-020 | Config must be clean before auth | Prioritize EPIC-002, add buffer |
| EPIC-021 → EPIC-022 | LLM stack before LangGraph | Spike story for LangGraph |
| EPIC-025 → EPIC-026 | Workers before services | Test worker reliability early |

---

## Alternative Paths

### Accelerated Path (10 weeks)

If resources allow parallel work:

```
Week 1-2:  M1 (Foundation)
Week 3-4:  M2 (Identity) + Start EPIC-021
Week 5-6:  M3 (Data) + Continue EPIC-021
Week 7-8:  M4 (Intelligence) 
Week 9-10: M5 (Production)
Week 11-12: M6 (Value)
```

**Requires:**
- 2 senior engineers (can work in parallel streams)
- EPIC-021 must be able to start after M2 (not strictly dependent on M3)

### Conservative Path (14 weeks)

If team is new or risks are high:

```
Week 1-2:   M1 (Foundation)
Week 3-4:   M2 (Identity)
Week 5-6:   Buffer / Risk mitigation
Week 7-8:   M3 (Data)
Week 9-10:  M4 (Intelligence)
Week 11-12: M5 (Production)
Week 13-14: M6 (Value)
```

---

## Related

- [M1: Safe Foundation](M1-Safe-Foundation.md)
- [M2: Secure Identity](M2-Secure-Identity.md)
- [M3: Modern Data Layer](M3-Modern-Data-Layer.md)
- [M4: Intelligent Agents](M4-Intelligent-Agents.md)
- [M5: Production Ready](M5-Production-Ready.md)
- [M6: Business Value](M6-Business-Value.md)
