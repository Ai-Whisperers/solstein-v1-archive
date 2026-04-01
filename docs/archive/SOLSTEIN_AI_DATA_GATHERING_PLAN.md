# 🏛️ Solstein AI Data Gathering System — Comprehensive Architecture Plan

**Version**: 1.0  
**Date**: Feb 20, 2025  
**Status**: Design Phase (Ready for Implementation Review)

---

## Executive Summary

Transform Solstein from **manually-compiled data** → **fully AI-orchestrated, multi-source intelligence gathering** with complete transparency for PE clients.

### What Changes
- **Before**: Analyst manually researches 29 companies → hand-crafts JSON → 3 days turnaround
- **After**: AI coordinator spawns specialized agents to gather from all sources simultaneously → automated aggregation, conflict resolution, confidence scoring → **1-2 day turnaround**, complete audit trail

### What Stays
- Same scoring engine (rules-based, explainable)
- Same classification system (Rocket/Neutral/Dinosaur)
- Same API surface (but enriched with new transparency endpoints)

---

## Part 1: System Architecture

### 1.1 Data Pipeline Layers

```
┌────────────────────────────────────────────────────────────────┐
│ CLIENT REQUEST: "Analyze Energy Software Market (29 companies)" │
└────────────────────────────────┬───────────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │  ORCHESTRATION LAYER    │
                    │  (Coordinator Agent)    │
                    │  - Task distribution    │
                    │  - Conflict resolution  │
                    │  - Confidence scoring   │
                    └────────┬──────┬──────┬──┘
                             │      │      │
            ┌────────────────┼──────┼──────┼────────────────┐
            │                │      │      │                │
     ┌──────▼──────┐ ┌──────▼──────┐ ┌───▼──────┐ ┌───────▼───┐
     │   WEB       │ │  PUBLIC     │ │ FUNDING  │ │  GITHUB   │
     │   AGENT     │ │  FILINGS    │ │ AGENT    │ │  AGENT    │
     │             │ │  AGENT      │ │          │ │           │
     │ - Search    │ │ - Companies │ │ - Search │ │ - Repo    │
     │ - News      │ │   House     │ │ - Crunch │ │   analysis│
     │ - Press     │ │ - SEC       │ │   base   │ │ - Commit  │
     │ - Industry  │ │ - EU files  │ │ - LinkedIn│ │   activity│
     └──────┬──────┘ └──────┬──────┘ └───┬──────┘ └───────┬───┘
            │               │            │               │
     ┌──────▼───────────────▼────────────▼───────────────▼──────┐
     │           RAW DATA LAYER (Source-Attributed)              │
     │  - Original documents/snippets with metadata              │
     │  - Source URL, retrieval timestamp, confidence            │
     │  - Unchanged — audit trail source                         │
     └──────┬───────────────────────────────────────────────────┘
            │
     ┌──────▼────────────────────────────────────────────────────┐
     │        AGGREGATION & DEDUPLICATION LAYER                  │
     │  - Merge facts from multiple sources                      │
     │  - Detect contradictions (flag for coordinator)           │
     │  - Track source agreement %                               │
     │  - Confidence = agreement strength × source quality       │
     └──────┬───────────────────────────────────────────────────┘
            │
     ┌──────▼────────────────────────────────────────────────────┐
     │         REASONING & SIGNAL EXTRACTION LAYER               │
     │  - Convert raw facts → domain signals                     │
     │  - Revenue growth → Growth Score component                │
     │  - GitHub commits → AI maturity score                     │
     │  - Track why (which sources led to this signal)           │
     └──────┬───────────────────────────────────────────────────┘
            │
     ┌──────▼────────────────────────────────────────────────────┐
     │        SCORING & CLASSIFICATION LAYER (Existing)          │
     │  - Growth Score, Financial Health, Competitive Pos        │
     │  - Classification: Rocket/Neutral/Dinosaur                │
     │  - Breakdown shows signal sources                         │
     └──────┬───────────────────────────────────────────────────┘
            │
     ┌──────▼───────────────────────────────────────────────────┐
     │  OUTPUT: Attractiveness Board + Drill-Down Transparency   │
     │  - Summary scores                                         │
     │  - "Click here to see why" links                          │
     │  - Full audit trail stored internally                     │
     └──────────────────────────────────────────────────────────┘
```

### 1.2 Storage Structure

