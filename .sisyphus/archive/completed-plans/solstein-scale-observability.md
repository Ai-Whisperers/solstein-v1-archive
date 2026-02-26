# Solstein Scale-Up: Data Growth + Observability + Visualization

## TL;DR
> Make Solstein able to ingest/enrich/score/export across any market + company type, while producing fully traceable, explainable runs (logs + traces + metrics + persisted artifacts).

**Deliverables**:
- A versioned, run-centric pipeline model (`batch_id`/`run_id`) with persistent intermediate artifacts + lineage.
- Pluggable data acquisition (connectors) that supports discovery + incremental refresh, not just static datasets.
- Stronger query generation + source credibility + confidence calibration.
- Scoring that is market-aware, testable, and drift-monitored.
- Visualizations for operators and clients (run explorer + coverage/quality dashboards).

**Estimated Effort**: XL
**Parallel Execution**: YES (5 waves + final verification)

---

## Context

### Original Request
"make a detaild plan for how we could improve each step and how we could visualize and log all the results etc and all they ways we can improve the logic to be able to run this and get all the data for all company types and all markets etc and not be limited to data we have already but to grow and get more data as our clients use us"

### Current System (repo-backed anchors)
- Entrypoints: `src/solstein/api/main.py`, `src/solstein/cli.py`
- Local ingestion: `src/solstein/data/loaders.py` (default `data/input/competitor_data.json`), `src/solstein/extractors/markdown_extractor.py`
- Enrichment/search: `src/solstein/agents/web_search_agent.py`, `src/solstein/data/web_search_client.py`, other agents in `src/solstein/agents/`
- Scoring: `src/solstein/analytics/scoring.py`
- Export: `src/solstein/exporters/excel.py`, `src/solstein/exporters/markdown/generator.py`
- Config + directories: `src/solstein/config.py`

### Metis Review (guardrails + missing decisions)
- Must define market coverage, source allowlist/licensing policy, freshness/cadence, entity resolution standard, and LLM role boundaries.
- Must include cost budgets + confidence gates; treat web/markdown as hostile input (prompt injection).

### Oracle Review (architecture options)
- Recommended near-term: DB-centric “Run Orchestrator” (persist artifacts keyed by `batch_id` + `company_id`), with clear interfaces for connectors, aggregation, signal extraction, scoring, and exporting.
- Add unified correlation IDs; adopt OpenTelemetry for traces/metrics; persist run artifacts + lineage for explainability.

---

## Work Objectives

### Core Objective
Evolve Solstein from “run on a dataset” into an extensible, market-wide intelligence pipeline: discover companies, enrich with multiple sources, score reliably, and export explainable outputs—while capturing end-to-end observability and reproducibility.

### Scope
- IN: ingestion generalization, connector architecture, entity resolution, incremental refresh, query improvements, confidence/credibility, market-aware scoring, observability (logs/traces/metrics), run visualization, export provenance.
- OUT: major UI redesign of the dashboard app (unless needed for a minimal run explorer), and any unlicensed scraping beyond an explicit allowlist.

### Decisions Needed (fill before execution if unknown)
- What is the canonical entity? `legal entity` vs `brand` vs `product`.
- Which markets first (languages/regions/currencies) and what “coverage” means.
- Source policy: allowed sources (web, paid APIs, client-provided docs) + ToS/licensing rules.
- Freshness targets (per source class) and cost budgets (per company/run).

---

## Verification Strategy (MANDATORY)

**Test Decision (default)**:
- **Infrastructure exists**: YES (`pytest` per `pyproject.toml`)
- **Automated tests**: YES (Tests-after for refactors; TDD for new modules)

**QA Policy**:
- Every task includes agent-executed QA scenarios with concrete commands (`pytest`, `uvicorn`, `curl`) and evidence paths under `.sisyphus/evidence/`.
- Every pipeline stage must be reproducible with a stable `run_id` and produce inspectable artifacts.

---

## Execution Strategy

### Parallel Execution Waves

Wave 1 (Start Immediately — observability + contracts)
├── Task 1: Run model + artifact layout
├── Task 2: Structured logging + correlation IDs
├── Task 3: Tracing (OpenTelemetry) span conventions
├── Task 4: Metrics + scrape endpoint
├── Task 5: Schema/versioning + validation gates
└── Task 6: Source policy + safety guardrails

Wave 2 (After Wave 1 — ingestion + identity)
├── Task 7: Connector interfaces (discover/refresh + cursors)
├── Task 8: Entity resolution (canonical IDs + aliasing + reversible merges)
├── Task 9: Dedupe/provenance hashing for sources + facts
└── Task 10: Incremental refresh scheduler + persisted cursors

