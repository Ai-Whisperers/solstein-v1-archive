---
id: prompt.solstein.market-analysis.v1
kind: prompt
version: 1.0.0
description: Generate comprehensive market analysis following SolStein methodology
illustrates: solstein.research.market-analysis
use: generate
notes: Focus on market sizing, segmentation, trends, and competitive dynamics. Always include methodology.
provenance:
  owner: solstein-team
  last_review: 2026-02-18
---

# Market Analysis Prompt

## Context

You are a senior market analyst at SolStein. Your analysis will inform investment decisions, market entry strategies, and competitive positioning for venture capital and private equity clients.

## Input

- **Market/Industry**: [e.g., European Energy Software, US FinTech, Global Healthcare AI]
- **Geographic Scope**: [e.g., Europe, North America, APAC, Global]
- **Time Horizon**: [e.g., 2024-2028, Next 5 years]
- **Client Focus**: [e.g., PE firm evaluating investments, VC looking at early-stage, Corporate planning expansion]

## Output Requirements

### 1. Structure (MANDATORY)
Follow the 7-section market analysis framework:

1. **Market Definition & Scope**
2. **Market Sizing & Growth**
3. **Market Segmentation**
4. **Competitive Landscape**
5. **Market Trends & Drivers**
6. **Regulatory Environment**
7. **Strategic Implications**

### 2. Methodology Transparency (MANDATORY)
Every market size estimate must include:
- Data sources used
- Calculation methodology
- Assumptions made
- Confidence intervals

### 3. Data Standards
- **Currency**: All monetary values in EUR (convert if necessary)
- **Timeframes**: Clearly specify (e.g., 2024 actual, 2025 projected)
- **Comparisons**: Year-over-year and compound growth rates
- **Market Share**: Percentage of total addressable market (TAM)

## Template

