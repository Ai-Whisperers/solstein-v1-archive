# Solstein Enrichment Pipeline Improvement Plan

## TL;DR

> **Goal**: Fix the enrichment pipeline so 33+ companies get differentiated scores instead of default 4.67, and enable discovery of new companies beyond the current database.
>
> **Current State**: All 33 companies score 4.67 (base 5.0/5.0/4.0) because enrichment adapters are disabled (no API keys) or fail (no ticker symbols). Raw JSON lacks rich signals.
>
> **Solution**: 4-phase improvement: (1) Configure API keys & infrastructure, (2) Enrich existing companies with tickers, (3) Add new discovery sources, (4) Build monitoring & validation
>
> **Deliverables**:
> - API key configuration for 4 data sources
> - Ticker symbols for 25+ private companies in catalog
> - 2 new discovery adapters (SEC EDGAR, Companies House)
> - Enrichment health monitoring & alerting
> - Data quality validation gates
>
> **Estimated Effort**: Large (12-15 tasks across 4 waves)
> **Parallel Execution**: YES - 4 waves, 3-4 tasks per wave
> **Critical Path**: Wave 1 (API keys) → Wave 2 (Tickers) → Wave 3 (Adapters) → Wave 4 (Validation)

---

## Context

### Original Request
Fix the company discovery, enrichment, and automated gathering system. Currently 33 companies all got default scores (5.0/5.0/4.0 = 4.67) because raw JSON lacks rich signals. Need to understand how to automatically discover and enrich MORE companies beyond the database.

### Architecture Analysis
**Discovery Sources (3 total):**
- `StaticCatalogSource` - Hardcoded catalog with ~44 companies (Energy: 23, LATAM: 21)
- `CompetitorJsonSource` - Reads `competitor_data.json` (5900+ lines of rich data)
- `WebSearchDiscoverySource` - Exa API search (requires EXA_API_KEY)

**Enrichment Adapters (15 total):**
- Always available: Yahoo Finance (needs ticker), Patents, Website, LinkedIn, Global Market
- Requires API keys: News (NEWS_API_KEY), Funding (CRUNCHBASE_API_KEY)
- Unified adapters: 6 additional adapters with refresh support

**Pipeline Flow:**
```
Discovery → Gather/Enrich → Aggregate → Signals → Score → Analyze → Export
```

**Root Cause of Default Scores:**
- 60% of catalog companies lack ticker symbols → Yahoo Finance fails
- No API keys configured → News, Funding, Web Search adapters disabled
- Fallback to `build_company_profile()` returns stub data with base scores

### Metis Review
**Identified Gaps (addressed in this plan):**

1. **Ticker Acquisition Strategy**: 25+ private companies in catalog have no tickers. Need fallback enrichment path.
2. **Data Quality Acceptance Criteria**: Define measurable success (70% coverage, score distribution targets)
3. **API Budget & Rate Limiting**: NewsAPI free tier = 100 requests/day. Need quota management.
4. **Monitoring & Alerting**: No adapter health metrics. Need success/failure tracking.
5. **Duplicate Detection**: Companies appear under different names across sources ("Octopus" vs "Kraken")
6. **Data Freshness**: No timestamp validation on cached enrichment results

---

## Work Objectives

### Core Objective
Enable differentiated company scoring by fixing the enrichment pipeline and expanding discovery capabilities beyond the current 33 companies.

### Concrete Deliverables
1. **API Key Infrastructure** (Wave 1)
   - `.env` configuration for NEWS_API_KEY, CRUNCHBASE_API_KEY, EXA_API_KEY
   - Environment validation script
   - API quota tracking & rate limiting

2. **Ticker Enrichment** (Wave 2)
   - Add ticker symbols to 25+ catalog companies
   - Implement ticker lookup service for private companies
   - Fallback enrichment path when no ticker available

3. **New Discovery Adapters** (Wave 3)
   - SEC EDGAR discovery adapter (US public companies)
   - Companies House discovery adapter (UK companies)
   - Duplicate detection with fuzzy matching

4. **Monitoring & Validation** (Wave 4)
   - Enrichment health dashboard
   - Data quality gates (min 2 sources per company)
   - Adapter success/failure metrics
   - Score distribution validation

### Definition of Done
```bash
# Verification commands
python -c "from solstein.adapters.registry import build_default_registry; r = build_default_registry(); print(f'Discovery: {len(r.discovery_sources)}, Enrichment: {len(r.enrichment_sources)}')"
# Expected: Discovery: 4+, Enrichment: 10+

python scripts/validate_enrichment.py
# Expected: >70% companies have ≥2 data sources, score distribution not 100% at 4.67
```

### Must Have
- [ ] API keys configured and validated at startup
- [ ] 25+ companies have ticker symbols or alternative enrichment
- [ ] 2+ new discovery adapters implemented
- [ ] Enrichment health monitoring in place
- [ ] Data quality gates (min 2 sources per company)
- [ ] Score distribution validation (not all 4.67)

### Must NOT Have (Guardrails)
- **NO sentiment analysis or NLP pipelines** - Out of scope, adds complexity
- **NO multi-provider fallback chains** - Use single adapter per source type
- **NO ML-based anomaly detection** - Rule-based validation only
- **NO real-time streaming** - Batch enrichment only
- **NO manual data entry UI** - Code/config-based company addition only

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: YES - pytest suite exists
- **Automated tests**: Tests-after (no TDD required for config/monitoring tasks)
- **Framework**: pytest with mocking for API calls
- **Agent-Executed QA**: Every task includes concrete verification scenarios

### QA Policy
Every task MUST include agent-executed QA scenarios using:
- **Bash/curl**: API endpoint validation, configuration checks
- **Python REPL**: Import tests, data validation
- **File reading**: Configuration verification, output inspection

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Foundation - API Keys & Infrastructure):
├── Task 1: Configure API keys in .env and settings
├── Task 2: Add API key validation at startup
├── Task 3: Implement API quota tracking
└── Task 4: Add enrichment adapter health check endpoint

Wave 2 (Data Quality - Tickers & Fallback):
├── Task 5: Add ticker symbols to 25+ catalog companies
├── Task 6: Implement ticker lookup service for private companies
├── Task 7: Create fallback enrichment path (no ticker required)
└── Task 8: Add duplicate detection with fuzzy matching

Wave 3 (Expansion - New Discovery Adapters):
├── Task 9: Implement SEC EDGAR discovery adapter
├── Task 10: Implement Companies House discovery adapter
├── Task 11: Add adapter priority ranking system
└── Task 12: Implement incremental enrichment with caching

Wave 4 (Validation - Monitoring & Quality Gates):
├── Task 13: Build enrichment health dashboard
├── Task 14: Implement data quality gates (min sources threshold)
├── Task 15: Add score distribution validation
└── Task 16: Create enrichment failure alerting

Wave FINAL (Review - 4 parallel validation tasks):
├── Task F1: Plan compliance audit
├── Task F2: Code quality review
├── Task F3: Real manual QA
└── Task F4: Scope fidelity check

