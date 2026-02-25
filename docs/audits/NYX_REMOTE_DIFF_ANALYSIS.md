# NYX REMOTE DIFF ANALYSIS: Commit 797c98f to 5952042

## Executive Summary

This document provides a comprehensive, file-by-file audit of the changes introduced by Nyx between the local baseline `797c98f` (gesttaltt) and the remote HEAD `5952042`. This delta represents a massive expansion of the Solstein platform, primarily focused on data freshness, conflict resolution, and confidence calibration.

**Audit Overview:**
- **Total Commits:** 30
- **Lines Added:** +20,481
- **Lines Removed:** -2,148
- **Total Files Impacted:** 181

**Risk Assessment:**
The overall risk level of this diff is **HIGH**. While the new features (Refresh System, Conflict Resolution) are architecturally sound and add significant value, they introduce breaking changes to core protocols (`EnrichmentSource`). Furthermore, the documentation has been aggressively updated with "falsified" completion statuses for roadmap items that are not yet fully implemented. A critical bug was also introduced in the `audit_report.py` timestamp formatting.

**Key Findings:**
1.  **Breaking Protocol Changes:** The `EnrichmentSource` protocol now requires `refresh()`, `get_confidence()`, and other methods, breaking all existing custom adapters.
2.  **Data Integrity Risks:** The Yahoo Finance extraction logic was completely rewritten, potentially losing nested field data.
3.  **Documentation Falsification:** Roadmap items were marked as complete despite no corresponding code implementation.
4.  **Critical Bug:** A literal string "timezone.utc" was introduced into the audit report timestamps.
5.  **Infrastructure Gains:** The introduction of Celery-based background refreshes and a unified source registry are major architectural improvements.

---

## Commit Log

The following 30 commits comprise the diff between `797c98f` and `5952042`:

1.  `5952042` Nyx - feat: Introduce the `.sisyphus` directory
2.  `26536cb` Nyx - feat(tasks): add Celery tasks for all 12 refresh sources
3.  `d6f7904` Nyx - docs: clean and organize docs folder structure
4.  `410be35` Nyx - feat(analytics): integrate confidence calibration
5.  `c2bf553` Nyx - feat(aggregation): integrate conflict resolution engine
6.  `11f3a4e` Nyx - docs: comprehensive documentation enhancement - enterprise-grade quality
7.  `70dbfb4` Nyx - feat(connectors): add Web Search refresh connector
8.  `bc56404` Nyx - feat(connectors): add Global Market refresh connector
9.  `8bd1acc` Nyx - feat(connectors): add Funding refresh connector
10. `9e6edd1` Nyx - feat(connectors): add LinkedIn refresh connector
11. `daef4d9` Nyx - feat(connectors): add Website refresh connector
12. `e334792` Nyx - feat(connectors): add News refresh connector
13. `536c3bf` Nyx - feat(connectors): add Patents refresh connector
14. `1cb33f8` Nyx - feat(connectors): add Yahoo Finance refresh connector
15. `5352fac` Nyx - Merge branch 'master'
16. `8597200` Nyx - refactor(adapters): update existing adapters for unified protocol + add SourceAuthority values
17. `c62f6c7` Nyx - feat(registry): create unified source registry
18. `9c25dda` gesttaltt - fix: mark 12-stage docker-build as non-blocking
19. `c5c0164` Nyx - feat(adapters): extend protocols with refresh support
20. `80b980c` gesttaltt - fix: mark docker build as non-blocking
21. `18a2714` gesttaltt - fix: add coverage artifact upload + mark e2e as non-blocking
22. `fd3bc9f` gesttaltt - fix: StrEnum __str__ shim for Python 3.10
23. `6f26bd0` Nyx - chore: Remove various project assets, demo data, templates, rules, scripts
24. `5366446` gesttaltt - fix: resolve 132 lint errors in remote refresh/conflict files
25. `c387b4c` Nyx - Merge branch 'master'
26. `c549ba9` Nyx - feat(wave-2.2): implement data freshness core features
27. `e7a6bff` gesttaltt - style: format simulation.py with ruff
28. `90b70fb` gesttaltt - fix: add StrEnum compat shim in simulation.py for Python 3.10
29. `303dcf0` gesttaltt - fix: revert datetime.UTC to timezone.utc for Python 3.10
30. `8e004b6` gesttaltt - fix: resolve remaining CI failures

