# Solstein: Comprehensive Data-Gathering Framework for PE Intelligence

> **Version**: 1.0  
> **Status**: Architecture Design  
> **Date**: Feb 20, 2026  
> **Scope**: Generalizable to ANY market vertical (energy, SaaS, fintech, biotech, manufacturing)

---

## 1. COMPREHENSIVENESS AUDIT

### What PE Firms Actually Care About (Ranked by Impact)

**Tier 1 - Deal Breakers (40% of decision weight)**
1. **Financial Health** - Can they survive? What's the burn rate, runway, unit economics?
2. **Team Quality** - Do they have the people to execute? Founder credibility, leadership depth?
3. **Market Position** - Are they winning? Growth vs competitors, customer quality, TAM addressable?

**Tier 2 - Significant Factors (40% of decision weight)**
4. **Technology Maturity** - Is the product defensible? Technical debt? AI-readiness?
5. **Growth Trajectory** - Consistent growth or declining? Net new revenue sources?
6. **Risk Indicators** - Customer concentration? Churn? Regulatory exposure? Key person risk?

**Tier 3 - Signal Boosters (20% of decision weight)**
7. **Strategic Positioning** - Partnerships, announced initiatives, market expansion?
8. **Innovation Velocity** - Patents, R&D spend, new products launched?
9. **Customer Quality** - Enterprise vs SMB? Logos? NPS? Retention?

### What Solstein Currently Gathers (LIMITED)
- ✅ Tech stack (GitHub)
- ✅ Engineering velocity (GitHub commits/contributors)
- ✅ Basic company info (Companies House)
- ❌ Financial data (revenue, growth, margins, burn rate)
- ❌ Team depth (leadership, key hires, retention)
- ❌ Customer base (logos, enterprise accounts, churn)
- ❌ Growth signals (funding announcements, partnerships)
- ❌ Risk factors (customer concentration, regulatory)
- ❌ Innovation signals (patents, product launches)
- ❌ Market position (competitor analysis, TAM)

### Critical Gaps (Priority Order)

| Gap | Why Critical | Ease | Cost | Priority |
|-----|-------------|------|------|----------|
| **Financial data** | Core to valuation | Hard | High | P0 |
| **Team intelligence** | Execution risk | Medium | Low | P0 |
| **Customer intelligence** | Revenue quality | Hard | Medium | P1 |
| **Growth signals** | Momentum | Easy | Free | P0 |
| **Risk indicators** | Downside protection | Medium | Free | P1 |
| **Innovation signals** | Defensibility | Medium | Low | P2 |
| **Market position** | Competitive advantage | Hard | Medium | P2 |

---

## 2. COMPREHENSIVE FACT MODEL

### Fact Taxonomy (150+ types organized by domain)

#### **DOMAIN A: FINANCIAL FACTS (25 types)**

| Fact Type | Description | Primary Source | Fallback | Confidence |
|-----------|-------------|-----------------|----------|------------|
| `annual_revenue` | Last 12 months revenue | SEC Filings / Accounts | News, Crunchbase | 0.95 |
| `revenue_growth_yoy` | % growth year-over-year | SEC Filings | News announcements | 0.90 |
| `gross_margin` | Gross profit / revenue | SEC Filings / Accounts | Crunchbase | 0.92 |
| `ebitda_margin` | EBITDA / revenue | SEC Filings | Accounts filings | 0.91 |
| `monthly_burn_rate` | Monthly cash burn | SEC Filings | Crunchbase | 0.88 |
| `cash_runway_months` | Months of runway @ burn | Calculated from above | News | 0.85 |
| `total_funding_raised` | Cumulative funding | Crunchbase / PitchBook | News | 0.93 |
| `last_funding_round` | Most recent round details | Crunchbase | News | 0.91 |
| `funding_velocity` | Months between rounds | Crunchbase | News | 0.89 |
| `customer_acquisition_cost` | CAC | SEC Filings (SaaS) | News | 0.85 |
| `lifetime_value` | LTV | SEC Filings (SaaS) | News | 0.85 |
| `ltv_cac_ratio` | LTV/CAC payback | Calculated | News | 0.83 |
| `annual_churn_rate` | % customer churn / year | SEC Filings | News | 0.87 |
| `net_revenue_retention` | NRR % | SEC Filings (SaaS) | Crunchbase | 0.88 |
| `customer_concentration_top10` | % revenue from top 10 | SEC Filings | News | 0.94 |
| `debt_to_equity` | Total debt / equity | SEC Filings / Accounts | News | 0.96 |
| `current_ratio` | Current assets / liabilities | SEC Filings / Accounts | News | 0.95 |
| `cash_position` | Cash on balance sheet | SEC Filings | News | 0.96 |
| `debt_facility_credit_lines` | Available credit | SEC Filings / News | News | 0.90 |
| `dividend_history` | Dividend payments | SEC Filings | News | 0.98 |
| `stock_price_history` | Historical stock prices | Public exchanges | Yahoo Finance | 0.98 |
| `market_cap` | Current market cap | Public exchanges | News | 0.97 |
| `eps_earnings_per_share` | EPS | SEC Filings | News | 0.96 |
| `r_and_d_spend` | R&D as % of revenue | SEC Filings | News | 0.93 |
| `capex_spending` | Capital expenditure | SEC Filings | News | 0.92 |

#### **DOMAIN B: TEAM & PEOPLE FACTS (28 types)**

