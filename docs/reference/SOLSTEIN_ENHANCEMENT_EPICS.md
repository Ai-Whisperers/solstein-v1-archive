# Solstein Enhancement Epics
## Bridging Automated Scale with Deep Intelligence

**Date**: 2026-03-11  
**Author**: Claude (AI Whisperers)  
**Status**: Proposed for Implementation

---

## Executive Summary

The current Solstein pipeline successfully automates data collection at scale (210 companies) but lacks the "board-level intelligence" of the original manual Solstein methodology (33 companies with deep qualitative analysis). This document proposes **6 epics** to bridge the gap, transforming the automated pipeline into a system that delivers **both scale AND depth**.

### Current State Gap

| Dimension | Original Solstein (Manual) | Current Pipeline (Automated) |
|-----------|---------------------------|------------------------------|
| **Coverage** | 33 competitors (deep) | 210 companies (broad) |
| **Analysis Type** | Qualitative narrative | Structured data fields |
| **AI Assessment** | Evidence-based scoring (0-10) with cited sources | Keyword-based detection |
| **Capability Overlap** | Matrix comparing 8 capabilities per competitor | None |
| **Corporate Genealogy** | M&A history, parent companies tracked | None |
| **Protocol Mapping** | Country-by-country protocol expertise | None |
| **Strategic Synthesis** | Board-ready implications written | Score-based only |
| **Evidence** | Every claim cites sources | URLs stored, not synthesized |

### Target State

A hybrid system that delivers:
- **Automated Scale**: 200+ companies with 3-day turnaround
- **Deep Intelligence**: Rich narrative reports comparable to original Solstein
- **Evidence-Based**: Every claim traceable to source
- **Actionable**: Strategic implications, not just scores

---

## Epic 1: Deep Analysis Intelligence Module

### Goal
Transform structured company data into rich, narrative deep analysis reports comparable to the original Solstein markdown files.

### Current Gap
- Current reports template basic scores into prose
- Missing strategic synthesis (why this matters for Eneve)
- Missing "Why We Missed This" analysis (how competitors hide in search blindspots)
- Missing board-ready implications

### Reference: Original SOPTIM Analysis
The original manual analysis included:
- **Executive Summary**: Classification, tier, AI signal level
- **Product Offering**: Detailed capability breakdown (3-tier architecture)
- **Overlap Matrix**: 8 Eneve capabilities × overlap levels
- **AI Assessment**: Evidence-based signal level with rationale
- **Acceleration Signal**: Growth trajectory analysis
- **Why We Missed This**: Search blindspot analysis
- **Strategic Notes**: 10+ bullet points on implications

### Proposed Solution

#### 1.1 LLM-Powered Narrative Synthesis Pipeline
```python
# New module: src/solstein/intelligence/deep_analyzer.py

class DeepAnalysisGenerator:
    """Generate board-level deep analysis from structured data."""
    
    async def generate(
        self,
        company: Company,
        eneve_capabilities: List[Capability],
        context: MarketContext
    ) -> DeepAnalysisReport:
        """
        Returns structured report with:
        - executive_assessment: Narrative score interpretation
        - product_offering: LLM-synthesized from raw data
        - overlap_matrix: Capability comparison
        - ai_assessment: Evidence-based AI evaluation
        - strategic_implications: Why this matters for Eneve
        - blindspot_analysis: How competitor hides from search
        """
```

#### 1.2 Report Structure
```markdown
# Deep Analysis - {company.name}

## Executive Assessment
**Overall Rating**: {composite_score}/10 - {classification}
**Strategic Classification**: {tier}
**Threat Level**: {threat_level}

{narrative_assessment_paragraph}

## Product Offering
{llm_synthesized_product_description}

## Eneve Capability Overlap Matrix

| Eneve Capability | Overlap Level | Evidence |
|------------------|---------------|----------|
| Time Series Mgmt | {level} | {cited_evidence} |
| Balancing & Settlement | {level} | {cited_evidence} |
| ... | ... | ... |

## AI Adoption Assessment
**Signal Level**: {signal_level} (0-10: {score})
**Evidence**:
- {cited_claim_1}
- {cited_claim_2}

## Strategic Implications for Eneve
{llm_generated_strategic_analysis}

## Why This Competitor Is Hard to Find
{search_blindspot_analysis}

## Notes
{key_insights_bullets}
```

### Technical Implementation