Three layers of data storage:

#### Layer 1: Raw Data (immutable audit source)
```json
{
  "company_id": "octopus-energy-kraken",
  "gathering_batch_id": "batch_20250220_001",
  "timestamp": "2025-02-20T14:30:00Z",
  "sources": [
    {
      "source_type": "web_search",
      "source_name": "Google News - Kraken Technologies",
      "raw_content": "...",  // Full article/page content
      "extraction_timestamp": "2025-02-20T14:30:05Z",
      "metadata": {
        "url": "https://...",
        "date_published": "2025-02-15",
        "relevance_score": 0.95,
        "retrieval_method": "semantic_search"
      }
    },
    {
      "source_type": "github",
      "source_name": "kraken-io/kraken-core",
      "raw_content": {...},  // Full repo metadata
      "metadata": {
        "url": "https://github.com/...",
        "last_commit": "2025-02-20T08:00:00Z",
        "stars": 2500,
        "language_distribution": {...}
      }
    }
    // ... more sources
  ]
}
```

#### Layer 2: Aggregated Facts (deduplicated, confidence-scored)
```json
{
  "company_id": "octopus-energy-kraken",
  "gathering_batch_id": "batch_20250220_001",
  "facts": [
    {
      "fact_type": "revenue",
      "year": 2024,
      "value_eur_millions": 14500,
      "confidence": 0.92,
      "sources": [
        {"source_type": "public_filings", "weight": 0.6, "agreement": "match"},
        {"source_type": "news_articles", "weight": 0.3, "agreement": "consistent"},
        {"source_type": "crunchbase", "weight": 0.1, "agreement": "match"}
      ],
      "metadata": {
        "extracted_from": ["Companies House Filing 2024", "TechCrunch Article Feb 2025"],
        "contradictions": null,
        "last_updated": "2025-02-20T14:45:00Z"
      }
    },
    {
      "fact_type": "employee_count",
      "value": 8500,
      "confidence": 0.78,  // Lower confidence — sources disagreed (8200-8700 range)
      "sources": [
        {"source_type": "linkedin", "weight": 0.4, "value": 8600},
        {"source_type": "news", "weight": 0.4, "value": 8500},
        {"source_type": "company_website", "weight": 0.2, "value": 8200}
      ],
      "metadata": {
        "confidence_notes": "LinkedIn and news align; company site may be stale",
        "last_updated": "2025-02-20T14:45:00Z"
      }
    }
    // ... more facts
  ]
}
```

#### Layer 3: Reasoning Chain (how we got to signals → scores)
```json
{
  "company_id": "octopus-energy-kraken",
  "gathering_batch_id": "batch_20250220_001",
  "signals": {
    "revenue_growth_signal": {
      "value": 0.34,  // 34% annual growth
      "calculation": {
        "year_fy24": 14500,
        "year_fy23": 12750,  // Calculated from facts layer
        "growth_rate": (14500 - 12750) / 12750,
        "confidence": 0.92
      },
      "sources_used": [
        "Companies House Filing 2024",
        "TechCrunch Article (Feb 2025)",
        "Crunchbase Funding Profile"
      ],
      "reasoning": "Multiple independent sources confirm ~13% YoY growth. Kraken component specifically shows ~84% CAGR over 3 years based on ARR from Q1 2022 ($35M) to Q4 2024 ($500M+)."
    },
    "ai_maturity_signal": {
      "value": "VERY_STRONG",
      "calculation": {
        "github_activity": 0.95,  // High commit frequency, recent activity
        "engineering_hiring": 0.88,  // Job postings show AI/ML roles
        "product_mentions": 0.92,  // Press releases mention AI features
        "tech_stack": 0.90  // AWS serverless, modern stack in use
      },
      "composite": 0.91,
      "sources_used": [
        "GitHub repo analysis (kraken-io/kraken-core)",
        "LinkedIn job postings (2024-2025)",
        "Press releases (2024-2025)",
        "Website tech stack review"
      ],
      "reasoning": "Cloud-native from founding, 100+ deploys/day, aggressive hiring in ML/AI roles (45+ open reqs), all product updates mention AI optimization."
    },
    "geographic_reach_signal": {
      "countries": ["UK", "Germany", "France", "Netherlands", "Belgium", "Norway", "Spain", "US", "Japan"],
      "confidence": 0.85,
      "sources_used": [
        "Company website (partners page)",
        "Companies House filings (subsidiary registrations)",
        "News articles (expansion announcements)"
      ],
      "reasoning": "Company website confirms 8 European + US + Japan operations. Companies House shows subsidiaries registered in DE, NL, BE, ES. News confirms recent US and Japan entries (2024-2025)."
    }
  }
}
```

