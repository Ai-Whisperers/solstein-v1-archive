# Solstein — Execution Order

> **This is the single source of truth for autonomous work.**
>
> Pick the **first READY item** in the queue. Work it. Mark it DONE. Move to the next.
> Do **not** skip ahead. Do **not** pick a story outside this list. Do **not** unblock items yourself by
> bypassing the gate criteria. If all remaining items are BLOCKED, stop and report.

| Updated | 2026-04-05 | By | Codebase audit + epic reorganization |

---

## How to Use This Document

1. **Read the current gate** before picking any story. If the gate is not satisfied, stop.
2. **Pick the first row with Status = READY** in the current phase.
3. **Read the story file** linked in the # column before writing a single line of code.
4. **Run the Before-grep** listed in the story file (or below) to confirm the bug exists.
5. **Implement**, run tests, confirm green, run the After-grep to confirm the fix.
6. **Commit** with `feat(STORY-NNN): ...` and update this file: change Status to DONE.
7. Move to the next READY row.

**Never mark a gate as passed yourself.** Gates are passed when every row above them is DONE.

---

## Phase 0 — Contamination & Test Infrastructure

> **⛔ GATE 0 — Required before any data or feature work**
>
> This phase fixes structural correctness: test pollution that corrupts CI, synthetic data that
> reaches production pipelines, and module-scope mutations that give false-green tests. Until these
> are done, any test result and any pipeline output is suspect.

### Group A — Test Isolation (do these first)

| # | Story | Title | Size | Status |
|---|-------|-------|------|--------|
| 1 | [STORY-376](EPICS/EPIC-013-test-suite-integrity/STORIES/STORY-376.md) | Remove leaked test DB files from git; add `.gitignore` rules | XS | READY |
| 2 | [STORY-373](EPICS/EPIC-013-test-suite-integrity/STORIES/STORY-373.md) | Add CI lint guard — no `src/` module may import from `tests.*` or `scripts.*` | XS | READY |
| 3 | [STORY-374](EPICS/EPIC-013-test-suite-integrity/STORIES/STORY-374.md) | Fix `test_api_routers_coverage.py` — move module-scope mutations into fixtures | S | READY |
| 4 | [STORY-375](EPICS/EPIC-013-test-suite-integrity/STORIES/STORY-375.md) | Fix `test_load.py` — move DB URL env overrides into monkeypatched fixtures | S | READY |
| 5 | [STORY-377](EPICS/EPIC-013-test-suite-integrity/STORIES/STORY-377.md) | Add CI guard detecting module-scope mutations in test files | S | READY |
| 6 | [STORY-387](EPICS/EPIC-013-test-suite-integrity/STORIES/STORY-387.md) | Fix `pyproject.toml` — remove global `DeprecationWarning` suppression; add integration test separation | S | READY |

### Group B — Production Contamination Gates

| # | Story | Title | Size | Status |
|---|-------|-------|------|--------|
| 7 | [STORY-371](EPICS/EPIC-013-test-suite-integrity/STORIES/STORY-371.md) | Fix test factories — add `data_source_type="synthetic"` default to all factory classes | XS | READY |
| 8 | [STORY-372](EPICS/EPIC-013-test-suite-integrity/STORIES/STORY-372.md) | Deduplicate test factory modules — consolidate into one canonical source | S | READY |
| 9 | [STORY-382](EPICS/EPIC-052-provenance-confidence-quality-gates/STORIES/STORY-382.md) | Fix `test_modes.py` — change `SOLSTEIN_TEST_MODE` default from `"mixed"` to `"strict_real"` | S | READY |
| 10 | [STORY-383](EPICS/EPIC-052-provenance-confidence-quality-gates/STORIES/STORY-383.md) | Fix `research_dual_write.py` — remove hardcoded `strict_provenance=False` from production pipeline | S | READY |
| 11 | [STORY-384](EPICS/EPIC-033-data-completeness-export-integrity/STORIES/STORY-384.md) | Add `data_source_type` column to `CompanyRecord` DB schema + Alembic migration | S | READY |
| 12 | [STORY-386](EPICS/EPIC-033-data-completeness-export-integrity/STORIES/STORY-386.md) | Fix `load_competitor_data.py` — remove `get_database_url(test=True)` from production migration | XS | READY |
| 13 | [STORY-381](EPICS/EPIC-033-data-completeness-export-integrity/STORIES/STORY-381.md) | Fix `load_competitor_data.py` migration — set `data_source_type` on all `CompanyRecord` objects | XS | BLOCKED by #11 |