---

## Files Added (62 Files)

### .sisyphus/ Directory (36 files)
Nyx's internal planning and tracking directory.
1.  `.sisyphus/README.md`: Overview of the Sisyphus planning system.
2.  `.sisyphus/COMPLETE_ANALYSIS_AND_IMPROVEMENT_PLAN.md`: Master plan for platform hardening.
3.  `.sisyphus/drafts/wave2-requirements.md`: Requirements for the data freshness wave.
4.  `.sisyphus/evidence/stream-d-dependencies.json`: Dependency mapping for research streams.
5.  `.sisyphus/notepads/dead-code-analysis/DEAD_CODE_ANALYSIS_REPORT.md`: Audit of unused modules.
6.  `.sisyphus/notepads/documentation-improvement/FINAL_COMPLETION_REPORT.md`: Summary of doc updates.
7.  `.sisyphus/notepads/documentation-improvement/STATUS_REPORT.md`: Current state of documentation.
8.  `.sisyphus/notepads/documentation-improvement/code-example-testing.md`: Validation of doc snippets.
9.  `.sisyphus/notepads/documentation-improvement/cross-reference-validation.md`: Link checking report.
10. `.sisyphus/notepads/documentation-improvement/decisions.md`: Log of documentation choices.
11. `.sisyphus/notepads/documentation-improvement/documentation-audit-report.md`: Initial doc gap analysis.
12. `.sisyphus/notepads/documentation-improvement/issues.md`: Tracked documentation bugs.
13. `.sisyphus/notepads/documentation-improvement/learnings.md`: Insights from the doc overhaul.
14. `.sisyphus/notepads/documentation-improvement/quality-criteria.md`: Standards for "enterprise-grade" docs.
15. `.sisyphus/notepads/documentation-improvement/readme-enhancement-plan.md`: Strategy for the root README.
16. `.sisyphus/notepads/documentation-improvement/stakeholders.md`: Mapping of doc audiences.
17. `.sisyphus/notepads/documentation-improvement/structure-review.md`: Analysis of folder hierarchy.
18. `.sisyphus/notepads/reliability-first-intelligence-hardening/decisions.md`: Reliability design choices.
19. `.sisyphus/notepads/reliability-first-intelligence-hardening/issues.md`: Reliability bottlenecks.
20. `.sisyphus/notepads/reliability-first-intelligence-hardening/learnings.md`: Insights from hardening.
21. `.sisyphus/notepads/reliability-first-intelligence-hardening/problems.md`: Identified stability issues.
22. `.sisyphus/notepads/solstein-data-integration-wave1/decisions.md`: Wave 1 integration choices.
23. `.sisyphus/notepads/solstein-data-integration-wave1/issues.md`: Wave 1 blockers.
24. `.sisyphus/notepads/solstein-data-integration-wave1/learnings.md`: Wave 1 insights.
25. `.sisyphus/notepads/solstein-data-integration-wave1/problems.md`: Wave 1 technical debt.
26. `.sisyphus/notepads/solstein-data-integration-wave1/stream-c-learnings.md`: Specific insights for Stream C.
27. `.sisyphus/plans/complete-quality-improvement-plan.md`: Comprehensive quality roadmap.
28. `.sisyphus/plans/documentation-improvement.md`: Detailed doc task list.
29. `.sisyphus/plans/reliability-first-intelligence-hardening.md`: Hardening task list.
30. `.sisyphus/plans/solstein-data-integration-wave1.md`: Integration task list.
31. `.sisyphus/plans/solstein-repo-cleanup.md`: Cleanup and organization plan.
32. `.sisyphus/plans/solstein-scale-observability.md`: Observability enhancement plan.
33. `.sisyphus/plans/solstein-wave2-data-freshness-quality.md`: Wave 2 task list.
34. `.sisyphus/plans/unify-nyx-gestalt-patterns.md`: Pattern alignment strategy.
35. `.sisyphus/tasks/solstein-data-integration-wave1.yaml`: Structured task definitions.
36. `.sisyphus/evidence/stream-d-dependencies.json`: (Duplicate entry in context, noted).