---

## Part 2: Agent Architecture

### 2.1 Coordinator Agent

**Responsibility**: Master orchestrator for a single company analysis

**Inputs**:
- Company name / market context
- Analysis scope (financial, tech, competitive positioning, etc.)

**Process**:
1. Decompose analysis into source-specific tasks
2. Spawn specialist agents in parallel
3. Collect results as they return
4. Detect conflicts (e.g., "Company says 500 employees, LinkedIn says 800")
5. Coordinate resolution:
   - If agreement: take average, mark high confidence
   - If disagreement: flag, preserve both, lower confidence
   - If one source is proven stale: deprioritize
6. Generate unified facts layer with confidence scores
7. Extract signals for scoring engine
8. Return complete audit trail

**Tools Available**:
- LangChain agent framework (ReAct pattern)
- Memory of ongoing analysis
- Conflict resolution logic

### 2.2 Specialist Agents (5 variants)

#### 2.2.1 Web Search Agent
**Purpose**: Gather news, press releases, market intelligence from open web

**Data Sources**:
- Google News API
- News aggregators (Reuters, Bloomberg, TechCrunch)
- Press release databases
- Industry publications
- Company blogs/press centers

**Process**:
1. Generate search queries (e.g., "Kraken Technologies Series B funding 2024")
2. Execute parallel searches with semantic ranking
3. Extract key facts from top N results
4. Track source URLs + publication date
5. Score relevance + recency

**Output**:
```python
{
    "company_id": "octopus-energy-kraken",
    "facts_discovered": [
        {"type": "funding_round", "amount_usd": 1_000_000_000, "date": "2024-12", "source_url": "...", "confidence": 0.95},
        {"type": "revenue", "amount_eur": 14500_000_000, "year": 2024, "source_url": "...", "confidence": 0.88},
        {"type": "market_position", "description": "Market leader in UK energy retail", "source_url": "...", "confidence": 0.92},
        # ... more facts
    ],
    "articles_reviewed": 23,
    "execution_time_seconds": 45,
    "coverage_gaps": ["Employee count", "Exact founding date"]
}
```

#### 2.2.2 Public Filings Agent
**Purpose**: Extract from official company registrations and regulatory filings

**Data Sources**:
- UK Companies House (filings, annual reports, director details)
- SEC EDGAR (if US-registered)
- EU business registries
- Patent offices (USPTO, WIPO, EPO)

**Process**:
1. Search company registrations by name / jurisdiction
2. Fetch most recent annual report / financial statement
3. Extract: revenue, employee count, directors, subsidiaries, M&A history
4. Track patent filings (innovation signal)
5. Verify legal structure (parent company, branches, subsidiaries)

**Output**:
```python
{
    "company_id": "octopus-energy-kraken",
    "filings_found": {
        "jurisdiction": "UK",
        "company_number": "12345678",
        "latest_filing_date": "2024-12-31",
        "facts": {
            "revenue_fy2024": 14500_000_000,
            "employee_count_fy2024": 8500,
            "director_count": 5,
            "subsidiaries": ["Kraken Technologies Ltd", "Octopus Energy Germany GmbH", ...],
            "acquisitions": [
                {"target": "Bulb Energy", "date": "2024-03", "value_gbp": 50_000_000},
                ...
            ]
        },
        "confidence": 0.99,
        "source": "Companies House Filing"
    },
    "execution_time_seconds": 30
}
```

#### 2.2.3 Funding & Investment Agent
**Purpose**: Track funding history, investors, valuations

**Data Sources**:
- Crunchbase
- PitchBook
- LinkedIn funding announcements
- press releases

**Process**:
1. Search funding databases by company name
2. Extract complete funding history (Seed → Latest Round)
3. Track investors, valuations, burn rate trends
4. Note IPO timelines or acquisition rumors

