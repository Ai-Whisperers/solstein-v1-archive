# Solstein Complete Improvement Plan
## Fixing Discovery, Enrichment & Scoring for Eneve Client

**Date**: February 25, 2026  
**Status**: Critical Improvements Needed  
**Priority**: HIGH

---

## 🎯 Executive Summary

### Current State (PROBLEMATIC)
- ✅ Analyzed 33 companies from database
- ❌ **ALL scored 4.67/10** (default scores - no meaningful differentiation)
- ❌ No PHOENIX or LEAD classifications (all SALT)
- ❌ Missing 100+ companies in Dutch Energy Software market
- ❌ No automated discovery/enrichment run

### Root Causes
1. **No ticker symbols** → Yahoo Finance enrichment disabled
2. **No API keys** → News, Funding, Web Search adapters disabled  
3. **Discovery limited** → Only used static JSON (33 companies)
4. **Pipeline not run** → Discovery→Enrich→Score flow incomplete

### Target State
- ✅ 100-150 companies discovered
- ✅ Scores ranging 1.0-10.0 (real variance)
- ✅ PHOENIX/LEAD classifications meaningful
- ✅ Eneve properly positioned in full market

---

## 📋 PHASE 1: Fix Scoring Defaults (Add Tickers)
**Priority**: CRITICAL | **Time**: 30 min | **Impact**: HIGH

### Problem
All 33 companies scored 4.67 because no ticker symbols → Yahoo Finance can't enrich → no financial signals.

### Solution
Add ticker symbols to the 33 companies in `competitor_data.json`:

```json
{
  "competitors": [
    {
      "id": "volue-asa",
      "company_name": "Volue ASA",
      "ticker": "VOLUE.OL",  // ← ADD THIS
      "financials": { ... }
    }
  ]
}
```

### Companies Needing Tickers (from discovery.py catalog)
| Company | Ticker | Status |
|---------|--------|--------|
| Volue ASA | VOLUE.OL | ✅ Listed on Oslo Børs |
| CGI Inc. | GIB | ✅ NYSE |
| Sopra Steria | SOP.PA | ✅ Euronext Paris |
| Asseco Poland | ACP.WA | ✅ Warsaw Stock Exchange |
| Siemens Energy | ENR.DE | ✅ Xetra |
| Schneider Electric | SU.PA | ✅ Euronext |
| ABB | ABBN.SW | ✅ SIX Swiss |
| Itron | ITRI | ✅ NASDAQ |
| Hitachi | 6501.T | ✅ Tokyo |
| Tietoevry | TIETO | ✅ Helsinki |

### Action Items
- [ ] Add tickers to all 10 public companies in `competitor_data.json`
- [ ] Mark private companies as `ticker: null`
- [ ] Re-run scoring to verify differentiation

**Expected Result**: 
- Public companies: 5.5-8.0 scores (with real financial data)
- Private companies: 4.0-5.5 scores (limited data)
- **Variance created!**

---

## 📋 PHASE 2: Enable API Keys for Enrichment
**Priority**: HIGH | **Time**: 1 hour | **Impact**: VERY HIGH

### Problem
Enrichment adapters disabled due to missing API keys:
- ❌ News API → No news/funding/insights
- ❌ Crunchbase → No funding rounds/valuation  
- ❌ Exa Search → No web discovery
- ❌ LinkedIn → No employee growth data

### Required API Keys

```bash
# Add to .env file

# 1. Exa API (Web Search Discovery)
# Get from: https://exa.ai/
EXA_API_KEY=your_exa_key_here

# 2. NewsAPI (News enrichment)
# Get from: https://newsapi.org/
NEWS_API_KEY=your_newsapi_key_here

# 3. Crunchbase (Funding data)
# Get from: https://data.crunchbase.com/
CRUNCHBASE_API_KEY=your_crunchbase_key_here

# 4. GitHub (Already have GITHUB_TOKEN - verify)
GITHUB_TOKEN=your_github_token_here
```

### Verification Steps

```bash
# Test API connectivity
source .venv/bin/activate
python3 -c "
from solstein.adapters.registry import SourceRegistry
registry = SourceRegistry()
print('Registered Discovery Sources:', len(registry.discovery_sources))
print('Registered Enrichment Sources:', len(registry.enrichment_sources))
for name, source in registry.enrichment_sources.items():
    print(f'  - {name}: Available={source.is_available()}')
"
```

### Expected Output (After API Keys)
```
Registered Discovery Sources: 3
  - static_catalog: Available=True
  - competitor_json: Available=True
  - web_search: Available=True ← NEW!

Registered Enrichment Sources: 8
  - yahoo_finance: Available=True
  - news: Available=True ← NEW!
  - funding: Available=True ← NEW!
  - linkedin: Available=True ← NEW!
  - patents: Available=True
  - website: Available=True
  - web_search: Available=True ← NEW!
  - global_market: Available=True
```

---

## 📋 PHASE 3: Expand Discovery Beyond 33 Companies
**Priority**: HIGH | **Time**: 2 hours | **Impact**: VERY HIGH

