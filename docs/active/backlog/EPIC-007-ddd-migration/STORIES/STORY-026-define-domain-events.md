# STORY-026: Define Domain Events for the Research Pipeline

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P1 |
| Severity | MEDIUM |
| Epic | [EPIC-007: Domain-Driven Design Migration](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-024](STORY-024-migrate-company-rich-domain.md) |

---

## The Audit Verdict

> The research pipeline writes directly to the database and outbox without any domain event mechanism. Side effects (cache invalidation, notification, audit log) are interleaved with core writes rather than being triggered by domain events. This couples every side effect implementation to the research pipeline directly.

## Problem Statement

Without domain events, the research pipeline must know about every side effect it triggers. Today, the pipeline directly calls cache invalidation, writes audit logs, and performs other side effects inline with its core data writes. This means:

1. Adding a new side effect (e.g., sending a Slack notification when a company upgrades tier) requires modifying the research pipeline code itself
2. Testing the pipeline requires accounting for all side effects — you cannot test the core pipeline logic in isolation
3. Side effect failures can break the core pipeline if error handling is not perfect at each call site
4. The pipeline's complexity grows linearly with the number of side effects

Domain events invert this dependency: the pipeline emits events, and independent handlers react to those events. Adding a new handler does not require touching the pipeline.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Extensibility** | Adding side effects requires modifying core pipeline code |
| **Testability** | Pipeline tests must account for all side effects to avoid false failures |
| **Coupling** | Pipeline directly depends on cache, notification, and audit implementations |
| **Reliability** | Side effect failures can cascade to core pipeline if not individually handled |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/domain/events.py` | Add | New module defining domain event classes |
| `src/solstein/domain/event_bus.py` | Add | Simple event bus (publish/subscribe) for domain events |
| `src/solstein/infrastructure/research_dual_write.py` | Modify | Emit domain events instead of directly calling side effects |
| Event handler modules (new) | Add | Independent handlers for cache invalidation, audit logging, etc. |

## Architectural Requirements

- **REQ-1**: Domain events must be defined for key state transitions: `ResearchCompleted` (research pipeline finishes for a company), `CompanyTierChanged` (a company's classification tier changes), `EnrichmentFailed` (an enrichment attempt fails)
- **REQ-2**: Events must be immutable value objects containing all data needed by handlers — handlers must not need to query additional state to process an event
- **REQ-3**: The research pipeline must emit domain events rather than directly calling side-effect code — the pipeline should not know or care which handlers are subscribed
- **REQ-4**: Event handlers must be independently testable without the pipeline — each handler receives an event and produces its effect in isolation

## Acceptance Criteria

- [ ] `ResearchCompleted` event is emitted when research finishes for a company
- [ ] `CompanyTierChanged` event is emitted when a company's tier changes
- [ ] `EnrichmentFailed` event is emitted when an enrichment attempt fails
- [ ] Adding a new event handler does not require modifying the research pipeline
- [ ] Each event handler can be unit-tested by constructing an event and calling the handler directly
- [ ] The event bus supports synchronous handler execution (async can be added later)

## Definition of Done

**Tests Required:**
- [ ] Unit test: research completion emits `ResearchCompleted` event with correct company data
- [ ] Unit test: tier change emits `CompanyTierChanged` event with old and new tier
- [ ] Unit test: event handler processes event in isolation without pipeline context
- [ ] Test: subscribing a new handler to an event does not require modifying the event emitter

**Documentation Required:**
- [ ] Docstrings on each event class documenting its fields and when it is emitted
- [ ] Docstring on the event bus explaining the subscription and publishing mechanism

**Code Review Gate:**
- [ ] Reviewer confirms the pipeline does not directly call side-effect code
- [ ] Reviewer confirms events are immutable and self-contained
- [ ] Reviewer confirms handlers are independently testable

## Notes

The initial event bus should be simple — a synchronous in-process publish/subscribe mechanism. Do not introduce Kafka, RabbitMQ, or any external message broker at this stage. The goal is to decouple the pipeline from its side effects, not to build a distributed event system.

If the system later needs asynchronous or distributed events, the event bus interface can be swapped without changing the event definitions or handlers. This is the point of the abstraction.

This story depends on STORY-024 because the events reference domain concepts (tiers, scores) that are defined by the rich domain model.
