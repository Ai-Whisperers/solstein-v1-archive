# Implementation Backlog (Execution-Ready)

## P0 - Enforcement and Safety
1. Hard synthetic-data gate before report generation.
   - Files: report entrypoints in markdown/export pipeline.
   - Done when: reports fail fast for synthetic-heavy inputs with remediation message.
2. Claim-level citation verification gate.
   - Files: LLM exporter/report generation.
   - Done when: unsupported claims are rejected or flagged low-confidence.
3. Evidence-gated response policy.
   - Done when: low-evidence outputs cannot be emitted as final claims.

## P1 - Runtime Integration
4. Wire AI orchestrator into loader/enrichment runtime.
   - Files: `src/solstein/data/unified_loader.py`, enrichment pipeline.
   - Done when: orchestrator output is consumed in standard ingestion flow.
5. Persist research memory with versioning.
   - Add versioned entity model (`payload_version`, `refresh_version`, lock version).
   - Done when: prior runs are reused as context and updates are conflict-safe.
6. Queue idempotency ledger and retry policies.
   - Files: worker tasks/outbox/research scheduling.
   - Done when: duplicate tasks do not duplicate side effects.

## P2 - Feedback Loops and Calibration
7. Knowledge-gap detector and auto-enqueue.
   - Gap types: missing, stale, contradictory, insufficient_depth.
   - Done when: gaps trigger prioritized follow-up tasks.
8. Confidence calibration feedback loop.
   - Files: scoring + confidence integration paths.
   - Done when: prediction-vs-outcome updates confidence weights.
9. Contradiction-driven source credibility adjustments.
   - Done when: contradiction stage updates source trust and scheduling.

## P3 - Production Hardening
10. Observability and governance.
   - Add run lineage, stage durations, queue metrics, cost limits, circuit breakers.
   - Done when: SLO dashboards and failure controls are enforceable.

## Work Policy
- One backlog item at a time.
- No item is complete without tests + diagnostics + dossier update.
- Prefer smallest vertical slice that exercises full path.
