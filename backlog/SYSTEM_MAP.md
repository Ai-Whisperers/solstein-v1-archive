# Solstein: System Map & Target Architecture

> The architecture we have versus the architecture we deserve. Use this as the north star for all remediation work.

> Last Updated: 2026-02-28 | Companion to: [Engineering Backlog](README.md)

---

## 1. Current State — The Reality

The current Solstein architecture is the result of rapid prototyping that was never consolidated. It contains dual middleware systems (one in `middleware/security.py`, another partially in `data/security_hardening.py`), three independent classification threshold definitions that produce different outputs for the same input, an authentication system that explicitly accepts all credentials, and health checks that verify nothing. The diagram below is not a simplification — it is a faithful representation of what the codebase actually does.

```mermaid
graph TD
    subgraph "Security Layer — BROKEN"
        AUTH["auth.py<br/>Demo: Accept any credentials<br/>lines 57-60"]
        BYPASS["security.py<br/>/companies and /enrichment<br/>BYPASS AUTH lines 62-63"]
    end

    subgraph "Config — CORRUPTED"
        CONFIG["config.py<br/>Duplicate class bodies<br/>postgres:postgres default<br/>change-me-in-production default"]
    end

    subgraph "Scoring — THREE IMPLEMENTATIONS"
        S1["scoring.py<br/>Lead threshold: 3.9"]
        S2["classification.py<br/>Lead threshold: 5.5"]
        S3["Router handlers<br/>own hardcoded values"]
    end

    subgraph "Data — NO ATOMICITY"
        DW["research_dual_write.py<br/>7 sequential commits<br/>no rollback<br/>no saga"]
    end

    subgraph "Monitoring — THEATER"
        HEALTH["monitoring.py lines 96, 127<br/>asyncio.sleep 0.01<br/>masquerading as health check"]
    end

    subgraph "Agents — STUBBED"
        STUBS["7 stub agents<br/>hardcoded mock data<br/>no external calls"]
    end

    subgraph "Migration — INCOMPLETE"
        DUPS["6 duplicate adapter pairs<br/>old and new coexisting<br/>no canonical indicator"]
    end

    AUTH --> CONFIG
    S1 --> CONFIG
    S2 --> CONFIG
    DW --> CONFIG
    HEALTH --> CONFIG
```

---

## 2. Target Clean Architecture

The target architecture follows a strict layered dependency model. Each layer depends only on the layer directly below it. Infrastructure concerns never leak into domain logic. The domain layer has zero framework dependencies.

```mermaid
graph TB
    subgraph "Presentation Layer"
        direction LR
        ROUTERS["FastAPI Routers<br/>request/response only"]
        SCHEMAS["Pydantic Schemas<br/>validation boundary"]
    end

    subgraph "Application Layer"
        direction LR
        SERVICES["Application Services<br/>orchestration only"]
        CMDS["Commands / Queries<br/>CQRS boundary"]
    end

    subgraph "Domain Layer"
        direction LR
        ENTITIES["Rich Domain Entities<br/>Company, FinancialData"]
        VOBJS["Value Objects<br/>Revenue, EmployeeCount"]
        EVENTS["Domain Events<br/>ResearchCompleted"]
        REPOS_I["Repository Interfaces<br/>Protocols / ABCs"]
        DSVCS["Domain Services<br/>ScoringService, ClassificationService"]
    end

    subgraph "Infrastructure Layer"
        direction LR
        DB["PostgreSQL<br/>SQLAlchemy 2.0 async"]
        CACHE["Redis<br/>Single CacheService"]
        LLM["LLM Client<br/>with UsageTracker"]
        AGENTS["External Agents<br/>real implementations"]
        REPOS_I2["Repository Implementations"]
    end

    ROUTERS -->|"validated input"| SERVICES
    SERVICES -->|"commands/queries"| CMDS
    CMDS -->|"domain operations"| ENTITIES
    ENTITIES -->|"uses"| DSVCS
    SERVICES -->|"persists via"| REPOS_I
    REPOS_I -.->|"implemented by"| REPOS_I2
    REPOS_I2 --> DB
    REPOS_I2 --> CACHE
    AGENTS --> LLM
```

### Layer Responsibilities

| Layer | Allowed Dependencies | Prohibited |
|-------|---------------------|------------|
| **Presentation** | Application Layer, Pydantic | Database, Redis, LLM clients |
| **Application** | Domain Layer | Direct DB access, HTTP concerns |
| **Domain** | Standard library only | Any framework, any infrastructure |
| **Infrastructure** | Domain interfaces, external libraries | Business logic, HTTP concerns |

---

## 3. Research Pipeline — Target Data Flow

The research pipeline is the platform's most critical data path. It must be atomic, observable, and recoverable.

```mermaid
sequenceDiagram
    participant Client
    participant Router as Enrichment Router
    participant Service as ResearchService
    participant Agents as Agent Coordinator
    participant DB
    participant Outbox

    Client->>Router: POST /enrichment/{company_id}
    Router->>Router: Validate JWT + Sanitize Input
    Router->>Service: initiateResearch(company_id)
    Service->>Agents: fetchAll() [parallel]
    Agents-->>Service: RawFacts[]
    Service->>Service: resolveConflicts(facts, recency+reliability)
    Service->>DB: BEGIN TRANSACTION
    DB-->>Service: tx_id
    Service->>DB: upsertCompanyData()
    Service->>Outbox: writeEvent() [within same tx]
    Service->>DB: COMMIT
    DB-->>Service: Success
    Service-->>Router: ResearchResult
    Router-->>Client: HTTP 200 + typed response
```