**New Files**:
- `src/solstein/intelligence/deep_analyzer.py` - Core LLM pipeline
- `src/solstein/intelligence/prompts/deep_analysis.py` - Structured prompts
- `src/solstein/intelligence/overlap_matrix.py` - Capability comparison engine
- `src/solstein/exporters/markdown/deep_analysis_enhanced.py` - Enhanced report generator

**LLM Prompt Strategy**:
```python
DEEP_ANALYSIS_PROMPT = """
You are a competitive intelligence analyst writing for a board presentation.
Analyze the following company data and synthesize a strategic assessment.

Company Data: {structured_json}
Eneve Capabilities: {eneve_capability_list}
Market Context: {market_context}

Generate:
1. Executive Assessment (2-3 paragraphs)
2. Product Offering Summary (3-5 paragraphs)
3. AI Signal Assessment with evidence
4. Strategic Implications (why Eneve should care)
5. Search Blindspot Analysis (why hard to find)

Requirements:
- Every claim must cite specific evidence
- Use professional board-level language
- Highlight direct threats to Eneve
- Identify hidden opportunities
"""
```

### Acceptance Criteria
- [ ] Generated reports match original Solstein depth and quality
- [ ] Every claim cites specific evidence from source data
- [ ] Capability overlap matrix shows all 8 Eneve capabilities
- [ ] Reports include "Why We Missed This" section
- [ ] Strategic implications section explains Eneve relevance
- [ ] LLM pipeline completes in <30 seconds per company
- [ ] Reports exportable as markdown and PDF

### Effort Estimate
**2-3 sprints** (4-6 weeks)
- 1 week: Design LLM pipeline and prompts
- 2 weeks: Implement overlap matrix and narrative synthesis
- 1 week: Testing and prompt refinement

---

## Epic 2: Financial Growth Intelligence Module

### Goal
Enhance financial analysis with trajectory tracking, funding intelligence, and growth vector identification.

### Current Gap
- Current shows static financial metrics
- Missing funding history analysis
- Missing growth vector identification (AI, SaaS, geographic)
- Missing financial trajectory projection

### Reference: Original Financial Analysis
The original included:
- **Growth Trajectory**: Revenue growth, CAGR analysis
- **Funding History**: Round-by-round breakdown
- **Growth Vectors**: AI/ML, SaaS scaling, market expansion
- **Financial Health Narrative**: Written assessment

### Proposed Solution

#### 2.1 Enhanced Financial Model
```python
# Extend Company model with:

class FinancialIntelligence:
    """Rich financial analysis container."""
    
    # Growth Trajectory
    revenue_timeline: List[RevenuePoint]  # Year-by-year revenue
    growth_trajectory: str  # "accelerating", "steady", "decelerating"
    growth_consistency_score: float  # 0-10 volatility measure
    
    # Funding Intelligence
    funding_rounds_enhanced: List[FundingRound]  # Rich round data
    investor_quality_score: float  # 0-10 based on lead investors
    funding_velocity: str  # "rapid", "steady", "sparse"
    runway_estimate_months: int  # Calculated from burn rate
    
    # Growth Vectors
    primary_growth_vectors: List[GrowthVector]  # AI, SaaS, Geo, M&A
    growth_vector_confidence: Dict[str, float]
    
    # Trajectory Projection
    projected_revenue_12mo: float  # LLM-assisted projection
    projection_confidence: str  # "high", "medium", "low"
```

#### 2.2 Financial Report Generator
```python
class FinancialGrowthStrategy:
    """Generate enhanced financial growth report."""
    
    def generate(self, company: Company) -> str:
        return f"""
# Financial Growth Analysis - {company.name}

## Growth Trajectory
**Current Revenue**: €{revenue}M
**Growth Rate**: {growth_rate}% ({trajectory_assessment})
**3-Year CAGR**: {cagr_3yr}%
**Consistency Score**: {consistency}/10

{llm_synthesized_trajectory_narrative}

## Funding Intelligence
**Total Raised**: €{total_funding}M across {round_count} rounds
**Investor Quality**: {investor_quality}/10 ({lead_investors_list})
**Funding Velocity**: {velocity}
**Estimated Runway**: {runway_months} months

### Funding History
| Round | Amount | Date | Lead Investor | Valuation |
|-------|--------|------|---------------|-----------|
{rounds_table}

## Growth Vectors
{identified_vectors}

## Financial Health Assessment
{llm_synthesized_assessment}

## 12-Month Projection
{projection_with_confidence}
"""
```

