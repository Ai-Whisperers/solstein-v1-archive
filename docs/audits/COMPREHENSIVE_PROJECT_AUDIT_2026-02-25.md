# Solstein — Comprehensive Project Audit

**Date:** February 25, 2026
**Auditors:** gesttaltt (human), Sisyphus (AI orchestrator)
**Reference:** DATA_PIPELINE_AUDIT_2026-02-23.md (190+ issues), CODEBASE_AUDIT_REPORT.md (20 issues), 4 prior audits
**Branch:** master @ 64444d3
**Scope:** Full project assessment — architecture, intelligence capabilities, quality infrastructure, PE/VC mission readiness

---

## Thesis

Solstein aims to be a Competitive Intelligence platform for Private Equity and Venture Capital, where **quality is not a feature but a structural particularity** of the solution. If the product's intelligence isn't trustworthy, explainable, and auditable, it has no reason to exist — a PE firm making acquisition decisions based on unreliable data faces catastrophic financial risk.

This audit evaluates the entire project against that standard.

---

## 1. Verdict

| Dimension | Grade | Summary |
|-----------|-------|---------|
| **Vision & Strategy** | A | Clear market positioning, differentiated value proposition, realistic business model |
| **Domain Modeling** | B- | CompanyResearch model is comprehensive but has validation gaps, unit confusion, duplicate fields |
| **Data Pipeline** | D | Only 3 of 13 data sources are wired; pipeline never run to full completion on disk |
| **Intelligence Quality** | F | Fabricated patent counts, keyword-based AI maturity, no factual validation, no cross-source verification |
| **Codebase Architecture** | D | ~87% dead code; 3 duplicate module trees; 2 disconnected pipelines; 2 divergent enum definitions |
| **Test Coverage** | D+ | 69 test files exist but cover <30% of modules; critical paths untested; CI billing expired |
| **Security** | F | Anonymous DB write access, plaintext API keys, CSV injection, no input sanitization |
| **Documentation** | B+ | 75+ files, 15,000+ lines, mostly accurate after our corrections, but describes features that don't work |
| **Deployment Readiness** | F | No lockfile, no Docker production config, no monitoring, broken DB schema-ORM alignment |
| **PE/VC Mission Fitness** | D | Beautiful concept, functional scoring math, but underlying data is too unreliable for investment decisions |

**Overall: The product is a well-documented prototype with strong vision but critical structural quality deficits that make it unfit for PE/VC decision-making in its current state.**

---

## 2. What Actually Works

These components are functional and tested:

| Component | Status | Evidence |
|-----------|--------|----------|
| Scoring math (GrowthScorer) | ✅ Works | Deterministic formulas, 35 passing unit tests |
| Classification (Phoenix/Salt/Lead) | ✅ Works | Score thresholds applied correctly |
| Excel export (4-sheet dashboard) | ✅ Works | Generates workbook with rankings and financials |
| Yahoo Finance data fetch | ✅ Works | yfinance library pulls real market data |
| FastAPI application scaffold | ✅ Works | 8 routers, health check, OpenAPI docs |
| Company domain model | ✅ Works | Pydantic model with 40+ fields |
| Provenance validation (structural) | ✅ Works | Checks source presence, not factual accuracy |
| Contradiction detection | ✅ Works | Flags >20% numeric divergence across sources |
| Evidence readiness scoring | ✅ Works | Weighted formula producing 0-100 readiness score |
| ConflictResolutionEngine | ✅ Exists | Implemented, integrated into aggregate.py, untested |
| Confidence calibration | ✅ Exists | Implemented, untested in pipeline context |
| 12 refresh connectors | ✅ Exist | Written, untested, never invoked by pipeline |

---

## 3. What Doesn't Work

### 3.1 The Dead Code Problem (CRITICAL)

**151 Python source files. ~29,800 lines of code. The pipeline uses approximately 10 of them.**