| Fact Type | Description | Primary Source | Fallback | Confidence |
|-----------|-------------|-----------------|----------|------------|
| `founder_names` | Founder(s) names | LinkedIn, Crunchbase | News | 0.98 |
| `founder_background` | Founder education, prior exits | LinkedIn | News, Crunchbase | 0.92 |
| `founder_serial_entrepreneur` | Is founder serial? | LinkedIn | News | 0.90 |
| `founder_industry_experience` | Years in industry | LinkedIn | News | 0.88 |
| `ceo_name` | Current CEO | LinkedIn, News | Crunchbase | 0.98 |
| `ceo_background` | CEO experience, past roles | LinkedIn | News | 0.95 |
| `ceo_tenure_years` | How long as CEO | LinkedIn | News | 0.96 |
| `cto_name` | Chief Technology Officer | LinkedIn | News | 0.95 |
| `cto_background` | CTO experience, expertise | LinkedIn | News | 0.93 |
| `cfo_name` | Chief Financial Officer | LinkedIn | News | 0.95 |
| `cpo_name` | Chief Product Officer | LinkedIn | News | 0.90 |
| `vp_engineering_name` | VP Engineering | LinkedIn | News | 0.90 |
| `key_board_members` | Board composition | LinkedIn, Crunchbase | News | 0.94 |
| `board_diversity` | Gender, experience diversity | LinkedIn | News | 0.88 |
| `investor_reputation` | Lead investor quality | Crunchbase | News | 0.92 |
| `total_headcount` | Total employees | LinkedIn | News | 0.85 |
| `engineering_headcount` | # of engineers | LinkedIn | Glassdoor | 0.82 |
| `sales_headcount` | # of sales people | LinkedIn | Crunchbase | 0.80 |
| `support_headcount` | # of support staff | LinkedIn | Glassdoor | 0.75 |
| `headcount_growth_yoy` | % headcount growth / year | LinkedIn | News | 0.80 |
| `engineering_hiring_velocity` | Eng hires / month | LinkedIn | GitHub, Job postings | 0.78 |
| `executive_departures_12m` | Key people who left | LinkedIn | News | 0.90 |
| `executive_departures_context` | Why did they leave? | News, LinkedIn | Blind | 0.70 |
| `employee_retention_rate` | % employees staying 12m | Glassdoor | LinkedIn | 0.75 |
| `employee_satisfaction_score` | Glassdoor rating | Glassdoor | LinkedIn | 0.85 |
| `glassdoor_rating` | Company rating (1-5) | Glassdoor | LinkedIn | 0.88 |
| `employee_reviews_sentiment` | Tone of reviews | Glassdoor | LinkedIn, Blind | 0.80 |
| `key_person_risk_flag` | Are we dependent on CEO/Founder? | News, LinkedIn | Glassdoor | 0.72 |

#### **DOMAIN C: PRODUCT & TECHNOLOGY FACTS (32 types)**

| Fact Type | Description | Primary Source | Fallback | Confidence |
|-----------|-------------|-----------------|----------|------------|
| `primary_programming_language` | Main language used | GitHub | Website | 0.95 |
| `tech_stack` | Full tech stack | GitHub | Website, news | 0.93 |
| `cloud_provider` | AWS/Azure/GCP/other | GitHub, Website | News | 0.90 |
| `infrastructure_maturity` | Serverless vs on-prem vs hybrid | GitHub | News, Website | 0.85 |
| `ai_ml_adoption` | Uses AI/ML in product? | GitHub | News, Website | 0.80 |
| `ai_ml_maturity` | Breadth/depth of AI integration | GitHub | News, Product demo | 0.75 |
| `open_source_contributions` | Contributions to OSS | GitHub | News | 0.92 |
| `open_source_dependencies` | # of OSS dependencies | GitHub | SBOM tools | 0.98 |
| `security_scanning_tools` | Uses SAST/DAST/SCA tools | GitHub | News | 0.80 |
| `code_quality_metrics` | SonarQube, CodeFactor scores | GitHub | Code analysis | 0.85 |
| `technical_debt_assessment` | Estimated tech debt | GitHub + manual review | News | 0.70 |
| `monorepo_architecture` | Single or multi-repo? | GitHub | News | 0.88 |
| `deployment_frequency` | Deploys per day/week | GitHub | News | 0.85 |
| `mean_time_to_recovery` | MTTR for incidents | News | Website | 0.65 |
| `uptime_sla` | Advertised uptime | Website | News | 0.92 |
| `actual_uptime_status` | Reported uptime | Uptime monitoring | News | 0.88 |
| `api_documentation_quality` | Completeness of API docs | Website | GitHub | 0.80 |
| `sdk_availability` | Available SDKs | Website | GitHub | 0.92 |
| `number_of_patents` | Utility patents filed | USPTO | News | 0.96 |
| `patent_categories` | Tech areas of patents | USPTO | News | 0.94 |
| `trademark_registrations` | Registered trademarks | USPTO, WIPO | News | 0.95 |
| `product_roadmap_public` | Publicly shared roadmap? | Website | News | 0.92 |
| `number_of_products` | How many product lines? | Website | News | 0.90 |
| `flagship_product_age` | How old is main product? | News | Website | 0.88 |
| `last_major_release` | When was last major version? | GitHub | Website | 0.92 |
| `feature_velocity` | Features shipped per month | GitHub | News | 0.85 |
| `backwards_compatibility` | Maintains API compat? | GitHub | News | 0.85 |
| `accessibility_compliance` | WCAG compliance level | Website audit | News | 0.80 |
| `gdpr_compliance` | GDPR certified/compliant? | Website | News | 0.85 |
| `soc2_certification` | SOC 2 Type II certified? | Website | News | 0.95 |
| `iso_certifications` | ISO 27001, 9001, etc | Website | News | 0.96 |
| `product_demo_quality` | Product fit and finish | Demo review | Website | 0.70 |

#### **DOMAIN D: MARKET & COMPETITIVE FACTS (26 types)**

| Fact Type | Description | Primary Source | Fallback | Confidence |
|-----------|-------------|-----------------|----------|------------|
| `target_market_segment` | SMB / Mid-market / Enterprise | Website | News | 0.88 |
| `total_addressable_market_tam` | TAM size estimate | News, Industry reports | Estimates | 0.70 |
| `serviceable_addressable_market_sam` | SAM for this company | News, Industry reports | Estimates | 0.68 |
| `serviceable_obtainable_market_som` | SOM - realistic capture | Calculated | News | 0.65 |
| `market_growth_rate` | Industry growth % CAGR | Industry reports | Crunchbase | 0.78 |
| `market_position_rank` | Rank in market (1st, 2nd, etc) | News, reports | Estimates | 0.72 |
| `estimated_market_share` | % of addressable market | News, reports | Estimates | 0.68 |
| `primary_competitors` | Top 3-5 competitors | News, Website | Industry reports | 0.90 |
| `competitive_advantage_defensibility` | Moat strength | News, Product review | Analysis | 0.65 |
| `customer_base_quality` | Enterprise vs SMB ratio | News, LinkedIn | Website | 0.75 |
| `fortune_500_customers` | # of Fortune 500 customers | News | Website | 0.85 |
| `customer_logos` | Known customer list | Website | News | 0.88 |
| `industries_served` | How many verticals? | Website | News | 0.90 |
| `geographies_served` | Countries/regions | Website | News | 0.92 |
| `net_new_markets_expansion` | Markets entered in 12m | News | Crunchbase | 0.80 |
| `nps_score` | Net Promoter Score | Website, News | Estimates | 0.75 |
| `analyst_coverage` | Gartner, Forrester, etc reviews | Industry reports | News | 0.90 |
| `g2_rating` | G2 Crowd rating | G2.com | News | 0.88 |
| `captera_rating` | Captera rating | Captera | News | 0.87 |
| `glassdoor_pros_cons` | What customers/employees praise/criticize | Glassdoor, G2 | News | 0.80 |
| `social_media_following` | Twitter, LinkedIn followers | Social media | News | 0.95 |
| `monthly_website_traffic` | Estimated website visitors | SimilarWeb, Alexa | Website analytics | 0.80 |
| `search_volume_for_competitors` | Google search volume | Google Trends | SimilarWeb | 0.85 |
| `product_hunt_presence` | Presence on Product Hunt | Product Hunt | News | 0.92 |
| `review_sentiment` | Overall sentiment from reviews | G2, Captera, Glassdoor | News | 0.78 |
| `market_timing_window` | Is this the right time to enter? | News, Industry trends | Analysis | 0.60 |

