# EPIC-017 — Non-API Master Execution Plan

> Scope: everything outside Jonathan's API/provider integration stream.
> Goal: stabilize the platform while real data APIs are being integrated.
> Input sources: codebase deep analysis, existing epics, backlog docs, and Oracle review.

---

## Working Assumption

Until real-provider pipelines are fully landed and validated, we run in **synthetic-first development mode**.

- Synthetic data is allowed for internal dev/test loops.
- Synthetic-backed output must never be treated as production intelligence.
- Every report/export must carry data-authenticity metadata and gating checks.

---

## Program Structure

This master plan is broken into **12 epics** and **55 stories**.

- EPIC-017A: Domain Contract and Model Hygiene
- EPIC-017B: Scoring Engine Integrity
- EPIC-017C: Classification Unification
- EPIC-017D: Readiness and Release Gates
- EPIC-017E: Unified Loader Refactor
- EPIC-017F: Exception and Failure Taxonomy
- EPIC-017G: Test Architecture and Coverage Hardening
- EPIC-017H: Data Quality, Provenance, and Confidence
- EPIC-017I: Export Reliability and Output Integrity
- EPIC-017J: Observability, Governance, and Degradation Control
- EPIC-017K: Performance and Throughput
- EPIC-017L: Synthetic-Only Interim Safety Controls

---

## EPIC-017A — Domain Contract and Model Hygiene

**Problem:** Domain model has duplicated fields, mixed representations, and runtime mutation burden that creates drift.

### Stories

1. **A1 — Remove duplicate financial fields**
   - Files: `src/solstein/domain/models.py`
   - Issue: duplicated `margin_confidence` and `funding_raised`.
   - Acceptance: one canonical field each, migration notes, tests green.

2. **A2 — Define canonical financial representation**
   - Files: `src/solstein/domain/models.py`, mapper modules.
   - Issue: flat + nested financial fields in same model.
   - Acceptance: single canonical structure with explicit adapters.

3. **A3 — Normalize confidence maps**
   - Files: `src/solstein/domain/models.py`
   - Issue: duplicated confidence structures (`confidence_scores` and signal variants).
   - Acceptance: one confidence contract and deterministic sync behavior.

4. **A4 — Move operational state out of domain entity**
   - Files: domain + pipeline-state modules.
   - Issue: enrichment operational errors stored in domain model.
   - Acceptance: operational metadata moved to pipeline state object.

5. **A5 — Add schema contract tests**
   - Files: `tests/unit/domain/`
   - Acceptance: tests assert serialization compatibility and no duplicate aliases.

---

## EPIC-017B — Scoring Engine Integrity

**Problem:** scoring paths are inconsistent and partially bypass configuration.

### Stories

6. **B1 — Eliminate hardcoded composite weights**
   - Files: `src/solstein/analytics/scoring.py`, `src/solstein/core/scoring_config.py`
   - Issue: hardcoded `0.4/0.3/0.3`.
   - Acceptance: all weights loaded through config, validated at startup.

7. **B2 — Enforce units contract (millions vs absolute)**
   - Files: scorers + ingestion normalizers.
   - Acceptance: unit schema documented and validated with tests.

8. **B3 — Add scoring-calibration fixtures**
   - Files: `tests/unit/analytics/`
   - Acceptance: known-company fixtures with expected score windows.

9. **B4 — Replace heuristic percentage inference**
   - Files: `growth_momentum.py`
   - Issue: `<=1` inferred as decimal percent.
   - Acceptance: no implicit unit guessing in scorer path.

10. **B5 — Add score explainability contract**
    - Files: scorers + API response schemas.
    - Acceptance: each component score includes rationale + source confidence.

---

## EPIC-017C — Classification Unification

**Problem:** classification logic is fragmented across analytics, API router, and presentation constants.

### Stories

11. **C1 — Create single classification service**
    - Files: new `analytics/classification_service.py` + integrations.
    - Acceptance: all paths use one service.

12. **C2 — Remove router-side ad-hoc classification**
    - Files: `src/solstein/api/routers/scoring.py`
    - Acceptance: router delegates to service only.

13. **C3 — Align tier/class labels and thresholds**
    - Files: `analytics/constants.py`, presentation constants.
    - Acceptance: one threshold source of truth.

14. **C4 — Fix edge-case handling for zero growth**
    - Files: `tier_classification.py`
    - Acceptance: `0` treated as valid value, not missing.

15. **C5 — Add classification regression suite**
    - Files: `tests/unit/analytics/`
    - Acceptance: deterministic class outputs for canonical fixtures.

---

## EPIC-017D — Readiness and Release Gates

**Problem:** readiness logic split across modules with inconsistent semantics.