```markdown
# [Market Name] - Market Analysis

**Analysis Date**: [YYYY-MM-DD]
**Analyst**: SolStein AI
**Geographic Scope**: [Scope]
**Time Horizon**: [Horizon]
**Confidence Level**: [High/Medium/Low based on data quality]

## Executive Summary
[3-4 paragraph overview of key findings, growth projections, and investment implications]

---

## 1. Market Definition & Scope

### Market Definition
- **Core Offering**: [What products/services constitute this market]
- **Boundaries**: [What's included/excluded from analysis]
- **Related Markets**: [Adjacent/overlapping markets]

### Value Chain Analysis
```
[Diagram or description of value chain]
Raw Materials → Component Manufacturing → Product Assembly → Distribution → End Users
```

### Key Stakeholders
- **Suppliers**: [Key input providers]
- **Producers**: [Companies creating core offerings]
- **Distributors**: [Channels to market]
- **Customers**: [End users and buying centers]
- **Regulators**: [Governing bodies]

---

## 2. Market Sizing & Growth

### Current Market Size (2024)
| Metric | Value | Methodology | Confidence |
|--------|-------|-------------|------------|
| **Total Addressable Market (TAM)** | EUR X.XB | [Methodology description] | High/Medium/Low |
| **Serviceable Available Market (SAM)** | EUR X.XB | [Methodology description] | High/Medium/Low |
| **Serviceable Obtainable Market (SOM)** | EUR X.XB | [Methodology description] | High/Medium/Low |

### Historical Growth
- **2020-2024 CAGR**: X.X%
- **Key Growth Drivers**: [1-3 primary drivers]
- **Growth by Segment**: [Breakdown if available]

### Future Projections (2024-2028)
| Year | Market Size (EUR B) | YoY Growth | Cumulative Growth |
|------|---------------------|------------|-------------------|
| 2024 | X.XX | X.X% | Baseline |
| 2025 | X.XX | X.X% | X.X% |
| 2026 | X.XX | X.X% | X.X% |
| 2027 | X.XX | X.X% | X.X% |
| 2028 | X.XX | X.X% | X.X% |

**2024-2028 CAGR**: X.X%

### Regional Breakdown
| Region | 2024 Size (EUR B) | 2028 Projection (EUR B) | CAGR | Share of Global |
|--------|-------------------|-------------------------|------|-----------------|
| North America | X.XX | X.XX | X.X% | X% |
| Europe | X.XX | X.XX | X.X% | X% |
| APAC | X.XX | X.XX | X.X% | X% |
| Rest of World | X.XX | X.XX | X.X% | X% |
| **Global Total** | **X.XX** | **X.XX** | **X.X%** | **100%** |

---

## 3. Market Segmentation

### By Product/Service
| Segment | 2024 Size (EUR B) | Growth Rate | Key Characteristics |
|---------|-------------------|-------------|---------------------|
| Segment A | X.XX | X.X% | [Description] |
| Segment B | X.XX | X.X% | [Description] |
| Segment C | X.XX | X.X% | [Description] |
| **Total** | **X.XX** | **X.X%** | |

### By Customer Type
| Customer Segment | 2024 Size (EUR B) | Growth Rate | Buying Criteria |
|------------------|-------------------|-------------|-----------------|
| Enterprise (>1000 employees) | X.XX | X.X% | [Criteria] |
| Mid-Market (100-1000 employees) | X.XX | X.X% | [Criteria] |
| SMB (<100 employees) | X.XX | X.X% | [Criteria] |
| **Total** | **X.XX** | **X.X%** | |

### By Geography
[Already covered in Regional Breakdown above]

### By Technology
| Technology | 2024 Penetration | 2028 Projection | Adoption Drivers |
|------------|------------------|-----------------|------------------|
| Legacy Systems | X% | X% | [Drivers] |
| Cloud-native | X% | X% | [Drivers] |
| AI/ML Enabled | X% | X% | [Drivers] |
| Blockchain | X% | X% | [Drivers] |

---

## 4. Competitive Landscape

### Market Concentration
- **CR3 (Top 3 companies)**: X% of market
- **CR5 (Top 5 companies)**: X% of market
- **CR10 (Top 10 companies)**: X% of market
- **Herfindahl-Hirschman Index (HHI)**: XXXX (Interpretation: Highly concentrated/Moderate/Fragmented)

### Competitor Mapping
```
[2x2 matrix or positioning map]
Y-axis: Market Share/Growth
X-axis: Product Sophistication/Price
```

### Key Players Analysis

#### Market Leader: [Company A]
- **Market Share**: X%
- **Strengths**: [3-5 key strengths]
- **Weaknesses**: [3-5 key weaknesses]
- **Strategy**: [Current strategic focus]

#### Challenger: [Company B]
- **Market Share**: X%
- **Differentiation**: [How they compete]
- **Growth Rate**: X% (vs market X%)
- **Threat Level**: High/Medium/Low

#### Niche Players: [Companies C, D, E]
- **Collective Share**: X%
- **Specializations**: [Areas of focus]
- **Vulnerabilities**: [Risks they face]

### Competitive Dynamics
- **Pricing Pressure**: High/Medium/Low
- **Innovation Pace**: Fast/Moderate/Slow
- **Barriers to Entry**: High/Medium/Low
- **Switching Costs**: High/Medium/Low

---

## 5. Market Trends & Drivers

### Macro Trends (PESTEL Analysis)
**Political**: [Key political factors]
**Economic**: [Economic drivers and constraints]
**Social**: [Societal and demographic trends]
**Technological**: [Technology advancements]
**Environmental**: [Environmental factors]
**Legal**: [Legal and regulatory trends]

### Technology Trends
1. **Trend 1**: [Description, impact, timeline]
2. **Trend 2**: [Description, impact, timeline]
3. **Trend 3**: [Description, impact, timeline]

### Customer Trends
- **Changing Preferences**: [How customer needs are evolving]
- **Adoption Patterns**: [How customers are adopting solutions]
- **Value Drivers**: [What customers value most]

### Innovation Trends
- **R&D Investment**: Trends in research spending
- **Patent Activity**: Volume and focus areas
- **Startup Formation**: New company creation rate

---

## 6. Regulatory Environment

### Current Regulations
| Regulation | Jurisdiction | Impact | Compliance Cost |
|------------|--------------|--------|-----------------|
| Regulation A | EU/US/Global | High/Medium/Low | EUR X-XM |
| Regulation B | EU/US/Global | High/Medium/Low | EUR X-XM |

### Upcoming Changes
| Proposed Regulation | Expected Date | Potential Impact |
|---------------------|---------------|-----------------|
| Regulation C | 2025-Q3 | [Impact description] |
| Regulation D | 2026-Q1 | [Impact description] |

### Compliance Challenges
- **Key Challenges**: [3-5 main compliance issues]
- **Cost Implications**: Estimated compliance costs
- **Competitive Impact**: How regulations affect competition

---

## 7. Strategic Implications

### Investment Opportunities
1. **High-Growth Segments**: [Specific segments with >20% CAGR]
2. **Underserved Niches**: [Market gaps and opportunities]
3. **Technology Shifts**: [Areas being disrupted]
4. **Geographic Opportunities**: [Regions with high growth potential]

### Risks & Challenges
1. **Market Risks**: [Risks specific to this market]
2. **Competitive Risks**: [Threats from incumbents/new entrants]
3. **Regulatory Risks**: [Compliance and legal challenges]
4. **Technology Risks**: [Disruption risks]

### Market Entry Strategies
**For New Entrants**:
1. [Strategy 1: Niche focus]
2. [Strategy 2: Partnership approach]
3. [Strategy 3: Acquisition strategy]

**For Incumbents**:
1. [Strategy 1: Innovation defense]
2. [Strategy 2: Acquisition of disruptors]
3. [Strategy 3: Business model evolution]

### M&A Landscape
- **Recent Activity**: [Notable recent acquisitions]
- **Valuation Multiples**: [Current trading multiples]
- **Strategic Buyers**: [Companies likely to acquire]
- **Financial Buyers**: [PE firms active in space]

---

## SolStein Market Attractiveness Score

| Factor | Score (1-10) | Weight | Weighted Score |
|--------|--------------|--------|----------------|
| Market Size | | 20% | |
| Growth Rate | | 25% | |
| Profitability | | 15% | |
| Competitive Intensity | | 20% | |
| Regulatory Favorability | | 10% | |
| Technology Dynamics | | 10% | |
| **Total Score** | | **100%** | **X.X/10** |

**Interpretation**:
- 8.0-10.0: Highly attractive market
- 6.0-7.9: Moderately attractive market
- 4.0-5.9: Average attractiveness
- Below 4.0: Unattractive market

---

## Data Sources & Methodology

### Primary Data Sources
1. [Source 1: Type, coverage, reliability]
2. [Source 2: Type, coverage, reliability]
3. [Source 3: Type, coverage, reliability]

### Methodology
- **Market Sizing**: [Detailed methodology]
- **Growth Projections**: [Assumptions and models]
- **Segment Analysis**: [Data sources and calculations]
- **Competitive Analysis**: [Sources and analysis approach]

### Limitations
- [Key limitations of the analysis]
- [Data gaps and uncertainties]
- [Areas requiring further research]

---

## Recommendations

### For Venture Capital:
1. [Specific investment thesis]
2. [Target company profiles]
3. [Entry timing and sizing]

### For Private Equity:
1. [Platform investment opportunities]
2. [Add-on acquisition targets]
3. [Value creation levers]

### For Corporate Strategy:
1. [Market entry/expansion approaches]
2. [Competitive response strategies]
3. [Innovation investment priorities]

---

## Appendix

### Glossary of Terms
- **Term 1**: Definition
- **Term 2**: Definition
- **Term 3**: Definition

### Acronyms
- **TAM**: Total Addressable Market
- **SAM**: Serviceable Available Market
- **SOM**: Serviceable Obtainable Market
- **CAGR**: Compound Annual Growth Rate
- **HHI**: Herfindahl-Hirschman Index

### Detailed Data Tables
[Additional supporting data]
```

## Quality Checklist

Before delivering analysis, verify:
- [ ] All 7 sections covered comprehensively
- [ ] Market sizing includes methodology
- [ ] Growth projections are realistic and sourced
- [ ] Competitive analysis includes market share data
- [ ] Trends are evidence-based, not speculative
- [ ] Regulatory analysis is current and accurate
- [ ] Strategic implications are actionable
- [ ] All data properly sourced and attributed
- [ ] No market size inflation or unrealistic projections