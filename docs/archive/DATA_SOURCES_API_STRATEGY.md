# 📊 Solstein Data Sources & API Strategy

**Smart, Graduated Approach: Free → Paid as Quality Demands Increase**

---

## Executive Summary

**Phase 1-3 (Rounds 1-3): Free/Open Sources Only**
- Use GitHub API (free, 60 requests/hour unauthenticated, 5,000/hour authenticated)
- Google Custom Search (free tier: 100 queries/day)
- Web scraping (BeautifulSoup, Selenium)
- Companies House (free UK filings API)
- Public Crunchbase data (limited, but free)
- Results: ~70-80% accuracy, good enough for pilot validation

**Phase 4+ (Paid APIs):**
- Crunchbase Pro ($500-2000/month) → 90-95% coverage, better data freshness
- PitchBook ($10k+/year) → institutional-grade data, M&A intel
- LinkedIn Recruiter Lite ($$$) → hiring signals
- Results: 95%+ accuracy, enterprise-grade, justifiable for paying clients

**Why This Matters**: First 3 clients validate the model with free sources (costs you almost nothing in data). By Round 4, client is paying EUR 60k+ pilot, so you can spend $500/month on APIs and still have 99% margin.

---

## Part 1: Free Data Sources (Rounds 1-3)

### 1.1 GitHub API
**Cost**: FREE (public), $25/month for private repos (optional)  
**Rate Limit**: 60 req/hour (public), 5,000 req/hour (authenticated)  
**Quality**: ⭐⭐⭐⭐ (95% confidence for engineering signals)  
**Use For**: Tech stack, engineering velocity, AI/ML hiring intent, code quality

**Best Practices**:
```python
# Register a GitHub App (free) → get 5,000 req/hour
# Search for company org repos:
GET https://api.github.com/search/repositories
  ?q=org:{company_name}+is:public
  
# Get commits, languages, contributors:
GET https://api.github.com/repos/{org}/{repo}/stats/commit_activity
GET https://api.github.com/repos/{org}/{repo}/languages
GET https://api.github.com/repos/{org}/{repo}/contributors
```

**Energy Software Example**:
```
Company: Octopus Energy / Kraken Technologies
GitHub Org: kraken-io

Facts Extractable:
✓ Latest commit timestamp (code freshness)
✓ Commit frequency (velocity)
✓ Language distribution (tech stack)
✓ Stars/watchers (community adoption)
✓ Open issues/PRs (roadmap transparency)
✓ Contributor count (team size proxy)

Signal Extracted:
- "48 commits in last week" → Active development
- "TypeScript 45%, Python 30%" → Modern stack
- "120 active contributors" → Growing team
- 0 archived repos → Not dead code

Confidence: 0.95 (GitHub is ground truth for open source)
Cost: FREE
```

### 1.2 Google Custom Search API
**Cost**: FREE (100 queries/day), or $100/month (10k queries/day)  
**Rate Limit**: 100/day free, 10,000/day paid  
**Quality**: ⭐⭐⭐ (70% confidence — mixed sources)  
**Use For**: News, press releases, company announcements, founding info

**Best Practices**:
```python
# Create a Custom Search Engine (free) → search business news only
# Queries to run per company:
1. "{company} Series A B C funding" 
2. "{company} acquisition merger"
3. "{company} hiring machine learning AI"
4. "{company} annual report revenue"
5. "{company} founders CEO"

# Extract from top 10 results:
- Publication date (freshness)
- Domain reputation (Reuters > TechCrunch > Random Blog)
- Mentioned facts (funding amount, dates, quotes)
```

**Energy Software Example**:
```
Company: Previse Systems AG
Search: "Previse Systems funding Germany"

Results:
1. crunchbase.com - "Series B €6.5M, May 2023"
2. eu-startups.com - "Series B €6.5M raised by German energy startup"
3. linkedin.com - Founder announcement of Series B
4. pitchbook.com - "$7.5M Series B equivalent"

Facts Extracted:
- Funding: €6.5-7.5M (range indicates uncertainty)
- Year: 2023 (confirmed in multiple sources)
- Round: Series B

Confidence: 0.82 (sources mostly agree, but one outlier)
  - Two sources say €6.5M (weight: 0.6)
  - One source says $7.5M equivalent (weight: 0.2) — might be dated exchange rate
  - Agreement: 90% (minor variance)

Cost: FREE (100 searches used, 900 remaining today)
```

### 1.3 Companies House API (UK)
**Cost**: FREE  
**Rate Limit**: Unlimited (reasonable use)  
**Quality**: ⭐⭐⭐⭐⭐ (99% confidence)  
**Use For**: UK company financials, legal structure, M&A history, official records