### Stories

16. **D1 — Merge readiness engines**
    - Files: `data/report_readiness.py`, `data/gap_analyzer.py`
    - Acceptance: one gate module with shared policy.

17. **D2 — Fix zero-value semantics by metric type**
    - Acceptance: `0` valid where business-valid; invalid where truly missing.

18. **D3 — Unify confidence threshold policy**
    - Acceptance: one confidence policy used by CLI/API/export paths.

19. **D4 — Add machine-readable gate report**
    - Acceptance: structured object for blocked fields + reasons.

20. **D5 — Enforce gate in all export/report entry points**
    - Files: exporters + API routers.
    - Acceptance: no client-ready report bypasses gate.

---

## EPIC-017E — Unified Loader Refactor

**Problem:** `unified_loader.py` is a high-risk orchestration monolith.

### Stories

21. **E1 — Extract orchestration layer**
    - New module for pipeline orchestration responsibilities.

22. **E2 — Extract normalization and parsing utilities**
    - Remove repeated inline parser blocks.

23. **E3 — Extract merge/conflict resolver adapter**
    - Centralize conflict handling and error categories.

24. **E4 — Replace mutable defaults with safe factories**
    - Eliminate shared-state risk.

25. **E5 — Add bounded concurrency for enrichment**
    - Move from mostly sequential loops to bounded async workers.

26. **E6 — Add loader-level performance benchmarks**
    - Baseline and compare before/after throughput.

---

## EPIC-017F — Exception and Failure Taxonomy

**Problem:** broad exception usage (`except Exception`) is pervasive and hides failure classes.

### Stories

27. **F1 — Define global exception taxonomy**
    - Types: retryable upstream, validation, contract, persistence, auth, timeout.

28. **F2 — Refactor top 20 hotspot modules**
    - Priority: `worker_tasks.py`, `agents/github_agent.py`, `api/routers/enrichment.py`, `data/unified_loader.py`.

29. **F3 — Add standardized error envelope**
    - Uniform structure for API and worker logs.

30. **F4 — Add policy lint check for broad catches**
    - CI fails on new untyped broad catches in critical modules.

31. **F5 — Add degraded-mode propagation**
    - Fail-open paths must emit explicit degraded-state signals.

---

## EPIC-017G — Test Architecture and Coverage Hardening

**Problem:** coverage quality and policy consistency are insufficient for confidence.

### Stories

32. **G1 — Build coverage truth dashboard**
    - Resolve mismatch between docs claims and current test inventory.

33. **G2 — Add scoring/classification golden tests**
    - Protect against calibration drift.

34. **G3 — Expand data-quality suite breadth**
    - Add field-level and pipeline-level DQ tests.

35. **G4 — Add exporter regression snapshots**
    - Validate schema/visual consistency for outputs.

36. **G5 — Add synthetic-mode gate tests**
    - Ensure no production-ready output bypasses authenticity policy.

37. **G6 — Tighten mypy profile in staged levels**
    - Ratchet strictness for critical modules first.

---

## EPIC-017H — Data Quality, Provenance, and Confidence

**Problem:** provenance and confidence are present but unevenly enforced/populated.

### Stories

38. **H1 — Make provenance required for key PE fields**
    - revenue, growth, margin, employees, valuation, funding.

39. **H2 — Implement provenance schema validation**
    - Allow internal URNs + external URLs with explicit schema.

40. **H3 — Add confidence determinism rules**
    - No implicit fallback confidence inflation.

41. **H4 — Add contradiction sensitivity by metric**
    - Replace global tolerances with per-metric tolerance profiles.

42. **H5 — Add calibration monitor for confidence vs observed accuracy**
    - Track confidence reliability over validation sets.

---

## EPIC-017I — Export Reliability and Output Integrity

**Problem:** exporter is robust but monolithic, with partial-failure behavior that can hide quality issues.

### Stories

43. **I1 — Split `excel_improved.py` into sheet builders**
    - Improve maintainability and testability.

44. **I2 — Add fail-fast policy mode for critical export failures**
    - No silent partial success for client-grade reports.

45. **I3 — Externalize classification color map and labels**
    - Remove hardwired business semantics.

46. **I4 — Optimize width/style pass for large datasets**
    - Reduce CPU cost for high-volume exports.

47. **I5 — Add export readiness compliance block**
    - Export blocked if readiness or authenticity requirements fail.

---

## EPIC-017J — Observability, Governance, and Degradation Control

**Problem:** fallback-heavy architecture needs explicit governance so degraded behavior is visible.

### Stories

48. **J1 — Add degradation budget per run**
    - Score run quality and abort thresholds.

49. **J2 — Add stage-level SLO metrics**
    - timing, fail rate, fallback ratio, confidence distribution.

