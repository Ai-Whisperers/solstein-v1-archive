# Provider Scorecard and Enforcement Matrix

> STORY-263 | EPIC-069: Provider Surface Rationalization
> Generated: 2026-03-31 | Evidence-backed inventory for adapter consolidation

This scorecard records every provider adapter in the codebase, its status,
quality, and the rules governing changes during consolidation. Downstream
stories (STORY-264, STORY-265, STORY-266) cite this document.

---

## 1. Adapter Inventory

### Enrichment Adapters (Feature-Flag Gated)

The `feature_new_unified_loader` flag in `adapters/registry.py:94-144`
controls whether legacy or unified adapters are registered.

| Data Source | Legacy File (LOC) | Unified File (LOC) | API | Async | Confidence |
|-------------|-------------------|-------------------|-----|-------|------------|
| Funding | `funding.py` (57) | `funding_unified.py` (266) | Crunchbase / News fallback | No / Yes | 0.7 / 0.65 |
| LinkedIn | `linkedin.py` (53) | `linkedin_unified.py` (160) | NewsAPI (proxy) | No / Yes | 0.3 / 0.60 |
| News | `news.py` (55) | `news_unified.py` (306) | NewsAPI.org / Web search | No / Yes | 0.6 / 0.70 |
| Patents | `patents.py` (71) | `patents_unified.py` (202) | USPTO / Google Patents / DDG | No / Yes | 0.7 / 0.80 |
| Web Search | `web_search_news.py` (47) | `web_search_unified.py` (308) | Exa / Google Search | No / Yes | 0.5 / 0.70 |
| Website | `website.py` (53) | `website_unified.py` (281) | HTTP scraping | No / Yes | 0.5 / 0.70 |
| **Totals** | **336 LOC** | **1523 LOC** | | | |

All files under `src/solstein/adapters/enrichment/`.

### Always-Available Enrichment Adapters

| Adapter | File (LOC) | API | Async | Confidence |
|---------|-----------|-----|-------|------------|
| Yahoo Finance | `yahoo_finance.py` (53) | yfinance SDK | No | 0.8 |
| Global Market | `global_market.py` (69) | yfinance SDK (wrapper) | No | 0.8 |

### Discovery Adapters

| Adapter | File (LOC) | Source | API Key |
|---------|-----------|--------|---------|
| Static Catalog | `discovery/static_catalog.py` (102) | Hardcoded lists | None |
| Competitor JSON | `discovery/competitor_json.py` (115) | File I/O | None |
| Web Search | `discovery/web_search.py` (65) | Exa API | `exa_api_key` |

All files under `src/solstein/adapters/discovery/`.

---

## 2. Quality Matrix

### Error Handling

| Tier | Adapters | Pattern |
|------|----------|---------|
| Excellent | All 6 unified | `log_adapter_error()` + type-specific catches |
| Good | 3 discovery adapters | `log_adapter_error()` + generic catch |
| Fair | All 6 legacy | Delegate to `AdditionalDataSources` wrapper |
| Fair | Yahoo Finance, Global Market | Basic ValueError / None return |

Structured logging infrastructure: `adapters/logging.py` (42 LOC) with
`log_adapter_error()` providing component, operation, error_type, entity_id.

### Test Coverage

| Category | Unit Tests | Integration Tests | Coverage |
|----------|-----------|------------------|----------|
| Legacy enrichment (6) | 3/6 | Via integration | 50% |
| Unified enrichment (6) | 0 (by design) | 6/6 | 100% |
| Discovery (3) | 0 | Partial | 33% |
| Registry | Full | Full | 100% |

Key test files:

- `tests/unit/test_adapters_enrichment.py` (105 LOC) -- legacy adapters
- `tests/unit/test_adapter_registry.py` (143 LOC) -- registry logic
- `tests/integration/test_unified_adapters.py` (352 LOC) -- all unified

### HTTP Client Usage

| Client | Adapters | Status |
|--------|----------|--------|
| httpx | Unified (funding, news, website) | Preferred (STORY-134) |
| yfinance SDK | Yahoo Finance, Global Market | Acceptable (SDK) |
| requests (via wrappers) | Legacy adapters | Deprecated (EPIC-035) |