#### **DOMAIN E: GROWTH & MOMENTUM FACTS (22 types)**

| Fact Type | Description | Primary Source | Fallback | Confidence |
|-----------|-------------|-----------------|----------|------------|
| `funding_announced_12m` | Funding announcements | News, Crunchbase | SEC filings | 0.94 |
| `funding_rumor_12m` | Funding rumors/speculation | News | Blind, Twitter | 0.50 |
| `strategic_partnerships_announced` | New partnerships in 12m | News | Website | 0.88 |
| `product_launches_12m` | New products/features launched | News, Website | GitHub releases | 0.85 |
| `market_expansion_announcements` | New geographies/verticals | News | Website | 0.85 |
| `acquisition_rumor` | Rumored to be acquired | News | Twitter, Blind | 0.45 |
| `acquisition_activity` | Company acquired someone else | News | Crunchbase | 0.96 |
| `ipo_announcements` | Filed for IPO | News | SEC filings | 0.98 |
| `dividend_announcement` | Announced dividend | News | SEC filings | 0.97 |
| `analyst_upgrade_downgrade` | Recent analyst changes | News | Reports | 0.90 |
| `insider_buying_selling` | Officer/director stock trades | SEC filings | News | 0.98 |
| `share_buyback_program` | Company buying back stock | News | SEC filings | 0.96 |
| `secondary_offering` | Selling additional shares | News | SEC filings | 0.97 |
| `debt_offering` | New debt issuance | News | SEC filings | 0.96 |
| `strategic_hires_announced` | Key talent joins | LinkedIn, News | Crunchbase | 0.88 |
| `international_expansion` | Entering new countries | News | Website | 0.85 |
| `sales_team_expansion` | Sales org growing | LinkedIn | Job postings | 0.80 |
| `channel_partner_announcements` | New reseller/partner deals | News | Website | 0.82 |
| `supply_chain_announcements` | Manufacturing, supplier news | News | Website | 0.85 |
| `sustainability_initiatives` | ESG announcements | News | Website | 0.85 |
| `sponsorship_investments` | Events, conferences sponsored | News | Website | 0.88 |
| `brand_relaunch_announcements` | Rebranding or pivot | News | Website | 0.92 |

#### **DOMAIN F: RISK & NEGATIVE SIGNALS (24 types)**

| Fact Type | Description | Primary Source | Fallback | Confidence |
|-----------|-------------|-----------------|----------|------------|
| `customer_concentration_top1` | % revenue from top customer | SEC filings | News | 0.94 |
| `customer_concentration_top5` | % revenue from top 5 | SEC filings | News | 0.94 |
| `key_customer_loss_announced` | Major customer left | News | SEC filings | 0.92 |
| `key_customer_concentration_risk` | Overdependent on one customer? | SEC filings | News | 0.90 |
| `supplier_concentration` | Overdependent on suppliers? | SEC filings | News | 0.88 |
| `regulatory_investigation` | Government investigation? | SEC filings, News | Legal databases | 0.95 |
| `legal_disputes_active` | Active lawsuits | Legal databases | News | 0.92 |
| `patent_litigation` | Patent disputes | USPTO | News | 0.94 |
| `data_breach_history` | Has company been breached? | News | HIPAA, SEC filings | 0.96 |
| `data_breach_materiality` | How severe was breach? | News | SEC filings | 0.90 |
| `security_vulnerability_disclosure` | Found critical vulns? | Security databases | News | 0.92 |
| `compliance_violation_history` | Failed audits, compliance issues | SEC filings, News | Regulatory databases | 0.93 |
| `environmental_violation` | EPA, environmental fines | News | Regulatory databases | 0.94 |
| `labor_dispute_history` | Union disputes, labor issues | News | NLRB filings | 0.88 |
| `executive_scandal` | Executive misconduct | News | Twitter | 0.85 |
| `product_recall_history` | Product recalled | News | CPSC, FDA | 0.96 |
| `quality_complaints` | Widespread quality issues | News, Reviews | Glassdoor | 0.78 |
| `reputational_crisis_history` | Public relations disaster | News | Social media | 0.82 |
| `competitive_disruption_risk` | New competitor threatening? | News | Analysis | 0.65 |
| `technology_obsolescence_risk` | Tech stack becoming legacy? | GitHub, News | Analysis | 0.68 |
| `market_saturation_risk` | Market becoming commoditized? | Industry reports | Analysis | 0.62 |
| `key_person_departure` | Founder or CEO left | News, LinkedIn | Blind | 0.94 |
| `talent_exodus` | Multiple key departures | LinkedIn, News | Glassdoor | 0.85 |
| `cash_crunch_signals` | Layoffs, restructuring | News | Blind, LinkedIn | 0.80 |

#### **DOMAIN G: STRATEGIC & VISION FACTS (18 types)**

| Fact Type | Description | Primary Source | Fallback | Confidence |
|-----------|-------------|-----------------|----------|------------|
| `company_mission_statement` | Stated mission | Website | News | 0.92 |
| `long_term_vision` | 5-10 year vision | Website, News | Interviews | 0.85 |
| `strategic_pillars` | 3-5 strategic focus areas | Website | News | 0.88 |
| `announced_transformation` | Major announced changes | News | Website | 0.90 |
| `pivot_risk` | Will company need to pivot? | News, Analysis | Reports | 0.60 |
| `market_trend_alignment` | Does strategy align with trends? | News, Reports | Analysis | 0.70 |
| `ceo_letter_to_shareholders` | CEO strategic messaging | SEC filings | Website | 0.92 |
| `investor_pitch_deck` | Raised deck (if available) | Crunchbase | News | 0.88 |
| `competitive_positioning_statement` | How company positions vs competitors | Website | News | 0.85 |
| `adjacent_market_ambitions` | Plans to expand into new markets | News | Website | 0.82 |
| `acquisition_strategy` | Organic growth vs M&A strategy | News | SEC filings | 0.80 |
| `international_strategy` | Plans for international | News | Website | 0.82 |
| `ecosystem_strategy` | Platform, API, partner strategy | Website | News | 0.85 |
| `sustainability_strategy` | ESG strategy | Website | News | 0.83 |
| `innovation_strategy` | R&D focus areas | News | Website | 0.80 |
| `organizational_restructuring` | Recent or planned reorg | News | LinkedIn | 0.85 |
| `cost_reduction_initiatives` | Efficiency programs | News | SEC filings | 0.88 |
| `diversity_and_inclusion_commitment` | DEI programs | Website | News | 0.85 |