**Best Practices**:
```python
# UK Companies House API (totally free):
GET https://api.company-information.service.gov.uk/company/{company_number}

# Returns:
- Company name, address, status
- Directors (names, dates of birth — useful for diligence)
- Incorporation date
- SIC codes (business classification)
- Accounts filed (most recent financial data)

# Get financial data:
GET https://api.company-information.service.gov.uk/company/{company_number}/filing-history

# You then fetch PDF reports and extract:
- Revenue
- Profit/Loss
- Number of employees
- Loans (leverage)
```

**Energy Software Example**:
```
Company: Octopus Energy Group plc
Companies House Number: 11014436

API Returns:
{
  "company_name": "Octopus Energy Group Limited",
  "incorporation_date": "2015-12-21",
  "status": "active",
  "directors": [
    {
      "name": "Greg Jackson",
      "date_of_birth": "1985-03",
      "appointment_date": "2015-12-21"
    },
    ...
  ],
  "accounts": [
    {
      "filing_date": "2024-12-31",
      "filed_date": "2025-01-15",
      "type": "full-accounts"
    }
  ]
}

Download & Parse Filing:
- FY2024 Revenue: £14,500,000,000
- Number of employees: 8,500
- Profit before tax: £450,000,000

Confidence: 0.99 (official filing)
Cost: FREE
```

### 1.4 LinkedIn Company Data (via Scraping)
**Cost**: FREE (browser-based scraping)  
**Rate Limit**: Scrape carefully (1 request per 3 seconds max)  
**Quality**: ⭐⭐⭐⭐ (85% confidence, real-time employee count)  
**Use For**: Employee count (current), company size, recent updates

**Best Practices** (legal/ethical):
```python
# Use Selenium + BeautifulSoup to scrape public LinkedIn Company Page
# NO private API (violates ToS)
# Public pages: fine to scrape

import selenium
from bs4 import BeautifulSoup

driver = selenium.webdriver.Chrome()
driver.get(f"https://www.linkedin.com/company/{company_slug}")

# Extract:
- Company followers
- Employee count (LinkedIn shows "7,850–8,500 employees")
- Company description
- Website
- Recent company posts (count = activity proxy)
- Open job postings (hiring velocity)

# Be respectful: 1 request per 3 seconds, user-agent rotation
```

**Energy Software Example**:
```
Company: Kraken Technologies (subsidiary of Octopus Energy)
LinkedIn Page: linkedin.com/company/kraken-technologies

Scraped Data:
- Employee count: "7,650–8,850 employees" (last 90 days)
- Recent hire growth: +2,200 in past 12 months (LinkedIn median)
- Job posts (last 30d): 127 open positions
- Company updates (last 7d): 8 posts (high activity)

Extracted Signals:
- Growth rate: 2200/6300 = 35% YoY (consistent with revenue growth)
- Hiring velocity: 127 / 30 days = 4.2 hires/day
- Activity level: "Very Active" (8 posts/week on LinkedIn)

Confidence: 0.82 (LinkedIn data is real-time but ranges shown, not exact)
Cost: FREE
```

### 1.5 Patent Databases (Free)
**Cost**: FREE  
**Sources**: USPTO (US), WIPO (World), EPO (Europe), Google Patents  
**Quality**: ⭐⭐⭐ (75% confidence — not all companies patent)  
**Use For**: Innovation signal, AI research investment, technical differentiation

**Best Practices**:
```python
# Google Patents (totally free, best UI):
# Search: "{company_name} AI machine learning"
# Returns: All patents assigned to company

# API Option (WIPO PatentScope - free):
GET https://patentscope.wipo.int/search/en/search.jsf
  ?query={company_name}&referenceNo=&scope=EVERYTHING
```

**Energy Software Example**:
```
Company: Kraken Technologies / Octopus Energy
Patent Search: "Kraken Technologies AI demand forecasting"

Results:
- Patent US11123456: "Machine Learning Model for Energy Demand Prediction" (2023)
- Patent EP4123456: "Distributed AI Architecture for Energy Management" (2024)
- Patent GB2123456: "Real-time Anomaly Detection in Power Grid" (2024)

Facts Extracted:
- 3 AI-related patents filed in past 2 years (active R&D)
- Filed in US, Europe, UK (global IP strategy)
- Timing: 2023-2024 (very recent = serious AI investment)

Signal: "Strong AI investment → expect high GitHub activity + hiring"

Confidence: 0.88 (Patents are strong signal, but only if filed)
Cost: FREE
```

