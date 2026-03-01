# EPIC-015: Dependency Resilience

| Field | Value |
|-------|-------|
| Priority | **P3** |
| Status | 🔴 Open |
| Stories | 1 |
| Created | 2026-02-28 |
| Depends On | None |

## Context

The platform depends on several external packages with non-trivial risk profiles: `yfinance` (scraping-based financial data, no official API), `edgartools` (SEC EDGAR parsing, subject to format changes), and `supabase` (managed Postgres — a vendor lock-in point). None have formal abstraction layers that would allow swapping them out without broad codebase changes.

Additionally, the circuit breaker pattern exists in `agents/resilience.py` but is not wired to any LLM provider calls. LLM provider failures result in uncontrolled error propagation rather than graceful degradation.

## Scope

| Story | Title | Severity |
|-------|-------|----------|
| [STORY-052](STORIES/STORY-052-dependency-audit-and-fallbacks.md) | Audit and Harden External Dependencies | MEDIUM |

## Definition of Done

- [ ] All high-risk external dependencies are abstracted behind interfaces
- [ ] Circuit breaker is wired to LLM provider calls
- [ ] Fallback behaviour is documented for each external dependency