Critical Path: T1 → T5 → T9 → T13 → F1-F4
Parallel Speedup: ~60% faster than sequential
Max Concurrent: 4 (Wave 1)
```

### Dependency Matrix
- **T1**: — — T2, T3, T4, 1
- **T5**: — — T6, T7, 2
- **T6**: T5 — T7, 3
- **T9**: T7 — T11, T12, 4
- **T13**: T9, T12 — F1, 5

### Agent Dispatch Summary
- **Wave 1**: 4 tasks → quick, quick, quick, quick
- **Wave 2**: 4 tasks → quick, quick, deep, deep
- **Wave 3**: 4 tasks → deep, deep, unspecified-high, deep
- **Wave 4**: 4 tasks → visual-engineering, unspecified-high, unspecified-high, unspecified-high
- **FINAL**: 4 tasks → oracle, unspecified-high, unspecified-high, deep

---

## TODOs

- [ ] 1. Configure API keys in .env and settings

- [ ] 2. Add API key validation at startup

- [ ] 3. Implement API quota tracking

- [ ] 4. Add enrichment adapter health check endpoint

- [ ] 5. Add ticker symbols to 25+ catalog companies

- [ ] 6. Implement ticker lookup service for private companies

- [ ] 7. Create fallback enrichment path (no ticker required)

- [ ] 8. Add duplicate detection with fuzzy matching

- [ ] 9. Implement SEC EDGAR discovery adapter

- [ ] 10. Implement Companies House discovery adapter

- [ ] 11. Add adapter priority ranking system

- [ ] 12. Implement incremental enrichment with caching

- [ ] 13. Build enrichment health dashboard

- [ ] 14. Implement data quality gates (min sources threshold)

- [ ] 15. Add score distribution validation

- [ ] 16. Create enrichment failure alerting

---

## Final Verification Wave

- [ ] F1. **Plan Compliance Audit** — oracle
- [ ] F2. **Code Quality Review** — unspecified-high
- [ ] F3. **Real Manual QA** — unspecified-high
- [ ] F4. **Scope Fidelity Check** — deep

---

## Commit Strategy

- **T1-T4**: chore(config): add API key configuration and validation
- **T5-T8**: feat(enrichment): add tickers and fallback enrichment path
- **T9-T12**: feat(discovery): add SEC EDGAR and Companies House adapters
- **T13-T16**: feat(monitoring): add enrichment health dashboard and quality gates
- **F1-F4**: chore(release): final verification and cleanup

---

## Success Criteria

### Verification Commands
```bash
# 1. API keys configured
python -c "from solstein.config import Settings; s = Settings.load(); print(f'News: {bool(s.news_api_key)}, Crunchbase: {bool(s.crunchbase_api_key)}, Exa: {bool(s.exa_api_key)}')"
# Expected: All True

# 2. Enrichment adapters active
python -c "from solstein.adapters.registry import build_default_registry, Settings; r = build_default_registry(Settings.load()); print(f'Discovery: {len(r.discovery_sources)}, Enrichment: {len(r.enrichment_sources)}')"
# Expected: Discovery: 4+, Enrichment: 10+

# 3. Companies have tickers or alternative enrichment
grep -c '"ticker":' src/solstein/research/discovery.py
# Expected: 25+ tickers

# 4. Score distribution not all 4.67
python -c "import json; data = json.load(open('data/output/scored.json')); scores = [c.get('composite_score', 0) for c in data]; print(f'Score range: {min(scores):.2f} - {max(scores):.2f}, Unique: {len(set(scores))}')"
# Expected: Range > 2.0, Unique scores > 5

# 5. Data quality gates pass
python scripts/validate_enrichment.py --min-sources 2
# Expected: >70% companies pass
```

### Final Checklist
- [ ] All API keys configured and validated
- [ ] 25+ companies have tickers or alternative enrichment
- [ ] 2+ new discovery adapters implemented
- [ ] Enrichment health monitoring working
- [ ] Data quality gates passing (>70% companies with ≥2 sources)
- [ ] Score distribution shows differentiation (not all 4.67)
- [ ] No sentiment analysis or ML pipelines added (scope guardrail)
- [ ] All tests passing


---

## Detailed Tasks

### Wave 1: Foundation (API Keys & Infrastructure)

#### TODO 1: Configure API keys in .env and settings

**What to do**:
Add three API keys to the configuration system:
1. Add EXA_API_KEY to config.py Settings class
2. Ensure NEWS_API_KEY and CRUNCHBASE_API_KEY are properly configured
3. Create .env.example template with placeholder values
4. Add validation that warns if keys are missing (not error)

**Files to modify**:
- src/solstein/config.py - Add EXA_API_KEY field (line ~176)
- .env.example - Create template file with all API keys

**Must NOT do**:
- Do NOT commit actual API keys to git
- Do NOT make API keys required (system should work without them)
- Do NOT add encryption for API keys (use env vars only)

**Recommended Agent Profile**:
- Category: quick
- Reason: Simple configuration changes, no complex logic
- Skills: None needed

**Parallelization**:
- Can Run In Parallel: YES - Wave 1, Task 1
- Blocks: T2, T3, T4
- Blocked By: None

**Acceptance Criteria**:
- [ ] EXA_API_KEY added to Settings class in config.py
- [ ] .env.example exists with all API key placeholders
- [ ] Settings.load() logs warning (not error) if API keys missing
- [ ] No actual API keys in committed code

**QA Scenarios**:
```
Scenario: Config loads without API keys
  Tool: Bash (python)
  Steps:
    1. unset NEWS_API_KEY CRUNCHBASE_API_KEY EXA_API_KEY
    2. python -c "from solstein.config import Settings; s = Settings.load()"
  Expected Result: Loads successfully with warning logs
  Evidence: .sisyphus/evidence/t1-config-load.log

Scenario: Config loads with API keys
  Tool: Bash (python)
  Steps:
    1. export NEWS_API_KEY=test_news CRUNCHBASE_API_KEY=test_cb EXA_API_KEY=test_exa
    2. python -c "from solstein.config import Settings; s = Settings.load(); print(f'exa: {bool(s.exa_api_key)}')"
  Expected Result: Prints "exa: True"
  Evidence: .sisyphus/evidence/t1-config-with-keys.log
```

**Commit**: YES (Wave 1 group)
- Message: chore(config): add EXA_API_KEY and improve API key configuration
- Files: src/solstein/config.py, .env.example


#### TODO 2: Add API key validation at startup

**What to do**:
Add validation in check_configuration() method that:
1. Logs WARNING (not error) when API keys are missing
2. Shows which enrichment adapters will be disabled
3. Lists available vs disabled adapters at startup
4. Provides helpful message on how to get API keys

**Files to modify**:
- src/solstein/config.py - check_configuration() method (line ~235)

**Must NOT do**:
- Do NOT raise ConfigurationError for missing API keys (they're optional)
- Do NOT block startup if keys missing
- Do NOT add key validation in adapter registry (keep it lazy)

**Recommended Agent Profile**:
- Category: quick
- Reason: Simple logging and validation logic

**Parallelization**:
- Can Run In Parallel: YES - Wave 1, Task 2
- Blocks: None
- Blocked By: T1 (needs EXA_API_KEY field)

**Acceptance Criteria**:
- [ ] check_configuration() logs API key status
- [ ] Shows count of enabled vs disabled adapters
- [ ] Provides helpful links for obtaining API keys
- [ ] All API keys treated as optional (warnings only)

**QA Scenarios**:
```
Scenario: Startup shows API key status
  Tool: Bash (python)
  Steps:
    1. python -c "from solstein.config import get_settings; get_settings().check_configuration()" 2>&1
  Expected Result: Output contains "API Key Status" section with enabled/disabled counts
  Evidence: .sisyphus/evidence/t2-startup-status.log

