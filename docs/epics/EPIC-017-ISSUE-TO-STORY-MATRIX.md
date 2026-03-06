# EPIC-017 Issue-to-Story Coverage Matrix

> Purpose: guarantee full coverage of known non-API gaps before implementation.
> Scope: non-API stream only (Jonathan owns provider/API integrations).

---

## How to Use

- Each issue has an ID, severity, evidence location, and mapped stories from `EPIC-017-NON-API-MASTER-EXECUTION-PLAN.md`.
- If an issue has no mapped story, add one before implementation starts.
- Do not mark an issue done until acceptance criteria and tests for mapped stories pass.

---

## A. Scoring and Classification Integrity

1. **ISS-001 (High)** Hardcoded composite weights bypass config.
   - Evidence: `src/solstein/analytics/scoring.py`
   - Stories: B1, O5

2. **ISS-002 (High)** Duplicate classification logic in API and analytics.
   - Evidence: `src/solstein/api/routers/scoring.py`, `src/solstein/analytics/scoring.py`
   - Stories: C1, C2, N2

3. **ISS-003 (High)** Threshold drift across constants/modules.
   - Evidence: `src/solstein/analytics/constants.py`, presentation constants
   - Stories: C3, B1

4. **ISS-004 (Medium)** Zero-growth treated as missing in classifier path.
   - Evidence: `src/solstein/analytics/tier_classification.py`
   - Stories: C4

5. **ISS-005 (Medium)** Percent/decimal heuristic (`<=1`) causes unit ambiguity.
   - Evidence: `src/solstein/analytics/scorers/growth_momentum.py`
   - Stories: B2, B4

6. **ISS-006 (High)** Unit mismatch risk in financial scoring normalization.
   - Evidence: scoring and scorer modules
   - Stories: B2, B3

7. **ISS-007 (Medium)** Confidence weighting inconsistent for unmapped signals.
   - Evidence: scoring confidence application path
   - Stories: H3, B5

8. **ISS-008 (Medium)** Competitive position scorer over-relies on static heuristics.
   - Evidence: `src/solstein/analytics/scorers/competitive_position.py`
   - Stories: B5, H4

9. **ISS-009 (Medium)** Classification labels/colors hardwired in exporter.
   - Evidence: `src/solstein/exporters/excel_improved.py`
   - Stories: I3, C3

10. **ISS-010 (Medium)** Batch scoring endpoint disabled.
   - Evidence: `src/solstein/api/routers/scoring.py`
   - Stories: K1

---

## B. Domain Model and Contract Hygiene

11. **ISS-011 (Critical)** Duplicate fields in domain model (`margin_confidence`, `funding_raised`).
   - Evidence: `src/solstein/domain/models.py`
   - Stories: A1, A5

12. **ISS-012 (Critical)** Flat and nested financial representations coexist.
   - Evidence: `src/solstein/domain/models.py`
   - Stories: A2, M1

13. **ISS-013 (High)** Multiple confidence maps can drift.
   - Evidence: `src/solstein/domain/models.py`
   - Stories: A3, H3

14. **ISS-014 (Medium)** Domain model contains operational enrichment state.
   - Evidence: `src/solstein/domain/models.py`
   - Stories: A4

15. **ISS-015 (High)** Backward-compatibility break risk for model field changes.
   - Evidence: API/domain schema coupling
   - Stories: M1, M2, M3, M4, M5

16. **ISS-016 (High)** Missing explicit deprecation windows for renamed/removed fields.
   - Evidence: no explicit compatibility matrix in current epics
   - Stories: M1, M3

---

## C. Readiness, Authenticity, and Release Gates

17. **ISS-017 (High)** Readiness logic split across two modules with semantic mismatch.
   - Evidence: `src/solstein/data/report_readiness.py`, `src/solstein/data/gap_analyzer.py`
   - Stories: D1, D3

18. **ISS-018 (High)** Zero-value semantics inconsistent in gap analysis.
   - Evidence: gap analyzer required field checks
   - Stories: D2

19. **ISS-019 (High)** Confidence key mismatch can block valid reports.
   - Evidence: readiness confidence checks
   - Stories: D3, D4

20. **ISS-020 (Critical)** Synthetic authenticity gate not uniformly enforced in all outputs.
   - Evidence: output entrypoints vary in gating
   - Stories: L1, D5, I5, P3

21. **ISS-021 (High)** No unified machine-readable gate error contract.
   - Evidence: ValueError-only blocking in readiness paths
   - Stories: D4, P4

22. **ISS-022 (High)** Client-grade exports can fail partially but still be produced.
   - Evidence: exporter broad exception handling patterns
   - Stories: I2, I5

