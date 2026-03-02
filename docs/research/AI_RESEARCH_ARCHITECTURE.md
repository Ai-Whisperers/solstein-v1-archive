# AI-Powered Autonomous Research Architecture
## Deep Research System with Ollama + Multi-Agent Orchestration

---

## Executive Summary

This architecture replaces synthetic data generation with **autonomous AI agents** that perform deep web research, extracting real company data from multiple sources with full provenance tracking.

### Key Innovation
Instead of relying on expensive APIs (Crunchbase, LinkedIn), we use **local LLMs (Ollama) + web search + intelligent scraping** to autonomously research companies and extract structured data.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        AI RESEARCH ORCHESTRATOR                              │
│                     (LangGraph State Machine)                                │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
┌───────────────┐      ┌──────────────────┐      ┌──────────────────┐
│ 1. PLANNER    │      │ 2. SEARCHER      │      │ 3. EXTRACTOR     │
│    AGENT      │──────▶│    AGENT         │──────▶│    AGENT         │
│               │      │                  │      │                  │
│ • Strategy    │      │ • Web search     │      │ • Scrape sites   │
│ • Query gen   │      │ • Find sources   │      │ • LLM extraction │
│ • Priority    │      │ • Rank results   │      │ • Structure data │
└───────────────┘      └──────────────────┘      └──────────────────┘
                                                           │
        ┌──────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│ 4. VALIDATOR     │──────▶│ 5. CROSS-REF     │──────▶│ 6. SYNTHESIZER   │
│    AGENT         │      │    AGENT         │      │    AGENT         │
│                  │      │                  │      │                  │
│ • Validate data  │      │ • Multi-source   │      │ • Merge findings │
│ • Check ranges   │      │ • Confidence     │      │ • Final output   │
│ • Flag anomalies │      │ • Resolve conflicts│     │ • Source links   │
└──────────────────┘      └──────────────────┘      └──────────────────┘
                                                           │
                                                           ▼
                                              ┌──────────────────────┐
                                              │ STRUCTURED OUTPUT    │
                                              │ • Company profile    │
                                              │ • Financial data     │
                                              │ • Funding history    │
                                              │ • Source URLs        │
                                              │ • Confidence scores  │
                                              └──────────────────────┘
```

---

## Agent Specifications

### 1. Research Planner Agent

**Purpose**: Strategize the research approach for each company

**Input**: Company name, industry (optional)
**Output**: Research plan with prioritized queries

**Process**:
```python
class ResearchPlanner:
    """Plans multi-step research strategy."""

    async def create_plan(self, company_name: str) -> ResearchPlan:
        # Use Ollama to generate search strategy
        prompt = f"""
        Create a research plan for company: {company_name}

        Generate 5-7 specific search queries to find:
        1. Official website and basic info
        2. Funding and valuation data
        3. Revenue and financial information
        4. Employee count and growth
        5. Recent news and announcements
        6. LinkedIn and social presence
        7. Industry classification

        Format as JSON with priority scores.
        """

        response = await self.llm.generate(prompt)
        return self.parse_research_plan(response)
```

**Example Output**:
```json
{
  "queries": [
    {"query": "Octopus Energy official website", "priority": 1, "intent": "website"},
    {"query": "Octopus Energy funding valuation Series", "priority": 1, "intent": "funding"},
    {"query": "Octopus Energy revenue 2024 2025", "priority": 2, "intent": "financials"},
    {"query": "Octopus Energy employees headcount", "priority": 2, "intent": "employees"},
    {"query": "Octopus Energy LinkedIn", "priority": 3, "intent": "social"}
  ]
}
```

---

### 2. Web Search Agent

**Purpose**: Execute searches and rank results by relevance

**Tools**:
- DuckDuckGo (free, no API key)
- Exa.ai (if API key available)
- Google Search (fallback)

**Process**:
```python
class WebSearchAgent(BaseDataGatheringAgent):
    """Performs intelligent web searches."""

    async def search(self, query: str, intent: str) -> List[SearchResult]:
        # Try multiple search backends
        results = []

        # 1. Try DuckDuckGo
        try:
            ddgs_results = await self._search_duckduckgo(query)
            results.extend(ddgs_results)
        except Exception as e:
            logger.warning(f"DuckDuckGo failed: {e}")

        # 2. Try Exa if available
        if self.exa_api_key:
            try:
                exa_results = await self._search_exa(query)
                results.extend(exa_results)
            except Exception as e:
                logger.warning(f"Exa failed: {e}")

        # 3. Use LLM to rank results by relevance to intent
        ranked = await self._rank_results_with_llm(results, intent)
        return ranked[:10]  # Top 10 most relevant
