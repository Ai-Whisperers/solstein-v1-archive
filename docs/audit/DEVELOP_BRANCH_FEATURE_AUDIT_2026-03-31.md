# Develop Branch Feature Audit - 2026-03-31

## Scope

This audit reviews `develop` relative to `master`, using:

- `planning/QUEUE.md` as the canonical shipped/ready feature ledger
- `docs/active/backlog/*` and `backlog/EPICS/*` for intended behavior
- `git log master..develop` for feature wave chronology
- existing project audits in `docs/audit/`
- story and subsystem tests under `tests/`

This is a branch audit, not a claim that all features are production-clean. `develop` contains a large amount of delivered functionality plus a smaller set of still-open contract/runtime defects.

## Current State Summary

### Verified branch-level strengths

- `develop` has shipped major platform capability across auth, tenancy, research orchestration, export pipeline modernization, retrieval, async adapters, observability, and domain-specific analytics.
- The branch also added broad regression coverage. Most delivered stories have dedicated `test_story*.py` coverage or equivalent subsystem tests.
- The repo now carries machine-checkable docs/AST guardrails and a generated audit index, which materially improves future auditability.

### Verified branch-level risks still open

| Area | Current reality on `develop` | Impact |
|---|---|---|
| Audit hotfix queue | `STORY-250`, `251`, `252`, `253`, `254` are still `READY`, not done | Boundary/schema/runtime contract hardening is incomplete |
| Test collection hygiene | Prior audit found pure pytest collection required manual `DATABASE__URL` injection | Unit tests still have import-time env coupling |
| Export contract | Queue explicitly says exporter still fails its own schema gate | Export-schema promises are ahead of runtime reality |
| Boundary schemas | Queue explicitly says extra fields can still survive or disappear silently at ingress | Silent data loss / silent acceptance still possible |
| Structured LLM contracts | Queue explicitly says empty structured payloads can still validate as success | False-positive extraction success remains possible |
| Docs strictness | Prior audit found `mkdocs build --strict` failing | Documentation gate not fully green |
| Makefile/dev UX | Prior audit found `make dashboard`, `make install`, `make lint` broken because `dashboard/` is absent | Claimed workflows are not universally runnable |

## Audit Interpretation Rules

For each feature below:

- `Expected behavior` describes what the story/epic says the branch should do.
- `Edge cases / QA analysis` focuses on numerical thresholds, null/empty behavior, failure handling, or test evidence.
- `Evidence` names the strongest implementation/test anchors found during review.

## Feature Ledger

### Security, Identity, Tenancy, Auditability

| Story | Feature | Expected behavior | Edge cases / QA analysis | Evidence |
|---|---|---|---|---|
| STORY-067 | Supabase Auth migration | Auth should use Supabase SDK/session flow instead of permissive custom auth | Verify invalid credentials reject cleanly, token absence blocks access, expired tokens fail closed | `tests/unit/test_story067_supabase_auth.py` |
| STORY-068 | JWT middleware wiring | Protected routes should require Supabase JWT validation and remove bypass paths | Edge case: mixed public/private routes; missing/invalid bearer token must return sanitized auth failure, not stack traces | `tests/unit/test_story068_jwt_middleware.py`, `tests/integration/test_auth_endpoints.py` |
| STORY-069 | Error sanitization and input hardening | API should return opaque errors with correlation/error IDs, not internals | Edge case: validation failures vs unexpected exceptions should remain distinguishable without leaking stack data | `tests/unit/test_story069_error_handling.py`, `tests/unit/test_error_envelope.py` |
| STORY-070 | SSRF prevention | URL-driven web/website agents should reject localhost, link-local, private-network and malformed targets | Edge cases: redirects, odd schemes, embedded credentials, IP literals | `tests/unit/test_story070_ssrf_prevention.py` |
| STORY-063 | Tenant model and scoping | Domain/runtime objects should carry tenant context explicitly | Edge case: missing tenant context must not silently default to global scope | `tests/unit/test_story063_tenant_model.py`, `tests/unit/test_tenant_isolation.py` |
| STORY-064 | Supabase RLS | Tenant-scoped tables should enforce row isolation in DB policy layer | Edge case: cross-tenant reads/writes must fail even if application code is wrong | `tests/unit/test_story064_rls_policies.py` |
| STORY-065 | Tenant-scoped API keys | API keys should belong to one tenant, be auditable, and be revocable/rotatable | Edge cases: expired/revoked keys, wrong-tenant usage, usage logging | `tests/unit/test_story065_api_key_management.py` |
| STORY-066 | Tenant isolation in jobs | Background jobs should preserve tenant boundaries end-to-end | Edge case: async/worker retries must not lose tenant context or read global data | `tests/unit/test_tenant_isolation.py`, `tests/unit/test_worker_tasks_isolated.py` |
| STORY-086 | Universal audit trail | Authenticated data-returning API calls should emit audit records consistently | Edge case: audit logging failure must not 500 the original request; append-only semantics matter | `tests/unit/test_story086_universal_audit_trail.py` |
| STORY-047 | Real health checks | Health endpoints should probe real dependencies, not return fake green | Edge case: degraded dependency should produce degraded/unhealthy signal deterministically | `tests/unit/test_story047_health_checks.py` |
| STORY-049 | Correlation IDs | Request/log chain should carry correlation IDs across API flows | Edge case: generated IDs when caller omits one; header propagation across middleware | `tests/unit/test_story049_correlation_ids.py` |
| STORY-050 | OpenTelemetry tracing | Distributed traces should wrap request/worker boundaries and key operations | Edge case: trace context continuity across async/background boundaries | `tests/unit/test_story050_opentelemetry_tracing.py` |
| STORY-051 | Prometheus metrics | Metrics endpoint and runtime counters should expose system health/activity | Edge cases: label cardinality, exporter presence, middleware instrumentation | `tests/unit/test_story051_prometheus_metrics.py` |