### Technical Implementation

**New Files**:
- `src/solstein/intelligence/financial_analyzer.py`
- `src/solstein/intelligence/funding_intelligence.py`
- `src/solstein/intelligence/growth_vectors.py`

**Data Sources**:
- Crunchbase API (funding rounds)
- Companies House (financial filings)
- LinkedIn (employee growth proxy)
- GitHub (engineering velocity)

### Acceptance Criteria
- [ ] Year-by-year revenue timeline for all companies
- [ ] Funding round table with lead investors and valuations
- [ ] Growth vector identification (AI/SaaS/Geo/M&A)
- [ ] 12-month revenue projection with confidence level
- [ ] Financial trajectory narrative (accelerating/steady/decelerating)
- [ ] Investor quality scoring based on lead investor prestige

### Effort Estimate
**2 sprints** (4 weeks)
- 1 week: Enhance financial data collection
- 1 week: Build growth vector detection and projection

---

## Epic 3: Corporate Genealogy Tracker

### Goal
Track corporate relationships: parent companies, subsidiaries, acquisitions, and spin-offs.

### Current Gap
- No M&A history tracking
- No parent/subsidiary relationships
- Misses acquisitions that change competitive landscape

### Reference: Original Methodology
Tracked:
- **Parent Companies**: e.g., TMX Group owns Trayport
- **Acquisitions**: e.g., EG acquired Bright Energy (Dec 2025)
- **Spin-offs**: e.g., Kraken spun off from Octopus Energy
- **Corporate Evolution**: Timeline of structural changes

### Proposed Solution

#### 3.1 Corporate Genealogy Graph
```python
# New module: src/solstein/genealogy/

class CorporateEntity:
    """Node in corporate genealogy graph."""
    
    id: str
    name: str
    entity_type: str  # "company", "subsidiary", "parent", "acquired"
    relationships: List[CorporateRelationship]
    
class CorporateRelationship:
    """Edge in genealogy graph."""
    
    source_id: str
    target_id: str
    relationship_type: str  # "owns", "acquired", "spun_off", "merged"
    since_date: Optional[date]
    acquisition_value_eur: Optional[float]
    deal_rationale: Optional[str]
    
class GenealogyGraph:
    """Graph of corporate relationships."""
    
    def get_ultimate_parent(self, company_id: str) -> CorporateEntity:
        """Find top-level parent company."""
        
    def get_subsidiaries(self, company_id: str) -> List[CorporateEntity]:
        """Find all subsidiaries."""
        
    def get_acquisition_history(self, company_id: str) -> List[CorporateEvent]:
        """Get M&A timeline."""
        
    def find_related_competitors(self, company_id: str) -> List[Company]:
        """Find competitors through shared parent/acquirer."""
```

#### 3.2 Acquisition Intelligence
```python
class AcquisitionTracker:
    """Track and analyze M&A activity."""
    
    async def detect_new_acquisitions(
        self,
        timeframe: timedelta = timedelta(days=90)
    ) -> List[AcquisitionEvent]:
        """
        Detect acquisitions in competitive landscape.
        
        Returns acquisitions with:
        - acquirer and target
        - deal value (if disclosed)
        - strategic rationale
        - competitive impact assessment
        """
        
    def assess_competitive_impact(
        self,
        acquisition: AcquisitionEvent
    ) -> CompetitiveImpact:
        """
        Assess how acquisition changes competitive landscape.
        
        Returns:
        - threat_level_change: "increased", "decreased", "neutral"
        - new_capabilities_gained: List[Capability]
        - geographic_expansion: Optional[str]
        - ai_capability_boost: bool
        """
```

#### 3.3 Genealogy Report Section
```markdown
## Corporate Genealogy

**Ultimate Parent**: {parent_company} ({parent_country})
**Ownership Structure**: {structure_type}

### Acquisition History
| Date | Event | Value | Impact |
|------|-------|-------|--------|
| 2025-12 | Acquired Bright Energy | Undisclosed | +AI capabilities |
| 2024-06 | Spun off Kraken platform | N/A | New competitor created |

### Related Entities
- **Sister Companies**: {list}
- **Former Subsidiaries**: {list}
- **Acquired By**: {acquirer}

### Strategic Implications
{llm_analysis_of_corporate_evolution}
```

### Technical Implementation