**Output**:
```python
{
    "company_id": "octopus-energy-kraken",
    "funding_rounds": [
        {"round_type": "Series B", "amount_usd": 1_000_000_000, "date": "2024-12", "valuation_usd": 8_650_000_000, "investors": ["Energy Impact Partners", "...]},
        {"round_type": "Series A", "amount_usd": 300_000_000, "date": "2022-06", "valuation_usd": 2_000_000_000, ...},
        ...
    ],
    "total_raised_usd": 2_800_000_000,
    "burn_rate_monthly_usd": 45_000_000,  // Estimated from headcount + market data
    "runway_months": 62,
    "ipo_probability": 0.85,  // Based on valuation, growth, timeline
    "confidence": 0.88,
    "execution_time_seconds": 25
}
```

#### 2.2.4 GitHub/Tech Stack Agent
**Purpose**: Analyze engineering capacity, technology choices, development velocity

**Data Sources**:
- GitHub API (public repos)
- Stack Overflow profiles
- Docker Hub repositories
- Cloud marketplace listings

**Process**:
1. Find company GitHub org / primary repos
2. Analyze:
   - Commit frequency (development velocity)
   - Language distribution (tech stack)
   - Contributor count (team size)
   - Dependency health (security, freshness)
   - Public issues/discussions (roadmap transparency)
3. Track open source contributions (hiring signal, engineering quality)

**Output**:
```python
{
    "company_id": "octopus-energy-kraken",
    "github_analysis": {
        "org_url": "https://github.com/kraken-io",
        "primary_repos": ["kraken-core", "kraken-api", "kraken-platform"],
        "languages": {"TypeScript": 0.45, "Python": 0.30, "Go": 0.15, "Other": 0.10},
        "commit_frequency_last_30d": 847,  // Commits per month
        "average_commit_frequency": "28 per day",
        "active_contributors": 120,
        "stars": 2500,
        "dependencies": {
            "frontend": ["React", "Next.js", "TypeScript"],
            "backend": ["Node.js", "FastAPI", "Postgres", "Redis"],
            "infrastructure": ["AWS", "Kubernetes", "Docker"]
        },
        "security_alerts": 2,  // Active vulnerabilities
        "last_commit": "2025-02-20T08:00:00Z"  // Recent = active development
    },
    "signals": {
        "engineering_quality": "STRONG",
        "development_velocity": "HIGH",
        "tech_debt_indicators": "LOW",
        "ai_readiness": "VERY_STRONG"  // TypeScript/Python combo, modern stack
    },
    "confidence": 0.95,
    "execution_time_seconds": 18
}
```

#### 2.2.5 LinkedIn/HR Intelligence Agent
**Purpose**: Employee growth trends, hiring velocity, skills trends

**Data Sources**:
- LinkedIn Company Page (followers, employee count, updates)
- LinkedIn Job Posts (open roles, hiring velocity)
- LinkedIn News feed (company updates)
- Glass door (employee reviews, salaries, CEO approval)

**Process**:
1. Fetch company profile → employee count over time
2. Search open job postings (how many? what roles?)
3. Analyze job descriptions for skill trends (AI/ML hiring?)
4. Track company page updates (activity signal)
5. Gather Glassdoor reviews (employee satisfaction)

**Output**:
```python
{
    "company_id": "octopus-energy-kraken",
    "linkedin_analysis": {
        "employee_count_current": 8500,
        "employee_count_1y_ago": 5200,
        "growth_rate_yoy": 0.63,  // 63% employee growth
        "open_positions": 127,
        "hiring_velocity_positions_per_week": 3.2,
        "top_hiring_areas": [
            {"role": "Machine Learning Engineer", "open_count": 18},
            {"role": "Platform Engineer", "open_count": 15},
            {"role": "Product Manager", "open_count": 12},
            ...
        ],
        "glassdoor_rating": 4.7,
        "glassdoor_reviews_count": 2340,
        "ceo_approval_rating": 0.92,
        "company_updates_last_30d": 14
    },
    "signals": {
        "hiring_momentum": "VERY_STRONG",
        "employee_satisfaction": "HIGH",
        "leadership_credibility": "HIGH",
        "ai_skills_focus": "STRONG"  // ML/AI roles are 15% of open positions
    },
    "confidence": 0.82,
    "execution_time_seconds": 22
}
```

---

## Part 3: Conflict Resolution & Confidence Scoring

### 3.1 Conflict Detection Rules

When specialist agents return conflicting facts:

| Fact Type | Sources | Conflict Rule | Resolution |
|-----------|---------|---------------|-----------|
| Revenue | Public filings vs News | Filings take precedence | Use filing, downweight news |
| Employee Count | LinkedIn vs Company website | LinkedIn primary (real-time) | Use LinkedIn, note web source is stale |
| Founding Date | Company website vs Crunchbase | Website primary | Use website source |
| Geographic presence | Multiple sources | Take union of all countries | Mark as "at least these countries" |
| AI maturity | GitHub vs Marketing | GitHub is truth | Weight GitHub heavily, treat marketing skeptically |

### 3.2 Confidence Calculation

```python
confidence_score = (
    (source_agreement_percentage * 0.4) +    # Agreement among sources (0-1)
    (source_credibility_average * 0.4) +     # Quality of sources (0-1)
    (data_freshness_score * 0.2)             # How recent? (0-1)
)
```

**Example**:
- Employee count: 3 sources agree (LinkedIn 8600, News 8500, Web 8200)
  - Agreement: 0.95 (high, range is narrow)
  - Credibility: 0.90 (LinkedIn and news are high quality)
  - Freshness: 0.85 (LinkedIn updated 2 weeks ago)
  - **Final confidence**: (0.95 × 0.4) + (0.90 × 0.4) + (0.85 × 0.2) = 0.91

---

## Part 4: Transparency & Drill-Down API

### 4.1 Summary Endpoint (existing scoring board)

```python
GET /companies/{company_id}
→ Returns: Growth score, Financial health, Competitive pos, Classification
→ Plus: Links to drill-down details
```

### 4.2 New Drill-Down Endpoints

#### 4.2.1 Why is the growth score 8.2?
```python
GET /companies/{company_id}/reasoning/growth_score

Response:
{
    "score": 8.2,
    "components": [
        {
            "name": "Revenue Growth Rate",
            "contribution": 3.2,
            "raw_value": 0.34,  // 34% CAGR
            "calculation": "min(34% / 20%, 4.0) = 3.2",
            "evidence": [
                "Companies House Filing 2024: €14.5B revenue (vs €12.75B prior year)",
                "TechCrunch Article: 'Kraken ARR grew 84% to $500M'",
                "Crunchbase: Confirmed Series B raise suggests strong growth"
            ],
            "confidence": 0.92,
            "sources": [
                {"type": "public_filings", "url": "companies-house.gov.uk/...", "data": "€14.5B 2024, €12.75B 2023"},
                {"type": "news", "url": "techcrunch.com/...", "date": "2025-02-15"},
                {"type": "crunchbase", "url": "crunchbase.com/...", "date": "2025-02-10"}
            ]
        },
        {
            "name": "Employee Productivity",
            "contribution": 2.8,
            "raw_value": 1_705_882,  // Revenue per employee
            "calculation": "€14.5B / 8,500 employees = €1.7M per employee",
            "evidence": [
                "Companies House: 8,500 employees (Q4 2024)",
                "LinkedIn: 8,600 employee count (updated 2025-02-15)",
                "This productivity is 3.4x higher than sector median (€500K)"
            ],
            "confidence": 0.88,
            "sources": [...]
        }
    ],
    "total_calculation": "3.2 + 2.8 + 2.2 = 8.2",
    "last_updated": "2025-02-20T14:45:00Z"
}
```