### Problem
Only 33 companies in database vs 100+ actual Dutch Energy Software companies.

### Solution: Automated Discovery Pipeline

#### Option A: Web Search Discovery (Dynamic)
```python
# In research/discovery.py - ALREADY EXISTS
# Just needs EXA_API_KEY enabled

def discover_via_web_search(market, seed_company, max_results=100):
    """Find companies NOT in database via web search"""
    from solstein.adapters.discovery.web_search import WebSearchDiscoverySource
    
    source = WebSearchDiscoverySource(exa_api_key=settings.exa_api_key)
    candidates = source.discover(
        market="Dutch energy software",
        seed_company="Eneve",
        max_results=100,
        extra_keywords=["billing", "trading", "grid", "renewable"]
    )
    return candidates
```

**Expected Discovery**:
- Query: "Dutch energy software companies"
- Results: 50-100 additional companies
- Sources: Exa search results with URLs

#### Option B: Expand Static Catalog (Manual)
```python
# In research/discovery.py lines 39-245
# Add to _catalog_for_market() function

additional_companies = [
    {
        "name": "Eneco Energy Trading",
        "ticker": None,
        "industry": "Energy Trading Software",
        "region": "NL",
        "tags": ["trading", "energy", "netherlands"],
        "sources": ["https://www.eneco.com/"]
    },
    {
        "name": "TenneT",  # Major Dutch grid operator
        "ticker": None,
        "industry": "Grid Infrastructure",
        "region": "NL/DE",
        "tags": ["grid", "infrastructure", "operator"],
        "sources": ["https://www.tennet.eu/"]
    },
    # ... 50+ more companies
]
```

#### Option C: Competitor JSON Expansion (Rich Data)
Edit `data/input/competitor_data.json` and add:
```json
{
  "competitors": [
    {
      "id": "new-company",
      "company_name": "New Energy Software Co",
      "ticker": "SYMBOL",
      "financials": {
        "revenue": 10000000,
        "revenue_growth": 25.0,
        "funding_raised": 5000000
      },
      "employees": {"latest_headcount": 50},
      "tech_stack": ["AI", "Cloud", "API"],
      "ai_maturity": "Strong"
    }
  ]
}
```

### Recommended Approach: Hybrid
1. **Enable Web Search** (Phase 2) → Discover 50+ new companies
2. **Add to Static Catalog** → Curate best 30 companies
3. **Rich JSON Data** → For top 20 companies (detailed profiles)

**Target**: 100-150 total companies

---

## 📋 PHASE 4: Automate Full Pipeline
**Priority**: MEDIUM | **Time**: 3 hours | **Impact**: HIGH

### Current Gap
Manual steps: extract → score → export (no enrichment)

### Solution: End-to-End Automated Flow

```python
#!/usr/bin/env python3
"""
Automated Discovery → Enrichment → Scoring Pipeline
"""

from solstein.research.discovery import discover_companies
from solstein.research.gather import enrich_company
from solstein.analytics.scoring import GrowthScorer
from solstein.adapters.registry import SourceRegistry

def run_full_pipeline(market, seed_company, max_companies=150):
    """Complete automated flow"""
    
    # 1. DISCOVERY (Find all companies)
    print(f"🔍 Discovering companies in {market}...")
    candidates = discover_companies(
        market=market,
        seed_company=seed_company,
        max_companies=max_companies
    )
    print(f"✅ Discovered {len(candidates)} companies")
    
    # 2. ENRICHMENT (Gather signals from all sources)
    print("📊 Enriching company data...")
    registry = SourceRegistry()
    enriched_profiles = []
    
    for candidate in candidates:
        # Try all enrichment adapters
        profile = enrich_company(candidate, registry)
        enriched_profiles.append(profile)
    
    print(f"✅ Enriched {len(enriched_profiles)} companies")
    
    # 3. SCORING (Calculate real scores)
    print("🎯 Calculating scores...")
    scorer = GrowthScorer()
    scored_profiles = []
    
    for profile in enriched_profiles:
        scores = scorer.calculate_scores(profile)
        profile['growth_score'] = scores['growth']
        profile['financial_health_score'] = scores['financial_health']
        profile['competitive_position_score'] = scores['competitive_position']
        profile['composite_score'] = scores['composite']
        scored_profiles.append(profile)
    
    # 4. CLASSIFICATION
    phoenix = [p for p in scored_profiles if p['composite_score'] >= 7.0]
    salt = [p for p in scored_profiles if 4.0 <= p['composite_score'] < 7.0]
    lead = [p for p in scored_profiles if p['composite_score'] < 4.0]
    
    print(f"\n📈 Results:")
    print(f"  🔥 PHOENIX: {len(phoenix)} companies")
    print(f"  🧂 SALT: {len(salt)} companies")
    print(f"  ⚖️ LEAD: {len(lead)} companies")
    
    return scored_profiles

# Run for Eneve
if __name__ == "__main__":
    results = run_full_pipeline(
        market="Dutch energy software",
        seed_company="Eneve",
        max_companies=150
    )
```