**New Files**:
- `src/solstein/genealogy/models.py` - Graph data models
- `src/solstein/genealogy/graph.py` - Graph operations
- `src/solstein/genealogy/acquisition_tracker.py` - M&A detection
- `src/solstein/genealogy/data_sources/crunchbase.py`
- `src/solstein/genealogy/data_sources/pitchbook.py`

**Data Sources**:
- Crunchbase (acquisitions)
- PitchBook (deal data)
- News APIs (M&A announcements)
- Company press releases

### Acceptance Criteria
- [ ] Genealogy graph stores parent/subsidiary relationships
- [ ] Acquisition history tracked with dates and values
- [ ] New acquisitions automatically detected within 48 hours
- [ ] Competitive impact assessment for each acquisition
- [ ] "Related competitors" identification through shared parents
- [ ] Corporate evolution timeline generation

### Effort Estimate
**2-3 sprints** (4-6 weeks)
- 1 week: Design genealogy graph schema
- 2 weeks: Implement acquisition tracking
- 1 week: Build impact assessment and reporting

---

## Epic 4: Market Protocol Mapping

### Goal
Map energy market protocols by country and identify protocol implementers (competitor discovery method).

### Current Gap
- No protocol expertise tracking
- Misses competitors discovered through protocol research
- No country-by-country market structure analysis

### Reference: Original Methodology
The original Solstein had:
- **Protocol Directory**: EDSN (NL), MaBiS/MaKo (DE), BSC (UK), etc.
- **Company-Protocol Matrix**: Which companies support which protocols
- **Protocol-Based Discovery**: Finding competitors through protocol implementer lists
- **Country Market Maps**: Regulatory structure per country

### Proposed Solution

#### 4.1 Protocol Knowledge Base
```python
# New module: src/solstein/protocols/

class EnergyProtocol:
    """Energy market protocol definition."""
    
    code: str  # "EDSN", "MaBiS", "MaKo", "BSC"
    name: str
    country: str
    description: str
    mandate_level: str  # "required", "optional", "emerging"
    regulatory_authority: str
    
    # Technical details
    message_formats: List[str]  # "AS4", "EDIFACT", "XML"
    version_current: str
    version_effective_date: date
    
    # Implementers
    certified_implementers: List[str]  # Company IDs
    known_integrators: List[str]

class ProtocolRegistry:
    """Registry of all energy market protocols."""
    
    def get_protocols_by_country(self, country: str) -> List[EnergyProtocol]:
        """Get all protocols for a country."""
        
    def get_implementers(self, protocol_code: str) -> List[Company]:
        """Get all companies implementing a protocol."""
        
    def discover_competitors_via_protocols(
        self,
        known_competitor: Company
    ) -> List[ProtocolDiscoveredCompetitor]:
        """
        Find competitors by looking at protocol implementers.
        
        Logic: If Company X implements protocols A, B, C in Country Y,
        find other implementers of A, B, C in Country Y.
        """
```

#### 4.2 Protocol-Based Competitor Discovery
```python
class ProtocolDiscoveryEngine:
    """Discover competitors through protocol research."""
    
    async def discover_via_protocols(
        self,
        base_competitor: Company,
        protocols: List[EnergyProtocol]
    ) -> List[DiscoveredCompetitor]:
        """
        Discover competitors by protocol overlap.
        
        Strategy:
        1. Get protocols implemented by base_competitor
        2. Find other implementers of same protocols
        3. Score by protocol overlap count
        4. Research new candidates
        
        Returns discovered competitors with:
        - discovery_method: "protocol_overlap"
        - overlap_score: number of shared protocols
        - protocol_evidence: which protocols match
        """
        
    async def research_protocol_expertise(
        self,
        company: Company
    ) -> ProtocolExpertiseProfile:
        """
        Research which protocols a company supports.
        
        Sources:
        - Company website/protocol documentation
        - Regulatory authority certified implementer lists
        - News/press releases about protocol implementations
        - Job postings mentioning protocols
        """
```

#### 4.3 Protocol Map Report
```markdown
## Market Protocol Profile

### Supported Protocols
| Protocol | Country | Implementation Depth | Certification |
|----------|---------|---------------------|---------------|
| EDSN C-ARM | NL | Full | Certified |
| MaBiS | DE | Partial | In Progress |

### Protocol-Based Competitive Position
**Netherlands (EDSN)**:
- Market Position: Established
- Competitors via EDSN: {list}
- Regulatory Status: Certified implementer

**Germany (MaBiS/MaKo)**:
- Market Position: Expanding
- Competitors via MaBiS: {list}
- Gap Analysis: Missing {protocols} vs SOPTIM

### Country Market Entry Assessment
| Country | Protocols Required | Eneve Readiness | Key Competitors |
|---------|-------------------|-----------------|-----------------|
| Belgium | {protocols} | {readiness} | {competitors} |
| UK | {protocols} | {readiness} | {competitors} |
```