### 1.6 News Aggregators (Free)
**Cost**: FREE  
**Sources**: NewsAPI, Bing News Search, DuckDuckGo News  
**Quality**: ⭐⭐⭐ (70% — dependent on reporter quality)  
**Use For**: Recent news, market movements, M&A rumors, executive changes

**Best Practices**:
```python
# NewsAPI.org (3,000 requests/month free):
import requests

response = requests.get(
  'https://newsapi.org/v2/everything',
  params={
    'q': 'Octopus Energy Kraken funding',
    'sortBy': 'publishedAt',
    'language': 'en',
    'apiKey': 'YOUR_KEY'
  }
)

# Returns: Articles with title, description, source, published date, URL

# For each article, extract:
- Publication date (newness)
- Source domain (credibility)
- Mentioned facts (funding, hiring, products)
- Sentiment (positive/negative tone)
```

**Energy Software Example**:
```
Query: "Kraken Technologies funding 2025"
Results (3 articles found):

1. TechCrunch (2025-02-15): "Kraken Technologies raises $1B at $8.65B valuation"
   → Fact: Funding $1B, valuation $8.65B
   → Confidence: 0.95 (TechCrunch is reputable, specific numbers)

2. Bloomberg (2025-02-15): "Kraken Technologies closes $1 billion funding round"
   → Fact: Funding $1B (confirms #1)
   → Confidence: 0.97 (Bloomberg is authoritative)

3. Random Blog (2025-02-16): "Kraken Technologies raises $1.2B, plans IPO by 2026"
   → Fact: Funding $1.2B (conflicts with $1B)
   → Confidence: 0.45 (blog is unreliable, number differs)

Aggregated Fact:
- Funding: $1B (sources 1 & 2 agree, source 3 is outlier)
- Confidence: 0.95 (TechCrunch + Bloomberg consensus)
- IPO rumors: Note source #3 mentioned it, but unconfirmed

Cost: FREE (3000/month used)
```

### 1.7 Public Databases (Free)
**Cost**: FREE  
**Sources**: Crunchbase free tier, AngelList, OpenCorporates  
**Quality**: ⭐⭐⭐ (70% — crowd-sourced)  
**Use For**: Founding info, investor history, employee directory (partial)

**Best Practices**:
```python
# Crunchbase has FREE data (limited):
# - Company profiles (basic info)
# - Funding rounds (summary, not detailed)
# - Investor information
# - Jobs (some company hiring info)

# OpenCorporates (totally free):
# - Legal entity searches across 500M companies
# - Ownership structures, directors
# - Good for international companies

# AngelList (free tier):
# - Startup data
# - Founder profiles
# - Investor connections
```

**Energy Software Example**:
```
Company: Previse Systems AG
Crunchbase Free Search: "Previse Systems"

Results:
- Founded: 2018, Germany
- Founders: [3 listed]
- Funding: €6.5M Series B (2023), €2.1M Series A (2020)
- Investors: [list of VCs]
- Website: previse.de

Confidence: 0.75 (Crunchbase free is crowd-sourced, may have gaps)
Cost: FREE
```

---

## Part 2: Paid Data Sources (Round 4+)

### 2.1 Crunchbase Pro/Max
**Cost**: $500/month (Pro), $2,000/month (Max)  
**Quality**: ⭐⭐⭐⭐⭐ (95% confidence)  
**What It Adds**: Detailed funding intel, verified data, M&A pipeline, executive moves

**Why Worth It**:
```
Round 1-3 (Free):
- Funding: "€6.5M Series B, 2023"
- Accuracy: 70%

Round 4+ (Crunchbase Pro, $500/month):
- Funding: "€6.5M Series B (May 2023, Lead: Lowercarbon Capital, Participants: XYZ)"
- Lead investor follow-on history
- Burn rate estimates
- Next funding timeline prediction
- Accuracy: 95%

Cost-Benefit:
- If managing 10 PE clients paying EUR 75k/year subscription
- EUR 750k/year revenue
- Crunchbase: $500/month × 12 = $6k/year = 0.8% of revenue
- Quality improvement: 70% → 95%
→ Worth it.
```

### 2.2 PitchBook
**Cost**: $10,000/year + data licenses  
**Quality**: ⭐⭐⭐⭐⭐ (98% confidence)  
**What It Adds**: Institutional-grade M&A data, exit multiples, comp analysis, transaction history

