# STORY-052: Audit and Harden High-Risk External Dependencies

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P3 |
| Severity | MEDIUM |
| Epic | [EPIC-015: Dependency Resilience](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-017: Resolve Stub Agents](../../EPIC-005-dead-code-removal/STORIES/STORY-017.md) |

---

## The Audit Verdict
> `yfinance`, `edgartools`, and `supabase` are used directly without abstraction layers. `agents/resilience.py` defines a `CircuitBreaker` class that is never wired to any LLM client call. An OpenAI outage results in cascading uncontrolled failures rather than graceful degradation to a fallback provider.

## Problem Statement
High-risk scraping-based dependencies and unabstracted vendor packages create brittle coupling. The circuit breaker implementation is feature-complete but disconnected from the components that need it. When `yfinance` breaks (and it does — it scrapes Yahoo Finance, which changes its HTML without notice), the platform has no abstraction layer to swap in an alternative data source. When an LLM provider goes down, failures cascade through the entire request rather than triggering a controlled fallback.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Reliability** | Scraping-based dependencies (`yfinance`) break without notice when the scraped site changes format — platform degrades with no fallback |
| **Vendor Risk** | `supabase` coupling makes storage backend changes expensive — a vendor price increase or deprecation requires broad codebase changes |
| **Resilience** | LLM provider failures cascade rather than trigger circuit breaker fallback — the circuit breaker exists but is not wired to anything |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| All files importing `yfinance` directly | Modify | Wrap behind a financial data adapter interface |
| All files importing `edgartools` directly | Modify | Wrap behind an SEC data adapter interface |
| All files importing `supabase` directly | Modify | Wrap behind a storage adapter interface |
| `src/solstein/agents/resilience.py` | Modify | Wire CircuitBreaker to LLM client calls |
| `src/solstein/llm/enhanced_client.py` | Modify | Integrate circuit breaker for provider failover |

## Architectural Requirements
*What the system must satisfy. No implementation instructions. No code. Only what — never how.*

- **REQ-1**: Each high-risk external dependency must be wrapped in an abstraction layer (adapter or facade) that defines a stable interface — application code must depend on the interface, not the implementation
- **REQ-2**: The `CircuitBreaker` from `agents/resilience.py` must be wired to all LLM provider call sites
- **REQ-3**: Each external dependency must have documented fallback behaviour: what happens when it is unavailable, what degradation the user sees, and what the recovery procedure is
- **REQ-4**: A dependency health check must be added to the startup validation (see STORY-008) for each critical external dependency

## Acceptance Criteria
- [ ] `yfinance`, `edgartools`, and `supabase` are not imported directly outside their respective adapter modules
- [ ] The circuit breaker is invoked on every LLM API call
- [ ] A dependency failure audit document exists listing fallback behaviour for each external dependency
- [ ] The circuit breaker trips after a configured failure threshold and recovers after a configured timeout

## Definition of Done

**Tests Required:**
- [ ] Unit test: circuit breaker trips after configured failure threshold
- [ ] Integration test: LLM provider failure triggers circuit breaker and initiates fallback to next provider
- [ ] Unit test: adapter interface can be satisfied by a test double (confirms abstraction is real, not leaky)

**Documentation Required:**
- [ ] Dependency risk register listing each external dependency, its risk profile, and its fallback behaviour

**Code Review Gate:**
- [ ] Reviewer confirms no direct imports of high-risk dependencies outside adapter modules
- [ ] Reviewer confirms circuit breaker is invoked on every LLM call path

## Notes
This story depends on STORY-017 (stub agent resolution) because the adapter interfaces should cover all data sources including the ones that are currently stubbed. The circuit breaker wiring for LLM providers should leverage the existing health checking in `llm/health_checker.py` — the health checker detects failures, the circuit breaker prevents cascading. These are complementary patterns, not redundant ones.