### Core Data Integrity, Conversion, Validation, Scoring

| Story | Feature | Expected behavior | Edge cases / QA analysis | Evidence |
|---|---|---|---|---|
| STORY-012 | Dual-write atomicity | Research persistence should avoid partial primary/outbox corruption | Highest-risk edge: failure between sequential writes should not leave dangling outbox state | Queue marks done; verify again before trusting for prod migrations |
| STORY-013 | Conflict resolution repair | Resolution should prefer recency/reliability rather than arbitrary merge | Numerical edge: tie-breaking when source confidence/recency are close; manual-review path must not be silent no-op | `tests/unit/test_story013_conflict_resolution.py` |
| STORY-014 | Hardcoded path removal | Data loading should not depend on one date/market path literal | Edge case: unknown date/market should fail clearly or resolve via config, not silently empty | `tests/unit/test_story014_hardcoded_paths.py` |
| STORY-169 | CLI JSON parsing fix | CLI commands should accept both flat list and wrapped-object input formats | Edge case: wrapped `{competitors:[...]}`, flat `[...]`, malformed payloads, empty list | `tests/unit/test_cli_json_parsing.py` |
| STORY-170 | LLM report import repair | `generate-llm-report` should no longer crash on renamed/missing exporter import | Edge case: command should fail with actionable message if upstream provider/config is absent | `tests/unit/test_cli_llm_report.py` |
| STORY-171 | CLI migration off deprecated loader | CLI should use canonical loader surface rather than deprecated code paths | Edge case: command parity with prior output and no `DeprecationWarning` under normal use | `tests/unit/test_cli.py` |
| STORY-172 | CLI structured validation | CLI should reject malformed inputs with actionable error text | Edge cases: missing files, invalid JSON, wrong top-level shape, empty datasets | `tests/unit/test_cli_validation.py` |
| STORY-173 | Threat-level derivation | `threat_level` should be derived from scored classification/composite, not stale input JSON | Numerical edge: threshold boundaries must map consistently on every scoring path | Queue verification plus scoring tests |
| STORY-174 | `saas_maturity` null guard | Scoring should not crash when `saas_maturity` is `None` | Edge case: `None` must degrade gracefully, not silently coerce to misleading max/min | `tests/unit/test_epic046_scoring_correctness.py` |
| STORY-175 | Dead scoring-method removal | Only live scoring code paths should remain, reducing false-maintenance surfaces | QA value is indirect: reviewers should no longer be able to edit unused `_calculate_*` paths | Queue verification, scoring path tests |
| STORY-176 | Authoritative classification mapping | Classification to threat-level mapping should live in one constants surface | Numerical edge: exact boundary mapping should remain deterministic for every tier | `tests/unit/test_scoring_boundaries.py`, queue verification |
| STORY-177 | `ai_score` fidelity | Float `ai_score` should not truncate during load | Numerical edge: preserve decimals rather than int-cast | Queue note plus loader tests |
| STORY-178 | Funding mapping | `funding_raised` should populate top-level/company financial funding fields | Numerical edge: preserve EUR totals, valuation, rounds, investors; absent funding should remain explicit `None`, not zero | `tests/unit/test_story178_funding_mapping.py` |
| STORY-179 | EBITDA and recurring-revenue exposure | Company model should expose `ebitda_margin_pct` and `recurring_revenue_pct` to scoring/reporting layers | Numerical edge: percentage fields should preserve 0-100 semantics and bonus logic should not overcount | `tests/unit/test_story179_profitability_exposure.py` |
| STORY-180 | Field parity test | Loader should have parity checks between raw JSON and Company object | QA significance is high: catches silent field drop regressions across formats | `tests/unit/test_story180_field_mapping_parity.py` |
| STORY-125 | Export dropped-field restoration | Export workbook should include previously lost competitive-intelligence fields | Edge cases: sparse companies, nested arrays/sheets, top-level vs financial duplication | `tests/unit/test_story125_restore_dropped_fields.py` |
| STORY-126 | Export schema validation | Export output should validate against explicit workbook/schema contract | Current open risk: queue says exporter still fails its own schema gate; this story exists but runtime parity is incomplete | `tests/unit/test_story126_export_schema_validation.py`, hotfix `STORY-250` |
| STORY-127 | Deduplicate employee/profit fields | One authoritative write path should feed duplicate-looking business fields | Numerical edge: `employee_count` vs `employees`, `profit_margin` surfaces should stay synchronized | `tests/unit/test_story127_deduplicate_fields.py` |
| STORY-128 | Field lineage documentation | There should be a documented ingestion-to-export map for fields | QA value is traceability; useful for audits and export regressions, not direct runtime behavior | `tests/unit/test_story128_field_lineage_ci.py`, `docs/field-lineage.md` |
| STORY-181 | Report path repair | All generated reports should land in one company directory, not nested duplicates | Edge case: slug/path sanitation and repeated generation | `tests/unit/test_report_paths.py` |
| STORY-182 | Score rounding in reports | Reports should present scores rounded to 2 decimals | Numerical edge: consistent half-up/formatting behavior for values like `7.138888...` | `tests/unit/test_report_score_rounding.py` |
| STORY-183 | Market classification counters | Market overview should count Phoenix/Salt/Lead correctly | Numerical edge: zero-company market, repeated classification categories, partial lists | `tests/unit/test_market_classification_counters.py` |
| STORY-184 | Signal-based deep analysis | Deep-analysis report sections should derive strengths/weaknesses from real signals | Edge case: sparse signal set should avoid boilerplate and still remain specific | `tests/unit/test_deep_analysis_signals.py` |
| STORY-185 | Report content quality assertions | Tests should assert content quality, not only file existence | QA significance: protects against regressions that still "generate a file" but say nothing useful | `tests/unit/test_report_content_quality.py` |
| STORY-202 | Unified JSON-to-company conversion | Conversion should route through one canonical extractor path | Edge case: mixed flat/nested source payloads and sparse inputs | `tests/unit/test_unified_converter_story_202.py` |
| STORY-203 | Format auto-detection | Converter should detect flat vs nested revenue/growth/profit fields | Numerical edge: conflicting flat and nested values need deterministic precedence | Queue verification |
| STORY-204 | Confidence preservation from lineage | `metric_lineage` confidence should feed `signal_confidences` | Numerical edge: confidence weights like `0.72` should survive conversion instead of collapsing to default `1.0` | queue note, `tests/unit/test_story208_confidence_preservation.py` covers adjacent runtime use |
| STORY-205 | Golden-dataset verification | Converter should stay green against representative real/sparse datasets | QA significance: protects against format regressions and sparse-company crashes | `tests/unit/test_golden_dataset_story_205.py` |
| STORY-206 | Company field validation | Company model should enforce readiness/range validation instead of allowing arbitrary empty state | Numerical edge: require meaningful primary indicators such as revenue or employees; range guards matter for percentages and counts | `tests/unit/test_story206_company_validation.py` |
| STORY-207 | None-safe scorers | Growth/competitive scorers should skip or degrade cleanly on `None` | Edge case: missing growth inputs should not classify everything as low-value by accident | `tests/unit/test_story207_none_safety_scorers.py` |
| STORY-208 | Confidence-aware scoring | Confidence from lineage should influence scoring and narrative outputs | Numerical edge: default confidence fallback noted as `0.50`; weighting must not invert or exceed `1.0` | `tests/unit/test_story208_confidence_preservation.py` |
| STORY-209 | Validation before scoring | Conversion/scoring boundary should fail fast before invalid Company objects flow downstream | Edge case: partial company with too many missing fields should stop early rather than die at export | `tests/unit/test_story209_validation_before_scoring.py` |
| STORY-210 | Robustness tests for incomplete data | Sparse/incomplete inputs should have explicit regression coverage | QA significance: this is a confidence story, proving degraded-mode behavior remains intentional | `tests/integration/test_robustness_incomplete_data.py`, `tests/unit/test_story_210_robustness.py` |
| STORY-250 | Export schema/workbook reconciliation | Workbook output and export schema should exactly match | Current status `READY`; this is the clearest remaining develop gap in the export surface | `planning/QUEUE.md` |
| STORY-251 | Strict boundary schemas | Connector/API/domain ingress should reject undeclared fields unless explicitly aliased | Current status `READY`; this is the clearest remaining anti-silent-drop boundary gap | `planning/QUEUE.md`, EPIC-059 README |
| STORY-252 | Structured LLM contract tightening | Empty structured extraction payloads should be rejected, not marked success | Current status `READY`; important because structured-output stack is otherwise mature | `planning/QUEUE.md` |
| STORY-253 | Behavioral contract tests | Runtime behavior should be tested directly, not inferred from source text | Current status `READY`; needed because source-inspection tests missed actual regressions | `planning/QUEUE.md` |
| STORY-254 | Env-decoupled test collection | Unit test import paths should not require manual env injection for collection | Current status `READY`; needed to make the test suite trustworthy in isolation | `planning/QUEUE.md` |

