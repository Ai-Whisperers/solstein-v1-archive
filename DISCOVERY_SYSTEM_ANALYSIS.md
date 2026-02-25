# Solstein Discovery & Enrichment System Analysis
## Why We Only Got 4 (Then 33) Companies - And How to Fix It

---

## 🎯 The Problem

### What Happened
1. **First Run**: Only analyzed 4 markdown files from `custom_market_runs/` directory
2. **Second Run**: Analyzed all 33 companies from `competitor_data.json`
3. **The Issue**: **ALL 33 companies scored exactly 4.67/10** (default scores!)

### Why All Companies Got Default Scores
```
Growth Score: 5.0/10 (default - no growth data)
Financial Health: 5.0/10 (default - no revenue data)
Competitive Position: 4.0/10 (default - no tech signals)
Composite: 4.67/10 (SALT classification for ALL)
```

**Root Cause**: The `competitor_data.json` database contains basic company info but **lacks rich signals**:
- ❌ No verified revenue figures
- ❌ No growth rate data
- ❌ No tech stack details
- ❌ No AI maturity signals
- ❌ No funding/valuation data

---

## ✅ The Solution: Automated Discovery & Enrichment

### Discovery System Architecture

Solstein has a **sophisticated discovery system** that can automatically find companies beyond the database:

```
┌─────────────────────────────────────────────────────────────┐
│                    DISCOVERY SOURCES                         │
├─────────────────────────────────────────────────────────────┤
│ 1. Web Search Discovery (Exa/Google)                        │
│    → Search: "Dutch energy software companies"              │
│    → Find companies NOT in database                         │
│    → Returns: Company names, websites, snippets             │
│                                                             │
│ 2. Static Catalog (Hardcoded Lists)                         │
│    → Predefined lists by market                             │
│    → Example: 50+ energy software companies                 │
│                                                             │
│ 3. Competitor JSON (Current Database)                       │
│    → 33 companies (what we just scored)                     │
│    → Should be starting point, not endpoint                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    ENRICHMENT ADAPTERS                       │
├─────────────────────────────────────────────────────────────┤
│ 1. Website Adapter         → Scrape company websites        │
│ 2. News Adapter            → Find news/articles             │
│ 3. LinkedIn Adapter        → Employee data, growth          │
│ 4. Funding Adapter         → Crunchbase, funding rounds     │
│ 5. Patents Adapter         → Innovation signals             │
│ 6. Web Search Adapter      → General company info           │
│ 7. Yahoo Finance Adapter   → Financial data for public cos  │
│ 8. Global Market Adapter   → Market-specific sources        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    INTELLIGENCE LAYER                        │
├─────────────────────────────────────────────────────────────┤
│ 1. Conflict Resolution       → Merge data from N sources    │
│ 2. Confidence Scoring        → 0.0-1.0 per data point      │
│ 3. Source Attribution        → Track where each fact came   │
│ 4. Scoring Engine            → Calculate real scores        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 Discovery Adapters Found

### 1. Web Search Discovery (`adapters/discovery/web_search.py`)
```python
# Automatically discovers companies via Exa search
discover(
    market="energy software",
    seed_company="Eneve",
    max_results=50
)
# Returns: List of DiscoveryCandidate objects
```

### 2. Static Catalog Discovery (`research/discovery.py`)
```python
# Hardcoded catalog of 50+ companies for Dutch/Energy market
_catalog_for_market("dutch energy software")
# Returns: Predefined list with URLs, tickers, industries
```

### 3. Competitor JSON (`adapters/discovery/competitor_json.py`)
```python
# Current database (33 companies)
# Should be used as seed, not limit
```

---

## 🚀 Enrichment Adapters Found (8 Total)

| Adapter | Purpose | Confidence | Data Provided |
|---------|---------|------------|---------------|
| **Website** | Scrape company sites | 0.75 | Tech stack, products, about |
| **News** | News aggregation | 0.70 | Funding, partnerships, growth |
| **LinkedIn** | Employee data | 0.65 | Headcount, growth, hiring |
| **Funding** | Investment data | 0.80 | Valuation, funding rounds |
| **Patents** | Innovation signals | 0.60 | R&D activity, IP |
| **Web Search** | General search | 0.70 | Overview, context |
| **Yahoo Finance** | Financial data | 0.90 | Revenue, margins (public) |
| **Global Market** | Market intel | 0.70 | Regional data |

---

## 📊 What Should Happen (Proper Flow)

### Step 1: Discovery (Find ALL Companies)
```python
# Use multiple discovery sources
candidates = []
candidates += web_search.discover("Dutch energy software", "Eneve", max_results=100)
candidates += static_catalog.get_companies("dutch energy software")
candidates += competitor_json.get_all()

