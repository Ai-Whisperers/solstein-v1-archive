# Ivan Weiss Van Der Pol — PR Merge Audit
## `develop` branch · 2026-03-30

---

## Purpose

This document provides a comprehensive, categorised record of every pull request
reviewed and merged by **Ivan Weiss Van Der Pol** (`IvanWeissVanDerPol@github`)
into the `develop` branch, together with the branch synchronisation state as of
2026-03-30 and the current queue status for future development.

> **Role clarification**: Ivan is the human PR reviewer/merger.
> Implementation code was produced by the autonomous agents **Nyx**
> (`nyx@ai-whisperers.com`) and **Sisyphus / Agent Zero**
> (`agent-zero@solstein.ai`, `gesttaltt`).
> Ivan reviewed and approved 123 pull requests; the one direct commit he made
> was a housekeeping Work Checker run.

---

## Branch Sync Status

| Item | Value |
|---|---|
| Branch | `develop` |
| Local HEAD | `1fa28dc` (synced to remote) |
| Remote HEAD | `1fa28dc` |
| Divergence resolved | Yes — 4 local-only commits (content-identical to remote) discarded; remote is canonical |
| Uncommitted workspace changes | Backlog story annotations (stash-applied) |

### Divergence Root Cause

The autonomous worker (Sisyphus) ran the same documentation commits
simultaneously on local and remote, producing 4 divergent but content-identical
commits. Resolution: hard reset to `origin/develop`, stash pop.

---

## PRs Merged by Ivan — Chronological Order

Total: **123 merge commits**

---

### Phase 1 — Foundation & Config (PRs #1–#89)

| PR | Story / Description | Epic | Category |
|---|---|---|---|
| #1 | Initial quality improvements — phase 1 | — | Foundation |
| #68 | Full openclaw audit (recursive structural findings) | — | Audit |
| #71–#79 | Dependabot pip upgrades (protobuf, cachetools, pytz, websockets, production deps) | — | Dependency |
| #80 | STORY-137: Centralize all env vars in config.py | EPIC-036 | Config |
| #81 | STORY-138: Replace hardcoded `/home/ai-whisperers/` paths with config-driven paths | EPIC-036 | Config |
| #82 | STORY-140: Fix `.env.example` — add all 14 missing required variables | EPIC-036 | Config |
| #83 | STORY-141: Delete disconnected refresh router | EPIC-037 | Dead code |
| #84 | STORY-142: Delete orphaned `worker_tasks_v2.py` | EPIC-037 | Dead code |
| #85 | STORY-143: Audit and delete orphaned data layer files (−1,214 lines) | EPIC-037 | Dead code |
| #86 | STORY-165: Archive historical professionalization documents | EPIC-043 | Repo cleanup |
| #87 | STORY-166: Consolidate setup documentation | EPIC-043 | Repo cleanup |
| #88 | STORY-167: Organize strategic documents and call summaries | EPIC-043 | Repo cleanup |
| #89 | STORY-168: Create repository organization standards | EPIC-043 | Repo cleanup |

**Key fixes**: Eliminated 14 missing `.env.example` variables that caused new-developer startup failures. Removed 15+ hardcoded `/home/ai-whisperers/` paths. Purged 1,214 lines of orphaned dead code.

---

### Phase 2 — CLI Correctness & Security (PRs #90–#108)

| PR | Story / Description | Epic | Category |
|---|---|---|---|
| #90 | STORY-169: CLI JSON parsing tests (flat-list + wrapped-object formats) | EPIC-045 | CLI |
| #91 | STORY-170: Add `test_cli_llm_report.py` verifying LLM report command | EPIC-045 | CLI |
| #92 | STORY-171: Migrate CLI commands from deprecated `CompetitorDataLoader` | EPIC-045 | CLI |
| #93 | STORY-172: Add structured input validation with actionable error messages | EPIC-059 | Validation |
| #94 | STORY-174: Add null guard for `saas_maturity` in `CompetitivePositionScorer` | EPIC-046 | Scoring |
| #95 | STORY-204/205: Sparse company financial fix + refactor `convert_to_domain_company` under 100 lines | EPIC-058 | Data conversion |
| #96 | EPIC-064: Markdown integrity — fix broken links, retire mirror, scan placeholders | EPIC-064 | Docs integrity |
| #97 | STORY-067: Migrate authentication to Supabase Auth SDK | EPIC-020 | Auth |
| #98 | STORY-068: Remove auth bypass, wire Supabase JWT middleware | EPIC-020 | Auth |
| #99 | STORY-069: Opaque error responses with error_id correlation | EPIC-020 | Auth / Security |
| #100 | STORY-070: SSRF prevention with shared URL validation utility | EPIC-020 | Security |
| #101 | STORY-226: Domain-aware fetch policy matrix | EPIC-062 | Research |
| #102 | STORY-227: Extraction contract + unit normalisation + contradiction detection | EPIC-062 | Research |
| #103 | STORY-228: Field-level evidence ledger and provenance | EPIC-062 | Research |
| #104 | STORY-229: Freshness windows and export trust tiers | EPIC-062 | Research |
| #105 | STORY-063: Define Tenant model and domain object scoping | EPIC-019 | Multi-tenancy |
| #106 | STORY-064: Supabase RLS policies for all tenant-scoped tables | EPIC-019 | Multi-tenancy |
| #107 | STORY-065: Tenant-scoped API key management | EPIC-019 | Multi-tenancy |
| #108 | STORY-066: Enforce tenant isolation in all background research jobs | EPIC-019 | Multi-tenancy |