```

---

### 3. Content Extractor Agent

**Purpose**: Scrape websites and extract structured data using LLM

**Key Innovation**: Uses Ollama to parse unstructured HTML into structured JSON

**Process**:
```python
class ContentExtractorAgent(BaseDataGatheringAgent):
    """Extracts structured data from web content."""

    async def extract(self, url: str, extraction_type: str) -> ExtractedData:
        # 1. Fetch page content
        html = await self._fetch_page(url)
        text = self._clean_html(html)

        # 2. Use LLM to extract structured data
        prompt = f"""
        Extract structured company data from this web content.

        Content: {text[:8000]}  # First 8k chars

        Extract the following fields (use null if not found):
        {{
          "company_name": "official company name",
          "website": "company website URL",
          "description": "brief company description (1-2 sentences)",
          "industry": "industry/sector",
          "headquarters": "city, country",
          "founded_year": "year founded (number)",
          "employees": "employee count (number)",
          "revenue": "annual revenue in millions (number)",
          "funding_raised": "total funding in millions (number)",
          "valuation": "valuation in millions (number)",
          "funding_rounds": [
            {"round": "Series A", "amount": "in millions", "date": "YYYY-MM", "lead_investor": "name"}
          ],
          "key_executives": ["CEO Name", "CTO Name"],
          "products": ["product 1", "product 2"],
          "confidence": "high/medium/low based on clarity of data"
        }}

        Return ONLY valid JSON. No markdown, no explanation.
        """

        response = await self.llm.generate(prompt)
        data = json.loads(response)

        # Add source tracking
        data['data_source'] = url
        data['extraction_timestamp'] = datetime.now().isoformat()

        return ExtractedData(**data)
```

---

### 4. Data Validator Agent

**Purpose**: Validate extracted data for sanity and consistency

**Checks**:
- Revenue > 0 and < €1T (reasonable range)
- Employee count > 0 and < 1M
- Founded year > 1800 and < current year
- Funding rounds are chronological
- No negative values

**Process**:
```python
class DataValidatorAgent:
    """Validates extracted data for consistency."""

    VALIDATION_RULES = {
        "revenue": {"min": 0, "max": 1_000_000, "unit": "millions EUR"},
        "employees": {"min": 1, "max": 1_000_000, "unit": "count"},
        "founded_year": {"min": 1800, "max": 2026, "unit": "year"},
        "funding_raised": {"min": 0, "max": 100_000, "unit": "millions"},
        "valuation": {"min": 0, "max": 1_000_000, "unit": "millions"},
    }

    async def validate(self, data: CompanyData) -> ValidationResult:
        issues = []
        confidence_adjustments = 0.0

        # Rule-based validation
        for field, rules in self.VALIDATION_RULES.items():
            value = getattr(data, field)
            if value is None:
                continue

            if value < rules["min"] or value > rules["max"]:
                issues.append(f"{field}={value} outside valid range [{rules['min']}, {rules['max']}] {rules['unit']}")
                confidence_adjustments -= 0.1

        # LLM-based cross-field validation
        llm_validation = await self._llm_validate(data)
        issues.extend(llm_validation.issues)

        return ValidationResult(
            is_valid=len(issues) == 0,
            issues=issues,
            confidence_adjustment=confidence_adjustments,
            recommendations=llm_validation.recommendations
        )
