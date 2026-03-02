"""
AI-Powered Autonomous Research System
======================================

Multi-agent research orchestration using Ollama LLMs and web search.
Replaces synthetic data with real web-researched company data.

Architecture:
1. Planner Agent - Creates research strategy
2. Search Agent - Finds relevant sources
3. Extractor Agent - Parses content with LLM
4. Validator Agent - Checks data sanity
5. CrossRef Agent - Multi-source reconciliation
6. Synthesizer Agent - Final structured output
"""

import asyncio
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from loguru import logger

# Optional: DuckDuckGo search
try:
    from duckduckgo_search import DDGS
    DUCKDUCKGO_AVAILABLE = True
except ImportError:
    DUCKDUCKGO_AVAILABLE = False
    logger.warning("duckduckgo_search not installed. Web search will use fallback method.")

from ..llm.enhanced_client import EnhancedLLMClient
from ..domain.models import Company, DataSourceType
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from loguru import logger

from ..llm.enhanced_client import EnhancedLLMClient
from ..domain.models import Company, DataSourceType


# ============================================================================
# DATA MODELS
# ============================================================================


@dataclass
class ResearchPlan:
    """Research strategy for a company."""

    company_name: str
    queries: List[Dict[str, Any]]  # [{"query": str, "priority": int, "intent": str}]
    estimated_sources: int
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SearchResult:
    """Web search result."""

    title: str
    url: str
    snippet: str
    source: str
    relevance_score: float = 0.0
    intent_match: str = ""


@dataclass
class ExtractedData:
    """Structured data extracted from a source."""

    source_url: str
    source_type: str
    data: Dict[str, Any]
    confidence: float
    extraction_method: str
    extracted_at: datetime = field(default_factory=datetime.now)
    raw_content: str = ""


@dataclass
class ValidationResult:
    """Data validation outcome."""

    is_valid: bool
    issues: List[str]
    confidence_adjustment: float
    recommendations: List[str]


@dataclass
class ResearchReport:
    """Final research report for a company."""

    company_name: str
    is_synthetic: bool = False
    confidence_score: float = 0.0
    basic_info: Dict[str, Any] = field(default_factory=dict)
    financials: Dict[str, Any] = field(default_factory=dict)
    funding: Dict[str, Any] = field(default_factory=dict)
    data_sources: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


# ============================================================================
# AGENT 1: RESEARCH PLANNER
# ============================================================================


class ResearchPlannerAgent:
    """Creates intelligent research strategies using LLM."""

    def __init__(self, llm_client: Optional[EnhancedLLMClient] = None):
        self.llm = llm_client or EnhancedLLMClient()

    async def create_plan(self, company_name: str, industry: Optional[str] = None) -> ResearchPlan:
        """Generate research plan with prioritized search queries."""

        industry_context = f"in the {industry} industry" if industry else ""

        prompt = f"""Create a detailed web research plan for: {company_name} {industry_context}

Your goal is to find real, factual information about this company from web sources.

Generate 6-8 specific search queries to find:
1. Official website and about page
2. Funding rounds and investors
3. Revenue and financial performance  
4. Employee count and headcount growth
5. Recent news and press releases
6. LinkedIn/social media presence
7. Industry classification and competitors

For each query, assign:
- priority: 1 (critical), 2 (important), or 3 (nice-to-have)
- intent: what type of data we expect to find

Return ONLY valid JSON in this exact format:
{{
  "queries": [
    {{"query": "...", "priority": 1, "intent": "website"}},
    {{"query": "...", "priority": 1, "intent": "funding"}},
    {{"query": "...", "priority": 2, "intent": "financials"}},
    {{"query": "...", "priority": 2, "intent": "employees"}},
    {{"query": "...", "priority": 2, "intent": "news"}},
    {{"query": "...", "priority": 3, "intent": "social"}},
    {{"query": "...", "priority": 3, "intent": "industry"}}
  ],
  "estimated_sources": 5
}}

Be specific in queries - include years, funding round types, and company-specific terms."""

        try:
            response = await self.llm.generate(prompt)
            plan_data = json.loads(self._extract_json(response))

            queries = sorted(plan_data.get("queries", []), key=lambda x: x.get("priority", 3))

            logger.info(f"📋 Created research plan for {company_name} with {len(queries)} queries")

            return ResearchPlan(
                company_name=company_name, queries=queries, estimated_sources=plan_data.get("estimated_sources", 5)
            )

        except Exception as e:
            logger.error(f"Failed to create research plan: {e}")
            # Fallback to basic plan
            return ResearchPlan(
                company_name=company_name,
                queries=[
                    {"query": f"{company_name} official website", "priority": 1, "intent": "website"},
                    {"query": f"{company_name} funding valuation", "priority": 1, "intent": "funding"},
                    {"query": f"{company_name} revenue 2024", "priority": 2, "intent": "financials"},
                    {"query": f"{company_name} employees headcount", "priority": 2, "intent": "employees"},
                ],
                estimated_sources=4,
            )

    def _extract_json(self, text: str) -> str:
        """Extract JSON from LLM response."""
        # Try to find JSON block
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            return text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            return text[start:end].strip()
        else:
            # Find first { and last }
            start = text.find("{")
            end = text.rfind("}")
            if start >= 0 and end > start:
                return text[start : end + 1]
        return text