> **⛔ GATE 0 SATISFIED when**: rows 1–13 are all DONE.
> Before proceeding to Phase 1, run:
> ```bash
> PYTHONPATH=src .venv/bin/python3 -m pytest tests/unit/ -q --ignore=tests/unit/test_async_boundary_regressions.py --ignore=tests/unit/test_api_routers_coverage.py --no-header 2>&1 | tail -3
> ```
> Regression floor: ≥ 3855 passed. If lower, stop and investigate before continuing.

---

## Phase 1 — Test Suite Interface Fixes

> **⛔ GATE 1 — Required before scoring or pipeline work**
>
> These fix interface-drift test failures (tests written against old APIs). They are independent of each
> other. Note: STORY-337 **must come after STORY-374** (Phase 0, #3).

| # | Story | Title | Size | Status |
|---|-------|-------|------|--------|
| 14 | [STORY-334](EPICS/EPIC-083-fix-test-suite/STORIES/STORY-334.md) | Fix 23 `news_signal_detector` tests (`daily_query_limit` → `_daily_query_count`) | S | READY |
| 15 | [STORY-335](EPICS/EPIC-083-fix-test-suite/STORIES/STORY-335.md) | Fix 15 `test_models` tests (FinancialMetric validator change) | S | READY |
| 16 | [STORY-336](EPICS/EPIC-083-fix-test-suite/STORIES/STORY-336.md) | Fix 21 `test_unified_loader` tests (refactored loader interface) | S | READY |
| 17 | [STORY-338](EPICS/EPIC-083-fix-test-suite/STORIES/STORY-338.md) | Mark DB-dependent tests `@pytest.mark.db`; exclude from default local run | S | READY |
| 18 | [STORY-337](EPICS/EPIC-083-fix-test-suite/STORIES/STORY-337.md) | Fix API router 401 failures — assess residual scope after STORY-374 lands | S | BLOCKED by #3 |

> **⛔ GATE 1 SATISFIED when**: rows 14–18 all DONE.
> ```bash
> PYTHONPATH=src .venv/bin/python3 -m pytest tests/unit/ -q -m "not db" --no-header 2>&1 | tail -3
> ```
> Target: ≥ 3920 passed, 0 DB-connection errors.

---

## Phase 2 — Infrastructure Reliability

> Independent S-effort stories. All three can be worked in any order.

| # | Story | Title | Size | Status |
|---|-------|-------|------|--------|
| 19 | [STORY-357](EPICS/EPIC-088-infrastructure-reliability/STORIES/STORY-357.md) | Harden Celery health check — return HTTP 503 when workers unreachable | S | READY |
| 20 | [STORY-358](EPICS/EPIC-088-infrastructure-reliability/STORIES/STORY-358.md) | Add startup check: broker reachable before accepting traffic | S | READY |
| 21 | [STORY-359](EPICS/EPIC-088-infrastructure-reliability/STORIES/STORY-359.md) | Add task discovery test — all 13 Beat-scheduled tasks importable and decorated | S | READY |

---

## Phase 3 — Multi-Tenancy Security

| # | Story | Title | Size | Status |
|---|-------|-------|------|--------|
| 22 | [STORY-353](EPICS/EPIC-087-multi-tenancy-enforcement/STORIES/STORY-353.md) | Audit tenant isolation strategy: Option A (SQLAlchemy RLS) vs Option B (app-layer) | M | READY |
| 23 | [STORY-352](EPICS/EPIC-087-multi-tenancy-enforcement/STORIES/STORY-352.md) | Fix `_validate_api_key()` stub; register middleware per strategy decision | S | BLOCKED by #22 |

---

## Phase 4 — Dead Code Removal

> STORY-341 and STORY-342 are confirmed safe (no callers). Do these first.
> STORY-340 and STORY-343 require caller fixes before deletion — do not skip that step.

| # | Story | Title | Size | Status |
|---|-------|-------|------|--------|
| 24 | [STORY-341](EPICS/EPIC-084-dead-code-cleanup/STORIES/STORY-341.md) | Delete `adapters/enrichment/_retired/` directory (8 dead adapter files) | XS | READY |
| 25 | [STORY-342](EPICS/EPIC-084-dead-code-cleanup/STORIES/STORY-342.md) | Delete `adapters/discovery/_retired/` directory | XS | READY |
| 26 | [STORY-340](EPICS/EPIC-084-dead-code-cleanup/STORIES/STORY-340.md) | Refactor `cli_research.py` to remove `RealDataLoader` dependency, then delete `real_data_integration.py` | M | READY |
| 27 | [STORY-343](EPICS/EPIC-084-dead-code-cleanup/STORIES/STORY-343.md) | Fix `review.py:168` import, then delete `research/graph/` (requires team sign-off) | M | BLOCKED — needs explicit team sign-off |

---

## Phase 5 — Data Supply (Product Phase P1)

> Enrich market catalog first (271-281), then fix adapters to not crash on missing data (286 before others).

| # | Story | Title | Size | Status |
|---|-------|-------|------|--------|
| 28 | [STORY-277](EPICS/EPIC-071-enrich-market-catalog-real-data/STORIES/STORY-277.md) | Add website URLs to all 24 Dutch Energy catalog companies | S | READY |
| 29 | [STORY-278](EPICS/EPIC-071-enrich-market-catalog-real-data/STORIES/STORY-278.md) | Add stock tickers for all publicly traded catalog companies | S | READY |
| 30 | [STORY-279](EPICS/EPIC-071-enrich-market-catalog-real-data/STORIES/STORY-279.md) | Add LinkedIn company slugs to all catalog companies | S | READY |
| 31 | [STORY-280](EPICS/EPIC-071-enrich-market-catalog-real-data/STORIES/STORY-280.md) | Add GitHub org names where applicable | S | READY |
| 32 | [STORY-281](EPICS/EPIC-071-enrich-market-catalog-real-data/STORIES/STORY-281.md) | Add CrunchBase slugs for funded companies | S | READY |
| 33 | [STORY-286](EPICS/EPIC-072-enrichment-adapter-resilience/STORIES/STORY-286.md) | All enrichment adapters: return partial data with low confidence instead of raising ValueError | M | READY |
| 34 | [STORY-282](EPICS/EPIC-072-enrichment-adapter-resilience/STORIES/STORY-282.md) | YahooFinanceEnrichment: fall back to web scraping when no ticker | M | READY |
| 35 | [STORY-283](EPICS/EPIC-072-enrichment-adapter-resilience/STORIES/STORY-283.md) | WebsiteEnrichment: auto-discover URL from company name via SearXNG | M | READY |
| 36 | [STORY-284](EPICS/EPIC-072-enrichment-adapter-resilience/STORIES/STORY-284.md) | GlobalMarketEnrichment: fall back to sector ETF data when no ticker | M | READY |
| 37 | [STORY-285](EPICS/EPIC-072-enrichment-adapter-resilience/STORIES/STORY-285.md) | FundingEnrichment: implement Crunchbase-free fallback via GDELT | M | READY |
| 38 | [STORY-287](EPICS/EPIC-073-wire-connectors-into-pipeline/STORIES/STORY-287.md) | Create SearXNG-based web search enrichment adapter | M | READY |
| 39 | [STORY-288](EPICS/EPIC-073-wire-connectors-into-pipeline/STORIES/STORY-288.md) | Create GDELT news enrichment adapter | M | READY |
| 40 | [STORY-289](EPICS/EPIC-073-wire-connectors-into-pipeline/STORIES/STORY-289.md) | Create SEC EDGAR enrichment adapter (10-K/10-Q) | M | READY |
| 41 | [STORY-290](EPICS/EPIC-073-wire-connectors-into-pipeline/STORIES/STORY-290.md) | Create GitHub enrichment adapter | M | READY |
| 42 | [STORY-291](EPICS/EPIC-073-wire-connectors-into-pipeline/STORIES/STORY-291.md) | Create arXiv/patent enrichment adapter | M | READY |
| 43 | [STORY-292](EPICS/EPIC-073-wire-connectors-into-pipeline/STORIES/STORY-292.md) | Register all new enrichment adapters in `build_default_registry()` | S | BLOCKED by #38–42 |
| 44 | [STORY-294](EPICS/EPIC-074-revenue-financial-data-validation/STORIES/STORY-294.md) | Normalize revenue units: detect K/M/B strings, convert all to EUR millions | S | READY |
| 45 | [STORY-293](EPICS/EPIC-074-revenue-financial-data-validation/STORIES/STORY-293.md) | Add revenue sanity checks: cap at industry max, flag outliers > 3 sigma | S | READY |
| 46 | [STORY-295](EPICS/EPIC-074-revenue-financial-data-validation/STORIES/STORY-295.md) | Cross-validate revenue across 2+ sources before accepting high-confidence value | S | READY |
| 47 | [STORY-296](EPICS/EPIC-074-revenue-financial-data-validation/STORIES/STORY-296.md) | Add employee count validation (1–10M range, cross-reference with revenue) | S | READY |
| 48 | [STORY-297](EPICS/EPIC-074-revenue-financial-data-validation/STORIES/STORY-297.md) | Add funding amount validation with automatic currency conversion to EUR | S | READY |

---

## Phase 6 — Scoring Accuracy (Product Phase P2)

| # | Story | Title | Size | Status |
|---|-------|-------|------|--------|
| 49 | [STORY-298](EPICS/EPIC-075-fix-scoring-missing-data/STORIES/STORY-298.md) | GrowthMomentumScorer: change base from 0 to 3.0, reduce missing-data penalty | S | READY |
| 50 | [STORY-299](EPICS/EPIC-075-fix-scoring-missing-data/STORIES/STORY-299.md) | FinancialHealthScorer: change base from 2.5 to 4.0, reduce missing-revenue penalty | S | READY |
| 51 | [STORY-300](EPICS/EPIC-075-fix-scoring-missing-data/STORIES/STORY-300.md) | Add `DataCompletenessScorer`: measures % of data fields populated per company | M | READY |
| 52 | [STORY-301](EPICS/EPIC-075-fix-scoring-missing-data/STORIES/STORY-301.md) | Weight composite score by data completeness | S | BLOCKED by #51 |
| 53 | [STORY-302](EPICS/EPIC-075-fix-scoring-missing-data/STORIES/STORY-302.md) | Update golden dataset expected ranges to match corrected scoring formula | S | BLOCKED by #49, #50 |
| 54 | [STORY-303](EPICS/EPIC-076-capability-overlap-enhancement/STORIES/STORY-303.md) | Expand capability keyword lists: add 20+ synonyms per Eneve capability | S | READY |
| 55 | [STORY-305](EPICS/EPIC-076-capability-overlap-enhancement/STORIES/STORY-305.md) | Add energy-software capability taxonomy with industry standard terms | S | READY |
| 56 | [STORY-306](EPICS/EPIC-076-capability-overlap-enhancement/STORIES/STORY-306.md) | Integrate capability overlap % into composite score (10% weight) | S | BLOCKED by #54 |
| 57 | [STORY-307](EPICS/EPIC-077-ai-maturity-scoring-enhancement/STORIES/STORY-307.md) | Expand AI signal detection: add LLM/GPT/neural/NLP/computer vision keywords | S | READY |
| 58 | [STORY-339](EPICS/EPIC-083-fix-test-suite/STORIES/STORY-339.md) | Update golden dataset expected ranges to match current scoring engine output | S | BLOCKED by #53 |
| 59 | [STORY-388](EPICS/EPIC-052-provenance-confidence-quality-gates/STORIES/STORY-388.md) | Fix `instrumented.py` — propagate actual adapter confidence (not hardcoded 1.0) | S | READY |
| 60 | [STORY-389](EPICS/EPIC-052-provenance-confidence-quality-gates/STORIES/STORY-389.md) | Fix SEC EDGAR connectors — replace `solstein@example.com` placeholder | XS | READY |
| 61 | [STORY-390](EPICS/EPIC-052-provenance-confidence-quality-gates/STORIES/STORY-390.md) | Fix `domain/models.py` — change `industry` default from `"Energy Software"` to `None` | XS | READY |

---

## Phase 7 — Infrastructure Deployment (Product Phase P3)

> These require human operator action (credentials, cloud provisioning). Hermes can prepare config
> files and verify locally, but cannot provision cloud resources.

| # | Story | Title | Size | Status |
|---|-------|-------|------|--------|
| 62 | [STORY-311](EPICS/EPIC-078-deploy-core-infrastructure/STORIES/STORY-311.md) | Deploy PostgreSQL 15 with pgvector | M | READY |
| 63 | [STORY-312](EPICS/EPIC-078-deploy-core-infrastructure/STORIES/STORY-312.md) | Run all Alembic migrations on deployed database | S | BLOCKED by #62 |
| 64 | [STORY-313](EPICS/EPIC-078-deploy-core-infrastructure/STORIES/STORY-313.md) | Deploy Redis 7 for Celery broker | S | READY |
| 65 | [STORY-314](EPICS/EPIC-078-deploy-core-infrastructure/STORIES/STORY-314.md) | Deploy SearXNG instance for web search | S | READY |
| 66 | [STORY-315](EPICS/EPIC-078-deploy-core-infrastructure/STORIES/STORY-315.md) | Create `.env.production` with all required env vars, secrets rotated | S | BLOCKED by #62–65 |
| 67 | [STORY-321](EPICS/EPIC-080-configure-llm-providers/STORIES/STORY-321.md) | Configure primary LLM provider (Anthropic Claude) | XS | READY |
| 68 | [STORY-322](EPICS/EPIC-080-configure-llm-providers/STORIES/STORY-322.md) | Configure fallback LLM provider chain (3+ providers) | S | BLOCKED by #67 |
| 69 | [STORY-323](EPICS/EPIC-080-configure-llm-providers/STORIES/STORY-323.md) | Verify LLM health check + deep_analyzer produces real output | S | BLOCKED by #67 |
| 70 | [STORY-316](EPICS/EPIC-079-deploy-application-stack/STORIES/STORY-316.md) | Build and test Solstein Docker image | M | BLOCKED by #66 |
| 71 | [STORY-317](EPICS/EPIC-079-deploy-application-stack/STORIES/STORY-317.md) | Deploy FastAPI server with uvicorn | S | BLOCKED by #70 |
| 72 | [STORY-318](EPICS/EPIC-079-deploy-application-stack/STORIES/STORY-318.md) | Deploy Celery worker (4 queues) | S | BLOCKED by #70 |
| 73 | [STORY-319](EPICS/EPIC-079-deploy-application-stack/STORIES/STORY-319.md) | Deploy Celery Beat scheduler | S | BLOCKED by #72 |
| 74 | [STORY-320](EPICS/EPIC-079-deploy-application-stack/STORIES/STORY-320.md) | Verify all health checks pass | S | BLOCKED by #71–73 |

---

## Phase 8 — End-to-End Pipeline Execution (Product Phase P4)

> All BLOCKED until Phase 5–7 complete.

| # | Story | Title | Size | Status |
|---|-------|-------|------|--------|
| 75 | [STORY-324](EPICS/EPIC-081-first-real-pipeline-run/STORIES/STORY-324.md) | Execute discovery stage: verify 20+ companies discovered | M | BLOCKED by phases 5–7 |
| 76 | [STORY-325](EPICS/EPIC-081-first-real-pipeline-run/STORIES/STORY-325.md) | Execute gather stage: verify 15+ companies enriched | M | BLOCKED by #75 |
| 77 | [STORY-326](EPICS/EPIC-081-first-real-pipeline-run/STORIES/STORY-326.md) | Execute scoring stage: verify composite scores in 2.0–9.0 range | M | BLOCKED by #76 |
| 78 | [STORY-327](EPICS/EPIC-081-first-real-pipeline-run/STORIES/STORY-327.md) | Execute analysis stage: verify LLM insights are real (not templates) | M | BLOCKED by #77 |
| 79 | [STORY-328](EPICS/EPIC-081-first-real-pipeline-run/STORIES/STORY-328.md) | Execute export stage: generate Excel + PDF | M | BLOCKED by #78 |
| 80 | [STORY-329](EPICS/EPIC-081-first-real-pipeline-run/STORIES/STORY-329.md) | Validate: ≥ 3 Phoenix, ≥ 10 Salt, ≥ 5 Lead in results | S | BLOCKED by #79 |
| 81 | [STORY-330](EPICS/EPIC-081-first-real-pipeline-run/STORIES/STORY-330.md) | Save golden run results as regression baseline | S | BLOCKED by #80 |
| 82 | [STORY-331](EPICS/EPIC-082-live-web-discovery/STORIES/STORY-331.md) | Implement SearXNG-based competitor discovery adapter | M | BLOCKED by #65 |
| 83 | [STORY-332](EPICS/EPIC-082-live-web-discovery/STORIES/STORY-332.md) | Add LLM-powered competitor identification from web results | M | BLOCKED by #82, #67 |
| 84 | [STORY-333](EPICS/EPIC-082-live-web-discovery/STORIES/STORY-333.md) | Merge static catalog + web discovery + LLM discovery with deduplication | M | BLOCKED by #83 |
| 85 | [STORY-362](EPICS/EPIC-089-workflow-orchestration-api/STORIES/STORY-362.md) | Define `Workflow` response model + `WorkflowStatus` enum; remove 501 stub | XS | READY |
| 86 | [STORY-363](EPICS/EPIC-089-workflow-orchestration-api/STORIES/STORY-363.md) | Implement `POST /workflows` + `run_workflow_task` | M | BLOCKED by #85 |
| 87 | [STORY-364](EPICS/EPIC-089-workflow-orchestration-api/STORIES/STORY-364.md) | Implement `GET /workflows/{workflow_id}` | M | BLOCKED by #86 |

---

## Phase 9 — LLM-Dependent Scoring Features

> Blocked until STORY-321 (LLM provider configured, Phase 7).

| # | Story | Title | Size | Status |
|---|-------|-------|------|--------|
| 88 | [STORY-304](EPICS/EPIC-076-capability-overlap-enhancement/STORIES/STORY-304.md) | LLM-based capability matching against Eneve's 8 capabilities | M | BLOCKED by #67 |
| 89 | [STORY-308](EPICS/EPIC-077-ai-maturity-scoring-enhancement/STORIES/STORY-308.md) | LLM-based AI maturity assessment from company descriptions | M | BLOCKED by #67 |
| 90 | [STORY-309](EPICS/EPIC-077-ai-maturity-scoring-enhancement/STORIES/STORY-309.md) | GitHub-based AI signals (ML framework detection in repo dependencies) | M | BLOCKED by #41 |
| 91 | [STORY-310](EPICS/EPIC-077-ai-maturity-scoring-enhancement/STORIES/STORY-310.md) | Patent-based AI signals (AI/ML patent filings from USPTO) | M | BLOCKED by #42 |

---

## Phase 10 — Quality & Polish (Product Phase P5)

| # | Story | Title | Size | Status |
|---|-------|-------|------|--------|
| 92 | [STORY-344](EPICS/EPIC-085-operator-documentation/STORIES/STORY-344.md) | Write deployment guide: docker-compose up → working system in 10 min | M | BLOCKED by #74 |
| 93 | [STORY-345](EPICS/EPIC-085-operator-documentation/STORIES/STORY-345.md) | Write API key configuration guide | S | READY |
| 94 | [STORY-346](EPICS/EPIC-085-operator-documentation/STORIES/STORY-346.md) | Write market catalog customization guide | S | READY |
| 95 | [STORY-347](EPICS/EPIC-085-operator-documentation/STORIES/STORY-347.md) | Write pipeline operations runbook | M | BLOCKED by #81 |

---

## Maintenance Rule

When you complete a story:
1. Change its Status cell in this file from READY → DONE (or BLOCKED → DONE if you just completed it).
2. Check whether any BLOCKED rows below it are now unblocked and change them to READY.
3. Commit this file together with the story implementation in the same commit.

When you add a new story: add it in the correct phase at the correct priority position, with Status = READY or BLOCKED. Do not append to the bottom.