### Technical Implementation

**New Files**:
- `src/solstein/protocols/models.py` - Protocol data models
- `src/solstein/protocols/registry.py` - Protocol registry
- `src/solstein/protocols/discovery.py` - Protocol-based discovery
- `src/solstein/protocols/country_maps/` - Country-specific protocol maps
  - `netherlands.py`
  - `germany.py`
  - `uk.py`
  - etc.

**Data Sources**:
- Regulatory authority websites (EDSN, Bundesnetzagentur, etc.)
- Protocol documentation
- Company protocol certification lists
- Industry associations

### Acceptance Criteria
- [ ] Protocol registry covers 10+ European energy markets
- [ ] Each protocol has implementer list
- [ ] Protocol-based discovery finds 20%+ new competitors
- [ ] Company profiles show protocol expertise
- [ ] Country market entry assessment generated
- [ ] Gap analysis vs competitors by protocol coverage

### Effort Estimate
**3 sprints** (6 weeks)
- 2 weeks: Build protocol registry and data models
- 2 weeks: Implement protocol-based discovery
- 2 weeks: Country market maps and reporting

---

## Epic 5: Evidence & Provenance System

### Goal
Every claim in every report must be traceable to its source with confidence scoring.

### Current Gap
- URLs stored but not linked to specific claims
- No confidence scoring per claim
- No provenance tracking (where did this fact come from?)
- No contradiction detection between sources

### Reference: Original Methodology
- Every claim had `[source]` citation
- Evidence quality assessed (primary vs secondary)
- Contradictions flagged and resolved

### Proposed Solution

#### 5.1 Evidence Graph Model
```python
# New module: src/solstein/evidence/

class Claim:
    """A single claim/assertion about a company."""
    
    id: str
    claim_text: str
    claim_type: str  # "financial", "product", "strategic", "ai"
    
    # Provenance
    source: DataSource
    source_url: str
    source_quality: str  # "primary", "secondary", "tertiary"
    extraction_date: datetime
    
    # Confidence
    confidence_score: float  # 0-1
    confidence_factors: Dict[str, float]
    
    # Verification
    verified_by: List[Verification]
    contradictions: List[Contradiction]
    
class EvidenceGraph:
    """Graph of claims and their relationships."""
    
    claims: Dict[str, Claim]
    contradictions: List[Contradiction]
    
    def add_claim(self, claim: Claim) -> None:
        """Add claim, check for contradictions."""
        
    def find_contradictions(self, claim: Claim) -> List[Contradiction]:
        """Find existing claims that contradict this one."""
        
    def resolve_contradiction(
        self,
        contradiction: Contradiction
    ) -> Resolution:
        """Use source quality and confidence to resolve."""
```

#### 5.2 Cited Report Generation
```python
class CitedReportGenerator:
    """Generate reports with every claim cited."""
    
    def generate_with_citations(
        self,
        company: Company,
        sections: List[ReportSection]
    ) -> CitedReport:
        """
        Generate report where every claim has:
        - Claim text
        - Source URL
        - Confidence score
        - Evidence quality indicator
        
        Returns report with citation IDs that map to evidence graph.
        """
        
    def export_citations(
        self,
        report: CitedReport,
        format: str = "markdown"
    ) -> str:
        """
        Export report with citations.
        
        Markdown format:
        "Company raised €10M Series A[1][2]."
        
        [1]: Source URL, confidence 0.95
        [2]: Source URL, confidence 0.87
        """
```

#### 5.3 Contradiction Detection
```python
class ContradictionDetector:
    """Detect contradictions between sources."""
    
    async def detect_contradictions(
        self,
        company: Company
    ) -> List[Contradiction]:
        """
        Find contradictions in company data.
        
        Examples:
        - Source A says 100 employees, Source B says 500
        - Source A says founded 2010, Source B says 2012
        - Source A claims AI product, Source B says no AI
        
        Returns contradictions with:
        - claim_a and claim_b
        - contradiction_type: "numerical", "boolean", "temporal"
        - suggested_resolution: "prefer_primary", "average", "flag_for_review"
        """
```