50. **J3 — Add fallback-mode telemetry tags**
    - every fallback path emits standardized metric.

51. **J4 — Add readiness/audit events to outbox**
    - track gate decisions and reasons for governance.

---

## EPIC-017K — Performance and Throughput

**Problem:** throughput and scaling paths are constrained in scoring and loader/export flows.

### Stories

52. **K1 — Restore batch scoring workflow (post-Temporal replacement)**
    - Replace `501` disabled path with queue-driven batch execution.

53. **K2 — Move scoring stats aggregation to DB-level queries**
    - avoid memory-heavy full scans.

54. **K3 — Add benchmark suite for loader/scoring/export**
    - track p50/p95 latency and throughput regressions.

---

## EPIC-017L — Synthetic-Only Interim Safety Controls

**Problem:** synthetic data is necessary short-term but dangerous if not constrained.

### Stories

55. **L1 — Enforce authenticity labeling and hard no-ship gate**
    - Every report must include authenticity metadata; client output blocked if synthetic ratio exceeds policy.

---

## Dependency Graph (Critical Path)

1. **EPIC-017A** (model contract) -> 2. **EPIC-017B/C** (scoring/classification) -> 3. **EPIC-017D/L** (gates/authenticity) -> 4. **EPIC-017G/H** (tests/provenance/confidence) -> 5. **EPIC-017I/J/K** (export/ops/perf hardening)

If you skip A, B/C fixes won’t be stable. If you skip D/L, synthetic-era outputs remain risky.

---

## Suggested Execution Waves

### Wave 1 (2 weeks)
- A1-A5, B1-B2, C1-C3, D1-D3, L1

### Wave 2 (2 weeks)
- E1-E4, F1-F4, G1-G3, H1-H3

### Wave 3 (2 weeks)
- E5-E6, G4-G6, H4-H5, I1-I3, J1-J4, K1-K3

---

## Definition of Done (Program-Level)

- No duplicate domain financial fields.
- One classification service used everywhere.
- No hardcoded scoring composite weights in runtime logic.
- One readiness gate and one authenticity gate enforced across API/CLI/export.
- Broad catches reduced in hotspot modules with typed handling.
- Golden scoring + classification + export regression tests in CI.
- Synthetic output cannot be emitted as client-ready artifact.

---

## How to Use This Plan Daily

- Pick one story, create branch, implement, add tests, run diagnostics.
- Update story status in epic tracker.
- Do not start dependent story before prerequisite is closed.
- Keep API-provider tasks out of this stream (Jonathan owns those).

---

## Completeness Audit Addendum (Deep Pre-Implementation Controls)

This addendum closes gaps that typically appear during implementation (not discovery), especially around compatibility, migrations, rollout safety, and CI parity.

### EPIC-017M — Compatibility and Migration Safety

**Problem:** Refactors can silently break API contracts, serializers, and persisted data assumptions.

#### Stories

56. **M1 — Define backward-compatibility contract for `Company` and `FinancialMetric`**
    - Files: `src/solstein/domain/models.py`, API schemas.
    - Acceptance: explicit compatibility matrix (old field -> new field), deprecation schedule documented.

57. **M2 — Add model migration playbook and dry-run validator**
    - Acceptance: migration dry-run script validates serialization/parsing for legacy payload fixtures.

58. **M3 — Create adapter-layer shims for removed/renamed fields**
    - Acceptance: old payloads still parse during transition window; warnings emitted.

59. **M4 — Add contract tests for persisted JSON and API responses**
    - Files: `tests/integration/` + snapshot fixtures.
    - Acceptance: no breaking changes without explicit version bump.

60. **M5 — Add rollback procedure for model-contract deploys**
    - Acceptance: one-command rollback documented and tested in staging.

### EPIC-017N — Rollout and Feature-Flag Safety

**Problem:** Correct code can still fail in production if introduced all-at-once without guardrails.

#### Stories

61. **N1 — Add feature flags for new classifier, readiness gate, and loader path**
    - Acceptance: flags allow dual-run and safe cutover.

62. **N2 — Implement shadow-mode scoring/classification comparison**
    - Acceptance: old and new outputs compared in logs/metrics before switch.

63. **N3 — Add canary rollout policy for export/readiness changes**
    - Acceptance: staged rollout percentages and abort thresholds defined.

64. **N4 — Add automatic rollback triggers on quality regressions**
    - Acceptance: if gate-fail ratio or confidence drift exceeds threshold, rollback fires.

65. **N5 — Add release checklist with mandatory sign-offs**
    - Acceptance: engineering + product + data quality checklist completed before promotion.