| Layer | Files | Lines | Status |
|-------|-------|-------|--------|
| `adapters/` (protocols, registry, 20 enrichment adapters) | 24 | ~4,200 | **DEAD** — never imported by pipeline |
| `agents/` (coordinator, github, web_search, etc.) | 9 | ~3,200 | **DEAD** — never imported by pipeline |
| `application/` (duplicate agents, analytics, exporters) | 8 | ~1,500 | **DEAD** — duplicate of agents/, also never imported |
| `infrastructure/connectors/` (12 refresh connectors) | 12 | ~2,400 | **DEAD** — referenced only by worker_tasks.py which is never started |
| `infrastructure/` (refresh, conflict, confidence, registry) | 8 | ~2,800 | **DEAD** — exists but pipeline doesn't call it |
| `data/` (web_search, patent, additional_sources) | 5 | ~1,800 | **DEAD** — capabilities exist, never wired in |
| `analytics/` (scorers/, signals/, simulation/, workflows) | 10 | ~3,500 | **MOSTLY DEAD** — only scoring.py is used |
| **Subtotal dead code** | **~76** | **~19,400** | **65% of all source code is dead** |

The actual pipeline (`research/pipeline.py`) imports:
1. `research/discovery.py` — hardcoded company catalogs
2. `research/gather.py` — yfinance enrichment
3. `research/evidence.py` — readiness scoring
4. `research/reconcile.py` — contradiction detection
5. `extractors/markdown_extractor.py` — provenance validation
6. `analytics/scoring.py` — score calculation
7. `exporters/excel.py` — Excel dashboard
8. `data/loaders.py` — competitor_data.json loading
9. `data/fetchers.py` — Yahoo Finance (partially)
10. `config.py` — settings

**Everything else exists in isolation.** The adapters, agents, refresh connectors, unified registry, conflict resolution, confidence calibration, web search, patent search, news aggregation, LinkedIn enrichment — all dead.

### 3.2 The Data Source Void

What a PE/VC firm needs vs what actually runs:

| Intelligence Domain | PE/VC Need | Source In Code | Actually Used | Status |
|---------------------|-----------|----------------|---------------|--------|
| Financial statements | CRITICAL | yfinance | ✅ Yes | Partial — no SEC/Companies House filings |
| Revenue & growth | CRITICAL | yfinance + catalog | ✅ Yes | Unit mismatch (millions vs absolute) corrupts scores |
| Market positioning | HIGH | Hardcoded catalogs | ✅ Yes | Static, stale, 40 companies total |
| Patent portfolio | HIGH | patent_client.py | ❌ Dead code | Fabricates counts (×3, ×5 multipliers) |
| News & sentiment | HIGH | additional_sources.py | ❌ Dead code | Flawed sentiment (word lists, no context) |
| Competitive landscape | HIGH | Discovery catalogs | ✅ Partial | Capped at 49 companies (energy) or 20 (others) |
| Team/leadership | HIGH | LinkedIn adapter | ❌ Dead code | Placeholder, no real integration |
| Technology assessment | MEDIUM | GitHub agent | ❌ Dead code | Never invoked by pipeline |
| Funding history | HIGH | Crunchbase adapter | ❌ Dead code | Placeholder |
| Website intelligence | MEDIUM | Website adapter | ❌ Dead code | Never invoked |
| Deal flow signals | HIGH | None | ❌ Doesn't exist | No deal sourcing capability |
| Portfolio monitoring | HIGH | None | ❌ Doesn't exist | No temporal tracking |
| Comparable analysis | HIGH | Overlap scorer | ⚠️ Buggy | Score can exceed 1.0 (§S-4) |
| Due diligence support | CRITICAL | None | ❌ Doesn't exist | No DD workflow |

**11 of 13 data source capabilities are dead code. The pipeline runs on hardcoded catalogs + yfinance only.**

### 3.3 Data Fabrication

The system invents data and presents it as sourced intelligence. This is disqualifying for PE/VC use.

