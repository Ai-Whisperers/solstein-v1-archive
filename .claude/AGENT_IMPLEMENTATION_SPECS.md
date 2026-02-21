# Agent Implementation Specifications

> **Version**: 1.0  
> **Status**: Technical Specification  
> **Audience**: Developers building new agents

This document specifies EXACTLY what each agent must gather, from which sources, with what confidence levels, and how to handle failures.

---

## Phase 1: Free & High-ROI Agents

### 1. LinkedIn Scraper Agent

**Purpose**: Extract team, leadership, hiring velocity, employee satisfaction

**What It Gathers**:

| Fact Type | Source | Confidence | Effort | Priority |
|-----------|--------|-----------|--------|----------|
| `founder_names` | Company LinkedIn page | 0.98 | Easy | P0 |
| `founder_background` | Founder profiles | 0.92 | Medium | P0 |
| `ceo_name` | Company page | 0.98 | Easy | P0 |
| `ceo_background` | CEO profile | 0.95 | Medium | P0 |
| `cto_name` | Company page | 0.95 | Medium | P1 |
| `cto_background` | CTO profile | 0.93 | Medium | P1 |
| `total_headcount` | Company page (employees) | 0.85 | Easy | P0 |
| `engineering_headcount` | Filter by role | 0.82 | Medium | P1 |
| `headcount_growth_yoy` | Historical snapshots | 0.80 | Hard | P1 |
| `engineering_hiring_velocity` | Recent hires (last 30d) | 0.78 | Medium | P0 |
| `executive_departures_12m` | Activity feed | 0.90 | Medium | P0 |
| `employee_satisfaction_score` | Company reviews | 0.85 | Easy | P1 |
| `employee_reviews_sentiment` | Glassdoor integration | 0.80 | Medium | P1 |

**Implementation Details**:

```python
class LinkedInAgent(BaseDataGatheringAgent):
    """Scrapes LinkedIn for team and hiring data."""
    
    def __init__(self, linkedin_email=None, linkedin_password=None):
        """Initialize with LinkedIn credentials (or use login-in browser)."""
        super().__init__("LinkedInAgent", DataSourceType.LINKEDIN)
        self.email = linkedin_email
        self.password = linkedin_password
        self.driver = None  # Selenium or Playwright
    
    async def gather(self, company_name: str, context: dict) -> AgentTaskResult:
        """Main gathering method."""
        # Step 1: Search for company on LinkedIn
        company_page = await self._search_company(company_name)
        
        # Step 2: Extract company facts
        # Step 3: Get employee list (followers/connections)
        # Step 4: Filter engineering team (by skills, roles)
        # Step 5: Extract hiring trends
        # Step 6: Integrate with Glassdoor for employee satisfaction
        
        return result
```

**API/Auth**:
- **Method**: Selenium/Playwright web scraping (no official API for companies)
- **Rate Limit**: 1 company per 5 seconds (avoid blocking)
- **Auth**: Browser login (store session)
- **Cost**: $0

**Fallback Strategy**:
1. **Primary**: LinkedIn scraping
2. **Fallback 1**: Crunchbase employee list (lower quality)
3. **Fallback 2**: Flag for manual research (analyst)

**Confidence Levels**:
- Employee count: 0.85 (LinkedIn approximate)
- Recent hires: 0.78 (only shows public activity)
- Departures: 0.90 (clear in activity feed)
- Headcount growth: 0.80 (estimates from snapshots)

---

### 2. Crunchbase Free Tier Agent

**Purpose**: Extract funding, investor, company basics

**What It Gathers**:

| Fact Type | Endpoint | Confidence | Notes |
|-----------|----------|-----------|-------|
| `total_funding_raised` | /companies | 0.93 | Sum of all rounds |
| `last_funding_round` | /companies/funding | 0.91 | Most recent round |
| `funding_velocity` | /companies/funding | 0.89 | Months between rounds |
| `investor_reputation` | /investors | 0.92 | Lead investor quality |

**Implementation**:

```python
class CrunchbaseAgent(BaseDataGatheringAgent):
    """Free tier Crunchbase scraping."""
    
    async def gather(self, company_name: str, context: dict) -> AgentTaskResult:
        # 1. Search for company
        company = await self._search_company(company_name)
        
        # 2. Extract funding rounds
        rounds = await self._get_funding_rounds(company['uuid'])
        
        # 3. Extract investor profiles
        investors = await self._get_investors(company['uuid'])
        
        # 4. Calculate metrics (velocity, total raised)
        
        return result
```

**API**:
- **Endpoint**: https://www.crunchbase.com (web scraping)
- **Cost**: Free tier limited, $500/mo for Pro (Phase 2)
- **Rate Limit**: 1 request per 3 seconds
- **Auth**: None (public data)

---

### 3. SEC EDGAR Agent

**Purpose**: Extract financial data (revenue, margins, ratios, insider trades)

**What It Gathers**:

| Fact Type | Form | Confidence | Update Freq |
|-----------|------|-----------|------------|
| `annual_revenue` | 10-K | 0.99 | Annual |
| `quarterly_revenue` | 10-Q | 0.99 | Quarterly |
| `gross_margin` | 10-K | 0.92 | Annual |
| `ebitda_margin` | 10-K | 0.91 | Annual |
| `customer_concentration_top10` | 10-K Item 1A | 0.94 | Annual |
| `debt_to_equity` | 10-K | 0.96 | Annual |
| `cash_position` | 10-Q | 0.96 | Quarterly |
| `insider_buying_selling` | Form 4 | 0.98 | Real-time |

**Implementation**:

```python
class SECEdgarAgent(BaseDataGatheringAgent):
    """SEC EDGAR financial data extraction."""
    
    async def gather(self, company_name: str, context: dict) -> AgentTaskResult:
        # 1. Find CIK number
        cik = await self._get_cik(company_name)
        
        # 2. Fetch latest 10-K (annual)
        filings = await self._get_filings(cik, form_type='10-K')
        
        # 3. Parse 10-K for financial data
        revenue = self._extract_revenue(filings[0])
        margins = self._extract_margins(filings[0])
        
        # 4. Fetch 10-Q (quarterly)
        quarterly = await self._get_filings(cik, form_type='10-Q')
        
        # 5. Fetch Form 4 (insider trades)
        insider_trades = await self._get_insider_trades(cik)
        
        return result
```

**API**:
- **Endpoint**: https://www.sec.gov/cgi-bin/browse-edgar
- **Format**: XBRL (structured), HTML (parse carefully)
- **Cost**: Free
- **Rate Limit**: 10 requests per second
- **Auth**: None

**Parsing Strategy**:
- Use XBRL API for structured data (most reliable)
- Fall back to HTML parsing if XBRL unavailable
- Validate numbers against prior quarters

---

### 4. USPTO Patents Agent

**Purpose**: Extract patents, trademarks, innovation signals

**What It Gathers**:

| Fact Type | Source | Confidence |
|-----------|--------|-----------|
| `number_of_patents` | USPTO search | 0.96 |
| `patent_categories` | Patent classifications | 0.94 |
| `trademark_registrations` | USPTO TESS | 0.95 |

**Implementation**:

```python
class USPTOAgent(BaseDataGatheringAgent):
    """Patent and trademark extraction."""
    
    async def gather(self, company_name: str, context: dict) -> AgentTaskResult:
        # 1. Search USPTO patents
        patents = await self._search_patents(company_name)
        
        # 2. Extract categories (IPC/CPC)
        categories = [p.classifications for p in patents]
        
        # 3. Search trademarks
        trademarks = await self._search_trademarks(company_name)
        
        # 4. Extract filing dates, status
        
        return result
```

**API**:
- **Endpoint**: https://www.uspto.gov (public search)
- **Cost**: Free
- **Rate Limit**: 5 requests per second
- **Auth**: None

---

### 5. News Aggregator Agent

**Purpose**: Real-time announcements, partnerships, funding, exec changes

**What It Gathers** (in real-time):

| Fact Type | Sources | Confidence |
|-----------|---------|-----------|
| `funding_announced_12m` | News sites | 0.94 |
| `strategic_partnerships_announced` | News | 0.88 |
| `product_launches_12m` | News, blog | 0.85 |
| `acquisition_activity` | News | 0.96 |
| `executive_departures_12m` | News | 0.90 |
| `ipo_announcements` | News | 0.98 |

**Implementation**:

```python
class NewsAggregatorAgent(BaseDataGatheringAgent):
    """Real-time news aggregation."""
    
    async def gather(self, company_name: str, context: dict) -> AgentTaskResult:
        # 1. Search across news sources
        sources = ['techcrunch', 'crunchbase_news', 'hacker_news', 'company_website_blog']
        
        results = []
        for source in sources:
            articles = await self._search_news(company_name, source, lookback=365)
            results.extend(articles)
        
        # 2. Classify by topic (funding, acquisition, partnership, exec change)
        classified = await self._classify_articles(results)
        
        # 3. Extract key facts from articles
        facts = await self._extract_facts(classified)
        
        return result
```

**Sources**:
- Techcrunch API
- Crunchbase News (free tier)
- Hacker News API
- Company website blog RSS
- Google News RSS

**Cost**: Free

---

### 6. Job Postings Scraper Agent

**Purpose**: Extract hiring velocity, team expansion, skills in demand

**What It Gathers**:

| Fact Type | Source | Confidence |
|-----------|--------|-----------|
| `engineering_hiring_velocity` | LinkedIn, Indeed, Wellfound | 0.75 |
| `sales_hiring_velocity` | Same | 0.75 |
| `total_open_positions` | LinkedIn | 0.82 |
| `job_level_distribution` | Job descriptions | 0.78 |

**Implementation**:

```python
class JobPostingsAgent(BaseDataGatheringAgent):
    """Job postings analysis for hiring trends."""
    
    async def gather(self, company_name: str, context: dict) -> AgentTaskResult:
        # 1. Scrape LinkedIn jobs (advanced search)
        linkedin_jobs = await self._scrape_linkedin_jobs(company_name)
        
        # 2. Scrape Indeed
        indeed_jobs = await self._scrape_indeed(company_name)
        
        # 3. Scrape Wellfound (startup jobs)
        wellfound_jobs = await self._scrape_wellfound(company_name)
        
        # 4. Classify by role (engineering, sales, operations, etc)
        by_role = self._classify_by_role(linkedin_jobs + indeed_jobs + wellfound_jobs)
        
        # 5. Calculate hiring velocity (jobs / month)
        
        return result
```

**Cost**: Free

---

### 7. Google Trends Agent

**Purpose**: Search volume trends, market interest

**What It Gathers**:

| Fact Type | Metric | Confidence |
|-----------|--------|-----------|
| `search_volume_trend` | Search volume over time | 0.85 |
| `search_vs_competitors` | Relative search volume | 0.88 |

**Implementation**: Use `pytrends` library

---

### 8. Website Intelligence Agent

**Purpose**: Tech stack, domain history, company info

**What It Gathers**:

| Fact Type | Source | Confidence |
|-----------|--------|-----------|
| `primary_programming_language` | Website source code | 0.88 |
| `tech_stack` | BuiltWith, Wappalyzer | 0.93 |
| `cloud_provider` | DNS/IP analysis | 0.90 |
| `domain_age` | WHOIS | 0.98 |
| `ssl_certificate_info` | SSL analysis | 0.98 |

**Implementation**:

```python
class WebsiteIntelligenceAgent(BaseDataGatheringAgent):
    """Website and domain intelligence."""
    
    async def gather(self, company_name: str, context: dict) -> AgentTaskResult:
        # 1. Resolve company domain
        domain = context.get('domain') or await self._find_domain(company_name)
        
        # 2. Analyze tech stack (BuiltWith API or Wappalyzer)
        tech_stack = await self._get_tech_stack(domain)
        
        # 3. Check domain age (WHOIS)
        domain_info = await self._get_domain_info(domain)
        
        # 4. Analyze SSL certificate
        ssl_info = await self._get_ssl_info(domain)
        
        # 5. Crawl website for company info
        website_content = await self._crawl_website(domain)
        
        return result
```

**Cost**: Free (BuiltWith has free tier)

---

## Phase 2: Low-Cost Agents (Coming Soon)

Detailed specs for:
- Crunchbase Pro
- Glassdoor API
- G2 Reviews API
- Tech Stack Detector (paid)
- Uptime Monitoring

---

## Phase 3: Enterprise Agents (Coming Soon)

Detailed specs for:
- PitchBook API
- CapitalIQ
- FactSet
- LinkedIn Enterprise API
- Social Sentiment APIs

---

## Agent Base Class Interface

All agents must implement this interface:

```python
class BaseDataGatheringAgent:
    """Abstract base class for all data gathering agents."""
    
    async def gather(
        self, 
        company_name: str, 
        context: dict
    ) -> AgentTaskResult:
        """
        Gather facts about a company.
        
        Args:
            company_name: Name of company to analyze
            context: Dict with hints (industry, known_github_org, domain, etc)
        
        Returns:
            AgentTaskResult with:
            - success: bool
            - raw_sources: List[RawDataSource]
            - extracted_facts: List[ExtractedFact]
            - execution_time_seconds: float
            - coverage_gaps: List[str]
            - errors: List[str]
        """
        pass
    
    def _create_raw_source(
        self,
        raw_content: dict,
        source_name: str,
        url: str = None,
        confidence: float = 0.0,
        extraction_method: str = "",
        metadata: dict = None,
    ) -> RawDataSource:
        """Create a raw data source."""
        pass
    
    def _create_fact(
        self,
        fact_type: str,
        value: str,
        confidence: float,
        sources_used: List[str],
    ) -> ExtractedFact:
        """Create an extracted fact."""
        pass
```

---

## Error Handling & Fallback

Every agent MUST implement error handling:

```python
async def gather(self, company_name: str, context: dict) -> AgentTaskResult:
    result = AgentTaskResult(agent_name=self.agent_name, source_type=self.source_type)
    
    try:
        # Primary approach
        data = await self._primary_method(company_name)
    except PrimaryException as e:
        self.log_warning(f"Primary method failed: {e}")
        
        try:
            # Fallback 1
            data = await self._fallback_method_1(company_name)
        except FallbackException as e:
            self.log_warning(f"Fallback 1 failed: {e}")
            
            # Fallback 2 or mark as gap
            result.coverage_gaps.append("Primary data source unavailable")
            result.success = True  # Partial success
            return result
    
    # Process data...
    result.success = True
    return result
```

---

## Testing Strategy

Each agent MUST pass:

1. **Unit Tests**: Single company, mock API
2. **Integration Tests**: Real API (rate-limited)
3. **Regression Tests**: Known companies, validate output stability
4. **Performance Tests**: Execution time < 10 seconds per company
5. **Reliability Tests**: 99%+ uptime, graceful degradation