Scenario: All keys present shows all adapters
  Tool: Bash (python)
  Steps:
    1. Set all API keys in environment
    2. python -c "from solstein.adapters.registry import build_default_registry, Settings; r = build_default_registry(Settings.load()); print(f'Discovery: {len(r.discovery_sources)}, Enrichment: {len(r.enrichment_sources)}')"
  Expected Result: Discovery: 3+, Enrichment: 10+
  Evidence: .sisyphus/evidence/t2-all-adapters.log
```

**Commit**: YES (Wave 1 group)
- Message: chore(config): add API key validation and adapter status logging
- Files: src/solstein/config.py

---

#### TODO 3: Implement API quota tracking

**What to do**:
Create a quota tracking system to prevent API limit exhaustion:
1. Create ApiQuotaTracker class in infrastructure/quota_tracker.py
2. Track request counts per adapter per day
3. Implement rate limiting with configurable thresholds
4. Add quota exceeded warnings

**Files to create**:
- src/solstein/infrastructure/quota_tracker.py - New file

**Files to modify**:
- src/solstein/adapters/instrumented.py - Wrap adapter calls with quota check
- src/solstein/config.py - Add quota config (NEWS_API_QUOTA=100, etc.)

**Must NOT do**:
- Do NOT implement distributed quota tracking (single instance only)
- Do NOT persist quota across restarts (in-memory only for now)
- Do NOT implement automatic retries on quota exceeded

**Recommended Agent Profile**:
- Category: quick
- Reason: Simple counter/tracker class

**Parallelization**:
- Can Run In Parallel: YES - Wave 1, Task 3
- Blocks: None
- Blocked By: T1 (needs config structure)

**Acceptance Criteria**:
- [ ] ApiQuotaTracker class exists with track_request(), is_quota_available()
- [ ] Per-adapter daily quotas configured
- [ ] Logs warning when quota 80% exhausted
- [ ] Skips adapter when quota exceeded (graceful degradation)

**QA Scenarios**:
```
Scenario: Quota tracking works
  Tool: Bash (python)
  Steps:
    1. python -c "
from solstein.infrastructure.quota_tracker import ApiQuotaTracker
t = ApiQuotaTracker({'news': 5})
for i in range(7):
    print(f'{i}: {t.is_quota_available("news")}')
    t.track_request('news')
"
  Expected Result: First 5 True, last 2 False
  Evidence: .sisyphus/evidence/t3-quota-tracking.log
```

**Commit**: YES (Wave 1 group)
- Message: feat(infrastructure): add API quota tracking and rate limiting
- Files: src/solstein/infrastructure/quota_tracker.py, src/solstein/config.py

---

#### TODO 4: Add enrichment adapter health check endpoint

**What to do**:
Add a health check endpoint to monitor enrichment adapter status:
1. Add /health/adapters endpoint to API
2. Returns status of each adapter (enabled/disabled, last error, quota status)
3. Shows enrichment success rates
4. Returns 200 if critical adapters working, 503 if degraded

**Files to create**:
- src/solstein/api/routers/health_adapters.py - New router

**Files to modify**:
- src/solstein/api/main.py - Include new router
- src/solstein/api/routers/__init__.py - Export router

**Must NOT do**:
- Do NOT make actual API calls in health check (use cached status)
- Do NOT add authentication to health endpoint (keep it public)
- Do NOT implement historical metrics (current status only)

**Recommended Agent Profile**:
- Category: quick
- Reason: Simple endpoint returning adapter metadata

**Parallelization**:
- Can Run In Parallel: YES - Wave 1, Task 4
- Blocks: None
- Blocked By: None

**Acceptance Criteria**:
- [ ] GET /health/adapters endpoint returns JSON with adapter status
- [ ] Shows discovery_sources and enrichment_sources lists
- [ ] Includes enabled/disabled status for each
- [ ] Returns HTTP 200 normally, 503 if critical adapters down

**QA Scenarios**:
```
Scenario: Health endpoint returns adapter status
  Tool: Bash (curl)
  Steps:
    1. Start API server
    2. curl -s http://localhost:8000/health/adapters | python -m json.tool
  Expected Result: JSON with discovery_sources and enrichment_sources arrays
  Evidence: .sisyphus/evidence/t4-health-endpoint.json

Scenario: Health check shows enabled adapters
  Tool: Bash (python)
  Steps:
    1. export NEWS_API_KEY=test
    2. python -c "
import requests
r = requests.get('http://localhost:8000/health/adapters')
print(f'Status: {r.status_code}')
print(f'Adapters: {len(r.json()["enrichment_sources"])}')
"
  Expected Result: Status 200, adapters count 10+
  Evidence: .sisyphus/evidence/t4-enabled-adapters.log
```

**Commit**: YES (Wave 1 group)
- Message: feat(api): add enrichment adapter health check endpoint
- Files: src/solstein/api/routers/health_adapters.py, src/solstein/api/main.py



### Wave 2: Data Quality (Tickers & Fallback)

#### TODO 5: Add ticker symbols to 25+ catalog companies

**What to do**:
Research and add ticker symbols to companies in the static catalog:
1. Add tickers to Energy market companies (currently ~40% have tickers)
2. Add tickers to LATAM market companies
3. Verify tickers are valid Yahoo Finance symbols
4. Add comment with data source for each ticker

**Files to modify**:
- src/solstein/research/discovery.py - _catalog_for_market() function (lines 39-468)

**Must NOT do**:
- Do NOT add tickers for private companies (they won't work with Yahoo Finance)
- Do NOT guess tickers - verify each one exists on Yahoo Finance
- Do NOT add tickers for companies without public listings

**Recommended Agent Profile**:
- Category: quick
- Reason: Research and data entry task
- Skills: None needed

**Parallelization**:
- Can Run In Parallel: YES - Wave 2, Task 5
- Blocks: T6, T7
- Blocked By: None

**Acceptance Criteria**:
- [ ] 25+ companies have ticker symbols added
- [ ] All tickers verified on finance.yahoo.com
- [ ] Private companies marked with ticker: null (explicit)
- [ ] Comment indicates data source and verification date

**QA Scenarios**:
```
Scenario: Ticker count increased
  Tool: Bash (grep)
  Steps:
    1. grep -c '"ticker":' src/solstein/research/discovery.py
    2. Compare to baseline (currently ~19)
  Expected Result: Count >= 25 (increase of 6+)
  Evidence: .sisyphus/evidence/t5-ticker-count.log

Scenario: Tickers are valid
  Tool: Bash (python)
  Steps:
    1. python -c "
import yfinance as yf
# Test a few tickers from the catalog
tickers = ['ACN', 'CAP.PA', 'VOLUE.OL']
for t in tickers:
    info = yf.Ticker(t).info
    print(f'{t}: {info.get("longName", "INVALID")}')