Wave 3 (After Wave 2 — enrichment + query engine)
├── Task 11: Query generation framework (locale + taxonomy aware)
├── Task 12: Source credibility + confidence calibration
├── Task 13: Unified rate-limit / retry / caching layer for fetches
└── Task 14: Prompt-injection hardening + content sanitization

Wave 4 (After Wave 3 — scoring + evaluation)
├── Task 15: Market-aware scoring + feature store for signals
├── Task 16: Coverage/completeness gates + graceful degradation
└── Task 17: Evaluation harness (golden datasets + drift monitors)

Wave 5 (After Wave 4 — visualization + exports)
├── Task 18: Run explorer API (runs/companies/artifacts/lineage)
├── Task 19: Operator dashboards (coverage/cost/latency)
└── Task 20: Export provenance + deliverable bundle

---

## TODOs

- [ ] 1. Run Model + Artifact Layout (Run-Centric Pipeline)

  **What to do**:
  - Introduce a first-class `run_id` / `batch_id` concept across API + CLI runs.
  - Define a standard artifact layout on disk (per run, per company, per stage) and a lightweight manifest index (JSON) for quick browsing.
  - Persist stage outputs (at minimum: raw sources metadata, aggregated facts, extracted signals, scores, exports) keyed by `run_id` + `company_id`.
  - Ensure artifacts can be generated locally first (filesystem), with a clear seam for object storage later.

  **Must NOT do**:
  - Store large raw HTML or full scraped pages directly in Postgres rows; store hashes + metadata + external references.
  - Assume a single market/language; run metadata must include locale/timezone/currency context.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `development/architecture-patterns`, `code-quality/defense-in-depth`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2-6)
  - **Blocks**: Tasks 7-20
  - **Blocked By**: None

  **References**:
  - `src/solstein/config.py` - output directory conventions and env configuration
  - `src/solstein/api/main.py` - API lifecycle where run context can be initialized
  - `src/solstein/cli.py` - CLI commands that should attach `run_id`
  - `src/solstein/domain/models.py` - domain models to extend/associate with run metadata

  **Acceptance Criteria**:
  - [ ] Every API-triggered run returns/records a `run_id`.
  - [ ] Every CLI run prints a `run_id` and writes a manifest file under a per-run directory.
  - [ ] A run manifest includes at least: run_id, start/end timestamps, inputs, markets/locale, per-stage status, and export artifact refs.

  **QA Scenarios**:
  ```
  Scenario: API run creates a persisted run manifest
    Tool: Bash (curl)
    Steps:
      1. Start API: uvicorn solstein.api.main:app --reload
      2. Trigger export: curl -sS "http://localhost:8000/export/excel" | tee .sisyphus/evidence/task-1-export-response.json
      3. Extract run_id from response (documented field) and verify a manifest exists on disk under the configured export/artifact root
    Expected Result: manifest file exists and includes stage statuses + timestamps
    Evidence: .sisyphus/evidence/task-1-export-response.json

  Scenario: CLI run writes artifacts with run_id
    Tool: Bash
    Steps:
      1. Run CLI scoring on a small fixture JSON: python -m solstein.cli score <fixture.json> --output <out.json>
      2. Verify CLI prints run_id and a manifest file exists
    Expected Result: run_id present + manifest created
    Evidence: .sisyphus/evidence/task-1-cli-run.txt
  ```

- [ ] 2. Structured Logging + Correlation IDs Everywhere

  **What to do**:
  - Standardize structured JSON logs with consistent keys: `request_id`, `run_id`, `batch_id`, `company_id`, `stage`, `agent`, `source_type`, `attempt`.
  - Ensure API requests bind `request_id` and propagate it into downstream calls.
  - Ensure agent execution binds `agent_name` + `source_type` automatically.
  - Write logs to a predictable file path and rotate safely.

  **Must NOT do**:
  - Emit free-form log lines without context for pipeline stages.
  - Log secrets or full raw payloads (store hashes + size + source URL).

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: `code-quality/error-handling-patterns`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1,3,4,5,6)
  - **Blocks**: Tasks 18-19 (dashboards need reliable logs/metrics)
  - **Blocked By**: None

  **References**:
  - `src/solstein/api/middleware.py` - request lifecycle and request-id propagation
  - `src/solstein/utils/logging.py` - existing logging setup patterns
  - `src/solstein/agents/base_agent.py` - common logging/binding for agent runs
  - `src/solstein/config.py` - logging config and file paths

  **Acceptance Criteria**:
  - [ ] API logs include `request_id` and `run_id` for all endpoints involved in runs.
  - [ ] Agent logs include `agent`, `source_type`, and link back to `run_id` + `company_id`.
  - [ ] A single grep on `run_id` reconstructs the full run timeline.

  **QA Scenarios**:
  ```
  Scenario: Request logs include correlation IDs
    Tool: Bash (curl)
    Steps:
      1. Start API
      2. Call: curl -sS "http://localhost:8000/health" > /dev/null
      3. Inspect latest log line(s) for JSON fields request_id and run_id
    Expected Result: structured log contains request_id; run_id present for run endpoints
    Evidence: .sisyphus/evidence/task-2-health-log.txt

  Scenario: Agent logs bind company context
    Tool: Bash
    Steps:
      1. Run a coordinator/enrichment path for 1 company (documented command)
      2. Verify logs include company_id + agent + stage
    Expected Result: logs are filterable by run_id and company_id
    Evidence: .sisyphus/evidence/task-2-agent-log.txt
  ```