#### 5.4 Report with Evidence
```markdown
## AI Adoption Assessment

**Signal Level**: STRONG (7/10)

**Evidence**:
1. "AI-powered demand forecasting" — Company blog, 2024-03-15 [1] (confidence: 0.95)
2. "Machine learning team of 20+" — LinkedIn, 2024-06 [2] (confidence: 0.87)
3. ⚠️ **Contradiction Detected**: Job posting mentions "exploring AI" [3] vs product page claims "AI-native" [4]

**Resolution**: Primary source (product page) preferred. Score: 7/10.

---

**Sources**:
- [1]: https://company.com/blog/ai-forecasting (Company Blog - Primary)
- [2]: https://linkedin.com/company/... (LinkedIn - Secondary)
- [3]: https://job-board.com/... (Job Posting - Primary)
- [4]: https://company.com/products (Product Page - Primary)
```

### Technical Implementation

**New Files**:
- `src/solstein/evidence/models.py` - Evidence data models
- `src/solstein/evidence/graph.py` - Evidence graph operations
- `src/solstein/evidence/contradiction.py` - Contradiction detection
- `src/solstein/evidence/citations.py` - Citation generation
- `src/solstein/evidence/confidence.py` - Confidence scoring

**Confidence Scoring Factors**:
- Source quality (primary: 1.0, secondary: 0.8, tertiary: 0.6)
- Source recency (within 6 months: 1.0, 1 year: 0.9, older: 0.7)
- Cross-validation (confirmed by 3+ sources: +0.2)
- Source authority (official company: 1.0, news: 0.8, social: 0.5)

### Acceptance Criteria
- [ ] Every claim in every report has source citation
- [ ] Confidence score (0-1) for every claim
- [ ] Contradiction detection across sources
- [ ] Automatic resolution using source quality hierarchy
- [ ] Evidence graph queryable by claim type, source, confidence
- [ ] Citation export in markdown, PDF, and JSON formats
- [ ] <5% of claims flagged for manual review

### Effort Estimate
**3 sprints** (6 weeks)
- 2 weeks: Build evidence graph and confidence scoring
- 2 weeks: Implement contradiction detection
- 2 weeks: Integration with report generation

---

## Epic 6: AI-Native Assessment Engine

### Goal
Replace keyword-based AI detection with LLM-powered capability assessment using evidence synthesis.

### Current Gap
- Current: Keyword matching ("AI", "machine learning" in description)
- Missing: Evidence-based assessment of AI maturity
- Missing: AI capability categorization
- Missing: Comparison to AI-native competitors

### Reference: Original Methodology
Original AI Assessment:
- **Signal Levels**: VERY STRONG, STRONG, MODERATE, LOW
- **Evidence-Based**: Each score backed by specific claims
- **Capability Breakdown**: ML forecasting, NLP, automation, etc.
- **Comparison**: Ranked list of all competitors by AI maturity

Example from original:
```
| Rank | Company | AI Signal | Key Evidence |
| 1 | Octopus/Kraken | VERY STRONG | 15B data points/day, ML forecasting, 
|   |              |             | Agent Assist, 700MW grid balancing |
```

### Proposed Solution

#### 6.1 AI Capability Taxonomy
```python
# New module: src/solstein/ai_assessment/

class AICapabilityTaxonomy:
    """Standardized AI capability categories."""
    
    CAPABILITIES = {
        "ml_forecasting": {
            "description": "Machine learning for demand/price forecasting",
            "keywords": ["forecasting", "prediction", "ML"],
            "weight": 1.0,
        },
        "nlp": {
            "description": "Natural language processing",
            "keywords": ["NLP", "language model", "chatbot"],
            "weight": 0.9,
        },
        "computer_vision": {
            "description": "Image/video analysis",
            "keywords": ["computer vision", "image recognition"],
            "weight": 0.7,
        },
        "automation": {
            "description": "AI-powered process automation",
            "keywords": ["automation", "RPA", "automated"],
            "weight": 0.9,
        },
        "optimization": {
            "description": "AI for operational optimization",
            "keywords": ["optimization", "reinforcement learning"],
            "weight": 0.9,
        },
        "generative_ai": {
            "description": "Generative AI / LLMs",
            "keywords": ["generative AI", "LLM", "GPT"],
            "weight": 1.0,
        },
    }
```