"
  Expected Result: All tickers return valid company names
  Evidence: .sisyphus/evidence/t5-ticker-validation.log
```

**Commit**: YES (Wave 2 group)
- Message: data(discovery): add ticker symbols for 25+ catalog companies
- Files: src/solstein/research/discovery.py

---

#### TODO 6: Implement ticker lookup service for private companies

**What to do**:
Create a service to lookup ticker symbols for private companies:
1. Create TickerLookupService in data/ticker_lookup.py
2. Search by company name against Yahoo Finance
3. Return best match with confidence score
4. Cache results to avoid repeated lookups

**Files to create**:
- src/solstein/data/ticker_lookup.py - New service

**Files to modify**:
- src/solstein/research/discovery.py - Use lookup service when ticker is None

**Must NOT do**:
- Do NOT use external paid APIs for lookup (use free sources only)
- Do NOT implement fuzzy matching for ticker symbols (exact matches only)
- Do NOT cache across application restarts (in-memory only)

**Recommended Agent Profile**:
- Category: quick
- Reason: Service class with simple lookup logic

**Parallelization**:
- Can Run In Parallel: YES - Wave 2, Task 6
- Blocks: T7
- Blocked By: T5

**Acceptance Criteria**:
- [ ] TickerLookupService class with lookup_by_name() method
- [ ] Returns ticker symbol + confidence score
- [ ] Caches results in memory
- [ ] Gracefully handles lookup failures

**QA Scenarios**:
```
Scenario: Lookup service finds tickers
  Tool: Bash (python)
  Steps:
    1. python -c "
from solstein.data.ticker_lookup import TickerLookupService
svc = TickerLookupService()
result = svc.lookup_by_name('Apple Inc')
print(f'Ticker: {result.ticker}, Confidence: {result.confidence}')
"
  Expected Result: Returns AAPL with high confidence
  Evidence: .sisyphus/evidence/t6-lookup-service.log

Scenario: Lookup caches results
  Tool: Bash (python)
  Steps:
    1. python -c "
from solstein.data.ticker_lookup import TickerLookupService
svc = TickerLookupService()
svc.lookup_by_name('Microsoft')  # First call
svc.lookup_by_name('Microsoft')  # Second call (should use cache)
print(f'Cache hits: {svc.cache_hits}')
"
  Expected Result: Cache hits = 1
  Evidence: .sisyphus/evidence/t6-lookup-cache.log
```

**Commit**: YES (Wave 2 group)
- Message: feat(data): add ticker lookup service for private companies
- Files: src/solstein/data/ticker_lookup.py

---

#### TODO 7: Create fallback enrichment path (no ticker required)

**What to do**:
Build enrichment that works without ticker symbols:
1. Create NoTickerEnrichment adapter in adapters/enrichment/no_ticker.py
2. Uses website scraping, news search, LinkedIn as data sources
3. Returns RawDataSource with available data
4. Registered in registry for all companies without tickers

**Files to create**:
- src/solstein/adapters/enrichment/no_ticker.py - New adapter

**Files to modify**:
- src/solstein/adapters/registry.py - Register new adapter
- src/solstein/research/gather.py - Use fallback when Yahoo Finance fails

**Must NOT do**:
- Do NOT duplicate existing adapter logic (compose existing adapters)
- Do NOT require API keys (use Website, LinkedIn which work without keys)
- Do NOT implement new data sources (use existing adapters only)

**Recommended Agent Profile**:
- Category: deep
- Reason: Complex adapter composition logic
- Skills: None needed

**Parallelization**:
- Can Run In Parallel: YES - Wave 2, Task 7
- Blocks: T9, T10
- Blocked By: T6

**Acceptance Criteria**:
- [ ] NoTickerEnrichment adapter implements EnrichmentSource protocol
- [ ] Works without ticker symbol
- [ ] Uses Website + LinkedIn + News (if available) as sources
- [ ] Returns valid RawDataSource with confidence scores

**QA Scenarios**:
```
Scenario: Fallback enrichment works for private company
  Tool: Bash (python)
  Steps:
    1. python -c "
from solstein.adapters.enrichment.no_ticker import NoTickerEnrichment
adapter = NoTickerEnrichment()
result = adapter.enrich(
    company_id='test-co',
    company_name='Test Company',
    website='https://example.com'
)
print(f'Sources: {result.source_type}')
print(f'Has data: {bool(result.raw_content)}')
"
  Expected Result: Returns RawDataSource with website/linkedin data
  Evidence: .sisyphus/evidence/t7-fallback-enrichment.log

Scenario: Pipeline uses fallback for companies without tickers
  Tool: Bash (python)
  Steps:
    1. Run discovery for a market with private companies
    2. Check that companies without tickers still get enriched
    3. Verify enrichment_source_count > 0
  Expected Result: Private companies have enrichment_source_count >= 1
  Evidence: .sisyphus/evidence/t7-pipeline-fallback.log
```

**Commit**: YES (Wave 2 group)
- Message: feat(enrichment): add fallback enrichment for companies without tickers
- Files: src/solstein/adapters/enrichment/no_ticker.py, src/solstein/adapters/registry.py

---

#### TODO 8: Add duplicate detection with fuzzy matching

**What to do**:
Implement fuzzy duplicate detection for companies across sources:
1. Create DuplicateDetector in research/duplicate_detector.py
2. Use fuzzy string matching (difflib or rapidfuzz)
3. Detect companies like "Octopus Energy" vs "Octopus Energy Group"
4. Merge duplicates keeping highest relevance score

**Files to create**:
- src/solstein/research/duplicate_detector.py - New module

**Files to modify**:
- src/solstein/research/discovery.py - Call duplicate detector in _deduplicate_candidates

**Must NOT do**:
- Do NOT add heavy ML/NLP dependencies (use simple string similarity)
- Do NOT implement complex entity resolution (just name matching)
- Do NOT merge companies with different regions/industries

**Recommended Agent Profile**:
- Category: deep
- Reason: Algorithm implementation for fuzzy matching
- Skills: None needed

**Parallelization**:
- Can Run In Parallel**: YES - Wave 2, Task 8
- Blocks: None
- Blocked By: None

**Acceptance Criteria**:
- [ ] DuplicateDetector class with find_duplicates() method
- [ ] Uses string similarity threshold (configurable, default 0.85)
- [ ] Returns list of duplicate groups
- [ ] Merged candidates keep highest relevance and union of sources

**QA Scenarios**:
```
Scenario: Duplicate detection finds similar names
  Tool: Bash (python)
  Steps:
    1. python -c "
from solstein.research.duplicate_detector import DuplicateDetector
detector = DuplicateDetector(threshold=0.85)
candidates = [
    {'name': 'Octopus Energy', 'company_id': 'octopus-energy'},
    {'name': 'Octopus Energy Group', 'company_id': 'octopus-energy-group'},
    {'name': 'Shell', 'company_id': 'shell'}
]
duplicates = detector.find_duplicates(candidates)
print(f'Found {len(duplicates)} duplicate groups')
"
  Expected Result: Finds 1 duplicate group (Octopus Energy variants)
  Evidence: .sisyphus/evidence/t8-duplicate-detection.log