- [ ] 3. Distributed Tracing (OpenTelemetry) for Every Pipeline Stage

  **What to do**:
  - Add OTel tracing with a standard span model: `ingest`, `gather`, `aggregate`, `extract_signals`, `score`, `export`.
  - Propagate trace context from FastAPI request → enrichment agents → external calls.
  - Add span attributes that match log keys (`run_id`, `company_id`, `agent`, `source_type`).

  **Must NOT do**:
  - Capture raw page contents in spans.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `infrastructure/distributed-tracing`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: Task 18 (run explorer benefits from trace links)
  - **Blocked By**: Task 1

  **References**:
  - `src/solstein/api/main.py` - lifespan hook for tracer init
  - `src/solstein/api/middleware.py` - request context propagation
  - `src/solstein/agents/coordinator_agent.py` - stage boundaries

  **Acceptance Criteria**:
  - [ ] A single run produces a trace with spans for all pipeline stages.
  - [ ] External calls (GitHub/search/etc) appear as child spans with status codes.

  **QA Scenarios**:
  ```
  Scenario: Trace created for export run
    Tool: Bash (curl)
    Steps:
      1. Start API with tracing enabled
      2. Trigger /export/excel
      3. Verify trace exporter outputs spans including stage names and run_id attributes
    Expected Result: trace exists and is queryable by run_id
    Evidence: .sisyphus/evidence/task-3-trace.txt
  ```

- [ ] 4. Metrics (Prometheus/OTel) for Coverage, Cost, and Reliability

  **What to do**:
  - Add a real scrapeable metrics endpoint (Prometheus exposition) in addition to any human JSON metrics.
  - Emit counters/histograms for: stage durations, agent call counts, error rates, rate-limit events, coverage/completeness.
  - Define SLO-style thresholds for alerts (budget overruns, low coverage, elevated error rates).

  **Must NOT do**:
  - Ship metrics without stable label cardinality controls (avoid unbounded labels like raw URLs).

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `infrastructure/prometheus-configuration`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: Task 19
  - **Blocked By**: Task 1

  **References**:
  - `src/solstein/api/routers/health.py` - existing health/metrics patterns
  - `src/solstein/agents/web_search_agent.py` - place to count external calls + retries

  **Acceptance Criteria**:
  - [ ] `curl http://localhost:8000/metrics` (or documented path) returns Prometheus-format metrics.
  - [ ] Metrics include stage durations and agent error rates.

  **QA Scenarios**:
  ```
  Scenario: Metrics endpoint exposes pipeline metrics
    Tool: Bash (curl)
    Steps:
      1. Start API
      2. Hit /health and /export/excel once
      3. curl -sS http://localhost:8000/metrics | tee .sisyphus/evidence/task-4-metrics.txt
      4. Assert output contains at least: stage_duration_seconds and agent_calls_total
    Expected Result: metrics present with stable labels
    Evidence: .sisyphus/evidence/task-4-metrics.txt
  ```