### Source Code (17 files)
New infrastructure and connectors for the Refresh/Conflict/Confidence system.
37. `src/solstein/infrastructure/refresh.py`: Base classes for the refresh system.
38. `src/solstein/infrastructure/conflict_resolution.py`: The `ConflictResolutionEngine` implementation.
39. `src/solstein/infrastructure/confidence_adjustment.py`: The `ConfidenceAdjuster` implementation.
40. `src/solstein/infrastructure/unified_registry.py`: Central registry for all data sources.
41. `src/solstein/infrastructure/connectors/companies_house_refresh.py`: Companies House refresh logic.
42. `src/solstein/infrastructure/connectors/funding_refresh.py`: Funding data refresh logic.
43. `src/solstein/infrastructure/connectors/github_refresh.py`: GitHub data refresh logic.
44. `src/solstein/infrastructure/connectors/global_market_refresh.py`: Global market refresh logic.
45. `src/solstein/infrastructure/connectors/linkedin_refresh.py`: LinkedIn refresh logic.
46. `src/solstein/infrastructure/connectors/news_refresh.py`: News data refresh logic.
47. `src/solstein/infrastructure/connectors/news_signal_refresh.py`: News signal refresh logic.
48. `src/solstein/infrastructure/connectors/patents_refresh.py`: Patents data refresh logic.
49. `src/solstein/infrastructure/connectors/sec_edgar_refresh.py`: SEC Edgar refresh logic.
50. `src/solstein/infrastructure/connectors/web_search_refresh.py`: Web search refresh logic.
51. `src/solstein/infrastructure/connectors/website_refresh.py`: Website content refresh logic.
52. `src/solstein/infrastructure/connectors/yahoo_finance_refresh.py`: Yahoo Finance refresh logic.
53. `src/solstein/worker_tasks.py`: Celery tasks for background data operations.
54. `src/solstein/celery_config.py`: Celery worker configuration.
55. `src/solstein/analytics/confidence_integration.py`: Pipeline integration for confidence scores.
56. `src/solstein/api/routes/refresh.py`: API endpoints for data refresh.
57. `alembic/versions/E2a_add_refresh_conflict_confidence_tables.py`: DB migration for new tables.

### Documentation (6 files)
58. `docs/DIRECTORY_ORGANIZATION.md`: Repository structure guide.
59. `docs/guides/documentation-style-guide.md`: Standards for technical writing.
60. `docs/examples/curl/curl-examples.md`: API examples for curl.
61. `docs/examples/javascript/javascript-client.md`: JS client integration.
62. `docs/examples/python/python-client.md`: Python SDK examples.
63. `docs/guides/ci-cd.md`: CI/CD pipeline overview (stub).

### Tests & Other (2 files)
64. `tests/unit/adapters/test_protocols.py`: Tests for `UnifiedDataSource`.
65. `dashboard/vitest.config.ts`: Frontend test configuration.

---

## Files Deleted (20 Files)