### Research Pipeline, Retrieval, LLM, Agent Runtime

| Story | Feature | Expected behavior | Edge cases / QA analysis | Evidence |
|---|---|---|---|---|
| STORY-071 | Anthropic SDK migration | LLM client should use supported provider SDK instead of custom brittle path | Edge cases: provider auth failure, timeouts, response-shape mismatches | `tests/unit/test_story071_anthropic_sdk.py` |
| STORY-072 | Structured outputs with Instructor | LLM extractions should validate into explicit schemas | Edge case: partial/empty structured payloads remain a known open hardening gap via `STORY-252` | `tests/unit/test_story072_instructor_outputs.py` |
| STORY-073 | Langfuse integration | LLM calls should emit tracing/cost/prompt metadata | Edge case: tracing should fail soft if Langfuse is unavailable | `tests/unit/test_story073_langfuse_integration.py` |
| STORY-074 | LLM evaluation framework | Repo should support repeatable LLM eval datasets/runs | QA significance: improves model/output regression detection rather than user-facing runtime | `tests/llm_eval/test_eval_framework.py` |
| STORY-075 | Provider fallback and circuit breaking | LLM runtime should fail over between providers without thrashing | Numerical edge: backoff, breaker-open thresholds, degraded provider health | `tests/unit/test_story075_multi_provider_fallback.py` |
| STORY-076 | LangGraph architecture/state schema | Research orchestration should have explicit graph state contracts | Edge case: invalid/missing state transitions should be structurally detectable | `tests/unit/test_story076_langgraph_architecture.py` |
| STORY-077 | Coordinator migration to graph executor | Runtime orchestration should dedupe requests and isolate node failures | Edge case: one node failing should not collapse whole graph when isolation says continue | `tests/unit/test_story077_coordinator_migration.py` |
| STORY-078 | Real agent nodes | Stub nodes should be replaced with real GitHub/news/website/etc. graph nodes | Edge cases: per-node external failures, empty returns, node prerequisites | `tests/unit/test_story078_real_agent_nodes.py` |
| STORY-079 | Checkpointing and HITL | Graph runs should checkpoint and support human review/resume | Edge case: resume from persisted checkpoint with partial node completion | `tests/unit/test_story079_checkpointing.py` |
| STORY-080 | pgvector schema | Embedding storage/schema should exist in Postgres | Numerical edge: embedding dimension/index correctness and extension availability | `tests/test_pgvector_schema.py` |
| STORY-081 | Embed during research | Research pipeline should generate and persist embeddings as part of normal flow | Edge case: embedding failure should be observable and not corrupt company persistence | `tests/test_embeddings.py` |
| STORY-082 | Semantic search endpoint | API should support similarity search over company embeddings | Numerical edge: top-k ordering, empty corpus, similarity threshold handling | `tests/test_semantic_search.py` |
| STORY-083 | Research job status table | Job status should be persisted for async/realtime consumers | Edge case: terminal states, retries, missing jobs | `tests/test_research_jobs.py` |
| STORY-084 | Realtime job subscriptions | Clients should receive job state changes without polling | Edge case: reconnect/subscription replay and no-update idle periods | `tests/test_realtime_listener.py` |
| STORY-101 | SearXNG web search | Search should use SearXNG as primary backend with fallback/cache behavior | Edge case: backend unavailable, empty result set, timeout, fallback to legacy provider | `tests/unit/test_story101_searxng.py` |
| STORY-102 | GDELT + RSS news | News aggregation should use GDELT primary and RSS supplement | Edge cases: duplicate articles, stale feeds, empty GDELT responses | `tests/unit/test_story102_gdelt_rss.py` |
| STORY-103 | Yahoo Finance stability | Finance refresh should degrade gracefully behind circuit breaker/freshness checks | Numerical edge: freshness SLA, breaker-open behavior, stale quote handling | `tests/unit/test_story103_yahoo_finance.py` |
| STORY-104 | Slack/email notifications | Notification dispatcher should send or suppress alerts by channel/config | Edge cases: opt-out, webhook failure, SMTP failure, partial channel availability | `tests/unit/test_story104_notifications.py` |
| STORY-133 | Async GitHub agent | GitHub acquisition should use async HTTP rather than blocking sync calls | Edge case: high-latency remote should not serialize whole event loop | `tests/unit/agents/test_github_agent_async.py` |
| STORY-134 | Async news/funding adapters | News and funding adapters should use async HTTP paths | Edge case: concurrent adapter fan-out and partial timeout behavior | `tests/unit/adapters/test_news_funding_async.py` |
| STORY-135 | Async Companies House/website | Website and Companies House paths should be async-safe | Edge case: redirect-heavy or slow websites should not block unrelated tasks | `tests/unit/agents/test_ch_website_async.py` |
| STORY-136 | Async HTTP guidelines and linting | CI/tooling should catch sync HTTP use in async paths | QA significance: prevents architectural regression after the adapter migration | `tests/unit/test_story136_banned_imports.py` |
| STORY-145 | AI-readiness scoring | Platform should score AI readiness across defined dimensions | Numerical edge: component weighting, sparse-data scoring, score band boundaries | `tests/unit/test_story145_ai_readiness.py` |
| STORY-146 | Transformation calculator | Platform should compute transformation readiness/actionability outputs | Numerical edge: threshold math and weighted dimension totals | `tests/unit/test_story146_transformation_calculator.py` |
| STORY-147 | PE due diligence module | System should surface diligence red flags/checklists/memos | Edge case: contradictory or missing evidence should remain explicit, not fabricated | `tests/unit/test_story147_due_diligence.py` |
| STORY-148 | Transformation roadmap generator | System should generate phased transformation roadmap output | Edge cases: sparse company context, industry-specific branching, missing prerequisites | `tests/unit/test_story148_roadmap_generator.py` |
| STORY-149 | Energy compliance scoring | Energy companies should be assessed on regulatory/compliance posture | Numerical edge: compliance subscore weighting and violation/certification handling | `tests/unit/test_story149_energy_compliance.py` |
| STORY-150 | Energy forecasting/demand scoring | Energy analytics should score forecasting and demand intelligence | Numerical edge: forecast quality bands and demand-signal normalization | `tests/unit/test_story150_energy_market_forecasting.py` |
| STORY-151 | Trading platform/digital infra assessment | Energy/market companies should be scored for trading/digital infrastructure maturity | Edge cases: on-prem vs digital hybrid models, partial infra evidence | `tests/unit/test_story151_trading_infrastructure.py` |
| STORY-152 | Grid/smart infrastructure scoring | Energy companies should be scored for grid integration and smart infra capability | Numerical edge: grid-integration factor weighting and sparse-signal handling | `tests/unit/test_story152_grid_infrastructure.py` |
| STORY-226 | Fetch policy matrix | Source acquisition should use domain-aware fetch policy and retry rules | Edge case: trusted vs untrusted domains, retryable vs non-retryable failures | `tests/unit/research/test_fetch_policy.py` |
| STORY-227 | Extraction contract and normalization | Numeric extraction should normalize units and flag contradictions | Numerical edge: k/M/B units, percent normalization, conflicting source values | `tests/unit/research/test_numeric_normalization.py` |
| STORY-228 | Evidence ledger | Enriched fields should carry field-level provenance lineage | Edge case: missing source metadata and multi-source field merge | `tests/unit/research/test_evidence_ledger.py` |
| STORY-229 | Freshness/trust tiers | Export/scoring quality should consider evidence freshness and trust tiers | Numerical edge: freshness windows, trust-tier mapping, stale evidence downgrade | `tests/unit/research/test_freshness_trust.py` |

