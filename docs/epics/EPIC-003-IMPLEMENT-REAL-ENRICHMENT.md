# EPIC-003: Implement Real Data Enrichment System

## Status: 🔴 CRITICAL
## Priority: P0 - System Blocking
## Effort: 13 story points
## Sprint: Must be completed before production use

---

## Problem Statement

The enrichment system is **completely fake**. It returns hardcoded mock data instead of making real API calls to external data sources.

### Current Broken State
```python
# In eneve_enrichment_integration.py lines 76-95
mock_sources = [
    ("LinkedIn", "linkedin"),      # FAKE - no API call
    ("Website", "website"),        # FAKE - no scraping
    ("Crunchbase", "crunchbase"),  # FAKE - no API call
]
# Always returns exactly 3 hardcoded sources
```

### Impact
- **0% real enrichment** - all data is fabricated
- **enrichment_source_count reset to 0** in final output despite input having 2-5 sources
- **Data quality score is calculated from fake data**
- **No actual competitive intelligence gathered**
- **System cannot be used for real investment decisions**

---

## Success Criteria

- [ ] Real API calls made to LinkedIn, Crunchbase, News sources
- [ ] Fallback mechanisms work when APIs fail or lack keys
- [ ] enrichment_source_count reflects actual data sources used
- [ ] Data quality score calculated from real confidence values
- [ ] Enrichment completes within 30 seconds per company
- [ ] Error handling for API failures, rate limits, timeouts
- [ ] API keys configurable via environment variables

---

## Technical Analysis

### Current Architecture
```
EneveEnricher.enrich_companies()
  → _enrich_company() [MOCKED - returns hardcoded data]
  → No real API calls
```

### Working Architecture (Already Exists!)
```
EnrichmentPipeline.enrich()
  → Calls registered adapters in parallel
  → AdditionalDataSources with real implementations
  → Proper error handling and fallbacks
```

### Root Cause
The ENEVE integration bypasses the working enrichment pipeline and uses mock data instead of calling `EnrichmentPipeline.enrich()`.

### Affected Files
- `src/solstein/data/eneve_enrichment_integration.py` (main issue)
- `src/solstein/application/enrichment_pipeline.py` (working, not used)
- `src/solstein/adapters/enrichment/*.py` (working adapters)
- `src/solstein/data/additional_sources.py` (working implementations)

---

## Stories

### Story 3.1: Replace Mock Enrichment with Real Pipeline
**Priority:** P0 | **Effort:** 5 points

**Description:**
Replace the mocked `EneveEnricher` with calls to the working `EnrichmentPipeline`.

**Acceptance Criteria:**
- [ ] `EneveEnricher._enrich_company()` calls `EnrichmentPipeline.enrich()`
- [ ] Remove all mock data generation
- [ ] Pass actual company data (name, website, industry) to pipeline
- [ ] Return real `RawDataSource` objects from pipeline results
- [ ] Handle pipeline errors gracefully
- [ ] Add logging for enrichment attempts and results

**Implementation:**
```python
# In eneve_enrichment_integration.py

async def _enrich_company(self, company_data: dict) -> list[RawDataSource]:
    """Enrich company data using real enrichment pipeline."""
    try:
        result = await self.pipeline.enrich(
            company_id=company_data.get("company_name", ""),
            company_name=company_data.get("company_name", ""),
            website=company_data.get("website"),
            industry=company_data.get("industry"),
        )
        
        if result and result.sources:
            logger.info(f"Enriched {company_data['company_name']} with {len(result.sources)} sources")
            return result.sources
        else:
            logger.warning(f"No enrichment data for {company_data['company_name']}")
            return []
            
    except Exception as e:
        logger.error(f"Enrichment failed for {company_data['company_name']}: {e}")
        return []
```

---

### Story 3.2: Configure API Keys for Enrichment Sources
**Priority:** P0 | **Effort:** 3 points

**Description:**
Set up API key configuration for all enrichment sources with fallback behavior.

**Acceptance Criteria:**
- [ ] LinkedIn API key configurable via `LINKEDIN_API_KEY`
- [ ] Crunchbase API key configurable via `CRUNCHBASE_API_KEY`
- [ ] News API key configurable via `NEWS_API_KEY`
- [ ] Patent API key configurable via `PATENT_API_KEY` (optional)
- [ ] Graceful degradation when keys are missing
- [ ] Document all required API keys in README
- [ ] Add validation that at least one enrichment source is available

**Configuration:**
```python
# In config.py
class EnrichmentSettings(BaseSettings):
    linkedin_api_key: str = ""
    crunchbase_api_key: str = ""
    news_api_key: str = ""
    patent_api_key: str = ""
    
    @property
    def has_any_enrichment(self) -> bool:
        return any([
            self.linkedin_api_key,
            self.crunchbase_api_key,
            self.news_api_key,
        ])
```

---

### Story 3.3: Implement Enrichment Fallback Mechanisms
**Priority:** P0 | **Effort:** 3 points

**Description:**
Ensure enrichment works even when primary APIs fail or lack keys by implementing fallback mechanisms.