- [ ] 5. Schema Versioning + Validation Gates (Company/Facts/Signals/Exports)

  **What to do**:
  - Add explicit schema versions for `Company` and for persisted run artifacts (raw sources, aggregated facts, signals, scoring explanation).
  - Enforce validation at stage boundaries: ingestion must produce valid domain objects; export must refuse to run if minimum required fields are missing.
  - Define backward compatibility rules so older runs/exports remain readable.

  **Must NOT do**:
  - Break existing exporter assumptions silently (e.g., missing fields yielding misleading “0.0” scores).

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `development/typescript-advanced-types` (omit if Python-only), `code-quality/defense-in-depth`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: Tasks 15-20
  - **Blocked By**: Task 1

  **References**:
  - `src/solstein/domain/models.py` - domain schema definitions to version
  - `src/solstein/exporters/excel.py` - export expectations for fields/scores
  - `src/solstein/exporters/markdown/generator.py` - report generation expectations

  **Acceptance Criteria**:
  - [ ] A run artifact manifest includes `schema_version`.
  - [ ] Export endpoints fail fast with a clear error when validation gates fail.
  - [ ] `pytest` includes at least 1 regression test proving old fixture data still exports.

  **QA Scenarios**:
  ```
  Scenario: Export refuses invalid data with actionable error
    Tool: Bash (curl)
    Steps:
      1. Start API
      2. Trigger export with a deliberately invalid fixture repo/config
      3. Assert response includes validation error and missing fields list
    Expected Result: 4xx error with precise validation details
    Evidence: .sisyphus/evidence/task-5-validation-error.json
  ```

- [ ] 6. Source Policy + Safety Guardrails (Licensing/PII/Prompt-Injection/Costs)

  **What to do**:
  - Implement an explicit source allowlist + per-source rules (rate limits, ToS, attribution, robots constraints).
  - Add content sanitation and prompt-injection defenses before any LLM step.
  - Add PII redaction policy for stored artifacts and logs.
  - Add per-run cost budgets (API calls, token budgets) with circuit breakers.

  **Must NOT do**:
  - Expand scraping into prohibited sources without an allowlist and explicit policy.
  - Persist raw content that may contain PII without redaction/retention controls.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `deployment/secrets-management`, `code-quality/defense-in-depth`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: Tasks 11-14
  - **Blocked By**: Task 2

  **References**:
  - `src/solstein/config.py` - env vars for keys and safe defaults
  - `src/solstein/agents/web_search_agent.py` - external calls + retries/circuit breaker
  - `src/solstein/infrastructure/data_loaders/additional_sources.py` - optional external sources + scraping fallbacks

  **Acceptance Criteria**:
  - [ ] Source allowlist exists and is enforced (blocked sources produce explicit errors).
  - [ ] LLM steps never see untrusted instructions from raw content (sanitized input only).
  - [ ] Logs/artifacts redact configured sensitive patterns.

  **QA Scenarios**:
  ```
  Scenario: Blocked source is rejected
    Tool: Bash
    Steps:
      1. Configure a blocked source in a test run
      2. Execute enrichment
      3. Assert run fails gracefully with "source not allowed" and no outbound call
    Expected Result: policy enforcement works
    Evidence: .sisyphus/evidence/task-6-source-policy.txt
  ```

- [ ] 7. Connector Interfaces for Discovery + Incremental Refresh

  **What to do**:
  - Introduce a connector abstraction with two capabilities:
    - `discover(market_context) -> list[CompanyCandidate]`
    - `refresh(company_id, cursor) -> SourceDocuments + new cursor`
  - Persist per-connector cursors (etag/page_token/last_seen_date) so refresh is incremental.
  - Provide an initial connector set that wraps existing agents and the local dataset loader.

  **Must NOT do**:
  - Conflate “discover” with “refresh”; they scale differently and have different cost models.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `development/architecture-patterns`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: Tasks 10-14
  - **Blocked By**: Tasks 1,6

  **References**:
  - `src/solstein/data/loaders.py` - current “load from dataset” ingestion
  - `src/solstein/agents/coordinator_agent.py` - orchestration boundaries
  - `src/solstein/data/repositories.py` - persistence/repository seams

  **Acceptance Criteria**:
  - [ ] Connectors can be registered/configured without editing core pipeline logic.
  - [ ] A refresh run only fetches data newer than the stored cursor.

  **QA Scenarios**:
  ```
  Scenario: Incremental refresh skips old items
    Tool: Bash
    Steps:
      1. Run refresh for a company with cursor at T
      2. Run refresh again without new data
      3. Assert second run makes 0 external fetches and completes quickly
    Expected Result: cursor works and prevents duplicate work
    Evidence: .sisyphus/evidence/task-7-refresh.txt
  ```

