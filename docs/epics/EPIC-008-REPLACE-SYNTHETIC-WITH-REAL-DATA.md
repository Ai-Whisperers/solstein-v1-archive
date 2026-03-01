# EPIC-008: Replace Synthetic Data with Real Competitive Data

## Status: 🔴 CRITICAL
## Priority: P0 - System Blocking
## Effort: 13 story points
## Sprint: Required for production viability

---

## Problem Statement

**196 out of 199 companies (98.5%) are synthetic generated data**, not real competitive intelligence. This makes the system unsuitable for actual investment decisions.

### Current State
- Real companies: 3 (Eneve, Test Company 2, Test Company 3)
- Synthetic companies: 196
- **Real data ratio: 1.5%**

### Impact
- **No actual competitive intelligence**
- **Investment decisions based on fiction**
- **System cannot be used for real PE/VC analysis**
- **Complete lack of credibility**

---

## Success Criteria

- [ ] Replace 196 synthetic companies with real competitive data
- [ ] Minimum 80% real data ratio (160/200 companies)
- [ ] Real data includes: revenue, employees, funding, growth metrics
- [ ] Data sourced from reliable public sources
- [ ] Data validated for accuracy
- [ ] Enrichment applied to real companies
- [ ] System produces actionable competitive intelligence

---

## Technical Analysis

### Data Sources to Integrate
1. **Crunchbase** - Funding, valuation, employee count
2. **LinkedIn** - Employee count, job postings, company info
3. **Company websites** - Product info, customer logos, pricing
4. **News sources** - Growth signals, partnerships, acquisitions
5. **Industry reports** - Market size, competitive positioning
6. **Public filings** - Revenue (for public companies)

### Data Collection Strategy
- **Batch collection** via APIs
- **Web scraping** for public information
- **Manual curation** for top 20-30 competitors
- **Third-party data providers** (ZoomInfo, PitchBook, etc.)

---

## Stories

### Story 8.1: Design Real Data Collection Pipeline
**Priority:** P0 | **Effort:** 3 points

**Description:**
Design the architecture for collecting real competitive data at scale.

**Acceptance Criteria:**
- [ ] Identify target data sources (Crunchbase, LinkedIn, etc.)
- [ ] Design API integration architecture
- [ ] Define data schema for real companies
- [ ] Design rate limiting and error handling
- [ ] Plan data validation and quality checks
- [ ] Document data collection workflow

**Architecture:**
```
Data Collection Pipeline:
├── Source: Crunchbase API
│   ├── Funding rounds
│   ├── Valuation
│   └── Employee count
├── Source: LinkedIn API
│   ├── Employee count
│   ├── Job postings
│   └── Company description
├── Source: Web Scraping
│   ├── Website content
│   ├── Pricing pages
│   └── Customer logos
├── Source: News APIs
│   ├── Growth signals
│   ├── Partnerships
│   └── Funding announcements
└── Validation Layer
    ├── Data quality checks
    ├── Outlier detection
    └── Confidence scoring
```

---

### Story 8.2: Implement Crunchbase Data Integration
**Priority:** P0 | **Effort:** 5 points

**Description:**
Integrate Crunchbase API to collect funding, valuation, and employee data.

**Acceptance Criteria:**
- [ ] Crunchbase API client implemented
- [ ] Extract funding rounds and total funding
- [ ] Extract valuation data
- [ ] Extract employee count
- [ ] Extract company description and website
- [ ] Handle API errors and rate limits
- [ ] Cache results to reduce API calls

**Implementation:**
```python
class CrunchbaseClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.crunchbase.com/v4"
    
    async def get_company(self, company_name: str) -> dict:
        """Fetch company data from Crunchbase."""
        url = f"{self.base_url}/entities/organizations/{company_name}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_company_data(data)
                else:
                    logger.error(f"Crunchbase API error: {response.status}")
                    return None
    
    def _parse_company_data(self, data: dict) -> dict:
        """Parse Crunchbase response into standard format."""
        return {
            "company_name": data["properties"]["name"],
            "funding_raised": data["properties"].get("funding_total", {}).get("value", 0),
            "valuation": data["properties"].get("valuation", {}).get("value", 0),
            "employees": data["properties"].get("num_employees_enum"),
            "website": data["properties"].get("website"),
            "description": data["properties"].get("description"),
        }
```

---

### Story 8.3: Implement LinkedIn Data Integration
**Priority:** P0 | **Effort:** 5 points

**Description:**
Integrate LinkedIn API (or scraping) to collect employee and company data.

**Acceptance Criteria:**
- [ ] LinkedIn API or scraping client implemented
- [ ] Extract employee count
- [ ] Extract company description
- [ ] Extract industry and specialties
- [ ] Extract job postings (growth signal)
- [ ] Handle authentication and rate limits
- [ ] Cache results