```

---

### 5. Cross-Reference Agent

**Purpose**: Compare data from multiple sources and resolve conflicts

**Process**:
```python
class CrossReferenceAgent:
    """Cross-references data from multiple sources."""

    async def cross_reference(
        self,
        findings: List[SourceFinding]
    ) -> ConsolidatedData:

        # Group findings by field
        field_sources = defaultdict(list)
        for finding in findings:
            for field, value in finding.data.items():
                field_sources[field].append({
                    "value": value,
                    "source": finding.source_url,
                    "confidence": finding.confidence
                })

        # Resolve conflicts using LLM
        consolidated = {}
        for field, sources in field_sources.items():
            if len(sources) == 1:
                consolidated[field] = sources[0]["value"]
            else:
                # Multiple sources - use LLM to reconcile
                consolidated[field] = await self._reconcile_field(field, sources)

        return ConsolidatedData(
            data=consolidated,
            sources=[f.source_url for f in findings],
            confidence=self._calculate_overall_confidence(findings)
        )

    async def _reconcile_field(self, field: str, sources: List[dict]):
        """Use LLM to decide which source is most reliable."""
        prompt = f"""
        Reconcile conflicting values for field: {field}

        Sources:
        {json.dumps(sources, indent=2)}

        Consider:
        1. Source authority (official website > news > blog)
        2. Recency (newer > older)
        3. Consistency across sources
        4. Data specificity (exact number > estimated)

        Return the most reliable value and explain why.
        """

        response = await self.llm.generate(prompt)
        return self.parse_reconciliation(response)
```

---

### 6. Synthesis Agent

**Purpose**: Merge all validated data into final structured output

**Output Format**:
```json
{
  "company_name": "Octopus Energy",
  "is_synthetic": false,
  "data_source_type": "web_research",
  "confidence_score": 0.85,

  "basic_info": {
    "website": "https://octopus.energy",
    "description": "Technology-driven renewable energy supplier",
    "industry": "Energy Software",
    "headquarters": "London, UK",
    "founded_year": 2015,
    "employees": 2500
  },

  "financials": {
    "revenue": 4500,
    "revenue_currency": "GBP",
    "revenue_year": 2024,
    "valuation": 6000,
    "valuation_currency": "USD",
    "valuation_date": "2024-12"
  },

  "funding": {
    "total_raised": 2100,
    "currency": "USD",
    "rounds": [
      {
        "round": "Series D",
        "amount": 800,
        "date": "2021-12",
        "lead_investor": "Generation Investment Management",
        "sources": ["https://techcrunch.com/...", "https://crunchbase.com/..."]
      }
    ]
  },

  "data_sources": [
    {
      "url": "https://octopus.energy/about",
      "type": "company_website",
      "confidence": 0.95,
      "fields_covered": ["website", "description", "founded_year"]
    },
    {
      "url": "https://techcrunch.com/2021/12/...",
      "type": "news",
      "confidence": 0.85,
      "fields_covered": ["funding", "valuation"]
    }
  ],

  "research_metadata": {
    "research_date": "2026-03-02T10:30:00Z",
    "queries_executed": 7,
    "sources_found": 12,
    "sources_used": 5,
    "llm_calls": 23,
    "total_time_seconds": 45.2
  }
}
```

---

## LangGraph State Machine

```python
from langgraph.graph import StateGraph, END

class ResearchState(TypedDict):
    company_name: str
    plan: ResearchPlan
    search_results: List[SearchResult]
    extracted_data: List[ExtractedData]
    validated_data: List[ValidatedData]
    consolidated: ConsolidatedData
    errors: List[str]
    current_step: str

# Define the graph
workflow = StateGraph(ResearchState)

# Add nodes
workflow.add_node("planner", planner_agent)
workflow.add_node("searcher", search_agent)
workflow.add_node("extractor", extract_agent)
workflow.add_node("validator", validate_agent)
workflow.add_node("cross_ref", cross_reference_agent)
workflow.add_node("synthesizer", synthesize_agent)

