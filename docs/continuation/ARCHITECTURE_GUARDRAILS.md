# Architecture Guardrails

## Non-Negotiable Principles
- Source of truth: Postgres + event/outbox reliability spine.
- Provenance-first: no external claim without evidence linkage.
- Replay-safe async: idempotent operations across retries/replays.
- Append-only memory: new evidence appends; trusted state promotion is gated.
- Feedback loops cannot silently overwrite trusted facts.

## Required Contracts
- Stable IDs: `tenant_id`, `run_id`, `stage_id`, `artifact_id`, `event_id`.
- Versioned payload envelopes for stage artifacts.
- Deterministic idempotency keys: `company_id + research_type + normalized params`.

## Reliability Requirements
- Retry with exponential backoff + jitter + max retries.
- Dead-letter policy for non-recoverable failures.
- Stale lock recovery for in-flight tasks.
- Provider circuit breakers and tenant budget caps.

## Provenance and Confidence Requirements
- Claim-level evidence chain in outputs.
- Confidence decomposition: source credibility + agreement + freshness decay.
- Citation verification before final report emission.

## Anti-Patterns to Reject
- Latest-state-only memory with no versions.
- Retry logic without idempotency ledger.
- Confidence numbers without citations.
- Gap detection on hot user read path.
- Reporting that bypasses provenance checks.