**Acceptance Criteria:**
- [ ] LinkedIn: Fallback to web scraping if API unavailable
- [ ] Crunchbase: Fallback to news-based funding detection
- [ ] News: Fallback to Google scraping if NewsAPI fails
- [ ] Website: Always attempt scraping (no API key needed)
- [ ] Cache enrichment results to reduce API calls
- [ ] Retry failed requests with exponential backoff

**Implementation:**
```python
# In additional_sources.py

async def get_linkedin_data(self, company_name: str) -> LinkedInData:
    """Get LinkedIn data with fallback to web scraping."""
    # Try API first
    if self.settings.linkedin_api_key:
        try:
            return await self._linkedin_api_call(company_name)
        except Exception as e:
            logger.warning(f"LinkedIn API failed, falling back to scraping: {e}")
    
    # Fallback to web scraping
    return await self._scrape_linkedin(company_name)

async def get_crunchbase_data(self, company_name: str) -> FundingData:
    """Get funding data with fallback to news detection."""
    # Try API first
    if self.settings.crunchbase_api_key:
        try:
            return await self._crunchbase_api_call(company_name)
        except Exception as e:
            logger.warning(f"Crunchbase API failed, falling back to news: {e}")
    
    # Fallback to news-based funding detection
    return await self._detect_funding_from_news(company_name)
```

---

### Story 3.4: Fix Enrichment Source Count Propagation
**Priority:** P0 | **Effort:** 2 points

**Description:**
Fix the data pipeline so enrichment_source_count is correctly propagated from input to output.

**Acceptance Criteria:**
- [ ] Trace enrichment_source_count through entire pipeline
- [ ] Fix any points where count is reset to 0
- [ ] Ensure final output reflects actual enrichment source count
- [ ] Add validation that count matches actual sources list
- [ ] Log discrepancies for debugging

**Investigation Points:**
1. `research/gather.py` line 331: `company.enrichment_source_count = 0`
2. `research/gather.py` line 347: `company.enrichment_source_count = len(raw_sources)`
3. Check if Company model defaults override the count
4. Verify pipeline doesn't create new Company objects that lose the count

**Fix:**
```python
# In research/gather.py
# Don't reset to 0 initially
company.enrichment_source_count = len(raw_sources) if raw_sources else 0

# In domain/models.py - ensure field is preserved
enrichment_source_count: int = Field(default=0, description="Number of enrichment sources used")
```

---

### Story 3.5: Add Enrichment Quality Metrics
**Priority:** P1 | **Effort:** 2 points

**Description:**
Add metrics to track enrichment quality and coverage.

**Acceptance Criteria:**
- [ ] Track enrichment success rate per source
- [ ] Track average enrichment time per company
- [ ] Track API error rates and types
- [ ] Generate enrichment coverage report
- [ ] Alert when enrichment success rate < 80%

**Metrics:**
```python
@dataclass
class EnrichmentMetrics:
    total_companies: int
    enriched_companies: int
    success_rate: float
    avg_sources_per_company: float
    source_breakdown: dict[str, int]  # {"linkedin": 150, "crunchbase": 120, ...}
    avg_enrichment_time_ms: float
    error_count: int
    error_breakdown: dict[str, int]  # {"timeout": 5, "rate_limit": 3, ...}
```

---

### Story 3.6: Implement Enrichment Caching
**Priority:** P1 | **Effort:** 3 points

**Description:**
Cache enrichment results to reduce API calls and improve performance.

**Acceptance Criteria:**
- [ ] Cache enrichment results in Redis/SQLite
- [ ] Cache key: company_name + source_type
- [ ] Cache TTL: 24 hours for volatile data, 7 days for stable data
- [ ] Invalidate cache when manually triggered
- [ ] Show cache hit rate in metrics

**Implementation:**
```python
# In enrichment_pipeline.py

async def enrich(self, company_id: str, **kwargs) -> EnrichmentResult:
    # Check cache first
    cache_key = f"enrichment:{company_id}:{hash(str(kwargs))}"
    cached = await self.cache.get(cache_key)
    if cached:
        logger.debug(f"Cache hit for {company_id}")
        return EnrichmentResult.parse_raw(cached)
    
    # Perform enrichment
    result = await self._perform_enrichment(company_id, **kwargs)
    
    # Cache result
    await self.cache.set(cache_key, result.json(), ttl=86400)
    
    return result
```

---

## Dependencies

- Story 3.1 is the critical fix - must be done first
- Stories 3.2 and 3.3 can be done in parallel with 3.1
- Story 3.4 depends on 3.1
- Stories 3.5 and 3.6 are enhancements (P1)

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| API rate limits | High | Implement caching, backoff, request batching |
| API costs | Medium | Monitor usage, set budgets, use free tiers |
| API keys exposed | High | Use environment variables, never commit keys |
| Enrichment too slow | Medium | Parallel processing, caching, timeouts |
| Data quality issues | Medium | Validation, fallback mechanisms, manual review |

## Definition of Done

- [ ] Real API calls made to enrichment sources
- [ ] Fallback mechanisms working for all sources
- [ ] enrichment_source_count correctly propagated
- [ ] Data quality score calculated from real data
- [ ] Enrichment completes within 30s per company
- [ ] API keys configurable via environment
- [ ] Error handling for all failure modes
- [ ] Metrics and monitoring in place
- [ ] Documentation updated with setup instructions
