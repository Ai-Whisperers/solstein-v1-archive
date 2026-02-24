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

*Audit conducted by automated review of source code on master branch at commit 4c4fa7a.*