### Key Invariants

1. **Atomicity**: All writes within a research execution occur within a single database transaction. No partial writes persist.
2. **Outbox ordering**: The outbox record is written within the same transaction as the primary data. It is never committed before the data it references.
3. **Conflict resolution**: When multiple agents return conflicting facts, resolution considers data recency first, source reliability second.
4. **Idempotency**: Re-executing the same research request produces the same result, not duplicate records.

---

## 4. Security Boundary — Target State

Every HTTP request must pass through the full middleware chain unless the route is explicitly documented as public. There are exactly four public routes.

```mermaid
graph LR
    EXT[External Client]

    subgraph "Public Routes — No Auth"
        HEALTH_EP["/health — real DB probe"]
        DOCS_EP["/docs, /openapi.json"]
    end

    subgraph "Auth Middleware — ALL private routes"
        RATE["RateLimitMiddleware<br/>first in chain"]
        AUTH_MW["AuthMiddleware<br/>JWT validation<br/>no bypass list"]
        SANITIZE["SanitizationMiddleware<br/>security_hardening.py<br/>applied universally"]
    end

    subgraph "Protected Routes"
        COMPANIES["/companies"]
        ENRICH["/enrichment"]
        SCORING_R["/scoring"]
        EXPORT_R["/export"]
    end

    EXT -->|"HTTP"| RATE
    RATE --> AUTH_MW
    AUTH_MW --> SANITIZE
    SANITIZE --> COMPANIES
    SANITIZE --> ENRICH
    SANITIZE --> SCORING_R
    SANITIZE --> EXPORT_R
    EXT --> HEALTH_EP
    EXT --> DOCS_EP
```

### Public Route Allowlist (Exhaustive)

| Route | Reason |
|-------|--------|
| `/health` | Infrastructure monitoring — must be accessible without credentials |
| `/docs` | OpenAPI documentation browser |
| `/openapi.json` | Machine-readable API specification |
| `/auth/login` | Authentication endpoint — credentials are the input, not a prerequisite |

Any route not in this list requires a valid JWT in the `Authorization` header. No exceptions. No environment-gated bypasses.

---

## 5. Domain Model — Target

The domain model uses value objects for financial quantities, ensuring type safety and preventing primitive obsession. Scores are tracked over time for auditability.

```mermaid
erDiagram
    Company {
        UUID id
        string name
        string registration_number
        TierClassification tier
    }
    Revenue {
        Decimal amount
        Currency currency
        Date as_of_date
    }
    EmployeeCount {
        int value
        Date as_of_date
        string source
    }
    CompositeScore {
        Decimal financial_health
        Decimal growth_momentum
        Decimal competitive_position
        Decimal composite
        Date scored_at
    }
    ResearchEvent {
        UUID id
        UUID company_id
        DateTime initiated_at
        DateTime completed_at
        string status
    }
    Company ||--|| Revenue : "has current"
    Company ||--|| EmployeeCount : "has current"
    Company ||--o{ CompositeScore : "scored over time"
    Company ||--o{ ResearchEvent : "generates"
```

### Value Object Rules

1. Value objects are immutable after construction
2. Equality is based on value, not identity
3. Currency-bearing amounts carry their currency — no implicit GBP assumption
4. Dates use `date` for business dates, `datetime` for timestamps — never strings

---

## 6. Epic Dependency Graph

This graph governs execution order. An epic may not begin until all epics it depends on are complete.

```mermaid
graph LR
    E002[EPIC-002<br/>Config Integrity<br/>P0]
    E001[EPIC-001<br/>Security<br/>P0]
    E003[EPIC-003<br/>Correctness<br/>P0]
    E004[EPIC-004<br/>Data Integrity<br/>P0]
    E007[EPIC-007<br/>DDD Migration<br/>P1]
    E008[EPIC-008<br/>God Files<br/>P1]
    E010[EPIC-010<br/>API Hardening<br/>P1]
    E014[EPIC-014<br/>Observability<br/>P2]
    E018[EPIC-018<br/>CI/CD<br/>P1]

    E002 --> E001
    E001 --> E003
    E001 --> E004
    E007 --> E010
    E008 --> E007
    E010 --> E014
    E018 --> E014
```

### Reading the Graph

- **Arrows point from prerequisite to dependent.** EPIC-002 must complete before EPIC-001 can begin.
- **Parallel work is permitted** where no arrow connects two epics. EPIC-003 and EPIC-004 can proceed concurrently after EPIC-001.
- **EPIC-002 is the root.** Nothing else starts until configuration is clean.

---

## Appendix: File Locations Quick Reference

| Concern | Current Location | Target Location |
|---------|-----------------|-----------------|
| Authentication | `api/routers/auth.py` | `api/routers/auth.py` (rewritten) |
| Auth Middleware | `api/middleware/security.py` | `api/middleware/auth.py` (dedicated) |
| Sanitization | `data/security_hardening.py` | `api/dependencies/sanitization.py` |
| Configuration | `config.py` (single file) | `config.py` (deduplicated, validated) |
| Classification | `analytics/classification.py` | `domain/scoring/classification.py` |
| Scoring | `analytics/scoring.py` + `analytics/scorers/` | `domain/scoring/` (single implementation) |
| Research Pipeline | `infrastructure/research_dual_write.py` | `application/services/research_service.py` |
| Conflict Resolution | `infrastructure/conflict_resolution.py` | `domain/services/conflict_resolution.py` |
| Data Loading | `data/unified_loader.py` | `infrastructure/loaders/` (decomposed) |
| Health Checks | `monitoring.py` | `api/health.py` (real probes) |