---

## 3. AGENT ARCHITECTURE & PHASED ROLLOUT

### Current Agents (Phase 0)
- ✅ **GitHub Agent** - Tech stack, engineering velocity, code quality
- ✅ **Web Search Agent** - News, announcements, public signals
- ✅ **Companies House Agent** - UK financials, company registration

### New Agents (Priority Order)

#### **PHASE 1: Free & High-ROI (Month 1-2)**

| Agent | What It Gathers | Confidence | Cost | Priority | Est. Effort |
|-------|-----------------|-----------|------|----------|------------|
| **LinkedIn Scraper** | Founder backgrounds, key hires, headcount, employee reviews | 0.80-0.92 | Free | P0 | 2 weeks |
| **Crunchbase Free Tier** | Funding, investors, company basics | 0.88-0.93 | Free | P0 | 1 week |
| **SEC Filings (EDGAR)** | Revenue, financials, risk factors, insider trades | 0.95-0.98 | Free | P0 | 2 weeks |
| **Patent Agent (USPTO)** | Patents, trademarks, innovation signals | 0.94-0.98 | Free | P1 | 1 week |
| **News Aggregator** | Real-time announcements, partnerships, exec changes | 0.75-0.90 | Free | P0 | 3 weeks |
| **Job Postings Scraper** | Hiring velocity, team expansion, job descriptions | 0.75-0.85 | Free | P1 | 2 weeks |
| **Google Trends** | Search volume trends, market interest | 0.80-0.88 | Free | P2 | 1 week |
| **Public Website Scraper** | Company info, tech stack (homepage), blog/announcements | 0.70-0.88 | Free | P1 | 1 week |

**Phase 1 Effort**: ~13 weeks, $0 cost

#### **PHASE 2: Low-Cost & High-Value (Month 3-4)**

| Agent | What It Gathers | Confidence | Cost | ROI | Est. Effort |
|-------|-----------------|-----------|------|-----|------------|
| **Crunchbase Pro** | Company financials, exit history, term sheet data | 0.85-0.92 | $500/mo | 9x | 1 week |
| **NewsGuard API** | News credibility filtering | 0.85-0.95 | $200/mo | High | 3 days |
| **Glassdoor API** | Employee reviews, sentiment, ratings | 0.75-0.88 | Free with limits | 5x | 1 week |
| **G2 Reviews API** | Customer reviews, sentiment, ratings | 0.78-0.92 | Free with limits | 5x | 1 week |
| **Domain Age & History** | Domain registration, history, reputation | 0.90-0.98 | Free/low | 3x | 3 days |
| **Tech Stack Analyzer** | Builds API, BuiltWith, Wappalyzer | 0.85-0.95 | Low/free | 4x | 1 week |
| **Uptime Monitoring** | Real-time uptime checks, SLA compliance | 0.95-0.98 | $50/mo | 3x | 3 days |
| **Shodan/SSL Cert Analysis** | Security posture, TLS certs, open ports | 0.85-0.95 | Low | 3x | 1 week |

**Phase 2 Effort**: ~7 weeks, $750/mo cost

#### **PHASE 3: Enterprise & Specialized (Month 5+)**

| Agent | What It Gathers | Confidence | Cost | ROI | Est. Effort |
|-------|-----------------|-----------|------|-----|------------|
| **PitchBook API** | PE-specific data, exits, comparables | 0.92-0.98 | $10k/yr | Very high | 2 weeks |
| **CapitalIQ (S&P)** | Financial modeling, multiples, comparables | 0.96-0.99 | $15k+/yr | Very high | 2 weeks |
| **Owler API** | Revenue estimates, org charts | 0.70-0.80 | Low | Medium | 1 week |
| **Preqin Alternative Data** | Exit data, fund performance | 0.95-0.98 | $20k+/yr | High | 2 weeks |
| **FactSet** | Real-time financial data, transcripts | 0.98-0.99 | $15k+/yr | Very high | 2 weeks |
| **Court Records API** | Legal disputes, litigation | 0.92-0.96 | Medium | 3x | 1 week |
| **Social Sentiment API** | Twitter, social media sentiment | 0.60-0.75 | Medium | 2x | 1 week |
| **LinkedIn API (Enterprise)** | Rich company profiles, employee data | 0.85-0.95 | $15k+/yr | High | 2 weeks |

**Phase 3 Effort**: ~14 weeks, $75k+/yr cost

### Agent Fallback Strategy

**Every agent must have a fallback chain:**

```
Primary Source → Fallback 1 → Fallback 2 → Manual Research Flag
   (0.95 confidence)    (0.80)       (0.65)     (for analyst)
```

Example: **Revenue Data**
1. **Primary**: SEC Edgar API (0.98 confidence)
2. **Fallback 1**: Crunchbase Pro (0.85 confidence)  
3. **Fallback 2**: News aggregator announcements (0.65 confidence)
4. **Fallback 3**: Flag for manual research (analyst review)

---

## 4. CONFIDENCE SCORING MODEL

### Multi-Source Confidence Calculation

When a fact comes from multiple sources with different credibilities, use **Bayesian weighted averaging**:

```
Confidence = (Source1_Credibility × Source1_Weight) + (Source2_Credibility × Source2_Weight) + ...
             ÷ Total_Weight
             
Where:
- Source credibility = inherent reliability (SEC filing 0.99, news 0.65, etc.)
- Weight = freshness factor (today 1.0, 6 months ago 0.8, 1 year ago 0.5)
- Minimum 2 sources recommended for confidence > 0.85
```

### Real Example: Revenue Estimation

**Scenario**: We have 3 data points for Company X's revenue:
- SEC Filing (Q3 2025): $50M (credibility 0.99, age 1 month)
- Crunchbase Report: $48M (credibility 0.85, age 2 months)
- News Article (funding announcement): "$50M+ annual run rate" (credibility 0.65, age 3 weeks)

**Calculation**:
```
Weights:
- SEC: 1.0 (1 month old) × 0.99 credibility = 0.99
- Crunchbase: 0.95 (2 months old) × 0.85 credibility = 0.81
- News: 0.98 (3 weeks old) × 0.65 credibility = 0.64

Weighted Average = (0.99 + 0.81 + 0.64) / 3 = 0.81 confidence

Final Fact: Revenue = $49.3M (average) ± Confidence 0.81
```

### Contradiction Detection Rules