**Key fixes**: Full Supabase Auth migration (replacing custom JWT). SSRF prevention gate. Tenant isolation enforced end-to-end. CLI no longer crashes on wrapped JSON input.

---

### Phase 3 — Data Integrity & Semantic Layer (PRs #109–#119)

| PR | Story / Description | Epic | Category |
|---|---|---|---|
| #109 | STORY-014: Remove hardcoded date path from data loader | EPIC-004 | Data integrity |
| #110 | STORY-013: Fix conflict resolution to recency-first priority chain | EPIC-004 | Data integrity |
| #111 | STORY-127: Deduplicate `profit_margin` and employee fields | EPIC-033 | Export |
| #112 | STORY-125: Restore 20 dropped fields to Excel export | EPIC-033 | Export |
| #113 | STORY-126: Add export schema validation | EPIC-033 | Export |
| #114 | STORY-128: Document field lineage from ingestion to export | EPIC-033 | Export |
| #115 | STORY-080: pgvector extension + company embedding schema | EPIC-023 | Semantic search |
| #116 | STORY-081: Embedding generation for company profiles during research | EPIC-023 | Semantic search |
| #117 | STORY-082: Semantic similarity search endpoint | EPIC-023 | Semantic search |
| #118 | STORY-083: Research job status table and repository | EPIC-024 | Realtime |
| #119 | STORY-084: Supabase Realtime listener for job status updates | EPIC-024 | Realtime |

**Key fixes**: 20 previously dropped Excel export fields restored. Export schema validation gate added. Company embeddings (pgvector) and realtime job status streaming wired.

---

### Phase 4 — Modern LLM Stack & Agent Orchestration (PRs #120–#132)

| PR | Story / Description | Epic | Category |
|---|---|---|---|
| #120 | STORY-071: Replace custom LLM client with Anthropic SDK | EPIC-021 | LLM |
| #121 | STORY-072: Structured LLM outputs with Instructor | EPIC-021 | LLM |
| #122 | STORY-073: Langfuse integration — tracing, cost tracking, prompt management | EPIC-021 | LLM |
| #123 | STORY-074: LLM evaluation framework with Langfuse | EPIC-021 | LLM |
| #124 | STORY-075: Multi-provider LLM fallback with circuit breaking | EPIC-021 | LLM |
| #125 | STORY-076: Define LangGraph architecture and `ResearchState` schema | EPIC-022 | Orchestration |
| #126 | STORY-077: GraphExecutor with request deduplication and node error isolation | EPIC-022 | Orchestration |
| #127 | STORY-078: Replace 7 stub agents with real LangGraph nodes | EPIC-022 | Orchestration |
| #128 | STORY-079: LangGraph checkpointing + human-in-the-loop review gate | EPIC-022 | Orchestration |
| #129 | STORY-091: Set result expiry TTL — prevent Redis bloat | EPIC-025 | Worker |
| #130 | STORY-088: Fix in-memory DLQ — persist failed tasks to PostgreSQL | EPIC-025 | Worker |
| #131 | STORY-089/090: At-least-once delivery + Redis deduplication lock | EPIC-025 | Worker |
| #132 | STORY-092: Establish canonical `worker_tasks` import surface | EPIC-025 | Worker |

**Key fixes**: Custom LLM client replaced with Anthropic SDK. 7 stub agents replaced with real LangGraph nodes. Dead Letter Queue now persists to PostgreSQL (was in-memory). Redis result TTL prevents unbounded memory growth.

---