### Export Pipeline, Workers, Runtime Topology, Delivery Infrastructure

| Story | Feature | Expected behavior | Edge cases / QA analysis | Evidence |
|---|---|---|---|---|
| STORY-088 | Durable DLQ | Permanently failed tasks should persist durable failure records | Edge case: worker restart must not erase failure history | `tests/unit/test_story088_persistent_dlq.py` |
| STORY-089 | `acks_late` / worker-lost rejection | Worker delivery semantics should reduce task loss on crash | Edge case: task redelivery after crash must remain safe | `tests/unit/test_story089_090_acks_late_idempotency.py` |
| STORY-090 | Idempotency/dedup lock | Duplicate task execution should be prevented or made harmless | Edge case: lock TTL and duplicate submissions close in time | `tests/unit/test_story089_090_acks_late_idempotency.py` |
| STORY-091 | Result-expiry TTL | Celery/Redis result storage should expire to prevent bloat | Numerical edge: TTL value long enough for consumers but finite for hygiene | `tests/unit/test_story091_result_expiry_ttl.py` |
| STORY-092 | Canonical worker task file | One worker task module should remain canonical | QA value is maintenance safety; prevents split task registration surfaces | `tests/unit/test_story092_worker_tasks_canonical.py` |
| STORY-093 | Worker service in compose | Local stack should include Celery worker service | Edge case: startup ordering and service health dependencies | `tests/unit/test_story093_docker_compose.py` |
| STORY-094 | Beat service in compose | Scheduled task service should exist in compose topology | Edge case: duplicate scheduler instances and config parity | Queue entry, compose verification story group |
| STORY-095 | Flower monitoring service | Worker monitoring UI/service should be wired into compose | Edge case: optionality and secure exposure in non-dev envs | Queue entry, compose verification story group |
| STORY-096 | Multi-stage Dockerfile | Production image should build reproducibly with smaller runtime stage | Edge case: missing runtime deps between builder and final stage | `tests/unit/test_story096_dockerfile.py` |
| STORY-097 | Automated migrations pre-deploy | Deployment flow should run Alembic migrations deterministically before app start | Edge case: failed migration must block deploy cleanly | `tests/unit/test_story097_migrations.py` |
| STORY-098 | Makefile targets | Common migrate/seed/deploy targets should exist | Current caveat: other Makefile paths still fail on absent `dashboard/`; feature is partly useful but not full dev-UX closure | `tests/unit/test_story098_makefile_targets.py`, prior audit |
| STORY-099 | Staging deploy + smoke test | CI/CD should deploy to staging and run post-deploy verification | Edge case: auth-protected health/smoke endpoint behavior | `tests/unit/test_story099_staging_smoke_test.py` |
| STORY-100 | Delete bypass scripts | Root scripts that bypass API/auth/audit should be removed | QA significance: closes unobserved operational path that could mutate data without trace | `tests/unit/test_story100_delete_bypass_scripts.py` |
| STORY-111 | Async export tasks | Export generation should run as async/background Celery jobs | Edge case: job failure/status updates and duplicate submission behavior | `tests/unit/test_story111_async_export_celery.py` |
| STORY-112 | Streaming Excel export | Large exports should stream/write without loading whole workbook in memory | Numerical edge: workbook size/row volume behavior under large datasets | `tests/unit/test_story112_streaming_excel.py` |
| STORY-113 | Export status/download links | Export jobs should expose status and downloadable artifact references | Edge case: failed/expired/missing artifact states | `tests/unit/test_story113_export_status_tracking.py` |
| STORY-114 | PDF export | Export pipeline should generate PDF output with expected sections | Edge cases: section omission with sparse data, formatting consistency | `tests/unit/test_story114_pdf_export.py`, `tests/unit/test_story114_pdf_sections.py` |
| STORY-115 | Supabase Storage backend | Export artifacts should persist in Supabase Storage | Edge case: storage upload failure and signed-link generation | `tests/unit/test_story115_storage_backend.py`, `tests/unit/test_story115_pipeline_integration.py` |