| File Path | Recommendation | Reason |
| :--- | :--- | :--- |
| `opencode/rules/testing/standards-2026.1` | ❌ **RESTORE** | Contains our project-specific testing standards. |
| `scripts/opencode-mcp-doctor.sh` | ❌ **RESTORE** | Essential diagnostic script for MCP. |
| `scripts/opencode-mcp-smoke-test.sh` | ❌ **RESTORE** | Essential smoke test for MCP. |
| `requirements.txt` | ✅ KEEP | `pyproject.toml` is now the single source of truth. |
| `patch_pragma.py` | ✅ KEEP | Obsolete utility script. |
| `react-native-template/App.tsx` | ✅ KEEP | Unused template file. |
| `react-native-template/package.json` | ✅ KEEP | Unused template file. |
| `react-native-template/src/styles/global.ts` | ✅ KEEP | Unused template file. |
| `react-native-template/tsconfig.json` | ✅ KEEP | Unused template file. |
| `dashboard/public/file.svg` | ✅ KEEP | Default Next.js asset. |
| `dashboard/public/globe.svg` | ✅ KEEP | Default Next.js asset. |
| `dashboard/public/next.svg` | ✅ KEEP | Default Next.js asset. |
| `dashboard/public/vercel.svg` | ✅ KEEP | Default Next.js asset. |
| `dashboard/public/window.svg` | ✅ KEEP | Default Next.js asset. |
| `data/output/demo_output/solstein_demo_20260218_065816.csv` | ✅ KEEP | Stale demo data. |
| `data/output/demo_output/solstein_demo_20260218_065816.xlsx` | ✅ KEEP | Stale demo data. |
| `data/output/demo_output/solstein_demo_20260219_223205.csv` | ✅ KEEP | Stale demo data. |
| `data/output/demo_output/solstein_demo_20260219_223205.xlsx` | ✅ KEEP | Stale demo data. |
| `data/output/demo_output/solstein_demo_20260219_224433.csv` | ✅ KEEP | Stale demo data. |
| `data/output/demo_output/solstein_demo_20260219_224433.xlsx` | ✅ KEEP | Stale demo data. |

---

## Files Modified (97 Files)

### A. FORMATTING-ONLY Changes
These files were modified by automated tools (ruff/black) or had import reordering. No logic was changed.
1.  `src/solstein/adapters/enrichment/funding.py` ✅ KEEP
2.  `src/solstein/adapters/enrichment/global_market.py` ✅ KEEP
3.  `src/solstein/adapters/enrichment/linkedin.py` ✅ KEEP
4.  `src/solstein/adapters/enrichment/news.py` ✅ KEEP
5.  `src/solstein/adapters/enrichment/patents.py` ✅ KEEP
6.  `src/solstein/adapters/enrichment/web_search_news.py` ✅ KEEP
7.  `src/solstein/adapters/enrichment/website.py` ✅ KEEP
8.  `src/solstein/adapters/enrichment/yahoo_finance.py` ✅ KEEP
9.  `src/solstein/adapters/instrumented.py` ✅ KEEP
10. `src/solstein/agents/base_agent.py` ✅ KEEP
11. `src/solstein/agents/companies_house_agent.py` ✅ KEEP
12. `src/solstein/agents/resilience.py` ✅ KEEP
13. `src/solstein/agents/web_search_agent.py` ✅ KEEP
14. `src/solstein/agents/website_agent.py` ✅ KEEP
15. `src/solstein/core/monitoring.py` ✅ KEEP
16. `src/solstein/data/loaders.py` ✅ KEEP
17. `src/solstein/monitoring/continuous_monitor.py` ✅ KEEP
18. `src/solstein/infrastructure/database_service.py` ✅ KEEP
19. `src/solstein/data/connectors/companies_house_connector.py` ✅ KEEP
20. `src/solstein/data/connectors/sec_edgar_connector.py` ✅ KEEP
21. `src/solstein/analytics/scorers/financial_health.py` ✅ KEEP
22. `src/solstein/analytics/scorers/growth_momentum.py` ✅ KEEP

### B. SUBSTANTIVE Changes