| What Is Fabricated | Where | How |
|--------------------|-------|-----|
| Patent counts | patent_client.py:177,229 | Multiplied by 3× or 5× arbitrarily |
| AI maturity | gather.py:24-39 | Keyword scan: "digital" → MODERATE |
| SaaS maturity | gather.py:303 | Hardcoded `5` for all companies |
| Tier (fallback) | gather.py:116 | Hardcoded `TIER_3` |
| Threat level (fallback) | gather.py:117 | Hardcoded `MEDIUM` |
| Region | discovery.py:495 | Hardcoded `"NL/EU"` |
| Tags | discovery.py:500 | Hardcoded `["energy", "software"]` |
| Industry | loaders.py:273 | Hardcoded `"Energy Software"` for ALL companies |
| Publication dates | additional_sources.py:185 | `datetime.now()` when missing |
| Source attribution | gather.py:79-86 | URLs attributed BEFORE data is fetched |

**No fabricated value is flagged as estimated or synthetic. All flow into scoring as if they were sourced facts.**

### 3.4 Revenue Unit Mismatch (CRITICAL)

The most impactful single bug in the system:

| Data Path | Revenue Unit | Effect on Score |
|-----------|-------------|-----------------|
| `competitor_data.json` via loaders | EUR millions | Revenue 30 → correctly below 100M threshold |
| yfinance via gather.py | Absolute (USD raw) | Revenue 30,000,000 → incorrectly exceeds 100M threshold |
| Scoring thresholds | "In Millions" per config comments | Revenue 100.0 means €100M |

**yfinance companies are systematically over-scored on every revenue-based metric.** A company with €30M revenue gets the "large company" bonus because the scorer compares 30,000,000 against 100.0.

### 3.5 Currency Conversion Bugs

| Issue | Impact |
|-------|--------|
| EUR→USD pair direction inverted for 5 currencies (JPY, CNY, HKD, INR, BRL) | All conversions for these currencies produce reciprocal values |
| Cross-rate formula inverted (`to_usd / from_usd` should be `from_usd / to_usd`) | Every cross-currency conversion is wrong |
| USD hardcoded as 1.0 in loaders (USD ≠ EUR) | All USD amounts overstated by ~8-9% |
| No cache TTL on rates | Multi-hour runs use stale rates |
| KRW and MXN missing from rate fetches | Silently default to 1.0 |

---

## 4. Architecture Assessment

### 4.1 Module Map (What Exists)

```
src/solstein/           151 files, 29,763 lines
├── adapters/           24 files  — Clean architecture layer (DEAD - never imported)
│   ├── discovery/      3 files   — Discovery source adapters
│   ├── enrichment/     14 files  — Enrichment adapters (original + 6 unified)
│   ├── protocols.py    — EnrichmentSource, UnifiedDataSource protocols
│   └── registry.py     — SourceRegistry (DEAD)
├── agents/             9 files   — AI agents (DEAD - never imported by pipeline)
├── analytics/          12 files  — Scoring, signals, simulation (mostly dead)
│   ├── scoring.py      — GrowthScorer (ALIVE - used by pipeline)
│   ├── scorers/        3 files   — Individual scorer modules (DEAD)
│   └── signals/        2 files   — Signal extraction (DEAD)
├── api/                12 files  — FastAPI application
│   ├── routers/        8 files   — REST endpoints (ALIVE but untested)
│   └── routes/         1 file    — refresh.py (split from routers/)
├── application/        8 files   — DUPLICATE of agents/ + analytics/ (DEAD)
├── core/               5 files   — Monitoring, config, Supabase client
├── data/               10 files  — Data fetchers, loaders, clients
│   ├── fetchers.py     — Yahoo Finance (ALIVE)
│   ├── loaders.py      — competitor_data.json (ALIVE)
│   └── others          — web_search, patents, news (DEAD)
├── domain/             5 files   — Company, RawDataSource, Facts models
├── exporters/          4 files   — Excel, markdown, LLM, audit_report
├── extractors/         1 file    — Markdown profile extraction
├── infrastructure/     20 files  — Database, refresh, conflict resolution
│   ├── connectors/     12 files  — Refresh connectors (DEAD)
│   └── others          — DB, dual-write, retry, registry (mostly dead)
├── monitoring/         1 file    — Continuous monitoring (DEAD)
├── research/           10 files  — Pipeline, discovery, gather, scoring pipeline
│   └── pipeline.py     — THE ACTUAL PIPELINE (ALIVE)
└── utils/              1 file    — Logging
```