### Configuration, Dead-Code Cleanup, Documentation and Quality Gates

| Story | Feature | Expected behavior | Edge cases / QA analysis | Evidence |
|---|---|---|---|---|
| STORY-006 | Duplicate config field removal | Config classes should not shadow validators/fields with duplicate definitions | QA significance: removes silent override behavior | Queue verification |
| STORY-007 | Hardcoded credential removal | Security-sensitive config should have no known-default secrets/URLs | Edge case: startup should fail if required secrets missing | Queue verification |
| STORY-008 | Startup validation for keys | Required config should validate at startup, not hours into runtime | Edge case: optional providers should warn, not hard-fail | Queue verification |
| STORY-137 | Env var centralization | Active env vars should be represented in config surface | Edge case: missing config docs vs runtime usage drift | queue and `config.py` |
| STORY-138 | Config-driven paths | Runtime should resolve paths without `/home/...` literals | Edge case: different environments/OS paths | `tests/unit/test_story138_paths.py` |
| STORY-139 | Timeout centralization | Timeouts/magic numbers should be controlled centrally | Numerical edge: avoid per-module drift; verify timeouts are not silently zero/unbounded | `tests/unit/test_story139_timeouts.py` |
| STORY-140 | `.env.example` completeness | Onboarding env template should include required variables | Edge case: stale example vs real startup requirements | `tests/unit/test_story140_env_example.py` |
| STORY-141 | Delete disconnected refresh router | Non-mounted orphan router should be removed | QA significance: shrinks false attack surface and route confusion | queue verification |
| STORY-142 | Remove orphaned worker task file | Duplicate/orphan task file should not mislead maintainers | QA significance: maintenance safety only | queue verification |
| STORY-143 | Remove orphaned data files | Unused data-layer files should be deleted after audit | QA significance: lowers ghost-surface risk; validate callers were truly absent | `docs/deletions/STORY-143-orphaned-data-files.md` |
| STORY-144 | Dead-code CI job | CI should continuously detect unused/dead code drift | QA significance: prevents re-accumulation after audit-based cleanup | queue plus workflow files |
| STORY-044 | Test fixture masking fix | Autouse fixture behavior should no longer hide real runtime/test failures | QA significance is high because false-green tests are worse than missing tests | queue verification |
| STORY-045 | Scoring boundary tests | Tier boundaries should have explicit regression coverage | Numerical edge: exact boundary values for classifications | `tests/unit/test_scoring_boundaries.py` |
| STORY-046 | Untested-core-module tests | Previously uncovered modules should have baseline tests | QA significance: expands coverage into registry/instrumentation seams | `tests/unit/test_adapter_registry.py`, `tests/unit/test_instrumented_adapter.py` |
| STORY-129 | Classified LLM exceptions | Enhanced LLM client should classify and observe exception types | Edge case: provider vs validation vs timeout vs unknown exceptions | `tests/unit/test_story129_classified_exceptions.py` |
| STORY-130 | Structured adapter logging | Adapter exceptions should log through consistent structured helper | Edge case: log context should include adapter identity and failure class | `tests/unit/test_story130_adapter_logging.py` |
| STORY-131 | Safe division helpers | Division operations should not explode on `None`/zero denominators | Numerical edge: zero denominator, `None`, and percentage helpers | `tests/unit/test_story131_safe_div.py` |
| STORY-132 | Exception-handling standards | Repo should define exception-handling policy and lint hooks | Caveat: prior audit found policy tooling/test expectations not fully self-consistent yet | `tests/unit/test_lint_exception_handling.py`, prior audit |
| STORY-165 | Archive historical docs | Historical root docs should move to archive | QA is repo hygiene, not runtime | queue verification |
| STORY-166 | Consolidate setup docs | Setup guidance should reduce duplication | Caveat: still validate against real runnable Make targets and current infra | queue verification |
| STORY-167 | Organize strategic docs | Strategic/call-summary materials should be reorganized coherently | QA is doc discoverability | queue verification |
| STORY-168 | Repository organization standards | Repo should have documented file-placement standards | QA is governance/maintainability | queue verification |
| STORY-230 | Canonical docs topology | Docs tree should have one authoritative topology and ownership matrix | QA is governance: useful for future audits and stale-doc control | queue verification |
| STORY-231 | Backlog mirror-resolution plan | Mirrored backlog trees should have explicit sync/migration plan | Caveat: queue notes destructive phases still need separate approval-gated change | queue verification |
| STORY-232 | Epic directory naming normalization | Epic directories should follow one naming convention | QA is navigation/governance | queue verification |
| STORY-233 | Archival/deprecation metadata policy | Docs should carry lifecycle metadata | QA is documentation honesty/staleness control | queue verification |
| STORY-238 | Docs quality gates | CI should fail on markdown/link/front-matter policy violations | Edge case: policy false positives need clear allowlist mechanism | queue verification, workflows |
| STORY-239 | Stale-doc detection | CI/reporting should flag stale maintained docs and ownership gaps | Edge case: generated vs maintained docs must not be conflated | queue verification |
| STORY-240 | Docs review checklist | Docs changes should follow review/change-control workflow | QA is process governance, not runtime | queue verification |
| STORY-241 | Docs health dashboard | Repo should publish docs-health metrics and weekly automation | Edge case: dashboard artifacts must be generated, not hand-edited | queue verification |
| STORY-242 | AST rule catalog | Repo should generate machine-readable AST guardrail registry | QA significance: structural constraints become inspectable and cheaper to audit | generated AST artifacts |
| STORY-243 | Master audit issue index | Master audit should have generated MD/JSON issue index | QA significance: cheaper, machine-usable defect tracking | `docs/audit/generated/MASTER_AUDIT_ISSUE_INDEX.md` |
| STORY-244 | Generated-doc freshness enforcement | Git hooks/CI should block stale generated docs | Caveat: strict docs gate still has remaining blockers on `develop` | queue verification, prior audit |