- [ ] 8. Entity Resolution (Canonical IDs + Aliases + Reversible Merges)

  **What to do**:
  - Define canonical identity strategy (domain + registry IDs first, fuzzy matching second).
  - Implement alias tables/structures: names, domains, registry IDs, previous names.
  - Make merges reversible (record merge events and allow rollback) to avoid poisoning downstream scoring.

  **Must NOT do**:
  - Auto-merge entities purely on name similarity.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `development/architecture-patterns`, `code-quality/root-cause-tracing`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: Tasks 15-20
  - **Blocked By**: Tasks 5,7

  **References**:
  - `src/solstein/domain/models.py` - add identity fields and linkages
  - `src/solstein/data/repositories.py` - persistence across JSON/Supabase
  - `src/solstein/agents/companies_house_agent.py` - registry identifiers

  **Acceptance Criteria**:
  - [ ] Same-name different-country entities stay distinct.
  - [ ] Merge/rollback is audited and does not delete underlying source docs.

  **QA Scenarios**:
  ```
  Scenario: Avoid false merge for same-name companies
    Tool: Bash
    Steps:
      1. Create two fixtures with same name, different domains/jurisdictions
      2. Run entity resolution
      3. Assert two distinct canonical IDs remain
    Expected Result: no incorrect merge
    Evidence: .sisyphus/evidence/task-8-er.txt
  ```

- [ ] 9. Dedupe + Provenance Hashing for Raw Sources and Derived Facts

  **What to do**:
  - Define canonical hashing for raw sources (normalized URL + published_at + body hash) and enforce uniqueness per `company_id`.
  - Ensure derived facts reference stable `source_id`s and keep contradictions rather than overwriting.
  - Add dedupe metrics (hits/misses) and ensure incremental refresh doesn’t re-ingest duplicates.

  **Must NOT do**:
  - Deduplicate by title only; it breaks on syndicated press and translations.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `code-quality/defense-in-depth`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: Tasks 12,16,20
  - **Blocked By**: Tasks 1,7

  **References**:
  - `src/solstein/agents/web_search_agent.py` - raw source construction
  - `src/solstein/domain/models.py` - facts/signals and provenance fields

  **Acceptance Criteria**:
  - [ ] Re-running enrichment on the same time window produces 0 new raw sources.
  - [ ] Facts retain `sources_used` references and contradictions are recorded.

  **QA Scenarios**:
  ```
  Scenario: Second run dedupes sources
    Tool: Bash
    Steps:
      1. Run enrichment twice for the same company/time window
      2. Compare raw source counts
    Expected Result: second run creates no new sources; dedupe counter increments
    Evidence: .sisyphus/evidence/task-9-dedupe.txt
  ```

- [ ] 10. Incremental Refresh Scheduler + Persisted Connector Cursors

  **What to do**:
  - Persist cursors per connector + company (last_seen_publication_date, etag/page_token).
  - Replace in-memory-only refresh state with persisted state so restarts don’t trigger storms.
  - Implement scheduling (interval + backoff) for continuous monitoring/refresh.

  **Must NOT do**:
  - Keep freshness state only in process memory.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `development/async-python-patterns`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: Tasks 13,17
  - **Blocked By**: Tasks 7,9

  **References**:
  - `src/solstein/monitoring/continuous_monitor.py` - current monitoring loop
  - `src/solstein/config.py` - cache/export directories and env settings
  - `src/solstein/data/repositories.py` - persistence layer seams

  **Acceptance Criteria**:
  - [ ] Restarting the API does not reset refresh cursors.
  - [ ] A scheduled refresh run only fetches new items since cursor.

  **QA Scenarios**:
  ```
  Scenario: Cursor persists across restart
    Tool: Bash
    Steps:
      1. Run refresh once and record cursor value
      2. Restart API/process
      3. Run refresh again and verify cursor continuity
    Expected Result: cursor remains; no storm
    Evidence: .sisyphus/evidence/task-10-cursor.txt
  ```

- [ ] 11. Query Generation Framework (Locale + Taxonomy Aware)

  **What to do**:
  - Replace scattered string templates with a single query planner that:
    - accepts `market_context` (language, region, industry taxonomy)
    - generates per-source query sets (news, funding, hiring, patents, etc)
    - records produced queries into run artifacts for explainability
  - Add localization: transliterations, language-specific keywords, and currency/date conventions.

  **Must NOT do**:
  - Hardcode a single year (e.g., “2025”) in queries; use time-window parameters.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `development/modern-javascript-patterns` (omit if Python-only), `code-quality/defense-in-depth`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocks**: Tasks 12-14
  - **Blocked By**: Tasks 6,7

  **References**:
  - `src/solstein/agents/web_search_agent.py` - current query templates
  - `src/solstein/data/web_search_client.py` - Exa/Google query templates
  - `src/solstein/infrastructure/data_loaders/additional_sources.py` - additional source queries

  **Acceptance Criteria**:
  - [ ] Generated queries are stored in the run manifest per company/source.
  - [ ] At least 2 locales (e.g., EN + one non-EN) have explicit query templates.

  **QA Scenarios**:
  ```
  Scenario: Locale-specific query sets are produced and persisted
    Tool: Bash
    Steps:
      1. Run enrichment for the same company with locale=en and locale=de (or other)
      2. Inspect run artifacts for query lists
    Expected Result: queries differ appropriately and are recorded
    Evidence: .sisyphus/evidence/task-11-queries.json
  ```