### 4.2 Three Duplicate Module Trees

| Original | Duplicate | Both Dead? |
|----------|-----------|------------|
| `agents/base_agent.py` | `application/agents/base_agent.py` | Yes |
| `agents/github_agent.py` | `application/agents/github_agent.py` | Yes |
| `agents/companies_house_agent.py` | `application/agents/companies_house_agent.py` | Yes |
| `agents/web_search_agent.py` | `application/agents/web_search_agent.py` | Yes |
| `agents/resilience.py` | `application/agents/resilience.py` | Yes |
| `analytics/filters/llm.py` | `application/analytics/filters/llm.py` | Yes |
| `exporters/llm.py` | `application/exporters/llm.py` | Yes |
| `data/additional_sources.py` | `infrastructure/data_loaders/additional_sources.py` | Yes |
| `data/patent_client.py` | `infrastructure/data_loaders/patent_client.py` | Yes |

### 4.3 Two Disconnected Pipelines

| Pipeline | Entry Point | Data Sources | Output | Ever Run? |
|----------|-------------|-------------|--------|-----------|
| **Pipeline A** (Discovery) | `pipeline.py` → `discover_and_research_market.py` | Hardcoded catalogs + yfinance | JSON + Excel | Only via demo script (5 companies) |
| **Pipeline B** (Markdown) | `run_market_pipeline.py` → `BatchExtractor` | 55 pre-gathered .md files | JSON + Excel | **Never** (no output artifacts exist) |

Neither pipeline calls the other. 55 hand-gathered markdown profiles sit unused.

### 4.4 Two Divergent Enum Definitions

| File | Enum | Values |
|------|------|--------|
| `constants.py` | `CompanyTier` | TIER_1, TIER_1B, TIER_2, TIER_3 |
| `domain/models.py` | `CompanyTier` | TIER_1, TIER_2, TIER_3, TIER_4 |

TIER_1B exists only in constants. TIER_4 exists only in models. Code importing from the wrong module gets incompatible values.

---

## 5. Quality Infrastructure

### 5.1 Test Coverage

| Metric | Value |
|--------|-------|
| Source files | 151 |
| Test files | 69 |
| Source lines | 29,763 |
| Test lines | 14,163 |
| Test:Source ratio | 0.48:1 |
| Unit tests | 54 files |
| Integration tests | 7 files |
| Data quality tests | 1 file |
| Modules with ZERO tests | `application/`, `utils/`, most of `infrastructure/connectors/` |

**Critical untested paths:**
- Currency conversion (inverted formulas)
- Revenue unit normalization
- yfinance success/failure paths in gather.py
- All 12 refresh connectors
- Conflict resolution integration
- Excel export data loss (0.0 → "N/A")
- API router classification logic
- End-to-end pipeline data consistency

### 5.2 CI/CD

| Component | Status |
|-----------|--------|
| GitHub Actions CI | ❌ Billing expired — all runs fail |
| GitHub Actions (6 workflows) | Exist: ci.yml, ci-12stage.yml, mutation.yml, release.yml, sbom.yml, docs.yml |
| Pre-commit hooks | ❌ None configured |
| Dependency lockfile | ❌ None (all deps use `>=` floor-only pinning) |
| mypy type checking | ⚠️ Effectively disabled — checks 4 files, 13 error codes suppressed |
| Ruff linting | ✅ Configured but E501 ignored |
| Test automation | ❌ Cannot run — billing expired |

### 5.3 Security

| Risk | Location | Severity |
|------|----------|----------|
| Anonymous full INSERT/UPDATE on companies table | RLS policy in 001_companies.sql | CRITICAL |
| All API keys as plaintext `str` (not `SecretStr`) | config.py:63-66, 172-181 | HIGH |
| DB credentials in process list | apply_supabase_migrations.py:26-36 | HIGH |
| Excel formula injection | excel.py:219+ — unsanitized company names | MEDIUM |
| No input sanitization on company names | patent_client, web_search, additional_sources | MEDIUM |
| Hardcoded default credentials | config.py:26 — `postgres:postgres` | HIGH |