## High-Value Deep Dives

### 1. Validation and contract maturity is real but incomplete

`develop` clearly moved from permissive, ad-hoc payload handling toward typed boundaries:

- validation before scoring exists
- confidence preservation exists
- evidence ledger/freshness tiers exist
- export schema validation exists

The remaining gap is consistency at all ingress/egress seams. The queue hotfixes are accurate: contract enforcement is not yet end-to-end. The branch still needs:

- exact workbook/schema parity
- strict extra-field policy
- rejection of empty structured LLM "success"
- behavior-first tests and env-decoupled test collection

### 2. Reporting/export quality improved materially, but this surface still deserves distrust-first QA

The export/report area saw the deepest corrective wave:

- async exports
- streaming Excel
- status tracking
- PDF export
- storage backend
- restored fields
- schema validation
- report-path fix
- rounding
- counter repair
- signal-based deep analysis
- content-quality tests

That is a strong improvement. It is also the area where the queue still records a live contract mismatch. This is the highest-priority user-facing re-verification surface.

### 3. Research/runtime architecture is much deeper than the older branch state

Compared with `master`, `develop` now has:

- typed graph state
- graph executor
- real graph nodes
- checkpointing/HITL
- pgvector retrieval
- realtime job status
- async-first adapters
- fetch policy / normalization / evidence ledger / freshness trust