**Note:** LinkedIn API has strict limitations. May need to use:
- LinkedIn Sales Navigator API (expensive)
- Web scraping (fragile)
- Proxy services (Proxycurl, etc.)

---

### Story 8.4: Build Data Validation Pipeline
**Priority:** P0 | **Effort:** 3 points

**Description:**
Build validation to ensure collected data is accurate and consistent.

**Acceptance Criteria:**
- [ ] Validate revenue is within reasonable range
- [ ] Validate employee count matches company size
- [ ] Validate funding rounds are chronological
- [ ] Detect outliers and flag for review
- [ ] Cross-validate data from multiple sources
- [ ] Generate data quality report

**Validation Rules:**
```python
VALIDATION_RULES = {
    "revenue": {
        "min": 0,
        "max": 1_000_000,  # €1B
        "outlier_threshold": 3.0,  # Standard deviations
    },
    "employees": {
        "min": 1,
        "max": 100_000,
        "outlier_threshold": 3.0,
    },
    "funding_raised": {
        "min": 0,
        "max": 10_000_000_000,  # $10B
        "outlier_threshold": 3.0,
    },
    "growth_rate": {
        "min": -100,
        "max": 1000,  # 1000%
        "outlier_threshold": 2.5,
    },
}

def validate_company_data(company: dict) -> list[str]:
    """Validate company data and return list of issues."""
    issues = []
    
    for field, rules in VALIDATION_RULES.items():
        value = company.get(field)
        if value is None:
            continue
        
        if value < rules["min"] or value > rules["max"]:
            issues.append(f"{field}={value} outside valid range [{rules['min']}, {rules['max']}]")
    
    # Cross-validation
    if company.get("funding_raised", 0) > company.get("valuation", float('inf')):
        issues.append("Funding > valuation (unusual)")
    
    return issues
```

---

### Story 8.5: Create Manual Curation Workflow
**Priority:** P1 | **Effort:** 3 points

**Description:**
Create workflow for manually curating top 20-30 most important competitors.

**Acceptance Criteria:**
- [ ] Identify top 20-30 competitors in energy software space
- [ ] Research and manually input data for each
- [ ] Validate data accuracy
- [ ] Document data sources for each company
- [ ] Set up review process for data updates

**Top Competitors to Research:**
1. Established players (Siemens, GE, Schneider Electric)
2. Growth-stage companies (Octopus Energy, Tesla Energy)
3. Emerging startups (identified from Crunchbase, PitchBook)
4. Regional competitors (European energy software companies)

---

### Story 8.6: Implement Data Refresh Schedule
**Priority:** P1 | **Effort:** 2 points

**Description:**
Implement automated data refresh to keep competitive intelligence current.

**Acceptance Criteria:**
- [ ] Schedule quarterly data refresh
- [ ] Track data freshness (last_updated field)
- [ ] Alert when data is > 90 days old
- [ ] Incremental updates (only changed data)
- [ ] Version control for historical data

**Implementation:**
```python
async def refresh_company_data(company_id: str) -> bool:
    """Refresh data for a single company."""
    company = await load_company(company_id)
    
    # Check if refresh needed
    if company.last_updated and (datetime.now() - company.last_updated).days < 90:
        logger.info(f"Skipping refresh for {company.name} (data is fresh)")
        return False
    
    # Collect fresh data
    fresh_data = await collect_company_data(company.name)
    
    # Validate and update
    issues = validate_company_data(fresh_data)
    if issues:
        logger.warning(f"Validation issues for {company.name}: {issues}")
    
    company.update(fresh_data)
    company.last_updated = datetime.now()
    await save_company(company)
    
    return True
```

---

## Dependencies

- Story 8.1 must be done first (architecture)
- Stories 8.2 and 8.3 can be done in parallel
- Story 8.4 should be done alongside 8.2-8.3
- Story 8.5 can be done in parallel with technical stories
- Story 8.6 is enhancement (P1)

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| API costs too high | High | Use free tiers, cache aggressively, prioritize |
| Data quality issues | High | Validation pipeline, manual review |
| API rate limits | Medium | Implement backoff, distribute requests |
| Legal issues with scraping | Medium | Use official APIs, respect robots.txt |

## Definition of Done

- [ ] Real data ratio > 80% (160/200 companies)
- [ ] Data validation passing for all companies
- [ ] Crunchbase integration working
- [ ] LinkedIn integration working (or alternative)
- [ ] Manual curation complete for top 30
- [ ] Data refresh schedule implemented
- [ ] Documentation complete for data sources
