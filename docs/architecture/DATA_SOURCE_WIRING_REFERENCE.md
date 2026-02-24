# Data Source Wiring Reference

> Generated: 2026-02-24
> Purpose: Reference for wiring 11 dead data-source modules into the active pipeline with adapter abstractions for modularity.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Current State: What Is Wired vs Dead](#2-current-state)
3. [Existing Domain Models to Build On](#3-existing-domain-models)
4. [Adapter Protocol Definitions](#4-adapter-protocol-definitions)
5. [Integration Points in the Pipeline](#5-integration-points)
6. [Dead Module API Surfaces](#6-dead-module-api-surfaces)
7. [Module-to-Adapter Mapping](#7-module-to-adapter-mapping)
8. [DataSourceType Enum Gaps](#8-datasourcetype-enum-gaps)
9. [Wiring Architecture](#9-wiring-architecture)
10. [Implementation Priority](#10-implementation-priority)
11. [Known Issues to Fix During Wiring](#11-known-issues)

---

## 1. Executive Summary

The Solstein pipeline has **13 data-source modules**. Only **2 are wired** into the active pipeline:

| Status | Modules |
|--------|---------|
| **WIRED** | `discovery.py` (hardcoded catalogs), `gather.py` (yfinance via ticker) |
| **DEAD** | `web_search_client.py`, `additional_sources.py`, `patent_client.py`, `company_research.py`, `fetchers.py` (3 unused classes), + 2 infrastructure duplicates |

The pipeline also has **5 domain models** (`RawDataSource`, `RawDataRecord`, `AggregatedFact`, `AggregatedDataRecord`, `SignalExtraction`) that were designed for multi-source aggregation but are **never instantiated** anywhere.

This document defines three adapter protocols, maps every dead module to its target protocol, and identifies the 9 exact pipeline integration points where adapters plug in.

---

## 2. Current State

### Active Data Flow

```
discover_companies()          build_company_profile()
       |                              |
  Hardcoded Python dicts         yfinance.Ticker(ticker).info
  (21 energy, 22 LATAM)         (revenue, growth, employees,
       |                         profit_margin, valuation)
       v                              v
  DiscoveryCandidate[]            Company[]
```

### Dead Modules Inventory

| # | Module | Location | Capability | Why Dead |
|---|--------|----------|-----------|----------|
| 1 | `web_search_client` | `data/` | Exa + Google company news/info search | Never imported by pipeline |
| 2 | `AdditionalDataSources` | `data/additional_sources.py` | NewsAPI, Crunchbase, PatentsView, LinkedIn, website scraping | Never imported by pipeline |
| 3 | `patent_client` | `data/` | USPTO + Google Patents + DuckDuckGo patent search | Never imported by pipeline |
| 4 | `CompanyResearcher` | `data/company_research.py` | Full yfinance-based company research with 8 sub-models | Never imported by pipeline |
| 5 | `CurrencyRateFetcher` | `data/fetchers.py` | Multi-currency exchange rate fetching | Never called |
| 6 | `CurrencyConverter` | `data/fetchers.py` | Currency conversion between pairs | Never called |
| 7 | `GlobalMarketLoader` | `data/fetchers.py` | Multi-market stock data with currency normalization | Never called by pipeline |
| 8 | `get_market_summary()` | `data/fetchers.py` | All major market indices summary | Never called |
| 9 | `additional_sources` | `infrastructure/data_loaders/` | Duplicate of #2 using httpx instead of requests | Broken imports |
| 10 | `patent_client` | `infrastructure/data_loaders/` | Duplicate of #3 using lxml instead of bs4 | Broken imports |
| 11 | `RawDataSource` pipeline | `domain/models.py` | 5 models for multi-source aggregation | Defined but never instantiated |

### Duplicate Consolidation Decision

Two modules exist in both `data/` and `infrastructure/data_loaders/`:

| Module | `data/` version | `infrastructure/` version | Recommendation |
|--------|----------------|--------------------------|----------------|
| `additional_sources` | `requests` + `bs4` | `httpx` + broken imports | **Keep `data/` version**, delete infrastructure duplicate |
| `patent_client` | `requests` + `bs4` | `httpx` + `lxml` | **Keep `data/` version**, delete infrastructure duplicate |

Rationale: The `data/` versions have working imports and consistent HTTP client usage with the rest of the codebase. The infrastructure duplicates have broken import paths and add no functionality.

---

## 3. Existing Domain Models to Build On

These models in `src/solstein/domain/models.py` were designed for the multi-source aggregation architecture but are unused. **Wire into them rather than reinventing.**

### RawDataSource (lines 249-267)

Represents a single data retrieval from one source.

```python
class RawDataSource(BaseModel):
    source_type: DataSourceType       # Enum: GITHUB, NEWS, CRUNCHBASE, etc.
    source_name: str                  # Human-readable source name
    raw_content: str | dict[str, Any] # Raw API response or scraped content
    url: str | None                   # Source URL
    retrieval_timestamp: datetime     # When data was fetched
    publication_date: datetime | None # When source was published
    confidence: float                 # 0.0-1.0 confidence in data quality
    relevance_score: float            # 0.0-1.0 relevance to company
    metadata: dict[str, Any]         # Extra context
    extraction_method: str | None     # How data was extracted
```

### RawDataRecord (lines 270-285)

Groups multiple sources for one company in one batch.

```python
class RawDataRecord(BaseModel):
    company_id: str                   # Links to Company.company_id
    gathering_batch_id: str           # Groups sources from same run
    timestamp: datetime               # Batch timestamp
    sources: list[RawDataSource]      # All raw sources collected
    total_sources_found: int          # Count of sources attempted
    # Property: source_count_by_type -> dict[str, int]
```

### AggregatedFact (lines 288-327)

A single fact derived from multiple sources with agreement tracking.

```python
class AggregatedFact(BaseModel):
    fact_type: str                           # e.g. "revenue", "employee_count"
    value: Any                               # The aggregated value
    confidence: float                        # 0.0-1.0
    year: int | None                         # Year the fact applies to
    sources_used: list[str]                  # Source names that contributed
    source_agreement_percentage: float       # 0.0-1.0 agreement between sources
    source_credibility_scores: dict[str, float]  # Per-source credibility
    contradictions_detected: list[dict[str, Any]] # Where sources disagree
    is_verified: bool                        # Cross-source verification flag
```

### AggregatedDataRecord (lines 330-360)

Aggregated facts for one company with quality metrics.

```python
class AggregatedDataRecord(BaseModel):
    company_id: str
    gathering_batch_id: str
    timestamp: datetime
    facts: list[AggregatedFact]
    total_facts: int
    verified_facts: int
    average_confidence: float
    data_completeness_percentage: float
    # Method: update_quality_metrics() — recalculates from facts
```

### SignalExtraction (lines 363-395)

Bridges aggregated facts to scoring dimensions.

```python
class SignalExtraction(BaseModel):
    signal_name: str                  # e.g. "growth_rate", "ai_maturity"
    signal_value: Any                 # Extracted signal value
    signal_confidence: float          # 0.0-1.0
    source_facts: list[str]          # Which fact_types were used
    calculation_method: str           # "average", "max", "enum_classification"
    calculation_formula: str | None   # Human-readable formula
    reasoning: str | None             # Why this signal matters
    why_it_matters: str | None        # Business context
```

### Company Model Multi-Source Fields (lines 99-102)

```python
class Company(BaseModel):
    # ... other fields ...
    source_links: list[str]                              # All source URLs
    metric_sources: dict[str, list[str]]                 # Metric -> source URLs
    metric_justifications: dict[str, str]                # Metric -> explanation
    metric_observations: dict[str, list[dict[str, Any]]] # Metric -> [{source, value}]
```

---

## 4. Adapter Protocol Definitions

Three protocols cover all 11 dead modules. Each protocol produces `RawDataSource` objects that feed the existing domain model pipeline.

### Protocol 1: DiscoverySource

Produces candidates for the discovery stage. Replaces/supplements hardcoded catalogs.

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class DiscoverySource(Protocol):
    """Provides company candidates for a given market."""

    source_name: str  # e.g. "exa_search", "crunchbase", "competitor_json"

    def discover(
        self,
        market: str,
        seed_company: str,
        max_results: int = 50,
        extra_keywords: list[str] | None = None,
    ) -> list[DiscoveryCandidate]:
        """Return candidate companies for the target market."""
        ...
```

**Modules that implement this:**
- `web_search_client.search_company_info()` — search for companies by market keywords
- `additional_sources.get_funding_data()` — discover funded companies in a space
- `company_research.CompanyResearcher` — discover companies via ticker universe
- Static catalog (current behavior, wrapped as an adapter)

### Protocol 2: EnrichmentSource

Provides factual data about a known company. Multiple enrichment sources can be composed.

```python
@runtime_checkable
class EnrichmentSource(Protocol):
    """Enriches a company profile with data from one source."""

    source_name: str  # e.g. "yahoo_finance", "newsapi", "patents_view"
    source_type: DataSourceType  # Enum value for this source

    def enrich(
        self,
        company_id: str,
        company_name: str,
        ticker: str | None = None,
        website: str | None = None,
    ) -> RawDataSource:
        """Fetch raw data for a single company. Returns a RawDataSource."""
        ...
```

**Modules that implement this:**
- `fetchers.YahooFinanceFetcher.get_quote()` — financial data (already partially wired)
- `fetchers.GlobalMarketLoader.get_stock_data()` — broader market data with currency normalization
- `web_search_client.search_company_news()` — news articles
- `additional_sources.AdditionalDataSources.get_news()` — press coverage + sentiment
- `additional_sources.AdditionalDataSources.get_funding_data()` — funding rounds
- `additional_sources.AdditionalDataSources.get_patent_data()` — patent portfolio
- `additional_sources.AdditionalDataSources.get_linkedin_data()` — headcount, hiring signals
- `additional_sources.AdditionalDataSources.scrape_company_website()` — product info
- `patent_client.search_company_patents()` — detailed patent search
- `company_research.CompanyResearcher.research()` — comprehensive yfinance profile

### Protocol 3: FactAggregator

Takes multiple `RawDataSource` objects and produces `AggregatedFact` objects. This is the new logic that doesn't exist yet.

```python
@runtime_checkable
class FactAggregator(Protocol):
    """Aggregates raw data from multiple sources into verified facts."""

    def aggregate(
        self,
        company_id: str,
        raw_record: RawDataRecord,
    ) -> AggregatedDataRecord:
        """Cross-reference sources, resolve contradictions, return aggregated facts."""
        ...
```

This protocol bridges `RawDataSource` → `AggregatedFact` → Company model population. Currently, `gather.py` writes metrics directly from one source without aggregation.

---

## 5. Integration Points in the Pipeline

Nine integration points in the active pipeline where adapters can plug in, ordered by execution sequence.

### D1: Discovery — Multi-Source Candidate Generation

**File:** `src/solstein/research/discovery.py`
**Function:** `discover_companies()` (line 104)
**Current behavior:** Returns hardcoded catalog entries
**Target behavior:** Iterate over registered `DiscoverySource` adapters, merge and deduplicate candidates

```python
# CURRENT (line 118)
catalog = _catalog_for_market(market)

# TARGET
sources: list[DiscoverySource] = registry.get_discovery_sources()
all_candidates = []
for source in sources:
    all_candidates.extend(source.discover(market, seed_company, max_results, extra_keywords))
catalog = deduplicate_candidates(all_candidates)
```

### D2: Discovery — Expansion Beyond Catalog

**File:** `src/solstein/research/discovery.py`
**Function:** `discover_companies()` (line 117)
**Current behavior:** Loads from `CompetitorDataLoader` when `max_companies > len(catalog)`
**Target behavior:** Use `DiscoverySource` adapters as expansion sources

### D3: Discovery — Relevance Scoring

**File:** `src/solstein/research/discovery.py`
**Function:** `discover_companies()` (lines 152-167)
**Current behavior:** Simple name/tag/region heuristics
**Target behavior:** Optional `RelevanceScorer` that uses richer signals (news mentions, shared investors, tech stack overlap)

### E1: Gather — Primary Enrichment

**File:** `src/solstein/research/gather.py`
**Function:** `build_company_profile()` (line 27)
**Current behavior:** Only fetches from yfinance via `yf.Ticker(ticker).info`
**Target behavior:** Iterate over registered `EnrichmentSource` adapters, collect `RawDataSource` objects into a `RawDataRecord`

```python
# CURRENT (line 121)
info = yf.Ticker(candidate.ticker).info

# TARGET
enrichment_sources: list[EnrichmentSource] = registry.get_enrichment_sources()
raw_sources = []
for source in enrichment_sources:
    try:
        raw = source.enrich(candidate.company_id, candidate.name, candidate.ticker)
        raw_sources.append(raw)
    except Exception:
        continue  # graceful degradation
raw_record = RawDataRecord(
    company_id=candidate.company_id,
    gathering_batch_id=batch_id,
    timestamp=datetime.utcnow(),
    sources=raw_sources,
    total_sources_found=len(raw_sources),
)
```

### E2: Gather — Fact Aggregation (NEW STAGE)

**File:** NEW — `src/solstein/research/aggregate.py`
**Current behavior:** Does not exist. `gather.py` writes single-source values directly.
**Target behavior:** `FactAggregator` cross-references `RawDataRecord` into `AggregatedDataRecord`

```python
aggregator = DefaultFactAggregator()
aggregated = aggregator.aggregate(candidate.company_id, raw_record)
```

### E3: Gather — Signal Extraction (NEW STAGE)

**File:** NEW — `src/solstein/research/signals.py`
**Current behavior:** Does not exist. Scoring operates on raw Company fields.
**Target behavior:** Extract `SignalExtraction` objects from `AggregatedDataRecord`, then populate Company model fields

```python
signals = extract_signals(aggregated)
company = build_company_from_signals(candidate, signals, aggregated)
```

### R1: Pipeline — Source Volume Gate

**File:** `src/solstein/research/pipeline.py`
**Function:** `run_market_intelligence()` (line 104)
**Current behavior:** Counts unique URLs from `company.source_links`
**Target behavior:** Count actual `RawDataSource` objects per company, with per-source-type minimums

### EV1: Evidence Readiness

**File:** `src/solstein/research/evidence.py`
**Function:** `evaluate_market_evidence()`
**Current behavior:** Scores based on metric presence and source link counts
**Target behavior:** Score based on `AggregatedFact.source_agreement_percentage` and `is_verified`

### S1: Scoring — Multi-Signal Input

**File:** `src/solstein/analytics/scoring.py`
**Function:** `GrowthScorer.calculate_scores()`
**Current behavior:** Reads Company fields directly, no confidence weighting
**Target behavior:** Read `SignalExtraction` objects, weight by `signal_confidence`

---

## 6. Dead Module API Surfaces

### 6.1 web_search_client.py

```python
def search_company_news(company_name: str, max_results: int = 20) -> list[dict[str, Any]]
    # Returns: [{"title", "snippet", "url", "date"}]
    # Backend: Exa primary, Google Search fallback
    # BUG: Hardcoded "2025" in date filter queries

def search_company_info(company_name: str, query_type: str = "general") -> list[dict[str, Any]]
    # query_type: "general" | "funding" | "product" | "technology"
    # Returns: [{"title", "snippet", "url"}]
    # Backend: Exa only
```

**Adapter target:** `EnrichmentSource` (news) + `DiscoverySource` (info search for new companies)
**Dependencies:** `exa_py`, `googlesearch-python` (optional)

### 6.2 additional_sources.py (AdditionalDataSources)

```python
class AdditionalDataSources:
    def __init__(self, news_api_key=None, crunchbase_key=None, patentsview_api_key=None)
    def get_news(self, company_name: str, days_back: int = 30) -> PressCoverage
    def scrape_company_website(self, company_name: str, website: str) -> ProductInfo
    def get_funding_data(self, company_name: str) -> FundingData
    def get_patent_data(self, company_name: str) -> PatentData
    def get_linkedin_data(self, company_name: str) -> LinkedInData

# Pydantic models returned:
# PressCoverage: articles, total_articles, positive/negative/neutral_count, sentiment_score
# FundingData: total_raised, last_round_amount/date/stage/valuation, investors, num_rounds
# PatentData: total_patents, recent_patents, ai_related_patents, top_patent_categories
# ProductInfo: main_products, features, pricing_model, target_customers, tech_stack
# LinkedInData: employee_count, employee_growth_pct, open_positions, ai_related_positions

def get_all_company_data(ticker, news_api_key=None, crunchbase_key=None) -> dict[str, Any]
    # Convenience: calls CompanyResearcher + GlobalMarketLoader + get_news + get_funding
```

**Adapter target:** `EnrichmentSource` (5 separate adapters, one per method)
**Dependencies:** `requests`, `beautifulsoup4`, `newsapi-python` (optional)

### 6.3 patent_client.py

```python
class PatentResult:
    total_patents: int
    recent_patents: list[dict[str, Any]]
    ai_related_patents: int
    top_categories: list[str]
    source: str  # "uspto" | "google_patents" | "duckduckgo" | "none"

def search_company_patents(company_name: str) -> PatentResult
    # Cascading: USPTO PEDS -> Google Patents -> DuckDuckGo
    # BUG: Patent counts fabricated (Google x5, DDG x3)
    # BUG: "patent" is listed as AI keyword, inflating all ai_related counts
```

**Adapter target:** `EnrichmentSource`
**Dependencies:** `requests`, `beautifulsoup4`

### 6.4 company_research.py (CompanyResearcher)

```python
class CompanyResearcher:
    def research(self, ticker: str) -> CompanyResearch

# CompanyResearch composite model includes:
#   ticker, name, exchange, description, founded, headquarters, website
#   leadership: CompanyLeadership (ceo, cfo, cto, board, founders)
#   financials: CompanyFinancials (revenue, revenue_growth_yoy, ebitda, net_income, ...)
#   products: CompanyProducts (description, products, services, competitors)
#   technology: CompanyTechnology (industry, sector, tech_stack, deployment_model)
#   growth: CompanyGrowthSignals (employee_count, job_postings, ai_related_jobs)
#   ai: CompanyAIAssessment (ai_score, ai_signal_strength, ai_products, ...)
#   news: CompanyNews (headlines, press_releases, earnings_calls, M&A, filings)
#   scorecard, composite_score, classification

def research_company(ticker: str) -> dict[str, Any]
    # Convenience wrapper
```

**Adapter target:** `EnrichmentSource` (most comprehensive single-source enrichment)
**Dependencies:** `yfinance`
**Note:** Overlaps with existing `gather.py` yfinance usage — should replace it, not duplicate

### 6.5 fetchers.py (Unused Classes)

```python
class CurrencyRateFetcher:
    def fetch_all_rates(self, base_currency: Currency = Currency.USD) -> dict[tuple[Currency, Currency], float]
    def get_live_rate(self, from_currency: Currency, to_currency: Currency) -> float | None
    def convert(self, amount: float, from_currency: Currency, to_currency: Currency) -> float
    # BUG: Cross-rate formula inverted (to_usd/from_usd should be from_usd/to_usd)
    # BUG: Silent 1.0 fallback for missing rates

class GlobalMarketLoader:
    def get_stock_data(self, ticker: str, target_currency: Currency = Currency.USD) -> GlobalStockData | None
    def get_index_data(self, index_symbol: str) -> IndexData | None
    def get_multiple_stocks(self, tickers: list[str], target_currency: Currency = Currency.USD) -> list[GlobalStockData]
    def get_indices_by_region(self, region: str) -> list[IndexData]
    def get_all_major_indices(self) -> list[IndexData]

def get_market_summary() -> dict[str, Any]
```

**Adapter target:** `EnrichmentSource` (GlobalMarketLoader), utility (CurrencyRateFetcher)
**Dependencies:** `yfinance`

---

## 7. Module-to-Adapter Mapping

### DiscoverySource Adapters

| Adapter Name | Wraps Module | Method | Output |
|-------------|-------------|--------|--------|
| `StaticCatalogSource` | `discovery._catalog_for_market()` | Returns hardcoded entries | `DiscoveryCandidate[]` |
| `WebSearchDiscoverySource` | `web_search_client.search_company_info()` | Searches for companies by market keywords | `DiscoveryCandidate[]` |
| `CompetitorJsonSource` | `loaders.CompetitorDataLoader` | Reads `competitor_data.json` | `DiscoveryCandidate[]` |

### EnrichmentSource Adapters

| Adapter Name | Wraps Module | Method | DataSourceType |
|-------------|-------------|--------|---------------|
| `YahooFinanceEnrichment` | `company_research.CompanyResearcher.research()` | Full yfinance profile | `YAHOO_FINANCE` (new) |
| `GlobalMarketEnrichment` | `fetchers.GlobalMarketLoader.get_stock_data()` | Market data with FX normalization | `YAHOO_FINANCE` (new) |
| `NewsEnrichment` | `additional_sources.get_news()` | Press coverage + sentiment | `NEWS` |
| `WebSearchNewsEnrichment` | `web_search_client.search_company_news()` | News via Exa/Google | `NEWS` |
| `FundingEnrichment` | `additional_sources.get_funding_data()` | Crunchbase funding data | `CRUNCHBASE` |
| `PatentEnrichment` | `patent_client.search_company_patents()` | Patent portfolio | `PATENTS` |
| `LinkedInEnrichment` | `additional_sources.get_linkedin_data()` | Headcount, hiring | `LINKEDIN` |
| `WebsiteEnrichment` | `additional_sources.scrape_company_website()` | Product info | `WEBSITE` |

### Utility (Not an Adapter)

| Name | Wraps | Purpose |
|------|-------|---------|
| `CurrencyNormalizer` | `fetchers.CurrencyRateFetcher` | Normalize all financial values to a common currency before scoring |

---

## 8. DataSourceType Enum Gaps

Current enum (`models.py` lines 237-246):
```python
class DataSourceType(str, Enum):
    GITHUB = "github"
    COMPANY_FILINGS = "company_filings"
    NEWS = "news"
    CRUNCHBASE = "crunchbase"
    LINKEDIN = "linkedin"
    PATENTS = "patents"
    WEBSITE = "website"
    PRESS_RELEASE = "press_release"
```

**Missing values needed for the dead modules:**

| Value | Used By |
|-------|---------|
| `YAHOO_FINANCE = "yahoo_finance"` | `fetchers.py`, `company_research.py` |
| `EXA_SEARCH = "exa_search"` | `web_search_client.py` |
| `GOOGLE_SEARCH = "google_search"` | `web_search_client.py` (fallback) |
| `USPTO = "uspto"` | `patent_client.py` |
| `GOOGLE_PATENTS = "google_patents"` | `patent_client.py` |
| `NEWSAPI = "newsapi"` | `additional_sources.py` |
| `COMPETITOR_JSON = "competitor_json"` | `loaders.py` static data |
| `STATIC_CATALOG = "static_catalog"` | `discovery.py` hardcoded entries |

---

## 9. Wiring Architecture

### Layer Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                         Pipeline Layer                           │
│  pipeline.py: run_market_intelligence()                         │
│    orchestrates stages, quality gates, export                   │
└──────────────┬───────────────────────────────┬──────────────────┘
               │                               │
┌──────────────▼──────────────┐  ┌─────────────▼─────────────────┐
│     Discovery Stage          │  │      Enrichment Stage          │
│  discovery.py                │  │  gather.py → aggregate.py      │
│                              │  │           → signals.py         │
│  DiscoverySource[] adapters  │  │  EnrichmentSource[] adapters   │
│  → DiscoveryCandidate[]      │  │  → RawDataRecord               │
│                              │  │  → AggregatedDataRecord        │
│                              │  │  → SignalExtraction[]          │
│                              │  │  → Company                     │
└──────────────┬───────────────┘  └─────────────┬─────────────────┘
               │                                │
┌──────────────▼────────────────────────────────▼─────────────────┐
│                      Adapter Layer (NEW)                         │
│  src/solstein/adapters/                                          │
│    registry.py          — SourceRegistry singleton               │
│    discovery/                                                    │
│      static_catalog.py  — wraps _catalog_for_market()           │
│      web_search.py      — wraps web_search_client               │
│      competitor_json.py — wraps CompetitorDataLoader             │
│    enrichment/                                                   │
│      yahoo_finance.py   — wraps CompanyResearcher                │
│      news.py            — wraps AdditionalDataSources.get_news   │
│      funding.py         — wraps AdditionalDataSources.get_funding│
│      patents.py         — wraps patent_client                    │
│      linkedin.py        — wraps AdditionalDataSources.linkedin   │
│      website.py         — wraps AdditionalDataSources.scrape     │
│    aggregation/                                                  │
│      default.py         — multi-source fact aggregation          │
│    signals/                                                      │
│      default.py         — AggregatedFact → SignalExtraction      │
└──────────────┬──────────────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────────────┐
│                      Data Source Layer (existing)                 │
│  src/solstein/data/                                              │
│    fetchers.py           — YahooFinanceFetcher, GlobalMarketLoader│
│    web_search_client.py  — Exa / Google search                   │
│    additional_sources.py — NewsAPI, Crunchbase, Patents, LinkedIn │
│    patent_client.py      — USPTO, Google Patents, DuckDuckGo     │
│    company_research.py   — CompanyResearcher                     │
│    loaders.py            — Static JSON/CSV loading               │
└──────────────────────────────────────────────────────────────────┘
```

### Source Registry

```python
# src/solstein/adapters/registry.py

from dataclasses import dataclass, field

@dataclass
class SourceRegistry:
    """Central registry for all data source adapters."""

    discovery_sources: list[DiscoverySource] = field(default_factory=list)
    enrichment_sources: list[EnrichmentSource] = field(default_factory=list)

    def register_discovery(self, source: DiscoverySource) -> None:
        self.discovery_sources.append(source)

    def register_enrichment(self, source: EnrichmentSource) -> None:
        self.enrichment_sources.append(source)

    def get_discovery_sources(self) -> list[DiscoverySource]:
        return list(self.discovery_sources)

    def get_enrichment_sources(self) -> list[EnrichmentSource]:
        return list(self.enrichment_sources)


def build_default_registry(settings: Settings) -> SourceRegistry:
    """Build registry with all available sources based on config."""
    registry = SourceRegistry()

    # Always available
    registry.register_discovery(StaticCatalogSource())
    registry.register_discovery(CompetitorJsonSource())
    registry.register_enrichment(YahooFinanceEnrichment())

    # Conditional on API keys
    if settings.exa_api_key:
        registry.register_discovery(WebSearchDiscoverySource(settings.exa_api_key))
        registry.register_enrichment(WebSearchNewsEnrichment(settings.exa_api_key))
    if settings.news_api_key:
        registry.register_enrichment(NewsEnrichment(settings.news_api_key))
    if settings.crunchbase_api_key:
        registry.register_enrichment(FundingEnrichment(settings.crunchbase_api_key))
    if settings.patentsview_api_key:
        registry.register_enrichment(PatentEnrichment(settings.patentsview_api_key))

    return registry
```

### Data Flow Through Adapters

```
1. Discovery:
   for source in registry.discovery_sources:
       candidates += source.discover(market, seed_company)
   candidates = deduplicate(candidates)
   candidates = score_relevance(candidates, seed_company)
   candidates = candidates[:max_companies]

2. Enrichment:
   for candidate in candidates:
       raw_sources = []
       for source in registry.enrichment_sources:
           raw = source.enrich(candidate.company_id, candidate.name, candidate.ticker)
           raw_sources.append(raw)
       raw_record = RawDataRecord(company_id=..., sources=raw_sources, ...)

3. Aggregation (NEW):
       aggregated = aggregator.aggregate(candidate.company_id, raw_record)
       # Cross-references sources, detects contradictions,
       # computes agreement percentages, marks verified facts

4. Signal Extraction (NEW):
       signals = extract_signals(aggregated)
       # Maps AggregatedFacts to SignalExtractions
       # e.g. revenue facts → growth_rate signal with confidence

5. Company Model Population:
       company = build_company_from_signals(candidate, signals, aggregated)
       # Populates Company.metric_sources from source tracking
       # Populates Company.metric_observations from raw sources
       # Populates Company.metric_justifications from signal reasoning

6. Quality Gates (existing, enhanced):
       # Source volume gate now counts RawDataSource objects, not just URLs
       # Provenance validation checks actual source attribution
       # Contradiction detection uses AggregatedFact.contradictions_detected
       # Evidence readiness uses fact verification status

7. Scoring (existing, enhanced):
       # GrowthScorer reads SignalExtraction.signal_confidence
       # Weights scores by data quality
```

---

## 10. Implementation Priority

Ordered by impact (which unblocks the most downstream value) and complexity.

### Phase 1: Foundation (Enables Everything Else)

| Priority | Task | Files | Effort |
|----------|------|-------|--------|
| P0 | Add missing `DataSourceType` enum values | `models.py` | Trivial |
| P0 | Create `src/solstein/adapters/` package with protocols | New | Small |
| P0 | Create `SourceRegistry` | New | Small |
| P0 | Delete infrastructure duplicate modules | `infrastructure/data_loaders/` | Trivial |

### Phase 2: Wrap Existing Modules as Adapters

| Priority | Task | Wraps | Effort |
|----------|------|-------|--------|
| P1 | `StaticCatalogSource` | `discovery._catalog_for_market()` | Small |
| P1 | `YahooFinanceEnrichment` | `company_research.CompanyResearcher` | Medium |
| P1 | `CompetitorJsonSource` | `loaders.CompetitorDataLoader` | Small |
| P2 | `NewsEnrichment` | `additional_sources.get_news()` | Medium |
| P2 | `PatentEnrichment` | `patent_client.search_company_patents()` | Medium |
| P2 | `FundingEnrichment` | `additional_sources.get_funding_data()` | Medium |
| P2 | `LinkedInEnrichment` | `additional_sources.get_linkedin_data()` | Medium |
| P2 | `WebsiteEnrichment` | `additional_sources.scrape_company_website()` | Medium |
| P3 | `WebSearchDiscoverySource` | `web_search_client.search_company_info()` | Medium |
| P3 | `WebSearchNewsEnrichment` | `web_search_client.search_company_news()` | Medium |
| P3 | `GlobalMarketEnrichment` | `fetchers.GlobalMarketLoader` | Medium |

### Phase 3: New Pipeline Stages

| Priority | Task | File | Effort |
|----------|------|------|--------|
| P1 | `DefaultFactAggregator` | `research/aggregate.py` | Large |
| P2 | `extract_signals()` | `research/signals.py` | Large |
| P2 | `build_company_from_signals()` | `research/gather.py` (refactor) | Large |

### Phase 4: Pipeline Integration

| Priority | Task | File | Effort |
|----------|------|------|--------|
| P1 | Refactor `discover_companies()` to iterate adapters | `research/discovery.py` | Medium |
| P1 | Refactor `build_company_profile()` to iterate adapters | `research/gather.py` | Large |
| P2 | Enhance quality gates to use `RawDataSource` counts | `research/pipeline.py` | Medium |
| P3 | Enhance scoring to use `SignalExtraction` confidence | `analytics/scoring.py` | Medium |

---

## 11. Known Issues to Fix During Wiring

These bugs in the dead modules must be fixed when wrapping them as adapters.

### Critical

| Module | Issue | Fix |
|--------|-------|-----|
| `fetchers.py` | Cross-rate formula inverted: `to_usd / from_usd` should be `from_usd / to_usd` | Fix formula in `CurrencyRateFetcher.convert()` |
| `fetchers.py` | Silent `1.0` fallback for missing currency rates | Raise or return `None` instead |
| `patent_client.py` | Patent counts fabricated: Google x5, DDG x3 multipliers | Remove multipliers, report actual counts |
| `patent_client.py` | "patent" listed as AI keyword, inflates all `ai_related_patents` counts | Remove "patent" from AI keyword list |

### High

| Module | Issue | Fix |
|--------|-------|-----|
| `web_search_client.py` | Hardcoded year "2025" in date filter queries | Use `datetime.now().year` |
| `gather.py` | `metric_sources` pre-populated before data fetch (false provenance) | Populate only after successful fetch |
| `gather.py` | `saas_maturity=5` hardcoded for all enriched companies | Derive from actual data or leave `None` |
| `company_research.py` | Overlaps with `gather.py` yfinance usage | Use `CompanyResearcher` as the single yfinance adapter, remove duplication from `gather.py` |
| `additional_sources.py` | Duplicate exists at `infrastructure/data_loaders/` with broken imports | Delete the infrastructure duplicate |

### Medium

| Module | Issue | Fix |
|--------|-------|-----|
| `fetchers.py` | Inconsistent currency pair directions (`EURUSD=X` vs `JPY=X`) | Normalize all to `XXX=USD` or `XXXUSD=X` |
| `gather.py` | Revenue from yfinance marked `CONFIRMED`, growth marked `ESTIMATED` (inconsistent) | Both should be `CONFIRMED` if from same yfinance API call |
| `discovery.py` | Energy catalog substring match too broad (line 35) | Use exact market name matching |
| `discovery.py` | LATAM catalog is silent fallback for ALL unknown markets | Return empty list for unknown markets, or raise |
| `discovery.py` | Stale entries: AutoGrid (acquired 2022), Limejump (acquired 2019) | Remove acquired companies from catalogs |

---

## Appendix: File Locations Quick Reference

```
src/solstein/
├── adapters/                    # NEW — Adapter layer
│   ├── __init__.py
│   ├── protocols.py             # DiscoverySource, EnrichmentSource, FactAggregator
│   ├── registry.py              # SourceRegistry + build_default_registry()
│   ├── discovery/
│   │   ├── static_catalog.py
│   │   ├── web_search.py
│   │   └── competitor_json.py
│   ├── enrichment/
│   │   ├── yahoo_finance.py
│   │   ├── news.py
│   │   ├── funding.py
│   │   ├── patents.py
│   │   ├── linkedin.py
│   │   └── website.py
│   ├── aggregation/
│   │   └── default.py           # DefaultFactAggregator
│   └── signals/
│       └── default.py           # extract_signals(), build_company_from_signals()
├── analytics/
│   └── scoring.py               # MODIFY — accept SignalExtraction confidence
├── data/                        # EXISTING — Raw data source implementations
│   ├── fetchers.py              # FIX currency bugs, wire GlobalMarketLoader
│   ├── web_search_client.py     # FIX hardcoded year
│   ├── additional_sources.py    # Wire all 5 methods as adapters
│   ├── patent_client.py         # FIX fabricated counts
│   ├── company_research.py      # Wire as primary yfinance adapter
│   └── loaders.py               # Wire as CompetitorJsonSource
├── domain/
│   └── models.py                # ADD enum values, models already exist
├── infrastructure/
│   └── data_loaders/            # DELETE duplicates
│       ├── additional_sources.py  # DELETE
│       └── patent_client.py       # DELETE
└── research/
    ├── aggregate.py             # NEW — FactAggregator implementation
    ├── discovery.py             # MODIFY — iterate DiscoverySource adapters
    ├── evidence.py              # MODIFY — use AggregatedFact.is_verified
    ├── gather.py                # MODIFY — iterate EnrichmentSource adapters
    ├── pipeline.py              # MODIFY — wire registry, add aggregation stage
    ├── reconcile.py             # MODIFY — use AggregatedFact.contradictions_detected
    ├── signals.py               # NEW — SignalExtraction logic
    └── sources.py               # Unchanged
```

---

## Appendix B: Phase 1 Implementation Log

> Implemented: 2026-02-24

### What Was Done

**1. DataSourceType enum extended** (`src/solstein/domain/models.py`)
- Added 8 new values: `YAHOO_FINANCE`, `EXA_SEARCH`, `GOOGLE_SEARCH`, `USPTO`, `GOOGLE_PATENTS`, `NEWSAPI`, `COMPETITOR_JSON`, `STATIC_CATALOG`
- Total enum values: 16 (was 8)

**2. Adapter package created** (`src/solstein/adapters/`)
- `protocols.py` — `DiscoverySource`, `EnrichmentSource`, `FactAggregator` as `@runtime_checkable` Protocol classes
- `registry.py` — `SourceRegistry` dataclass + `build_default_registry(settings)` factory
- `discovery/static_catalog.py` — wraps `_catalog_for_market()` as a `DiscoverySource`
- `discovery/competitor_json.py` — wraps `CompetitorDataLoader` as a `DiscoverySource`
- Sub-packages created (empty `__init__.py`): `discovery/`, `enrichment/`, `aggregation/`, `signals/`

**3. Config updated** (`src/solstein/config.py`)
- Added `exa_api_key` and `crunchbase_api_key` fields to `Settings` class
- These join existing `news_api_key` and `patentsview_api_key` for conditional adapter registration

**4. Infrastructure duplicates deleted**
- Removed `src/solstein/infrastructure/data_loaders/additional_sources.py` (httpx duplicate with broken imports)
- Removed `src/solstein/infrastructure/data_loaders/patent_client.py` (lxml duplicate with broken imports)
- Removed `src/solstein/infrastructure/data_loaders/` directory (now empty)

### Verification

All components verified via import tests:
- Protocol imports: OK
- Registry construction: OK — `build_default_registry()` returns 2 discovery sources, 0 enrichment sources
- Protocol conformance: OK — both `StaticCatalogSource` and `CompetitorJsonSource` pass `isinstance()` checks against `DiscoverySource`
- Functional test: `StaticCatalogSource.discover()` returns candidates for energy and LATAM markets
- DataSourceType enum: 16 values confirmed

### What Remains (Phase 3+)

- Create `DefaultFactAggregator` in `aggregation/default.py`
- Create signal extraction in `signals/default.py`
- Refactor `discover_companies()` to iterate registry adapters
- Refactor `build_company_profile()` to iterate registry adapters
- Wire registry into `run_market_intelligence()`

---

## Appendix C: Phase 2 Implementation Log

> Implemented: 2026-02-24

### Bug Fixes Applied

| Module | Bug | Fix |
|--------|-----|-----|
| `web_search_client.py` | Hardcoded year "2025" in 3 locations | Replaced with `_current_year()` using `datetime.now().year` |
| `patent_client.py` | Fabricated patent counts: Google x5, DuckDuckGo x3 | Changed to `len(results)` — report actual counts |
| `patent_client.py` | "patent" listed as AI keyword inflating `ai_related_patents` | Removed "patent" from AI keyword lists in both backends |
| `fetchers.py` | Cross-rate formula inverted: `to_usd / from_usd` | Fixed to `from_usd / to_usd` |
| `fetchers.py` | Silent `1.0` fallback for missing rates masked errors | Changed to `None` fallback (uses `.get()` without default) |

### Enrichment Adapters Created (8 total)

| Adapter | File | Wraps | DataSourceType | Requires Key? |
|---------|------|-------|---------------|--------------|
| `YahooFinanceEnrichment` | `enrichment/yahoo_finance.py` | `CompanyResearcher.research()` | `YAHOO_FINANCE` | No (needs ticker) |
| `NewsEnrichment` | `enrichment/news.py` | `AdditionalDataSources.get_news()` | `NEWSAPI` / `NEWS` | Optional (`news_api_key`) |
| `FundingEnrichment` | `enrichment/funding.py` | `AdditionalDataSources.get_funding_data()` | `CRUNCHBASE` | Optional (`crunchbase_api_key`) |
| `PatentEnrichment` | `enrichment/patents.py` | `search_company_patents()` | `USPTO` / `GOOGLE_PATENTS` | No |
| `LinkedInEnrichment` | `enrichment/linkedin.py` | `AdditionalDataSources.get_linkedin_data()` | `LINKEDIN` | No |
| `WebsiteEnrichment` | `enrichment/website.py` | `AdditionalDataSources.scrape_company_website()` | `WEBSITE` | No (needs URL) |
| `WebSearchNewsEnrichment` | `enrichment/web_search_news.py` | `search_company_news()` | `EXA_SEARCH` | Optional (`exa_api_key`) |
| `GlobalMarketEnrichment` | `enrichment/global_market.py` | `GlobalMarketLoader.get_stock_data()` | `YAHOO_FINANCE` | No (needs ticker) |

### Discovery Adapters Created (1 new, 2 from Phase 1)

| Adapter | File | Wraps | Requires Key? |
|---------|------|-------|--------------|
| `WebSearchDiscoverySource` | `discovery/web_search.py` | `search_company_info()` | Optional (`exa_api_key`) |

### Registry Updated

`build_default_registry(settings)` now registers:
- **Always available (no API keys):** StaticCatalog, CompetitorJson, YahooFinance, Patents, LinkedIn, Website, GlobalMarket
- **Conditional on `news_api_key`:** NewsEnrichment
- **Conditional on `crunchbase_api_key`:** FundingEnrichment
- **Conditional on `exa_api_key`:** WebSearchDiscovery, WebSearchNewsEnrichment

Default configuration (no keys): **2 discovery + 5 enrichment** sources.
All keys configured: **3 discovery + 8 enrichment** sources.

### Verification

- All 11 adapters (3 discovery + 8 enrichment) pass `isinstance()` checks against their protocols
- 222 existing tests pass with zero regressions
- Registry builds correctly with conditional adapter registration

### Config Changes

Added to `Settings` class in `config.py`:
- `exa_api_key: str | None` (Phase 1)
- `crunchbase_api_key: str | None` (Phase 1)

### What Remains (Phase 3+)

- Create `DefaultFactAggregator` in `aggregation/default.py` ✅ Done (Phase 3)
- Create signal extraction in `signals/default.py` ✅ Done (Phase 3)
- Refactor `discover_companies()` to iterate registry adapters instead of hardcoded catalog
- Refactor `build_company_profile()` to iterate registry enrichment adapters
- Wire registry into `run_market_intelligence()`
- Enhance quality gates to use `RawDataSource` counts
- Enhance scoring to use `SignalExtraction` confidence

---

## Appendix D: Phase 3 Implementation Log (2026-02-24)

**Objective:** Create the three new pipeline stages: fact aggregation, signal extraction, and signal-based Company construction.

### Files Created

| File | Purpose | Size |
|------|---------|------|
| `src/solstein/research/aggregate.py` | `DefaultFactAggregator` — cross-references `RawDataRecord` into `AggregatedDataRecord` | ~470 lines |
| `src/solstein/research/signals.py` | `extract_signals()` — maps `AggregatedFact` to `SignalExtraction` objects | ~425 lines |

### Files Modified

| File | Change |
|------|--------|
| `src/solstein/research/gather.py` | Added `build_company_from_signals()` + helper functions (~300 lines added) |

### DefaultFactAggregator (`research/aggregate.py`)

Implements the `FactAggregator` protocol. Core algorithm:

1. **Per-source-type extractors** — Dedicated extractor for each `DataSourceType` that maps raw_content dict keys to normalized `(fact_type, value)` tuples:
   - `_extract_yahoo_finance()`: Handles both `CompanyResearch.model_dump()` (nested `financials.revenue`) and `GlobalMarketEnrichment` (top-level `revenue`) structures
   - `_extract_news()`: Maps `PressCoverage` fields (sentiment_score, article counts)
   - `_extract_crunchbase()`: Maps `FundingData` fields (total_raised → total_funding_raised)
   - `_extract_patents()`: Maps `PatentResult` fields
   - `_extract_linkedin()`: Maps `LinkedInData` fields
   - `_extract_website()`: Maps `ProductInfo` fields

2. **Fact grouping** — All observations for the same `fact_type` from different sources are grouped together

3. **Numeric aggregation** — For numeric facts (revenue, employee_count, etc.):
   - Best value: from highest-confidence source
   - Agreement: fraction of sources within 10% of best value
   - Contradiction detection: sources diverging >25% flagged with details
   - Confidence: base confidence penalized by 15% per contradiction

4. **Non-numeric aggregation** — For strings and lists:
   - Best value: from highest-confidence source
   - Agreement: exact match ratio

5. **Data completeness** — Computed against 10 desired fact types: revenue, employee_count, market_cap, profit_margin, revenue_growth, total_patents, total_funding_raised, description, industry, headquarters

### extract_signals() (`research/signals.py`)

10 signal extractors, each mapping one or more fact types to a business signal:

| Signal | Source Facts | Method | Purpose |
|--------|-------------|--------|---------|
| `revenue_level` | revenue | direct | Core financial metric |
| `growth_rate` | revenue_growth | direct | Growth scoring |
| `profitability` | profit_margin | direct | Financial health |
| `company_size` | employee_count, market_cap | composite | Tier classification |
| `valuation` | market_cap, valuation | direct | Tier classification |
| `innovation` | total_patents, ai_related_patents | direct | R&D strength |
| `ai_maturity` | ai_score, ai_signal_strength, ai_related_positions | composite | Threat assessment |
| `hiring_velocity` | employee_growth_pct, open_positions | composite | Growth trajectory |
| `market_sentiment` | sentiment_score, article_count | direct | Brand perception |
| `funding` | total_funding_raised, funding_rounds, last_round_stage | direct | Runway / investor confidence |

Each signal includes:
- `signal_confidence`: inherited from aggregated fact, used downstream by scoring
- `reasoning`: human-readable explanation of the signal value and sources
- `calculation_method` and `calculation_formula`: audit trail for how the signal was derived

### build_company_from_signals() (`research/gather.py`)

Replaces the direct-yfinance approach with signal-based Company construction:

**Key improvements over `build_company_profile()`:**
- **Provenance populated AFTER data fetch** — `metric_sources` built from actual `AggregatedFact.sources_used`, not pre-assumed URLs
- **Multi-source metric_observations** — Each metric observation includes the actual value and source URL/name
- **Signal-derived justifications** — `metric_justifications` populated from signal `reasoning` (human-readable)
- **Confidence levels derived from data quality** — `ConfidenceLevel` mapped from signal confidence (≥0.7 → CONFIRMED, ≥0.4 → ESTIMATED, else UNKNOWN)
- **AI maturity from actual assessment** — Uses `ai_score` to derive `AIMaturity` enum instead of keyword-matching description text
- **No hardcoded `saas_maturity=5`** — Left as default (1) when no data available

Helper functions added:
- `_confidence_from_signal()` — Maps 0-1 float to ConfidenceLevel
- `_ai_maturity_from_score()` — Maps 0-10 AI score to AIMaturity enum
- `_build_metric_sources()` — Builds metric→source URL mapping from facts
- `_build_metric_observations()` — Builds metric→observation list from facts
- `_build_metric_justifications()` — Builds metric→justification from signals

### Protocol Conformance

- `DefaultFactAggregator` passes `isinstance(agg, FactAggregator)` check
- End-to-end test with 5 synthetic sources → 30 aggregated facts → 9 signals → Company with fully populated provenance fields

### Verification

- All Phase 3 modules import cleanly
- 244 existing tests pass with zero regressions (14 pre-existing async failures unrelated)
- End-to-end pipeline test: `RawDataSource[]` → `DefaultFactAggregator` → `extract_signals()` → `build_company_from_signals()` produces correct `Company` with verified fields

### Design Decisions

1. **Placed in `research/` not `adapters/`** — The aggregator and signal modules are pipeline stages, not adapter wrappers. They belong alongside `discovery.py`, `gather.py`, and `pipeline.py` in the research package.

2. **Backward compatible** — `build_company_profile()` left intact. `build_company_from_signals()` is additive. Phase 4 will swap the call site in `pipeline.py`.

3. **Flat extraction, no inheritance** — Per-source-type extractors are plain functions, not subclasses. This avoids over-abstraction for what is essentially a dict key mapping.

4. **Contradiction threshold separation** — 10% for agreement, 25% for contradiction. Values between 10-25% are "soft disagreement" (not flagged as contradiction, but reduce agreement percentage).

### What Remains (Phase 4: Pipeline Integration)

- ~~Refactor `discover_companies()` to iterate `DiscoverySource` adapters from registry~~ ✅
- ~~Refactor `build_company_profile()` call site in `pipeline.py` to use enrichment loop + `build_company_from_signals()`~~ ✅
- ~~Wire `SourceRegistry` into `run_market_intelligence()` (build once, pass through)~~ ✅
- Enhance quality gates to use `RawDataSource` counts per company (P3 — future)
- Enhance scoring to weight by `SignalExtraction.signal_confidence` (P3 — future)

---

## Appendix E — Phase 4 Implementation Log

**Committed:** Phase 4 — Pipeline integration

### discover_companies() Refactoring (`research/discovery.py`)

Added registry-aware discovery path alongside preserved legacy path:

- **New parameter:** `registry: SourceRegistry | None = None` (optional, backward-compatible)
- **`_discover_via_registry()`** — Iterates `registry.discovery_sources`, calls `discover()` on each adapter, deduplicates by `company_id`, applies relevance scoring
- **`_discover_legacy()`** — Original hardcoded static catalog + competitor JSON logic (preserved intact)
- **`_score_candidate()`** — Computes relevance score based on market/industry/keyword overlap
- **`_deduplicate_candidates()`** — Keeps highest-scored candidate per `company_id`
- Routing: if `registry` is provided → `_discover_via_registry()`, else → `_discover_legacy()`

### enrich_company() (`research/gather.py`)

New function replacing `build_company_profile()` as the pipeline's enrichment entry point:

```
enrich_company(candidate, registry, batch_id) → Company
```

Flow:
1. Iterates `registry.enrichment_sources`, calls `enrich()` on each adapter
2. Collects `RawDataSource` results into `RawDataRecord`
3. Passes to `DefaultFactAggregator.aggregate()` → `AggregatedDataRecord`
4. Passes to `extract_signals()` → `SignalExtractionRecord`
5. Passes to `build_company_from_signals()` → `Company`
6. Falls back to `build_company_profile(candidate)` if all enrichment sources fail

### run_market_intelligence() Refactoring (`research/pipeline.py`)

Key changes:
- **Registry construction:** Builds `SourceRegistry` via `build_default_registry(Settings.load())` at function start
- **Batch ID:** Generates `uuid.uuid4().hex[:12]` batch ID per pipeline run
- **Discovery:** Passes `registry=registry` to `discover_companies()` (adapter-driven discovery)
- **Enrichment:** Replaced `build_company_profile(candidate)` with `enrich_company(candidate, registry, batch_id)` (multi-source aggregation)
- **Pipeline version:** Updated from `research.v1` to `research.v2` in dual-write stable run ID
- **Lazy import:** `build_default_registry` imported inside function body to avoid circular dependency (pipeline → adapters → protocols → research → pipeline)

### Test Updates (`tests/unit/test_research_pipeline.py`)

Updated 3 tests that monkeypatched `build_company_profile`:
- Monkeypatch target changed from `research_pipeline.build_company_profile` to `research_pipeline.enrich_company`
- Fake function signatures updated to accept `(candidate, registry, batch_id)` instead of just `(candidate)`
- Registry builds normally from Settings (no mocking needed for registry)

### Verification

- All 7 pipeline tests pass (7/7)
- 295 existing unit tests pass with zero regressions
- Pre-existing failures unchanged (async tests, langgraph dependency, supabase client)

### Circular Import Resolution

The import chain `pipeline.py → adapters.registry → adapters.__init__ → adapters.protocols → research.discovery → research.__init__ → pipeline.py` created a circular dependency. Resolved by making the `build_default_registry` import lazy (inside `run_market_intelligence()` function body instead of module level).

### What Remains (Phases 5–7)

See below.

---

## Phase 5 — Confidence-Weighted Scoring

**Status:** Implemented ✅

**Goal:** `GrowthScorer.calculate_scores()` currently reads Company fields directly with no awareness of how confident we are in each value. This phase multiplies raw scores by `SignalExtraction.signal_confidence` so that low-confidence data points contribute less to the final score.

### Implementation

#### Model changes (`domain/models.py`)

- **`Company.signal_confidences: dict[str, float]`** — Maps signal names to 0-1 confidence values. Populated during `build_company_from_signals()`. Default empty dict preserves backward compatibility for legacy Company objects.
- **`ScoreComponent.confidence_weight: float = 1.0`** — Records the confidence multiplier applied to each scoring component. Visible in the scoring breakdown for dashboards/audit.

#### Signal propagation (`research/gather.py`)

`build_company_from_signals()` now populates `signal_confidences` from the `SignalExtractionRecord`:
```python
signal_confidences={s.signal_name: s.signal_confidence for s in signal_record.signals}
```

This preserves the original 0-1 float values (previously lost when converting to the coarse CONFIRMED/ESTIMATED/UNKNOWN enum).

#### Confidence-weighting engine (`analytics/scoring.py`)

Three new module-level constructs:

1. **`_COMPONENT_SIGNAL_MAP`** — Maps each ScoreComponent name to the signal(s) that inform it:

| Component | Signals |
|-----------|---------|
| Revenue Growth | growth_rate |
| Employee Efficiency | revenue_level, company_size |
| Funding Momentum | funding |
| Profitability Profile | profitability |
| Revenue Scale | revenue_level |
| Profitability Health | profitability |
| Operating Efficiency | revenue_level, company_size |
| Funding Cushion | funding, revenue_level |
| Market Tier | company_size, valuation |
| AI Maturity | ai_maturity |
| SaaS Maturity | _(none — weight 1.0)_ |
| Geographic Footprint | _(none — weight 1.0)_ |
| Stack Diversity | _(none — weight 1.0)_ |

2. **`_confidence_weight(component_name, signal_confidences)`** — Returns the average confidence of mapped signals (or 1.0 if no signals mapped).

3. **`_apply_confidence_weights(explanation, signal_confidences)`** — Post-processes a `ScoringExplanation`: multiplies each component's value by its confidence weight, records the weight on `component.confidence_weight`, and recalculates `final_score`.

#### Scoring integration

`GrowthScorer.calculate_scores()` applies `_apply_confidence_weights()` after all three sub-scorers return, **only when `profile.signal_confidences` is non-empty**. This means:
- Sub-scorer interfaces unchanged (no signature changes)
- All existing sub-scorer unit tests pass without modification
- Legacy Company objects (no signal_confidences) score identically to before

### Design Decisions

1. **Post-processing, not inline** — Confidence weighting happens after sub-scorers return, not inside them. Sub-scorer interfaces stay unchanged.
2. **Multiplicative** — `adjusted_value = raw_value × confidence`. Full confidence (1.0) = no change.
3. **Base score unaffected** — Only component adjustments are weighted, not the base score (5.0).
4. **Graceful fallback** — Empty `signal_confidences` → weight=1.0 on all components.
5. **Average confidence for multi-signal components** — Components like "Employee Efficiency" that depend on both revenue and employee count use the average confidence of both signals.

### Verification

- 121 tests pass (34 scoring + 22 growth + 21 financial + 21 competitive + 7 pipeline + 16 coverage)
- 5 new confidence-weighting tests:
  - `test_confidence_weighting_full_confidence_matches_unweighted` — 1.0 confidence = same scores
  - `test_confidence_weighting_half_confidence_reduces_scores` — 0.5 confidence = lower scores
  - `test_confidence_weighting_no_confidences_unchanged` — empty dict = legacy behavior
  - `test_confidence_weight_populates_score_components` — confidence_weight visible in breakdown
  - `test_confidence_weighting_scores_still_clamped` — scores remain in [0, 10]

---

## Phase 6 — Per-Company Source Volume Gates

**Status:** Implemented ✅

**Goal:** The current source volume gate in `run_market_intelligence()` checks *total* unique sources across all companies. This is too coarse — a single well-sourced company can mask several companies with zero enrichment data. This phase adds per-company minimum source requirements.

**Scope:**
- Track `RawDataSource` count per company during enrichment (available from `RawDataRecord.sources`)
- Add a per-company minimum source threshold parameter to `run_market_intelligence()`
- Companies below the threshold are either flagged in the stage report or excluded from scoring
- Update the `gather` stage report to include per-company source counts
- Add a "data quality" tier to the output: "well-sourced" (≥N sources), "partial" (1–N), "stub" (0 real sources, fallback only)

**Key files:**
- `src/solstein/research/pipeline.py` — new gate logic after enrichment
- `src/solstein/research/gather.py` — `enrich_company()` already has `RawDataRecord`; needs to surface source count
- `src/solstein/domain/models.py` — may add `enrichment_source_count` or `data_quality_tier` to Company

**Risks:**
- Strict per-company gates may reduce the candidate set too aggressively in markets with sparse data
- Need a sensible default threshold that doesn't break existing runs

### Phase 6 Implementation Log

**Changes:**

1. **`src/solstein/domain/models.py`** — Added `enrichment_source_count: int = 0` and `data_quality_tier: str = "unknown"` fields to Company. Default values ensure backward compatibility with existing Company objects.

2. **`src/solstein/research/gather.py`** — Added `_data_quality_tier()` helper with thresholds: ≥3 sources → "well-sourced", 1–2 → "partial", 0 → "stub". `enrich_company()` now populates both fields after enrichment. Fallback path (no enrichment sources succeeded) sets count=0, tier="stub".

3. **`src/solstein/research/pipeline.py`** — Added `min_sources_per_company: int | None = None` parameter. Gather stage report now includes `data_quality_breakdown` (counts per tier) and `per_company_sources` (per-company detail). New `per_company_source_gate` stage filters companies below threshold, logs filtered count, and raises `RuntimeError` if all companies removed.

4. **`tests/unit/test_research_pipeline.py`** — Added 4 tests:
   - `test_data_quality_tier_classification` — verifies tier thresholds
   - `test_per_company_source_gate_filters_low_source_companies` — mixed sources, some filtered
   - `test_per_company_source_gate_removes_all_raises` — all below threshold → RuntimeError
   - `test_gather_stage_reports_source_quality_breakdown` — gather stage includes quality breakdown

**Test results:** 11 pipeline tests pass, 98 scoring tests pass (no regressions).

**Design decisions:**
- Gate parameter is `None` by default → no filtering on existing runs (backward compat)
- Tier thresholds are module-level constants (`_WELL_SOURCED_MIN = 3`, `_PARTIAL_MIN = 1`) for easy tuning
- Gate filtering produces a stage report entry with filtered company details before removing them

---

## Phase 7 — Integration Tests with Real Adapters (Fully Validated Runs)

**Status:** Planned

**Goal:** End-to-end tests exercising the full adapter → aggregate → signal → Company flow with **real** adapters (not mocked). Produces a full audit report document in markdown format as a reference artifact proving the pipeline works against live data sources.

**Scope:**
- Create integration test suite that runs the complete pipeline against a known seed company/market
- Each adapter is called with real credentials (tests gated on API key availability via `pytest.mark.skipif`)
- Validate the full chain: discovery adapters produce candidates → enrichment adapters return `RawDataSource` → aggregation cross-references → signals extracted → Company built with real provenance
- Generate a **markdown audit report** per run containing:
  - Run metadata (seed company, market, timestamp, batch_id)
  - Per-adapter results: which adapters succeeded/failed, response times, data shapes
  - Aggregation summary: fact count, agreement percentages, contradictions detected
  - Signal extraction summary: which signals were produced, confidence levels
  - Per-company data quality: source count, completeness percentage, confidence breakdown
  - Final scored output with provenance chain for each metric
- Store the audit report as a dated artifact (e.g., `docs/audit/run_YYYY-MM-DD_<market>.md`)

**Key files:**
- `tests/integration/test_full_pipeline.py` — new integration test file
- `src/solstein/research/pipeline.py` — may need a "report mode" flag or hook to emit the audit report
- `docs/audit/` — output directory for generated audit reports

**Prerequisites:**
- Phase 5 (confidence-weighted scoring) should ideally land first so the audit report includes confidence data
- API keys for at least Yahoo Finance + one additional source must be configured in the test environment

**Audit report template:**

```markdown
# Pipeline Audit Report — {market}

**Seed company:** {seed}
**Date:** {timestamp}
**Batch ID:** {batch_id}
**Pipeline version:** research.v2

## Discovery
- Adapters called: {list}
- Candidates discovered: {count}
- Deduplicated to: {count}

## Enrichment
| Company | Sources Attempted | Sources Succeeded | Facts Extracted | Completeness |
|---------|-------------------|-------------------|-----------------|--------------|
| ...     | ...               | ...               | ...             | ...          |

## Aggregation Quality
| Company | Total Facts | Avg Agreement | Contradictions | Confidence |
|---------|-------------|---------------|----------------|------------|
| ...     | ...         | ...           | ...            | ...        |

## Signal Extraction
| Company | Signals Produced | Avg Confidence | Missing Signals |
|---------|------------------|----------------|-----------------|
| ...     | ...              | ...            | ...             |

## Scoring
| Company | Raw Score | Confidence-Weighted Score | Data Quality Tier |
|---------|-----------|---------------------------|-------------------|
| ...     | ...       | ...                       | ...               |

## Adapter Health
| Adapter | Status | Response Time | Error (if any) |
|---------|--------|---------------|----------------|
| ...     | ...    | ...           | ...            |
```

**Risks:**
- Integration tests with real APIs are slow, flaky, and cost money — must be clearly gated and not run in CI by default
- API rate limits may cause intermittent failures
- Audit report format may need iteration based on what's actually useful for review