### 5.4 Database Schema-ORM Alignment

| Issue | Impact |
|-------|--------|
| ORM uses `Integer` PK; SQL migration uses `UUID` | Complete incompatibility |
| ORM column `last_updated` vs SQL column `updated_at` | Wrong column reads/writes |
| ORM uses `Float`; SQL uses `NUMERIC` | Precision loss |
| ORM uses `JSON`; SQL uses `JSONB` | Different indexing/query behavior |
| 4 ORM tables have no migration file | Schema drift |
| ORM has 30+ columns absent from SQL | Insert failures on production DB |

---

## 6. Documentation vs Reality

| Documentation Claims | Actual State |
|---------------------|-------------|
| "5+ data sources feeding scoring" | 1 data source (yfinance) feeds scoring; catalog is static |
| "Processes 50+ companies in <2 days" | Max 49 companies (energy), 20 (anything else), never run to completion |
| "Full signal chain visible" | Fabricated data (patent ×5, AI from keywords) mixed with real data, no distinction |
| "90 Tests Passing" badge in README | CI billing expired; 66 tests fail due to missing deps |
| "Coverage 57%" badge in README | Cannot verify — CI doesn't run |
| "Celery Workers" badge in README | Worker tasks exist but celery_config never started |
| "Interactive dashboard" | No frontend exists — dashboard/ is Next.js scaffold with no data integration |
| "Quarterly refreshes" | No refresh mechanism runs; 12 connectors are dead code |
| "Data coverage: 8% → 40%" (.sisyphus plans) | Still at 8% — plans never executed |

---

## 7. PE/VC Mission Fitness Assessment

### What a PE/VC Competitive Intelligence Platform Must Deliver

| Requirement | Weight | Solstein Status | Gap |
|-------------|--------|----------------|-----|
| **Trustworthy financial data** | CRITICAL | ⚠️ yfinance works but unit mismatch corrupts scores | Revenue unit normalization needed |
| **Multi-source verification** | CRITICAL | ❌ Single source (yfinance) + static catalogs | 11 data sources exist as dead code |
| **Explainable scoring** | HIGH | ✅ Score breakdowns exist with reasoning strings | Works but reasoning cites fabricated inputs |
| **Auditable data lineage** | CRITICAL | ❌ Sources attributed before fetch; fabricated data unmarked | False provenance chains |
| **Scalable company universe** | HIGH | ❌ Hard cap at 49 companies; no dynamic discovery | Static catalogs only |
| **Data freshness** | HIGH | ❌ All data is fetch-once; no refresh runs | Refresh system dead code |
| **Cross-source conflict resolution** | MEDIUM | ⚠️ Engine exists, untested, integrated in aggregate.py | Needs tests and pipeline wiring |
| **Comparable analysis** | HIGH | ⚠️ Overlap scorer exists but can exceed 1.0 | Bug fix needed |
| **Due diligence workflow** | HIGH | ❌ No DD support | Not implemented |
| **Portfolio monitoring** | MEDIUM | ❌ No temporal tracking | Not implemented |
| **Deal sourcing signals** | HIGH | ❌ No deal flow detection | Not implemented |

### The Quality Paradox

Solstein's documentation and business narrative are **genuinely excellent**. The pitch materials, case study, and README convey a compelling product story. The scoring math is sound. The classification system (Phoenix/Salt/Lead) is clever and PE-relevant.

But the gap between narrative and reality is the core quality problem:

- The README says "5+ sources feeding scoring" — actually 1
- The architecture diagram shows adapters, agents, connectors — none are wired in
- The scoring produces numbers, but from data that is partially fabricated
- The explainability is beautiful, but explains scores derived from keyword-matching and hardcoded defaults
- The pipeline "works" but has never run to completion on a real market at scale