# Define edges
workflow.set_entry_point("planner")
workflow.add_edge("planner", "searcher")
workflow.add_edge("searcher", "extractor")
workflow.add_edge("extractor", "validator")
workflow.add_edge("validator", "cross_ref")
workflow.add_edge("cross_ref", "synthesizer")
workflow.add_edge("synthesizer", END)

# Add conditional edges for error handling
workflow.add_conditional_edges(
    "searcher",
    should_retry_search,
    {True: "searcher", False: "extractor"}
)

# Compile
research_graph = workflow.compile()

# Execute
result = await research_graph.ainvoke({
    "company_name": "Octopus Energy"
})
```

---

## Implementation Strategy

### Phase 1: Core Infrastructure (1-2 days)
1. Create `AIResearchOrchestrator` class
2. Implement base agent classes with Ollama integration
3. Set up LangGraph state machine

### Phase 2: Search & Extract (2-3 days)
1. Implement WebSearchAgent with DuckDuckGo
2. Implement ContentExtractorAgent with LLM parsing
3. Add caching layer for results

### Phase 3: Validation & Cross-Reference (2-3 days)
1. Implement DataValidatorAgent
2. Implement CrossReferenceAgent
3. Add confidence scoring

### Phase 4: Integration (1-2 days)
1. Wire into existing data pipeline
2. Replace synthetic data loader
3. Add CLI commands

### Phase 5: Testing & Optimization (2-3 days)
1. Test with 20-30 real companies
2. Tune prompts for accuracy
3. Optimize parallel execution

---

## Cost Analysis

### vs. Crunchbase API
| Approach | Cost per 1000 companies | Data Quality |
|----------|------------------------|--------------|
| Crunchbase Pro API | $2,990/month | High |
| **Ollama + Web Search** | **$0** (local LLM) | **Medium-High** |
| Hybrid (Ollama + Exa) | ~$50/month | High |

### Resource Requirements
- **CPU**: 4-8 cores for Ollama (llama3.2:3b or similar)
- **RAM**: 16GB minimum, 32GB recommended
- **Storage**: 10GB for models, 1GB for cache
- **Network**: Standard internet (web search)

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Research Success Rate | >80% | Companies with complete data |
| Revenue Accuracy | ±30% | vs. known public data |
| Employee Count Accuracy | ±25% | vs. LinkedIn |
| Funding Data Accuracy | ±20% | vs. Crunchbase |
| False Positive Rate | <5% | Incorrect data flagged |
| Research Time | <60s | Per company |
| Source Coverage | 3+ sources | Per company |

---

## Example Research Output

```json
{
  "company_name": "Octopus Energy",
  "confidence_score": 0.87,
  "is_synthetic": false,
  "data_sources": [
    {
      "url": "https://octopus.energy/about",
      "type": "company_website",
      "confidence": 0.95
    },
    {
      "url": "https://www.linkedin.com/company/octopus-energy",
      "type": "linkedin",
      "confidence": 0.80
    },
    {
      "url": "https://techcrunch.com/2021/12/14/octopus-energy-raises-800m",
      "type": "news",
      "confidence": 0.90
    }
  ],
  "extracted_data": {
    "revenue": 4500,
    "employees": 2500,
    "funding_raised": 2100,
    "valuation": 6000,
    "founded_year": 2015
  },
  "validation_status": "PASSED",
  "research_time_seconds": 42.3
}
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| LLM hallucination | Multi-source validation + confidence scoring |
| Web scraping failures | Multiple backends + graceful degradation |
| Rate limiting | Exponential backoff + caching |
| Data staleness | Timestamp tracking + refresh scheduling |
| Source reliability | Authority scoring + cross-referencing |

---

## Next Steps

1. **Immediate**: Implement core orchestrator + planner agent
2. **Day 2-3**: Add search + extraction agents
3. **Day 4-5**: Add validation + cross-reference
4. **Day 6-7**: Integration testing with 30 companies
5. **Week 2**: Production deployment + monitoring

---

*This architecture enables fully autonomous, AI-powered company research using only local LLMs and free web search, eliminating the need for expensive data APIs while maintaining data quality through multi-agent validation.*