**Why Worth It** (after proven pilot success):
```
You're now selling to 10+ PE clients at EUR 150k/year each
You need institutional-grade data to justify premium pricing
PitchBook gives you:
- Complete M&A history (all deals, prices, advisors)
- Exit multiples by sector
- Comparable company analysis
- Investor track records

PitchBook cost: $10k/year
Revenue impact: Allows you to charge EUR 150k instead of EUR 75k → +EUR 75k upside
→ 7.5x ROI
```

### 2.3 LinkedIn Recruiter (Optional)
**Cost**: $500-2,000/month (Recruiter Lite)  
**Quality**: ⭐⭐⭐⭐ (90% confidence)  
**What It Adds**: Executive moves, hiring trends, competitive hiring patterns

**When to Use**: 
- If analyzing hiring velocity is critical
- If you want to detect executive departures (CEO turnover = risk signal)
- Only for top prospects (worth the cost)

---

## Part 3: Recommendation Matrix

### When to Use FREE (Rounds 1-3)
| Data Type | Free Source | Confidence | Use Case |
|-----------|------------|-----------|----------|
| Tech Stack | GitHub API | 95% | Always use GitHub first |
| News/Press | Google Custom Search + NewsAPI | 70% | Validate with official sources |
| UK Financials | Companies House API | 99% | Only source for UK companies |
| Employee Count | LinkedIn scraping | 82% | Current staffing, not historical |
| Patents | Google Patents | 88% | Innovation signal only |
| Funding (initial) | Crunchbase free tier | 70% | Get rough amounts, then verify |
| Company Info | OpenCorporates | 85% | Verify legal structure |

### When to Upgrade to PAID (Round 4+)
| Data Type | Paid Source | Confidence | Justification |
|-----------|------------|-----------|---------------|
| Detailed Funding | Crunchbase Pro | 95% | Client willing to pay for accuracy |
| M&A History | PitchBook | 98% | Enterprise feature → premium pricing |
| Exit Multiples | PitchBook | 98% | Justifies premium pricing tier |
| Hiring Trends | LinkedIn Recruiter | 90% | Competitive intelligence |

---

## Part 4: Data Gathering Workflow by Round

### Round 1: Pilot (Free, Jan-Feb 2025)
```
Client: PE Firm (Energy Software Market, 29 companies)
Budget: EUR 60k (validation pilot)
Data Sources: 100% FREE
Timeline: 1-2 weeks

Agents Used:
1. GitHub: 100% coverage (all 29 have repos or none)
2. Google Search: 100% queries (3000 queries/month budget)
3. Companies House: 15/29 UK-based companies
4. LinkedIn: 29/29 company pages
5. Patents: Best effort (10-15/29 have patents)

Data Quality:
- Revenue: 70% complete (news + filings)
- Tech Stack: 95% complete (GitHub)
- Employee Count: 85% complete (LinkedIn)
- Funding: 60% complete (Crunchbase free + news)
- AI Maturity: 90% complete (GitHub + news)

Cost: ~$0 (APIs free, time investment ~40 hours)
Revenue: EUR 60k
Margin: 100%

Decision Point: Did we match or exceed manual analysis quality?
- YES → Proceed to Round 2
- NO → Adjust methodology, try again
```

### Round 2: Validation (Free, Mar 2025)
```
Client: 2nd PE Firm (Building Automation Market, 35 companies)
Budget: EUR 60k
Data Sources: 100% FREE (same as Round 1)
Timeline: 1-2 weeks

Goal: Prove repeatability. Can we do this for ANY market, not just energy?

Learning:
- Building automation has fewer GitHub repos (different industry)
- More patent filers (safety/certification industry)
- More private companies (harder to find data)

Adjustments:
- Increase patent search weight
- Add SEC EDGAR for US companies
- Add patent examiner interviews (if possible)

Result: 80% data completion (slightly lower than energy, but acceptable)
```

### Round 3: Refinement (Free, Apr 2025)
```
Client: 3rd PE Firm (SaaS Market, 25 companies)
Budget: EUR 75k (you're increasing price as you gain confidence)
Data Sources: 100% FREE
Timeline: 1-2 weeks

Goal: Optimize the free workflow to near-perfection

By Round 3, you should have:
- Tuned search queries
- Known data gaps by market
- Fallback strategies
- 85-90% data completion across diverse markets
- 4-5 repeat clients by now (cumulative revenue: EUR 195k)

Cost: Still $0 in APIs
Margin: 100%
```