- [ ] 12. Source Credibility + Confidence Calibration

  **What to do**:
  - Introduce a source credibility registry (filings > audited reports > reputable press > scraped pages).
  - Calibrate confidence: cap confidence by source class + cross-source agreement; penalize contradictions.
  - Ensure LLM-generated text never increases factual confidence without supporting sources.

  **Must NOT do**:
  - Treat LLM prose as evidence.

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: `code-quality/root-cause-tracing`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocks**: Tasks 15-17
  - **Blocked By**: Tasks 9,11

  **References**:
  - `src/solstein/domain/models.py` - confidence + contradictions fields
  - `src/solstein/agents/web_search_agent.py` - raw source confidence defaults

  **Acceptance Criteria**:
  - [ ] Contradictory facts are preserved and surfaced with confidence adjustments.
  - [ ] Exported reports include citations + confidence for key claims.

  **QA Scenarios**:
  ```
  Scenario: Contradictions reduce confidence
    Tool: Bash
    Steps:
      1. Provide two fixtures with conflicting revenue values from different source classes
      2. Run aggregation + calibration
      3. Assert "current best" fact chooses higher credibility source and flags contradiction
    Expected Result: best fact selected with contradiction recorded
    Evidence: .sisyphus/evidence/task-12-calibration.json
  ```

- [ ] 13. Unified Fetch Layer: Rate Limits, Retries, Caching, and Backpressure

  **What to do**:
  - Centralize outbound HTTP behavior: retry policy, circuit breakers, timeouts, and concurrency limits.
  - Add caching for expensive calls (per provider) keyed by query + time window + locale.
  - Emit metrics/logs for throttling events and cache hits.

  **Must NOT do**:
  - Retry forever; all retries must have ceilings and budget awareness.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `code-quality/condition-based-waiting`, `code-quality/error-handling-patterns`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocks**: Tasks 17-20
  - **Blocked By**: Tasks 4,6

  **References**:
  - `src/solstein/agents/web_search_agent.py` - existing retry/circuit breaker usage
  - `src/solstein/config.py` - cache directory + Redis config
  - `src/solstein/data/web_search_client.py` - Exa/Google fallback behaviors

  **Acceptance Criteria**:
  - [ ] All external calls go through the unified fetch layer.
  - [ ] Cache reduces repeat calls for the same query/time window.
  - [ ] Rate limiting triggers graceful degrade rather than cascading failures.

  **QA Scenarios**:
  ```
  Scenario: Simulated 429 triggers backoff and circuit breaker
    Tool: Bash
    Steps:
      1. Configure a provider stub to return 429
      2. Run enrichment for 1 company
      3. Assert retries follow policy and circuit breaker opens after threshold
    Expected Result: run completes with coverage gaps recorded; no infinite retry
    Evidence: .sisyphus/evidence/task-13-rate-limit.txt
  ```

- [ ] 14. Prompt-Injection Hardening + Content Sanitization

  **What to do**:
  - Treat web/markdown as hostile content; sanitize before LLM use (strip scripts, cap size, normalize encoding).
  - Ensure prompts are tool-safe: never execute instructions found in retrieved content.
  - Persist sanitized inputs + prompt versions for reproducibility.

  **Must NOT do**:
  - Pass raw scraped HTML into LLM prompts.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `code-quality/defense-in-depth`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocks**: Tasks 15-20
  - **Blocked By**: Tasks 6,11

  **References**:
  - `src/solstein/exporters/markdown/generator.py` - LLM enhancement path
  - `src/solstein/analytics/filters/llm.py` - LLM filtering prompts and fallbacks

  **Acceptance Criteria**:
  - [ ] Adversarial content cannot change tool behavior or policy decisions.
  - [ ] Sanitization is applied consistently across all LLM entry points.

  **QA Scenarios**:
  ```
  Scenario: Adversarial page content is neutralized
    Tool: Bash
    Steps:
      1. Feed a fixture document containing "ignore previous instructions" and tool-invocation bait
      2. Run the LLM step
      3. Assert output ignores injected instructions and logs show sanitization applied
    Expected Result: safe behavior; injection detected/neutralized
    Evidence: .sisyphus/evidence/task-14-injection.txt
  ```

