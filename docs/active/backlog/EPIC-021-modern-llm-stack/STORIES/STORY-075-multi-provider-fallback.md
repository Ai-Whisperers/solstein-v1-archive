# STORY-075: Implement Multi-Provider Fallback and Circuit Breaking via SDK

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P1 |
| Severity | MEDIUM |
| Epic | [EPIC-021: Modern LLM Stack Migration](../README.md) |
| Created | 2026-02-28 |
| Supersedes | — |
| Dependencies | [STORY-071: Replace Custom LLM Client with Anthropic SDK](STORY-071-anthropic-sdk-migration.md) |

---

## The Audit Verdict

> The existing provider fallback chain (Ollama → Fireworks → OpenAI → Groq → Template Fallback, documented in AGENTS.md) is implemented in the custom `enhanced_client.py`. The circuit breaker in `src/solstein/agents/resilience.py` exists but is not wired to LLM call sites. After migrating to the Anthropic SDK (STORY-071), the fallback chain implemented in the custom client will no longer be the active code path. Provider fallback and circuit breaking must be reimplemented using SDK-compatible patterns.

## Problem Statement

STORY-071 replaces the custom LLM client with the Anthropic SDK. The custom client's provider fallback logic — which selects the next provider when the primary fails — lives inside the code being replaced. After migration, there is no fallback. A primary provider outage becomes a total LLM outage.

Additionally, the circuit breaker in `agents/resilience.py` was built but never connected to LLM calls. It exists as dead infrastructure. The SDK migration is the natural point to wire it properly — building the fallback chain with circuit breaking integrated from the start, rather than bolting it on later.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Availability** | Without fallback, a single provider outage makes the entire research pipeline unavailable — unacceptable for a platform serving PE/VC clients with time-sensitive intelligence needs |
| **Cost** | Without circuit breaking, a degraded provider continues receiving requests (and accumulating timeout costs) until it fully fails — the circuit breaker should short-circuit early |
| **Recovery** | Without the template fallback, total provider failure returns an error instead of a degraded-but-useful response — the template fallback is the difference between "service unavailable" and "limited service available" |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/llm/` | Modify | Provider selection and fallback logic using SDK clients for each provider |
| `src/solstein/agents/resilience.py` | Modify | Wire the existing `CircuitBreaker` to SDK-based LLM call sites |
| `src/solstein/config.py` | Modify | Configurable fallback chain order and circuit breaker thresholds |
| New `src/solstein/llm/fallback.py` | Add | Fallback chain orchestration — provider selection, circuit breaker integration, template fallback |

## Architectural Requirements

*What — never how. No code.*

- **REQ-1**: The fallback chain (primary provider → secondary → tertiary → template fallback) must be implemented using the official SDK of each provider — the Anthropic SDK for Claude, OpenAI-compatible clients for Groq/Fireworks, and the Ollama client for local models
- **REQ-2**: The `CircuitBreaker` from `agents/resilience.py` must be wired to all LLM provider call sites — a provider with an open circuit (exceeded failure threshold) must be skipped in the fallback chain without attempting a call
- **REQ-3**: Template fallback (returning a structured template response when all LLM providers fail) must be preserved as the last resort — it provides degraded-but-useful output instead of a hard failure
- **REQ-4**: The fallback chain order must be configurable via application settings (environment variables or config file) — not hardcoded in source code. The default order documented in AGENTS.md must be the initial configuration.
- **REQ-5**: Each provider attempt and fallback decision must be logged with the reason for failure (timeout, rate limit, authentication error, circuit breaker open) — enabling post-incident analysis of provider reliability

## Acceptance Criteria

- [ ] Disabling the primary provider causes automatic fallback to the secondary provider — the research job completes successfully
- [ ] A provider exceeding its circuit breaker failure threshold is skipped in the fallback chain — no request is attempted against it
- [ ] Template fallback is returned when all LLM providers fail — the response is structured and usable, not an error
- [ ] Fallback chain order is configurable via application settings without code changes
- [ ] Each fallback decision is logged with the failure reason

## Definition of Done

**Tests Required:**
- [ ] Integration test: primary provider unavailable → secondary provider used → research job completes
- [ ] Integration test: circuit breaker trips after configured failure count → provider skipped on next call
- [ ] Integration test: all providers fail → template response returned with correct structure
- [ ] Unit test: fallback chain order respects configuration
- [ ] Unit test: fallback decision logging includes failure reason

**Documentation Required:**
- [ ] Provider configuration guide: how to configure the fallback chain order
- [ ] Circuit breaker tuning guide: how to set failure thresholds and recovery periods
- [ ] Template fallback reference: what the template response contains and when it is used

**Code Review Gate:**
- [ ] No hardcoded provider order in source code
- [ ] Circuit breaker is actually wired (not just imported)
- [ ] Template fallback produces a structurally valid response (schema-compliant per STORY-072)
- [ ] Logging covers all fallback decisions

## Notes

The circuit breaker in `agents/resilience.py` is a real implementation that was never connected to call sites — it is not a stub. The wiring effort is connecting existing infrastructure, not building new infrastructure.

The template fallback is a pragmatic degradation strategy. When all LLM providers are down, returning a structured template with placeholder values and a `"generated_by": "template_fallback"` flag is more useful to downstream consumers than throwing an exception. Consumers can check the flag and display appropriate caveats.

This story is P1 severity MEDIUM because the fallback chain is critical for production availability, but its absence only manifests during provider outages — which are uncommon but high-impact when they occur.