**For a platform where quality is structural, this gap is existential.** A PE firm trusting Solstein's current output could make investment decisions based on:
- Revenue numbers in wrong currency units
- AI maturity scores from keyword matching ("digital banking" → MODERATE)
- Patent portfolios multiplied by arbitrary constants
- Competitive positions based on 20-company static catalogs with acquired/defunct entries

---

## 8. Issue Census

### From Previous Audits (Resolved)

| ID | Description | Status |
|----|-------------|--------|
| ISSUE-003 | EnrichmentSource protocol break | ✅ Fixed (session 1) |
| ISSUE-008 | Documentation status falsification | ✅ Fixed (session 1) |
| ISSUE-009 | DOCUMENTATION_AUDIT claims items missing that exist | ✅ Fixed (session 2) |
| ISSUE-010 | STRUCTURE.md wrong file paths | ✅ Fixed (session 2) |
| ISSUE-011 | QUICK-REFERENCE.md wrong class paths | ✅ Fixed (session 2) |
| ISSUE-012 | DOCUMENTATION_MAINTENANCE.md wrong year | ✅ Fixed (session 2) |
| ISSUE-019 | Deleted developer config files | ✅ Fixed (session 1) |
| Yahoo extraction | Flat keys instead of nested CompanyResearch.model_dump() | ✅ Fixed (session 1) |
| Timestamp bug | Literal "timezone.utc" string in audit_report.py | ✅ Fixed (session 1) |

### Open Issues by Priority

#### P0 — Fix Before Any Pipeline Run

| # | Issue | Source | Severity |
|---|-------|--------|----------|
| 1 | Revenue unit mismatch (millions vs absolute) | §31.1, S-1, S-2 | CRITICAL |
| 2 | Currency rate inversions (5 currencies wrong) | F-1, F-2 | CRITICAL |
| 3 | USD = 1.0 in loaders (should be ~0.92) | L-1 | CRITICAL |
| 4 | Schema-ORM PK type mismatch (Integer vs UUID) | DB-1 | CRITICAL |
| 5 | Hardcoded year "2025" in web search queries | W-1 | CRITICAL |
| 6 | Patent count fabrication (×3, ×5 multipliers) | PT-1, PT-2 | CRITICAL |
| 7 | "patent" as AI keyword inflates all AI counts to 100% | PT-3, PT-4 | HIGH |
| 8 | All quality gates disabled by default (all None) | P-1 | HIGH |
| 9 | Test DB URL generation bug (_test after port, not DB name) | CF-4 | HIGH |

#### P1 — Fix Within Sprint

| # | Issue | Source | Severity |
|---|-------|--------|----------|
| 10 | Single bad candidate crashes entire pipeline | P-2, P-3 | HIGH |
| 11 | Pydantic model has no bounds on financial fields | DM-1..12 | HIGH |
| 12 | Excel scores written as strings, not numbers | EX-1 | HIGH |
| 13 | Excel 0.0 displays as "N/A" (truthiness check) | EX-2, EX-3 | HIGH |
| 14 | Excel formula injection (unsanitized company names) | EX-4 | MEDIUM |
| 15 | API router classifies on growth_score not composite | §31.3 | HIGH |
| 16 | ORM columns don't match SQL migrations | DB-2..6 | HIGH |
| 17 | Duplicate CompanyTier enum (constants.py vs models.py) | §4.4 | HIGH |
| 18 | Anonymous write access to companies table | DB-17 | HIGH |
| 19 | API keys as plaintext str, not SecretStr | CF-2, CF-3 | HIGH |
| 20 | Duplicate agent implementations (agents/ vs application/) | ISSUE-016 | MEDIUM |
| 21 | API routes split (routers/ vs routes/) | ISSUE-018 | MEDIUM |
| 22 | CI/CD billing expired — no automated tests run | ISSUE-001 | BLOCKING |
| 23 | 66 pre-existing test failures (missing deps) | ISSUE-002 | MEDIUM |

#### P2 — Fix Within Quarter