# Result: 100+ companies (not just 33!)
```

### Step 2: Enrichment (Gather Rich Signals)
```python
for company in candidates:
    # Parallel enrichment from 8 sources
    facts = []
    facts += website_adapter.enrich(company)
    facts += news_adapter.enrich(company)
    facts += linkedin_adapter.enrich(company)
    facts += funding_adapter.enrich(company)
    # ... etc
    
    # Each fact has confidence score
    # Result: Rich company profile with signals
```

### Step 3: Scoring (Calculate Real Scores)
```python
# With rich signals, scores vary:
# - High growth + funding → 9.0+ (PHOENIX)
# - Moderate growth → 5.0-7.0 (SALT)
# - Stagnant/declining → < 4.0 (LEAD)
```

---

## 🎯 The Gap in Current Implementation

### What's Missing
1. **Discovery Not Automated**: We only used the 33 JSON companies
2. **Enrichment Not Run**: Rich signals not gathered before scoring
3. **Flow Not Connected**: Discovery → Enrichment → Scoring should be one pipeline

### What Eneve Flow Should Have Done
```
1. Discover Phase:
   - Search for "Dutch energy software companies"
   - Find 100+ candidates (including the 33 in DB)
   
2. Enrichment Phase:
   - Scrape websites for tech stack
   - Check LinkedIn for headcount growth
   - Find funding news
   - Gather revenue estimates
   
3. Scoring Phase:
   - Score ALL 100+ with rich signals
   - Get meaningful variance (1.0 to 10.0)
   - Identify true PHOENIX vs LEAD
```

---

## 💡 Immediate Recommendations

### Option 1: Run Full Discovery + Enrichment Pipeline
```bash
# This would discover 100+ companies and enrich them
python -m solstein.cli discover \
    --market "Dutch energy software" \
    --seed-company "Eneve" \
    --max-results 100 \
    --output data/output/exports/discovered_companies.json

# Then enrich all discovered companies
python -m solstein.cli enrich \
    --input data/output/exports/discovered_companies.json \
    --adapters website,news,linkedin,funding \
    --output data/output/exports/enriched_companies.json

# Then score with rich signals
python -m solstein.cli score \
    data/output/exports/enriched_companies.json \
    --output data/output/exports/scored_companies.json
```

### Option 2: Use Existing Markdown Files (Rich Data)
The 4 markdown files had rich data because they were manually created with:
- Revenue estimates
- Growth rates
- Employee counts
- Tech stack details
- AI maturity assessments

**This is why Eneve scored 9.03/10 from markdown vs 4.67/10 from JSON!**

### Option 3: Combine Approaches
1. Discover all companies (100+)
2. Check if rich markdown exists (like Eneve)
3. Enrich those without rich data
4. Score everyone with full signals

---

## 📈 Expected Results With Full Pipeline

| Metric | Current (33 JSON) | Expected (100+ Enriched) |
|--------|-------------------|--------------------------|
| Companies | 33 | 100-150 |
| PHOENIX (≥7) | 0 | 10-20 |
| SALT (4-7) | 33 | 50-80 |
| LEAD (<4) | 0 | 20-40 |
| Score Range | 4.67 only | 1.0 - 10.0 |
| Data Quality | Poor (defaults) | Rich (8 sources) |

---

## 🎬 Next Steps

To get meaningful results for Eneve:

1. **Run Discovery**: Find all 100+ Dutch energy software companies
2. **Enrich Data**: Gather signals from 8 adapters
3. **Score Properly**: Get meaningful variance (PHOENIX vs LEAD)
4. **Position Eneve**: See where they rank in FULL market

**The infrastructure exists** - we just need to run the complete pipeline!

---

*Analysis completed: February 25, 2026*
*Files examined: discovery.py, 8 enrichment adapters, competitor_json.py*