---

## 3. API Key Dependencies

| Key | Config Field | Adapters | Optional |
|-----|-------------|----------|----------|
| Crunchbase | `crunchbase_api_key` | Funding (L+U) | Yes (fallback to news) |
| NewsAPI.org | `news_api_key` | News (L+U), LinkedIn (L+U) | Yes (fallback) |
| Exa Search | `exa_api_key` | Web Search Discovery, Web Search (L+U) | Yes (fallback to Google) |
| Google | `google_api_key` | Web Search (fallback) | Yes |
| Companies House | `companies_house_api_key` | Companies House connector | Yes |
| PatentsView | `patentsview_api_key` | Patents (L+U) | Yes |

---

## 4. Enforcement Matrix

### Rules During Consolidation (EPIC-069)

| Rule | Scope | Enforcement |
|------|-------|-------------|
| **No new adapters** | All of `adapters/` | PR review; cite STORY-266 |
| **No new compatibility wrappers** | All of `adapters/` | PR review; cite STORY-266 |
| **No new feature flags** | `registry.py`, `feature_flags.py` | PR review; cite STORY-256 |
| **Bug fixes only on legacy** | Legacy 6 adapters | PR review; cite ADR-009 |
| **Unified is the target** | New enrichment work | Targets unified adapters only |
| **httpx required** | New HTTP calls | No new `requests` usage (EPIC-035) |
| **Structured logging required** | New error handling | Must use `log_adapter_error()` |

### Collapse Candidates (for STORY-265)

Once the `feature_new_unified_loader` flag is permanently enabled:

| Legacy File | Unified Replacement | Delta LOC | Action |
|-------------|-------------------|-----------|--------|
| `funding.py` (57) | `funding_unified.py` (266) | +209 | Delete legacy, keep unified |
| `linkedin.py` (53) | `linkedin_unified.py` (160) | +107 | Delete legacy, keep unified |
| `news.py` (55) | `news_unified.py` (306) | +251 | Delete legacy, keep unified |
| `patents.py` (71) | `patents_unified.py` (202) | +131 | Delete legacy, keep unified |
| `web_search_news.py` (47) | `web_search_unified.py` (308) | +261 | Delete legacy, keep unified |
| `website.py` (53) | `website_unified.py` (281) | +228 | Delete legacy, keep unified |
| **Total deletable** | | **336 LOC** | Remove 6 files |

### Duplicate Overlap (for STORY-265)

| Pair | Overlap | Resolution |
|------|---------|------------|
| Yahoo Finance + Global Market | Both use yfinance, Global wraps Yahoo | Consider merging into one |
| `data/enrichment/orchestrator.py` + `application/enrichment_pipeline.py` | Both fan-out to adapters in parallel | Deduplicate (see runtime ledger) |

---

## 5. Provider Ownership

| Provider | Owner Module | Authority Enum | Conflict Resolution |
|----------|-------------|---------------|-------------------|
| Crunchbase | `funding_unified` | `FUNDING` | Highest for funding data |
| NewsAPI | `news_unified` | `NEWS_API` | Highest for press coverage |
| LinkedIn (proxy) | `linkedin_unified` | `LINKEDIN` | Lowest (news-derived) |
| USPTO/Patents | `patents_unified` | `PATENTS` (0.85) | Highest for IP data |
| Exa/Google Search | `web_search_unified` | `WEB_SEARCH` | Mid-tier for discovery |
| Website scraping | `website_unified` | `WEBSITE` | Mid-tier for tech stack |
| Yahoo Finance | `yahoo_finance` | `YAHOO_FINANCE` | Highest for market data |

Authority levels drive conflict resolution in the unified loader when
multiple sources report different values for the same field.

---

## 6. Dependency Map for Downstream Stories

```
STORY-263 (this scorecard)
    |
    +-> STORY-265: Collapse duplicate adapter pairs (delete legacy 6)
    |
    +-> STORY-264: Remove replaceable providers from canonical runtime
    |       (also depends on EPIC-067 canonical-runtime decision)
    |
    +-> STORY-266: Ban new compatibility patches at provider boundaries
```

Each downstream story MUST cite specific sections of this scorecard when
justifying collapse, removal, or ban actions.