#### 6.2 LLM-Powered AI Assessment
```python
class AICapabilityAssessor:
    """Assess AI capabilities using LLM analysis."""
    
    async def assess(
        self,
        company: Company,
        source_materials: List[SourceMaterial]
    ) -> AIAssessment:
        """
        Comprehensive AI capability assessment.
        
        Process:
        1. Ingest all source materials (website, news, docs)
        2. LLM extracts AI-related claims
        3. Categorize claims by capability type
        4. Score each capability (0-10)
        5. Calculate overall AI maturity score
        6. Generate evidence-based narrative
        
        Returns:
        - overall_score: 0-10
        - signal_level: "very_strong", "strong", "moderate", "low"
        - capabilities: Dict[str, CapabilityScore]
        - evidence: List[ClaimWithSource]
        - narrative: str  # LLM-generated assessment
        """
        
    async def compare_to_baseline(
        self,
        company: Company,
        baseline_companies: List[Company]
    ) -> AIComparison:
        """
        Compare company's AI capabilities to baseline.
        
        Returns:
        - percentile_rank: Where company ranks vs baseline
        - gap_analysis: Capabilities where company lags
        - advantage_analysis: Capabilities where company leads
        - recommendations: Suggested AI investments
        """
```

#### 6.3 AI Assessment Report
```markdown
## AI Capability Assessment

### Overall Signal: {signal_level} ({score}/10)
{percentile_rank} percentile among energy software competitors

### Capability Breakdown

| Capability | Score | Evidence Count | Status |
|------------|-------|----------------|--------|
| ML Forecasting | 8/10 | 5 claims | ✅ Strong |
| NLP | 3/10 | 1 claim | ⚠️ Limited |
| Automation | 7/10 | 4 claims | ✅ Strong |
| Optimization | 6/10 | 3 claims | ⚠️ Moderate |
| Generative AI | 9/10 | 6 claims | ✅ Very Strong |

### Key Evidence

**ML Forecasting** (Score: 8/10):
1. "AI-powered demand forecasting reduces errors by 30%" — Product page, 2024 [1]
2. "Machine learning models trained on 5 years of data" — Blog, 2024 [2]
3. "Predictive analytics for grid balancing" — Press release, 2023 [3]

**Generative AI** (Score: 9/10):
1. "GPT-4 powered customer assistant" — Product launch, 2024 [4]
2. "LLM-based report generation" — Documentation [5]
...

### Gap Analysis vs {baseline_company}
| Capability | {company} | {baseline} | Gap |
|------------|-----------|------------|-----|
| ML Forecasting | 8 | 6 | +2 ✅ |
| NLP | 3 | 7 | -4 ⚠️ |

### AI Maturity Trajectory
{assessment_of_improving_or_stagnant}

### Strategic Implications
{llm_synthesized_implications}
```

#### 6.4 Industry-Wide AI Rankings
```python
class AIIndustryRankings:
    """Generate AI maturity rankings across all competitors."""
    
    async def generate_rankings(
        self,
        companies: List[Company]
    ) -> AIRankingsReport:
        """
        Generate industry-wide AI rankings.
        
        Similar to original Solstein table:
        | Rank | Company | AI Signal | Key Evidence |
        
        Includes:
        - Rank by overall AI score
        - Rank by specific capability
        - Trend analysis (improving/stable/declining)
        - "AI-native" classification (founded with AI)
        """
```

### Technical Implementation

**New Files**:
- `src/solstein/ai_assessment/capabilities.py` - Capability taxonomy
- `src/solstein/ai_assessment/assessor.py` - LLM assessment engine
- `src/solstein/ai_assessment/rankings.py` - Industry rankings
- `src/solstein/ai_assessment/evidence_extractor.py` - AI claim extraction

**LLM Prompt Strategy**:
```python
AI_ASSESSMENT_PROMPT = """
You are an AI capabilities analyst. Review the following source materials about {company}
and assess their AI capabilities.

Source Materials:
{source_texts}

Capability Taxonomy:
{capabilities}

For each capability:
1. Identify evidence in sources (specific claims)
2. Score 0-10 based on evidence strength
3. Note confidence level

Generate:
- Overall AI maturity score (0-10)
- Signal level (very_strong/strong/moderate/low)
- Narrative assessment (2-3 paragraphs)
- List of top 5 AI capabilities with evidence
"""
```