- [ ] 15. Market-Aware Scoring + Feature Store for Signals

  **What to do**:
  - Separate "feature extraction" (signals) from "scoring" with a persisted feature store per run.
  - Add market context (locale/currency/industry taxonomy) as explicit scoring inputs.
  - Support per-market calibration (thresholds, priors) and keep it versioned.

  **Must NOT do**:
  - Use one global threshold for Phoenix/Salt/Lead across all markets without calibration.

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: `code-quality/root-cause-tracing`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4
  - **Blocks**: Tasks 17-20
  - **Blocked By**: Tasks 5,12

  **References**:
  - `src/solstein/analytics/scoring.py` - current scoring entrypoints
  - `src/solstein/domain/models.py` - scoring explanation + signal models

  **Acceptance Criteria**:
  - [ ] Scores reference a feature set with provenance.
  - [ ] Calibration versions are recorded in run manifests.

  **QA Scenarios**:
  ```
  Scenario: Same company scored under two market calibrations
    Tool: Bash
    Steps:
      1. Run scoring with market=A calibration
      2. Run scoring with market=B calibration
      3. Assert output records calibration version and differences are explainable
    Expected Result: market context affects scoring predictably
    Evidence: .sisyphus/evidence/task-15-market-score.json
  ```

- [ ] 16. Coverage/Completeness Gates + Graceful Degradation

  **What to do**:
  - Define minimum evidence thresholds per score dimension.
  - If evidence is insufficient, mark scores as "insufficient_data" and surface coverage gaps.
  - Ensure exports include an explicit "coverage" section so clients understand uncertainty.

  **Must NOT do**:
  - Fill missing data with zeros that look like real measurements.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `code-quality/defense-in-depth`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4
  - **Blocks**: Tasks 18-20
  - **Blocked By**: Tasks 5,12

  **References**:
  - `src/solstein/agents/web_search_agent.py` - coverage gaps mechanism
  - `src/solstein/exporters/excel.py` - ensure coverage is visible in exports

  **Acceptance Criteria**:
  - [ ] Low-signal companies do not receive falsely precise scores.
  - [ ] Exports show coverage and missing-signal reasons.

  **QA Scenarios**:
  ```
  Scenario: Low-signal company triggers insufficient_data
    Tool: Bash
    Steps:
      1. Provide a fixture company with minimal fields and no enrichment sources
      2. Run scoring
      3. Assert classification is withheld or marked insufficient_data and coverage gaps are present
    Expected Result: safe degrade with transparent gaps
    Evidence: .sisyphus/evidence/task-16-coverage.json
  ```

- [ ] 17. Evaluation Harness: Golden Datasets + Drift + Performance/Cost Budgets

  **What to do**:
  - Create golden fixtures across multiple markets/languages/currencies with expected intermediate artifacts (queries, sources, facts, signals, scores).
  - Define measurable quality metrics (coverage ratio, rank stability, confidence calibration) and enforce minimum thresholds in CI.
  - Add drift monitoring: detect when scoring/extraction changes significantly due to code/model/prompt updates.

  **Must NOT do**:
  - Rely on manual spot checks as the only validation; scaling requires automated regression.

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: `testing/test-specialist`, `code-quality/verification-before-completion`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4
  - **Blocks**: Final Verification Wave
  - **Blocked By**: Tasks 5,11,12,15

  **References**:
  - `tests/` - existing unit/integration/data quality test structure
  - `pyproject.toml` - pytest configuration and coverage

  **Acceptance Criteria**:
  - [ ] `pytest tests/` runs a multi-market golden regression suite.
  - [ ] Drift checks fail loudly when score distributions change beyond configured thresholds.
  - [ ] Performance and cost budgets are measured and reported per run.

  **QA Scenarios**:
  ```
  Scenario: Golden dataset regression
    Tool: Bash
    Steps:
      1. Run: pytest tests/ -q
      2. Verify golden dataset tests pass and output a coverage summary
    Expected Result: PASS with reported metrics
    Evidence: .sisyphus/evidence/task-17-pytest.txt
  ```