**Flag for human review if:**
1. Sources disagree by >20% on factual metrics (revenue, headcount, growth)
2. Credibility-weighted sources contradict fundamentally
3. Recent source contradicts older source on core fact
4. Multiple sources from different backgrounds agree on something unusual

**Example Contradiction**:
- SEC Filing says "Customer concentration top 10 = 35%" (0.96 confidence)
- Crunchbase says "No major customer concentration risk" (0.70 confidence)
- → Flag for analyst: "Potential customer concentration risk - sources conflict"

### Freshness Penalties

Data quality degrades with age. Apply freshness multiplier:

| Age | Multiplier | Reasoning |
|-----|-----------|-----------|
| 0-1 week | 1.0 | Fresh, assume accurate |
| 1-4 weeks | 0.98 | Still very recent |
| 1-3 months | 0.95 | Recent but potentially stale |
| 3-6 months | 0.85 | Moderately stale |
| 6-12 months | 0.70 | Significantly outdated |
| 1-2 years | 0.40 | Old, high change risk |
| 2+ years | 0.10 | Very old, likely inaccurate |

---

## 5. SIGNAL EXTRACTION RULES (Facts → Signals)

### Signal = Business Insight (extracted from multiple facts)

**Example 1: Engineering Maturity Signal**
```
Signal: engineering_maturity_score (0.0-10.0)

Inputs:
- Tech stack modernity (0-1.0): Language, frameworks, age
- Code quality (0-1.0): SonarQube score, test coverage
- Deployment frequency (0-1.0): Deploys per day
- AI/ML adoption (0-1.0): % of codebase using ML
- Open source engagement (0-1.0): OSS contributions
- Engineering team size (0-1.0): # engineers vs revenue

Calculation:
score = (tech_stack*0.15 + code_quality*0.20 + deploy_freq*0.20 + ai_adoption*0.15 + oss*0.15 + team_size*0.15)

Example: (0.8 + 0.75 + 0.85 + 0.60 + 0.70 + 0.80) = 7.5/10 = "Good"
```

**Example 2: Financial Health Signal**
```
Signal: financial_health_score (0.0-10.0)

Inputs:
- Revenue growth YoY (0-1.0)
- Gross margin (0-1.0) 
- Cash runway (0-1.0): Months / 24
- Customer concentration (0-1.0): 1 - (top_10_pct / 100)
- Debt to equity ratio (0-1.0): (1 - ratio/10) clamped
- Funding status (0-1.0): Recent funding = higher score

Example: (0.90 + 0.85 + 0.75 + 0.70 + 0.80 + 0.95) / 6 = 8.3/10 = "Strong"
```

**Example 3: Team Strength Signal**
```
Signal: team_strength_score (0.0-10.0)

Inputs:
- Founder credibility (0-1.0): Prior exits, experience
- Leadership depth (0-1.0): How many C-suite hires?
- Hiring velocity (0-1.0): # of hires per month
- Employee retention (0-1.0): % staying 12 months
- Employee satisfaction (0-1.0): Glassdoor rating / 5
- Key person risk (0-1.0): 1 - overdependence on founder

Example: (0.85 + 0.70 + 0.80 + 0.75 + 0.72 + 0.60) / 6 = 7.4/10 = "Good"
```

**Example 4: Growth Momentum Signal**
```
Signal: growth_momentum_score (0-10.0)

Inputs:
- Revenue growth rate (0-1.0): % growth, capped
- Funding activity (0-1.0): Recent funding = 1.0
- New product launches (0-1.0): # launched / 12
- Market expansion (0-1.0): New geographies/verticals
- Customer acquisition (0-1.0): CAC payback < 12 months
- Feature velocity (0-1.0): Features per month

Example: (0.75 + 0.90 + 0.80 + 0.70 + 0.65 + 0.70) / 6 = 7.5/10 = "Good"
```

---

## 6. PE ANALYST WORKFLOW & DRILL-DOWN JOURNEY

### The PE Decision Journey