23. **ISS-023 (Medium)** No release sign-off process linked to gate outcomes.
   - Evidence: process/document gap
   - Stories: N5

24. **ISS-024 (High)** No automated rollback trigger on gate quality regressions.
   - Evidence: rollout policy gap
   - Stories: N4

---

## D. Loader/Research Pipeline Refactor Risk

25. **ISS-025 (Critical)** `unified_loader.py` is monolithic and cross-concern.
   - Evidence: `src/solstein/data/unified_loader.py`
   - Stories: E1, E2, E3

26. **ISS-026 (High)** Mutable defaults risk shared state.
   - Evidence: unified loader structures
   - Stories: E4

27. **ISS-027 (Medium)** Enrichment paths mostly sequential and throughput-limited.
   - Evidence: loader enrichment loops
   - Stories: E5, K3

28. **ISS-028 (Medium)** Repeated connector parsing logic increases bug surface.
   - Evidence: unified loader inline normalizers
   - Stories: E2

29. **ISS-029 (Medium)** Silent continue patterns hide systemic upstream regressions.
   - Evidence: loader/research broad catches with fallback
   - Stories: F5, J1, J3

30. **ISS-030 (Medium)** Aggregation tolerance settings are globally hardcoded.
   - Evidence: `src/solstein/research/aggregate.py`
   - Stories: H4

31. **ISS-031 (Medium)** Contradiction penalties not metric-sensitive.
   - Evidence: aggregate conflict handling
   - Stories: H4, H5

32. **ISS-032 (Medium)** Discovery legacy/hardcoded paths can bypass intended architecture.
   - Evidence: `src/solstein/research/discovery.py`
   - Stories: E1, J3

---

## E. Exception Taxonomy and Operational Failure Handling

33. **ISS-033 (Critical)** Broad exception usage pervasive in critical modules.
   - Evidence: repo scan (`except Exception` hotspots)
   - Stories: F1, F2, O5

34. **ISS-034 (High)** Worker task wrappers normalize heterogeneous failures.
   - Evidence: `src/solstein/worker_tasks.py`
   - Stories: F2, F3, F5

35. **ISS-035 (High)** Enrichment router error mapping not strict enough.
   - Evidence: `src/solstein/api/routers/enrichment.py`
   - Stories: F2, F3

36. **ISS-036 (Medium)** CLI catches reduce diagnostic granularity.
   - Evidence: CLI command exception wrappers
   - Stories: F1, F3

37. **ISS-037 (High)** Fallback behavior not tied to explicit degraded-state SLOs.
   - Evidence: multiple fallback pathways
   - Stories: J1, J2, J3, P1

38. **ISS-038 (Medium)** No runbook for synthetic gate violations/degraded mode incidents.
   - Evidence: operational docs gap
   - Stories: P2

---

## F. Testing, CI, and Environment Parity

39. **ISS-039 (High)** Coverage claims and real test posture need authoritative single source.
   - Evidence: docs mismatch vs repository test inventory
   - Stories: G1

40. **ISS-040 (High)** Missing robust golden tests for scoring/classification drift.
   - Evidence: drift risk from refactors
   - Stories: G2, B3

41. **ISS-041 (High)** Data quality suite breadth is limited relative to platform complexity.
   - Evidence: `tests/data_quality/` scope
   - Stories: G3, H1

42. **ISS-042 (Medium)** Export regression snapshots not comprehensive.
   - Evidence: exporter evolution risk
   - Stories: G4, I1

43. **ISS-043 (High)** Synthetic gate tests not comprehensive across all report paths.
   - Evidence: authenticity enforcement risk
   - Stories: G5, L1

44. **ISS-044 (Medium)** Mypy policy is not strict in critical modules.
   - Evidence: `pyproject.toml` mypy settings
   - Stories: G6

45. **ISS-045 (High)** Runtime/tooling version policy mismatch can create CI-local drift.
   - Evidence: `pyproject.toml`, CI workflows
   - Stories: O1

46. **ISS-046 (Medium)** Dev dependency parity (factory/dev extras) can break local test validity.
   - Evidence: environment setup drift risk
   - Stories: O2

47. **ISS-047 (Medium)** Dependency drift monitoring not formalized.
   - Evidence: process gap
   - Stories: O4

48. **ISS-048 (High)** Post-deploy verification is not mandatory for score integrity.
   - Evidence: release process gap
   - Stories: P5

---

## Coverage Check

- Total issues tracked: **48**
- Stories available in EPIC-017 (A..P): **75**
- Uncovered issues: **0**

If any new issue appears during implementation, add it here as `ISS-049+` and map it to a story before coding.