### Phase 5 — Docker, CI/CD & Observability (PRs #133–#143)

| PR | Story / Description | Epic | Category |
|---|---|---|---|
| #133 | STORY-093/094/095: Celery worker, beat, and flower services in `docker-compose` | EPIC-026 | Infrastructure |
| #134 | STORY-096: Multi-stage Dockerfile for production | EPIC-026 | Infrastructure |
| #135 | STORY-097: Automate Alembic migrations pre-deploy | EPIC-027 | CI/CD |
| #136 | STORY-098: Add `migrate-down`, `seed`, `deploy`, `help` Makefile targets | EPIC-027 | CI/CD |
| #137 | STORY-099: Staging smoke tests, rollback, and production gating | EPIC-027 | CI/CD |
| #138 | STORY-100: Add root-script CI gate + migration guide (delete bypass scripts) | EPIC-027 | CI/CD |
| #139 | STORY-047: Replace fake health checks with real infrastructure probes | EPIC-014 | Observability |
| #140 | STORY-049: Structured logging with correlation IDs | EPIC-014 | Observability |
| #141 | STORY-050: OpenTelemetry distributed tracing | EPIC-014 | Observability |
| #142 | STORY-051: Prometheus metrics scrape endpoint | EPIC-014 | Observability |
| #143 | STORY-086: Universal audit trail across all API endpoints | EPIC-014 | Observability |

**Key fixes**: Health checks were returning fake `{"status":"ok"}` — now probe real DB/Redis/Celery. Fake DLQ (in-memory) replaced. Correlation IDs added to all structured logs. Full OpenTelemetry trace propagation.

---

### Phase 6 — Export Pipeline & Business Intelligence (PRs #144–#160)

| PR | Story / Description | Epic | Category |
|---|---|---|---|
| #144 | STORY-111: Move exports to async Celery tasks | EPIC-030 | Export |
| #145 | STORY-112: Streaming Excel export with O(1) memory usage | EPIC-030 | Export |
| #146 | STORY-051: PrometheusMiddleware wire-up (metrics catalogue) | EPIC-014 | Observability |
| #147 | STORY-113: Export status tracking, list, cancel, expiry | EPIC-030 | Export |
| #148 | STORY-114: PDF export format with structured sections | EPIC-030 | Export |
| #149 | STORY-115: Supabase Storage backend for export files | EPIC-030 | Export |
| #150 | STORY-145: AI-Readiness Scoring Model — 4 sub-dimensions | EPIC-038 | AI Assessment |
| #151 | STORY-146: AI Transformation Readiness Calculator | EPIC-038 | AI Assessment |
| #152 | STORY-147: PE Due Diligence Integration Module | EPIC-038 | AI Assessment |
| #153 | STORY-148: Transformation Roadmap Generator | EPIC-038 | AI Assessment |
| #154 | STORY-149: Energy Compliance & Control Intelligence Module | EPIC-039 | Energy |
| #155 | STORY-150: Energy Market Forecasting & Demand Scoring | EPIC-039 | Energy |
| #156 | STORY-151: Trading Platform & Digital Infrastructure Assessment | EPIC-039 | Energy |
| #157 | STORY-152: Grid Integration & Smart Infrastructure Scoring | EPIC-039 | Energy |
| #158 | STORY-178: Map `funding_raised` to top-level funding fields on `Company` | EPIC-047 | Data loading |
| #159 | STORY-179: Expose `ebitda_margin` and `recurring_revenue_pct` on `Company` | EPIC-047 | Data loading |
| #160 | STORY-180: Field mapping parity test (JSON → Company) | EPIC-047 | Data loading |

**Key fixes**: Excel export now O(1) memory (streaming). Exports are async via Celery (no HTTP timeout risk). Full AI Readiness + Energy sector scoring modules added.

---

### Phase 7 — Report Quality & Exception Handling (PRs #161–#174)