- [ ] 18. Run Explorer API (Runs, Companies, Artifacts, Lineage)

  **What to do**:
  - Add API endpoints to list runs, inspect per-run status, and drill into per-company artifacts (queries, sources, facts, signals, scoring explanation, exports).
  - Link artifacts to citations and provenance so clients can click-through to evidence.
  - Ensure endpoints are secure (authz) and redact sensitive fields.

  **Must NOT do**:
  - Expose raw unredacted source payloads via public endpoints.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `development/api-design-principles`, `code-quality/error-handling-patterns`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 5
  - **Blocks**: Task 20
  - **Blocked By**: Tasks 1,2,5

  **References**:
  - `src/solstein/api/services/drill_down_service.py` - drill-down/audit trail patterns
  - `src/solstein/api/routers/` - existing router patterns
  - `src/solstein/domain/models.py` - audit trail and stage records

  **Acceptance Criteria**:
  - [ ] API provides endpoints: list runs, run detail, company detail, artifact list.
  - [ ] All responses include `run_id` and omit/redact sensitive content.

  **QA Scenarios**:
  ```
  Scenario: Inspect a run via API
    Tool: Bash (curl)
    Steps:
      1. Trigger a run
      2. Call run explorer endpoint: curl -sS http://localhost:8000/runs/<run_id>
      3. Assert response includes stage statuses + artifact references
    Expected Result: run is inspectable end-to-end
    Evidence: .sisyphus/evidence/task-18-run.json
  ```

- [ ] 19. Operator Dashboards (Coverage, Latency, Errors, Cost)

  **What to do**:
  - Create dashboards for:
    - Coverage/completeness by market/industry
    - Latency and failure rates by stage/provider
    - Rate limiting and budget usage
  - Prefer Grafana with Prometheus/OTel sources; document setup for local dev.

  **Must NOT do**:
  - Add dashboards that depend on unstable labels (raw URLs, unbounded company names).

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `infrastructure/grafana-dashboards`, `infrastructure/prometheus-configuration`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 5
  - **Blocks**: Final Verification Wave
  - **Blocked By**: Task 4

  **References**:
  - `src/solstein/api/routers/health.py` - metrics exposure patterns
  - `src/solstein/config.py` - env vars and runtime configuration

  **Acceptance Criteria**:
  - [ ] Dashboards can be imported and show non-empty metrics after a run.
  - [ ] A “Run Overview” dashboard can filter by `run_id`.

  **QA Scenarios**:
  ```
  Scenario: Metrics drive dashboards
    Tool: Bash
    Steps:
      1. Execute one run
      2. Confirm key metrics exist (stage durations, agent errors, coverage)
      3. Import dashboard JSON and verify panels render (documented steps)
    Expected Result: dashboard renders with data
    Evidence: .sisyphus/evidence/task-19-dashboard-import.txt
  ```

- [ ] 20. Export Provenance + Deliverable Bundles (Excel + Markdown + Manifest)

  **What to do**:
  - Embed provenance in exports: `run_id`, schema versions, calibration version, and citations for key claims.
  - Create a single deliverable bundle per run (zip): Excel dashboard + markdown reports + manifest + citations.
  - Ensure exports remain stable across locales (encoding, date/currency formatting).

  **Must NOT do**:
  - Produce exports that cannot be traced back to sources and signals.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `code-quality/verification-before-completion`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 5
  - **Blocks**: Final Verification Wave
  - **Blocked By**: Tasks 1,5,12,15,18

  **References**:
  - `src/solstein/exporters/excel.py` - add provenance sheets/fields
  - `src/solstein/exporters/markdown/generator.py` - add citations/provenance blocks
  - `src/solstein/api/routers/export.py` - export trigger and output paths

  **Acceptance Criteria**:
  - [ ] Export bundle includes Excel + markdown + manifest + citations.
  - [ ] Exports include coverage/completeness and confidence.
  - [ ] Bundle is reproducible given the same run artifacts.

  **QA Scenarios**:
  ```
  Scenario: Export bundle contains provenance
    Tool: Bash
    Steps:
      1. Trigger an export run
      2. Locate the produced bundle
      3. Verify Excel contains run_id and markdown contains citations
    Expected Result: provenance present and consistent
    Evidence: .sisyphus/evidence/task-20-bundle-check.txt
  ```

---

## Final Verification Wave

- [ ] F1. Plan compliance audit (oracle)
- [ ] F2. Code quality + safety checks
- [ ] F3. End-to-end QA run across 3 markets
- [ ] F4. Scope fidelity + cost budget validation

---

## Commit Strategy
- Prefer small, reversible commits per wave (observability first, then connectors, then scoring, then UI/export).

## Success Criteria
- End-to-end run creates a persisted `run_id` with: logs, traces, metrics, artifacts, lineage, and exports.
- New market/company types can be onboarded by adding a connector + taxonomy mapping—no core rewrites.
- Scores are explainable (citations + confidence) and regression-tested on golden datasets.