### Acceptance Criteria
- [ ] AI assessment uses LLM analysis, not just keywords
- [ ] Capability breakdown across 6+ AI categories
- [ ] Every score backed by specific evidence claims
- [ ] Industry-wide AI rankings generated
- [ ] Gap analysis vs baseline competitors
- [ ] "AI-native" classification (founded with AI vs retrofitted)
- [ ] Assessment completes in <60 seconds per company

### Effort Estimate
**2-3 sprints** (4-6 weeks)
- 1 week: Design capability taxonomy
- 2 weeks: Build LLM assessment pipeline
- 1-2 weeks: Rankings and gap analysis

---

## Implementation Roadmap

### Phase 1: Foundation (Epics 1, 5)
**Sprints 1-6** (12 weeks)
- Epic 1: Deep Analysis Intelligence Module
- Epic 5: Evidence & Provenance System

**Rationale**: These two epics form the foundation. Deep Analysis needs evidence system to cite claims properly. Evidence system needs deep analysis to generate claims worth citing.

### Phase 2: Intelligence Layer (Epics 2, 6)
**Sprints 7-12** (12 weeks)
- Epic 2: Financial Growth Intelligence Module
- Epic 6: AI-Native Assessment Engine

**Rationale**: Build on foundation to add financial and AI intelligence layers. These use the evidence system and feed into deep analysis.

### Phase 3: Discovery & Context (Epics 3, 4)
**Sprints 13-18** (12 weeks)
- Epic 3: Corporate Genealogy Tracker
- Epic 4: Market Protocol Mapping

**Rationale**: These add competitive discovery and market context. They build on the intelligence layer but can be developed in parallel once foundation is solid.

### Total Timeline: 18 sprints (36 weeks / 9 months)

---

## Success Metrics

### Quality Metrics
- **Report Depth Score**: Average report length/complexity matches original Solstein
- **Citation Coverage**: >95% of claims have source citations
- **Evidence Confidence**: Average confidence score >0.8
- **Contradiction Rate**: <5% of claims flagged for contradiction

### Scale Metrics
- **Coverage**: 200+ companies with deep analysis
- **Turnaround**: <3 days from data collection to final report
- **Cost**: <€500 per company (vs €15K+ for manual research)

### Business Value Metrics
- **Competitor Discovery**: 20%+ new competitors found via protocols/genealogy
- **Strategic Insights**: >10 actionable insights per market report
- **Board Readiness**: Reports usable for C-suite presentations without editing

---

## Open Questions

1. **LLM Cost Management**: How to balance deep LLM analysis with cost? (Consider: cheaper models for initial pass, expensive models only for key sections)

2. **Data Source Priorities**: Which new data sources to prioritize? (Crunchbase, PitchBook, proprietary research?)

3. **Eneve-Specific Customization**: How much should epics be generic vs Eneve-specific? (Recommend: build generic with Eneve config layer)

4. **Human-in-the-Loop**: Where should human reviewers be inserted? (Recommend: flag low-confidence claims for review, auto-approve high-confidence)

---

## Appendix A: Original vs Current Data Model Comparison

| Field Category | Original (Manual) | Current (Automated) | Gap |
|----------------|-------------------|---------------------|-----|
| **Identification** | Rich narrative | Basic fields | ❌ Missing narrative synthesis |
| **Overlap Matrix** | 8 capabilities × levels | None | ❌ Missing entirely |
| **AI Assessment** | 0-10 score with evidence | Keyword boolean | ❌ Missing depth |
| **Genealogy** | M&A timeline | None | ❌ Missing entirely |
| **Protocols** | Country-by-country map | None | ❌ Missing entirely |
| **Financials** | Growth trajectory narrative | Static metrics | ⚠️ Needs enhancement |
| **Evidence** | Every claim cited | URLs only | ⚠️ Needs provenance |

---

## Appendix B: Recommended Tech Stack Additions

| Component | Current | Recommended | Purpose |
|-----------|---------|-------------|---------|
| **Graph DB** | None | Neo4j or NetworkX | Genealogy, evidence graphs |
| **Vector DB** | Qdrant (partial) | Enhanced Qdrant | Semantic search, similarity |
| **LLM Cache** | None | LiteLLM Proxy | Cost management, caching |
| **Workflow** | Celery | Temporal.io | Complex multi-step pipelines |
| **Knowledge Base** | None | Custom protocol registry | Protocol mappings |

---

*End of Epic Proposal*
