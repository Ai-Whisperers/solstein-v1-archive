# STORY-048: Wire LLM Cost Tracking into Every LLM Call

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P2 |
| Severity | HIGH |
| Epic | [EPIC-014: Observability & Telemetry](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-016: UsageTracker Decision](../../EPIC-005-dead-code-removal/STORIES/STORY-016.md) |

---

## The Audit Verdict
> `llm/enhanced_client.py` lines 591–661 define a `UsageTracker` class with methods for recording prompt tokens, completion tokens, cost estimates per provider, and cumulative usage. It is never imported, never instantiated, and never called. LLM costs are entirely invisible to the business.

## Problem Statement
The platform makes LLM API calls for every research job. The cost of these calls is unknown. There is no mechanism to attribute costs to specific clients, jobs, or companies. Budget overruns are invisible until the invoice arrives. Someone wrote a perfectly good cost tracking implementation and it sits unused — 70 lines of dead code that solve an active problem.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Business** | No cost visibility for LLM API spend — the business cannot forecast or control its largest variable cost |
| **Operations** | Cannot identify expensive queries or optimise provider selection — an expensive model is used where a cheap one would suffice |
| **Client Attribution** | Cannot charge clients proportionally to their platform usage — all clients subsidise heavy users |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/llm/enhanced_client.py` | Modify | Lines 591–661: wire UsageTracker into all LLM call paths |
| All LLM call sites | Modify | Ensure usage tracking is invoked on every call |
| `src/solstein/core/monitoring.py` | Modify | Expose aggregated usage metrics |

## Architectural Requirements
*What the system must satisfy. No implementation instructions. No code. Only what — never how.*

- **REQ-1**: Every LLM API call must record: provider, model, prompt token count, completion token count, estimated cost in USD, and request timestamp
- **REQ-2**: Usage data must be persisted or emitted to a durable store (database or structured log) — in-memory tracking alone is not sufficient across process restarts
- **REQ-3**: Usage must be attributable to the originating request (correlation ID) and company ID where available
- **REQ-4**: A usage summary must be available via the `/health` or a dedicated `/metrics` endpoint

## Acceptance Criteria
- [ ] Every LLM call produces a usage record with provider, model, token counts, and cost estimate
- [ ] Usage records include the correlation ID of the originating request
- [ ] Aggregated usage is queryable (log query or database query)
- [ ] The UsageTracker class is imported and instantiated — no longer dead code

## Definition of Done

**Tests Required:**
- [ ] Unit test: mock LLM call produces a usage record with all required fields
- [ ] Integration test: usage records are persisted after a real research job completes

**Documentation Required:**
- [ ] LLM cost tracking architecture documented
- [ ] Per-provider cost rates documented or referenced

**Code Review Gate:**
- [ ] Reviewer confirms every LLM call path invokes usage tracking
- [ ] Reviewer confirms usage data is persisted, not just held in memory

## Notes
This story depends on STORY-016 (which decides whether to revive the existing UsageTracker or replace it). If the decision is to revive, this story wires it in. If the decision is to replace, this story wires the replacement in. Either way, the requirements here define what the wired solution must do. The correlation ID requirement creates a dependency on STORY-049, but usage tracking can start without correlation IDs and add them later.