Scenario: Discovery deduplicates across sources
  Tool: Bash (python)
  Steps:
    1. Run discovery with multiple sources
    2. Check that companies like "Octopus Energy" appear only once
    3. Verify merged entry has combined source_links
  Expected Result: No duplicate company names in final list
  Evidence: .sisyphus/evidence/t8-discovery-dedup.log
```

**Commit**: YES (Wave 2 group)
- Message: feat(discovery): add fuzzy duplicate detection across sources
- Files: src/solstein/research/duplicate_detector.py, src/solstein/research/discovery.py



### Wave 3: Expansion (New Discovery Adapters)

#### TODO 9: Implement SEC EDGAR discovery adapter

**What to do**:
Create discovery adapter for US public companies via SEC EDGAR:
1. Create SecEdgarDiscovery in adapters/discovery/sec_edgar.py
2. Search EDGAR by company name or ticker
3. Returns DiscoveryCandidate with CIK, ticker, company info
4. Requires no API key (EDGAR is public)

**Files to create**:
- src/solstein/adapters/discovery/sec_edgar.py - New adapter

**Files to modify**:
- src/solstein/adapters/registry.py - Register new adapter

**Must NOT do**:
- Do NOT implement full EDGAR parsing (just company lookup)
- Do NOT download filings (just metadata)
- Do NOT require API authentication

**Recommended Agent Profile**:
- Category: deep
- Reason: Complex integration with external API
- Skills: None needed

**Parallelization**:
- Can Run In Parallel: YES - Wave 3, Task 9
- Blocks: T11
- Blocked By: T7

**Acceptance Criteria**:
- [ ] SecEdgarDiscovery implements DiscoverySource protocol
- [ ] Searches EDGAR by company name and returns matches
- [ ] Returns CIK, ticker, company name, industry
- [ ] No API key required

**QA Scenarios**:
```
Scenario: SEC EDGAR adapter finds companies
  Tool: Bash (python)
  Steps:
    1. python -c "
from solstein.adapters.discovery.sec_edgar import SecEdgarDiscovery
adapter = SecEdgarDiscovery()
results = adapter.discover(
    market='energy',
    seed_company='renewable energy',
    max_results=5
)
print(f'Found {len(results)} companies')
for r in results[:3]:
    print(f'  - {r.name} ({r.ticker})')
"
  Expected Result: Returns 5 companies with valid tickers
  Evidence: .sisyphus/evidence/t9-sec-edgar.log

Scenario: SEC adapter registered in registry
  Tool: Bash (python)
  Steps:
    1. python -c "
from solstein.adapters.registry import build_default_registry, Settings
r = build_default_registry(Settings.load())
source_names = [s.source_name for s in r.discovery_sources]
print(f'Sources: {source_names}')
"
  Expected Result: List includes 'sec_edgar'
  Evidence: .sisyphus/evidence/t9-sec-registered.log
```

**Commit**: YES (Wave 3 group)
- Message: feat(discovery): add SEC EDGAR discovery adapter for US public companies
- Files: src/solstein/adapters/discovery/sec_edgar.py, src/solstein/adapters/registry.py

---

#### TODO 10: Implement Companies House discovery adapter

**What to do**:
Create discovery adapter for UK companies via Companies House API:
1. Create CompaniesHouseDiscovery in adapters/discovery/companies_house.py
2. Search by company name or SIC code
3. Returns DiscoveryCandidate with company number, name, status
4. Requires COMPANIES_HOUSE_API_KEY (free tier available)

**Files to create**:
- src/solstein/adapters/discovery/companies_house.py - New adapter

**Files to modify**:
- src/solstein/adapters/registry.py - Register new adapter (conditional on API key)
- src/solstein/config.py - Add COMPANIES_HOUSE_API_KEY setting

**Must NOT do**:
- Do NOT implement full company profile lookup (just discovery)
- Do NOT download filing PDFs (just metadata)
- Do NOT require paid API tier

**Recommended Agent Profile**:
- Category: deep
- Reason: External API integration with authentication
- Skills: None needed

**Parallelization**:
- Can Run In Parallel: YES - Wave 3, Task 10
- Blocks: T11
- Blocked By: T7

**Acceptance Criteria**:
- [ ] CompaniesHouseDiscovery implements DiscoverySource protocol
- [ ] Searches Companies House by name
- [ ] Returns company number, name, status, incorporation date
- [ ] Conditional registration (only if API key present)

**QA Scenarios**:
```
Scenario: Companies House adapter finds UK companies
  Tool: Bash (python)
  Steps:
    1. export COMPANIES_HOUSE_API_KEY=test_key
    2. python -c "
from solstein.adapters.discovery.companies_house import CompaniesHouseDiscovery
adapter = CompaniesHouseDiscovery(api_key='test_key')
results = adapter.discover(
    market='energy',
    seed_company='renewable',
    max_results=5
)
print(f'Found {len(results)} UK companies')
"
  Expected Result: Returns UK companies with company numbers
  Evidence: .sisyphus/evidence/t10-companies-house.log

Scenario: Adapter disabled without API key
  Tool: Bash (python)
  Steps:
    1. unset COMPANIES_HOUSE_API_KEY
    2. python -c "
from solstein.adapters.registry import build_default_registry, Settings
r = build_default_registry(Settings.load())
source_names = [s.source_name for s in r.discovery_sources]
print(f'Has companies_house: {"companies_house" in source_names}')
"
  Expected Result: False (adapter not registered without key)
  Evidence: .sisyphus/evidence/t10-conditional-registration.log
```

**Commit**: YES (Wave 3 group)
- Message: feat(discovery): add Companies House discovery adapter for UK companies
- Files: src/solstein/adapters/discovery/companies_house.py, src/solstein/adapters/registry.py, src/solstein/config.py

---

#### TODO 11: Add adapter priority ranking system

**What to do**:
Implement priority ranking for enrichment adapters:
1. Add priority field to EnrichmentSource protocol
2. Rank adapters by confidence and authority
3. Process high-priority adapters first
4. Skip low-priority adapters if high-priority succeed

**Files to modify**:
- src/solstein/adapters/protocols.py - Add priority property
- src/solstein/adapters/registry.py - Sort by priority
- src/solstein/research/gather.py - Use priority order

**Must NOT do**:
- Do NOT implement dynamic priority adjustment (static only)
- Do NOT skip adapters based on quota (handled separately)
- Do NOT add complex scoring algorithms (simple 1-10 scale)

**Recommended Agent Profile**:
- Category: unspecified-high
- Reason: Protocol changes affecting multiple files
- Skills: None needed

**Parallelization**:
- Can Run In Parallel**: YES - Wave 3, Task 11
- Blocks: None
- Blocked By: T9, T10

**Acceptance Criteria**:
- [ ] EnrichmentSource protocol has priority property
- [ ] Adapters ranked: Yahoo Finance (10), Funding (8), News (7), etc.
- [ ] High priority adapters processed first in enrich_company()
- [ ] Registry returns sorted list by priority

**QA Scenarios**:
```
Scenario: Adapters sorted by priority
  Tool: Bash (python)
  Steps:
    1. python -c "