```
STEP 1: Initial Screening
  Analyst clicks "Analyze Market"
  → Solstein gathers 150+ facts from all agents (5-10 seconds)
  → Returns summary scores for each company

STEP 2: Quick Triage
  PE analyst sees:
  ┌─────────────────────────────────────────────┐
  │ Company: Acme Energy Software              │
  │ Overall Attractiveness: 7.2 / 10            │
  │ ├─ Engineering Maturity: 8.1 ✓              │
  │ ├─ Financial Health: 6.8 ⚠                  │
  │ ├─ Team Strength: 7.5 ✓                     │
  │ ├─ Growth Momentum: 7.9 ✓                   │
  │ └─ Risk Indicators: 6.2 ⚠                   │
  │                                              │
  │ [Why is Financial Health low?] ← Click      │
  └─────────────────────────────────────────────┘

STEP 3: Deep Dive on Specific Signal
  Analyst clicks "Why is Financial Health low?"
  → Solstein shows:
  
  ┌──────────────────────────────────────────────────┐
  │ Financial Health: 6.8 / 10                        │
  │                                                    │
  │ Contributing Factors (weighted):                  │
  │ ├─ Revenue Growth: 8.5/10 ✓                      │
  │ │  └─ Q3 2025: $50M (+45% YoY)                   │
  │ │     Sources: SEC Filing (0.99 confidence)      │
  │ │                                                 │
  │ ├─ Gross Margin: 6.2/10 ⚠ ← LOW                 │
  │ │  └─ Current: 42% (industry avg 55%)            │
  │ │     Sources: SEC Filing (0.99), Crunchbase     │
  │ │                                                 │
  │ ├─ Cash Runway: 5.8/10 ⚠ ← LOW                  │
  │ │  └─ Estimated: 14 months @ current burn        │
  │ │     Burn rate: $3.5M/month                     │
  │ │     Cash on hand: $49M                         │
  │ │     Sources: SEC Filing (0.98), News (0.75)   │
  │ │                                                 │
  │ ├─ Customer Concentration: 7.0/10 ⚠            │
  │ │  └─ Top 10 customers = 38% of revenue         │
  │ │     Risk: Medium-high concentration           │
  │ │     Sources: SEC Filing (0.96 confidence)      │
  │ │                                                 │
  │ ├─ Debt-to-Equity: 8.2/10 ✓                     │
  │ │  └─ Ratio: 0.35 (healthy)                     │
  │ │     Sources: SEC Filing (0.96 confidence)      │
  │ │                                                 │
  │ └─ Funding Status: 8.9/10 ✓                     │
  │    └─ Last round: Series D, $25M (2 months ago) │
  │       Investors: Tier 1 VCs                     │
  │       Sources: Crunchbase (0.92), News (0.88)   │
  │                                                  │
  │ [See all sources] [View risk factors]           │
  └──────────────────────────────────────────────────┘

STEP 4: Investigate Specific Risk
  Analyst notices low margin and clicks "Why is margin only 42%?"
  → Solstein shows:
  
  ┌──────────────────────────────────────────────────┐
  │ Gross Margin: 42% (vs 55% industry average)     │
  │                                                    │
  │ Possible Explanations:                           │
  │ ├─ High professional services revenue (lower GM) │
  │ ├─ New market with heavy investment             │
  │ ├─ Pricing pressure from competition            │
  │ ├─ Inefficient delivery model (technical risk)  │
  │                                                    │
  │ Related Facts from Data:                         │
  │ ├─ Services revenue % of total: 35% (from 10-K) │
  │ ├─ New market expansion: 4 countries in 12m     │
  │ ├─ Major competitor price drop: 6 months ago    │
  │ ├─ COGS per customer: $X (from financials)      │
  │                                                    │
  │ Recommendation:                                   │
  │ → Margin is depressed by services mix, not      │
  │   operational inefficiency. Watch for SaaS      │
  │   margin expansion as services decline.         │
  │                                                    │
  │ [See financials detail] [Market comparables]    │
  └──────────────────────────────────────────────────┘

STEP 5: Cross-Reference with Team Intelligence
  Analyst wants to understand who's executing the strategy
  → Clicks on "Team Strength" signal
  → Sees:
  
  ┌──────────────────────────────────────────────────┐
  │ Team Strength: 7.5 / 10                          │
  │                                                    │
  │ Leadership:                                       │
  │ ├─ CEO: Jane Smith (serial founder, 2 exits)    │
  │ │  └─ Tenure: 3 years. Prior: CTO at Company X  │
  │ │  └─ LinkedIn: 2.5k followers                  │
  │ │                                                │
  │ ├─ CTO: Bob Johnson (Google, Apple, 15 yrs)    │
  │ │  └─ Tenure: 18 months (hired from Google)     │
  │ │  └─ Strong AI/ML background                   │
  │ │                                                │
  │ ├─ CFO: Sarah Lee (BigCorp CFO, 20 yrs exp)   │
  │ │  └─ Tenure: 6 months (strategic hire)         │
  │ │  └─ Public company experience                 │
  │ │                                                │
  │ └─ VP Engineering: 5 engineers at company       │
  │    └─ Hiring: 2-3 per month (strong velocity)  │
  │                                                    │
  │ People Risk Factors:                             │
  │ ├─ Key person dependency: CEO (high risk)       │
  │ ├─ Recent departures: None in 12m (good)        │
  │ ├─ Employee satisfaction: 4.1/5 Glassdoor       │
  │ ├─ Retention: 89% (vs 85% industry avg)         │
  │                                                    │
  │ [Org chart] [Full bios] [Hiring analytics]      │
  └──────────────────────────────────────────────────┘

STEP 6: Final Considerations - Risk Assessment
  Analyst clicks "Risk Indicators" to assess downside
  → Sees:
  
  ┌──────────────────────────────────────────────────┐
  │ Risk Indicators: 6.2 / 10 (Moderate Risk)       │
  │                                                    │
  │ 🔴 HIGH RISK FACTORS:                            │
  │ ├─ Customer concentration (38% top 10)          │
  │ │  └─ Mitigation: Actively hired new sales team │
  │ │  └─ Trend: Concentration improving (42%→38%)  │
  │ │                                                │
  │ └─ Tech debt assessment (estimated moderate)    │
  │    └─ Mitigations: New CTO from Google          │
  │    └─ Recent tech stack modernization started   │
  │                                                    │
  │ 🟡 MEDIUM RISK FACTORS:                         │
  │ ├─ Key person risk (CEO dependent)              │
  │ ├─ Cash runway (14 months, above minimum 12)   │
  │ └─ Competitive pressure (new feature launches) │
  │                                                    │
  │ 🟢 LOW RISK FACTORS:                            │
  │ ├─ No regulatory issues (clean compliance)      │
  │ ├─ No data breaches or security incidents       │
  │ ├─ Stable board composition                     │
  │ └─ Strong investor backing                      │
  │                                                    │
  │ [See all risk factors] [Comparables risk]       │
  └──────────────────────────────────────────────────┘

STEP 7: Generate Investment Thesis
  Analyst synthesizes all data:
  
  ✅ BULL CASE:
     - Strong revenue growth (45% YoY)
     - Excellent team (serial founder, world-class CTO)
     - High engineering maturity (8.1/10)
     - Series D funding validates market
  
  ⚠️  RISKS TO MONITOR:
     - Customer concentration (mitigating with sales expansion)
     - Margin pressure (expect to improve as services decline)
     - Key person risk on CEO
     - Tech debt being addressed
  
  💰 VALUATION FRAMEWORK:
     - Comparable SaaS multiples: 8-12x ARR
     - Solstein estimated ARR: $48M-52M
     - Fair value range: $384M - $624M
     - Current valuation (from Series D): $500M (reasonable)
```

---

## 7. COMPREHENSIVE DOCUMENTATION STRUCTURE

### Document 1: Data Dictionary (150+ Facts)
**Location**: `.claude/DATA_DICTIONARY.md`
- Complete list of all fact types
- For each: name, description, primary source, fallback, baseline confidence, freshness multiplier
- Organized by domain (Financial, Team, Product, Market, Growth, Risk, Strategic)
- Used by: Developers implementing agents

### Document 2: Agent Implementation Specifications
**Location**: `.claude/AGENT_SPECS.md`
- One section per agent (GitHub, LinkedIn, SEC, Patents, News, etc.)
- What facts does it gather?
- API endpoints / authentication
- Rate limits and cost
- Confidence levels by fact type
- Fallback strategy when API fails
- Example fact extraction
- Used by: Developers building agents

### Document 3: Fact-to-Signal Mapping Rules
**Location**: `.claude/SIGNAL_EXTRACTION_RULES.md`
- 50+ signals (engineering_maturity, financial_health, team_strength, growth_momentum, risk_profile, etc.)
- For each signal:
  - Formula / calculation method
  - Input facts (with weights)
  - Min/max thresholds
  - Interpretation guide (what score means)
  - Examples
- Used by: Developers and analysts

### Document 4: Confidence Calculation Guide
**Location**: `.claude/CONFIDENCE_CALCULATION_GUIDE.md`
- Multi-source confidence formula (Bayesian averaging)
- Freshness penalty table
- Contradiction detection rules
- Human review escalation criteria
- Real examples from actual data
- Used by: Developers and data quality team

### Document 5: PE Analyst Workflow Guide
**Location**: `.claude/PE_ANALYST_GUIDE.md`
- How to use the drill-down API
- What each signal means in PE context
- How to interpret confidence levels
- Common questions and how to answer them
- Case studies
- Used by: PE analysts and operators