| # | Issue | Source | Severity |
|---|-------|--------|----------|
| 24 | Wire existing data sources into pipeline | §38.3 | HIGH |
| 25 | Enable mypy on full codebase | PY-3 | MEDIUM |
| 26 | Add dependency lockfile | PY-2 | MEDIUM |
| 27 | Unify slugification across entry points | §31.4 | MEDIUM |
| 28 | Remove dead code / consolidate into working pipeline | §3.1 | MEDIUM |
| 29 | Normalize all datetime usage to UTC | §34.1 | MEDIUM |
| 30 | Add pool_recycle and pool_pre_ping to DB engines | DB-11 | MEDIUM |
| 31 | Replace broad `except Exception` with specific catches | §24.1 | MEDIUM |
| 32 | Add migration idempotency and tracking | DB-14, DB-15 | MEDIUM |
| 33 | Write tests for refresh connectors (12 untested) | ISSUE-005 | MEDIUM |
| 34 | Write tests for worker_tasks.py | ISSUE-006 | LOW |
| 35 | CI/CD guide is a stub (56 lines) | ISSUE-013 | LOW |
| 36 | Examples directory has no runnable code | ISSUE-014 | LOW |

#### P3 — Backlog

| # | Issue | Source |
|---|-------|--------|
| 37 | Replace keyword-based AI maturity with LLM classifier | §24.3 |
| 38 | Add URL liveness checks to evidence scoring | §7.2 |
| 39 | Add multi-source financial data for cross-validation | §38.4 |
| 40 | Implement source credibility tiers | §10.2 |
| 41 | Replace Google scraping with legitimate API alternatives | A-3 |
| 42 | Add end-to-end data consistency integration tests | TC-4 |
| 43 | Implement dynamic company discovery via external APIs | §40.3 |
| 44 | Connect Pipeline B (markdown) to Pipeline A (discovery) | §38.1 |
| 45 | Implement deal sourcing / portfolio monitoring | §7 |

---

## 9. Quantitative Summary

| Metric | Value |
|--------|-------|
| Total source files | 151 |
| Total source lines | 29,763 |
| Dead code (estimated) | ~65% (~19,400 lines) |
| Test files | 69 |
| Test lines | 14,163 |
| Test:source ratio | 0.48:1 |
| Data sources in code | 13 |
| Data sources actually used | 3 (catalogs + yfinance + competitor_data.json) |
| Data sources dead | 10 |
| Maximum companies (energy market) | 49 |
| Maximum companies (other markets) | 20 |
| Companies discovered dynamically | 0 |
| Fabricated data points in pipeline | 12+ categories |
| Currency conversion bugs | 6 |
| Security vulnerabilities | 6 |
| DB schema-ORM mismatches | 6 |
| Previous audits referenced | 6 |
| Total cataloged issues (all audits) | 190+ (DATA_PIPELINE) + 20 (CODEBASE) + 45 (this audit) |
| Issues resolved in sessions 1-2 | 9 |
| Open issues remaining | ~200+ |
| Documentation files | 75+ |
| Documentation lines | ~15,000 |

---

## 10. Strategic Recommendations

### 10.1 The Core Decision

Solstein has two possible paths forward:

**Path A: Fix the Foundation (Recommended)**
- Fix P0 issues (9 critical bugs) — ~2 days
- Wire 3-4 existing dead-code data sources into pipeline — ~2 weeks
- Run pipeline to completion on a real market — ~1 day
- Validate output against known company data — ~1 day
- Remove dead code, consolidate duplicates — ~1 week
- Result: Honest product with 4-5 data sources, 49-100 companies, trustworthy scores

**Path B: Keep Building Features**
- Risk: More dead code, more documentation describing non-existent capabilities
- Risk: The quality gap widens as features accumulate without integration
- Risk: First customer deployment exposes all issues simultaneously

### 10.2 Immediate Actions (This Week)