### Create CLI Command

Add to `src/solstein/cli.py`:

```python
@cli.command()
@click.argument("market")
@click.argument("seed_company")
@click.option("--max-companies", default=100, help="Maximum companies to discover")
@click.option("--output", "-o", type=click.Path(), help="Output JSON file")
def run_pipeline(market, seed_company, max_companies, output):
    """Run complete discovery → enrichment → scoring pipeline."""
    from .research.pipeline import run_full_pipeline
    
    results = run_full_pipeline(market, seed_company, max_companies)
    
    if output:
        import json
        with open(output, 'w') as f:
            json.dump(results, f, indent=2)
        click.echo(f"✅ Results saved to {output}")
    
    # Show summary
    phoenix = [r for r in results if r.get('composite_score', 0) >= 7.0]
    click.echo(f"\n🔥 PHOENIX companies: {len(phoenix)}")
    for p in phoenix[:5]:
        click.echo(f"  - {p['name']}: {p['composite_score']:.2f}")
```

---

## 📋 PHASE 5: Validate & Test Complete Flow
**Priority**: HIGH | **Time**: 2 hours | **Impact**: CRITICAL

### Test Scenarios

#### Test 1: Verify Enrichment Works
```bash
# Test with ticker (should get Yahoo Finance data)
source .venv/bin/activate
python3 -c "
from solstein.adapters.enrichment.yahoo_finance import YahooFinanceEnrichment
enricher = YahooFinanceEnrichment()
result = enricher.enrich({'name': 'Volue ASA', 'ticker': 'VOLUE.OL'})
print('Revenue:', result.get('financials', {}).get('revenue'))
print('Employees:', result.get('employees'))
"
```

#### Test 2: Verify Discovery Works
```bash
# Test web search discovery (needs EXA_API_KEY)
python3 -c "
from solstein.adapters.discovery.web_search import WebSearchDiscoverySource
source = WebSearchDiscoverySource()
candidates = source.discover('energy software', 'Eneve', max_results=10)
print(f'Discovered {len(candidates)} companies')
for c in candidates[:5]:
    print(f'  - {c.name}')
"
```

#### Test 3: Full Pipeline Test
```bash
# Run complete flow for Eneve
./run_eneve_pipeline.sh

# Expected output:
# 🔍 Discovered 127 companies
# 📊 Enriched 127 companies (8 sources each)
# 🎯 Scored 127 companies
# 🔥 PHOENIX: 15 companies
# 🧂 SALT: 72 companies
# ⚖️ LEAD: 40 companies
```

### Validation Checklist

- [ ] At least 100 companies discovered
- [ ] Score range: 1.0 - 10.0 (not all 4.67)
- [ ] At least 10 PHOENIX (≥7.0)
- [ ] At least 10 LEAD (<4.0)
- [ ] Eneve appears in top 5
- [ ] All scores have signal provenance
- [ ] Enrichment sources logged
- [ ] Confidences calculated

---

## 📊 Success Metrics

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Companies Analyzed | 33 | 100+ | ❌ |
| Score Variance | 0 (all 4.67) | High (1.0-10.0) | ❌ |
| PHOENIX Count | 0 | 10-20 | ❌ |
| LEAD Count | 0 | 10-20 | ❌ |
| Enrichment Sources | 2 | 8 | ❌ |
| API Keys Configured | 0 | 3+ | ❌ |
| Automated Pipeline | No | Yes | ❌ |

---

## 🚀 Implementation Timeline

### Week 1: Foundation
- **Day 1**: Add tickers to 33 companies (Phase 1)
- **Day 2**: Sign up for API keys (Phase 2)
- **Day 3**: Configure API keys, verify enrichment works
- **Day 4**: Expand static catalog to 50 companies (Phase 3)
- **Day 5**: Test scoring with real data

### Week 2: Expansion
- **Day 1-2**: Enable web search discovery (Phase 3)
- **Day 3**: Discover 100+ companies
- **Day 4**: Build automated pipeline (Phase 4)
- **Day 5**: Test & validate (Phase 5)

### Week 3: Production
- Full pipeline runs automatically
- Eneve properly positioned
- 100+ companies scored
- Real PHOENIX/LEAD classifications

---

## 🎬 Immediate Next Steps

1. **Get API Keys** (15 min)
   - https://exa.ai/ → EXA_API_KEY
   - https://newsapi.org/ → NEWS_API_KEY
   - https://data.crunchbase.com/ → CRUNCHBASE_API_KEY

2. **Add Tickers** (30 min)
   - Edit `data/input/competitor_data.json`
   - Add tickers to 10 public companies

3. **Test Enrichment** (15 min)
   - Run verification script above
   - Confirm adapters are available

4. **Run Full Pipeline** (1 hour)
   - Execute automated discovery
   - Score 100+ companies
   - Generate Eneve report

---

**Document Created**: February 25, 2026  
**Author**: Solstein Analysis Team  
**Status**: Ready for Implementation