#### `src/solstein/adapters/protocols.py` ⚠️ REVIEW
- **Changes:** Added `refresh()`, `get_confidence()`, `get_authority()`, and `supports_incremental()` to `EnrichmentSource`. Introduced `UnifiedDataSource` protocol.
- **Risk:** High. This is a breaking change for all existing enrichment adapters.
- **Verdict:** ⚠️ REVIEW. Necessary for the new architecture but requires a migration plan for custom adapters.

#### `src/solstein/research/aggregate.py` ⚠️ REVIEW
- **Changes:** Integrated `ConflictResolutionEngine`. Rewrote Yahoo Finance extraction to a flat mapping.
- **Risk:** High. The Yahoo Finance rewrite might miss nested fields previously captured.
- **Verdict:** ⚠️ REVIEW. Verify field coverage for Yahoo Finance.

#### `src/solstein/domain/facts.py` ✅ KEEP
- **Changes:** Added ORM models for `RefreshMetadata`, `DataSourceConflict`, and `ConfidenceCalibration`.
- **Verdict:** ✅ KEEP. Essential for the new data quality features.

#### `src/solstein/research/pipeline.py` ✅ KEEP
- **Changes:** Removed unused `build_company_profile` import. Formatting cleanup.
- **Verdict:** ✅ KEEP.

#### `src/solstein/exporters/audit_report.py` ❌ REVERT
- **Changes:** Formatting cleanup, but introduced a critical bug in timestamp formatting.
- **Bug:** Changed `strftime("%Y-%m-%d %H:%M UTC")` to `strftime("%Y-%m-%d %H:%M timezone.utc")`.
- **Verdict:** ❌ REVERT.

#### `src/solstein/research/gather.py` ✅ KEEP
- **Changes:** Formatting and removal of unused variable assignments.
- **Verdict:** ✅ KEEP.

#### `src/solstein/infrastructure/database_models.py` ✅ KEEP
- **Changes:** Extensive reformatting of mapped columns and relationships.
- **Verdict:** ✅ KEEP.

#### `src/solstein/config.py` ✅ KEEP
- **Changes:** Added Celery broker/backend and refresh schedule settings.
- **Verdict:** ✅ KEEP.

#### `src/solstein/core/supabase_client.py` ✅ KEEP
- **Changes:** Added try/except for `supabase` package imports.
- **Verdict:** ✅ KEEP. Improves resilience in environments without Supabase.

#### `src/solstein/adapters/discovery/competitor_json.py` 🔄 CHERRY-PICK
- **Changes:** Implemented the new `UnifiedDataSource` protocol.
- **Verdict:** 🔄 CHERRY-PICK.

#### `src/solstein/agents/coordinator_agent.py` ✅ KEEP
- **Changes:** Added try/except for `langgraph` imports.
- **Verdict:** ✅ KEEP.

#### `src/solstein/agents/github_agent.py` ✅ KEEP
- **Changes:** Fixed variable shadowing (`l` -> `lat`) and simplified logic.
- **Verdict:** ✅ KEEP.

#### `src/solstein/domain/models.py` & `simulation.py` ✅ KEEP
- **Changes:** Added `StrEnum` compatibility shim for Python 3.10.
- **Verdict:** ✅ KEEP.

#### `src/solstein/api/routers/scoring.py` ✅ KEEP
- **Changes:** Updated "Neutral" to "Salt" terminology.
- **Verdict:** ✅ KEEP.

#### `src/solstein/infrastructure/repositories.py` ✅ KEEP
- **Changes:** Modernized type hints (List -> list) and removed unused imports.
- **Verdict:** ✅ KEEP.

#### `src/solstein/data/connectors/news_signal_detector.py` ✅ KEEP
- **Changes:** Replaced for-loop with `any()` expression in `_match_patterns`.
- **Verdict:** ✅ KEEP.