1. **Fix revenue unit normalization** — decide on one unit (absolute EUR or millions), enforce consistently
2. **Fix currency conversion** — correct the inverted formulas and USD=1.0
3. **Restore CI/CD** — renew billing or set up self-hosted runner
4. **Install missing test deps** — pytest-asyncio, aiohttp into pyproject.toml [dev]
5. **Run the full pipeline once** — `python scripts/discover_and_research_market.py --max-companies 49`
6. **Validate output** — compare 5 known companies against public data

### 10.3 Short-Term Actions (This Month)

7. **Wire web_search_client into discovery** — enable dynamic company finding
8. **Wire patent_client into gather** — remove fabricated multipliers, use real data
9. **Wire additional_sources into gather** — news, funding enrichment
10. **Delete application/ directory** — resolve duplicate agent tree
11. **Merge api/routes/ into api/routers/** — resolve split
12. **Consolidate CompanyTier enum** — pick one, delete the other
13. **Add Pydantic Field constraints** — bounds on all financial fields
14. **Fix Excel output** — numbers not strings, proper None handling

### 10.4 Quality Gates to Enforce

Before any customer deployment, the system must pass:

| Gate | Criterion |
|------|-----------|
| **Data Integrity** | Zero fabricated data points in scored output |
| **Unit Consistency** | All financial values in one documented unit |
| **Multi-Source** | ≥3 real external data sources feeding each company profile |
| **Test Coverage** | ≥70% on all pipeline modules |
| **CI Green** | All GitHub Actions workflows passing |
| **Schema Alignment** | ORM models match SQL migrations exactly |
| **Security** | No anonymous DB write, no plaintext secrets |
| **Pipeline Completion** | Full pipeline runs on 50+ companies without crash |
| **Output Validation** | Scored output for 5 known companies matches public data within 10% |

---

## 11. Relationship to Previous Audits

This audit subsumes and references:

| Audit | Date | Lines | Scope | Status |
|-------|------|-------|-------|--------|
| DATA_PIPELINE_AUDIT_2026-02-23.md | Feb 23 | 1,710 | Pipeline files deep dive (190+ issues) | Reference — most detailed |
| CODEBASE_AUDIT_REPORT.md | Feb 24 | 207 | Nyx's 30 commits review (20 issues) | Superseded by this audit |
| YAHOO_EXTRACTION_AUDIT.md | Feb 24 | 42 | Yahoo extraction regression | Resolved — fixes pushed |
| NYX_REMOTE_DIFF_ANALYSIS.md | Feb 24 | 446 | File-by-file diff of Nyx's changes | Historical reference |
| DOCUMENTATION_AUDIT.md | Feb 20 | 348 | Documentation gaps | Mostly resolved |
| .sisyphus documentation-audit-report.md | Feb 24 | 269 | Nyx's doc inventory | Superseded |

The DATA_PIPELINE_AUDIT remains the authoritative source for granular, line-by-line issue references. This audit provides the strategic overlay and PE/VC mission assessment that the pipeline audit does not.

---

## 12. Conclusion

Solstein has the **vision, domain model, and scoring math** to be a category-defining PE/VC intelligence platform. The business narrative is compelling. The classification system is clever. The architecture intentions (clean architecture, adapter pattern, event-driven refresh) are correct.

But the current state is a prototype that tells a better story than it delivers. The gap between documentation and reality — between what the code *describes* and what the code *does* — is the fundamental quality problem.

For a product where quality is structural, the path forward is:

1. **Make what exists work correctly** (fix P0 bugs, run the pipeline)
2. **Wire in what's already built** (connect the 10 dead data sources)
3. **Stop building new features until the foundation is solid** (no more adapters, connectors, or plans until the pipeline runs clean on 50+ companies with verified output)
4. **Measure quality empirically** (compare scored output against known data)

The codebase has ~30,000 lines of code. Approximately 10,000 of those lines form a working (if buggy) pipeline. The remaining 20,000 lines represent ambitious but disconnected work that needs integration, not more accumulation.

**Quality is not built by writing more code. It's built by making existing code trustworthy.**

---

*Audit conducted February 25, 2026. Next audit recommended after P0 fixes are implemented and pipeline runs to completion.*