from solstein.adapters.registry import build_default_registry, Settings
r = build_default_registry(Settings.load())
for s in r.enrichment_sources[:5]:
    print(f'{s.priority}: {s.source_name}')
"
  Expected Result: Yahoo Finance first (priority 10), then Funding (8), etc.
  Evidence: .sisyphus/evidence/t11-priority-sorting.log
```

**Commit**: YES (Wave 3 group)
- Message: feat(adapters): add priority ranking system for enrichment adapters
- Files: src/solstein/adapters/protocols.py, src/solstein/adapters/registry.py, src/solstein/research/gather.py

---

#### TODO 12: Implement incremental enrichment with caching

**What to do**:
Add caching to avoid re-enriching unchanged companies:
1. Create EnrichmentCache in infrastructure/enrichment_cache.py
2. Cache RawDataSource by company_id + source_name + date
3. Check cache before calling adapter
4. Invalidate cache after 7 days

**Files to create**:
- src/solstein/infrastructure/enrichment_cache.py - New module

**Files to modify**:
- src/solstein/research/gather.py - Check cache before enrichment
- src/solstein/config.py - Add cache settings (ENRICHER_CACHE_TTL_DAYS)

**Must NOT do**:
- Do NOT use external cache (Redis) - use file-based cache
- Do NOT cache across application restarts (in-memory + file backup)
- Do NOT implement cache warming (on-demand only)

**Recommended Agent Profile**:
- Category: deep
- Reason: Complex caching logic with TTL and invalidation
- Skills: None needed

**Parallelization**:
- Can Run In Parallel**: YES - Wave 3, Task 12
- Blocks: T13, T14
- Blocked By: T9

**Acceptance Criteria**:
- [ ] EnrichmentCache class with get() and set() methods
- [ ] Cache key includes company_id, source_name, date
- [ ] TTL of 7 days (configurable)
- [ ] Cache hit logged at DEBUG level

**QA Scenarios**:
```
Scenario: Cache stores and retrieves enrichment data
  Tool: Bash (python)
  Steps:
    1. python -c "
from solstein.infrastructure.enrichment_cache import EnrichmentCache
from solstein.domain.models import RawDataSource, DataSourceType

cache = EnrichmentCache(ttl_days=7)

# Store
raw = RawDataSource(
    source_type=DataSourceType.YAHOO_FINANCE,
    source_name='yahoo_finance',
    raw_content={'test': 'data'},
    retrieval_timestamp=datetime.now()
)
cache.set('test-co', 'yahoo_finance', raw)

# Retrieve
cached = cache.get('test-co', 'yahoo_finance')
print(f'Cache hit: {cached is not None}')
"
  Expected Result: Cache hit: True
  Evidence: .sisyphus/evidence/t12-cache-basic.log

Scenario: Cache respects TTL
  Tool: Bash (python)
  Steps:
    1. python -c "
from solstein.infrastructure.enrichment_cache import EnrichmentCache
# Create cache with 0-day TTL (immediate expiry)
cache = EnrichmentCache(ttl_days=0)
# Store and try to retrieve
# ... store data ...
cached = cache.get('test-co', 'yahoo_finance')
print(f'Expired: {cached is None}')
"
  Expected Result: Expired: True
  Evidence: .sisyphus/evidence/t12-cache-ttl.log
```

**Commit**: YES (Wave 3 group)
- Message: feat(infrastructure): add incremental enrichment caching with TTL
- Files: src/solstein/infrastructure/enrichment_cache.py, src/solstein/research/gather.py, src/solstein/config.py



### Wave 4: Validation (Monitoring & Quality Gates)

#### TODO 13: Build enrichment health dashboard

**What to do**:
Create a dashboard to monitor enrichment pipeline health:
1. Create dashboard page at /dashboard/enrichment-health
2. Show adapter status (enabled/disabled, last run, success rate)
3. Display company enrichment coverage (how many have 2+ sources)
4. Show score distribution chart
5. List recent enrichment failures

**Files to create**:
- dashboard/src/app/enrichment-health/page.tsx - New dashboard page
- dashboard/src/components/enrichment/AdapterStatus.tsx - Component
- dashboard/src/components/enrichment/ScoreDistribution.tsx - Component

**Files to modify**:
- dashboard/src/app/page.tsx - Add link to enrichment health
- dashboard/src/components/layout/Navigation.tsx - Add nav item

**Must NOT do**:
- Do NOT implement real-time updates (static data, refresh button only)
- Do NOT add authentication (public dashboard)
- Do NOT implement historical charts (current state only)

**Recommended Agent Profile**:
- Category: visual-engineering
- Reason: Frontend UI development with React/Next.js
- Skills: frontend-ui-ux

**Parallelization**:
- Can Run In Parallel: YES - Wave 4, Task 13
- Blocks: None
- Blocked By: T4 (needs health endpoint)

**Acceptance Criteria**:
- [ ] /dashboard/enrichment-health page exists and loads
- [ ] Shows adapter status (enabled/disabled counts)
- [ ] Shows company enrichment coverage percentage
- [ ] Shows score distribution chart (not all 4.67)
- [ ] Lists recent failures with timestamps

**QA Scenarios**:
```
Scenario: Dashboard loads and shows data
  Tool: Playwright
  Steps:
    1. Navigate to http://localhost:3000/enrichment-health
    2. Wait for page to load
    3. Screenshot of full page
    4. Verify "Adapter Status" section visible
    5. Verify "Score Distribution" chart visible
  Expected Result: Page loads with all sections visible
  Evidence: .sisyphus/evidence/t13-dashboard-screenshot.png

Scenario: Dashboard shows correct adapter counts
  Tool: Playwright
  Steps:
    1. Navigate to /enrichment-health
    2. Read "Discovery Sources" count
    3. Read "Enrichment Sources" count
    4. Compare to API /health/adapters response
  Expected Result: Counts match API response
  Evidence: .sisyphus/evidence/t13-dashboard-counts.log
```

**Commit**: YES (Wave 4 group)
- Message: feat(dashboard): add enrichment health monitoring dashboard
- Files: dashboard/src/app/enrichment-health/page.tsx, dashboard/src/components/enrichment/*

---

#### TODO 14: Implement data quality gates (min sources threshold)

**What to do**:
Add configurable quality gates to pipeline:
1. Add min_enrichment_sources parameter to run_market_intelligence()
2. Gate rejects companies with fewer sources than threshold
3. Log which companies were filtered and why
4. Make threshold configurable per market

**Files to modify**:
- src/solstein/research/pipeline.py - Add quality gate (already has min_sources_per_company)
- src/solstein/research/gather.py - Expose source count in Company model
- src/solstein/api/routers/research.py - Add parameter to API endpoint

**Must NOT do**:
- Do NOT implement automatic retry for failed enrichments
- Do NOT add ML-based quality scoring (simple count only)
- Do NOT block entire pipeline if some companies fail gate

**Recommended Agent Profile**:
- Category: unspecified-high
- Reason: Pipeline modification with gating logic
- Skills: None needed

**Parallelization**:
- Can Run In Parallel: YES - Wave 4, Task 14
- Blocks: None
- Blocked By: T7 (needs fallback enrichment working)

**Acceptance Criteria**:
- [ ] min_sources_per_company parameter works in pipeline
- [ ] Companies below threshold logged and filtered
- [ ] Gate shows count before/after filtering
- [ ] API endpoint accepts min_sources parameter

**QA Scenarios**:
```
Scenario: Quality gate filters low-source companies
  Tool: Bash (python)
  Steps:
    1. python -c "