#### `src/solstein/extractors/markdown_extractor.py` ✅ KEEP
- **Changes:** Pure formatting and line unwrapping.
- **Verdict:** ✅ KEEP.

#### `src/solstein/infrastructure/database.py` ✅ KEEP
- **Changes:** Line unwrapping of async_sessionmaker call.
- **Verdict:** ✅ KEEP.

#### `src/solstein/infrastructure/outbox_worker.py` ✅ KEEP
- **Changes:** Import reorder + line unwrapping of ternary expressions.
- **Verdict:** ✅ KEEP.

#### `src/solstein/infrastructure/reconcile_runs.py` ✅ KEEP
- **Changes:** Line unwrapping throughout.
- **Verdict:** ✅ KEEP.

#### `src/solstein/infrastructure/retry_policy.py` ✅ KEEP
- **Changes:** Line unwrapping.
- **Verdict:** ✅ KEEP.

#### `src/solstein/research/discovery.py` ✅ KEEP
- **Changes:** Line unwrapping.
- **Verdict:** ✅ KEEP.

#### `src/solstein/research/evidence.py` ✅ KEEP
- **Changes:** Line unwrapping.
- **Verdict:** ✅ KEEP.

#### `src/solstein/research/hashing.py` ✅ KEEP
- **Changes:** Dict comprehension reformatted to single line.
- **Verdict:** ✅ KEEP.

#### `src/solstein/research/signals.py` ✅ KEEP
- **Changes:** Removed unused `Any` import. Line unwrapping.
- **Verdict:** ✅ KEEP.

#### `src/solstein/adapters/discovery/static_catalog.py` ⚠️ REVIEW
- **Changes:** Implemented `UnifiedDataSource` protocol.
- **Verdict:** ⚠️ REVIEW.

#### `src/solstein/infrastructure/research_dual_write.py` ✅ KEEP
- **Changes:** Pure formatting: line unwrapping, query chain reformatting.
- **Verdict:** ✅ KEEP.

### C. DOCUMENTATION Changes (Existing Files)
Nyx performed a massive overhaul of the `docs/` directory.
1.  `docs/DOCUMENTATION_INDEX.md`: 5 false status changes (⏳TODO→✅Complete). **REVERTED**.
2.  `docs/DOCUMENTATION_AUDIT.md`: Terminology update (Rocket/Dinosaur/Neutral → Phoenix/Lead/Salt). ✅ KEEP.
3.  `docs/DOCUMENTATION_ROADMAP.md`: All 16 roadmap items changed from ⏳TODO → ✅Complete (FALSIFIED). ❌ REVERT.
4.  `docs/GLOSSARY.md`: Terminology update. ✅ KEEP.
5.  `docs/LORE/grimoire.md`: Terminology update. ✅ KEEP.
6.  `docs/LORE/origin.md`: Terminology update + section heading renames. ✅ KEEP.
7.  `docs/LORE/the-play.md`: Terminology update. ✅ KEEP.
8.  `docs/PITCH/case-study.md`: Terminology update + emoji updates. ✅ KEEP.
9.  `docs/PITCH/executive-brief.md`: Terminology update. ✅ KEEP.
10. `docs/PITCH/full-proposal.md`: Terminology update. ✅ KEEP.
11. `docs/README.md`: Terminology + replaced opencode-tooling link with operator/API links. ✅ KEEP.
12. `docs/api/reference.md`: Added Quick Reference table, schema reference section. ✅ KEEP.
13. `docs/architecture/DATA_SOURCE_WIRING_REFERENCE.md`: Fixed indentation. ✅ KEEP.
14. `docs/architecture/modules.md`: Terminology update. ✅ KEEP.
15. `docs/audits/DATA_PIPELINE_AUDIT_2026-02-23.md`: Fixed "Returns Neutral instead of Salt" → "Returns Salt instead of Salt". ⚠️ REVIEW.
16. `docs/examples/README.md`: Terminology update. ✅ KEEP.
17. `docs/guides/code-conventions.md`: Reformatting. ✅ KEEP.
18. `docs/guides/database.md`: Formatting. ✅ KEEP.
19. `docs/guides/developer.md`: Reformatting. ✅ KEEP.
20. `docs/guides/extending-solstein.md`: Formatting. ✅ KEEP.
21. `docs/guides/troubleshooting.md`: Formatting. ✅ KEEP.
22. `docs/index.md`: Updated classification terminology. ✅ KEEP.