This is substantial system depth, not cosmetic churn. The risk has shifted from "feature absent" to "feature-rich system with several remaining contract seams."

### 4. Documentation and quality automation are now a platform feature in their own right

The branch added:

- docs quality gates
- stale-doc detection
- docs review workflow
- docs dashboard
- AST rule catalog
- generated audit index
- generated-doc freshness enforcement

This meaningfully improves future maintainability. The remaining issue is gate credibility: strict-docs failures and broken Make targets show that some claimed workflows still need reconciliation with reality.

## Recommended Next Audit Order

If the goal is depth-first QA rather than breadth-first description, the next passes should be:

1. `STORY-250` export schema/workbook reconciliation
2. `STORY-251` strict ingress-boundary schemas
3. `STORY-252` reject empty structured-output success
4. `STORY-254` remove env-coupled import/test collection side effects
5. `STORY-253` replace source-inspection tests with behavioral contract tests

## Bottom Line

`develop` is no longer a thin feature branch. It is a large platform expansion with real depth across identity, tenancy, export, search, orchestration, observability, domain scoring, and docs automation.

The correct reading is:

- many major features are present and test-backed
- the branch still has a small but important set of unfinished trust-boundary repairs
- the most important remaining risks are not "missing capability" but "mismatch between declared contract and runtime truth"