### Round 4: Premium Upgrade (Paid APIs, May 2025)
```
Client: 4th PE Firm (European Energy Software, 40 companies)
Budget: EUR 150k (premium tier)
Data Sources: FREE + Crunchbase Pro ($500/month)
Timeline: 1-2 weeks

Why Crunchbase Pro Now?
- You have 3 successful pilots (de-risks the investment)
- Client paying 2.5x more → expects better data
- Crunchbase Pro gives you:
  - Verified funding rounds (no guessing)
  - Investor track records
  - Burn rate estimates
  - Better M&A data

Data Quality:
- Revenue: 95% complete (verified sources)
- Funding: 98% complete (Crunchbase Pro)
- M&A History: 95% complete (Crunchbase Pro)
- Employee Growth: 90% complete (verified trends)

Cost: Crunchbase Pro = $500/month × (let's say 2 months = $1000)
Revenue: EUR 150k
Margin: 99.3% (Crunchbase cost is <1%)

New Capability: You can now offer "M&A Opportunities" analysis
(Which companies are acquisition targets? Which are buyers?)
→ Sell additional premium features
```

### Round 5+ (Continuous, Crunchbase + PitchBook)
```
Once you have 5+ customers paying EUR 150k/year each:
- Total revenue: EUR 750k/year
- Crunchbase/month: $500
- Add PitchBook: $10k/year
- Total data cost: $16k/year = 2% of revenue

PitchBook enables new products:
1. "M&A Valuation Analysis" → Tell PE firm what this company should be worth
2. "Exit Opportunity Assessment" → Which companies are acquisition targets?
3. "Competitive Exit Scenarios" → How do exits work in this sector?

These new products can be sold as EUR 25k-50k add-ons.
```

---

## Part 5: Cost Progression

```
Phase    Clients  Avg Price  Revenue   Data Cost  Margin  API Stack
─────────────────────────────────────────────────────────────────────
Rounds 1-3   3    EUR 65k   EUR 195k     $0     100%    Free only
Round 4      1    EUR 150k  EUR 150k    $1k     99%    Free + Crunchbase
Rounds 5-8   5    EUR 150k  EUR 750k   $16k    98%    Free + Crunchbase + PitchBook
Round 9+    10+   EUR 150k+ EUR 1.5M+  $20k    98%    Full stack
```

---

## Part 6: Implementation Strategy for YOU

### Immediate Action (Today - Week 1)
1. **Set up free APIs**:
   - GitHub API (OAuth app)
   - Google Custom Search (free tier)
   - Companies House API (no setup needed)
   
2. **Build agent for free sources**:
   - Web Search Agent (Google Custom Search)
   - GitHub Agent (free API)
   - Companies House Agent
   - LinkedIn scraper

3. **Test with one company**: Pick Octopus Energy, run all free agents, see what we get

### Phase 1 Deliverable (Week 1-2)
- ✅ All 5 free-source agents working
- ✅ One pilot company (Octopus) fully analyzed with free data
- ✅ Accuracy: Can you match or beat the manual JSON analysis?

### After Pilot Success (Week 3-4)
- ✅ Run on all 29 energy software companies
- ✅ Compare to manual results
- ✅ Calculate: Free data → 85% accuracy? 90%?
- ✅ If ≥85%: Declare "MVP success", take next client
- ✅ If <85%: Adjust agents, iterate

### When Revenue Justifies Paid APIs (Month 5+)
- At 3-4 clients paying EUR 60-75k each = EUR 200k+ revenue
- Spend $500/month on Crunchbase Pro (0.3% of revenue)
- Upgrade agents to use verified data
- Increase accuracy to 95%+

---

## Summary Table: FREE vs PAID

| Scenario | Use FREE | Use PAID |
|----------|----------|----------|
| **Pilot Client #1** | ✅ Free sources only | ❌ Too early, high risk |
| **Validating Model** (2-3 clients) | ✅ Still free | ❌ Not justified yet |
| **Scaling** (4-5 clients) | ✅ Primary | ⚠️ Start Crunchbase |
| **Premium Service** (10+ clients) | ✅ Baseline | ✅ Full paid stack |
| **Enterprise** (Fortune 500 clients) | ✅ Required for coverage | ✅ Mandatory for credibility |

---

## Your Decision

**Option A: Conservative (Recommended)**
- Rounds 1-3: Free sources only
- Build pipeline, validate model
- After 3rd client success: Add Crunchbase Pro
- After 5th client: Consider PitchBook

**Option B: Premium from Day 1**
- All sources: Free + Crunchbase + PitchBook
- Higher quality from start
- Higher cost (~$6k/month)
- Only viable if you already have paying clients

**Recommendation: Option A**
- Reduces risk
- Proves ROI before spending
- By Round 4, data costs are negligible vs revenue
- Better for first-time PE sale

---

*This strategy allows you to build a world-class system with <$1k/month in data costs, scaling to profitable enterprise business.*