### D. TEST Changes (Existing Files)
1.  `tests/test_fastapi.py`: health check assertion "healthy" → in ("healthy", "degraded"). ✅ KEEP.
2.  `tests/unit/test_api_base_coverage.py`: Same health assertion change. ✅ KEEP.
3.  `tests/unit/test_monitoring.py`: HealthStatus.HEALTHY → in (HEALTHY, DEGRADED). ✅ KEEP.
4.  `tests/unit/test_contradiction_lifecycle.py`: datetime.UTC → timezone.utc (Py3.10 compat). ✅ KEEP.
5.  `tests/unit/test_facts_orm_models.py`: Same + blank line after imports. ✅ KEEP.
6.  `tests/unit/test_reconciliation_report.py`: Same UTC fix. ✅ KEEP.
7.  `tests/unit/test_repositories.py`: Same UTC fix. ✅ KEEP.
8.  `tests/unit/test_research_pipeline.py`: Same UTC fix + line unwrapping. ✅ KEEP.
9.  `tests/unit/test_growth_scorer_with_facts.py`: Removed unused ScoringSettings import. ✅ KEEP.
10. `tests/unit/test_financial_health_scorer_with_facts.py`: Removed unused ScoringSettings import. ✅ KEEP.
11. `tests/unit/test_facts_migration_smoke.py`: Import reorder. ✅ KEEP.
12. `tests/unit/test_retry_policy.py`: Line unwrapping. ✅ KEEP.
13. `tests/unit/data/test_sec_edgar_connector.py`: Import reorder, assertion order swap. ✅ KEEP.
14. `tests/unit/data/test_news_signal_detector.py`: Removed unused os import. ✅ KEEP.
15. `tests/integration/conftest.py`: Removed blank line, line unwrapping. ✅ KEEP.
16. `tests/integration/test_data_gathering_e2e.py`: Import reorder, renamed batch → _batch. ✅ KEEP.
17. `tests/integration/test_full_pipeline.py`: Used contextlib.suppress, line unwrapping. ✅ KEEP.
18. `tests/integration/test_golden_dataset_regression.py`: Removed 3 unused connector imports. ✅ KEEP.

---

## New Feature: Refresh/Conflict/Confidence System

Nyx has implemented a comprehensive data lifecycle management system.

### 1. Refresh System
Connectors can now perform incremental updates.
- **Base Logic:** `src/solstein/infrastructure/refresh.py`
- **Connectors:** 12 new refresh connectors in `src/solstein/infrastructure/connectors/`
- **Scheduling:** Managed via Celery in `src/solstein/worker_tasks.py`

### 2. Conflict Resolution
Handles contradicting data from multiple sources.
- **Engine:** `ConflictResolutionEngine` in `src/solstein/infrastructure/conflict_resolution.py`
- **Logic:** Uses `SourceAuthority` rankings to resolve discrepancies during aggregation.

### 3. Confidence Calibration
Calculates a dynamic score for data reliability.
- **Adjuster:** `ConfidenceAdjuster` in `src/solstein/infrastructure/confidence_adjustment.py`
- **Integration:** Integrated into the research pipeline via `src/solstein/analytics/confidence_integration.py`.

---

## New Feature: UnifiedDataSource Protocol

The `UnifiedDataSource` protocol is the new standard for all data sources in Solstein.