| PR | Story / Description | Epic | Category |
|---|---|---|---|
| #161 | STORY-181: Fix report output path nesting and clean filenames | EPIC-048 | Reports |
| #162 | STORY-182: Round all score outputs to 2 decimal places | EPIC-048 | Reports |
| #163 | STORY-183: Fix market overview classification counters | EPIC-048 | Reports |
| #164 | STORY-184: Replace boilerplate deep analysis with signal-based strengths/weaknesses | EPIC-048 | Reports |
| #165 | STORY-185: Add report content quality assertions to tests | EPIC-048 | Reports |
| #166 | STORY-132: Exception handling standards doc + TRY ruff lint rules | EPIC-034 | Error handling |
| #167 | STORY-131: Null safety guards + `safe_div` applied to all scoring paths | EPIC-034 | Error handling |
| #168 | STORY-129: Eliminate silent `None` returns from LLM enhanced client | EPIC-034 | Error handling |
| #169 | STORY-130: Structured logging for all adapter exception handlers | EPIC-034 | Error handling |
| #170 | STORY-206: Add field range validators + scoring readiness check | EPIC-059 | Validation |
| #171 | STORY-207: `None`-safety with data confidence tracking in scorers | EPIC-059 | Validation |
| #172 | STORY-208: Wire confidence score preservation into scoring engine | EPIC-059 | Validation |
| #173 | STORY-209: Validation-before-scoring gate | EPIC-059 | Validation |
| #174 | STORY-210: Robustness tests for incomplete data inputs | EPIC-059 | Validation |

**Key fixes**: Report output paths were nested incorrectly (double-nesting). Score rounding was inconsistent. `safe_div` prevents ZeroDivisionError across all scoring paths. Confidence scores now preserved through entire pipeline.

---

### Phase 8 — External Services & Async HTTP (PRs #175–#185)

| PR | Story / Description | Epic | Category |
|---|---|---|---|
| #175 | STORY-101: Replace Google Custom Search with SearXNG meta-search | EPIC-028 | External |
| #176 | STORY-102: GDELT connector + news backend dispatcher | EPIC-028 | External |
| #177 | STORY-103: Financial backend dispatcher with circuit breaker | EPIC-028 | External |
| #178 | STORY-104: Slack and Email notification service | EPIC-028 | External |
| #179 | STORY-044: Convert autouse fixture to explicit opt-in (fix test masking) | EPIC-013 | Testing |
| #180 | STORY-045: Comprehensive scoring boundary tests for all tiers | EPIC-013 | Testing |
| #181 | STORY-046: Tests for adapter registry and instrumented wrappers | EPIC-013 | Testing |
| #182 | STORY-133: Replace sync `httpx` with async `httpx.AsyncClient` in GitHub Agent | EPIC-035 | Async |
| #183 | STORY-134: Replace `requests` with `httpx` in news and funding adapters | EPIC-035 | Async |
| #184 | STORY-135: Replace `requests` with `httpx` in Companies House + Website agents | EPIC-035 | Async |
| #185 | STORY-136: Async HTTP client guidelines, CI linting, pre-commit hook | EPIC-035 | Async |

**Key fixes**: Google Custom Search replaced with self-hosted SearXNG. All external HTTP clients migrated from blocking `requests` to async `httpx`. Autouse pytest fixture was masking test isolation failures.

---

### Phase 9 — Documentation Topology & LLM Tooling (PRs #186–#196)

| PR | Story / Description | Epic | Category |
|---|---|---|---|
| #186 | STORY-230: Canonical docs topology + ownership matrix | EPIC-063 | Docs |
| #187 | STORY-232: Epic directory naming convention + anomaly registry | EPIC-063 | Docs |
| #188 | STORY-233: Archival and deprecation metadata policy | EPIC-063 | Docs |
| #189 | STORY-231: Mirror retirement plan + dry-run report | EPIC-063 | Docs |
| #190 | STORY-055: Centralize all inline LLM prompt strings into managed registry | EPIC-017 | LLM tooling |
| #191 | STORY-056: Build LLM output evaluation harness | EPIC-017 | LLM tooling |
| #192 | STORY-242/243/244: Complete EPIC-065 in-progress stories | EPIC-065 | Docs lifecycle |
| #193 | STORY-238: Implement CI docs quality gates | EPIC-065 | Docs lifecycle |
| #194 | STORY-239: Add stale-doc detection and ownership alerts | EPIC-065 | Docs lifecycle |
| #195 | STORY-240: Docs review checklist and change-control workflow | EPIC-065 | Docs lifecycle |
| #196 | STORY-241: Publish docs health dashboard and weekly audit automation | EPIC-065 | Docs lifecycle |

**Key fixes**: Backlog mirroring (`backlog/` ↔ generated mirror) reconciled and mirror retired. All inline LLM prompts centralised. CI now gates PRs touching `docs/` with placeholder-token and staleness checks.

---

## Agent-Side Documentation Commits (Not PRs — Direct to `develop`)

These commits were pushed directly to `develop` by the Sisyphus autonomous worker
after Ivan merged the last batch:

| Commit | Description |
|---|---|
| `f44529e` | `docs/agent-cycles/` — 53 cycle reports (March 28–29, cycles #26–#079) |
| `d8158af` / `aeeff65` | `DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` — schema enforcement reality capture |
| `d3ac583` / `d773c35` | EPIC-010/012/036 README — typing & config evidence for Ivan handoff |
| `3c4c901` / `04e444b` | EPIC-021/023/024 README — schema contract evidence |
| `1526f45` / `e807211` | EPIC-059/013/046/034 README — validation gate evidence |
| `1fa28dc` | Refresh `DOCS_HEALTH.json` / `DOCS_HEALTH.md` generated artifacts |

*(The `d8158af`/`aeeff65` pairs and similar are content-identical commits that
diverged because the worker ran on local and remote simultaneously. Resolved by
reset to remote canonical.)*

---

## Thematic Summary of Fixes Applied

| Theme | Stories | Impact |
|---|---|---|
| Configuration & secrets | STORY-006/007/008/137/138/139/140 | Startup no longer fails for new developers; no more hardcoded paths |
| Dead code removal | STORY-141/142/143/144 | −1,214+ lines; orphaned router and V2 tasks gone |
| Security: Auth | STORY-067/068/069/070 | Full Supabase JWT; SSRF prevention; opaque error responses |
| Multi-tenancy | STORY-063/064/065/066 | RLS policies; tenant-scoped research jobs and API keys |
| Data integrity | STORY-012/013/014 | Dual-write atomicity; recency-first conflict resolution |
| Export correctness | STORY-125/126/127/128 | 20 dropped fields restored; schema validation; lineage |
| Worker reliability | STORY-088/089/090/091/092 | Persistent DLQ; Redis dedup lock; TTL; canonical task surface |
| LLM stack | STORY-071/072/073/074/075 | Anthropic SDK; Instructor; Langfuse; multi-provider fallback |
| Agent orchestration | STORY-076/077/078/079 | LangGraph; real nodes (was stubs); checkpointing; HITL gate |
| Observability | STORY-047/049/050/051/086 | Real health probes; correlation IDs; OTel; Prometheus |
| Async HTTP | STORY-133/134/135/136 | All external I/O migrated to `httpx` async |
| Scoring quality | STORY-131/206/207/208/209/210 | `safe_div`; confidence preservation; validation gate |
| Report quality | STORY-181/182/183/184/185 | Path nesting fixed; rounding; signal-based analysis |
| Docs lifecycle | STORY-230/231/232/233/238/239/240/241/242/243/244/245 | CI gates; staleness detection; health dashboard; mirror retired |

---

## Current Queue State (as of 2026-03-30)

### Active / READY

| Story | Epic | Title | Notes |
|---|---|---|---|
| STORY-245 | EPIC-065 | Expand Generated API Docs and Schema Registries | First available READY item |
| STORY-116 | EPIC-031 | Centralize All Retry/Backoff in `core/retry_policy.py` | Can run in parallel with STORY-245 |
| STORY-117 | EPIC-031 | Fix Circular Import Risk — Introduce `shared/` package | Can run in parallel |
| STORY-118 | EPIC-031 | Formalize CLI as proper package entrypoint | Can run in parallel |
| STORY-119 | EPIC-031 | Split `unified_loader.py` into separate modules | Can run in parallel |
| STORY-120 | EPIC-031 | Enforce UTC timezone policy across all modules | Can run in parallel |

### BLOCKED

| Story/Epic | Blocker |
|---|---|
| EPIC-066 (STORY-246/247/248/249) | Waiting for STORY-245 + EPIC-031 to complete |
| STORY-057 | Blocked on STORY-059 (Dockerfile verification) |
| STORY-058 | Blocked on STORY-057 + STORY-039 |
| EPIC-052 (STORY-198/199/200/201) | Story files newly canonicalized; re-evaluate queue before starting |

### Complete

All 120+ stories across M1–M12 milestones are DONE.

---

## Strict Working Rules for Next Agent (Ivan or Autonomous)

Per `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md`:

1. Read `planning/QUEUE.md` first — it is the live execution order.
2. Read the autonomy audit second — it corrects stale backlog badges.
3. Read the canonical epic README and story file.
4. Read `docs/reference/ENGINEERING_GUARDRAILS.md` before implementation.
5. Do not start EPIC-066 until STORY-245 and EPIC-031 are complete.
6. Every story must produce a durable artefact: regression test, schema gate, AST rule, or generated reference update.
7. Do not broaden scope beyond the queued story.

---

*Generated: 2026-03-30 · Branch: `develop` · Author: Claude Sonnet 4.6 (Code audit)*