### Document 6: Implementation Roadmap
**Location**: `.claude/IMPLEMENTATION_ROADMAP.md`
- Phase 1 (Month 1-2): 8 free agents, $0 cost, 13 weeks
- Phase 2 (Month 3-4): 8 low-cost APIs, $750/mo, 7 weeks
- Phase 3 (Month 5+): 8 enterprise APIs, $75k+/yr, 14 weeks
- Dependencies, milestones, team requirements
- Used by: Project planning and execution

---

## 8. IMPLEMENTATION ROADMAP

### Phase 1: Foundation (Weeks 1-13, $0 cost)

**Week 1-2: LinkedIn Agent**
- Scrape founder profiles, key hires, headcount trends
- Gather employee reviews (Glassdoor integration)
- Extract: `founder_background`, `ceo_background`, `total_headcount`, `engineering_headcount`, `key_departures`, `employee_satisfaction`
- Test: Extract 10 companies, validate data

**Week 3: Crunchbase Free Tier**
- Company basics, funding history, investor profiles
- Extract: `total_funding_raised`, `last_funding_round`, `funding_velocity`, `investor_reputation`
- Test: Compare with manual data

**Week 4-5: SEC EDGAR**
- Parse 10-K, 10-Q filings (public US companies)
- Extract: `annual_revenue`, `gross_margin`, `ebitda_margin`, `customer_concentration`, `debt_ratios`, `insider_trades`
- Test: 20 public companies

**Week 6: USPTO Patents**
- Search patent database, count patents, extract categories
- Extract: `number_of_patents`, `patent_categories`, `trademark_registrations`
- Test: 10 companies

**Week 7-9: News Aggregator**
- Scrape HN, Techcrunch, Crunchbase News, Company News
- Parse for: funding, partnerships, exec changes, announcements
- Extract: `funding_announced`, `strategic_partnerships`, `product_launches`, `market_expansion`, `acquisition_activity`
- Test: Real-time tracking on 5 companies

**Week 10-11: Job Postings Scraper**
- Scrape LinkedIn Jobs, Indeed, Wellfound for company job postings
- Extract: `engineering_hiring_velocity`, `sales_hiring_velocity`, `job_level_distribution`
- Test: Hiring trend extraction

**Week 12: Google Trends + Domain History**
- Track search volume trends, domain registration history
- Extract: `search_volume_trends`, `domain_age`, `domain_reputation_history`
- Test: Trend detection

**Week 13: Integration & Testing**
- Connect all agents to coordinator
- Test parallel execution
- Deploy to staging

**Deliverables**:
- 8 agent implementations
- Data Dictionary (Phase 1 facts)
- 100+ facts gathering for test companies
- Phase 1 integration tests passing
- Agent Specs document

**Metrics**:
- Successfully gather 80+ facts per company
- Average execution time: < 30 seconds per company
- Confidence scores accurate to within 10% of manual validation

---

### Phase 2: Enrichment (Weeks 14-20, $750/month)

**Week 14: Crunchbase Pro Integration**
- Upgrade to Pro tier for richer data
- Extract: financial estimates, exit history, comparables
- Integrate: revenue estimates, valuation data

**Week 15: Glassdoor & G2 Reviews**
- Systematic review scraping with sentiment analysis
- Extract: overall ratings, pros/cons, employee satisfaction trends
- Analyze: review sentiment over time

**Week 16: Tech Stack Detection**
- Integrate Builds API, BuiltWith, Wappalyzer
- Extract: detailed tech stack, infrastructure providers, hosting
- Validate against GitHub data

**Week 17: Uptime Monitoring**
- Real-time monitoring of company SLAs
- Extract: uptime percentage, incident history
- Alert on significant outages

**Week 18: Security Analysis**
- SSL cert analysis, Shodan scanning
- Extract: security posture, TLS compliance, open ports
- Risk flag dangerous configurations

**Week 19-20: Integration & Analysis**
- Connect new agents to coordinator
- Confidence score validation
- Signal extraction testing
- Load test with full company set (100+ companies)

**Deliverables**:
- 8 new low-cost agents
- Enhanced Data Dictionary (Phase 1 + 2)
- 120+ facts per company
- Confidence validation report
- Signal extraction rules (draft)
- Updated Agent Specs

**Metrics**:
- 95% data quality validation
- <5% data gaps per company
- Average 45 second execution per company
- Confidence scores 0.80+ for 85% of facts

---

### Phase 3: Enterprise (Weeks 21-34, $75k+/year)

**Week 21-22: PitchBook Integration**
- PE-specific data (exits, comparables, fund performance)
- Extract: comparable transaction data, valuation multiples

**Week 23-24: CapitalIQ / S&P Integration**
- Financial modeling, real-time market data
- Extract: company metrics, financial transcripts, guidance

**Week 25-26: Advanced Financial Data**
- FactSet, Bloomberg terminal data (if available)
- Extract: real-time pricing, analyst estimates, guidance

**Week 27: Court Records & Legal Data**
- Litigation tracking, regulatory filings
- Extract: active disputes, fines, compliance issues

**Week 28: LinkedIn Enterprise API**
- Rich org charts, employee profiles, skill mapping
- Extract: detailed org structure, skill gaps, succession risk

**Week 29-30: Social Sentiment Analysis**
- Twitter, Reddit, Blind sentiment tracking
- Extract: market sentiment, employee sentiment, investor sentiment

**Week 31-32: Advanced Competitor Intelligence**
- Build vs Buy decision modeling
- Market share estimation
- Competitive positioning analysis

**Week 33-34: Full Integration & Optimization**
- Connect all 24 agents to coordinator
- Performance optimization
- Multi-company batch processing
- Load test with 1000+ companies

**Deliverables**:
- 8 enterprise agents
- Complete Data Dictionary (all 150+ facts)
- 150+ facts per company
- All signal extraction rules finalized
- PE Analyst Guide (complete)
- Confidence Calculation Guide (complete)
- Full implementation documentation
- API documentation

**Metrics**:
- 98%+ data quality
- <1% data gaps
- Average 60 second execution (100+ companies)
- Confidence scores 0.85+ for 90% of facts
- Zero false positives on risk flags

---

## 9. USAGE EXAMPLES: From Data to Decision

### Example 1: Evaluating "TechStarUp Energy"

**Scenario**: PE firm evaluating acquisition of TechStarUp Energy

**Command**: `analyze_company("TechStarUp Energy", market="energy", deep_dive=true)`

**Execution Time**: 45 seconds