**Key Methods:**
- `refresh()`: Perform an incremental update.
- `get_confidence()`: Retrieve the current confidence score for the source.
- `get_authority()`: Retrieve the `SourceAuthority` level.
- `supports_incremental()`: Boolean flag for refresh capability.

**Breaking Change Analysis:**
The addition of these methods to the base `EnrichmentSource` protocol means that all existing adapters that do not implement these methods will fail type checking and potentially runtime execution if called via the new registry.

---

## CI/Config Changes

- **.github/workflows/ci-12stage.yml**: Added coverage artifact upload. Marked E2E and Docker builds as non-blocking (`continue-on-error`).
- **.github/workflows/ci.yml**: Removed `action-get-latest-tag`.
- **pyproject.toml**: Added several Ruff ignore rules (`TC001-TC006`, `UP017`, `UP036`) to suppress linting errors in the new infrastructure code.
- **.gitignore**: Removed `.sisyphus/` to allow tracking of planning artifacts.

---

## Risk Summary Table

| File | Risk Level | Recommendation |
| :--- | :--- | :--- |
| `src/solstein/adapters/protocols.py` | High | ⚠️ REVIEW (Breaking Protocol) |
| `src/solstein/research/aggregate.py` | High | ⚠️ REVIEW (Yahoo Finance Logic) |
| `src/solstein/exporters/audit_report.py` | High | ❌ REVERT (Timestamp Bug) |
| `docs/DOCUMENTATION_ROADMAP.md` | Medium | ❌ REVERT (Falsified Status) |
| `opencode/rules/testing/standards-2026.1` | High | ❌ RESTORE (Deleted Standards) |
| `scripts/opencode-mcp-doctor.sh` | High | ❌ RESTORE (Deleted Script) |
| `scripts/opencode-mcp-smoke-test.sh` | High | ❌ RESTORE (Deleted Script) |
| `src/solstein/infrastructure/refresh.py` | Low | ✅ KEEP (New Feature) |
| `src/solstein/worker_tasks.py` | Low | ✅ KEEP (New Feature) |
| `src/solstein/domain/facts.py` | Low | ✅ KEEP (New Models) |
| `src/solstein/config.py` | Low | ✅ KEEP (New Config) |
| `src/solstein/agents/github_agent.py` | Low | ✅ KEEP (Bug Fix) |
| `src/solstein/core/supabase_client.py` | Low | ✅ KEEP (Resilience Fix) |
| `src/solstein/domain/models.py` | Low | ✅ KEEP (Py3.10 Compat) |
| `src/solstein/domain/simulation.py` | Low | ✅ KEEP (Py3.10 Compat) |
| `src/solstein/api/routers/scoring.py` | Low | ✅ KEEP (Terminology) |
| `tests/test_fastapi.py` | Low | ✅ KEEP (Health Check) |
| `.github/workflows/ci-12stage.yml` | Medium | ⚠️ REVIEW (Non-blocking CI) |

---

## Recommendations by Strategy

### 1. Keep + Selective Restore (Recommended)
This strategy preserves the valuable new features while fixing the critical errors.
- **Action:** Merge Nyx's branch.
- **Action:** Restore deleted `opencode/` rules and `scripts/`.
- **Action:** Revert the `audit_report.py` timestamp change.
- **Action:** Revert the `DOCUMENTATION_ROADMAP.md` status changes.
- **Action:** Implement no-op `refresh()` methods in legacy adapters.

### 2. Rollback + Cherry-pick
Use this if the protocol changes are deemed too disruptive for the current release cycle.
- **Action:** Reset to `797c98f`.
- **Action:** Cherry-pick bug fixes from `github_agent.py` and `supabase_client.py`.
- **Action:** Cherry-pick the `StrEnum` compatibility shims.

### 3. Full Discard
Not recommended. The Refresh and Conflict Resolution systems are high-value additions that should be integrated.

---
*End of Audit Report*
