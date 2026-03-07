# 📚 Anti-Patterns Catalog

> **Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

This catalog documents all anti-patterns found in the codebase for reference and training.

---

## ARCHITECTURE Anti-Patterns

### God File
**Severity:** HIGH  
**Location:** `domain/models.py`  
**Description:** File has 817 lines (limit: 500)  
**Recommendation:** Split into multiple modules by responsibility  

---

### Large File
**Severity:** MEDIUM  
**Location:** `research/aggregate.py`  
**Description:** File has 663 lines (target: <500)  
**Recommendation:** Consider splitting large files  

---

### Circular Import
**Severity:** CRITICAL  
**Location:** `Multiple files`  
**Description:** Circular dependencies detected  
**Recommendation:** Refactor to break cycles using interfaces or dependency injection  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `cli_ai_research.py:185`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `cli_ai_research.py:186`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `config.py:324`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `cli.py:252`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `cli.py:253`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `cli.py:312`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `cli.py:313`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `cli.py:344`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `cli.py:351`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `cli.py:374`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `cli.py:375`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `cli.py:407`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `cli.py:415`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `cli.py:425`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `analytics/classification.py:44`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `analytics/classification.py:93`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `analytics/classification.py:156`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `analytics/workflows.py:23`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/web_research_pipeline.py:157`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/repositories.py:78`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/repositories.py:189`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/repositories.py:255`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/repositories.py:261`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/repositories.py:296`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/repositories.py:305`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/repositories.py:325`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/enrichment_service.py:49`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/enrichment_service.py:58`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/enrichment_service.py:67`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/enrichment_service.py:237`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/enrichment_executors.py:39`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/enrichment_executors.py:93`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/enrichment_executors.py:94`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/enrichment_executors.py:200`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/safe_defaults.py:18`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/safe_defaults.py:20`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/safe_defaults.py:21`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/patent_client.py:140`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/patent_client.py:193`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `agents/companies_house_agent.py:23`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `agents/github_agent.py:30`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `domain/value_objects.py:160`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `domain/value_objects.py:165`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `domain/simulation.py:18`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `llm/enhanced_client.py:65`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `llm/provider_strategies.py:49`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `llm/provider_strategies.py:84`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `llm/provider_strategies.py:104`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `llm/provider_strategies.py:124`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `llm/provider_strategies.py:144`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `llm/provider_strategies.py:164`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `llm/provider_strategies.py:184`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `llm/provider_strategies.py:204`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `llm/provider_strategies.py:224`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `llm/provider_strategies.py:245`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `llm/provider_strategies.py:265`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `llm/tracing.py:75`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `llm/tracing.py:131`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `llm/tracing.py:134`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `llm/structured_client.py:67`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `research/pipeline_async.py:74`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `research/company_builder.py:43`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `research/company_builder.py:86`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `research/company_builder.py:103`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `research/company_builder.py:120`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `research/company_builder.py:146`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `research/company_builder.py:168`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `research/pipeline.py:70`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `research/discovery.py:45`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `research/pipeline_stages.py:492`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `research/pipeline_stages.py:526`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `research/gather.py:86`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `research/gather.py:145`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `research/gather.py:146`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `research/gather.py:347`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `tenant/context.py:163`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `tenant/services.py:122`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `api/main.py:95`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `api/main.py:103`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `api/main.py:166`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `monitoring/llm_tracker.py:219`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `monitoring/metrics.py:19`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `monitoring/metrics.py:20`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `monitoring/metrics.py:21`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `monitoring/metrics.py:23`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `monitoring/metrics.py:24`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `monitoring/metrics.py:27`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `monitoring/metrics.py:28`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `monitoring/metrics.py:360`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `monitoring/metrics.py:361`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `monitoring/metrics.py:416`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `monitoring/health.py:279`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `monitoring/errors.py:370`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `core/coverage_dashboard.py:202`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `adapters/instrumented.py:156`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `adapters/registry.py:74`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `adapters/registry.py:75`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `adapters/registry.py:76`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `adapters/registry.py:77`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `adapters/registry.py:91`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `adapters/registry.py:96`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `adapters/registry.py:106`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `adapters/registry.py:107`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `adapters/registry.py:113`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `adapters/registry.py:114`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `adapters/registry.py:120`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `adapters/registry.py:126`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `adapters/registry.py:127`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `adapters/registry.py:128`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `adapters/registry.py:129`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `adapters/registry.py:130`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `adapters/registry.py:131`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `migrations/load_competitor_data.py:143`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `infrastructure/cache_protocol.py:15`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `infrastructure/cache_protocol.py:17`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `infrastructure/reconcile_runs.py:94`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `infrastructure/research_persistence.py:155`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `infrastructure/cache_warming.py:48`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `infrastructure/cache_warming.py:71`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `infrastructure/cache_warming.py:73`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `infrastructure/database.py:184`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `infrastructure/database.py:185`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `infrastructure/database.py:186`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `infrastructure/database.py:192`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `infrastructure/db_router.py:256`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `infrastructure/research_dual_write.py:138`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `infrastructure/unified_registry.py:175`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `infrastructure/unified_registry.py:176`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `infrastructure/unified_registry.py:177`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `infrastructure/unified_registry.py:178`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `infrastructure/unified_registry.py:179`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `infrastructure/unified_registry.py:180`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `infrastructure/unified_registry.py:181`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `infrastructure/unified_registry.py:196`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `infrastructure/unified_registry.py:201`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `infrastructure/unified_registry.py:211`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `infrastructure/unified_registry.py:212`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `infrastructure/unified_registry.py:244`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `infrastructure/search.py:119`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `infrastructure/search.py:184`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `worker/enrichment_tasks.py:52`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `worker/enrichment_tasks.py:132`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `security/auth.py:15`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `security/auth.py:16`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `security/auth.py:17`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `security/auth.py:19`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `security/auth.py:20`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `security/auth.py:22`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `security/auth.py:125`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `security/auth.py:403`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `security/auth.py:405`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `security/auth.py:430`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `security/auth.py:432`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `security/headers.py:74`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `security/headers.py:75`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `evidence/vector_store.py:81`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `evidence/vector_store.py:171`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `evidence/vector_store.py:252`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `evidence/crawler.py:351`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `evidence/service.py:157`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `connectors/financial/__init__.py:310`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `connectors/financial/__init__.py:321`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `connectors/financial/__init__.py:322`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `connectors/financial/__init__.py:329`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `connectors/financial/__init__.py:330`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `connectors/financial/__init__.py:337`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/connectors/sec_edgar_connector.py:65`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/connectors/sec_edgar_connector.py:93`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/connectors/github_connector.py:38`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/connectors/companies_house_connector.py:34`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/connectors/news_signal_detector.py:94`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/converters/company_extractors.py:185`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/unified/merger.py:175`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/unified/sec_edgar_helpers.py:28`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/unified/sec_edgar_helpers.py:55`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/unified/sec_edgar_helpers.py:81`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/unified/sec_edgar_helpers.py:111`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/unified/sec_edgar_helpers.py:152`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/unified/unified.py:35`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/unified/unified.py:36`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/unified/unified.py:37`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/unified/unified.py:190`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/unified/enrichment.py:44`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/unified/enrichment.py:157`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/unified/enrichment.py:166`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/unified/enrichment.py:249`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `data/unified/enrichment.py:299`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `llm/health/checker.py:42`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `llm/health/clients.py:86`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `llm/health/clients.py:95`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `api/schemas/pagination.py:16`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `api/schemas/pagination.py:18`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `api/schemas/pagination.py:20`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `api/routers/health.py:149`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `api/routers/enrichment_audit.py:57`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `api/routers/enrichment_audit.py:80`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `api/middleware/tenant.py:64`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `api/middleware/tenant.py:149`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `api/middleware/tenant.py:150`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `api/middleware/tenant.py:152`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `api/middleware/tenant.py:153`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `api/websocket/manager.py:21`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `api/websocket/manager.py:24`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `api/websocket/manager.py:27`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `core/ports/__init__.py:18`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `core/ports/__init__.py:19`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `core/health_checks/redis.py:30`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `core/health_checks/database.py:28`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `core/health_checks/database.py:30`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `core/health_checks/database.py:31`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `core/health_checks/llm.py:31`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `core/health_checks/configuration.py:26`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `adapters/discovery/web_search.py:31`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `adapters/discovery/web_search.py:34`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `adapters/discovery/competitor_json.py:39`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `adapters/discovery/competitor_json.py:42`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `adapters/enrichment/linkedin.py:36`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `adapters/enrichment/global_market.py:36`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `adapters/enrichment/yahoo_finance.py:36`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `adapters/enrichment/linkedin_unified.py:43`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `adapters/enrichment/patents.py:43`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `adapters/enrichment/funding.py:36`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `adapters/enrichment/web_search_news.py:33`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `adapters/enrichment/funding_unified.py:74`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `adapters/enrichment/funding_unified.py:104`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `adapters/enrichment/website.py:35`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `adapters/enrichment/news.py:37`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `infrastructure/connectors/web_search_refresh.py:65`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `infrastructure/models/infrastructure.py:77`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `exporters/markdown/client.py:53`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `exporters/markdown/client.py:91`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `exporters/markdown/generator.py:61`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `exporters/markdown/generator.py:199`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `exporters/markdown/generator.py:200`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `exporters/excel/utils.py:118`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `exporters/excel/sheets.py:25`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `evidence/repositories/base.py:92`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

### Lazy Import
**Severity:** MEDIUM  
**Location:** `evidence/repositories/claim.py:35`  
**Description:** Import inside function (lazy import)  
**Recommendation:** Move imports to top of file to avoid circular deps  

---

## QUALITY Anti-Patterns

### Long Function
**Severity:** MEDIUM  
**Location:** `cli_ai_research.py:86`  
**Description:** Function 'ai_research_batch' has 74 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `cli_ai_research.py:167`  
**Description:** Function 'ai_research_server' has 54 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `cli_ai_research.py:229`  
**Description:** Function '_display_report' has 72 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `cli_research.py:105`  
**Description:** Function 'validate_data' has 59 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `cli.py:310`  
**Description:** Function 'generate_llm_report' has 52 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `analytics/classification.py:208`  
**Description:** Function 'report_classification_distribution' has 53 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `analytics/classification.py:264`  
**Description:** Function 'display_confidence_report' has 90 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `analytics/classification.py:357`  
**Description:** Function 'display_batch_confidence_report' has 70 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `data/report_release_gate.py:53`  
**Description:** Function 'evaluate' has 92 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `data/eneve_enrichment.py:13`  
**Description:** Function 'enrich_company_with_confidence' has 69 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `data/eneve_enrichment.py:109`  
**Description:** Function 'validate_enriched_data' has 54 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `data/eneve_enrichment.py:166`  
**Description:** Function 'merge_enrichment_data' has 55 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### God Function
**Severity:** HIGH  
**Location:** `data/enrichment_executors.py:80`  
**Description:** Function 'execute' has 105 lines  
**Recommendation:** Extract helper functions, apply Single Responsibility Principle  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `data/company_research.py:180`  
**Description:** Function '_build_profile' has 70 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `data/company_research.py:252`  
**Description:** Function '_assess_ai_capabilities' has 56 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `data/company_research.py:331`  
**Description:** Function '_calculate_scorecard' has 68 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `data/gap_analyzer.py:88`  
**Description:** Function 'analyze_company_gaps' has 56 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `data/conflict_resolution.py:346`  
**Description:** Function 'resolve_merge' has 55 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `data/provenance.py:244`  
**Description:** Function 'validate_field' has 77 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `data/enrichment_config.py:89`  
**Description:** Function 'print_configuration_guide' has 65 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `data/enrichment_config.py:245`  
**Description:** Function 'from_env' has 60 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `data/interpolation.py:52`  
**Description:** Function 'interpolate_revenue' has 52 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `data/interpolation.py:106`  
**Description:** Function 'interpolate_growth_rate' has 51 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `agents/coordinator_agent.py:66`  
**Description:** Function '_build_graph' has 66 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Parameter List
**Severity:** MEDIUM  
**Location:** `agents/base_agent.py:62`  
**Description:** Function '_create_raw_source' has 9 parameters  
**Recommendation:** Use data classes or kwargs for grouped parameters  

---

### Long Parameter List
**Severity:** MEDIUM  
**Location:** `agents/base_agent.py:87`  
**Description:** Function '_create_fact' has 8 parameters  
**Recommendation:** Use data classes or kwargs for grouped parameters  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `agents/companies_house_agent.py:246`  
**Description:** Function '_extract_facts_from_company_data' has 66 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `research/profile_builders.py:219`  
**Description:** Function 'build_company_profile_from_ticker' has 80 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `research/company_builder.py:160`  
**Description:** Function 'build_company_entity_from_signals' has 65 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### God Function
**Severity:** HIGH  
**Location:** `research/aggregate.py:148`  
**Description:** Function '_extract_yahoo_finance' has 116 lines  
**Recommendation:** Extract helper functions, apply Single Responsibility Principle  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `research/aggregate.py:397`  
**Description:** Function '_aggregate_numeric_fact' has 96 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `research/aggregate.py:496`  
**Description:** Function '_aggregate_non_numeric_fact' has 58 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `research/aggregate.py:585`  
**Description:** Function 'aggregate' has 72 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### God Function
**Severity:** HIGH  
**Location:** `research/pipeline.py:49`  
**Description:** Function 'run_market_intelligence' has 105 lines  
**Recommendation:** Extract helper functions, apply Single Responsibility Principle  

---

### Long Parameter List
**Severity:** MEDIUM  
**Location:** `research/pipeline.py:49`  
**Description:** Function 'run_market_intelligence' has 11 parameters  
**Recommendation:** Use data classes or kwargs for grouped parameters  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `research/discovery.py:148`  
**Description:** Function '_discover_legacy' has 82 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `research/evidence.py:30`  
**Description:** Function 'evaluate_company_evidence' has 76 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Parameter List
**Severity:** MEDIUM  
**Location:** `research/contracts.py:48`  
**Description:** Function 'build_stage_artifact' has 8 parameters  
**Recommendation:** Use data classes or kwargs for grouped parameters  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `research/pipeline_stages.py:186`  
**Description:** Function '_run' has 56 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `research/gather.py:131`  
**Description:** Function 'enrich_company' has 59 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `research/hashing.py:20`  
**Description:** Function '_to_canonical_jsonable' has 63 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `api/exceptions.py:68`  
**Description:** Function 'setup_exception_handlers' has 79 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `monitoring/llm_tracker.py:344`  
**Description:** Function 'track_llm' has 53 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `monitoring/llm_tracker.py:143`  
**Description:** Function 'track_call' has 64 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Parameter List
**Severity:** MEDIUM  
**Location:** `monitoring/llm_tracker.py:143`  
**Description:** Function 'track_call' has 10 parameters  
**Recommendation:** Use data classes or kwargs for grouped parameters  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `monitoring/llm_tracker.py:223`  
**Description:** Function 'get_daily_summary' has 68 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `monitoring/profiler.py:163`  
**Description:** Function 'profile' has 51 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `monitoring/errors.py:157`  
**Description:** Function 'track_error' has 52 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `monitoring/errors.py:266`  
**Description:** Function 'analyze_trends' has 57 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Parameter List
**Severity:** MEDIUM  
**Location:** `validation/financial_sanity.py:80`  
**Description:** Function 'validate_company' has 8 parameters  
**Recommendation:** Use data classes or kwargs for grouped parameters  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `core/error_handler.py:130`  
**Description:** Function 'handle_error' has 60 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `core/coverage_dashboard.py:124`  
**Description:** Function 'parse_coverage' has 61 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `core/coverage_dashboard.py:251`  
**Description:** Function 'export_html' has 73 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `core/scoring_utils.py:31`  
**Description:** Function 'populate_signal_confidences' has 58 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `adapters/registry.py:64`  
**Description:** Function 'build_default_registry' has 76 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `infrastructure/query_cache.py:18`  
**Description:** Function 'cached_query' has 78 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `infrastructure/query_cache.py:36`  
**Description:** Function 'decorator' has 58 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `infrastructure/reconcile_runs.py:84`  
**Description:** Function 'reconcile_research_run' has 76 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Parameter List
**Severity:** MEDIUM  
**Location:** `infrastructure/research_persistence.py:69`  
**Description:** Function 'create_research_run' has 9 parameters  
**Recommendation:** Use data classes or kwargs for grouped parameters  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `infrastructure/reconciliation_helpers.py:84`  
**Description:** Function 'compare_artifacts' has 80 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Parameter List
**Severity:** MEDIUM  
**Location:** `infrastructure/reconciliation_helpers.py:167`  
**Description:** Function 'build_reconciliation_report' has 10 parameters  
**Recommendation:** Use data classes or kwargs for grouped parameters  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `infrastructure/research_dual_write.py:80`  
**Description:** Function 'transition_contradiction_status' has 54 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `infrastructure/research_dual_write.py:150`  
**Description:** Function 'persist_research_run_records' has 76 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Parameter List
**Severity:** MEDIUM  
**Location:** `infrastructure/research_dual_write.py:150`  
**Description:** Function 'persist_research_run_records' has 10 parameters  
**Recommendation:** Use data classes or kwargs for grouped parameters  

---

### Long Parameter List
**Severity:** MEDIUM  
**Location:** `infrastructure/research_dual_write.py:229`  
**Description:** Function '_build_outbox_payload' has 9 parameters  
**Recommendation:** Use data classes or kwargs for grouped parameters  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `infrastructure/research_dual_write.py:254`  
**Description:** Function 'persist_research_run' has 74 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Parameter List
**Severity:** MEDIUM  
**Location:** `infrastructure/research_dual_write.py:254`  
**Description:** Function 'persist_research_run' has 10 parameters  
**Recommendation:** Use data classes or kwargs for grouped parameters  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `infrastructure/unified_registry.py:155`  
**Description:** Function 'build_default_registry' has 69 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `infrastructure/outbox_worker.py:36`  
**Description:** Function '_process_outbox_record' has 56 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `worker/refresh_tasks.py:40`  
**Description:** Function 'create_refresh_task' has 65 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `worker/enrichment_tasks.py:33`  
**Description:** Function 'enrich_company_async' has 76 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `worker/enrichment_tasks.py:113`  
**Description:** Function 'enrich_companies_batch_async' has 82 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `exporters/pdf.py:77`  
**Description:** Function '_export_pdf' has 74 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `exporters/audit_report.py:37`  
**Description:** Function 'generate' has 61 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `extractors/markdown_extractor.py:197`  
**Description:** Function 'to_company_profile' has 64 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `extractors/markdown_extractor.py:442`  
**Description:** Function '_merge_company_profiles' has 53 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `extractors/markdown_extractor.py:508`  
**Description:** Function 'validate_profile_provenance' has 56 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `presentation/adaptive_templates.py:83`  
**Description:** Function '_moderate_strengths' has 54 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### God Function
**Severity:** HIGH  
**Location:** `presentation/adaptive_templates.py:140`  
**Description:** Function '_rich_strengths' has 110 lines  
**Recommendation:** Extract helper functions, apply Single Responsibility Principle  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `utils/logging.py:92`  
**Description:** Function 'setup_logging' has 68 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `security/rate_limiter.py:69`  
**Description:** Function '_update_bucket' has 62 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `evidence/vector_store.py:139`  
**Description:** Function 'search_similar_claims' has 54 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `evidence/crawler.py:268`  
**Description:** Function 'extract_claims_from_content' has 60 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `evidence/crawler.py:348`  
**Description:** Function 'crawl' has 51 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `analytics/signals/extractors.py:30`  
**Description:** Function 'extract' has 56 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `analytics/signals/extractors.py:92`  
**Description:** Function 'extract' has 52 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `analytics/signals/extractors.py:150`  
**Description:** Function 'extract' has 52 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `analytics/signals/extractors.py:208`  
**Description:** Function 'extract' has 53 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `analytics/simulation/market.py:38`  
**Description:** Function '_simulate_company' has 76 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `analytics/scorers/competitive_position.py:13`  
**Description:** Function 'score' has 76 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `analytics/scorers/growth_momentum.py:61`  
**Description:** Function '_score_growth_rate' has 62 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `analytics/scorers/growth_momentum.py:244`  
**Description:** Function '_merge_facts_into_financials' has 53 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `data/connectors/sec_edgar_connector.py:75`  
**Description:** Function 'fetch_filing' has 91 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `data/connectors/sec_edgar_connector.py:223`  
**Description:** Function '_extract_minimal_metrics' has 69 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `data/connectors/news_signal_detector.py:194`  
**Description:** Function '_extract_signals' has 68 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `data/converters/company_extractors.py:336`  
**Description:** Function 'build_confidence_scores' has 53 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### God Function
**Severity:** HIGH  
**Location:** `data/converters/company.py:108`  
**Description:** Function 'convert_to_domain_company' has 119 lines  
**Recommendation:** Extract helper functions, apply Single Responsibility Principle  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `data/normalization/strings.py:95`  
**Description:** Function 'normalize_date' has 52 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `data/parsers/funding.py:15`  
**Description:** Function 'parse_funding_amount' has 69 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `data/parsers/funding.py:87`  
**Description:** Function 'parse_valuation' has 99 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `data/unified/merger.py:18`  
**Description:** Function 'merge_companies' has 63 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `data/unified/merger.py:84`  
**Description:** Function 'merge_financials' has 59 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `data/unified/unified.py:29`  
**Description:** Function '__init__' has 76 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `data/unified/unified.py:107`  
**Description:** Function 'load_unified_companies' has 58 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `data/unified/enrichment.py:77`  
**Description:** Function 'enrich_batch' has 56 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `data/unified/enrichment.py:151`  
**Description:** Function 'fill_nulls_from_sec_edgar' has 79 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `data/sources/news.py:35`  
**Description:** Function '_get_news_from_api' has 64 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `data/sources/news.py:101`  
**Description:** Function '_get_news_from_web_search' has 80 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Parameter List
**Severity:** MEDIUM  
**Location:** `data/enrichment/orchestrator.py:295`  
**Description:** Function 'compare_results' has 8 parameters  
**Recommendation:** Use data classes or kwargs for grouped parameters  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `api/middleware/rate_limit.py:164`  
**Description:** Function '_check_rate_limit' has 53 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `adapters/enrichment/web_search_unified.py:46`  
**Description:** Function 'discover' has 57 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `adapters/enrichment/web_search_unified.py:105`  
**Description:** Function 'enrich' has 67 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### God Function
**Severity:** HIGH  
**Location:** `infrastructure/connectors/yahoo_finance_refresh.py:70`  
**Description:** Function '_convert_profile_to_facts' has 103 lines  
**Recommendation:** Extract helper functions, apply Single Responsibility Principle  

---

### Long Parameter List
**Severity:** MEDIUM  
**Location:** `exporters/markdown/report_sections.py:61`  
**Description:** Function 'generate_client_profile' has 8 parameters  
**Recommendation:** Use data classes or kwargs for grouped parameters  

---

### Long Parameter List
**Severity:** MEDIUM  
**Location:** `exporters/markdown/report_sections.py:85`  
**Description:** Function 'generate_competitive_positioning' has 11 parameters  
**Recommendation:** Use data classes or kwargs for grouped parameters  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `exporters/markdown/client.py:80`  
**Description:** Function '_generate_competitive_analysis' has 66 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `exporters/markdown/client.py:225`  
**Description:** Function '_generate_client_weaknesses' has 61 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### God Function
**Severity:** HIGH  
**Location:** `exporters/markdown/market.py:25`  
**Description:** Function 'generate_market_overview' has 105 lines  
**Recommendation:** Extract helper functions, apply Single Responsibility Principle  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `exporters/markdown/company.py:204`  
**Description:** Function '_generate_weaknesses' has 69 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `exporters/excel/sheets.py:83`  
**Description:** Function 'add_executive_summary' has 76 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `exporters/excel/sheets.py:162`  
**Description:** Function 'add_market_rankings' has 77 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `exporters/excel/sheets.py:242`  
**Description:** Function 'add_financial_intelligence' has 87 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `evidence/repositories/contradiction.py:18`  
**Description:** Function 'create' has 61 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `evidence/repositories/claim.py:25`  
**Description:** Function 'create' has 63 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Long Function
**Severity:** MEDIUM  
**Location:** `evidence/repositories/claim.py:90`  
**Description:** Function 'get_for_entity' has 52 lines (target: <50)  
**Recommendation:** Consider breaking into smaller functions  

---

### Bare Except Clause
**Severity:** HIGH  
**Location:** `core/error_taxonomy.py:219`  
**Description:** Bare 'except:' catches KeyboardInterrupt, SystemExit  
**Recommendation:** Use 'except Exception:' or specific exception types  

---

### Low Test Coverage
**Severity:** HIGH  
**Location:** `tests/`  
**Description:** Test-to-source ratio: 0.39 (target: 1.0+)  
**Recommendation:** Add unit tests for all public functions  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `cli_research.py:119`  
**Description:** FunctionDef 'status_color' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `__init__.py:47`  
**Description:** ClassDef 'InterceptHandler' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `__init__.py:48`  
**Description:** FunctionDef 'emit' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `analytics/energy_sector.py:24`  
**Description:** ClassDef 'EnergySubSector' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `analytics/scoring.py:54`  
**Description:** ClassDef 'CompositeScoreResult' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `analytics/scoring.py:109`  
**Description:** FunctionDef 'calculate_composite_score' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `analytics/competitive_mapping.py:25`  
**Description:** ClassDef 'CompetitiveRelation' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `analytics/workflows.py:26`  
**Description:** ClassDef 'BatchScoreMarketWorkflow' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `analytics/workflows.py:9`  
**Description:** ClassDef 'RetryPolicy' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `analytics/workflows.py:16`  
**Description:** FunctionDef 'info' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/enrichment_types.py:8`  
**Description:** ClassDef 'EnrichableCompany' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/report_release_gate.py:14`  
**Description:** ClassDef 'GateReason' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/report_release_gate.py:28`  
**Description:** ClassDef 'ReportGateResult' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/report_release_gate.py:40`  
**Description:** ClassDef 'ReportReleaseGate' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/report_release_gate.py:19`  
**Description:** FunctionDef 'to_dict' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/report_release_gate.py:32`  
**Description:** FunctionDef 'to_dict' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/report_release_gate.py:53`  
**Description:** FunctionDef 'evaluate' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/report_release_gate.py:147`  
**Description:** FunctionDef 'ensure_release_ready' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/repositories.py:248`  
**Description:** FunctionDef 'json_safe' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/metric_contract.py:6`  
**Description:** ClassDef 'MetricNormalizationResult' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/metric_contract.py:11`  
**Description:** FunctionDef 'normalize_revenue_to_millions' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/metric_contract.py:28`  
**Description:** FunctionDef 'normalize_percent' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/metric_contract.py:40`  
**Description:** FunctionDef 'normalize_financial_payload' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/fetchers.py:191`  
**Description:** FunctionDef 'convert' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/enrichment_service.py:284`  
**Description:** FunctionDef 'analyze_unresolved_gaps' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/source_policy.py:7`  
**Description:** ClassDef 'SourceTier' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/source_policy.py:13`  
**Description:** ClassDef 'SourcePolicy' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/source_policy.py:21`  
**Description:** FunctionDef 'default_source_policy_catalog' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/report_readiness.py:28`  
**Description:** FunctionDef 'get_missing_financial_fields' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/report_readiness.py:37`  
**Description:** FunctionDef 'get_missing_pe_fields' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/report_readiness.py:46`  
**Description:** FunctionDef 'get_low_confidence_fields' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/report_readiness.py:59`  
**Description:** FunctionDef 'get_report_readiness_issues' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/report_readiness.py:74`  
**Description:** FunctionDef 'assert_report_ready' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/report_readiness.py:79`  
**Description:** FunctionDef 'build_report_gate_snapshot' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/report_readiness.py:85`  
**Description:** FunctionDef 'assert_client_report_ready' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/gap_analyzer.py:8`  
**Description:** ClassDef 'GapStatus' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/gap_analyzer.py:29`  
**Description:** ClassDef 'FieldGap' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/gap_analyzer.py:88`  
**Description:** FunctionDef 'analyze_company_gaps' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/enrichment_config.py:257`  
**Description:** FunctionDef 'as_int' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/enrichment_config.py:268`  
**Description:** FunctionDef 'as_optional_str' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/web_search_client.py:71`  
**Description:** FunctionDef 'search_company_news' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/web_search_client.py:123`  
**Description:** FunctionDef 'search_company_info' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `agents/website_agent.py:13`  
**Description:** ClassDef 'WebsiteAgent' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `agents/seed_markdown_agent.py:13`  
**Description:** ClassDef 'SeedMarkdownAgent' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `agents/coordinator_agent.py:40`  
**Description:** ClassDef 'AgentState' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `domain/models.py:19`  
**Description:** ClassDef 'StrEnum' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `domain/models.py:101`  
**Description:** FunctionDef 'funding' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `domain/models.py:105`  
**Description:** FunctionDef 'funding' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `domain/models.py:110`  
**Description:** FunctionDef 'validate_employees' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `domain/models.py:261`  
**Description:** FunctionDef 'sync_financial_fields' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `domain/models.py:414`  
**Description:** FunctionDef 'validate_ai_score_value' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `domain/models.py:421`  
**Description:** FunctionDef 'validate_saas_maturity' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `domain/models.py:428`  
**Description:** FunctionDef 'validate_cagr' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `domain/models.py:435`  
**Description:** FunctionDef 'validate_percentage' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `domain/models.py:442`  
**Description:** FunctionDef 'validate_positive_int' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `domain/models.py:552`  
**Description:** FunctionDef 'company_count' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `domain/models.py:556`  
**Description:** FunctionDef 'average_growth_rate' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `domain/models.py:563`  
**Description:** FunctionDef 'market_leaders' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `domain/models.py:268`  
**Description:** FunctionDef 'sync_field' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `domain/repository_interfaces.py:70`  
**Description:** FunctionDef 'has_next' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `domain/repository_interfaces.py:74`  
**Description:** FunctionDef 'has_prev' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `domain/value_objects.py:71`  
**Description:** FunctionDef 'coerce_decimal' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `domain/value_objects.py:79`  
**Description:** FunctionDef 'non_negative' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `domain/value_objects.py:86`  
**Description:** FunctionDef 'valid_currency' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `domain/value_objects.py:122`  
**Description:** FunctionDef 'valid_range' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `domain/value_objects.py:154`  
**Description:** FunctionDef 'valid_range' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `domain/value_objects.py:159`  
**Description:** FunctionDef 'is_phoenix' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `domain/value_objects.py:164`  
**Description:** FunctionDef 'is_lead' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `domain/value_objects.py:214`  
**Description:** FunctionDef 'end_after_start' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `domain/value_objects.py:220`  
**Description:** FunctionDef 'duration_days' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `domain/value_objects.py:223`  
**Description:** FunctionDef 'contains' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `domain/simulation.py:13`  
**Description:** ClassDef 'StrEnum' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `domain/payload_compat.py:7`  
**Description:** ClassDef 'CompatibilityTransformResult' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `domain/validators.py:25`  
**Description:** FunctionDef 'name_must_not_be_empty' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `domain/validators.py:32`  
**Description:** FunctionDef 'revenue_must_be_positive' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `domain/validators.py:39`  
**Description:** FunctionDef 'employees_must_be_positive' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `domain/validators.py:46`  
**Description:** FunctionDef 'growth_rate_bounds' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `domain/validators.py:76`  
**Description:** FunctionDef 'cagr_must_be_reasonable' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `domain/validators.py:83`  
**Description:** FunctionDef 'profit_margin_bounds' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `domain/source_contract.py:7`  
**Description:** FunctionDef 'normalize_source_key' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `domain/source_contract.py:14`  
**Description:** FunctionDef 'canonical_source_uri' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `domain/source_contract.py:23`  
**Description:** FunctionDef 'is_valid_source_uri' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `llm/enhanced_client.py:271`  
**Description:** FunctionDef 'get_enhanced_llm_client' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `llm/provider_strategies.py:45`  
**Description:** FunctionDef 'provider_name' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `llm/provider_strategies.py:48`  
**Description:** FunctionDef 'create_client' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `llm/provider_strategies.py:62`  
**Description:** FunctionDef 'provider_name' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `llm/provider_strategies.py:65`  
**Description:** FunctionDef 'create_client' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `llm/provider_strategies.py:80`  
**Description:** FunctionDef 'provider_name' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `llm/provider_strategies.py:83`  
**Description:** FunctionDef 'create_client' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `llm/provider_strategies.py:100`  
**Description:** FunctionDef 'provider_name' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `llm/provider_strategies.py:103`  
**Description:** FunctionDef 'create_client' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `llm/provider_strategies.py:120`  
**Description:** FunctionDef 'provider_name' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `llm/provider_strategies.py:123`  
**Description:** FunctionDef 'create_client' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `llm/provider_strategies.py:140`  
**Description:** FunctionDef 'provider_name' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `llm/provider_strategies.py:143`  
**Description:** FunctionDef 'create_client' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `llm/provider_strategies.py:160`  
**Description:** FunctionDef 'provider_name' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `llm/provider_strategies.py:163`  
**Description:** FunctionDef 'create_client' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `llm/provider_strategies.py:180`  
**Description:** FunctionDef 'provider_name' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `llm/provider_strategies.py:183`  
**Description:** FunctionDef 'create_client' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `llm/provider_strategies.py:200`  
**Description:** FunctionDef 'provider_name' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `llm/provider_strategies.py:203`  
**Description:** FunctionDef 'create_client' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `llm/provider_strategies.py:220`  
**Description:** FunctionDef 'provider_name' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `llm/provider_strategies.py:223`  
**Description:** FunctionDef 'create_client' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `llm/provider_strategies.py:241`  
**Description:** FunctionDef 'provider_name' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `llm/provider_strategies.py:244`  
**Description:** FunctionDef 'create_client' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `llm/provider_strategies.py:261`  
**Description:** FunctionDef 'provider_name' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `llm/provider_strategies.py:264`  
**Description:** FunctionDef 'create_client' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `llm/usage_tracker.py:15`  
**Description:** ClassDef 'UsageTracker' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `llm/usage_tracker.py:59`  
**Description:** FunctionDef 'get_usage_tracker' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `llm/usage_tracker.py:23`  
**Description:** FunctionDef 'record_usage' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `llm/usage_tracker.py:46`  
**Description:** FunctionDef 'get_summary' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `llm/health_checker.py:23`  
**Description:** ClassDef 'ProviderHealthChecker' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `llm/health_checker.py:24`  
**Description:** FunctionDef 'get_health' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `llm/health_checker.py:27`  
**Description:** FunctionDef 'report_success' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `llm/health_checker.py:33`  
**Description:** FunctionDef 'report_error' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `llm/health_checker.py:43`  
**Description:** FunctionDef 'should_retry' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `llm/health_checker.py:47`  
**Description:** FunctionDef 'get_retry_delay' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `research/reconcile.py:24`  
**Description:** FunctionDef 'detect_company_contradictions' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `research/reconcile.py:72`  
**Description:** FunctionDef 'detect_market_contradictions' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `research/discovery.py:15`  
**Description:** ClassDef 'DiscoveryCandidate' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `research/discovery.py:96`  
**Description:** FunctionDef 'discover_companies' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `research/sources.py:19`  
**Description:** FunctionDef 'canonicalize_url' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `research/sources.py:67`  
**Description:** FunctionDef 'is_probably_url' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `research/evidence.py:30`  
**Description:** FunctionDef 'evaluate_company_evidence' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `research/evidence.py:109`  
**Description:** FunctionDef 'evaluate_market_evidence' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `research/contracts.py:23`  
**Description:** ClassDef 'StageRequestEnvelope' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `research/contracts.py:32`  
**Description:** ClassDef 'StageResponseEnvelope' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `research/contracts.py:43`  
**Description:** FunctionDef 'build_config_hash' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `research/contracts.py:48`  
**Description:** FunctionDef 'build_stage_artifact' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `research/pipeline_context.py:100`  
**Description:** FunctionDef 'strip_volatile' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `research/hashing.py:86`  
**Description:** FunctionDef 'canonical_json_dumps' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `research/hashing.py:97`  
**Description:** FunctionDef 'sha256_canonical_json' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `tenant/models.py:59`  
**Description:** ClassDef 'Config' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `tenant/models.py:127`  
**Description:** ClassDef 'Config' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `monitoring/llm_tracker.py:356`  
**Description:** FunctionDef 'decorator' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `monitoring/profiler.py:34`  
**Description:** FunctionDef 'to_dict' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `monitoring/profiler.py:76`  
**Description:** FunctionDef 'is_enabled' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `monitoring/profiler.py:181`  
**Description:** FunctionDef 'decorator' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `monitoring/profiler.py:237`  
**Description:** FunctionDef 'decorator' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `monitoring/profiler.py:199`  
**Description:** FunctionDef 'sync_wrapper' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `monitoring/profiler.py:250`  
**Description:** FunctionDef 'sync_wrapper' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `monitoring/metrics.py:246`  
**Description:** FunctionDef 'decorator' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `monitoring/metrics.py:264`  
**Description:** FunctionDef 'sync_wrapper' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `core/error_handler.py:280`  
**Description:** FunctionDef 'decorator' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `core/error_handler.py:324`  
**Description:** FunctionDef 'decorator' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `core/error_handler.py:282`  
**Description:** FunctionDef 'wrapper' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `core/error_handler.py:326`  
**Description:** FunctionDef 'wrapper' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `core/rollback_profile.py:5`  
**Description:** ClassDef 'RollbackProfile' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `core/rollback_profile.py:18`  
**Description:** FunctionDef 'default_safe_rollback_profile' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `core/rollback_profile.py:10`  
**Description:** FunctionDef 'as_env_overrides' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `core/test_modes.py:9`  
**Description:** ClassDef 'TestMode' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `core/test_modes.py:15`  
**Description:** FunctionDef 'resolve_test_mode' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `core/test_modes.py:30`  
**Description:** FunctionDef 'apply_test_mode_seed' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `core/degradation.py:323`  
**Description:** FunctionDef 'decorator' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `core/degradation.py:324`  
**Description:** FunctionDef 'wrapper' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `core/coverage_dashboard.py:31`  
**Description:** FunctionDef 'to_dict' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `core/coverage_dashboard.py:49`  
**Description:** FunctionDef 'to_dict' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `core/coverage_dashboard.py:76`  
**Description:** FunctionDef 'to_dict' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `core/feature_flags.py:7`  
**Description:** ClassDef 'FeatureFlags' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `core/feature_flags.py:21`  
**Description:** FunctionDef 'get_feature_flags' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `core/feature_flags.py:13`  
**Description:** FunctionDef 'from_settings' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `core/rollout_guard.py:5`  
**Description:** ClassDef 'RolloutMetrics' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `core/rollout_guard.py:12`  
**Description:** ClassDef 'RolloutThresholds' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `core/rollout_guard.py:19`  
**Description:** ClassDef 'RolloutDecision' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `core/rollout_guard.py:24`  
**Description:** FunctionDef 'evaluate_rollout' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `core/canary_rollout.py:8`  
**Description:** ClassDef 'CanaryDecision' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `core/canary_rollout.py:20`  
**Description:** FunctionDef 'canary_decision' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/instrumented.py:44`  
**Description:** FunctionDef 'source_name' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/instrumented.py:48`  
**Description:** FunctionDef 'source_type' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/instrumented.py:52`  
**Description:** FunctionDef 'health_records' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/instrumented.py:55`  
**Description:** FunctionDef 'enrich' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/instrumented.py:105`  
**Description:** FunctionDef 'source_name' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/instrumented.py:109`  
**Description:** FunctionDef 'health_records' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/instrumented.py:112`  
**Description:** FunctionDef 'discover' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/registry.py:29`  
**Description:** FunctionDef 'register_discovery' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/registry.py:32`  
**Description:** FunctionDef 'register_enrichment' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/registry.py:40`  
**Description:** FunctionDef 'discovery_sources' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/registry.py:44`  
**Description:** FunctionDef 'enrichment_sources' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/refresh.py:18`  
**Description:** ClassDef 'RefreshStatus' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/refresh.py:267`  
**Description:** FunctionDef 'build_refresh_snapshot' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/refresh.py:292`  
**Description:** FunctionDef 'raise_if_stale' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/query_cache.py:36`  
**Description:** FunctionDef 'decorator' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/query_cache.py:65`  
**Description:** FunctionDef 'sync_wrapper' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/repositories.py:186`  
**Description:** ClassDef 'ReleaseGateAuditRepository' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/retry_policy.py:9`  
**Description:** ClassDef 'FailureClassification' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/retry_policy.py:19`  
**Description:** ClassDef 'RetryDecision' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/retry_policy.py:27`  
**Description:** ClassDef 'RetryPolicy' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/retry_policy.py:86`  
**Description:** ClassDef 'CircuitBreakerState' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/retry_policy.py:92`  
**Description:** ClassDef 'CircuitBreaker' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/retry_policy.py:14`  
**Description:** FunctionDef 'is_retryable' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/retry_policy.py:44`  
**Description:** FunctionDef 'classify_failure' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/retry_policy.py:47`  
**Description:** FunctionDef 'next_delay_seconds' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/retry_policy.py:59`  
**Description:** FunctionDef 'evaluate' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/retry_policy.py:106`  
**Description:** FunctionDef 'state' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/retry_policy.py:111`  
**Description:** FunctionDef 'consecutive_failures' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/retry_policy.py:114`  
**Description:** FunctionDef 'allow_request' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/retry_policy.py:117`  
**Description:** FunctionDef 'record_success' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/retry_policy.py:120`  
**Description:** FunctionDef 'record_failure' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/retry_policy.py:126`  
**Description:** FunctionDef 'open' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/retry_policy.py:130`  
**Description:** FunctionDef 'close' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/reconcile_runs.py:21`  
**Description:** ClassDef 'ReconciliationError' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/reconcile_runs.py:162`  
**Description:** FunctionDef 'reconcile_research_run_with_configured_db' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/reconcile_runs.py:199`  
**Description:** FunctionDef 'main' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/research_dual_write.py:46`  
**Description:** ClassDef 'ContradictionLifecycleError' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/research_dual_write.py:80`  
**Description:** FunctionDef 'transition_contradiction_status' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/research_dual_write.py:254`  
**Description:** FunctionDef 'persist_research_run' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/research_dual_write.py:331`  
**Description:** FunctionDef 'process_outbox' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/research_dual_write.py:72`  
**Description:** FunctionDef 'to_dict' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/cache.py:193`  
**Description:** FunctionDef 'decorator' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/cache.py:231`  
**Description:** FunctionDef 'decorator' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/query_optimizer.py:250`  
**Description:** FunctionDef 'traverse' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/circuit_breaker.py:142`  
**Description:** FunctionDef 'sync_wrapper' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/outbox_worker.py:95`  
**Description:** FunctionDef 'process_outbox_records' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/outbox_worker.py:109`  
**Description:** FunctionDef 'process_outbox_records_with_session' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `exporters/excel_compat.py:20`  
**Description:** ClassDef 'TemplateExporter' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `exporters/excel_compat.py:21`  
**Description:** FunctionDef 'create_dashboard' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `extractors/markdown_extractor.py:508`  
**Description:** FunctionDef 'validate_profile_provenance' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `extractors/markdown_extractor.py:566`  
**Description:** FunctionDef 'validate_profiles_provenance' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `utils/logging.py:16`  
**Description:** FunctionDef 'emit' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `utils/context.py:104`  
**Description:** FunctionDef 'decorator' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `utils/context.py:106`  
**Description:** FunctionDef 'wrapper' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `security/auth.py:177`  
**Description:** FunctionDef 'decorator' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `security/auth.py:218`  
**Description:** FunctionDef 'decorator' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `evidence/models.py:115`  
**Description:** ClassDef 'Config' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `evidence/models.py:165`  
**Description:** ClassDef 'Config' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `evidence/models.py:194`  
**Description:** ClassDef 'Config' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `evidence/models.py:229`  
**Description:** ClassDef 'Config' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `connectors/government/usaspending.py:71`  
**Description:** FunctionDef 'normalize' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `connectors/government/wayback.py:88`  
**Description:** FunctionDef 'normalize' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `connectors/government/patentsview.py:106`  
**Description:** FunctionDef 'normalize' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `connectors/government/whois.py:44`  
**Description:** FunctionDef 'normalize' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `connectors/government/dns.py:76`  
**Description:** FunctionDef 'normalize' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `connectors/news/rss.py:79`  
**Description:** FunctionDef 'normalize' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `connectors/news/hacker_news.py:96`  
**Description:** FunctionDef 'normalize' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `connectors/news/newsapi.py:100`  
**Description:** FunctionDef 'normalize' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `connectors/academic/arxiv.py:88`  
**Description:** FunctionDef 'normalize' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `connectors/financial/yahoo_finance.py:60`  
**Description:** FunctionDef 'normalize' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `connectors/financial/opencorporates.py:109`  
**Description:** FunctionDef 'normalize' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `connectors/financial/crunchbase.py:90`  
**Description:** FunctionDef 'normalize' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `connectors/financial/betalist.py:43`  
**Description:** FunctionDef 'normalize' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `connectors/financial/f6s.py:43`  
**Description:** FunctionDef 'normalize' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `connectors/financial/angellist.py:43`  
**Description:** FunctionDef 'normalize' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `connectors/product/bitbucket.py:81`  
**Description:** FunctionDef 'normalize' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `connectors/product/gitlab.py:110`  
**Description:** FunctionDef 'normalize' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `connectors/product/pypi.py:67`  
**Description:** FunctionDef 'normalize' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `connectors/product/producthunt.py:120`  
**Description:** FunctionDef 'normalize' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `connectors/product/maven.py:111`  
**Description:** FunctionDef 'normalize' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `connectors/product/g2.py:43`  
**Description:** FunctionDef 'normalize' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `connectors/product/dockerhub.py:96`  
**Description:** FunctionDef 'normalize' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `connectors/product/github.py:116`  
**Description:** FunctionDef 'normalize' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `connectors/product/capterra.py:43`  
**Description:** FunctionDef 'normalize' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `connectors/product/appstore.py:109`  
**Description:** FunctionDef 'normalize' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `connectors/product/googleplay.py:44`  
**Description:** FunctionDef 'normalize' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `connectors/product/stackoverflow.py:88`  
**Description:** FunctionDef 'normalize' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `connectors/product/npm.py:95`  
**Description:** FunctionDef 'normalize' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `connectors/social/glassdoor.py:43`  
**Description:** FunctionDef 'normalize' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `connectors/social/youtube.py:87`  
**Description:** FunctionDef 'normalize' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `connectors/social/linkedin.py:57`  
**Description:** FunctionDef 'normalize' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `connectors/social/twitter.py:98`  
**Description:** FunctionDef 'normalize' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `connectors/social/reddit.py:93`  
**Description:** FunctionDef 'normalize' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `connectors/social/trustpilot.py:84`  
**Description:** FunctionDef 'normalize' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `connectors/social/podcastindex.py:78`  
**Description:** FunctionDef 'normalize' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `analytics/signals/base.py:36`  
**Description:** ClassDef 'Config' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `analytics/valuation/models.py:37`  
**Description:** FunctionDef 'is_undervalued' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `analytics/valuation/models.py:43`  
**Description:** FunctionDef 'is_overvalued' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `analytics/valuation/models.py:61`  
**Description:** FunctionDef 'calculate_intrinsic_value' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `analytics/valuation/models.py:78`  
**Description:** FunctionDef 'analyze' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `analytics/valuation/models.py:131`  
**Description:** FunctionDef 'estimate_growth_rate' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `analytics/valuation/models.py:157`  
**Description:** FunctionDef 'calculate' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `analytics/valuation/models.py:175`  
**Description:** FunctionDef 'benchmark_companies' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `analytics/valuation/models.py:192`  
**Description:** FunctionDef 'get_undervalued' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `analytics/valuation/models.py:195`  
**Description:** FunctionDef 'get_overvalued' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `analytics/valuation/models.py:206`  
**Description:** FunctionDef 'is_member' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/connectors/sec_edgar_connector.py:21`  
**Description:** ClassDef 'CompanyNotFoundError' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/connectors/sec_edgar_connector.py:26`  
**Description:** ClassDef 'FilingProtocol' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/connectors/sec_edgar_connector.py:35`  
**Description:** ClassDef 'StatementProtocol' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/connectors/sec_edgar_connector.py:40`  
**Description:** ClassDef 'FinancialsProtocol' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/connectors/sec_edgar_connector.py:47`  
**Description:** ClassDef 'SecFilingRequest' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/connectors/sec_edgar_connector.py:53`  
**Description:** ClassDef 'SECEdgarConnector' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/connectors/sec_edgar_connector.py:31`  
**Description:** FunctionDef 'obj' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/connectors/sec_edgar_connector.py:36`  
**Description:** FunctionDef 'to_dataframe' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/connectors/sec_edgar_connector.py:41`  
**Description:** FunctionDef 'income_statement' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/connectors/sec_edgar_connector.py:43`  
**Description:** FunctionDef 'balance_sheet' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/connectors/sec_edgar_connector.py:75`  
**Description:** FunctionDef 'fetch_filing' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/connectors/companies_house_connector.py:15`  
**Description:** ClassDef 'CompaniesHouseNotConfiguredError' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/connectors/companies_house_connector.py:19`  
**Description:** ClassDef 'CompaniesHouseCompanyNotFoundError' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/connectors/companies_house_connector.py:23`  
**Description:** ClassDef 'CompaniesHouseConnector' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/connectors/companies_house_connector.py:41`  
**Description:** FunctionDef 'search_company_by_name' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/connectors/companies_house_connector.py:63`  
**Description:** FunctionDef 'fetch_company_details' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/connectors/companies_house_connector.py:70`  
**Description:** FunctionDef 'get_company_metrics' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/connectors/lookup_service.py:12`  
**Description:** ClassDef 'IdentifierLookupService' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/connectors/lookup_service.py:228`  
**Description:** FunctionDef 'lookup_ticker' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/connectors/lookup_service.py:261`  
**Description:** FunctionDef 'lookup_company_number' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/connectors/lookup_service.py:296`  
**Description:** FunctionDef 'lookup_isin' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/connectors/lookup_service.py:321`  
**Description:** FunctionDef 'infer_geography' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/connectors/lookup_service.py:353`  
**Description:** FunctionDef 'resolve_identifiers' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/markets/models.py:52`  
**Description:** FunctionDef 'yahoo_code' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/markets/models.py:74`  
**Description:** FunctionDef 'convert' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/markets/currency.py:89`  
**Description:** FunctionDef 'last_update' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/converters/company_extractors.py:350`  
**Description:** FunctionDef 'convert_confidence_value' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/enrichment/orchestrator.py:31`  
**Description:** FunctionDef 'get_source_policy_tier' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `data/enrichment/orchestrator.py:103`  
**Description:** FunctionDef 'get_paid_escalation_order' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `domain/models/__init__.py:31`  
**Description:** ClassDef 'CompanyClassification' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `domain/models/__init__.py:27`  
**Description:** ClassDef 'StrEnum' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `api/routes/refresh.py:20`  
**Description:** ClassDef 'AsyncResult' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `api/routes/refresh.py:24`  
**Description:** ClassDef 'CeleryTask' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `api/routes/refresh.py:48`  
**Description:** ClassDef 'RefreshRequest' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `api/routes/refresh.py:53`  
**Description:** ClassDef 'RefreshResponse' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `api/routes/refresh.py:59`  
**Description:** ClassDef 'RefreshStatusResponse' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `api/routes/refresh.py:70`  
**Description:** ClassDef 'WebhookPayload' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `api/routes/refresh.py:25`  
**Description:** FunctionDef 'apply_async' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `api/schemas/errors.py:52`  
**Description:** ClassDef 'Config' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `api/routers/auth.py:30`  
**Description:** ClassDef 'Config' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `api/routers/auth.py:39`  
**Description:** ClassDef 'Config' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `core/health_checks/redis.py:17`  
**Description:** FunctionDef 'name' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `core/health_checks/database.py:17`  
**Description:** FunctionDef 'name' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `core/health_checks/llm.py:17`  
**Description:** FunctionDef 'name' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `core/health_checks/configuration.py:15`  
**Description:** FunctionDef 'name' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `core/health_checks/api.py:15`  
**Description:** FunctionDef 'name' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/discovery/web_search.py:21`  
**Description:** FunctionDef 'source_name' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/discovery/web_search.py:24`  
**Description:** FunctionDef 'discover' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/discovery/competitor_json.py:25`  
**Description:** FunctionDef 'source_name' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/discovery/competitor_json.py:29`  
**Description:** FunctionDef 'source_type' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/discovery/competitor_json.py:32`  
**Description:** FunctionDef 'discover' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/discovery/static_catalog.py:25`  
**Description:** FunctionDef 'source_name' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/discovery/static_catalog.py:29`  
**Description:** FunctionDef 'source_type' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/discovery/static_catalog.py:32`  
**Description:** FunctionDef 'discover' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/linkedin.py:22`  
**Description:** FunctionDef 'source_name' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/linkedin.py:26`  
**Description:** FunctionDef 'source_type' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/linkedin.py:29`  
**Description:** FunctionDef 'enrich' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/global_market.py:19`  
**Description:** FunctionDef 'source_name' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/global_market.py:23`  
**Description:** FunctionDef 'source_type' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/global_market.py:26`  
**Description:** FunctionDef 'enrich' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/yahoo_finance.py:19`  
**Description:** FunctionDef 'source_name' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/yahoo_finance.py:23`  
**Description:** FunctionDef 'source_type' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/yahoo_finance.py:26`  
**Description:** FunctionDef 'enrich' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/website_unified.py:192`  
**Description:** FunctionDef 'get_confidence' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/website_unified.py:195`  
**Description:** FunctionDef 'get_authority' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/website_unified.py:198`  
**Description:** FunctionDef 'supports_incremental' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/website_unified.py:201`  
**Description:** FunctionDef 'supports_discovery' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/linkedin_unified.py:144`  
**Description:** FunctionDef 'get_confidence' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/linkedin_unified.py:147`  
**Description:** FunctionDef 'get_authority' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/linkedin_unified.py:150`  
**Description:** FunctionDef 'supports_incremental' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/linkedin_unified.py:153`  
**Description:** FunctionDef 'supports_discovery' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/patents.py:29`  
**Description:** FunctionDef 'source_name' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/patents.py:33`  
**Description:** FunctionDef 'source_type' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/patents.py:36`  
**Description:** FunctionDef 'enrich' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/funding.py:22`  
**Description:** FunctionDef 'source_name' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/funding.py:26`  
**Description:** FunctionDef 'source_type' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/funding.py:29`  
**Description:** FunctionDef 'enrich' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/web_search_news.py:19`  
**Description:** FunctionDef 'source_name' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/web_search_news.py:23`  
**Description:** FunctionDef 'source_type' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/web_search_news.py:26`  
**Description:** FunctionDef 'enrich' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/funding_unified.py:196`  
**Description:** FunctionDef 'get_confidence' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/funding_unified.py:199`  
**Description:** FunctionDef 'get_authority' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/funding_unified.py:202`  
**Description:** FunctionDef 'supports_incremental' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/funding_unified.py:205`  
**Description:** FunctionDef 'supports_discovery' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/patents_unified.py:182`  
**Description:** FunctionDef 'get_confidence' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/patents_unified.py:185`  
**Description:** FunctionDef 'get_authority' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/patents_unified.py:188`  
**Description:** FunctionDef 'supports_incremental' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/patents_unified.py:191`  
**Description:** FunctionDef 'supports_discovery' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/website.py:18`  
**Description:** FunctionDef 'source_name' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/website.py:22`  
**Description:** FunctionDef 'source_type' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/website.py:25`  
**Description:** FunctionDef 'enrich' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/news_unified.py:238`  
**Description:** FunctionDef 'get_confidence' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/news_unified.py:241`  
**Description:** FunctionDef 'get_authority' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/news_unified.py:244`  
**Description:** FunctionDef 'supports_incremental' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/news_unified.py:247`  
**Description:** FunctionDef 'supports_discovery' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/news.py:21`  
**Description:** FunctionDef 'source_name' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/news.py:25`  
**Description:** FunctionDef 'source_type' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `adapters/enrichment/news.py:30`  
**Description:** FunctionDef 'enrich' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/models/infrastructure.py:76`  
**Description:** FunctionDef 'to_dict' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/models/company.py:109`  
**Description:** FunctionDef 'to_dict' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/models/company.py:188`  
**Description:** FunctionDef 'to_dict' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/models/company.py:228`  
**Description:** FunctionDef 'to_dict' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/models/company.py:263`  
**Description:** FunctionDef 'to_dict' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

### Missing Docstring
**Severity:** LOW  
**Location:** `infrastructure/models/company.py:313`  
**Description:** FunctionDef 'to_dict' has no docstring  
**Recommendation:** Add docstring explaining purpose and usage  

---