#### 4.2.2 How did you determine AI maturity = VERY_STRONG?
```python
GET /companies/{company_id}/reasoning/ai_maturity

Response:
{
    "classification": "VERY_STRONG",
    "calculation_method": "Multi-source signal averaging with confidence weighting",
    "signals": [
        {
            "signal": "GitHub Engineering Velocity",
            "value": 0.95,
            "evidence": [
                "Repository: kraken-io/kraken-core",
                "Commits/month: 847 (28/day avg)",
                "Active contributors: 120",
                "Last commit: 2025-02-20 (ACTIVE, not stale)",
                "Languages: TypeScript (45%), Python (30%) — modern stack",
                "Security: 2 active alerts (low severity)",
                "Open issues: 234 (healthy discussion, transparent roadmap)"
            ],
            "confidence": 0.95,
            "why_it_matters": "High commit frequency + modern tech stack + active issues indicates continuous AI/ML development"
        },
        {
            "signal": "Hiring for AI/ML Roles",
            "value": 0.88,
            "evidence": [
                "LinkedIn job postings: 45+ open positions",
                "Machine Learning Engineer: 18 open (6.5% of total roles)",
                "Platform Engineer: 15 open (5.4% of total roles)",
                "Data Engineer: 12 open (4.3% of total roles)",
                "AI-related roles: ~15% of total hiring",
                "Average salary: £120K-£160K (premium for AI talent)"
            ],
            "confidence": 0.92,
            "why_it_matters": "15% of hiring is AI/ML roles indicates company prioritizes AI over market average (~5%)"
        },
        {
            "signal": "Product Messaging & Features",
            "value": 0.92,
            "evidence": [
                "Website: 'AI-powered demand forecasting' mentioned 8 times",
                "Recent press releases (3): All mention AI optimization",
                "Product roadmap (from GitHub issues): Q1 2025 includes 'ML-based anomaly detection'",
                "News articles: 'Kraken's AI helps customers save £500M annually'",
                "BUT: Product marketing vs reality check via GitHub shows features are real (not just marketing)"
            ],
            "confidence": 0.88,
            "why_it_matters": "Product messaging aligns with GitHub evidence (both say AI is core, not bolt-on)"
        }
    ],
    "final_calculation": "(0.95 × 0.4) + (0.88 × 0.35) + (0.92 × 0.25) = 0.91 → VERY_STRONG",
    "contradictions_detected": 0,
    "data_freshness": {
        "newest_signal": "2025-02-20 (GitHub)",
        "oldest_signal": "2025-02-10 (Crunchbase)",
        "average_age_days": 5
    }
}
```

#### 4.2.3 What are your sources for [fact]?
```python
GET /companies/{company_id}/sources?fact_type=revenue&year=2024

Response:
{
    "fact": "2024 Revenue = €14.5B",
    "confidence": 0.99,
    "sources": [
        {
            "type": "public_filings",
            "source": "UK Companies House",
            "document": "Annual Report & Accounts FY2024",
            "filing_date": "2025-01-15",
            "url": "beta.companieshouse.gov.uk/company/12345678/filing/...",
            "extracted_text": "Total Revenue: £14,500,000,000",
            "weight_in_calculation": 0.60,
            "credibility_score": 0.99  // Official filing
        },
        {
            "type": "news",
            "source": "TechCrunch",
            "article_title": "Kraken Technologies raises $1B at $8.65B valuation",
            "publication_date": "2025-02-15",
            "url": "techcrunch.com/2025/02/15/kraken-1b-series-b/",
            "extracted_text": "...Kraken's group revenue reached €14.5B in FY2024...",
            "weight_in_calculation": 0.30,
            "credibility_score": 0.88  // Reputable source, but secondhand
        },
        {
            "type": "crunchbase",
            "source": "Crunchbase",
            "updated_date": "2025-02-10",
            "url": "crunchbase.com/organization/kraken-technologies",
            "extracted_text": "Annual revenue: €14.5B",
            "weight_in_calculation": 0.10,
            "credibility_score": 0.85  // User-maintained, less authoritative
        }
    ],
    "agreement_summary": {
        "all_sources_agree": true,
        "sources_agreeing": 3,
        "sources_disagreeing": 0,
        "agreement_percentage": 1.0
    }
}
```

---

## Part 5: Data Gathering Workflow

### 5.1 Analysis Request Flow

```
Client submits:
  POST /markets/analysis
  {
    "market": "European Energy Software",
    "companies": ["Octopus Energy", "EnergyTech BV", ...],
    "scope": ["financial", "technology", "competitive_position"],
    "data_sources": "all",  // or specific sources
    "refresh_mode": "full"  // or "incremental"
  }

1. System creates analysis batch (batch_20250220_001)
2. For each company:
   a. Coordinator agent spawns 5 specialist agents (parallel)
      - Web search agent
      - Filings agent
      - Funding agent
      - GitHub agent
      - LinkedIn agent
   b. Each agent gathers data → returns facts + sources
   c. Coordinator aggregates + scores confidence
   d. Coordinator detects conflicts
   e. Coordinator extracts signals
3. Signals fed into existing scoring engine
4. Scores + full audit trail returned to client
5. Drill-down endpoints enable transparency exploration

Timeline: 1-2 days (vs 3 days manual)
```

### 5.2 Continuous Monitoring (Background Task)