from solstein.research.pipeline import run_market_intelligence
from pathlib import Path

result = run_market_intelligence(
    seed_company='Shell',
    market='energy',
    output_dir=Path('test_output'),
    max_companies=10,
    min_sources_per_company=2  # Require 2+ sources
)
print(f'Companies after gate: {result["profiles"]}')
"
  Expected Result: Only companies with 2+ sources in output
  Evidence: .sisyphus/evidence/t14-quality-gate.log

Scenario: API accepts min_sources parameter
  Tool: Bash (curl)
  Steps:
    1. curl -X POST 'http://localhost:8000/api/v1/research/market?min_sources=2'          -H 'Content-Type: application/json'          -d '{"seed_company": "Shell", "market": "energy"}'
  Expected Result: HTTP 200 with companies having 2+ sources
  Evidence: .sisyphus/evidence/t14-api-gate.json
```

**Commit**: YES (Wave 4 group)
- Message: feat(pipeline): implement data quality gates for minimum enrichment sources
- Files: src/solstein/research/pipeline.py, src/solstein/api/routers/research.py

---

#### TODO 15: Add score distribution validation

**What to do**:
Create validation to ensure scores are differentiated:
1. Create ScoreValidator in analytics/score_validator.py
2. Check that not all scores are identical (4.67)
3. Verify score distribution across Phoenix/Salt/Lead
4. Alert if >80% of companies have same score

**Files to create**:
- src/solstein/analytics/score_validator.py - New module

**Files to modify**:
- src/solstein/research/pipeline.py - Call validator after scoring
- src/solstein/api/routers/scoring.py - Add validation endpoint

**Must NOT do**:
- Do NOT implement automatic score adjustment (validation only)
- Do NOT add complex statistical tests (simple variance check)
- Do NOT require specific distribution shape (just not all identical)

**Recommended Agent Profile**:
- Category: unspecified-high
- Reason: Validation logic with statistical checks
- Skills: None needed

**Parallelization**:
- Can Run In Parallel**: YES - Wave 4, Task 15
- Blocks: None
- Blocked By: T14

**Acceptance Criteria**:
- [ ] ScoreValidator class with validate_distribution() method
- [ ] Returns warning if >80% of scores identical
- [ ] Shows distribution across Phoenix/Salt/Lead classifications
- [ ] API endpoint /scoring/validate returns validation results

**QA Scenarios**:
```
Scenario: Validator detects uniform scores
  Tool: Bash (python)
  Steps:
    1. python -c "
from solstein.analytics.score_validator import ScoreValidator
from solstein.domain.models import Company, ScoringExplanation

# Create companies with identical scores
companies = []
for i in range(10):
    c = Company(id=f'co{i}', name=f'Company {i}')
    c.composite_score = 4.67
    companies.append(c)

validator = ScoreValidator()
result = validator.validate_distribution(companies)
print(f'Uniform scores detected: {result.is_uniform}')
"
  Expected Result: Uniform scores detected: True
  Evidence: .sisyphus/evidence/t15-uniform-detection.log

Scenario: Validator passes differentiated scores
  Tool: Bash (python)
  Steps:
    1. python -c "
from solstein.analytics.score_validator import ScoreValidator
# Create companies with varied scores
companies = []
scores = [8.5, 6.2, 4.67, 3.1, 7.8, 5.5, 4.2, 9.1, 2.3, 6.9]
for i, score in enumerate(scores):
    c = Company(id=f'co{i}', name=f'Company {i}')
    c.composite_score = score
    companies.append(c)

validator = ScoreValidator()
result = validator.validate_distribution(companies)
print(f'Valid distribution: {not result.is_uniform}')
print(f'Phoenix: {result.phoenix_count}, Salt: {result.salt_count}, Lead: {result.lead_count}')
"
  Expected Result: Valid distribution: True, counts in each category
  Evidence: .sisyphus/evidence/t15-differentiated-scores.log
```

**Commit**: YES (Wave 4 group)
- Message: feat(analytics): add score distribution validation
- Files: src/solstein/analytics/score_validator.py, src/solstein/research/pipeline.py

---

#### TODO 16: Create enrichment failure alerting

**What to do**:
Add alerting when enrichment fails for companies:
1. Create EnrichmentAlerter in monitoring/enrichment_alerts.py
2. Log ERROR when enrichment fails for >20% of companies
3. Send alert if critical adapter (Yahoo Finance) fails
4. Include failure details (company name, adapter, error)

**Files to create**:
- src/solstein/monitoring/enrichment_alerts.py - New module

**Files to modify**:
- src/solstein/research/gather.py - Call alerter on enrichment failure
- src/solstein/research/pipeline.py - Alert on pipeline completion

**Must NOT do**:
- Do NOT implement email/Slack notifications (log alerts only)
- Do NOT add PagerDuty integration (out of scope)
- Do NOT implement automatic remediation (alert only)

**Recommended Agent Profile**:
- Category: unspecified-high
- Reason: Monitoring and alerting logic
- Skills: None needed

**Parallelization**:
- Can Run In Parallel**: YES - Wave 4, Task 16
- Blocks: None
- Blocked By: T14

**Acceptance Criteria**:
- [ ] EnrichmentAlerter class with alert_failure() method
- [ ] Logs ERROR when >20% of companies fail enrichment
- [ ] Logs WARNING when critical adapter fails
- [ ] Alert includes company name, adapter, error message

**QA Scenarios**:
```
Scenario: Alerter triggers on high failure rate
  Tool: Bash (python)
  Steps:
    1. python -c "
from solstein.monitoring.enrichment_alerts import EnrichmentAlerter

alerter = EnrichmentAlerter(failure_threshold=0.2)

# Simulate failures (30% failure rate)
failures = []
for i in range(30):
    failures.append({'company': f'co{i}', 'adapter': 'yahoo_finance', 'error': 'Timeout'})

alerter.alert_failure(failures, total_companies=100)
"
  Expected Result: ERROR log: "Enrichment failure rate 30% exceeds threshold 20%"
  Evidence: .sisyphus/evidence/t16-high-failure-alert.log

Scenario: Alerter ignores low failure rate
  Tool: Bash (python)
  Steps:
    1. python -c "
from solstein.monitoring.enrichment_alerts import EnrichmentAlerter

alerter = EnrichmentAlerter(failure_threshold=0.2)

# Simulate low failures (10% failure rate)
failures = [{'company': 'co1', 'adapter': 'news', 'error': 'API limit'}]

alerter.alert_failure(failures, total_companies=100)
"
  Expected Result: No ERROR log (only DEBUG/INFO)
  Evidence: .sisyphus/evidence/t16-low-failure-ok.log
