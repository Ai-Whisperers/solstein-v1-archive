# Solstein Data Pipeline & Web Fetching Audit

**Date**: 2026-02-23
**Scope**: Full review of all workflows and pipelines related to information fetching from the web, document creation, data validation, and score calculation.
**Branch**: master @ 4c4fa7a

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Data Sources Inventory](#2-data-sources-inventory)
3. [Pipeline Architecture](#3-pipeline-architecture)
4. [Stage-by-Stage Audit](#4-stage-by-stage-audit)
5. [Document Creation & Output Artifacts](#5-document-creation--output-artifacts)
6. [Scoring & Calculation Methodology](#6-scoring--calculation-methodology)
7. [Validation & Verification Mechanisms](#7-validation--verification-mechanisms)
8. [Data Authenticity Assessment](#8-data-authenticity-assessment)
9. [Risk Matrix](#9-risk-matrix)
10. [Recommendations](#10-recommendations)

---

## 1. Executive Summary

Solstein is a **data aggregation and scoring platform** — it does not generate primary financial data. All market data originates from external sources (Yahoo Finance, news APIs, web scraping, patent databases, and curated JSON files). The platform's value lies in organizing, validating structure, detecting contradictions, and computing composite scores.

**Key finding**: Data authenticity depends entirely on the quality and accuracy of external sources. The validation system checks **structural completeness and internal consistency**, not **factual truthfulness**. A well-structured but fabricated profile would pass all current validation gates.

### Verdict Summary

| Area | Status | Confidence |
|------|--------|------------|
| Financial data (Yahoo Finance) | Real, third-party sourced | HIGH |
| Patent data (USPTO/Google) | Real, multi-source fallback | MEDIUM |
| News/sentiment | Real sources, simplistic analysis | MEDIUM |
| Hardcoded market catalog | Static, may be stale | LOW |
| Scoring formulas | Deterministic, auditable | HIGH |
| Provenance validation | Structural only, not factual | MEDIUM |

---

## 2. Data Sources Inventory

### 2.1 Active External Data Sources

| Source | File | API Key Required | Data Type | Reliability |
|--------|------|-----------------|-----------|------------|
| Yahoo Finance (yfinance) | `src/solstein/data/fetchers.py` | No | Stock prices, financials, fundamentals | HIGH — widely used, official API |
| Exa API | `src/solstein/data/web_search_client.py` | Yes (`EXA_API_KEY`) | Web search, content extraction | MEDIUM — third-party search |
| Google Search (fallback) | `src/solstein/data/web_search_client.py` | No | Web search results | LOW — scraping, rate-limited |
| NewsAPI.org | `src/solstein/data/additional_sources.py` | Yes (`NEWS_API_KEY`) | News articles | MEDIUM — optional, paid tier |
| USPTO PEDS | `src/solstein/data/patent_client.py` | No | Patent examination data | HIGH — official government source |
| Google Patents | `src/solstein/data/patent_client.py` | No | Patent records (scraping) | MEDIUM — scraping is brittle |
| DuckDuckGo | `src/solstein/data/patent_client.py` | No | Patent search fallback | LOW — indirect, unstructured |
| Crunchbase | `src/solstein/data/additional_sources.py` | Yes (`CRUNCHBASE_API_KEY`) | Funding, valuations | MEDIUM — optional |
| PatentsView API | `src/solstein/data/additional_sources.py` | Yes (`PATENTSVIEW_API_KEY`) | Patent analytics | MEDIUM — optional |

### 2.2 Static/Local Data Sources

| Source | File | Description |
|--------|------|-------------|
| `data/input/competitor_data.json` | `src/solstein/data/loaders.py` | ~208 KB curated competitor dataset |
| Hardcoded market catalog | `src/solstein/research/discovery.py` | Static company lists per market vertical |

### 2.3 Configured but Inactive

| Key | Status |
|-----|--------|
| `OPENAI_API_KEY` | Configured, not in active pipeline |
| `PERPLEXITY_API_KEY` | Configured, marked "(currently unused)" |
| `GROQ_API_KEY` | LLM fallback provider |
| `FIREWORKS_API_KEY` | LLM fallback provider |
| `COMPANIES_HOUSE_API_KEY` | Placeholder, not implemented |
| `GOOGLE_API_KEY` | Placeholder, not implemented |

---

## 3. Pipeline Architecture

### 3.1 High-Level Data Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                   Market Intelligence Pipeline                    │
│              Orchestrator: src/solstein/research/pipeline.py      │
└──────────────────────────────────────────────────────────────────┘

  PHASE 1: DISCOVERY
  ┌─────────────────────────────────────────────────────────┐
  │  seed_company + market keywords                         │
  │  → _catalog_for_market() [hardcoded company lists]      │
  │  → CompetitorDataLoader [competitor_data.json]          │
  │  → Output: DiscoveryCandidate objects (~25 companies)   │
  └─────────────────────────────────────────────────────────┘
                           │
                           ▼
  PHASE 2: GATHERING
  ┌─────────────────────────────────────────────────────────┐
  │  For each candidate:                                    │
  │  → yfinance ticker lookup (if available)                │
  │  → Web search for company info (Exa/Google)             │
  │  → Patent lookup (USPTO → Google Patents → DDG)         │
  │  → News search + sentiment analysis                     │
  │  → Fallback: hardcoded values + justifications          │
  │  → Output: Company domain entities with metrics         │
  └─────────────────────────────────────────────────────────┘
                           │
                           ▼
  PHASE 3: VALIDATION
  ┌─────────────────────────────────────────────────────────┐
  │  3a. Provenance Validation                              │
  │      → Check metric_sources exist for required metrics  │
  │      → Check all sources in source_links                │
  │      → Output: provenance_report.json                   │
  │                                                         │
  │  3b. Contradiction Detection                            │
  │      → Numeric divergence > 20% threshold               │
  │      → Categorical value conflicts                      │
  │      → Output: contradictions_report.json               │
  │                                                         │
  │  3c. Evidence Readiness Evaluation                      │
  │      → Source count, domain diversity                   │
  │      → Metric coverage, explainability                  │
  │      → Readiness score (0-100)                          │
  │      → Output: evidence_readiness.json                  │
  └─────────────────────────────────────────────────────────┘
                           │
                           ▼
  PHASE 4: SCORING
  ┌─────────────────────────────────────────────────────────┐
  │  GrowthScorer.calculate_scores()                        │
  │  → Growth score (0-10)                                  │
  │  → Financial health score (0-10)                        │
  │  → Competitive position score (0-10)                    │
  │  → Composite = 40% growth + 30% financial + 30% comp   │
  │  → Classification: Phoenix / Salt / Lead                │
  │  → Output: scored.json                                  │
  └─────────────────────────────────────────────────────────┘
                           │
                           ▼
  PHASE 5: EXPORT
  ┌─────────────────────────────────────────────────────────┐
  │  → JSON artifacts (all intermediate + final)            │
  │  → Excel dashboard (multi-sheet workbook)               │
  │  → Database persistence (optional dual-write)           │
  │  → Market analysis summary                              │
  └─────────────────────────────────────────────────────────┘
```

### 3.2 Entry Points

| Entry Point | File | Purpose |
|-------------|------|---------|
| `run_market_intelligence()` | `src/solstein/research/pipeline.py` | Full pipeline orchestration |
| `scripts/discover_and_research_market.py` | `scripts/` | CLI script wrapping the pipeline |

---

## 4. Stage-by-Stage Audit

### 4.1 Discovery Stage

**File**: `src/solstein/research/discovery.py`

**How it works**: The `_catalog_for_market()` function returns a hardcoded list of companies for each market vertical (e.g., "maritime technology", "fintech"). Each entry includes:
- Company name, ticker symbol
- Static revenue, growth rate, employee count
- Description text
- Generic source links (mostly `finance.yahoo.com/{ticker}`)

**Authenticity concern**: These are **manually curated, static entries**. There is no mechanism to:
- Verify the data is current
- Refresh stale entries
- Detect companies that no longer exist or have changed significantly

**What makes it real**: The tickers are real and resolve against Yahoo Finance. The company names, descriptions, and approximate financials correspond to real companies.

**What could be stale**: Revenue figures, growth rates, employee counts — all hardcoded at catalog creation time with no refresh mechanism.

### 4.2 Gathering Stage

**File**: `src/solstein/research/gather.py`

**How it works**: `build_company_profile()` enriches each candidate:

1. **Ticker resolution** via `yfinance`: Fetches real-time market data, financials, and fundamentals. This is **real data from Yahoo Finance** — the most reliable source in the pipeline.

2. **Metric extraction**: Pulls revenue, market cap, employees, profit margins from Yahoo Finance response. Falls back to discovery-phase values if ticker data unavailable.

3. **AI maturity classification**: Simple keyword matching against company description:
   - "generative", "llm", "artificial intelligence", "machine learning", "neural" → STRONG
   - "analytics", "automation", "digital" → MODERATE
   - Otherwise → LOW

4. **Tier/threat determination**: Calculated from numeric thresholds (market cap for tier, growth rate for threat level).

**Authenticity concern**:
- AI maturity is **inferred from keywords, not verified** — a logistics company mentioning "machine learning" once would score STRONG
- When yfinance data is unavailable, the pipeline falls back to hardcoded values with "justification" strings instead of real sources

### 4.3 Validation Stage

**File**: `src/solstein/extractors/markdown_extractor.py` (provenance), `src/solstein/research/reconcile.py` (contradictions), `src/solstein/research/evidence.py` (readiness)

#### Provenance Validation
- Checks that 6 required metrics (revenue, growth_rate, employees, profit_margin, funding, valuation) have either:
  - Source URLs in `metric_sources`, OR
  - Explicit text justifications in `metric_justifications`
- Validates all metric sources appear in the global `source_links` list
- **Does NOT**: Visit URLs to verify they're live, check if the data at the URL matches the metric value, or assess source credibility

#### Contradiction Detection
- Compares numeric metrics across observations; flags divergence > 20%
- Flags categorical metrics with multiple distinct values
- **Limitation**: 20% threshold is arbitrary; no mechanism to determine which source is correct

#### Evidence Readiness Score
Formula (0-100):
- 20% weight: Source count (capped at 6 sources)
- 20% weight: Domain diversity (capped at 4 unique domains)
- 35% weight: Metric source coverage (% of 6 required metrics with URL sources)
- 25% weight: Metric explainability (% with sources OR justifications)
- -40 point penalty per unsupported metric

Readiness levels:
- ≥85: Investment Ready
- ≥70: Decision Support Ready
- ≥50: Needs More Evidence
- <50: Insufficient Evidence

### 4.4 Scoring Stage — See Section 6

### 4.5 Export Stage

**File**: `src/solstein/exporters/excel.py`, pipeline.py

Produces 10+ output artifacts — see Section 5.

---

## 5. Document Creation & Output Artifacts

### 5.1 JSON Artifacts

| Artifact | Content | Source of Truth |
|----------|---------|----------------|
| `discovery_candidates.json` | Raw candidate list from catalog | Hardcoded catalog + competitor_data.json |
| `extracted.json` | Full company profiles with all metrics | yfinance + catalog fallbacks |
| `provenance_report.json` | Validation violations per company | Computed from extracted.json |
| `contradictions_report.json` | Conflicting data points | Computed from extracted.json |
| `evidence_readiness.json` | Source quality scores per company | Computed from source metadata |
| `scored.json` | Companies with all calculated scores | Computed from extracted.json via GrowthScorer |
| `market_analysis.json` | Market-level aggregations | Computed from scored.json |
| `stage_report.json` | Pipeline execution metadata | Pipeline runtime data |
| `run_summary.json` | High-level run statistics | Pipeline runtime data |

### 5.2 Excel Dashboard

**File**: `src/solstein/exporters/excel.py`

4-sheet workbook:
1. **Executive Summary** — Market KPIs, company counts by classification
2. **Market Rankings** — Sorted by composite score, color-coded (Phoenix=green, Salt=yellow, Lead=red)
3. **Financial Intelligence** — Revenue, growth, margins, CAGR, funding, valuations
4. **Tech & AI Maturity** — AI scores, SaaS maturity, moat strength

**How numbers get there**: Every cell in the Excel output traces back to either:
- Yahoo Finance API response (financial data)
- Hardcoded catalog values (when API data unavailable)
- Calculated scores (deterministic formulas applied to the above)

### 5.3 Database Persistence

**File**: `src/solstein/infrastructure/database_models.py`, `research_dual_write.py`

Optional dual-write to PostgreSQL/Supabase with 12 tables:
- `companies`, `scoring_records`, `signal_records`
- `market_snapshots`, `audit_trails`
- `research_runs`, `research_stages`, `research_artifacts`
- `source_documents`, `metric_observations`
- `evidence_readiness`, `contradictions`

---

## 6. Scoring & Calculation Methodology

### 6.1 Growth Score (0-10)

| Component | Formula | Max Points |
|-----------|---------|------------|
| Revenue Growth | min(growth_rate% / 15, 3) | 3.0 |
| Employee Efficiency | rev/employee > €100k: +0.5; > €50k: +0.25 | 0.5 |
| Funding Momentum | funding > €50M: +0.5; > €10M: +0.25 | 0.5 |
| Profitability Profile | margin > 30%: +0.5; > 15%: +0.25; < 0%: -0.5 | 0.5 |

### 6.2 Financial Health Score (0-10)

| Component | Formula | Max Points |
|-----------|---------|------------|
| Revenue Scale | > €500M: +1.5; > €100M: +1.0; < €10M: -0.5 | 1.5 |
| Profitability | margin > 30%: +1.0; > 15%: +0.5; < 0%: -0.5 | 1.0 |
| Operating Efficiency | rev/emp > €200k: +0.5; > €100k: +0.25; < €25k: -0.5 | 0.5 |
| Funding Cushion | funding/revenue > 2.0: +0.5; > 0.5: +0.25 | 0.5 |

### 6.3 Competitive Position Score (0-10)

| Component | Formula | Max Points |
|-----------|---------|------------|
| Market Tier | Tier 1: +2.0; Tier 2: +1.0; Tier 3: +0.5 | 2.0 |
| AI Maturity | STRONG: +1.5; MODERATE: +0.5 | 1.5 |
| SaaS Maturity | (score-1)/9 × 2.0 | 2.0 |
| Geographic Presence | > 5 regions: +1.0; > 2: +0.5 | 1.0 |
| Tech Stack Diversity | > 5 technologies: +0.5 | 0.5 |

### 6.4 Composite Score

```
Composite = (Growth × 0.40) + (Financial Health × 0.30) + (Competitive Position × 0.30)
```

Capped to 0-10 range.

### 6.5 Classification

| Range | Classification | Meaning |
|-------|---------------|---------|
| ≥ 7.0 | Phoenix | High performer |
| 3.9 – 7.0 | Salt | Stable / average |
| ≤ 3.9 | Lead | Underperformer |

### 6.6 Tier Determination

| Criterion | Tier |
|-----------|------|
| Market cap or revenue ≥ €10B | Tier 1 |
| ≥ €2B | Tier 2 |
| ≥ €200M | Tier 3 |
| < €200M | Tier 4 |

### 6.7 Threat Level

| Growth Rate | Threat |
|-------------|--------|
| ≥ 20% | HIGH |
| 8% – 20% | MEDIUM |
| < 8% | LOW |

### 6.8 AI Maturity (keyword-based)

| Keywords in Description | Level |
|------------------------|-------|
| generative, llm, artificial intelligence, machine learning, neural | STRONG |
| analytics, automation, digital | MODERATE |
| none of the above | LOW |

---

## 7. Validation & Verification Mechanisms

### 7.1 What IS Validated

| Check | Location | What It Catches |
|-------|----------|-----------------|
| Metric source presence | `markdown_extractor.py` | Missing source URLs for required metrics |
| Source link consistency | `markdown_extractor.py` | Metric sources not in global source list |
| Numeric divergence | `reconcile.py` | Contradictory numeric values (>20% difference) |
| Categorical conflicts | `reconcile.py` | Multiple values for same categorical metric |
| Source count | `evidence.py` | Too few total sources |
| Domain diversity | `evidence.py` | All sources from single domain |
| URL canonicalization | `sources.py` | Duplicate URLs with tracking params |

### 7.2 What Is NOT Validated

| Gap | Impact | Risk Level |
|-----|--------|------------|
| URL accessibility (are links live?) | Dead links counted as valid sources | MEDIUM |
| Data-to-source matching (does the URL actually contain the claimed metric?) | Fabricated attribution passes validation | HIGH |
| Source credibility ranking (is Reuters more reliable than a blog?) | All sources weighted equally | MEDIUM |
| Data freshness (when was the data last verified?) | Stale data treated as current | HIGH |
| Cross-source verification (does Yahoo Finance agree with the catalog?) | Contradictions only detected within same snapshot | MEDIUM |
| AI maturity verification (actual AI capabilities vs. marketing claims) | Keyword detection is trivially gameable | MEDIUM |

---

## 8. Data Authenticity Assessment

### 8.1 What Is Definitely Real

- **Yahoo Finance market data**: Pulled via the `yfinance` library at runtime. These are real stock prices, market caps, revenue figures, and employee counts from Yahoo's aggregation of exchange data and company filings.
- **USPTO patent data**: When available, pulled from the official US Patent and Trademark Office API (PEDS).
- **Company existence**: Ticker symbols resolve to real publicly-traded companies.

### 8.2 What May Be Stale or Approximate

- **Hardcoded catalog values**: Revenue, growth rates, and employee counts in `_catalog_for_market()` were accurate at catalog creation time but have no refresh mechanism. These could be months or years out of date.
- **Competitor JSON data** (`competitor_data.json`): A 208 KB curated dataset. Last-modified date should be checked; values may lag reality.
- **Currency conversions**: Hardcoded rates in `loaders.py` (e.g., DKK at 0.134, AUD at 0.60) — not live exchange rates.

### 8.3 What Is Inferred, Not Verified

- **AI maturity classifications**: Keyword matching against descriptions. A company describing "automated logistics" would score MODERATE even if they use no AI.
- **Sentiment analysis**: Hardcoded positive/negative word lists. Not contextual — "not profitable" would score "profitable" as positive.
- **Patent AI-relatedness**: Keyword matching on patent titles/abstracts. Broad terms like "system" or "method" could false-positive.
- **SaaS maturity**: Source of this metric is unclear; appears to come from catalog data or manual assignment.

### 8.4 What Could Be Fabricated (and Would Pass Validation)

A company profile with:
- Plausible-looking source URLs (valid format, real domains)
- Consistent internal metrics (no contradictions)
- Justification strings for any missing sources
- 6+ source links across 4+ domains

...would receive a high evidence readiness score and pass all quality gates, even if the actual data was invented. **The validation system checks structure, not truth.**

---

## 9. Risk Matrix

| Risk | Likelihood | Impact | Mitigation Status |
|------|-----------|--------|-------------------|
| Stale hardcoded catalog data | HIGH | MEDIUM | NOT mitigated — no refresh mechanism |
| Yahoo Finance API unavailability | LOW | HIGH | PARTIAL — fallback to catalog values |
| Dead source URLs in reports | MEDIUM | LOW | NOT mitigated — URLs never verified |
| False AI maturity classification | HIGH | MEDIUM | NOT mitigated — keyword-only detection |
| Incorrect currency conversion | MEDIUM | MEDIUM | NOT mitigated — hardcoded rates |
| Fabricated data passing validation | LOW | HIGH | NOT mitigated — structural validation only |
| Patent scraping breakage | MEDIUM | LOW | PARTIAL — 3-tier fallback (USPTO → Google → DDG) |
| Score manipulation via input data | LOW | HIGH | NOT mitigated — no input sanitization beyond format |
| Single-source dependency (Yahoo) | MEDIUM | HIGH | NOT mitigated — no cross-validation |

---

## 10. Recommendations

### 10.1 Immediate (High Priority)

1. **Add URL liveness checks**: Before counting a source in evidence readiness, verify the URL returns HTTP 200.

2. **Add data freshness tracking**: Timestamp when each metric was last fetched from an external source. Flag metrics older than a configurable threshold (e.g., 90 days).

3. **Replace hardcoded currency rates**: Use the existing Yahoo Finance fetcher's `CurrencyRateFetcher` for live exchange rates in the data loader, instead of hardcoded constants.

4. **Cross-validate Yahoo Finance data against catalog**: When both sources provide the same metric, compare them. Flag significant discrepancies in the contradictions report.

### 10.2 Short-Term (Medium Priority)

5. **Implement source credibility tiers**: Weight sources by credibility (e.g., SEC filings > Reuters > company blog > random URL). Factor into evidence readiness score.

6. **Replace keyword-based AI maturity**: Integrate an LLM-based classifier (using existing GROQ/Fireworks keys) to assess AI maturity from company descriptions with more nuance.

7. **Add catalog refresh mechanism**: Script or scheduled job that re-fetches key metrics for catalog companies from Yahoo Finance and updates the hardcoded values, or migrate entirely to runtime-only data.

8. **Validate source-to-metric mapping**: For critical metrics (revenue, growth), check that the source URL's domain is plausible for that data type (e.g., financial data should come from financial sources).

### 10.3 Long-Term (Low Priority)

9. **Implement data provenance chain**: Track the full lineage of every metric from raw API response → parsed value → scored output, with timestamps and source hashes.

10. **Add multi-source financial data**: Integrate a second financial data provider (e.g., Alpha Vantage, Financial Modeling Prep) for cross-validation of Yahoo Finance data.

11. **Automated regression testing**: Compare pipeline outputs across runs to detect unexpected score changes that might indicate data quality issues.

12. **Source document archival**: Cache/archive the actual content of source URLs at fetch time, so auditors can verify what data was available when scores were calculated.

---

## Appendix A: File Inventory

| File | Role in Pipeline |
|------|-----------------|
| `src/solstein/research/pipeline.py` | Pipeline orchestrator |
| `src/solstein/research/discovery.py` | Company discovery + hardcoded catalog |
| `src/solstein/research/gather.py` | Company profile enrichment |
| `src/solstein/research/evidence.py` | Evidence readiness scoring |
| `src/solstein/research/reconcile.py` | Contradiction detection |
| `src/solstein/research/sources.py` | URL canonicalization |
| `src/solstein/data/fetchers.py` | Yahoo Finance data fetching |
| `src/solstein/data/web_search_client.py` | Exa/Google web search |
| `src/solstein/data/additional_sources.py` | News, patents, funding APIs |
| `src/solstein/data/patent_client.py` | Multi-source patent lookup |
| `src/solstein/data/loaders.py` | Static data loading |
| `src/solstein/analytics/scoring.py` | Score calculation |
| `src/solstein/extractors/markdown_extractor.py` | Provenance validation |
| `src/solstein/exporters/excel.py` | Excel dashboard generation |
| `src/solstein/infrastructure/database_models.py` | Database schema |
| `src/solstein/infrastructure/research_dual_write.py` | Database persistence |
| `src/solstein/config.py` | Configuration + API keys |
| `scripts/discover_and_research_market.py` | CLI entry point |

## Appendix B: Quality Gate Configuration

From `pipeline.py` — configurable gates that can halt the pipeline:

| Gate | Parameter | Default | Effect |
|------|-----------|---------|--------|
| Minimum total sources | `min_total_sources` | Configurable | Fails if total unique sources below threshold |
| Strict provenance | `strict_provenance` | Configurable | Fails if any company has provenance violations |
| Minimum readiness score | `min_readiness_score` | Configurable | Fails if average readiness below threshold |
| Maximum contradictions | `max_contradictions` | Configurable | Fails if contradiction count exceeds limit |

---

---

# PART 2: Deep Dive — Granular Issue Catalog

*Appended 2026-02-23 after line-by-line review of every pipeline file.*

Total issues found: **120+** across 14 files. Organized by file, with severity ratings.

---

## 11. fetchers.py — Financial Data Fetching

**File**: `src/solstein/data/fetchers.py`

### CRITICAL — Financial Data Corruption

| # | Lines | Issue | Impact |
|---|-------|-------|--------|
| F-1 | 142-155 | **Inconsistent Yahoo Finance currency pair directions.** `EURUSD=X` returns EUR→USD, but `JPY=X` returns USD→JPY. The code treats ALL pairs identically when storing rates — no direction normalization. Rates for JPY, CNY, HKD, INR, and BRL are inverted. | All conversions involving these 5 currencies produce wrong values |
| F-2 | 183-188 | **Cross-rate calculation formula is inverted.** Code returns `to_usd / from_usd` but correct formula is `from_usd / to_usd`. | Every cross-currency conversion is the reciprocal of the correct value |
| F-3 | 183-184 | **Silent fallback to `1.0` for missing currency rates.** If a rate is not in cache, defaults to `1.0` — the caller receives a converted amount with no indication the conversion used a fallback. | GBP silently treated as equal to USD when rate missing |
| F-4 | 193 | **`convert()` returns unconverted amount on failure.** If rate lookup fails, returns original amount. Caller gets a float in the wrong currency with no error signal. | 1000 GBP → caller receives 1000.0 believing it's USD |
| F-5 | 230 | **Silent `0` for missing stock price.** `current_price=quote.get("regularMarketPrice") or 0` — a missing price becomes $0, flowing into valuation calculations. | Graham intrinsic values and discount percentages become nonsense |

### HIGH — Incorrect Behavior Under Common Conditions

| # | Lines | Issue |
|---|-------|-------|
| F-6 | 295-309 | **`_detect_exchange` defaults everything to NYSE.** Shanghai, Bombay, BOVESPA, NASDAQ stocks all get NYSE. Wrong currency assignment for non-US exchanges. |
| F-7 | 142-155 | **KRW and MXN missing from rate fetches.** Both are in the `Currency` enum but have no fetch pairs. Conversions silently use `1.0`. |
| F-8 | 135-176 | **No cache TTL on currency rates.** Once fetched, rates cached forever. Multi-hour/day runs use stale rates. |
| F-9 | 101-105 | **`NaN` from yfinance history passes `is None` check.** `numpy.nan is not None` is `True`, so NaN flows through as a valid index value. |
| F-10 | 110-111 | **Fabricated `change_pct` when `previous_close` unavailable.** Sets `previous_close = current_value`, making `change_pct` always `0` — caller cannot distinguish "no change" from "data unavailable". |

### MEDIUM — Operational/Reliability

| # | Lines | Issue |
|---|-------|-------|
| F-11 | 55-57, 81-83, 125-127 | **Broad `except Exception` swallows all errors.** `TypeError`, `KeyError`, `AttributeError` from bugs are silently caught and return None/empty DataFrame. |
| F-12 | 135-136, 157-168 | **No thread safety.** Mutable `_cached_rates` and `_last_fetch` have no synchronization. Concurrent reads during writes produce inconsistent state. |
| F-13 | 246-259, 273-293, 157-163 | **No rate limiting or backoff.** Rapid sequential API calls to Yahoo Finance with no throttling. Hitting rate limits causes silent cascading failures. |
| F-14 | 138-168 | **Partial rate fetch returns no warning.** If 3 of 12 pairs fail, caller gets partial rates with no indication. |
| F-15 | 312-330 | **New objects created on every `get_market_summary()` call.** No caching reuse — each call makes 9+ API requests. |
| F-16 | 122, 166, 318 | **`datetime.now()` without timezone.** All timestamps are naive — ambiguous across time zones. |
| F-17 | 231 | **`price_date` hardcoded to `date.today()`.** Weekend prices show Saturday/Sunday dates instead of last trading day. |
| F-18 | 275-285 | **Hardcoded major indices list.** Not derived from `MARKET_INDICES` dict — two sources of truth that can drift. |

---

## 12. discovery.py — Company Discovery & Market Catalogs

**File**: `src/solstein/research/discovery.py`

### Stale/Inaccurate Data

| # | Lines | Issue |
|---|-------|-------|
| D-1 | 200-206 | **AutoGrid was acquired by Schneider Electric in June 2022.** No longer an independent entity. URL likely redirects. Schneider Electric is already listed separately. |
| D-2 | 232-238 | **Limejump was acquired by Shell in 2019.** Over 6 years out of date. Entity absorbed into Shell Energy. |
| D-3 | 419-428 | **"MercadoLibre Fintech" is not the legal entity name.** Legal name is "MercadoLibre, Inc." — fintech arm is "Mercado Pago". Name mismatch against real data sources. |
| D-4 | 441-449 | **"BBAJIO" is a ticker symbol, not a company name.** Legal name is "Banco del Bajío" (BanBajio). Reports display a ticker as the company name. |
| D-5 | 216-222 | **Kaluza status uncertain.** Spun out of OVO Energy, significant organizational changes. May be stale. |

### Logic Bugs

| # | Lines | Issue | Impact |
|---|-------|-------|--------|
| D-6 | 35 | **"energy" substring matches too broadly.** `"LATAM renewable energy"` or `"US energy sector"` triggers the Dutch/Netherlands catalog instead of the LATAM fallback. | Wrong market catalog returned |
| D-7 | 241 (implicit) | **LATAM catalog is the silent fallback for ALL unknown markets.** `discover_companies("Tesla", "US automotive")` returns LATAM banks. No "unknown market" handling. | Completely wrong results for any market not explicitly handled |
| D-8 | 525 | **Substring name matching gives false positives.** Token `"it"` (from seed "IT Solutions") matches "Hitachi", "Itron", "Capgemini" (all contain "it"). Token `"a"` matches essentially everything. | Relevance scoring is unreliable |
| D-9 | 560 | **Reverse-alphabetical tiebreaker.** `reverse=True` sorts Z-to-A on name when relevance scores tie. Counterintuitive and non-deterministic for display. | |
| D-10 | 547 | **`company_id` collisions from `_slugify`.** "ABC Corp." and "ABC Corp" both become `"abc-corp"`. No deduplication or collision detection. | Silent data overwrites downstream |
| D-11 | 541-544 | **Market-agnostic tag boost.** "energy" tags get boosted in LATAM banking market; "bank" tags boosted in energy market. | Cross-contamination of relevance scores |
| D-12 | 35, 475-478 | **Duplicate market-detection logic.** Same condition expressed twice in two functions. If one is changed, they silently diverge. | |
| D-13 | 479 | **Enrichment gate off-by-one.** `max_companies > len(catalog)` — when equal, enrichment is skipped. | Potentially misses better data |

### Silent Data Fabrication

| # | Lines | Issue |
|---|-------|-------|
| D-14 | 497-500 | **Invented tags `["energy", "software"]` for companies with no tech_stack.** These fabricated tags influence relevance scoring. |
| D-15 | 492-495 | **Invented region `"NL/EU"` for companies with no geographic data.** Flows into `Company.headquarters`. |
| D-16 | loaders.py:273 | **Hardcoded `industry="Energy Software"` for ALL CompetitorDataLoader companies** regardless of actual industry. |
| D-17 | 483 | **Single hardcoded GitHub URL as source attribution** for all loader companies. Not the actual source of the data. |

### Missing Validation

| # | Lines | Issue |
|---|-------|-------|
| D-18 | 466-467 | **No validation on `seed_company` or `market` parameters.** `None` causes `AttributeError`; empty string causes silent degradation or wrong catalog. |
| D-19 | 506 | **Overly broad `except Exception` on enrichment.** Swallows `MemoryError` and traceback. |

### Catalog Completeness

| Market | Entries | Missing Notable Companies |
|--------|---------|---------------------------|
| Energy | 20 | Tibber, GridBeyond, Next Kraftwerke, Enel X, 1KOMMA5, Lichtblick, EnergyHub, Origami Energy |
| LATAM | 20 | Uala, dLocal (DLO), Inter & Co (INTR), Clip, Konfio, Creditas, C6 Bank, Neon |

Both catalogs overweight large traditional players vs. disruptive newcomers.

---

## 13. gather.py — Company Profile Building

**File**: `src/solstein/research/gather.py`

### Data Fabrication in Fallback Paths

| # | Path | Lines | What Gets Invented |
|---|------|-------|--------------------|
| G-1 | No ticker | 116-118 | `tier=TIER_3`, `threat_level=MEDIUM`, `ai_maturity=MODERATE` — all hardcoded with zero evidence |
| G-2 | Ticker, no yfinance | 147-149 | `tier=TIER_3`, `threat_level=MEDIUM`, `ai_maturity=LOW` — different arbitrary defaults than G-1 |
| G-3 | Ticker, yfinance exception | 178-180 | Same as G-2 but **missing `metric_observations` entirely** — silent data loss vs other paths |
| G-4 | Successful enrichment | 303 | `saas_maturity=5` — hardcoded middle-of-scale value, never computed from data |
| G-5 | Successful enrichment | 198 | Auto-generated description: `"Discovered candidate in {market}."` when `longBusinessSummary` is empty |

### Inconsistencies Across Fallback Paths

| Field | No ticker (A) | No yfinance (B) | Exception (C) | Notes |
|-------|---------------|-----------------|---------------|-------|
| `ai_maturity` | MODERATE | LOW | LOW | A gets higher maturity with less evidence |
| `metric_observations` | Included | Included | **Missing** | Silent data loss in path C |
| `saas_maturity` | model default (1) | model default (1) | model default (1) | Path D hardcodes 5 |

### Data Transformation Bugs

| # | Lines | Issue |
|---|-------|-------|
| G-6 | 62-65 | **`_as_percent` multiplies by 100 but unit is undocumented.** yfinance returns ratios (0.15 = 15%); after conversion it becomes 15.0. Downstream consumers must know the convention — no type annotation or unit field. |
| G-7 | 266 | **Unsafe `int()` conversion on employees.** String `"1,500"` or `"~200"` from yfinance raises `ValueError` — NOT caught by the outer try/except which only wraps `.info`. |
| G-8 | 256, 262, 272, 278 | **Unsafe `float()` conversions.** yfinance returning `"N/A"` or `"None"` raises `ValueError` uncaught. |
| G-9 | 297 | **`founded_year` type mismatch.** `Company` model expects `int | None` but yfinance `foundedDate` could be a date string. Pydantic `ValidationError` possible. |
| G-10 | 304 | **`str(None)` in tech_stack.** If `sector` resolves to `None`, `str(None)` produces literal `"None"` string in the tech stack list. |

### False Provenance

| # | Lines | Issue |
|---|-------|-------|
| G-11 | 79-86 | **`metric_sources` pre-populated with ticker_url BEFORE data is fetched.** If yfinance fails, the Company still attributes revenue/growth/etc. to the Yahoo Finance URL even though no data was retrieved. |
| G-12 | 258-261 | **Revenue from yfinance marked `CONFIRMED`** but growth_rate from the same source marked `ESTIMATED`. Inconsistent confidence for identical data quality. |

### Inferred Data Treated as Factual

| # | Lines | What | Method |
|---|-------|------|--------|
| G-13 | 24-39 | AI maturity | Keyword scan: "digital" → MODERATE. "Digital banking" company gets AI credit. |
| G-14 | 52-59 | Threat level | Growth rate alone. Ignores market positioning, product overlap, patents. |
| G-15 | 42-49 | Tier | Market cap alone. Ignores revenue, employees, market share, strategic relevance. |
| G-16 | 306 | Geographic presence | Single `info.get("country")` value. Company in 50 countries shows as 1. |

---

## 14. pipeline.py — Pipeline Orchestration

**File**: `src/solstein/research/pipeline.py`

### Critical Pipeline Flaws

| # | Lines | Issue | Impact |
|---|-------|-------|--------|
| P-1 | 27-29 | **All quality gates disabled by default.** `min_readiness_score`, `max_contradictions`, `min_total_sources` are all `None`. A caller who doesn't explicitly enable them gets zero enforcement. | Pipeline produces output regardless of data quality |
| P-2 | 75-77 | **Single bad candidate crashes entire pipeline.** List comprehension over `build_company_profile` — one Pydantic `ValidationError` kills everything. No per-candidate isolation. | Complete pipeline failure from one corrupt entry |
| P-3 | 204-205 | **Single scoring failure crashes entire pipeline.** Same pattern — one bad company in the scoring list comprehension kills everything. | No partial results saved |
| P-4 | 251-306 | **Database failure kills pipeline despite all files being written.** If `persist_research_run` raises after all JSON/Excel artifacts are saved, the entire function crashes and `run_summary` is never returned. | Transient DB issue destroys successful run |
| P-5 | 292-294 vs 80-85 | **Data inconsistency between file and database artifacts.** `extracted.json` is written before scoring, but the database dual-write serializes the same `companies` objects AFTER scoring mutates them in-place. Database "extracted" contains scores; files do not. | Audit trail unreliable |

### Quality Gate Issues

| # | Lines | Issue |
|---|-------|-------|
| P-6 | 128-131 | **Strict provenance failure writes no stage report.** `RuntimeError` raised BEFORE stage entry is appended. Source volume gate (lines 104-120) correctly writes before raising — inconsistent. |
| P-7 | 148-157 | **Contradiction gate failure writes no stage report.** Same pattern — stage appended after the check. |
| P-8 | 178-189 | **Readiness gate failure writes no stage report.** Same pattern. |
| P-9 | 128-131 | **`strict_provenance=False` silently swallows all violations.** Violations written to report, but scored companies are not flagged. Downstream consumers cannot tell which companies had provenance issues. |

### Data Loss / Integrity

| # | Lines | Issue |
|---|-------|-------|
| P-10 | 263-278 | **Deterministic `run_id` silently overwrites previous runs.** Same parameters = same hash. `persist_research_run` deletes existing run before inserting. No versioning or archive. |
| P-11 | 75-77, 92 | **Empty candidates produce vacuous output.** Pipeline runs all stages on zero companies. Creates empty but valid-looking JSON files and Excel dashboards. No early termination or warning. |
| P-12 | 204-205 | **Scoring mutates Company objects in-place.** `scored` list is the same objects as `companies`. The `extracted` artifact in the DB (line 292) contains post-scoring data. |
| P-13 | 63-66 through 226-229 | **No file write error handling.** Multiple `write_text()` calls with no try/except. Disk full → unhandled crash with partial files. |

### Configuration Concerns

| # | Lines | Issue |
|---|-------|-------|
| P-14 | 252-254 | **Global `db_manager` singleton mutated at runtime.** Settings replaced and re-initialized. Unsafe if used concurrently. |
| P-15 | 252, 217 | **Three separate `Settings` instantiations.** `db_manager` at import, pipeline at line 252, `ExcelExporter` internally. Each may resolve differently. |
| P-16 | 41-46, 75-77 | **No timeout on external calls.** `discover_companies` reads filesystem; `build_company_profile` calls yfinance HTTP. Neither has a timeout. |

---

## 15. scoring.py — Score Calculation

**File**: `src/solstein/analytics/scoring.py` + `src/solstein/analytics/scorers/*.py`

### CRITICAL — Score Integrity

| # | Lines | Issue | Impact |
|---|-------|-------|--------|
| S-1 | config | **Revenue units inconsistency.** Config comments say revenue thresholds are "in Millions" but efficiency thresholds are "in absolute EUR". If revenue is in millions, `rev/employee = 10.0/100 = 0.1` → triggers "low efficiency" penalty. If in absolute, thresholds are correct. System has contradictory unit assumptions. | All efficiency scores potentially wrong |
| S-2 | config | **Funding thresholds in millions but `funding_raised` unit unknown.** If `funding_raised` is absolute (e.g., 50,000,000), then `50M > 50.0` is always true — every funded company hits the high bonus. | Funding scores meaningless |
| S-3 | 59-65 | **Composite score silently falls back to growth-only.** When any sub-score is `None`, composite = `growth_score` alone. A company classified "Phoenix" on growth could be financially distressed. No flag indicating degraded mode. | Misleading classifications |
| S-4 | 597-614 | **Customer overlap can exceed 1.0.** Nested loop counts pairwise matches: 3 customers × 3 customers = 9 matches / 3 = 3.0 overlap. Claimed range 0-1 is violated. | Distorted competitive overlap scores |

### HIGH — Scoring Formula Issues

| # | Lines | Issue |
|---|-------|-------|
| S-5 | scorer:19-34 | **Negative growth rates have no lower bound.** Positive growth capped at +4.0, but negative growth can subtract up to -15.0 from base score. Asymmetric penalty — growth of -100% and -200% both score 0.0 (after clamp). |
| S-6 | 101, 121, 173 | **Truthiness checks treat `0.0` as missing data.** `if financials.employees` is `False` when employees=0. Zero revenue, zero funding, zero employees all treated as "no data" instead of meaningful values. |
| S-7 | 25-33 | **`None` score classified as "Salt" (same as mid-range).** No way to distinguish "no data" from "average company" in final classification. |
| S-8 | 542-569 | **Variable overlap components change weighting.** Customer overlap is conditional — with it, average of 5 scores; without, average of 4. Missing data inflates other components' weights. |
| S-9 | multiple | **Max possible score is 15.0, clamped to 10.0.** Companies strong on all dimensions are indistinguishable. Top-end compression loses discriminative power. |

### MEDIUM — Formula Gaps

| # | Lines | Issue |
|---|-------|-------|
| S-10 | 140-160 | **Profit margin 0-10% is a dead zone.** Companies at 0.1% and 9.9% margin score identically. Score jumps by 1.0+ at the 10% boundary. |
| S-11 | 295 / scorer:41 | **SaaS maturity formula assumes 1-10 range but allows 0.** `(0-1)/9 * 2.0 = -0.22` penalty for zero value. |
| S-12 | 94-96 | **"Moderate growth" label for negative growth.** A company shrinking at -50% gets reasoning "Moderate growth rate identified." |
| S-13 | config:107,112 | **`geo_single_penalty` and `tech_none_penalty` defined but never used.** Config suggests penalties should exist but they're not implemented. |

### Dead Code Divergence

| # | Lines | Issue |
|---|-------|-------|
| S-14 | 76-345 | **Three dead private methods diverged from live scorers.** Dead `_calculate_financial_health_score` line 244 checks `profit_margin is not None and < 5`, but live scorer line 91 checks `profit_margin is None or < 5` — opposite behavior on `None`. |

---

## 16. loaders.py — Static Data Loading

**File**: `src/solstein/data/loaders.py`

| # | Lines | Issue | Severity |
|---|-------|-------|----------|
| L-1 | 343 | **USD treated as 1.0 (equal to EUR).** `"$": 1.0` — actual rate ~0.92. All USD amounts overstated by ~8-9%. | CRITICAL |
| L-2 | 342-352, 445-454 | **All currency rates hardcoded.** GBP 1.18, NOK 0.085, DKK 0.134, AUD 0.60 — all drift over time. | HIGH |
| L-3 | 106-114 | **CAGR assumes timeline sorted newest-first.** No validation of chronological order. Ascending-order JSON produces garbage. | HIGH |
| L-4 | 135 | **`not profit_margin` treats `0.0` as falsy.** Falls through to Strategy 2, may overwrite valid zero margin. | MEDIUM |
| L-5 | 379-384 | **Currency detection is order-dependent.** `"A$50M"` matches `"$"` before `"A$"` — applies wrong rate (1.0 instead of 0.60). | HIGH |
| L-6 | 47-50, 62-63 | **Double-limiting.** Limit applied in both `_load_from_json` and `load_companies`. Redundant but masks intent. | LOW |
| L-7 | 70-72, 77-79 | **Conversion errors silently dropped.** Company count discrepancy not reported to caller. | MEDIUM |
| L-8 | 207 | **`int("1,500")` raises ValueError.** Comma-separated employee counts crash, caught by broad except that drops entire company. | MEDIUM |
| L-9 | 514-533 | **Headquarters guessing via keyword.** `"fukushima-energy"` matches `"uk"` → returns "United Kingdom". No word-boundary matching. | MEDIUM |
| L-10 | 61 | **No validation of JSON structure.** Top-level array (not object) causes `AttributeError` on `.get()`. | MEDIUM |

---

## 17. additional_sources.py — News, Patents, Funding

**File**: `src/solstein/data/additional_sources.py`

| # | Lines | Issue | Severity |
|---|-------|-------|----------|
| A-1 | 308-355 | **Sentiment analysis is deeply flawed.** "revenue decline" scores positive ("revenue" is positive). "investor" classified as negative. No contextual awareness. | HIGH |
| A-2 | 157-158 | **HTTP status code not checked.** 401/429/500 responses parsed as JSON. Silent failure mode. | MEDIUM |
| A-3 | 226-233 | **Google scraping violates ToS and is fragile.** Spoofed User-Agent, regex HTML parsing, frequent CAPTCHAs. | HIGH |
| A-4 | 185, 278 | **Missing publication date defaults to `datetime.now()`.** Old articles appear current. | MEDIUM |
| A-5 | 484-485 | **`total_raised` always `None` in `_get_public_funding_data`.** Variable declared but never updated. Method always returns `total_raised=None`. | HIGH — dead code |
| A-6 | 621 | **AI patent count limited to 10 results.** Only 10 patents inspected but `total_patents` can be much larger. Systematically undercounts. | MEDIUM |
| A-7 | 153 | **API key sent as URL query parameter.** Appears in server logs, proxy logs, browser history. | MEDIUM — security |
| A-8 | 729 | **Runtime import of `company_research` module.** If missing, `ImportError` inside the function with no handler. | LOW |

---

## 18. web_search_client.py — Web Search

**File**: `src/solstein/data/web_search_client.py`

| # | Lines | Issue | Severity |
|---|-------|-------|----------|
| W-1 | 32-33, 35 | **Hardcoded year "2025" in search queries.** Current date is 2026-02-23 — searches miss all 2026 content. `start_published_date="2025-01-01"` is 14 months stale. | CRITICAL |
| W-2 | 30-31 | **`Exa()` instantiated with no explicit API key validation.** If env var missing, fails with unhelpful error. | MEDIUM |
| W-3 | 67 | **Runtime import of unknown `google_search` package.** Not a well-known library; could be any package on PyPI. | MEDIUM — security |
| W-4 | 16, 62, 96 | **Company names not sanitized before search queries.** Special characters could cause injection or unexpected behavior. | MEDIUM |

---

## 19. patent_client.py — Patent Data

**File**: `src/solstein/data/patent_client.py`

| # | Lines | Issue | Severity |
|---|-------|-------|----------|
| PT-1 | 177 | **Google Patents `total_patents` FABRICATED.** `total_patents=len(results) * 5` — arbitrary 5x multiplier. | CRITICAL — data fabrication |
| PT-2 | 229 | **DuckDuckGo `total_patents` FABRICATED.** `total_patents=len(results) * 3` — arbitrary 3x multiplier. | CRITICAL — data fabrication |
| PT-3 | 167-173 | **"patent" listed as an AI keyword.** Every patent search result contains "patent" in its title, so `ai_count` always equals total count. AI-related metric is meaningless. | HIGH |
| PT-4 | 219-225 | **Same "patent" AI keyword bug in DuckDuckGo search.** | HIGH |
| PT-5 | 156-163 | **Google Patents scraping targets a JavaScript SPA.** `search-result-item` CSS selector likely returns nothing from raw HTTP GET — content is client-side rendered. | HIGH |
| PT-6 | 142-143 | **Company name in URL without proper encoding.** `replace(" ", "+")` is not URL encoding. `&`, `#`, `=` in names break the URL. | MEDIUM |
| PT-7 | 39-52 | **Early return on first successful source.** USPTO results found → Google Patents never checked. No cross-source aggregation. | LOW |

---

## 20. evidence.py — Evidence Readiness Scoring

**File**: `src/solstein/research/evidence.py`

| # | Lines | Issue | Severity |
|---|-------|-------|----------|
| E-1 | 69-71 | **`metric_explainability` can exceed 1.0.** Metrics with BOTH sources and justifications are double-counted. 6 metrics × 2 = 12/6 = 2.0. Inflates the explainability component to 0.50 instead of 0.25. | HIGH |
| E-2 | 81-88 | **`readiness_score` can exceed 100 before clamping.** Due to E-1, weighted sum exceeds 100. Clamping masks the inflation but reduces penalty effectiveness. | MEDIUM |
| E-3 | 102 vs 90-97 | **Rounding changes threshold crossing.** Score of 84.995 rounds to 85.00 (investment ready), but classification used unrounded value (not investment ready). Classification and reported score can disagree. | MEDIUM |
| E-4 | 88 | **Score 0.0 indistinguishable from "not evaluated".** No sentinel value for "evaluated and terrible" vs "function never called". | LOW |
| E-5 | 17-26 | **`_domains` uses O(n²) list dedup.** Should use set or OrderedDict. | LOW |

---

## 21. reconcile.py — Contradiction Detection

**File**: `src/solstein/research/reconcile.py`

| # | Lines | Issue | Severity |
|---|-------|-------|----------|
| R-1 | 43-46 | **Divergence calculation doesn't handle negative values correctly.** Both values negative (e.g., margins -5 and -20) produces unexpected relative divergence. | MEDIUM |
| R-2 | 15-20 | **`_as_float` silently converts booleans and arbitrary types.** `True` becomes `1.0`. Strings like `"$100M"` silently become `None`. | MEDIUM |
| R-3 | 59 | **Categorical conflict casts floats to strings.** `5.0` and `5` become `"5.0"` and `"5"` — treated as different categories, triggering false conflicts. | MEDIUM |
| R-4 | 48 | **No minimum absolute threshold.** Revenue 1.0M vs 1.3M is 30% divergence (flagged) but trivially small absolute difference. | LOW |

---

## 22. sources.py — URL Canonicalization

**File**: `src/solstein/research/sources.py`

| # | Lines | Issue | Severity |
|---|-------|-------|----------|
| U-1 | 30 | **`www.` prefix not normalized.** `www.example.com` and `example.com` produce different canonical URLs. | MEDIUM |
| U-2 | 29 | **HTTP vs HTTPS not normalized.** Same content served over both produces two canonical URLs. | LOW |
| U-3 | 20 | **`None` input returns empty string.** Two `None` URLs canonicalize to `""` = `""` — false equivalence. | LOW |

---

## 23. markdown_extractor.py — Profile Extraction & Provenance

**File**: `src/solstein/extractors/markdown_extractor.py`

| # | Lines | Issue | Severity |
|---|-------|-------|----------|
| M-1 | 230-240 | **All sources for a metric get the same value.** If different sources report different values, this structure cannot represent it. Creates false appearance of cross-source confirmation. | HIGH |
| M-2 | 71 | **Company name regex matches any heading level.** `r"#\s+(.+)"` matches `##` or `###`, not just `#`. A subsection title could be taken as the company name. | MEDIUM |
| M-3 | 319-321 | **`_parse_threat_level` does `.upper()` then `.capitalize()`.** "HIGH" → "High" — may not match enum if it uses uppercase values. Fallback mapping compensates. | LOW |
| M-4 | 317, 335 | **Default MEDIUM threat and TIER_3 when missing.** Silent assumptions that mask absent data. | MEDIUM |
| M-5 | 54-58 | **Broad `except Exception` returns `None` on any extraction error.** `PermissionError`, `UnicodeDecodeError`, `MemoryError` all silently swallowed. | MEDIUM |

---

## 24. Cross-Cutting Systemic Issues

### 24.1 The "Silent Empty" Pattern

Every module follows the same anti-pattern: catch `Exception` broadly, return empty/default values. A systemic failure (DNS down, all API keys expired, disk full) produces output that looks like "no data found" rather than "system is broken":

| Module | Pattern | Result Type |
|--------|---------|-------------|
| fetchers.py | `except Exception → return None` | Missing quotes |
| loaders.py | `except Exception → continue` | Dropped companies |
| web_search_client.py | `except → return []` | Empty search results |
| additional_sources.py | `except → return PressCoverage()` | Empty news |
| patent_client.py | `except → return PatentResult()` | Zero patents |
| markdown_extractor.py | `except → return None` | Missing profiles |

**Impact**: It is impossible to distinguish "the system is healthy but this company has no data" from "the system is completely broken." No alerting, no health checks, no error aggregation.

### 24.2 Currency/Unit Confusion

Three separate, inconsistent approaches to currency handling exist:

1. **fetchers.py**: Live rates from Yahoo Finance, but with inverted formulas and inconsistent pair directions
2. **loaders.py**: Hardcoded rates (USD=1.0, GBP=1.18, DKK=0.134) that never update
3. **scoring_config.py**: Thresholds in "Millions" for revenue but "absolute EUR" for efficiency — contradictory within the same config file

No single source of truth for what unit `revenue`, `funding_raised`, or `market_cap` are stored in.

### 24.3 Data Fabrication Summary

The following data points are invented by the system, not sourced from external data:

| What | Where | Value |
|------|-------|-------|
| AI maturity | gather.py:24-39 | Keyword matching on descriptions |
| SaaS maturity | gather.py:303 | Hardcoded `5` for all enriched companies |
| Tier (fallback) | gather.py:116 | Hardcoded `TIER_3` |
| Threat level (fallback) | gather.py:117 | Hardcoded `MEDIUM` |
| AI maturity (fallback) | gather.py:118 | Hardcoded `MODERATE` |
| Patent total (Google) | patent_client.py:177 | Actual count × 5 |
| Patent total (DDG) | patent_client.py:229 | Actual count × 3 |
| AI patent count | patent_client.py:167 | Inflated by "patent" keyword |
| Region (fallback) | discovery.py:495 | Hardcoded `"NL/EU"` |
| Tags (fallback) | discovery.py:500 | Hardcoded `["energy", "software"]` |
| Industry (loader) | loaders.py:273 | Hardcoded `"Energy Software"` |
| Publication date | additional_sources.py:185 | `datetime.now()` when missing |

### 24.4 No Input Sanitization

Company names flow unsanitized into:
- URL construction (patent_client.py, web_search_client.py)
- API query parameters (additional_sources.py)
- Search queries (web_search_client.py)
- File path construction (potential)

Characters like `&`, `#`, `=`, `?`, `../` in company names could cause URL injection, search injection, or path traversal.

---

## 25. Updated Risk Matrix (Post-Deep-Dive)

| Risk | Likelihood | Impact | Issues | Status |
|------|-----------|--------|--------|--------|
| **Currency conversion errors** | HIGH | CRITICAL | F-1, F-2, F-3, F-4, L-1, L-2 | NOT mitigated — inverted formulas, hardcoded rates |
| **Fabricated patent counts** | HIGH | HIGH | PT-1, PT-2, PT-3, PT-4 | NOT mitigated — multipliers embedded in code |
| **Unit mismatch in scoring** | HIGH | CRITICAL | S-1, S-2 | NOT mitigated — contradictory config comments |
| **Stale search dates** | HIGH | HIGH | W-1 | NOT mitigated — hardcoded "2025" |
| **Pipeline crash from single bad entry** | MEDIUM | HIGH | P-2, P-3 | NOT mitigated — no per-item isolation |
| **All quality gates disabled by default** | HIGH | HIGH | P-1 | NOT mitigated — all None |
| **Wrong market catalog for unknown markets** | MEDIUM | HIGH | D-7 | NOT mitigated — LATAM is catch-all |
| **False provenance chains** | HIGH | MEDIUM | G-11, M-1 | NOT mitigated — URLs attributed before fetch |
| **Silent system failures** | MEDIUM | HIGH | §24.1 | NOT mitigated — broad except everywhere |
| **Acquired/defunct companies in catalog** | HIGH | MEDIUM | D-1, D-2 | NOT mitigated — no freshness checks |
| **Scoring ceiling compression** | HIGH | MEDIUM | S-9 | NOT mitigated — max 15 clamped to 10 |
| **Dead code divergence from live scorers** | MEDIUM | MEDIUM | S-14 | NOT mitigated — can mislead maintainers |

---

## 26. Priority Remediation Roadmap

### P0 — Fix Before Next Pipeline Run

1. **Fix currency rate inversion** (F-1, F-2): Normalize all Yahoo Finance pairs to a consistent direction before storing.
2. **Fix USD=1.0 in loaders** (L-1): USD is not EUR. Use `CurrencyRateFetcher` or at minimum `0.92`.
3. **Update hardcoded year** (W-1): Replace `"2025"` with dynamic `datetime.now().year` in web_search_client.py.
4. **Remove "patent" from AI keywords** (PT-3, PT-4): This makes every AI patent metric 100%.
5. **Remove fabricated patent multipliers** (PT-1, PT-2): Report actual counts or clearly label estimates.

### P1 — Fix Within Sprint

6. **Enable quality gates by default** (P-1): Set sensible defaults for `min_total_sources`, `min_readiness_score`.
7. **Add per-candidate error isolation** (P-2, P-3): Wrap `build_company_profile` and scoring in individual try/except.
8. **Fix unit documentation** (S-1, S-2): Decide on units (millions vs absolute) and enforce consistently.
9. **Fix `metric_explainability` double-counting** (E-1): Count each metric once regardless of how many attribution methods exist.
10. **Remove or update stale catalog entries** (D-1, D-2): AutoGrid → Schneider Electric, Limejump → Shell Energy.
11. **Add "unknown market" handling** (D-7): Return empty list or raise instead of defaulting to LATAM.

### P2 — Fix Within Quarter

12. **Replace broad `except Exception` with specific catches** across all modules.
13. **Add truthiness→explicit None checks** (S-6, L-4): `if x is not None` instead of `if x`.
14. **Remove dead scoring methods** (S-14): Delete the 270 lines of diverged dead code.
15. **Fix `metric_sources` pre-population** (G-11): Only attribute sources after successful data fetch.
16. **Add cache TTL for currency rates** (F-8).
17. **Add word-boundary matching for discovery** (D-8): Replace `token in name` with regex `\btoken\b`.
18. **Document and enforce unit conventions** for all financial fields.

### P3 — Backlog

19. Replace keyword-based AI maturity with LLM classifier.
20. Add URL liveness checks to evidence evaluation.
21. Add multi-source financial data for cross-validation.
22. Implement source credibility tiers.
23. Add per-company provenance degradation flags in scored output.
24. Replace Google scraping with legitimate API alternatives.

---

*Deep dive audit conducted by line-by-line review of 14 source files on master branch at commit 4c4fa7a.*

---

# PART 3: Nuanced Findings — Second Pass

*Appended 2026-02-23 after pull of commits through 9e6c7c6. Covers new scripts, domain models, database layer, configuration, exports, inter-module data flows, test coverage gaps, and environment-specific behavior.*

---

## 27. New Scripts Audit

### 27.1 apply_supabase_migrations.py

**File**: `scripts/apply_supabase_migrations.py`

| # | Lines | Issue | Severity |
|---|-------|-------|----------|
| NS-1 | 26-36 | **Credential exposure in process list.** Database URL (with password) passed as CLI arg to `psql`. Visible via `ps aux` on multi-user systems. Should use `PGPASSWORD` env var. | HIGH |
| NS-2 | 25-36 | **No migration tracking.** All `*.sql` files re-run every time. No metadata table tracking applied migrations. Re-runs fail on `CREATE TABLE` or silently re-execute `ALTER/UPDATE`. | HIGH |
| NS-3 | 26-36 | **No `--single-transaction` flag.** A migration with multiple statements can fail mid-way, leaving DB in partially-migrated state. | MEDIUM |
| NS-4 | 25-36 | **No partial-failure recovery.** If migration 002 fails after 001 succeeds, retry re-runs 001 which fails. | MEDIUM |
| NS-5 | 19 | **No production safeguard.** No confirmation prompt, no `--dry-run`, no environment detection. Will immediately apply to any DB URL provided. | MEDIUM |
| NS-6 | 19 | **No URL format validation.** Malformed URLs produce confusing `psql` errors. | LOW |

### 27.2 supabase_dual_write_smoke_test.py

**File**: `scripts/supabase_dual_write_smoke_test.py`

| # | Lines | Issue | Severity |
|---|-------|-------|----------|
| NS-7 | 26 | **Writes real data to potentially production DB.** `db_dual_write=True` unconditionally. No schema isolation, no cleanup mechanism. | HIGH |
| NS-8 | 10-13 | **Redundant validation that gives false confidence.** Checks `SUPABASE__DB_URL` non-empty, but pipeline reads it independently via `Settings`. Validation here is cosmetic. | MEDIUM |
| NS-9 | 21 | **Unsafe `int()` conversion.** `int(os.getenv("MAX_COMPANIES", "25"))` raises `ValueError` on non-integer input with no handler. | MEDIUM |
| NS-10 | 17-27 | **No pre-flight DB connectivity check.** Full pipeline runs (minutes) before discovering DB is unreachable. | MEDIUM |
| NS-11 | 25 | **Non-standard boolean parsing.** Only `"true"` accepted; `"1"`, `"yes"`, `"on"` all treated as `False`. | LOW |
| NS-12 | 16 | **Relative output path default.** Actual location depends on CWD at execution time. | LOW |
| NS-13 | 28 | **No success confirmation output.** Smoke test returns 0 silently — no indication of what was tested. | LOW |

---

## 28. Domain Models Audit

**File**: `src/solstein/domain/models.py`

### 28.1 Missing Pydantic Validation Constraints

| # | Lines | Field | Issue |
|---|-------|-------|-------|
| DM-1 | 56 | `FinancialMetric.revenue` | No constraints. Accepts negative, NaN, infinity. Should have `ge=0`. |
| DM-2 | 58 | `FinancialMetric.growth_rate` | No bounds. `FinancialMetric` has no CAGR-style validator, unlike `Company.revenue_cagr_*` which validates >= -100. |
| DM-3 | 62 | `FinancialMetric.profit_margin` | No constraints, yet `Company.profit_margin` (line 132) IS validated to -100..100. Same concept, different validation. |
| DM-4 | 64 | `FinancialMetric.funding_raised` | No constraint. Should be `ge=0`. |
| DM-5 | 66 | `FinancialMetric.valuation` | No constraint. Should be `ge=0`. |
| DM-6 | 82-83 | `Company.id`, `Company.name` | No `min_length`. Empty string `""` is a valid company ID/name. |
| DM-7 | 86 | `Company.website` | No URL validation. Any string accepted. |
| DM-8 | 88 | `Company.founded_year` | No range constraint. Year -5000 or 999999 both valid. |
| DM-9 | 121-124 | Score fields | All `float | None` with no bounds. Accept negative, infinity, NaN. |
| DM-10 | 145 | `employee_cagr_3yr` | NOT covered by `validate_cagr` (which only handles `revenue_cagr_*`). |
| DM-11 | 275 | `CompetitiveOverlap.overlap_score` | No bounds at all. Can be negative, >1.0, or NaN. |
| DM-12 | 273-274 | `company_a_id`, `company_b_id` | No validation that they're different. Self-overlap is valid. |

### 28.2 Defaults That Mask Missing Data

| # | Lines | Field | Default | Problem |
|---|-------|-------|---------|---------|
| DM-13 | 84 | `industry` | `"Energy Software"` | Every company without explicit industry data silently receives a domain-specific default. Should be `str | None`. |
| DM-14 | 91 | `tier` | `TIER_3` | Unknown tier silently becomes mid-tier. `market_leaders` property (line 243) filters TIER_1 — unknowns are excluded. |
| DM-15 | 92 | `threat_level` | `MEDIUM` | Unknown threat = "Medium". Cannot distinguish "assessed as medium" from "no data". |
| DM-16 | 96 | `saas_maturity` | `1` | Why not 0 or None? Implies minimum level 1 even when unknown. |
| DM-17 | 265 | `ScoringExplanation.final_score` | `0.0` | "Not scored" = "scored zero". Indistinguishable. |
| DM-18 | 310-311 | `RawDataSource.confidence`, `.relevance_score` | `0.5` | Midpoint default masks "unknown" vs "assessed as 50%". |
| DM-19 | 377-378 | `AggregatedDataRecord.average_confidence`, `.data_completeness_percentage` | `0.0` | "Not computed" = "zero confidence/completeness". |

### 28.3 Extensive Use of `Any` Undermines Type Safety

12+ fields use `Any` or `dict[str, Any]`, making Pydantic validation nearly useless for those fields:

| Lines | Field | Problem |
|-------|-------|---------|
| 344 | `AggregatedFact.value` | Revenue could be `"banana"` or `[1,2,3]` |
| 394 | `SignalExtraction.signal_value` | Completely untyped |
| 109 | `acquisitions: list[dict[str, Any]]` | Unstructured |
| 125 | `scoring_breakdown: dict[str, Any]` | Loses `ScoringExplanation` type after JSON round-trip |
| 128 | `revenue_timeline: list[dict[str, Any]]` | Unstructured |
| 136 | `profitability_raw_metrics: dict[str, Any]` | Unstructured |
| 118 | `metric_observations` | Deeply nested unstructured |
| 138 | `funding_rounds: list[dict[str, Any]]` | Unstructured |

### 28.4 String Fields That Should Be Enums

| Lines | Field | Known Values |
|-------|-------|-------------|
| 126 | `classification` | "Phoenix", "Salt", "Lead" |
| 149 | `ai_signal_level` | Unknown, should be constrained |
| 153 | `data_availability` | Unknown, should be constrained |
| 277 | `competitive_intensity` | "Low", "Medium", "High", "Critical" |
| 438 | `GatheringBatch.status` | "pending", "in_progress", "completed", "failed" |
| 435 | `refresh_mode` | "full", "incremental" |
| 483 | `confidence_level` | "low", "medium", "high", "very_high" |

### 28.5 Duplicate Field Semantics

The `Company` model has parallel fields that can diverge:

| Nested (FinancialMetric) | Top-level (Company) | Used By |
|--------------------------|--------------------|---------|
| `financials.profit_margin` | `profit_margin` (line 132) | Scoring reads nested; Excel reads top-level |
| `financials.employees` | `employee_count` (line 144) | Scoring reads nested; display reads top-level |
| `financials.valuation` | `latest_valuation_eur` (line 140) | Scoring reads nested |
| `financials.funding_raised` | `total_funding_raised_eur` (line 139) | Scoring reads nested |

### 28.6 Duplicate Divergent Enum: constants.py vs domain/models.py

`src/solstein/constants.py` defines `CompanyTier` with `TIER_1`, `TIER_1B`, `TIER_2`, `TIER_3`.
`src/solstein/domain/models.py` defines `CompanyTier` with `TIER_1`, `TIER_2`, `TIER_3`, `TIER_4`.

**TIER_1B exists only in constants. TIER_4 exists only in models.** Code importing from the wrong module gets incompatible enum values.

### 28.7 NaN Acceptance

All `float` fields accept `float('nan')`, `float('inf')`, `float('-inf')`. No Pydantic validator rejects these. NaN is particularly insidious because `NaN != NaN`, breaking equality checks and dict lookups.

### 28.8 `arbitrary_types_allowed=True` Without Justification

Line 80: `arbitrary_types_allowed=True` weakens type checking. The model uses only standard types — this flag appears unnecessary.

---

## 29. Database & Infrastructure Audit

### 29.1 CRITICAL Schema-Model Mismatches

| # | Issue | ORM | SQL Migration | Impact |
|---|-------|-----|---------------|--------|
| DB-1 | **Primary key type mismatch** | `database_models.py:33` — `Integer` | `001_companies.sql:5` — `UUID` | Inserts from ORM produce integer PKs; DB expects UUID. Complete incompatibility. |
| DB-2 | **Column name mismatch** | `database_models.py:99` — `last_updated` | `001_companies.sql:22` — `updated_at` | ORM reads/writes wrong column name. |
| DB-3 | **Type mismatch: Float vs NUMERIC** | `database_models.py:392,564,570,573,526` — `Float` | `003_research_runs.sql:8,77,81,82,57` — `NUMERIC` | Silent precision loss. |
| DB-4 | **Type mismatch: JSON vs JSONB** | `database_models.py:396,427,456,527,605` — `JSON` | Migration files — `JSONB` | ORM emits `JSON`, DB expects `JSONB`. Indexing and query operators differ. |
| DB-5 | **4 ORM tables have no migration** | `scoring_records`, `signal_records`, `market_snapshots`, `audit_trails` (lines 164-373) | None | Tables only created via `Base.metadata.create_all()` — schema conflicts with manual migrations. |
| DB-6 | **ORM has many columns absent from SQL** | `database_models.py:34-96` — 30+ columns | `001_companies.sql` — ~12 columns | ORM attempts to insert into nonexistent columns. |

### 29.2 Transaction Safety

| # | Lines | Issue | Severity |
|---|-------|-------|----------|
| DB-7 | `research_dual_write.py:33-57` | **Race condition: delete-then-insert without `SELECT FOR UPDATE`.** Concurrent runs with same `run_id` can both find `existing`, both delete, both insert. | HIGH |
| DB-8 | `research_dual_write.py:219` | **Commit inside function, no rollback on failure.** Violates caller-controlled transaction boundaries. Partial writes on exception leave dirty session. | HIGH |
| DB-9 | `research_dual_write.py:38-56` | **Manual child deletion bypasses ORM cascade.** `Query.delete()` executes bulk DELETE without ORM event synchronization. Redundant for tables with cascade; required for those without. Asymmetric and fragile. | MEDIUM |
| DB-10 | `database.py:93-94` | **Async session yielded with no commit/rollback.** Caller must handle transactions manually. No explicit rollback on exceptions. | MEDIUM |

### 29.3 Connection Management

| # | Lines | Issue | Severity |
|---|-------|-------|----------|
| DB-11 | `database.py:52-58` | **No `pool_recycle` or `pool_pre_ping`.** Stale connections returned from pool without health check. Supabase/PgBouncer may enforce idle timeouts. | MEDIUM |
| DB-12 | `database.py:96-108` | **Sync session returned without context manager.** Callers must manually close. Inconsistent with async `get_session()` which auto-closes. | MEDIUM |
| DB-13 | `database.py:137` | **Module-level singleton runs `Settings.load()` at import time.** Creates directories, logs config, reads `.env` as side effect of importing. | LOW |

### 29.4 Migration Safety

| # | Issue | Severity |
|---|-------|----------|
| DB-14 | **No `IF NOT EXISTS` guards.** All 3 migration files fail on re-run. | MEDIUM |
| DB-15 | **No migration tracking table.** No way to know which migrations have been applied. | MEDIUM |
| DB-16 | **`source_url VARCHAR(2000)` in unique constraint.** PostgreSQL B-tree index row size limit (~2712 bytes) can be exceeded with multi-byte characters. | MEDIUM |

### 29.5 Security — RLS Policies

| # | Migration | Issue | Severity |
|---|-----------|-------|----------|
| DB-17 | `001_companies.sql:48-50` | **Anonymous full INSERT/UPDATE on companies table.** `anon` role can write arbitrary company data. RLS is effectively disabled. | HIGH |
| DB-18 | `003_research_runs.sql:114-120` | **Anonymous SELECT on all research tables with `USING (true)`.** All research data publicly readable. No INSERT/UPDATE policies for service role. | MEDIUM |

### 29.6 Data Integrity Gaps

| # | Lines | Issue |
|---|-------|-------|
| DB-19 | `database_models.py:170` | `ScoringRecord.company_id` — no `ForeignKey` constraint. Can reference nonexistent companies. |
| DB-20 | `database_models.py:533-547` | Unique constraint includes nullable columns (`source_url`, `metric_value`). PostgreSQL treats NULLs as distinct — duplicates with NULL fields are not prevented. |
| DB-21 | `database_models.py:387,426` | `status` columns are plain `String(50)` — no CHECK constraint or PostgreSQL ENUM. Any arbitrary string accepted. |
| DB-22 | Multiple | Score columns (`growth_score`, `readiness_score`, `confidence`, etc.) have no CHECK constraints for valid ranges. |

---

## 30. Configuration & Exports Audit

### 30.1 config.py

| # | Lines | Issue | Severity |
|---|-------|-------|----------|
| CF-1 | 26 | **Hardcoded `postgres:postgres` in default DB URL.** Production-unsafe credentials as class-level default. | HIGH |
| CF-2 | 63-66 | **Supabase secrets as plain `str`, not `SecretStr`.** Exposed in logs, tracebacks, and serialization. | HIGH |
| CF-3 | 172-181 | **All API keys as plain `str | None`.** Same exposure risk as CF-2. | HIGH |
| CF-4 | 221-227 | **Test DB URL generation is broken.** `rsplit("/", 1)` puts `_test` after the port, not the database name. Produces invalid URL. | HIGH |
| CF-5 | 142 | **`__file__`-based project root breaks after `pip install`.** Resolves to `site-packages` directory, not project root. All relative paths become invalid. | MEDIUM |
| CF-6 | 205-206 | **`.env` path is CWD-relative, not project-root-relative.** Different working directories load different (or no) env files. | MEDIUM |
| CF-7 | 268-287 | **`get_settings()` duplicates all `Settings.load()` work.** Double `.env` check, double `ensure_dirs()`, double logging. | LOW |
| CF-8 | 95-105 | **`secret_key` validator only warns, never rejects.** "change-me-in-production" accepted in all environments. | MEDIUM |

### 30.2 scoring_config.py

| # | Lines | Issue | Severity |
|---|-------|-------|----------|
| SC-1 | 10-36 | **Maximum growth score is 15.0** (5.0 base + 4.0 + 2.0 + 2.0 + 2.0). Clamped to 10 — 5 points of discrimination lost. | MEDIUM |
| SC-2 | 39-74 | **Minimum financial health score is -0.5** (5.0 - 1.0 - 2.5 - 1.0 - 1.0). Negative score possible before clamp. | MEDIUM |
| SC-3 | 19 vs 59 | **Two sets of efficiency thresholds** with different tiers, names, and granularity. Unclear which applies where. | MEDIUM |
| SC-4 | 25-29, 44-50 | **"In Millions" comments but no unit enforcement.** If data arrives in absolute EUR, thresholds are wrong by 6 orders of magnitude. | CRITICAL (repeat) |
| SC-5 | 82-89 | **Tier score lookup has no default for unknown tiers.** `KeyError` if tier not in hardcoded dict. | MEDIUM |
| SC-6 | 107, 112 | **`geo_single_penalty` and `tech_none_penalty` defined but never used.** Config suggests penalties should exist but they're unimplemented. | LOW |
| SC-7 | All | **No `Field` constraints on any config value.** `base_score = -1000` would pass without error. | MEDIUM |

### 30.3 excel.py — Excel Dashboard

| # | Lines | Issue | Severity |
|---|-------|-------|----------|
| EX-1 | 218-228 | **All scores written as formatted strings, not numbers.** Users cannot sort, chart, or calculate on these columns. | HIGH |
| EX-2 | 222-225 | **Score of 0.0 displays as "N/A".** `0.0` is falsy — truthiness check conflates zero with missing. Affects all 4 score columns. | HIGH |
| EX-3 | 259-263 | **Financial values of 0.0 display as "N/A" or "Bootstrapped".** Revenue 0.0 → "N/A". Funding 0.0 → "Bootstrapped". Zero is not the same as missing. | HIGH |
| EX-4 | 219, 258, 301, 303, 306 | **CSV/Formula injection vulnerability.** Company names from external sources written directly to cells. Names starting with `=`, `+`, `-`, `@` execute as Excel formulas. | MEDIUM |
| EX-5 | 124 | **Banner merge hardcoded to 7 columns.** Market Rankings and Financial Intelligence have 9 columns — banner doesn't span full width. | LOW |
| EX-6 | 254 | **Financial Intelligence sheet is unsorted.** Market Rankings sorts by composite_score; Financial Intelligence uses arbitrary order. Inconsistent. | LOW |
| EX-7 | 24 | **Creates standalone `Settings()`, bypasses singleton `get_settings()`.** Different config path than pipeline. | LOW |
| EX-8 | 128 | **Timezone-naive `datetime.now()`.** Domain models use UTC; Excel banner uses local time. | LOW |

### 30.4 pyproject.toml

| # | Lines | Issue | Severity |
|---|-------|-------|----------|
| PY-1 | 5 vs 55, 123 | **`requires-python >= 3.10` but ruff/mypy target 3.12.** 3.12-only syntax passes linting but fails on 3.10/3.11. | MEDIUM |
| PY-2 | 11-30 | **All deps use floor-only pinning (`>=X`).** No upper bounds. Pydantic 3.0, FastAPI breaking changes, yfinance API changes all accepted silently. No lockfile. | HIGH |
| PY-3 | 122-152 | **mypy effectively disabled.** Only checks 4 files. 13 error codes disabled including `arg-type`, `union-attr`, `return-value`. Type checker is a no-op. | MEDIUM |
| PY-4 | 54, 109 | **Line length unenforced.** `line-length = 120` set but `E501` rule ignored. | LOW |
| PY-5 | 25 | **`aiosqlite` dependency may be unused.** Entire DB layer is PostgreSQL. | LOW |
| PY-6 | 18 | **`python-dotenv` redundant with `pydantic-settings`.** Risk of double-loading env vars. | LOW |
| PY-7 | 35, 38 | **`black` alongside `ruff format`.** Redundant formatters may conflict. | LOW |

---

## 31. Inter-Module Data Flow Inconsistencies

### 31.1 CRITICAL: Revenue Unit Mismatch Across Data Paths

| Source | Revenue Unit | Evidence |
|--------|-------------|----------|
| `competitor_data.json` via `loaders.py:96` | **EUR millions** | `latest.get("eur_millions")` |
| yfinance via `gather.py:191` | **Absolute (raw API value, typically USD)** | `info.get("totalRevenue")` |
| Scoring thresholds in `scoring_config.py:45-50` | **"In Millions" per comments** | `revenue_large_threshold: 100.0` |
| Efficiency thresholds in `scoring_config.py:19` | **"In EUR" per comments** | `efficiency_high_threshold: 500_000.0` |

**Impact**: A yfinance company with 30M real revenue has `revenue = 30,000,000`. Against the "in Millions" threshold of 100.0: `30,000,000 > 100` = True → incorrectly gets the large-revenue bonus. A loader company with the same real revenue has `revenue = 30`. Against the threshold: `30 > 100` = False → correctly scored.

**yfinance companies are systematically over-scored on every revenue-based metric.**

### 31.2 Tier Determination Uses Different Criteria Per Source

| Path | Tier Metric | Scale |
|------|------------|-------|
| `loaders.py:500-512` | Revenue | Millions (1000 = 1B) |
| `gather.py:42-49` | Market cap | Absolute (10,000,000,000 = 10B) |

Same company gets different tiers depending on entry point.

### 31.3 API Router Classification Bug

`src/solstein/api/routers/scoring.py:56-61`:
- Classifies on `growth_score` instead of `composite_score`
- Returns `"Salt"` instead of `"Salt"` for mid-range
- Ignores the already-correct `classification` field on the `Company` object

### 31.4 Inconsistent Slugification Across Entry Points

| Module | Method | Example: "ABC Corp." |
|--------|--------|---------------------|
| `discovery.py:22-30` | `ch.isalnum()` filter + hyphen | `"abc-corp"` |
| `loaders.py:270` | `.lower().replace(" ", "-").replace("/", "-")` | `"abc-corp."` (keeps dot) |
| `markdown_extractor.py:192-198` | `.lower().replace(" ", "-").replace(".", "").replace(",", "")` | `"abc-corp"` |

The same company can get different IDs from different entry points. Cross-referencing between loader data and discovery data fails silently.

---

## 32. Test Coverage Gaps

| # | Area | Issue |
|---|------|-------|
| TC-1 | `sources.py` | **Zero dedicated unit tests.** `canonicalize_url` and `is_probably_url` completely untested. Used throughout pipeline for deduplication. |
| TC-2 | `gather.py` yfinance paths | Only the no-ticker path is tested. yfinance success path, exception path, `_as_percent`, `_ai_maturity_from_text`, `_tier_from_market_cap`, `_threat_from_growth` — all untested. |
| TC-3 | `reconcile.detect_market_contradictions` | Only `detect_company_contradictions` tested. Market-level aggregation untested. |
| TC-4 | End-to-end data consistency | No integration test traces a Company from discovery → gather → scoring → evidence → export verifying field values remain consistent. |
| TC-5 | `test_core_config.py:137` | **Test asserts the BUGGY behavior** of `get_database_url(test=True)`. `_test` after port is tested as correct. |
| TC-6 | `MarketAnalyzer.analyze_market` | Public method untested. Uses `datetime.now()` (naive) which may conflict with UTC-aware model fields. |
| TC-7 | Currency conversion | No tests for `CurrencyRateFetcher`, `CurrencyConverter`, or the inverted cross-rate formula. |
| TC-8 | Excel exporter | No tests for data loss (0.0→"N/A"), formula injection, or layout issues. |

---

## 33. Hidden Dependencies & Import Side Effects

| # | Location | Issue |
|---|----------|-------|
| HD-1 | `data/fetchers.py:14` | **Top-level `import yfinance`** — no guard. Missing yfinance crashes the entire module. |
| HD-2 | `data/loaders.py:542` | **Module-level `CompetitorDataLoader()` singleton** — runs `Settings.load()` at import time. Creates directories on disk. |
| HD-3 | `infrastructure/database.py:137` | **Module-level `DatabaseManager(Settings.load())`** — same import-time side effects. |
| HD-4 | `__init__.py:19,27` | **`import solstein` requires pandas, openpyxl, pydantic-settings** installed. Missing any one crashes the entire package. |

---

## 34. Environment-Specific Behavior

### 34.1 Timezone Inconsistency

| Location | Method | Timezone |
|----------|--------|----------|
| `gather.py:69` | `datetime.now(UTC)` | UTC |
| `domain/models.py:112` | `datetime.now(UTC)` | UTC |
| `scoring.py:373` (MarketAnalyzer) | `datetime.now()` | **Local** |
| `excel.py:128` | `datetime.now()` | **Local** |
| `api/routers/scoring.py:74` | `datetime.now()` | **Local** |

On a UTC+2 machine, Excel timestamps are 2 hours ahead of gather timestamps. Mixing aware/naive datetimes in the same model can cause `TypeError` on comparison.

### 34.2 CWD-Dependent Configuration

`config.py:205` uses `Path(".env")` — resolves relative to CWD. Running from `/home/user` vs project root loads different env files.

### 34.3 Locale-Dependent Float Formatting

`excel.py` uses Python f-string formatting (`f"{value:.1f}"`). On systems with non-US locales, this could theoretically interact with locale-specific decimal separators if the `locale` module has been configured, though Python's built-in `format` is locale-independent by default.

---

## 35. Updated Comprehensive Risk Matrix (All Passes Combined)

| Risk | Likelihood | Impact | Total Issues | Status |
|------|-----------|--------|-------------|--------|
| **Revenue unit mismatch (millions vs absolute)** | HIGH | CRITICAL | §31.1, S-1, S-2 | NOT mitigated |
| **Schema-model mismatch (UUID vs Integer PK)** | HIGH | CRITICAL | DB-1 | NOT mitigated |
| **Currency conversion bugs** | HIGH | CRITICAL | F-1, F-2, F-3, F-4, L-1, L-2 | NOT mitigated |
| **Test DB URL bug (port not DB name)** | HIGH | HIGH | CF-4, TC-5 | Bug enshrined in tests |
| **Fabricated patent counts** | HIGH | HIGH | PT-1, PT-2, PT-3 | NOT mitigated |
| **All quality gates disabled by default** | HIGH | HIGH | P-1 | NOT mitigated |
| **Excel scores as strings (not sortable)** | HIGH | HIGH | EX-1 | NOT mitigated |
| **Zero values display as "N/A"** | HIGH | HIGH | EX-2, EX-3 | NOT mitigated |
| **No Pydantic bounds on financial fields** | HIGH | HIGH | DM-1 through DM-12 | NOT mitigated |
| **Anon write access to companies table** | MEDIUM | HIGH | DB-17 | NOT mitigated |
| **Credential exposure in migration script** | MEDIUM | HIGH | NS-1 | NOT mitigated |
| **Dependencies unpinned (no lockfile)** | MEDIUM | HIGH | PY-2 | NOT mitigated |
| **Duplicate divergent CompanyTier enums** | MEDIUM | HIGH | DM-23, §2.3 | NOT mitigated |
| **API router wrong classification** | HIGH | MEDIUM | §31.3 | NOT mitigated |
| **mypy effectively disabled** | HIGH | MEDIUM | PY-3 | NOT mitigated |
| **Import-time side effects** | HIGH | MEDIUM | HD-2, HD-3, HD-4 | NOT mitigated |
| **Missing tests for critical paths** | HIGH | MEDIUM | TC-1 through TC-8 | NOT mitigated |

---

## 36. Revised Priority Remediation Roadmap

### P0 — Fix Before Next Pipeline Run (carries forward + new)

1. **Fix revenue unit mismatch** (§31.1): Normalize all revenue to a single unit (absolute EUR or EUR millions) across both data paths and scoring thresholds.
2. **Fix currency rate inversion** (F-1, F-2): Normalize all Yahoo Finance pairs to consistent direction.
3. **Fix USD=1.0 in loaders** (L-1): USD is not EUR.
4. **Update hardcoded year "2025"** (W-1): Use `datetime.now().year`.
5. **Remove "patent" from AI keywords** (PT-3, PT-4).
6. **Remove fabricated patent multipliers** (PT-1, PT-2).
7. **Fix Schema-Model PK type** (DB-1): Align ORM `Integer` with SQL `UUID`, or vice versa.
8. **Fix test DB URL generation** (CF-4): `_test` goes on database name, not port.

### P1 — Fix Within Sprint (carries forward + new)

9. **Enable quality gates by default** (P-1).
10. **Add per-candidate error isolation** (P-2, P-3).
11. **Add Pydantic constraints** to `FinancialMetric` and score fields (DM-1 through DM-12).
12. **Fix Excel: write numbers not strings** (EX-1). Use `is not None` instead of truthiness (EX-2, EX-3).
13. **Sanitize Excel cell values** against formula injection (EX-4).
14. **Fix API router classification** (§31.3): Use `composite_score` and return `"Salt"`.
15. **Align ORM columns with SQL migrations** (DB-2 through DB-6).
16. **Remove duplicate `CompanyTier` enum** from constants.py.
17. **Use `SecretStr` for API keys and DB credentials** (CF-2, CF-3).
18. **Secure migration script**: Use `PGPASSWORD` env var instead of CLI arg (NS-1).
19. **Add `--single-transaction` to migration runner** (NS-3).

### P2 — Fix Within Quarter (carries forward + new)

20. **Add dependency upper bounds or lockfile** (PY-2).
21. **Enable mypy on more files, re-enable critical error codes** (PY-3).
22. **Add unit tests for `sources.py`, `gather.py` paths, `reconcile.py`** (TC-1 through TC-8).
23. **Unify slugification** across all entry points (§31.4).
24. **Make `industry` default to `None` not "Energy Software"** (DM-13).
25. **Replace `Any`-typed fields with structured models** where possible.
26. **Add `pool_recycle` and `pool_pre_ping` to DB engines** (DB-11).
27. **Add migration idempotency** (`IF NOT EXISTS`) and tracking table (DB-14, DB-15).
28. **Fix RLS policies**: Remove anonymous write access to companies (DB-17).
29. **Normalize all datetime usage to UTC** (§34.1).

### P3 — Backlog (carries forward)

30. Replace keyword-based AI maturity with LLM classifier.
31. Add URL liveness checks to evidence evaluation.
32. Add multi-source financial data for cross-validation.
33. Implement source credibility tiers.
34. Replace Google scraping with legitimate API alternatives.
35. Add end-to-end data consistency integration tests (TC-4).

---

---

# PART 4: Data Origin & Batch Size Analysis

*Appended 2026-02-23 after full provenance trace of information fetching pipelines and investigation of company count constraints.*

---

## 37. Why Only ~33 Companies — Not 100

### 37.1 The Company Count Ceiling Stack

The pipeline cannot reach 100 companies because of a stack of hard limits at every layer:

```
Layer 1: CLI Default               → max_companies = 25
Layer 2: Pipeline Function Default  → max_companies = 25
Layer 3: Discovery Function Default → max_companies = 25
Layer 4: Hardcoded Catalog Size     → 20 companies (energy) or 20 (LATAM)
Layer 5: competitor_data.json       → 33 companies (energy market only)
Layer 6: Deduplication              → ~4 exact matches removed
Layer 7: Final Truncation           → scored[:max_companies]
```

**Maximum possible companies for the energy/Dutch market:**
- 20 (hardcoded catalog) + 33 (competitor_data.json) - 4 (dedup) = **49 unique candidates**
- Default truncation at 25 → **25 in output**
- Even with `max_companies=100` → **49 is the absolute ceiling**

**Maximum possible companies for LATAM or ANY other market:**
- 20 (hardcoded catalog only — no enrichment path exists)
- **20 is the absolute ceiling regardless of max_companies setting**

### 37.2 Constraint-by-Constraint Trace

| # | File:Line | Constraint | Value | Type |
|---|-----------|-----------|-------|------|
| C-1 | `scripts/discover_and_research_market.py:13` | `--max-companies` CLI default | 25 | Overridable default |
| C-2 | `scripts/supabase_dual_write_smoke_test.py:21` | `MAX_COMPANIES` env var default | 25 | Overridable default |
| C-3 | `research/pipeline.py:24` | `max_companies` function parameter | 25 | Overridable default |
| C-4 | `research/discovery.py:468` | `max_companies` function parameter | 25 | Overridable default |
| C-5 | `research/discovery.py:36-239` | Energy market catalog | 20 entries | Hard-coded ceiling |
| C-6 | `research/discovery.py:241-462` | LATAM/fallback catalog | 20 entries | Hard-coded ceiling |
| C-7 | `data/input/competitor_data.json` | Competitor dataset | 33 entries | Data ceiling |
| C-8 | `research/discovery.py:479` | Enrichment gate: `max_companies > len(catalog)` | Only when 25 > 20 | Conditional filter |
| C-9 | `research/discovery.py:482-505` | Name deduplication | ~4 exact matches | Filter |
| C-10 | `research/discovery.py:561` | `scored[:max_companies]` | Truncation to 25 | Hard cap |
| C-11 | `research/discovery.py:475-478` | Enrichment only for energy-type markets | Other markets get 0 enrichment | Conditional filter |

### 37.3 Off-by-One in Enrichment Gate

`discovery.py:479`:
```python
) and max_companies > len(catalog):
```

If `max_companies == len(catalog)` (e.g., both are 20), enrichment from `competitor_data.json` is **skipped entirely**. Setting `max_companies=20` for the energy market yields only the 20 hardcoded companies, discarding the 29 potential additions from the JSON.

### 37.4 Silent Enrichment Failure

`discovery.py:506-510`: If `CompetitorDataLoader` fails for any reason (file not found, JSON parse error, config path mismatch), the entire enrichment is silently skipped and the catalog stays at 20. The `config.py` default `data_dir` is `data/input`, but if `DATA__DATA_DIR=data` is set in `.env`, the loader looks for `data/competitor_data.json` (doesn't exist) instead of `data/input/competitor_data.json`.

### 37.5 No Dynamic Discovery Exists

**There is no mechanism to discover companies at runtime.** Every company comes from:
1. A hardcoded Python list literal in `discovery.py` (40 total across 2 catalogs), OR
2. A static JSON file (`competitor_data.json`, 33 entries)

Despite the function name `discover_companies()`, there is zero API-based discovery. No web search, no database query, no market data scan. The "discovery" is a static catalog lookup with a relevance scoring overlay.

---

## 38. Complete Data Origin Map

### 38.1 Two Separate Pipelines Exist

The codebase contains **two distinct pipeline entry points** that are not connected:

#### Pipeline A: Discovery-First (`discover_and_research_market.py` → `pipeline.py`)

```
discover_companies()          [hardcoded catalogs + competitor_data.json]
    → build_company_profile() [yfinance for tickers, defaults for non-tickers]
    → validate_provenance()   [structural checks only]
    → detect_contradictions()
    → evaluate_evidence()
    → calculate_scores()
    → export (JSON + Excel + optional DB)
```

**Actual external API calls: yfinance ONLY**

#### Pipeline B: Markdown-First (`run_market_pipeline.py` → `BatchExtractor`)

```
BatchExtractor.extract_directory()  [reads .md files from data/input/custom_market_runs/]
    → validate_provenance()          [structural checks]
    → calculate_scores()
    → export (JSON + Excel)
```

**Actual external API calls: NONE** — reads pre-gathered markdown profiles from disk.

These pipelines are **completely independent**. Pipeline A doesn't read markdown files. Pipeline B doesn't call `discover_companies()` or yfinance.

### 38.2 55 Markdown Research Profiles Exist But Are Disconnected

55 hand-gathered research markdown files sit in `data/input/custom_market_runs/2026-02-23/`:

| Directory | Count | Market |
|-----------|-------|--------|
| `dutch_market/` | 4 | Initial Dutch energy research |
| `dutch_market_bulk/` | 33 | Bulk Dutch energy profiles |
| `latam_market/` | 3 | Initial LATAM financial research |
| `latam_market_bulk/` | 15 | Bulk LATAM financial profiles |
| **Total** | **55** | |

**These files are never read by Pipeline A** (`run_market_intelligence`). They are only consumable by Pipeline B (`run_market_pipeline.py`), which is referenced in documentation (`docs/guides/data-gathering-stages.md`) but has no evidence of ever being run.

### 38.3 Actual External Data Sources Called During Pipeline A

| Data Source | Module | Called? | Evidence |
|-------------|--------|---------|----------|
| **Hardcoded Python catalogs** | `discovery.py` | YES | Always — this is the only discovery mechanism |
| **`competitor_data.json`** | `loaders.py` | YES | Only for energy markets when `max_companies > 20` |
| **Yahoo Finance (yfinance)** | `gather.py` | YES | For companies with ticker symbols |
| Exa web search | `web_search_client.py` | **NO** | Not imported by any pipeline module |
| Google search | `web_search_client.py` | **NO** | Not imported by any pipeline module |
| NewsAPI.org | `additional_sources.py` | **NO** | Not imported by any pipeline module |
| Crunchbase API | `additional_sources.py` | **NO** | Not imported by any pipeline module |
| PatentsView API | `additional_sources.py` | **NO** | Not imported by any pipeline module |
| USPTO PEDS | `patent_client.py` | **NO** | Not imported by any pipeline module |
| Google Patents | `patent_client.py` | **NO** | Not imported by any pipeline module |
| DuckDuckGo patents | `patent_client.py` | **NO** | Not imported by any pipeline module |
| LinkedIn | `additional_sources.py` | **NO** | Not imported by any pipeline module |
| Website scraping | `additional_sources.py` | **NO** | Not imported by any pipeline module |

**11 of 13 data source capabilities are dead code — never invoked by either pipeline.**

### 38.4 Data Source Capabilities vs. Actual Usage

```
┌──────────────────────────────────────────────────────────┐
│              WHAT EXISTS IN THE CODEBASE                  │
│                                                          │
│  web_search_client.py ─── Exa API, Google Search         │
│  additional_sources.py ── NewsAPI, Crunchbase, LinkedIn,  │
│                           PatentsView, Web Scraping       │
│  patent_client.py ─────── USPTO, Google Patents, DDG      │
│  fetchers.py ──────────── Yahoo Finance, Currency Rates   │
│  loaders.py ───────────── competitor_data.json            │
│  markdown_extractor.py ── Markdown profile parsing        │
│                                                          │
└──────────────────────────────────────────────────────────┘
                         vs.
┌──────────────────────────────────────────────────────────┐
│            WHAT THE PIPELINE ACTUALLY USES                │
│                                                          │
│  1. Hardcoded Python dicts (discovery.py catalogs)       │
│  2. competitor_data.json (33 static entries)             │
│  3. yfinance (Yahoo Finance ticker lookups)              │
│                                                          │
│  Everything else is dead code.                           │
└──────────────────────────────────────────────────────────┘
```

---

## 39. Pipeline Has Never Run To Completion On Disk

### 39.1 No Pipeline A Artifacts Exist

The `data/output/` directory contains only demo script outputs:

| File | Source | Companies |
|------|--------|-----------|
| `demo_output/solstein_demo_20260218_065816.csv` | `demo_solstein.py` | 5 |
| `demo_output/solstein_demo_20260218_065816.xlsx` | `demo_solstein.py` | 5 |
| `demo_output/solstein_demo_20260219_223205.csv` | `demo_solstein.py` | 2 |
| `demo_output/solstein_demo_20260219_223205.xlsx` | `demo_solstein.py` | 2 |
| `demo_output/solstein_demo_20260219_224433.csv` | `demo_solstein.py` | 2 |
| `demo_output/solstein_demo_20260219_224433.xlsx` | `demo_solstein.py` | 2 |

**Zero** `discovery_candidates.json`, `extracted.json`, `scored.json`, `run_summary.json`, `stage_report.json`, `evidence_readiness.json`, `provenance_report.json`, `contradictions_report.json`, or `dashboard.xlsx` files exist anywhere on disk.

The full research pipeline (`run_market_intelligence`) has **never been run to completion** — or outputs were cleaned up / gitignored.

### 39.2 No Pipeline B Artifacts Exist

Despite 55 markdown research profiles existing in `data/input/custom_market_runs/`, `run_market_pipeline.py` has never been executed (no output directories exist for it).

### 39.3 Demo Script Bypasses The Entire Pipeline

`scripts/demo_solstein.py` is the only script that has produced output. It:
- Reads directly from `competitor_data.json` with a hard cap of 5 companies
- Bypasses discovery, evidence evaluation, contradiction detection, and quality gates
- Uses a simplified scoring path
- Is not representative of the full pipeline's capabilities

---

## 40. Root Causes: Why Not 100 Companies

### 40.1 Structural Limitations (Cannot Be Overcome Without Code Changes)

| Cause | Impact | Fix Required |
|-------|--------|-------------|
| **Only 2 hardcoded catalogs exist** (20 + 20 = 40 companies) | Universe is 40 + 33 = 49 max (energy) or 20 max (any other market) | Add catalogs for more markets, or implement dynamic discovery |
| **No external discovery API** | Cannot find companies at runtime | Integrate Exa, Crunchbase, or similar for dynamic company discovery |
| **`competitor_data.json` only covers energy market** | LATAM and all other markets have no enrichment source | Create equivalent JSON datasets for other markets |
| **Enrichment only works for energy-type markets** | `discovery.py:475-478` gates enrichment on market name containing "dutch"/"netherlands"/"energy" | Remove market-type gate or make enrichment market-agnostic |

### 40.2 Configuration Limitations (Overridable But Not Obvious)

| Cause | Default | Max Achievable |
|-------|---------|---------------|
| `max_companies` default is 25 | 25 | Set `--max-companies 100` but still capped by data ceiling |
| No CLI option to add extra catalogs | N/A | Would require code change to load additional market catalogs |
| No CLI option to enable web search enrichment | N/A | Would require integrating `web_search_client.py` into pipeline |

### 40.3 Dead Code That Could Help

The codebase already contains implementations for:
- **Web search** (`web_search_client.py`) — could discover new companies via Exa/Google
- **News aggregation** (`additional_sources.py`) — could identify trending/emerging companies
- **Patent search** (`patent_client.py`) — could enrich company profiles with IP data

None of these are wired into the pipeline. Connecting them would:
1. Enable dynamic company discovery (breaking the 49-company ceiling)
2. Enrich profiles with multi-source data (improving evidence readiness scores)
3. Enable cross-validation (catching data inaccuracies)

### 40.4 The "33" Number Explained

The number 33 likely comes from `competitor_data.json` containing exactly 33 entries. When users count "how many companies does Solstein know about", they see the 33 in the JSON file. But the pipeline's actual output depends on which path is taken:

| Scenario | Output Count | Explanation |
|----------|-------------|-------------|
| Energy market, default settings | **25** | 49 candidates truncated to `max_companies=25` |
| Energy market, `max_companies=100` | **49** | Full universe: 20 catalog + 33 JSON - 4 dedup |
| Energy market, enrichment fails | **20** | Only hardcoded catalog, JSON silently skipped |
| LATAM market, any settings | **20** | Only hardcoded catalog, no enrichment path |
| Any unknown market | **20** | Falls through to LATAM catalog as default |
| Demo script | **2-5** | Hard-capped in demo code |

---

## 41. Disconnected Data Assets

### 41.1 Markdown Profiles Not Consumed By Main Pipeline

55 research markdown files in `data/input/custom_market_runs/` are only consumable by `scripts/run_market_pipeline.py` (Pipeline B), which:
- Reads `.md` files via `BatchExtractor.extract_directory()`
- Scores and exports
- Does NOT call yfinance, web search, or any enrichment API
- Has never been run (no output artifacts exist)

**Pipeline A** (`run_market_intelligence`) does not read these files. It uses `discover_companies()` + `build_company_profile()`, which only touch the hardcoded catalogs, `competitor_data.json`, and yfinance.

The two pipelines produce **different Company objects** from **different data sources** with **no shared lineage**.

### 41.2 `fetchers.py` Partially Dead

`src/solstein/data/fetchers.py` contains:
- `YahooFinanceFetcher` — used by `gather.py` indirectly via `yfinance`
- `CurrencyRateFetcher` — **not imported by any pipeline module**
- `CurrencyConverter` — **not imported by any pipeline module**
- `GlobalMarketLoader` — **not imported by any pipeline module**
- `get_market_summary()` — **not imported by any pipeline module**

The currency conversion and market summary capabilities exist but are never used in either pipeline.

### 41.3 `additional_sources.py` Exists in TWO Locations

The same module is duplicated:
- `src/solstein/data/additional_sources.py`
- `src/solstein/infrastructure/data_loaders/additional_sources.py`

Neither copy is imported by either pipeline. Both are dead code.

Similarly `patent_client.py` is duplicated:
- `src/solstein/data/patent_client.py`
- `src/solstein/infrastructure/data_loaders/patent_client.py`

Both are dead code.

---

## 42. Updated Risk Matrix — Data Origin Findings

| Risk | Likelihood | Impact | Issues | Status |
|------|-----------|--------|--------|--------|
| **Total company universe capped at 49** | CERTAIN | HIGH | §37.1 | Structural — no dynamic discovery |
| **Non-energy markets limited to 20 companies** | CERTAIN | HIGH | C-6, C-11 | No enrichment path exists |
| **11 of 13 data source modules are dead code** | CERTAIN | HIGH | §38.3 | Never integrated into pipeline |
| **Pipeline never run to completion** | HIGH | HIGH | §39.1 | Only demo outputs exist on disk |
| **Two disconnected pipelines** | CERTAIN | MEDIUM | §38.1 | Markdown profiles unreachable from main pipeline |
| **Silent enrichment failure drops to 20 companies** | MEDIUM | HIGH | C-8, §37.4 | Config path mismatch can trigger this |
| **Markdown profiles are a wasted data asset** | CERTAIN | MEDIUM | §41.1 | 55 files not consumed by primary pipeline |
| **Duplicate dead modules** | CERTAIN | LOW | §41.3 | `additional_sources.py` and `patent_client.py` in 2 locations each |

---

## 43. Recommendations — Reaching 100+ Companies

### Phase 1: Unlock Existing Data (no new code needed)

1. **Raise `max_companies` default** to 50 or 100 in all three locations (CLI, pipeline, discovery).
2. **Add more companies to hardcoded catalogs** — the energy catalog has 20 entries, could easily be 50-100 with known players.
3. **Create additional market catalogs** — currently only energy and LATAM exist. Add tech, healthcare, fintech-global, etc.
4. **Create `competitor_data.json` equivalents for other markets** — the LATAM path has no enrichment dataset.

### Phase 2: Wire Up Dead Code (moderate effort)

5. **Integrate `web_search_client.py` into discovery** — use Exa search to find additional companies dynamically when catalogs are exhausted.
6. **Integrate `additional_sources.py` into gather** — enrich company profiles with news, funding, and patent data.
7. **Integrate `patent_client.py` into gather** — replace keyword-based AI maturity with actual patent analysis.
8. **Connect Pipeline B into Pipeline A** — use markdown profiles as an additional data source in `discover_companies()` or `build_company_profile()`.

### Phase 3: True Dynamic Discovery (significant effort)

9. **Implement API-based company discovery** — use Exa, Crunchbase, or industry databases to find companies matching market keywords at runtime.
10. **Implement competitor graph traversal** — start from seed company, find competitors, find their competitors, building a network.
11. **Implement automatic catalog refresh** — periodically re-fetch financials for cataloged companies and add newly discovered ones.

---

*Total issues cataloged across all four passes: **190+** across CRITICAL, HIGH, MEDIUM, and LOW severity.*
*Audit covers 20+ source files, 3 SQL migrations, 3 scripts, pyproject.toml, inter-module data flows, data provenance, and batch size constraints.*