**Output Summary**:
```
COMPANY: TechStarUp Energy
ATTRACTIVENESS: 7.8 / 10 (Strong)

SIGNALS:
├─ Engineering Maturity: 8.5 / 10 (Excellent)
├─ Financial Health: 7.2 / 10 (Good)
├─ Team Strength: 7.9 / 10 (Good)
├─ Growth Momentum: 8.1 / 10 (Excellent)
└─ Risk Indicators: 6.8 / 10 (Moderate)

DATA SOURCES USED: 18/24 agents successful
├─ GitHub: 12 facts (0.92 avg confidence)
├─ SEC EDGAR: 8 facts (0.97 avg confidence)
├─ LinkedIn: 15 facts (0.85 avg confidence)
├─ Crunchbase: 7 facts (0.88 avg confidence)
├─ News: 14 facts (0.78 avg confidence)
├─ Patents: 6 facts (0.96 avg confidence)
└─ ... [18 agents total]

DATA QUALITY: 92% (137/150 facts gathered)
CONFIDENCE: 0.86 average
LAST UPDATED: 2 minutes ago
```

**PE Analyst Query**: "Why is this company worth acquiring now?"

**Solstein Drill-Down**:
```
INVESTMENT THESIS:

BULL CASE (Weight: 70% confidence):
✓ Revenue: $62M (+52% YoY) - Strong growth in expanding TAM
✓ Team: World-class technical leadership (CTO ex-Google, CEO ex-Uber)
✓ Engineering: 8.5/10 - Modern tech stack, AI/ML integration, 0.1% technical debt
✓ Growth Momentum: New market expansion (3 countries in 12m), partnerships with Tier-1 customers
✓ Funding: Series C $18M (6 months ago) validates market - fresh capital

RISK CASE (Weight: 30% confidence):
⚠ Customer Concentration: Top 5 = 42% of revenue (vs 35% target)
  → Mitigated by: Active hiring of sales team (+40% in 12m)
  → Trend: Improving (50% → 42% in last 18m)
⚠ Cash Runway: 24 months (healthy but watch burn rate)
  → Context: Burn is decreasing (6% reduction QoQ)
⚠ Market Risk: New entrant from BigTech company
  → Opportunity: Acquisition target for strategic buyer

COMPARABLE VALUATION:
Current: $185M (Series C valuation)
Market Comparables: 10-14x ARR on revenue
Your potential entry: $200-250M
Exit potential (5yr): $800M-1.2B (5-7x return)

WHY NOW:
1. Growth is accelerating (40% → 52% YoY)
2. Technical foundation strong (new CTO freshly optimized)
3. Team complete (recently hired CFO for institutional finance)
4. Market timing: TAM growing, competitive moat forming
5. Valuation: Fair relative to growth + risk profile
```

**Result**: PE firm decides to pursue acquisition, requests detailed vendor diligence plan

---

### Example 2: Portfolio Monitoring

**Scenario**: PE firm holding 5 portfolio companies, needs quarterly health check

**Command**: `monitor_portfolio(companies=["CompanyA", "CompanyB", "CompanyC", "CompanyD", "CompanyE"], period="quarterly")`

**Execution Time**: 3 minutes (all companies in parallel)

**Output**: Scorecard

```
PORTFOLIO HEALTH SCORECARD (Q1 2026)

                Current  Q4 2025  Trend  Alert
CompanyA        8.1/10   7.9/10   ↑     None
CompanyB        6.2/10   6.8/10   ↓     ⚠ Retention declining
CompanyC        7.5/10   7.2/10   ↑     None
CompanyD        5.8/10   5.9/10   ↓     🔴 Cash runway < 18m
CompanyE        7.9/10   7.6/10   ↑     None

CHANGES THIS QUARTER:
├─ CompanyA
│  ├─ Revenue: +48% YoY (was +42%) ✓
│  ├─ Headcount: +22% (hiring accelerating) ✓
│  └─ No material changes
│
├─ CompanyB ⚠
│  ├─ Revenue: +28% YoY (was +35%) ⚠ SLOWING
│  ├─ Employee retention: 85% (was 91%) ⚠ DECLINING
│  ├─ Key departures: 2 engineers, 1 PM in 30 days
│  └─ Action: Recommend organizational health check
│
├─ CompanyC
│  ├─ Revenue: +35% YoY ✓
│  ├─ Funding: Series B $12M announced ✓
│  └─ New CTO hire (ex-Stripe) ✓
│
├─ CompanyD 🔴 
│  ├─ Cash runway: 16 months (was 19m) 🔴 CRITICAL
│  ├─ Burn rate: $2.1M/month (increasing) 🔴
│  ├─ Growth: +18% YoY (slowing) ⚠
│  └─ Action: URGENT - Fundraising or M&A needed within 6 months
│
└─ CompanyE
   ├─ Revenue: +52% YoY ✓
   ├─ Funding: Series C $25M (announced) ✓
   └─ Team: Hiring above plan ✓
```

**Result**: PE team escalates CompanyD to investment committee for urgent strategy session

---

## 10. SUCCESS CRITERIA & KPIs

### Data Quality Metrics
- [ ] 95%+ fact coverage per company (>140 of 150 facts)
- [ ] 0.85+ average confidence across all facts
- [ ] <5% of facts require manual research escalation
- [ ] <1% contradiction rate (sources disagreeing)
- [ ] 98%+ accuracy on verified facts (vs. manual audit)

### Performance Metrics
- [ ] <60 seconds execution per company (Phase 3)
- [ ] <2 minutes batch processing (5 companies)
- [ ] <5 minutes processing (50 companies)
- [ ] 99.9% agent availability (failover chains working)
- [ ] <1% data loss due to API failures

### Adoption Metrics
- [ ] PE analysts using drill-down on 80%+ of decisions
- [ ] 70%+ of analysis recommendations match human judgment
- [ ] 50%+ reduction in manual research time
- [ ] <1 day from question to data-driven answer

### Business Impact
- [ ] 3-5x faster deal screening (faster Go/No-Go decisions)
- [ ] Better risk assessment (catch 80%+ of risks pre-investment)
- [ ] Portfolio monitoring automated (free up analyst time)
- [ ] Data-driven investment theses (vs subjective)

---

## Summary

This framework enables Solstein to gather **150+ comprehensive facts** about ANY company in ANY market vertical, generating **50+ actionable signals** for PE decision-making. 

**By Phase 3**, you'll have:
- ✅ 8 free agents (Phase 1)
- ✅ 8 low-cost agents (Phase 2)
- ✅ 8 enterprise agents (Phase 3)
- ✅ 150+ fact types
- ✅ 50+ signals
- ✅ Confidence scoring
- ✅ Drill-down transparency
- ✅ PE analyst workflows

**Cost Progression**: $0 (MVP) → $750/mo (enriched) → $75k+/yr (complete)

**Ready to build?** Start with Phase 1 (free, high-impact agents) and validate the model before committing to expensive APIs.