### EPIC-017O — CI/CD, Environment Parity, and Dependency Risk

**Problem:** Local/CI mismatch and dependency drift create false confidence and flaky rollouts.

#### Stories

66. **O1 — Align runtime/tooling Python versions and CI matrix**
    - Files: `pyproject.toml`, CI workflows.
    - Acceptance: tested matrix for supported Python versions; policy documented.

67. **O2 — Enforce dev dependency parity for tests**
    - Acceptance: tests requiring factory/dev tooling fail fast with clear setup diagnostics.

68. **O3 — Add deterministic test modes for synthetic and mixed data**
    - Acceptance: separate test profiles with fixed seeds and explicit data-authenticity assertions.

69. **O4 — Add dependency drift monitor and upgrade cadence**
    - Acceptance: scheduled dependency checks and risk labels for breaking upgrades.

70. **O5 — Add CI quality gates for broad catches in critical modules**
    - Acceptance: no new broad catches in hotspots without explicit exception justification.

### EPIC-017P — Operational Pre-Mortem and Incident Readiness

**Problem:** Most failures happen at integration boundaries under load, not in isolated unit tests.

#### Stories

71. **P1 — Build failure-injection scenarios for fallback paths**
    - Acceptance: chaos tests for provider failure, cache failure, and partial data failure.

72. **P2 — Add incident runbook for degraded mode and synthetic gate violations**
    - Acceptance: runbook includes detection, mitigation, rollback, and communication templates.

73. **P3 — Define SLOs for data authenticity and readiness compliance**
    - Acceptance: SLOs instrumented and visible in dashboards.

74. **P4 — Add audit trail completeness checks for report generation**
    - Acceptance: every client-ready report has traceable readiness and provenance evidence.

75. **P5 — Add post-deploy verification suite (smoke + integrity + scoring drift)**
    - Acceptance: deployment is incomplete unless verification suite passes.

---

## Pre-Mortem (Top 15 Likely Implementation Failures)

1. **Model field removals break hidden serializers** -> Mitigation: M1, M2, M4.
2. **Scoring changes pass tests but shift business distribution unexpectedly** -> Mitigation: B3, N2, P5.
3. **Router/classifier mismatch reappears via hotfixes** -> Mitigation: C1, C2, O5.
4. **Readiness gate blocks too aggressively due confidence key mismatch** -> Mitigation: D1-D4, H3.
5. **Valid zero values marked missing** -> Mitigation: D2 + targeted fixtures.
6. **Loader refactor introduces throughput regression** -> Mitigation: E6, K3, canary rollout.
7. **Fallbacks mask systematic upstream failures** -> Mitigation: F5, J1-J3.
8. **Synthetic data leaks into client exports** -> Mitigation: L1, I5, P3.
9. **Confidence inflation from missing signal maps** -> Mitigation: H3 + regression tests.
10. **Export partial success accepted as complete** -> Mitigation: I2 + release checklist.
11. **CI green but local/staging differs** -> Mitigation: O1-O3.
12. **Dependency update silently changes behavior** -> Mitigation: O4.
13. **Rollback path undocumented and unused** -> Mitigation: M5, N4.
14. **Outbox/audit events missing for governance** -> Mitigation: J4, P4.
15. **Batch scoring remains disabled too long** -> Mitigation: K1 + explicit milestone gate.

---

## Traceability Matrix (Issue Class -> Story Coverage)

- **Model hygiene and duplication:** A1-A5, M1-M4
- **Scoring consistency and units:** B1-B5, C3, N2
- **Classification divergence:** C1-C5, O5
- **Readiness inconsistencies:** D1-D5, H1-H3, I5
- **Loader monolith and refactor risk:** E1-E6, K3, N1
- **Exception granularity and silent degradation:** F1-F5, J1-J3, P1
- **Testing confidence and anti-regression:** G1-G6, O2-O3, P5
- **Provenance and confidence realism:** H1-H5, P4
- **Export integrity:** I1-I5, N3
- **Operational governance:** J1-J4, P2-P4
- **Performance and scale:** K1-K3, N3-N4
- **Synthetic-only safety:** L1, O3, P3

---

## Sequencing Update (Safer Order)

- **Wave 0 (Prep, 3-5 days):** M1, O1, O2, N1
- **Wave 1 (Core Correctness):** A1-A5, B1-B2, C1-C3, D1-D3, L1
- **Wave 2 (Stability):** E1-E4, F1-F4, G1-G3, H1-H3, M2-M4
- **Wave 3 (Production Safety):** E5-E6, G4-G6, H4-H5, I1-I5, J1-J4, K1-K3, N2-N5, P1-P5

This sequencing reduces rollback risk by putting compatibility and environment parity before deep structural changes.
