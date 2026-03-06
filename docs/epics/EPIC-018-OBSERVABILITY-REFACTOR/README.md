# EPIC-018: Observability and Error Handling Refactor

> **Status**: 🔴 Critical - Blocks Production Debugging
> **Priority**: P0 - Major Impact
> **Effort**: 13 story points
> **Sprint**: Infrastructure Foundation
> **Related**: Extends EPIC-011 (Error Handling and Logging)

---

## Problem Statement

The system suffers from **critical observability gaps** that make debugging, incident response, and operational monitoring nearly impossible at scale. Current state:

- **Dual logging systems** (Loguru + stdlib) with inconsistent context propagation
- **Silent error swallowing** in middleware (`except Exception: pass`)
- **No request/correlation ID propagation** across async boundaries
- **Stack traces exposed to clients** regardless of environment
- **Inconsistent exception taxonomy** leading to poor error classification
- **Missing structured logging** for production observability
- **No outbound dependency tracing** (LLM calls, database, external APIs)

### Impact on Operations

| Impact Area | Current State | Risk Level |
|-------------|---------------|------------|
| Incident Response | Cannot trace request flow across services | 🔴 Critical |
| Debugging | Stack traces lost or inconsistent | 🔴 Critical |
| Security | Internal details exposed to clients | 🔴 Critical |
| Performance | Cannot identify slow paths | 🟡 High |
| Compliance | No audit trail for data access | 🟡 High |
| Cost | Cannot optimize LLM/provider usage | 🟢 Medium |

---

## Success Criteria

- [ ] All logs use unified Loguru pipeline with consistent formatting
- [ ] Request/correlation/tenant IDs propagate across all async boundaries
- [ ] Zero silent exception swallowing (all errors logged with context)
- [ ] Stack traces never exposed to clients in production
- [ ] Structured JSON logging available for production environments
- [ ] Outbound dependency calls logged with timing and correlation IDs
- [ ] Exception taxonomy reduced to 6-10 domain-specific types with clear HTTP mapping
- [ ] All API routes return consistent error schema with `request_id`
- [ ] Celery tasks log correlation context and failure details
- [ ] Metrics collection for error rates, latency, and dependency health

---

## Technical Analysis Summary

### Root Causes

1. **Logging Fragmentation**: Loguru dominates but stdlib persists in security middleware, outbox worker, audit logging
2. **Context Loss**: `request_id` exists in middleware but doesn't propagate through contextvars to all loggers
3. **Silent Failures**: `ErrorLoggingMiddleware` silently swallows body parsing errors
4. **Security Exposure**: Global exception handler returns `traceback` list unconditionally
5. **Taxonomy Sprawl**: Base exceptions exist but aren't used consistently; custom exceptions scattered
6. **Missing Observability**: No structured logging, no dependency call tracing, no metrics

### Affected Components

| Component | Files | Issues |
|-----------|-------|--------|
| Logging Config | `utils/logging.py`, `config.py` | Dual systems, no contextvars |
| API Middleware | `api/middleware/logging.py`, `api/middleware/tracing.py`, `api/middleware.py` | Duplication, silent errors |
| Exception Handling | `api/exceptions.py`, `exceptions.py` | Exposure, taxonomy gaps |
| Security | `api/middleware/security.py` | Uses stdlib logging |
| Infrastructure | `infrastructure/outbox_worker.py`, `infrastructure/research_dual_write.py` | Uses stdlib logging |
| Error Handling | `core/error_handler.py`, `data/error_logging.py` | Underutilized, fragmentation |
| Data Layer | `data/enrichment_config.py` | Custom exceptions |
| LLM Layer | `llm/structured_client.py`, `llm/enhanced_client.py` | Custom exceptions, no tracing |

---

## Stories Overview

| Story | Title | Priority | Points | Dependencies |
|-------|-------|----------|--------|--------------|
| 18.1 | Unify Logging Pipeline | P0 | 3 | None |
| 18.2 | Implement Context Propagation | P0 | 3 | 18.1 |
| 18.3 | Fix Silent Error Handling | P0 | 2 | 18.1, 18.2 |
| 18.4 | Secure Error Responses | P0 | 2 | 18.1 |
| 18.5 | Standardize Exception Taxonomy | P1 | 2 | 18.4 |
| 18.6 | Add Dependency Tracing | P1 | 1 | 18.2 |

**Total Stories**: 6
**Total Points**: 13

---

## Dependencies

```
Story 18.1 (Unify Logging)
    ├── Story 18.2 (Context Propagation)
    │   ├── Story 18.3 (Fix Silent Errors)
    │   └── Story 18.6 (Dependency Tracing)
    └── Story 18.4 (Secure Responses)
        └── Story 18.5 (Taxonomy)
```

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Log format changes break existing log parsers | Medium | High | Document format changes, provide migration guide |
| Performance impact from contextvars | Low | Medium | Benchmark before/after, optimize hot paths |
| Migration misses edge cases | Medium | High | Comprehensive test coverage, phased rollout |
| Breaking change to error response format | Medium | High | Version API responses, maintain backward compat |
| Context propagation overhead in async | Low | Medium | Use efficient contextvar implementation |

---

## Definition of Done

- [ ] All stories completed and code reviewed
- [ ] All existing tests pass
- [ ] New tests added for error handling paths
- [ ] Performance benchmark shows <5% regression
- [ ] Documentation updated (API error schema, logging guide)
- [ ] Runbook created for incident response using new observability
- [ ] Staged rollout to staging environment verified

---

## Files

### Epic Structure

```
docs/epics/EPIC-018-OBSERVABILITY-REFACTOR/
├── README.md                           # This file
├── STORY-18.1-UNIFY-LOGGING.md         # Unify logging pipeline
├── STORY-18.2-CONTEXT-PROPAGATION.md   # Context propagation via contextvars
├── STORY-18.3-FIX-SILENT-ERRORS.md     # Eliminate silent exception swallowing
├── STORY-18.4-SECURE-RESPONSES.md      # Secure error responses (no traceback leak)
├── STORY-18.5-TAXONOMY.md              # Standardize exception taxonomy
├── STORY-18.6-DEPENDENCY-TRACING.md    # Add outbound dependency tracing
├── TECHNICAL-ANALYSIS.md               # Deep technical analysis
└── RISK-ASSESSMENT.md                  # Future risk analysis
```

---

## Related Documentation

- [EPIC-011: Error Handling and Logging](../EPIC-011-IMPLEMENT-ERROR-HANDLING-AND-LOGGING.md) - Foundation epic
- [AGENTS.md](../../../../AGENTS.md) - Project architecture context
- `src/solstein/api/exceptions.py` - Current exception handlers
- `src/solstein/utils/logging.py` - Current logging setup
- `src/solstein/api/middleware/logging.py` - Current middleware

---

*Last Updated: 2026-03-05*
*Version: 1.0*
*Status: Ready for Implementation*
