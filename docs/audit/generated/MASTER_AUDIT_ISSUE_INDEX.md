# Master Audit Issue Index

Generated on `2026-03-26` from `docs/audit/18-03-2026_MASTER_AUDIT.md`.

This is a generated, deduplicated index of issue identifiers parsed from the master audit.
It does not modify the source audit. If table metadata repeats across multiple passes, the latest row is kept.

## Source Snapshot

- Source line count: `7589`
- Declared total issues found: `288 (3 false positives closed, 1 issue corrected)`
- Parsed distinct issue ids: `271`
- Parsed issue table rows: `1196`

The declared audit tracker total is higher than the distinct issue-id count because the source audit also tracks false positives, corrected entries, and pass-level aggregate accounting.

## Issue Index

| Issue | Severity | Status | Location | Table Rows | Title |
|---|---|---|---|---|---|
| ISSUE-01 | 🔴 HIGH | Open | `domain/models.py:107-134` | 19 | FinancialMetric has two conflicting model validators; allow_empty_primary bypass is broken |
| ISSUE-02 | 🟡 MED | Open | `domain/models.py:97-103` | 19 | FinancialMetric has duplicate Pydantic field declarations |
| ISSUE-03 | 🟡 MED | Open | `domain/models.py:143-153 vs 195-201` | 19 | Company model has duplicate field declarations across two blocks |
| ISSUE-04 | 🔴 HIGH | Open | `analytics/scoring.py:161-180` | 19 | Scoring silently degrades to base_score=0.0 on sub-scorer exceptions |
| ISSUE-05 | 🟡 MED | Open | `worker/enrichment_tasks.py:23-29` | 19 | Celery EnrichmentTask hooks are empty stubs |
| ISSUE-06 | 🔴 HIGH | Open | `worker/enrichment_tasks.py:99-109` | 19 | Celery DLQ records string-only error, no monitoring, traceback lost |
| ISSUE-07 | 🟡 MED | Open | `data/unified/enrichment.py:72-85` | 19 | Enrichment loop catches exceptions and breaks without re-raising |
| ISSUE-08 | 🟡 MED | Open | `data/report_release_gate.py:297-315` | 19 | ensure_release_ready() throwing path still exists alongside non-throwing evaluate() |
| ISSUE-09 | 🟡 MED | Open | `data/unified/enrichment.py:129+` | 19 | Enrichment errors appended to company list; no caller contract enforces checking |
| ISSUE-10 | 🔴 HIGH | Open | `api/routers/enrichment_batch.py:50-70` | 18 | Batch API response hardcodes all failure metrics to zero / 100% |
| ISSUE-11 | 🔴 HIGH | Open | `data/unified/enrichment.py:189-191` | 18 | `enrich_batch()` silently substitutes unenriched original on per-company failure |
| ISSUE-12 | 🔴 HIGH | Open | `worker/base.py:34-59` | 18 | `store_facts()` is an unimplemented stub; the DB write never happens |
| ISSUE-13 | 🟡 MED | Open | `data/gap_analyzer.py:80-85` | 18 | Gap analyzer treats `revenue=0.0` as missing, blocking pre-revenue companies |
| ISSUE-14 | 🔴 HIGH | Open | `data/gap_analyzer.py:36-46` | 18 | Gap analyzer provenance check requires HTTP/HTTPS/URN; JSON-loaded companies always fail |
| ISSUE-15 | 🟡 MED | Open | `analytics/completeness.py:98-104` | 18 | Completeness calculator counts enum defaults and empty lists as "filled" |
| ISSUE-16 | 🟡 MED | Open | `data/metric_contract.py:34-37` | 18 | `normalize_percent()` heuristic is ambiguous for values near the [-1, 1] boundary |
| ISSUE-17 | 🟡 MED | Open | `analytics/scorers/growth_momentum.py:75-77` | 18 | Scorers have inconsistent None-handling: missing data is penalized in one, silently skipped in another |
| ISSUE-18 | 🔴 HIGH | Open | `worker/base.py:67-88` | 18 | DLQ is in-memory only and logs failures at INFO severity (extends ISSUE-06) |
| ISSUE-19 | 🔴 HIGH | Open | `data/report_readiness.py:74-112` | 18 | Three of seven CLI report commands still hard-block on gate failure (resolves ISSUE-08 disclaimer) |
| ISSUE-20 | 🟢 LOW | Open | `analytics/scorers/competitive_position.py:41` | 18 | `saas_maturity` None fallback in CompetitivePositionScorer is unreachable dead code |
| ISSUE-21 | 🟡 MED | Open | `domain/models.py:30` vs `data/provenance.py:27` | 18 | Two `ConfidenceLevel` enums with the same name exist in different modules |
| ISSUE-22 | 🟢 LOW | Open | `api/routers/enrichment_single.py:108` | 18 | Deprecated Pydantic v2 `.dict()` method used in API cache path |
| ISSUE-23 | 🔴 HIGH | Open | `data/patent_client.py:33-54` | 17 | `search_company_patents()` calls async sub-functions without `await`; always raises `AttributeError` |
| ISSUE-24 | 🔴 HIGH | Open | `adapters/enrichment/patents_unified.py:66,97,134` | 17 | `PatentsUnifiedAdapter` is entirely non-functional due to ISSUE-23 |
| ISSUE-25 | 🟡 MED | Open | `data/patent_client.py:202-203` | 17 | `_search_duckduckgo()` in `patent_client.py` does not check HTTP status before parsing |
| ISSUE-26 | 🟡 MED | Open | `analytics/workflows.py:30-41` | 17 | `BatchScoreMarketWorkflow` is missing Temporal `@workflow.defn` and `@workflow.run` decorators |
| ISSUE-27 | 🟡 MED | Open | `research/ai_research_orchestrator.py:371` | 17 | `ContentExtractorAgent.http` (httpx.AsyncClient) is created in `__init__` and never closed |
| ISSUE-28 | 🟡 MED | Open | `research/ai_research_orchestrator.py:183,216` | 17 | `WebSearchAgent.cache` is an unbounded in-memory dict with no eviction policy |
| ISSUE-29 | 🟡 MED | Open | `research/ai_research_orchestrator.py:553-616` | 17 | `DataValidatorAgent` validation bounds are unit-agnostic; revenue-per-employee check implicitly assumes millions |
| ISSUE-30 | 🟡 MED | Open | `agents/github/client.py:80-81` | 17 | `GitHubClient.fetch_file()` silently swallows all exceptions with no logging |
| ISSUE-31 | 🟢 LOW | Open | `agents/github/search.py:56` | 17 | `GitHubOrgSearcher.fetch_repos()` silently truncates at 100 regardless of `max_repos` parameter |
| ISSUE-32 | 🟡 MED | Open | `data/eneve_enrichment_integration.py:299-328` | 17 | `EneveEnricher._merge_enrichment()` mutates the caller's input dict in-place |
| ISSUE-33 | 🟡 MED | Open | `data/eneve_enrichment_integration.py:310` | 17 | `EneveEnricher.data_quality_score` is a fabricated metric based solely on source count |
| ISSUE-34 | 🟡 MED | Open | `agents/web_search_agent.py:145-167` | 16 | `WebSearchAgent._api_search_news()` contains unreachable dead code with undefined `requests` reference |
| ISSUE-35 | 🔴 HIGH | Open | `agents/companies_house_agent.py:138,182,224` | 16 | `CompaniesHouseAgent` uses `requests.get()` in three methods without importing `requests` |
| ISSUE-36 | 🔴 HIGH | Open | `agents/companies_house_agent.py:114-121` | 16 | `CompaniesHouseAgent` async methods called via `asyncio.to_thread` return coroutines instead of results |
| ISSUE-37 | 🔴 HIGH | Open | `agents/coordinator_agent.py:23-28` | 16 | CLOSED (False Positive) |
| ISSUE-38 | 🔴 HIGH | Open | `agents/coordinator_agent.py:135-148` | 16 | `CoordinatorAgent.analyze_company()` constructs `AgentTaskResult` with wrong fields, causing `ValidationError` |
| ISSUE-39 | 🟡 MED | Open | `core/production_hardening.py:111,125` | 16 | `ResponseCache` uses deprecated `datetime.utcnow()`, will break on Python 3.13 |
| ISSUE-40 | 🔴 HIGH | Open | `api/middleware/logging.py:168-186` | 15 | ADDENDUM: Middleware ordering confirmed; `ErrorLoggingMiddleware` is outermost wrapper affecting 100% of 4xx/5xx responses |
| ISSUE-41 | 🟡 MED | Open | `api/middleware/rate_limit.py:50` | 15 | `get_rate_limit_for_path()` operator precedence bug neutralizes trailing-slash guard; exact-path routes match as prefixes |
| ISSUE-42 | 🟡 MED | Open | `api/middleware/security.py:61-62` | 15 | `AuthenticationMiddleware` bypasses auth for any URL starting with `/companies` or `/enrichment`; no path separator check |
| ISSUE-43 | — | ❌ CLOSED false positive | `—` | 15 | CLOSED (False Positive) |
| ISSUE-44 | 🔴 HIGH | Open | `llm/structured_client.py:113` | 15 | `StructuredLLMClient.extract()` passes `temperature` kwarg to `EnhancedLLMClient.generate()` which has no such parameter; `TypeError` on every call |
| ISSUE-45 | 🟡 MED | Open | `llm/enhanced_client.py:114-115` | 15 | `EnhancedLLMClient.generate()` returns `None` silently after all providers fail; callers receive no exception signal |
| ISSUE-46 | 🟢 LOW | Open | `llm/query/ollama.py:67-68` | 15 | `OllamaQuerier.query()` uses bare `except Exception: raise` without any diagnostic logging |
| ISSUE-47 | 🟡 MED | Open | `api/routers/async_jobs.py:130,173` | 15 | `async_jobs.py` calls `celery_app.send_task()` synchronously in async handlers; blocks the event loop under broker latency |
| ISSUE-48 | 🔴 HIGH | Open | `application/enrichment_pipeline.py:170-174` | 14 | DEEPENED: `_merge()` checks for `.records` and `.data` — attributes from old `RawDataSource` schema; both branches unreachable for all current `RawDataSource` objects; `_merge()` ALWAYS returns empty `AggregatedDataRecord` |
| ISSUE-49 | 🔴 HIGH | Open | `website_unified`, `news_unified`, `funding_unified`, `web_search_unified`, `linkedin_unified` | 13 | All `BaseRefreshConnector` unified adapters construct `RawDataSource` with wrong field names; `raw_content` (required, no default) never provided; every `enrich()` call raises `ValidationError` |
| ISSUE-50 | 🟡 MED | Open | `research/evidence.py:23` | 12 | `research/evidence.py` uses `logger` that is never imported; exception handler raises `NameError` |
| ISSUE-51 | 🔴 HIGH | Open | `analytics/signals/extractors.py:44-83+` | 12 | `GitHubSignalExtractor` (and all `SignalExtractor` subclasses) instantiate `Signal` with nonexistent fields; `Pydantic ValidationError` on every `extract()` call |
| ISSUE-52 | 🟡 MED | Open | `api/routers/export.py:57-58, 161-162` | 12 | `GET /export/excel` and `GET /export/llm-search` silently ignore their advertised query parameters (`include_charts`, `include_reasoning`) |
| ISSUE-53 | 🔴 HIGH | Open | `api/routers/scoring.py:269` | 12 | `GET /scoring/stats` crashes with `AttributeError` for every company; `company.tier.value` called on a nullable `String` ORM column |
| ISSUE-54 | 🟢 LOW | Open | `monitoring/sla.py`; `exporters/pdf.py` | 12 | `datetime.utcnow()` used in production data structures and monitoring reports (deprecated since Python 3.12) |
| ISSUE-55 | 🟡 MED | Open | `infrastructure/company_repository.py:192-212, 244-267` | 11 | Dead code blocks after `return` in `CompanyRepository.search()` and `CompanyRepository.filter_by()` — merge artifact leaves second, incompatible implementation unreachable |
| ISSUE-56 | 🟡 MED | Open | `research/sources.py:27` | 11 | `research/sources.py:canonicalize_url()` uses `logger` that is never imported; `NameError` when URL parse exception fires |
| ISSUE-57 | 🟢 LOW | Open | `infrastructure/enrichment_repositories.py:158` | 11 | `EnrichmentCacheRepository.get_cache_stats()` discards the result of `datetime.now(timezone.utc)` — dead computation |
| ISSUE-58 | 🟡 MED | Open | `infrastructure/cache.py:41-50` | 11 | `CacheManager.__init__()` sets `self.available = True` before any connectivity check; Redis server failures are not detected at construction time; in-memory fallback is never activated for server-down scenarios |
| ISSUE-59 | 🔴 HIGH | Open | `api/routers/health.py:30,33,37,41` | 10 | `GET /health` crashes on every call: `status` local variable shadows the FastAPI `status` module; `AttributeError: 'str' object has no attribute 'value'` |
| ISSUE-60 | 🔴 HIGH | Open | `api/routers/export.py:22-30` | 10 | `_run_excel_export()` background task calls `async repo.get_all()` without `await` in a sync function; always yields coroutine object instead of data; export always silently fails |
| ISSUE-61 | 🔴 HIGH | Open | `infrastructure/batch_processor.py:147-148` | 9 | `infrastructure/batch_processor.py` uses `Company` in type annotations without importing it; `NameError` at module load time |
| ISSUE-62 | 🟡 MED | Open | `adapters/enrichment/linkedin_unified.py:31-37` | 9 | `LinkedInUnifiedAdapter.__init__()` accepts `db_manager=None` and passes `None` to `BaseRefreshConnector` which calls `self.db_manager.get_session()` unconditionally; `AttributeError` at first use |
| ISSUE-63 | 🟢 LOW | Open | `monitoring/metrics.py:279, 358` | 8 | `asyncio` imported mid-file at line 358 in `monitoring/metrics.py`; used inside function body at line 279 |
| ISSUE-64 | 🟢 LOW | Open | `analytics/confidence_weighting.py:51` | 7 | Redundant condition in `get_average_confidence()` |
| ISSUE-65 | 🟡 MED | Open | `monitoring/continuous_monitor.py:71` | 7 | `ContinuousMonitor` unconditionally `await`s callback; `TypeError` with sync callables, silently swallowed |
| ISSUE-66 | 🟡 MED | Open | `analytics/equity_analysis.py:102-104` | 7 | `float("nan")` in `EquityResult` causes JSON `ValueError`; NaN comparisons misclassify deals |
| ISSUE-67 | 🟢 LOW | Open | `monitoring/errors.py:153` | 7 | `traceback.format_exc()` captures wrong exception context; fingerprints collide |
| ISSUE-68 | 🔴 HIGH | Open | `data/connectors/github_connector.py:64,104,149` | 6 | `GitHubConnector` uses `requests.get()` at 3 call sites; `requests` never imported; all methods silently return `[]` |
| ISSUE-69 | 🟡 MED | Open | `data/enrichment_types.py:14-20` | 6 | `EnrichableCompany` Protocol has 3 duplicate attribute declarations |
| ISSUE-70 | 🟡 MED | Open | `data/company_research.py:190` | 5 | `company_research.py` concatenates `None` country with string city → `TypeError`; outer handler silently returns bare object |
| ISSUE-71 | 🟢 LOW | Open | `exporters/markdown/market.py:42-53` | 4 | Duplicate `tier_counts` computation in `market.py`; first result discarded |
| ISSUE-72 | 🟢 LOW | Open | `exporters/excel/utils.py:130-131` | 4 | Silent `except Exception: pass` in `auto_adjust_columns()` |
| ISSUE-73 | 🔴 HIGH | Open | `exporters/llm.py:77-82` | 3 | `LLMReportEnhancer.is_available()` uses wrong dict key (always `False`) + `RuntimeError` inside async event loop |
| ISSUE-74 | 🟡 MED | Open | `evidence/service.py:211` → `evidence/repositories/claim.py:116` | 2 | `EvidenceService.get_claims()` passes `ClaimStatus` enum where `str` expected; status filter silently returns empty list |
| ISSUE-75 | 🟢 LOW | Open | `evidence/vector_store.py:62` | 2 | `EvidenceVectorStore.init_collection()` calls `self.client` without null-check; `AttributeError` if `connect()` not called |
| ISSUE-76 | 🟢 LOW | Open | `utils/context.py:101-118` | 1 | `with_context` decorator resets context before async body executes; latent defect — decorator is never used in codebase |
| ISSUE-77 | 🔴 HIGH | Open | `intelligence/protocol_mapper.py:233–236` | 1 | `protocol_mapper.py` fabricates protocol presence when none detected; `pass` before assignment is dead code (HIGH) |
| ISSUE-78 | 🔴 HIGH | Open | `intelligence/genealogy_analyzer.py:319,331` | 1 | `genealogy_analyzer.py` regex word-boundary anchors broken by double-backslash in raw f-string; all ownership detection silently returns empty (HIGH) |
| ISSUE-79 | 🔴 HIGH | Open | `intelligence/financial_report_generator.py:392–410` | 1 | `BatchFinancialReportGenerator.generate_with_narratives()` calls private methods that only exist on `FinancialGrowthReportGenerator`; `AttributeError` on every call (HIGH) |
| ISSUE-80 | 🔴 HIGH | Open | `intelligence/genealogy_report_generator.py:222` | 1 | `BatchGenealogyReportGenerator.generate_with_narratives()` calls private methods that only exist on `GenealogyReportGenerator`; `AttributeError` on every call (HIGH) |
| ISSUE-81 | 🔴 HIGH | Open | `intelligence/protocol_report_generator.py:185` | 1 | `BatchProtocolReportGenerator.generate_with_narratives()` calls private methods that only exist on `ProtocolReportGenerator`; `AttributeError` on every call (HIGH) |
| ISSUE-82 | 🟡 MED | Open | `data/connectors/lookup_strategies/opencorporates.py:76–77`, `openfigi.py:84–85` | 1 | `OpenCorporatesStrategy` and `OpenFIGIStrategy` return source-prefixed confidence keys; `_merge_results()` reads field-prefixed keys; confidence scoring silently falls back to 0.5 for both strategies (MED) |
| ISSUE-83 | 🟡 MED | Open | `data/connectors/lookup_strategies/opencorporates.py:29,48`, `openfigi.py:30,49` | 1 | `OpenCorporatesStrategy.lookup()` and `OpenFIGIStrategy.lookup()` are `async def` but call `requests.get/post` synchronously; blocks the event loop on every lookup (MED) |
| ISSUE-84 | 🔴 HIGH | Open | `data/interpolation.py:88–98` | 1 | `RevenueInterpolator` divides by zero when timeline contains duplicate years; `ZeroDivisionError` on interpolation (HIGH) |
| ISSUE-85 | 🔴 HIGH | Open | `data/unified/enrichment.py:110,373` | 1 | `fill_identifiers_from_lookup()` and `attach_news_signals()` call `asyncio.run()` from within running async event loop; `RuntimeError` on every enrichment API call (HIGH) |
| ISSUE-86 | 🔴 HIGH | Open | `security/auth.py:430–434` | 1 | `security/auth.py` `create_refresh_token()` uses `timezone.utc` without importing `timezone`; `NameError` on every refresh token creation (HIGH) |
| ISSUE-87 | 🔴 HIGH | Open | `infrastructure/connectors/sec_edgar_refresh.py:39` | 1 | `sec_edgar_refresh.py` `fetch_facts()` dereferences `end_date.year` and `start_date.year` which are typed `Optional[datetime]`; `AttributeError` when called without date parameters (HIGH) |
| ISSUE-88 | 🔴 HIGH | Open | `tenant/services.py:94` | 1 | `tenant/services.py` awaits `session.delete()` which is synchronous; `TypeError` on company deletion (HIGH) |
| ISSUE-89 | 🟡 MED | Open | `monitoring/sla.py:216` | 1 | `sla.py` `generate_monthly_report()` calls `asyncio.run()` from sync wrapper that is called from async context; `RuntimeError` (MED) |
| ISSUE-90 | 🟡 MED | Open | `infrastructure/repositories.py:274–375` | 1 | `infrastructure/repositories.py` `ReleaseGateAuditRepository` contains three copy-pasted `FactRepository` methods; wrong class, wrong semantics (MED) |
| ISSUE-91 | 🟡 MED | Open | `intelligence/projection_engine.py:249` | 1 | `intelligence/projection_engine.py` uses falsy check on `growth_rate`; zero-percent growth treated as missing data (MED) |
| ISSUE-92 | 🟡 MED | Open | `analytics/classification.py:71` | 1 | `analytics/classification.py` boundary certainty zones check wrong score ranges; actual Lead/Salt boundary at 4.5 not covered (MED) |
| ISSUE-93 | 🟢 LOW | Open | `data/unified/error_tracking.py:49` | 1 | `data/unified/error_tracking.py` `categorize_error()` converts error to lowercase but discards the result; `error` parameter is effectively unused (LOW) |
| ISSUE-94 | 🔴 HIGH | Open | `data/data_quality.py` | 1 | `data/data_quality.py` does not exist — `ModuleNotFoundError` on import (HIGH) |
| ISSUE-95 | 🔴 HIGH | Open | `data/normalization/currency.py` etc.` | 1 | Four `normalization/` files missing — `ModuleNotFoundError` on import (HIGH) |
| ISSUE-96 | 🔴 HIGH | Open | `data/benchmarks.py:109,352` | 1 | `benchmarks.py` uses `T` before definition; `T` defined as `Any` not `TypeVar` (HIGH) |
| ISSUE-97 | 🔴 HIGH | Open | `data/eneve_enrichment.py:190` | 1 | `eneve_enrichment.py` accesses `.funding` — field is `.funding_raised` (HIGH) |
| ISSUE-98 | 🔴 HIGH | Open | `data/eneve_enrichment.py:153` vs `enrichment_validators.py:70` | 1 | Growth rate scale mismatch between `eneve_enrichment.py` and `enrichment_validators.py` (HIGH) |
| ISSUE-99 | 🟡 MED | Open | `data/fetchers.py:192` | 1 | `fetchers.py` silently returns unconverted `amount` when exchange rate unavailable (MED) |
| ISSUE-100 | 🟡 MED | Open | `data/fetchers.py:113` | 1 | `fetchers.py` `0.0` previous_close treated as falsy — silently returns `0` change_pct (MED) |
| ISSUE-101 | 🟡 MED | Open | `data/enrichment_service.py:291–304` | 1 | `enrichment_service.py` three `_enrich_from_*` methods are unimplemented stubs (MED) |
| ISSUE-102 | 🟡 MED | Open | `data/error_logging.py:188` | 1 | `error_logging.py` `ErrorSampler.should_log()` raises `ZeroDivisionError` when `sample_rate=0` (MED) |
| ISSUE-103 | 🟡 MED | Open | `data/conflict_resolution.py:258` | 1 | `conflict_resolution.py` `StringResolver` reports `strategy_used=CONCATENATE` when not concatenating (MED) |
| ISSUE-104 | 🟢 LOW | Open | `data/fetchers.py:122,166` + signal detectors` | 1 | Signal detectors and `fetchers.py` use naive `datetime.now()` mixed with aware datetimes (LOW) |
| ISSUE-105 | 🔴 HIGH | Open | `agents/workflow_nodes/process_raw.py:36` | 1 | `process_raw.py` constructs `RawDataSource` with ~7 non-existent field names (HIGH) |
| ISSUE-106 | 🔴 HIGH | Open | `agents/workflow_nodes/logic_fusion.py:35` | 1 | `logic_fusion.py` constructs `AggregatedFact` with non-existent fields (HIGH) |
| ISSUE-107 | 🔴 HIGH | Open | `agents/workflow_nodes/extract_signals.py:62` | 1 | `extract_signals.py` constructs `SignalExtraction` with 4 non-existent fields (HIGH) |
| ISSUE-108 | 🔴 HIGH | Open | `agents/coordinator_agent.py:149` | 1 | `coordinator_agent.py` accesses `result.signals` — field does not exist on `AgentTaskResult` (HIGH) |
| ISSUE-109 | 🔴 HIGH | Open | `extractors/batch/processor.py:247` | 1 | `batch/processor.py` calls `asyncio.run()` inside sync method called from async pipeline (HIGH) |
| ISSUE-110 | 🔴 HIGH | Open | `extractors/markdown_extractor.py:151–187` | 1 | `markdown_extractor.py` constructs `Company` and `FinancialMetric` with multiple non-existent fields (HIGH) |
| ISSUE-111 | 🔴 HIGH | Open | `extractors/batch/processor.py:69–133` | 1 | `batch/processor.py` `_merge_company_profiles` accesses non-existent `Company` fields throughout (HIGH) |
| ISSUE-112 | 🔴 HIGH | Open | `extractors/batch/processor.py:169` | 1 | `batch/processor.py` `ProvenanceValidator.validate` accesses `profile.financial_metrics` (HIGH) |
| ISSUE-113 | 🟡 MED | Open | `research/pipeline_stages.py:512` | 1 | `ExportStage._run_async` silently performs `GatherStage` work; all export logic is skipped (MED) |
| ISSUE-114 | 🟡 MED | Open | `research/pipeline_stages.py:189` | 1 | `GatherStage` re-runs full discovery instead of reading `context.candidates` (MED) |
| ISSUE-115 | 🟢 LOW | Open | `research/pipeline_async.py:162` | 1 | `pipeline_async.py` sync alias for async function — callers get unawaited coroutine (LOW) |
| ISSUE-116 | 🟢 LOW | Open | `domain/models.py:145–223` | 1 | `domain/models.py` `Company` re-declares `last_updated`, `data_source`, `source_links` (LOW) |
| ISSUE-117 | 🔴 HIGH | Open | `infrastructure/connectors/sec_edgar_refresh.py:131` | 1 | `sec_edgar_refresh.py` `.session()` does not exist on `DatabaseManager` — `AttributeError` (HIGH) |
| ISSUE-118 | 🔴 HIGH | Open | `infrastructure/connectors/sec_edgar_refresh.py:131–141` | 1 | `sec_edgar_refresh.py` raw string SQL without `text()` — `ObjectNotExecutableError` (HIGH) |
| ISSUE-119 | 🔴 HIGH | Open | `infrastructure/connectors/companies_house_refresh.py:129` | 1 | `companies_house_refresh.py` `.session()` and raw SQL — identical crash (HIGH) |
| ISSUE-120 | 🔴 HIGH | Open | `infrastructure/connectors/github_refresh.py:210` | 1 | `github_refresh.py` `.session()` and raw SQL — identical crash (HIGH) |
| ISSUE-121 | 🔴 HIGH | Open | `infrastructure/connectors/news_signal_refresh.py:116` | 1 | `news_signal_refresh.py` `.session()` and raw SQL — identical crash (HIGH) |
| ISSUE-122 | 🔴 HIGH | Open | `infrastructure/connectors/news_signal_refresh.py:63` | 1 | `news_signal_refresh.py` calls `.get()` on `Signal` dataclass — `AttributeError` drops all signals (HIGH) |
| ISSUE-123 | 🔴 HIGH | Open | `data/connectors/github_connector.py:64,104,149` | 1 | `github_connector.py` blocking sync `httpx.get()` inside `async def` methods (HIGH) |
| ISSUE-124 | 🔴 HIGH | Open | `infrastructure/query_cache.py:13` | 1 | `query_cache.py` imports `get_cache` which does not exist — `ImportError` at module load (HIGH) |
| ISSUE-125 | 🔴 HIGH | Open | `infrastructure/query_cache.py:75,85` | 1 | `query_cache.py` calls `.get_sync()` / `.set_sync()` — methods do not exist on `CacheManager` (HIGH) |
| ISSUE-126 | 🔴 HIGH | Open | `infrastructure/test_cleanup.py:72,101` | 1 | `test_cleanup.py` calls `.query()` on `AsyncSession` — not supported in SQLAlchemy 2.x (HIGH) |
| ISSUE-127 | 🔴 HIGH | Open | `infrastructure/search.py:101–108` | 1 | `search.py` uses Python `+` on SQLAlchemy expression objects for `to_tsvector` — malformed SQL (HIGH) |
| ISSUE-128 | 🔴 HIGH | Open | `infrastructure/database_service.py:68` | 1 | `database_service.py` passes `company_id` to `SignalRecord` — field does not exist (HIGH) |
| ISSUE-129 | 🔴 HIGH | Open | `infrastructure/database_service.py:98` | 1 | `database_service.py` passes `market_segment` to `MarketSnapshot` — field does not exist (HIGH) |
| ISSUE-130 | 🔴 HIGH | Open | `infrastructure/database_service.py:125` | 1 | `database_service.py` passes `scoring_timestamp` to `AuditTrailRecord` — field does not exist (HIGH) |
| ISSUE-131 | 🔴 HIGH | Open | `infrastructure/db_router.py:109` | 1 | `db_router.py` `_primary_engine` may be `None` — `AsyncSession(None)` raises `TypeError` (HIGH) |
| ISSUE-132 | 🟡 MED | Open | `infrastructure/vector_store.py:50` | 1 | `vector_store.py` `func.uuid_generate_v4()` evaluated once at class definition — all rows share same UUID (MED) |
| ISSUE-133 | 🟡 MED | Open | `infrastructure/vector_store.py:33` | 1 | `vector_store.py` isolated `declarative_base()` — `EmbeddingRecord` table never created at startup (MED) |
| ISSUE-134 | 🟡 MED | Open | `infrastructure/cache_protocol.py:52` | 1 | `cache_protocol.py` declares `clear()` but `CacheManager` implements `clear_pattern()` — protocol broken (MED) |
| ISSUE-135 | 🟡 MED | Open | `connectors/registry.py:12–23` | 1 | `connectors/registry.py` all six wildcard imports duplicated — all subpackage `__init__` modules execute twice (MED) |
| ISSUE-136 | 🟡 MED | Open | `connectors/registry.py:249–258` | 1 | `registry.py` `TrustpilotConnector` registered twice — second silently overwrites first (MED) |
| ISSUE-137 | 🔴 HIGH | Open | `connectors/financial/__init__.py:24`, `extra.py:20`, `sec_edgar.py:14` | 1 | `financial/__init__.py` three separate `SECEdgarConnector` definitions; class identity non-deterministic (HIGH) |
| ISSUE-138 | 🔴 HIGH | Open | `connectors/financial/extra.py:71` vs `opencorporates.py:14` | 1 | `financial/extra.py` and `financial/opencorporates.py` duplicate `OpenCorporatesConnector` with schema field mismatch (HIGH) |
| ISSUE-139 | 🔴 HIGH | Open | `connectors/product/stackoverflow.py:102` | 1 | `product/stackoverflow.py` `datetime.fromtimestamp(None)` when API returns explicit null (HIGH) |
| ISSUE-140 | 🔴 HIGH | Open | `connectors/social/reddit.py:108` | 1 | `social/reddit.py` same `datetime.fromtimestamp(None)` crash pattern (HIGH) |
| ISSUE-141 | 🔴 HIGH | Open | `connectors/financial/yahoo_finance.py:29,40` | 1 | `financial/yahoo_finance.py` and `financial/__init__.py` blocking sync `yfinance` calls inside `async def` methods (HIGH) |
| ISSUE-142 | 🟡 MED | Open | `connectors/financial/__init__.py:17` | 1 | `financial/__init__.py` imports `pandas` unconditionally — `ModuleNotFoundError` if not installed (MED) |
| ISSUE-143 | 🟡 MED | Open | `connectors/product/appstore.py:87` | 1 | `product/appstore.py` `get_by_id()` calls `response.json()` on `text/javascript` content-type (MED) |
| ISSUE-144 | 🔴 HIGH | Open | `core/health_checks/redis.py:34` | 1 | `core/health_checks/redis.py` accesses `settings.redis_url` — field absent from `Settings` (HIGH) |
| ISSUE-145 | 🔴 HIGH | Open | `celery_context.py:17` | 1 | `celery_context.py` `headers=None` subscript raises `TypeError` when tasks have context data (HIGH) |
| ISSUE-146 | 🔴 HIGH | Open | `core/health_checks/database.py:35` | 1 | `core/health_checks/database.py` missing `await` on `init_async()` — engine always `None` (HIGH) |
| ISSUE-147 | 🟡 MED | Open | `infrastructure/refresh.py:119` | 1 | `infrastructure/refresh.py` naive `datetime.now()` compared to timezone-aware datetime — `TypeError` (MED) |
| ISSUE-148 | 🟡 MED | Open | `cli.py:252–254` | 1 | `cli.py` accesses `p1.financials.revenue` without None guard — `AttributeError` uncaught (MED) |
| ISSUE-149 | 🟡 MED | Open | `core/coverage_dashboard.py:167` | 1 | `core/coverage_dashboard.py` wrong field key `executed_lines` returns a list — `TypeError` in division (MED) |
| ISSUE-150 | 🟡 MED | Open | `data/enrichment/policies/decisions.py:9` | 1 | `data/enrichment/policies/decisions.py` wrong `TYPE_CHECKING` import path for `EnrichableCompany` (MED) |
| ISSUE-151 | 🔴 HIGH | Open | `intelligence/protocol_mapper.py:236` | 1 | `intelligence/protocol_mapper.py` unconditional mutation sets first protocol active — `IndexError` if empty (HIGH) |
| ISSUE-152 | 🔴 HIGH | Open | `intelligence/financial_report_generator.py:392` | 1 | `intelligence/financial_report_generator.py` `BatchFinancialReportGenerator` calls methods it does not inherit (HIGH) |
| ISSUE-153 | 🔴 HIGH | Open | `intelligence/genealogy_report_generator.py:207` | 1 | `intelligence/genealogy_report_generator.py` `BatchGenealogyReportGenerator` calls methods it does not inherit (HIGH) |
| ISSUE-154 | 🔴 HIGH | Open | `intelligence/protocol_report_generator.py:154` | 1 | `intelligence/protocol_report_generator.py` `BatchProtocolReportGenerator` calls methods it does not inherit (HIGH) |
| ISSUE-155 | 🔴 HIGH | Open | `intelligence/deep_analyzer.py:761` | 1 | `intelligence/deep_analyzer.py` `generate_from_dict` returns `dict` instead of declared `DeepAnalysisReport` (HIGH) |
| ISSUE-156 | 🔴 HIGH | Open | `intelligence/genealogy_analyzer.py:319,331` | 1 | `intelligence/genealogy_analyzer.py` regex uses `\\b` in raw f-string — word boundary never matches (HIGH) |
| ISSUE-157 | 🔴 HIGH | Open | `monitoring/errors.py:193` | 1 | `monitoring/errors.py` `track_error` assigns to `existing.last_seen` — field does not exist on `ErrorRecord` (HIGH) |
| ISSUE-158 | 🔴 HIGH | Open | `monitoring/profiling/dashboard.py:23` | 1 | `monitoring/profiling/dashboard.py` uses `profiler` module as singleton instance — all attribute accesses fail (HIGH) |
| ISSUE-159 | 🔴 HIGH | Open | `evidence/repositories/claim.py:12` | 1 | `evidence/repositories/claim.py` imports `SourceRepository` from non-existent `source.py` — `ModuleNotFoundError` (HIGH) |
| ISSUE-160 | 🔴 HIGH | Open | `evidence/repositories/company.py:54–58` | 1 | `evidence/repositories/company.py` Cypher query uses wrong enum values `'VERIFIED'`/`'DISPUTED'` — counts always zero (HIGH) |
| ISSUE-161 | 🔴 HIGH | Open | `monitoring/llm_tracker.py:357` | 1 | `monitoring/llm_tracker.py` creates new `LLMTracker` instance per decorated function — global aggregation broken (HIGH) |
| ISSUE-162 | 🔴 HIGH | Open | `evidence/models.py:93,112` | 1 | `evidence/models.py` uses deprecated `datetime.utcnow` — naive datetimes cause `TypeError` on comparison (HIGH) |
| ISSUE-163 | 🟢 LOW | Open | `monitoring/continuous_monitor.py:232` | 1 | `monitoring/continuous_monitor.py` uses `timedelta.days` for fractional-day comparison — companies skipped too long (LOW) |
| ISSUE-164 | 🟢 LOW | Open | `monitoring/business_metrics.py:73` | 1 | `monitoring/business_metrics.py` deprecated `datetime.utcnow` default (LOW) |
| ISSUE-165 | 🔴 HIGH | Open | `presentation/adaptive_templates.py:175` | 1 | `presentation/adaptive_templates.py` `:.0f` format on `None` `revenue_per_employee_eur_k` — `TypeError` (HIGH) |
| ISSUE-166 | 🔴 HIGH | Open | `validation/financial_rules.py:10,51` | 1 | `validation/financial_rules.py` `growth_rate_max: 10.0` flags all growth > 10% as unrealistic (HIGH) |
| ISSUE-167 | 🟡 MED | Open | `presentation/data_quality_indicators.py:92` | 1 | `presentation/data_quality_indicators.py` unguarded `company.financials.revenue` chain when `financials=None` (MED) |
| ISSUE-168 | 🟡 MED | Open | `presentation/data_quality_indicators.py:116` | 1 | `presentation/data_quality_indicators.py` `IndexError` when `metric_sources[key]` is empty list (MED) |
| ISSUE-169 | 🟡 MED | Open | `analytics/tier_classification.py:128` | 1 | `analytics/tier_classification.py` wrong sub-tier code `"Tier 4E"` instead of `"4E"` (MED) |
| ISSUE-170 | 🟡 MED | Open | `worker/refresh_tasks.py:87` | 1 | `worker/refresh_tasks.py` `asyncio.run()` inside Celery task crashes with eventlet/gevent or async test harness (MED) |
| ISSUE-171 | 🟢 LOW | Open | `analytics/data_quality.py:91` | 1 | `analytics/data_quality.py` zero numeric values reported as missing (LOW) |
| ISSUE-172 | 🟢 LOW | Open | `analytics/tier_classification.py:160` | 1 | `analytics/tier_classification.py` negative "revenue needed" display for near-threshold companies (LOW) |
| ISSUE-173 | 🔴 HIGH | Open | `utils/async_json.py:54` | 1 | `utils/async_json.py` `json.dumps` with `default=str` passed as misplaced positional arg via `run_in_executor` (HIGH) |
| ISSUE-174 | 🟡 MED | Open | `utils/memory.py:76` | 1 | `utils/memory.py` `async def stream()` annotated as `Generator` instead of `AsyncGenerator` (MED) |
| ISSUE-175 | 🟡 MED | Open | `utils/tracing.py:67` | 1 | `utils/tracing.py` `success` variable unbound if `asyncio.CancelledError` raised — `UnboundLocalError` in `finally` (MED) |
| ISSUE-176 | 🟢 LOW | Open | `llm/health_checker.py:28` | 1 | `llm/health_checker.py` `report_success`/`report_error` reset counters to 1 instead of incrementing (LOW) |
| ISSUE-177 | 🟢 LOW | Open | `llm/optimizations.py:44` | 1 | `llm/optimizations.py` uses deprecated `asyncio.get_event_loop()` inside async context (LOW) |
| ISSUE-178 | 🔴 HIGH | Open | `data/connectors/sec_edgar_connector.py:206,212` | 1 | `data/connectors/sec_edgar_connector.py` second `list(filings)` on exhausted iterator — fallback filing search never works (HIGH) |
| ISSUE-179 | 🔴 HIGH | Open | `data/connectors/lookup_strategies/opencorporates.py:48` | 1 | `lookup_strategies/opencorporates.py` blocking `requests.get` inside `async def` — blocks event loop (HIGH) |
| ISSUE-180 | 🔴 HIGH | Open | `data/connectors/lookup_strategies/openfigi.py:49` | 1 | `lookup_strategies/openfigi.py` blocking `requests.post` inside `async def` — blocks event loop (HIGH) |
| ISSUE-181 | 🔴 HIGH | Open | `data/connectors/lookup_strategies/duckduckgo.py:43` | 1 | `lookup_strategies/duckduckgo.py` sync DDG I/O called from `async def lookup` — blocks event loop (HIGH) |
| ISSUE-182 | 🟢 LOW | Open | `data/connectors/news_signal_detector.py:91` | 1 | `data/connectors/news_signal_detector.py` naive `datetime.now()` for rate-limit reset (LOW) |
| ISSUE-183 | 🔴 HIGH | Open | `api/services/drill_down_service.py:177` | 1 | `api/services/drill_down_service.py` factory calls `DrillDownService()` with no `session` argument — `TypeError` (HIGH) |
| ISSUE-184 | 🟢 LOW | Open | `api/middleware/logging.py:127` | 1 | `api/middleware/logging.py` dead `log_level` variable computed but never used (LOW) |
| ISSUE-185 | 🟢 LOW | Open | `infrastructure/connectors/sec_edgar_refresh.py:57` | 1 | `sec_edgar_refresh.py` quarter-iteration loop always breaks on first iteration — dead code (LOW) |
| ISSUE-186 | 🟡 MED | Open | `infrastructure/connectors/companies_house_refresh.py:109` | 1 | `companies_house_refresh.py` `_filter_delta` `else` clause always fires — delta filter is a no-op (MED) |
| ISSUE-187 | 🟢 LOW | Open | `infrastructure/connectors/github_refresh.py:188` | 1 | `github_refresh.py` duplicate `created_at` in `date_fields` list (LOW) |
| ISSUE-188 | 🔴 HIGH | Open | `infrastructure/connectors/funding_refresh.py:64` | 1 | `funding_refresh.py` `get_funding_data()` is a sync call inside `async def fetch_facts` — blocks event loop (HIGH) |
| ISSUE-189 | 🔴 HIGH | Open | `infrastructure/connectors/funding_refresh.py:99` | 1 | `funding_refresh.py` calls `.get()` on `latest_round` which may be a dataclass — `AttributeError` (HIGH) |
| ISSUE-190 | 🟡 MED | Open | `infrastructure/connectors/funding_refresh.py` | 1 | `funding_refresh.py` missing `_filter_delta` and `_fact_exists` implementations (MED) |
| ISSUE-191 | 🔴 HIGH | Open | `infrastructure/connectors/linkedin_refresh.py:60` | 1 | `linkedin_refresh.py` sync `get_linkedin_data()` blocks event loop (HIGH) |
| ISSUE-192 | 🔴 HIGH | Open | `infrastructure/connectors/linkedin_refresh.py:67` | 1 | `linkedin_refresh.py` no None guard on `data` before attribute access — `AttributeError` (HIGH) |
| ISSUE-193 | 🟡 MED | Open | `infrastructure/connectors/linkedin_refresh.py` | 1 | `linkedin_refresh.py` missing `_filter_delta` and `_fact_exists` (MED) |
| ISSUE-194 | 🔴 HIGH | Open | `infrastructure/connectors/global_market_refresh.py:60` | 1 | `global_market_refresh.py` sync `get_stock_data()` blocks event loop (HIGH) |
| ISSUE-195 | 🟡 MED | Open | `infrastructure/connectors/global_market_refresh.py:82` | 1 | `global_market_refresh.py` `.value` on `source_currency` which may be `None` (MED) |
| ISSUE-196 | 🟡 MED | Open | `infrastructure/connectors/global_market_refresh.py` | 1 | `global_market_refresh.py` missing `_filter_delta` and `_fact_exists` (MED) |
| ISSUE-197 | 🔴 HIGH | Open | `infrastructure/connectors/patents_refresh.py:58` | 1 | `patents_refresh.py` sync `search_company_patents()` blocks event loop (HIGH) |
| ISSUE-198 | 🟡 MED | Open | `infrastructure/connectors/patents_refresh.py` | 1 | `patents_refresh.py` missing `_filter_delta` and `_fact_exists` (MED) |
| ISSUE-199 | 🔴 HIGH | Open | `infrastructure/connectors/news_refresh.py:68` | 1 | `news_refresh.py` sync `get_news()` blocks event loop (HIGH) |
| ISSUE-200 | 🔴 HIGH | Open | `infrastructure/connectors/news_refresh.py:78` | 1 | `news_refresh.py` no None guard on `coverage` before attribute access (HIGH) |
| ISSUE-201 | 🟡 MED | Open | `infrastructure/connectors/news_refresh.py` | 1 | `news_refresh.py` missing `_filter_delta` and `_fact_exists` (MED) |
| ISSUE-202 | 🟢 LOW | Open | `infrastructure/connectors/web_search_refresh.py:65` | 1 | `web_search_refresh.py` runtime `import` inside loop (LOW) |
| ISSUE-203 | 🟡 MED | Open | `infrastructure/connectors/web_search_refresh.py` | 1 | `web_search_refresh.py` missing `_filter_delta` and `_fact_exists` (MED) |
| ISSUE-204 | 🔴 HIGH | Open | `infrastructure/connectors/website_refresh.py:58` | 1 | `website_refresh.py` `fetch_facts()` unconditionally skips every company — always returns `[]` (HIGH) |
| ISSUE-205 | 🔴 HIGH | Open | `infrastructure/connectors/website_refresh.py:92` | 1 | `website_refresh.py` sync `scrape_company_website()` blocks event loop (HIGH) |
| ISSUE-206 | 🟡 MED | Open | `infrastructure/connectors/website_refresh.py` | 1 | `website_refresh.py` missing `_filter_delta` and `_fact_exists` (MED) |
| ISSUE-207 | 🔴 HIGH | Open | `infrastructure/connectors/yahoo_finance_refresh.py:59` | 1 | `yahoo_finance_refresh.py` sync `researcher.research()` blocks event loop (HIGH) |
| ISSUE-208 | 🟡 MED | Open | `infrastructure/connectors/yahoo_finance_refresh.py:77` | 1 | `yahoo_finance_refresh.py` no None guard on `profile` before attribute access (MED) |
| ISSUE-209 | 🟢 LOW | Open | `infrastructure/query_cache.py:47` | 1 | `infrastructure/query_cache.py` uses MD5 as cache key (LOW) |
| ISSUE-210 | 🟡 MED | Open | `infrastructure/db_router.py:141` | 1 | `infrastructure/db_router.py` `get_write_session` has no rollback on exception (MED) |
| ISSUE-211 | 🔴 HIGH | Open | `infrastructure/vector_store.py:53` | 1 | `infrastructure/vector_store.py` `ARRAY(Float)` column used with pgvector `<=>` operator — query fails (HIGH) |
| ISSUE-212 | 🔴 HIGH | Open | `infrastructure/vector_store.py:58` | 1 | `infrastructure/vector_store.py` IVFFlat index with `vector_cosine_ops` on `ARRAY(Float)` — DDL failure (HIGH) |
| ISSUE-213 | 🟡 MED | Open | `infrastructure/circuit_breaker.py:174` | 1 | `infrastructure/circuit_breaker.py` shared global instances not thread-safe (MED) |
| ISSUE-214 | 🔴 HIGH | Open | `infrastructure/conflict_resolution.py:239` | 1 | `infrastructure/conflict_resolution.py` `datetime > str` comparison raises `TypeError` (HIGH) |
| ISSUE-215 | 🟢 LOW | Open | `infrastructure/db_monitor.py:276` | 1 | `infrastructure/db_monitor.py` `**details` may conflict with loguru reserved parameter names (LOW) |
| ISSUE-216 | 🔴 HIGH | Open | `infrastructure/query_logger.py:26` | 1 | `infrastructure/query_logger.py` DBAPI events not fired on `AsyncEngine` — logger produces zero output in async context (HIGH) |
| ISSUE-217 | 🔴 HIGH | Open | `infrastructure/query_optimizer.py:99` | 1 | `infrastructure/query_optimizer.py` `table.insert()` not valid on ORM model class (HIGH) |
| ISSUE-218 | 🔴 HIGH | Open | `infrastructure/query_optimizer.py:330` | 1 | `infrastructure/query_optimizer.py` raw SQL string interpolation with unescaped column names — SQL injection risk (HIGH) |
| ISSUE-219 | 🟡 MED | Open | `infrastructure/reconcile_runs.py:138` | 1 | `infrastructure/reconcile_runs.py` possible UUID vs int FK type mismatch for `run_id` (MED) |
| ISSUE-220 | 🔴 HIGH | Open | `infrastructure/research_dual_write.py:83` | 1 | `infrastructure/research_dual_write.py` `session.commit()` called inside savepoint block — corrupts transaction state (HIGH) |
| ISSUE-221 | 🟡 MED | Open | `infrastructure/research_dual_write.py:307` | 1 | `infrastructure/research_dual_write.py` `session.rollback()` after `OperationalError` may itself fail — shadows original error (MED) |
| ISSUE-222 | 🟡 MED | Open | `infrastructure/research_outbox_helpers.py:88` | 1 | `infrastructure/research_outbox_helpers.py` `SQLAlchemyError` and `OSError` classified as terminal instead of retryable (MED) |
| ISSUE-223 | 🟡 MED | Open | `infrastructure/research_persistence.py:59` | 1 | `infrastructure/research_persistence.py` legacy `session.query()` mixed with `session.execute(select(...))` (MED) |
| ISSUE-224 | 🔴 HIGH | Open | `agents/coordinator_agent.py:58` | 1 | `agents/coordinator_agent.py` uses `DataSourceType.WEB_SEARCH` which does not exist — `ValueError` on instantiation (HIGH) |
| ISSUE-225 | 🔴 HIGH | Open | `intelligence/deep_analyzer.py:42` | 1 | `intelligence/deep_analyzer.py` missing `Company` import — `NameError` at class definition time (HIGH) |
| ISSUE-226 | 🔴 HIGH | Open | `evidence/repositories/claim.py:37` | 1 | `evidence/repositories/claim.py` `_extract_domain` method missing — `AttributeError` on every `create()` call (HIGH) |
| ISSUE-227 | 🔴 HIGH | Open | `src/solstein/analytics/completeness.py:188–204` | 0 | `revenue_per_employee_eur_k` and `employee_cagr_3yr` read from `company.financials` — they live on `Company` directly |
| ISSUE-228 | 🟡 MED | Open | `src/solstein/analytics/scoring.py:16–21` | 0 | `CompanyClassification` import ambiguity — only in models package, not flat models.py |
| ISSUE-229 | 🟡 MED | Open | `src/solstein/analytics/scoring.py:240, 243, 310, 328, 384` | 0 | `p.financials.revenue` accessed without guarding `p.financials is None` (multiple sites) |
| ISSUE-230 | 🔴 HIGH | Open | `src/solstein/adapters/enrichment/funding_unified.py:153–162` | 0 | `source_type="funding"` is not a valid `DataSourceType` member — Pydantic `ValidationError` at runtime |
| ISSUE-231 | 🔴 HIGH | Open | `src/solstein/adapters/enrichment/web_search_unified.py:146–163, 169–175` | 0 | `source_type="web_search"` is not a valid `DataSourceType` member — Pydantic `ValidationError` at runtime |
| ISSUE-232 | 🔴 HIGH | Open | `src/solstein/adapters/enrichment/patents_unified.py:71–83` | 0 | `DiscoveryCandidate` constructed with entirely wrong field names |
| ISSUE-233 | 🟢 LOW | Open | `src/solstein/adapters/enrichment/linkedin_unified.py:109`, `news_unified.py:205`, `website_unified.py:155`, `funding_unified.py:156`, `web_search_unified.py:151` | 0 | Naive `datetime.now()` used for `retrieval_timestamp` — all other adapters use `datetime.now(timezone.utc)` |
| ISSUE-234 | 🟡 MED | Open | `src/solstein/analytics/scoring.py:162` | 0 | `profile.financials` passed directly to `GrowthMomentumScorer.score()` — crashes if `None` |
| ISSUE-235 | 🟢 LOW | Open | `src/solstein/analytics/scorers/_shared.py:28–29` | 0 | `asyncio.iscoroutine()` guard misses non-coroutine awaitables |
| ISSUE-236 | 🟡 MED | Open | `src/solstein/api/main.py:103–110` | 0 | Cache warming failure silently swallowed — startup continues with cold cache, no error surfaced |
| ISSUE-237 | 🔴 HIGH | Open | `src/solstein/api/routers/market.py:87–88, 98–99` | 0 | `peer.company_id` and `target.company_id` do not exist — correct field is `.id` |
| ISSUE-238 | 🔴 HIGH | Open | `src/solstein/api/routers/scoring.py:243, 255` | 0 | Unguarded `c.financials.revenue` and `c.financials.growth_rate` — crashes when `financials` is `None` |
| ISSUE-239 | 🔴 HIGH | Open | `src/solstein/api/services/drill_down_service.py:109, 111` and `src/solstein/api/routers/drill_down.py:69` | 0 | `source.id` accessed on `RawDataSource` — field does not exist |
| ISSUE-240 | 🟡 MED | Open | `src/solstein/api/services/drill_down_service.py:148` | 0 | `contradiction_detected` checked instead of `contradictions_detected` (plural) — always empty |
| ISSUE-241 | 🟡 MED | Open | `src/solstein/api/routers/enrichment_single.py:65–88` | 0 | Cache hit detected but ignored — enrichment always re-runs from scratch |
| ISSUE-242 | 🟡 MED | Open | `src/solstein/api/routers/dashboard.py:132–139` | 0 | Tier filter appended after `.limit(n)` — filters an already-truncated result set |
| ISSUE-243 | 🟡 MED | Open | `src/solstein/domain/models.py:393–405` | 0 | `get_data_completeness` does not count `Company.funding` — only checks `FinancialMetric.funding_raised` |
| ISSUE-244 | 🟡 MED | Open | `src/solstein/presentation/data_quality_indicators.py:92–98, 132–135` | 0 | `company.financials.revenue` accessed without `None` guard on `financials` |
| ISSUE-245 | 🟢 LOW | Open | `src/solstein/api/routers/async_jobs.py:91–93` | 0 | `request.client.host` accessed without `None` guard — `AttributeError` when client is `None` |
| ISSUE-246 | 🟢 LOW | Open | `src/solstein/core/scoring_utils.py:99` | 0 | `financials.ai_maturity` checked but `ai_maturity` is on `Company`, not `FinancialMetric` |
| ISSUE-247 | 🟡 MED | Open | `src/solstein/research/pipeline_stages.py:477–575` | 0 | `GatherStage._run_async` is physically indented inside `ExportStage` — becomes an `ExportStage` method |
| ISSUE-248 | 🔴 HIGH | Open | `src/solstein/research/company_builder.py:63` | 0 | Unguarded `int(employees_raw.value)` cast — `ValueError` when value is non-integer string |
| ISSUE-249 | 🔴 HIGH | Open | `src/solstein/research/signals.py:228` | 0 | `ai_strength.value` accessed without guard — `AttributeError` if `ai_strength` is not an `AggregatedFact` |
| ISSUE-250 | 🔴 HIGH | Open | `src/solstein/data/unified/merger.py:27` | 0 | `UnifiedCompany(**json_company.model_dump())` fails validation for stub profiles — `allow_empty_primary=True` excluded from dump |
| ISSUE-251 | 🟡 MED | Open | `src/solstein/data/unified/merger.py:40` | 0 | `tier` comparison: `CompanyTier` enum vs. plain string — spurious conflicts on every merge |
| ISSUE-252 | 🟡 MED | Open | `src/solstein/data/unified/unified.py:14, 28` | 0 | `loguru.logger` immediately overwritten by `stdlib.logging.getLogger` — structured logging silently broken |
| ISSUE-253 | 🟡 MED | Open | `src/solstein/research/gather.py:165–175` | 0 | Fallback `build_company_profile` path has no exception handling — unhandled `ValueError` kills entire batch |
| ISSUE-254 | 🟡 MED | Open | `src/solstein/intelligence/financial_analyzer.py:191` | 0 | `fi.growth_trajectory.value` — `AttributeError` if `fi` was constructed with raw string `"accelerating"` |
| ISSUE-255 | 🟡 MED | Open | `src/solstein/intelligence/financial_models.py:43` | 0 | Shadow `ConfidenceLevel` enum with incompatible values silently accepted where `domain.models.ConfidenceLevel` expected |
| ISSUE-256 | 🟡 MED | Open | `src/solstein/research/pipeline_stages.py:186–210` | 0 | `GatherStage._run` re-calls `discover_companies` instead of reusing `DiscoveryStage` results |
| ISSUE-257 | 🟢 LOW | Open | `src/solstein/api/routers/jobs.py:12–15` | 0 | `APIRouter` instance created twice — second assignment overwrites the first |
| ISSUE-258 | 🔴 HIGH | Open | `src/solstein/infrastructure/connectors/sec_edgar_refresh.py:39` | 0 | `start_date.year` / `end_date.year` accessed when both may be `None` — crashes standard refresh path |
| ISSUE-259 | 🟢 LOW | Open | `` | 0 | Bare `except Exception` in `_filter_delta` includes stale facts on date parse error |
| ISSUE-260 | 🟡 MED | Open | `src/solstein/infrastructure/database_service.py:52–79` | 0 | `save_signal` accepts `company_id` argument but `SignalRecord` may not have that column |
| ISSUE-261 | 🟢 LOW | Open | `src/solstein/infrastructure/repositories.py:249–376` | 0 | `ReleaseGateAuditRepository` duplicates three methods verbatim from `FactRepository` |
| ISSUE-262 | 🟢 LOW | Open | `src/solstein/infrastructure/vector_store.py:50` | 0 | `func.uuid_generate_v4()` as column `default=` evaluated at import time, not per-row |
| ISSUE-263 | 🟡 MED | Open | `src/solstein/infrastructure/research_dual_write.py:357–381` | 0 | `process_outbox` commits run records and outbox status in separate implicit transactions — partial write risk |
| ISSUE-264 | 🔴 HIGH | Open | `src/solstein/evidence/repositories/claim.py:22–23` | 0 | `ClaimRepository.__init__` creates unmanaged Neo4j `Driver` instances for sub-repositories — connection pool leak |
| ISSUE-265 | 🔴 HIGH | Open | `src/solstein/monitoring/business_metrics.py:146` | 0 | `CompanyRecord.ai_data_quality_score` does not exist — column is `ai_score` |
| ISSUE-266 | 🔴 HIGH | Open | `src/solstein/monitoring/business_metrics.py:152` | 0 | `CompanyRecord.enrichment_updated_at` does not exist — column is `last_updated` |
| ISSUE-267 | 🔴 HIGH | Open | `src/solstein/api/routers/enrichment_batch.py:64` | 0 | `status="partial_failure"` rejected by `BatchEnrichmentResponse.validate_status` — correct value is `"partial"` |
| ISSUE-268 | 🟡 MED | Open | `src/solstein/adapters/enrichment/patents_unified.py:19`, `src/solstein/research/discovery.py:10`, `src/solstein/adapters/registry.py:98` | 0 | Static import cycle between `patents_unified`, `research.discovery`, and `adapters.registry` breaks structural tooling assumptions |
| ISSUE-269 | 🟡 MED | Open | `src/solstein/domain/value_objects.py:24,160,165` | 0 | Domain `value_objects` imports analytics scoring constants, coupling core domain rules to the analytics layer |
| ISSUE-270 | 🟡 MED | Open | `src/solstein/infrastructure/research_dual_write.py:17`, `src/solstein/infrastructure/research_persistence.py:14` | 0 | Infrastructure persistence imports URL canonicalization from the higher `research` layer instead of a lower shared utility boundary |
| ISSUE-271 | 🟡 MED | Open | `src/solstein/infrastructure/reconcile_runs.py:12` | 0 | Infrastructure reconciliation imports JSON hashing helper from the higher `research` layer |