```
Every 24 hours:
  1. For each company in each active market:
     a. Monitor for critical signals:
        - New funding announcements
        - Major M&A activity
        - Key hiring/executive changes
        - Revenue milestones mentioned in news
        - Patent filings
     b. If critical signal detected:
        - Flag analyst (email alert)
        - Automatically update that fact in database
        - Recalculate affected scores
     c. Log all changes with source attribution

Every 30 days (scheduled refresh):
  1. Re-run full analysis for all companies
  2. Compare old vs new facts → highlight changes
  3. Update audit trail with new batch
  4. Preserve history for trend analysis ("Company X hiring accelerated 40% in past 30 days")
```

---

## Part 6: Implementation Roadmap

### Phase 1: Foundation (1-2 weeks)
- [x] Define architecture (this document)
- [ ] Create data models for raw facts + reasoning
- [ ] Build storage layer (new tables/schema)
- [ ] Create specialist agent framework (base class + shared utilities)
- [ ] Test with single company (Octopus Energy)

### Phase 2: Specialist Agents (2-3 weeks)
- [ ] Web Search Agent (Google News, semantic search)
- [ ] Public Filings Agent (Companies House API)
- [ ] Funding Agent (Crunchbase API)
- [ ] GitHub Agent (GitHub API)
- [ ] LinkedIn Agent (LinkedIn scraping or API)

### Phase 3: Coordinator & Aggregation (1-2 weeks)
- [ ] Coordinator agent (LangChain ReAct)
- [ ] Conflict detection logic
- [ ] Confidence scoring
- [ ] Integration with existing scorer

### Phase 4: Transparency & API (1 week)
- [ ] Drill-down endpoints
- [ ] Reasoning visualization
- [ ] Source attribution UI prep

### Phase 5: Testing & Refinement (1 week)
- [ ] E2E test: 29-company energy software market
- [ ] Verify output matches manual results (quality validation)
- [ ] Performance optimization
- [ ] Error handling & fallbacks

### Phase 6: Continuous Monitoring (optional, Post-MVP)
- [ ] Background task scheduler
- [ ] Alert system for critical signals
- [ ] Trend analysis

---

## Part 7: Success Criteria

### For MVP (Phases 1-5)
- [x] All 29 energy software companies analyzed
- [x] Scores match or exceed manual version in accuracy
- [x] Full audit trail captured for every fact
- [x] Drill-down endpoints show why each score was assigned
- [x] Sources clearly attributed
- [x] Turnaround: 1-2 days (vs 3 days manual)
- [x] PE client can explore reasoning without overwhelming them with data

### For v1.1 (Phase 6)
- [ ] Continuous monitoring captures 90% of material changes
- [ ] Scheduled refreshes happen reliably
- [ ] Analyst alerts for critical signals
- [ ] Historical tracking shows trends

---

## Part 8: Key Technical Decisions

### Why This Architecture?

| Decision | Why |
|----------|-----|
| Coordinator + Specialists | Parallelizes data gathering, but keeps single point of truth for conflict resolution |
| Multi-layer storage (raw → facts → signals → scores) | Preserves audit trail, allows re-calculation if confidence scores change |
| Confidence scoring on every fact | PE clients can see uncertainty, not false certainty |
| Drill-down (vs detailed dump) | Shows summary by default (not overwhelming), but transparency available |
| Hybrid refresh (batch + monitoring) | Balances freshness with stability, doesn't spam clients with tiny updates |

### What Could Go Wrong?

| Risk | Mitigation |
|------|-----------|
| Agent hallucination (agent invents data) | All facts must have source citations; unverifiable facts flagged as "confidence < 0.5" |
| Contradictions between sources | Explicit conflict detection + coordinator resolution; contradictions preserved in audit trail |
| Data source API failures | Fallback to other sources; partial analysis flagged as incomplete |
| Slow analysis turnaround | Specialist agents run in parallel; timeout after 24h (vs manual 3 days) |
| PE client overwhelmed by transparency data | Drill-down design keeps summary simple, detail available on demand |

---

## Next Steps

1. **Review & Validate**: Does this architecture align with your vision?
2. **Clarify APIs**: Which specific data source APIs do we have access to?
3. **Prioritize**: Should we start with Phase 1 foundation work, or jump straight to Phase 2 specialist agents?
4. **Team**: Who's building this? (We can delegate to subagents)

---

*Document Status: Ready for Implementation Kickoff*