# ============================================================================
# AGENT 2: WEB SEARCH
# ============================================================================


class WebSearchAgent:
    """Performs intelligent web searches across multiple backends."""

    def __init__(self):
        self.ddgs = DDGS() if DUCKDUCKGO_AVAILABLE else None
        self.cache: Dict[str, List[SearchResult]] = {}

    async def search(self, query: str, intent: str, max_results: int = 10) -> List[SearchResult]:
        """Execute search and return ranked results."""

        cache_key = f"{query}_{intent}"
        if cache_key in self.cache:
            logger.debug(f"Cache hit for: {query}")
            return self.cache[cache_key]

        results = []

        # Try DuckDuckGo if available
        if DUCKDUCKGO_AVAILABLE and self.ddgs:
            try:
                ddgs_results = await asyncio.to_thread(self._search_duckduckgo, query, max_results)
                results.extend(ddgs_results)
                logger.debug(f"DuckDuckGo found {len(ddgs_results)} results for: {query}")
            except Exception as e:
                logger.warning(f"DuckDuckGo search failed: {e}")
        else:
            logger.warning("DuckDuckGo not available. Install with: pip install duckduckgo-search")

        # Rank results by relevance to intent
        ranked = await self._rank_by_relevance(results, intent)

        self.cache[cache_key] = ranked
        return ranked

    def _search_duckduckgo(self, query: str, max_results: int) -> List[SearchResult]:
        """Search using DuckDuckGo."""
        results = []

        if not DUCKDUCKGO_AVAILABLE or not self.ddgs:
            return results

        for r in self.ddgs.text(query, max_results=max_results):
            results.append(
                SearchResult(
                    title=r.get("title", ""),
                    url=r.get("href", ""),
                    snippet=r.get("body", ""),
                    source=urlparse(r.get("href", "")).netloc,
    """Performs intelligent web searches across multiple backends."""

    def __init__(self):
        self.ddgs = DDGS()
        self.cache: Dict[str, List[SearchResult]] = {}

    async def search(self, query: str, intent: str, max_results: int = 10) -> List[SearchResult]:
        """Execute search and return ranked results."""

        cache_key = f"{query}_{intent}"
        if cache_key in self.cache:
            logger.debug(f"Cache hit for: {query}")
            return self.cache[cache_key]

        results = []

        # Try DuckDuckGo
        try:
            ddgs_results = await asyncio.to_thread(self._search_duckduckgo, query, max_results)
            results.extend(ddgs_results)
            logger.debug(f"DuckDuckGo found {len(ddgs_results)} results for: {query}")
        except Exception as e:
            logger.warning(f"DuckDuckGo search failed: {e}")

        # Rank results by relevance to intent
        ranked = await self._rank_by_relevance(results, intent)

        self.cache[cache_key] = ranked
        return ranked

    def _search_duckduckgo(self, query: str, max_results: int) -> List[SearchResult]:
        """Search using DuckDuckGo."""
        results = []

        for r in self.ddgs.text(query, max_results=max_results):
            results.append(
                SearchResult(
                    title=r.get("title", ""),
                    url=r.get("href", ""),
                    snippet=r.get("body", ""),
                    source=urlparse(r.get("href", "")).netloc,
                    intent_match="",
                )
            )

        return results

    async def _rank_by_relevance(self, results: List[SearchResult], intent: str) -> List[SearchResult]:
        """Rank search results by relevance to intent."""
        # Simple keyword-based scoring
        intent_keywords = {
            "website": ["official", "about", "company", "home"],
            "funding": ["funding", "investment", "raised", "series", "valuation"],
            "financials": ["revenue", "financial", "sales", "growth", "profit"],
            "employees": ["employees", "headcount", "team", "hiring", "jobs"],
            "news": ["news", "press", "announces", "launches"],
            "social": ["linkedin", "twitter", "social", "media"],
        }

        keywords = intent_keywords.get(intent, [])

        for result in results:
            text = f"{result.title} {result.snippet}".lower()
            score = 0.0

            # Keyword matching
            for kw in keywords:
                if kw in text:
                    score += 0.2

            # Domain authority
            if any(x in result.source for x in ["crunchbase.com", "linkedin.com", "bloomberg.com"]):
                score += 0.3
            elif any(x in result.source for x in ["techcrunch.com", "forbes.com", "reuters.com"]):
                score += 0.25
            elif ".gov" in result.source:
                score += 0.2

            # Recent content bonus
            if any(year in text for year in ["2024", "2025", "2026"]):
                score += 0.1

            result.relevance_score = min(score, 1.0)
            result.intent_match = intent

        # Sort by relevance
        return sorted(results, key=lambda x: x.relevance_score, reverse=True)


# ============================================================================
# AGENT 3: CONTENT EXTRACTOR
# ============================================================================


class ContentExtractorAgent:
    """Extracts structured data from web pages using LLM."""

    def __init__(self, llm_client: Optional[EnhancedLLMClient] = None):
        self.llm = llm_client or EnhancedLLMClient()
        self.http = httpx.AsyncClient(timeout=30.0, follow_redirects=True)

    async def extract(self, url: str, company_name: str) -> ExtractedData:
        """Extract structured data from a URL."""

        logger.info(f"🔍 Extracting data from: {url}")

        try:
            # Fetch page
            html = await self._fetch_page(url)
            text = self._clean_html(html)

            if len(text) < 100:
                return ExtractedData(
                    source_url=url,
                    source_type="error",
                    data={},
                    confidence=0.0,
                    extraction_method="fetch_failed",
                    raw_content="",
                )

            # Use LLM to extract structured data
            data = await self._llm_extract(text[:8000], company_name, url)

            # Determine source type
            source_type = self._classify_source(url)

            # Calculate confidence based on data completeness
            confidence = self._calculate_confidence(data)

            return ExtractedData(
                source_url=url,
                source_type=source_type,
                data=data,
                confidence=confidence,
                extraction_method="llm_parsing",
                raw_content=text[:2000],  # Store preview
            )

        except Exception as e:
            logger.error(f"Extraction failed for {url}: {e}")
            return ExtractedData(
                source_url=url,
                source_type="error",
                data={},
                confidence=0.0,
                extraction_method=f"error: {str(e)}",
                raw_content="",
            )

    async def _fetch_page(self, url: str) -> str:
        """Fetch page HTML."""
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = await self.http.get(url, headers=headers)
        response.raise_for_status()
        return response.text

    def _clean_html(self, html: str) -> str:
        """Extract clean text from HTML."""
        soup = BeautifulSoup(html, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()

        # Get text
        text = soup.get_text(separator="\n")

        # Clean up
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = "\n".join(chunk for chunk in chunks if chunk)

        return text

    async def _llm_extract(self, text: str, company_name: str, url: str) -> Dict[str, Any]:
        """Use LLM to extract structured data."""

        prompt = f"""Extract structured company information from this web content.

Company: {company_name}
Source: {url}

Content:
{text[:6000]}

Extract these fields (use null if not found):
{{
  "company_name": "official company name",
  "website": "company website URL",
  "description": "brief description (1-2 sentences)",
  "industry": "industry/sector",
  "headquarters": "city, country",
  "founded_year": number or null,
  "employees": number or null,
  "revenue": number (in millions) or null,
  "revenue_currency": "EUR|USD|GBP",
  "funding_raised": number (in millions) or null,
  "valuation": number (in millions) or null,
  "funding_rounds": [
    {{"round": "Series A", "amount": number, "date": "YYYY-MM", "lead_investor": "name"}}
  ],
  "key_executives": ["CEO Name", "CTO Name"],
  "products": ["product 1", "product 2"],
  "is_public": true/false
}}

Return ONLY valid JSON. No markdown, no explanation. Use null for unknown values."""

        try:
            response = await self.llm.generate(prompt)
            return json.loads(response)
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            return {}

    def _classify_source(self, url: str) -> str:
        """Classify the type of source."""
        domain = urlparse(url).netloc.lower()

        if any(x in domain for x in ["crunchbase.com"]):
            return "crunchbase"
        elif any(x in domain for x in ["linkedin.com"]):
            return "linkedin"
        elif any(x in domain for x in ["bloomberg.com", "reuters.com", "forbes.com", "techcrunch.com"]):
            return "news"
        elif any(x in domain for x in ["wikipedia.org"]):
            return "wikipedia"
        else:
            return "company_website"

    def _calculate_confidence(self, data: Dict[str, Any]) -> float:
        """Calculate confidence based on data completeness."""
        critical_fields = ["company_name", "website", "description"]
        important_fields = ["industry", "headquarters", "founded_year", "employees"]
        financial_fields = ["revenue", "funding_raised"]

        score = 0.0

        # Critical fields (0.6 total)
        for field in critical_fields:
            if data.get(field):
                score += 0.2

        # Important fields (0.3 total)
        for field in important_fields:
            if data.get(field):
                score += 0.075

        # Financial fields (0.1 total)
        for field in financial_fields:
            if data.get(field):
                score += 0.05

        return min(score, 1.0)


# ============================================================================
# AGENT 4: DATA VALIDATOR
# ============================================================================


class DataValidatorAgent:
    """Validates extracted data for sanity and consistency."""

    VALIDATION_RULES = {
        "revenue": {"min": 0, "max": 1_000_000, "unit": "millions"},
        "employees": {"min": 1, "max": 1_000_000, "unit": "count"},
        "founded_year": {"min": 1800, "max": 2026, "unit": "year"},
        "funding_raised": {"min": 0, "max": 100_000, "unit": "millions"},
        "valuation": {"min": 0, "max": 1_000_000, "unit": "millions"},
    }

    async def validate(self, data: ExtractedData) -> ValidationResult:
        """Validate extracted data."""
        issues = []
        confidence_adjustment = 0.0
        recommendations = []

        company_data = data.data

        # Rule-based validation
        for field, rules in self.VALIDATION_RULES.items():
            value = company_data.get(field)
            if value is None:
                continue

            if not isinstance(value, (int, float)):
                issues.append(f"{field} is not a number: {value}")
                confidence_adjustment -= 0.1
                continue

            if value < rules["min"] or value > rules["max"]:
                issues.append(f"{field}={value} outside valid range [{rules['min']}, {rules['max']}] {rules['unit']}")
                confidence_adjustment -= 0.15

        # Cross-field validation
        funding = company_data.get("funding_raised", 0) or 0
        valuation = company_data.get("valuation", 0) or 0

        if funding > 0 and valuation > 0:
            if funding > valuation * 0.9:
                issues.append(f"Funding ({funding}M) unusually high vs valuation ({valuation}M)")
                recommendations.append("Verify funding and valuation data")
                confidence_adjustment -= 0.1

        # Check for suspicious patterns
        employees = company_data.get("employees")
        revenue = company_data.get("revenue")

        if employees and revenue:
            revenue_per_employee = revenue / employees
            if revenue_per_employee > 10:  # >€10M per employee
                issues.append(f"Revenue per employee ({revenue_per_employee:.1f}M) unusually high")
                confidence_adjustment -= 0.1
            elif revenue_per_employee < 0.01:  # <€10K per employee
                issues.append(f"Revenue per employee ({revenue_per_employee:.3f}M) unusually low")
                confidence_adjustment -= 0.1

        return ValidationResult(
            is_valid=len(issues) == 0,
            issues=issues,
            confidence_adjustment=confidence_adjustment,
            recommendations=recommendations,
        )


# ============================================================================
# ORCHESTRATOR
# ============================================================================


class AIResearchOrchestrator:
    """Orchestrates multi-agent research workflow."""

    def __init__(self):
        self.planner = ResearchPlannerAgent()
        self.searcher = WebSearchAgent()
        self.extractor = ContentExtractorAgent()
        self.validator = DataValidatorAgent()

    async def research_company(
        self, company_name: str, industry: Optional[str] = None, max_sources: int = 8
    ) -> ResearchReport:
        """Perform full autonomous research on a company."""

        logger.info(f"🚀 Starting AI research for: {company_name}")
        start_time = datetime.now()

        report = ResearchReport(company_name=company_name)

        try:
            # Step 1: Create research plan
            plan = await self.planner.create_plan(company_name, industry)
            logger.info(f"📋 Research plan: {len(plan.queries)} queries")

            # Step 2: Execute searches
            all_search_results = []
            for query_info in plan.queries[:6]:  # Top 6 queries
                results = await self.searcher.search(query_info["query"], query_info["intent"], max_results=5)
                all_search_results.extend(results)
                await asyncio.sleep(0.5)  # Rate limiting

            # Deduplicate and select top sources
            seen_urls = set()
            unique_results = []
            for r in all_search_results:
                if r.url not in seen_urls and len(unique_results) < max_sources:
                    seen_urls.add(r.url)
                    unique_results.append(r)

            logger.info(f"🔍 Found {len(unique_results)} unique sources")

            # Step 3: Extract data from each source
            extracted_data_list = []
            for result in unique_results:
                extracted = await self.extractor.extract(result.url, company_name)
                if extracted.confidence > 0.2:  # Minimum confidence threshold
                    extracted_data_list.append(extracted)
                await asyncio.sleep(0.3)

            logger.info(f"📊 Extracted data from {len(extracted_data_list)} sources")

            # Step 4: Validate each extraction
            validated_data = []
            for extraction in extracted_data_list:
                validation = await self.validator.validate(extraction)

                # Adjust confidence based on validation
                adjusted_confidence = max(0, min(1, extraction.confidence + validation.confidence_adjustment))

                if adjusted_confidence > 0.3:
                    validated_data.append(
                        {"extraction": extraction, "validation": validation, "confidence": adjusted_confidence}
                    )

            # Step 5: Cross-reference and synthesize
            final_data = self._synthesize_data(validated_data, company_name)

            # Build report
            report = ResearchReport(
                company_name=company_name,
                is_synthetic=False,
                confidence_score=final_data.get("_confidence", 0.5),
                basic_info={
                    "website": final_data.get("website"),
                    "description": final_data.get("description"),
                    "industry": final_data.get("industry"),
                    "headquarters": final_data.get("headquarters"),
                    "founded_year": final_data.get("founded_year"),
                    "employees": final_data.get("employees"),
                },
                financials={
                    "revenue": final_data.get("revenue"),
                    "revenue_currency": final_data.get("revenue_currency", "EUR"),
                    "valuation": final_data.get("valuation"),
                },
                funding={
                    "total_raised": final_data.get("funding_raised"),
                    "rounds": final_data.get("funding_rounds", []),
                },
                data_sources=[
                    {
                        "url": d["extraction"].source_url,
                        "type": d["extraction"].source_type,
                        "confidence": d["confidence"],
                    }
                    for d in validated_data
                ],
                metadata={
                    "research_date": datetime.now().isoformat(),
                    "queries_executed": len(plan.queries),
                    "sources_found": len(unique_results),
                    "sources_used": len(validated_data),
                    "research_time_seconds": (datetime.now() - start_time).total_seconds(),
                },
            )

            logger.info(f"✅ Research complete for {company_name}: confidence={report.confidence_score:.2f}")

        except Exception as e:
            logger.error(f"Research failed for {company_name}: {e}")
            report.errors.append(str(e))

        return report

    def _synthesize_data(self, validated_data: List[Dict], company_name: str) -> Dict[str, Any]:
        """Merge data from multiple sources, preferring high-confidence values."""

        # Group by field
        field_values = {}

        for item in validated_data:
            data = item["extraction"].data
            confidence = item["confidence"]

            for field, value in data.items():
                if value is None:
                    continue

                if field not in field_values:
                    field_values[field] = []

                field_values[field].append(
                    {"value": value, "confidence": confidence, "source": item["extraction"].source_url}
                )

        # Select best value for each field
        final_data = {"_confidence": 0.0}
        total_confidence = 0.0
        field_count = 0

        for field, values in field_values.items():
            # Sort by confidence
            values.sort(key=lambda x: x["confidence"], reverse=True)

            # Take highest confidence value
            best = values[0]
            final_data[field] = best["value"]
            total_confidence += best["confidence"]
            field_count += 1

        if field_count > 0:
            final_data["_confidence"] = total_confidence / field_count

        return final_data


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    "AIResearchOrchestrator",
    "ResearchPlannerAgent",
    "WebSearchAgent",
    "ContentExtractorAgent",
    "DataValidatorAgent",
    "ResearchReport",
    "ResearchPlan",
    "SearchResult",
    "ExtractedData",
    "ValidationResult",
]