```

**Commit**: YES (Wave 4 group)
- Message: feat(monitoring): add enrichment failure alerting system
- Files: src/solstein/monitoring/enrichment_alerts.py, src/solstein/research/gather.py



---

## Final Verification Wave

### F1. Plan Compliance Audit — oracle

**What to do**:
Read the plan end-to-end and verify all Must Haves are implemented:
1. Check API keys configured (EXA_API_KEY, NEWS_API_KEY, CRUNCHBASE_API_KEY)
2. Verify 25+ companies have tickers or alternative enrichment
3. Confirm 2+ new discovery adapters implemented (SEC EDGAR, Companies House)
4. Validate enrichment health monitoring exists
5. Check data quality gates (min 2 sources per company)
6. Verify score distribution shows differentiation (not all 4.67)

**Must NOT do**:
- Do NOT run full pipeline (just verify code exists)
- Do NOT modify any files (read-only audit)
- Do NOT skip any checklist items

**Acceptance Criteria**:
- [ ] All Must Haves verified with file references
- [ ] All Must NOT Haves confirmed absent
- [ ] No critical gaps identified
- [ ] Report generated with VERDICT: APPROVE or REJECT

**QA Scenarios**:
```
Scenario: All Must Haves present
  Tool: Bash (grep/find)
  Steps:
    1. grep -l "EXA_API_KEY" src/solstein/config.py
    2. grep -c '"ticker":' src/solstein/research/discovery.py
    3. ls src/solstein/adapters/discovery/sec_edgar.py
    4. ls src/solstein/adapters/discovery/companies_house.py
    5. ls dashboard/src/app/enrichment-health/page.tsx
  Expected Result: All files present, ticker count >= 25
  Evidence: .sisyphus/evidence/f1-compliance-report.txt
```

**Commit**: NO (verification task)

---

### F2. Code Quality Review — unspecified-high

**What to do**:
Run all quality checks on modified files:
1. Run `tsc --noEmit` for TypeScript files (dashboard)
2. Run `ruff check` for Python files
3. Run `mypy` for type checking
4. Check for `as any`, `@ts-ignore`, empty catches, console.log in prod
5. Review for AI slop patterns (excessive comments, generic names)

**Acceptance Criteria**:
- [ ] Build passes (no TypeScript errors)
- [ ] Lint passes (no ruff errors)
- [ ] Type check passes (no mypy errors)
- [ ] No `as any` or `@ts-ignore` added
- [ ] No empty catch blocks
- [ ] No AI slop patterns detected

**QA Scenarios**:
```
Scenario: All quality checks pass
  Tool: Bash (npm/python)
  Steps:
    1. cd dashboard && npm run build 2>&1 | head -20
    2. ruff check src/solstein/
    3. mypy src/solstein/ --ignore-missing-imports
  Expected Result: Build success, 0 ruff errors, 0 mypy errors
  Evidence: .sisyphus/evidence/f2-quality-report.txt
```

**Commit**: NO (verification task)

---

### F3. Real Manual QA — unspecified-high

**What to do**:
Execute every QA scenario from every task:
1. Run all Python REPL test scenarios
2. Test API endpoints with curl
3. Verify dashboard pages load
4. Check enrichment pipeline end-to-end
5. Validate score distribution changed from 4.67

**Acceptance Criteria**:
- [ ] All 16 task QA scenarios executed
- [ ] All scenarios pass (expected results match actual)
- [ ] Evidence files captured for each scenario
- [ ] Score distribution shows range > 2.0

**QA Scenarios**:
```
Scenario: End-to-end pipeline test
  Tool: Bash (python)
  Steps:
    1. Set all API keys
    2. python -c "
from solstein.research.pipeline import run_market_intelligence
from pathlib import Path

result = run_market_intelligence(
    seed_company='Shell',
    market='energy',
    output_dir=Path('test_output'),
    max_companies=10,
    min_sources_per_company=2
)
print(f'Discovered: {result["discovered"]}')
print(f'Profiles: {result["profiles"]}')
print(f'Avg sources: {result["avg_unique_sources_per_company"]}')
"
  Expected Result: 10 companies discovered, >5 profiles, avg sources >= 2
  Evidence: .sisyphus/evidence/f3-e2e-test.log

Scenario: Score distribution validation
  Tool: Bash (python)
  Steps:
    1. python -c "
import json
data = json.load(open('test_output/scored.json'))
scores = [c.get('composite_score', 0) for c in data]
print(f'Range: {min(scores):.2f} - {max(scores):.2f}')
print(f'Unique: {len(set(scores))}')
print(f'All 4.67: {all(s == 4.67 for s in scores)}')
"
  Expected Result: Range > 2.0, Unique > 5, All 4.67 = False
  Evidence: .sisyphus/evidence/f3-score-distribution.log
```

**Commit**: NO (verification task)

---

### F4. Scope Fidelity Check — deep

**What to do**:
Verify implementation matches plan specification:
1. Check that only specified files were modified
2. Verify NO sentiment analysis or NLP pipelines added
3. Confirm NO multi-provider fallback chains implemented
4. Validate NO ML-based anomaly detection added
5. Check that all tasks address specific plan items

**Acceptance Criteria**:
- [ ] All tasks implemented as specified
- [ ] No scope creep (extra features not in plan)
- [ ] All guardrails respected
- [ ] Cross-task contamination checked (no task N touching Task M's files incorrectly)

**QA Scenarios**:
```
Scenario: No scope creep detected
  Tool: Bash (grep/find)
  Steps:
    1. grep -r "sentiment" src/solstein/ --include="*.py" | wc -l
    2. grep -r "NLP\|natural language" src/solstein/ --include="*.py" | wc -l
    3. grep -r "machine learning\|ML\|neural" src/solstein/ --include="*.py" | wc -l
    4. git diff --name-only | wc -l
  Expected Result: All counts = 0 (no scope creep files), file count reasonable
  Evidence: .sisyphus/evidence/f4-scope-check.txt

Scenario: Tasks match plan specification
  Tool: Bash (git)
  Steps:
    1. git log --oneline --all | head -20
    2. Verify commit messages match plan task messages
    3. Check no commits mention unplanned features
  Expected Result: All commits match plan, no unplanned features
  Evidence: .sisyphus/evidence/f4-commit-check.txt
```

**Commit**: NO (verification task)

---

## Summary

**Total Tasks**: 16 implementation tasks + 4 verification tasks = 20 tasks
**Waves**: 4 implementation waves + 1 final verification wave
**Estimated Timeline**: 
- Wave 1 (API Keys): 1-2 days
- Wave 2 (Tickers): 2-3 days  
- Wave 3 (Adapters): 3-4 days
- Wave 4 (Monitoring): 2-3 days
- **Total: 8-12 days**

**Critical Path**: T1 → T5 → T9 → T13 → F1-F4
**Parallel Speedup**: ~60% (can run 3-4 tasks simultaneously in early waves)

**Success Metrics**:
- >70% of companies have ≥2 enrichment sources
- Score distribution range > 2.0 (not all 4.67)
- 4+ discovery sources registered
- 10+ enrichment sources registered
- Enrichment health dashboard functional
- All quality gates passing

**Next Steps**:
1. Run `/start-work` to begin execution
2. Start with Wave 1 (API keys configuration)
3. Review results after each wave before proceeding
