"""
AI-powered autonomous research orchestration.

This module performs company research by combining an LLM planning/extraction
stage with web search and deterministic validation.
"""

import asyncio
import importlib
import importlib.util
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from loguru import logger

# Optional: DuckDuckGo search backend (loaded lazily)
_ddgs_class: Any | None = None
_duckduckgo_available = False

try:
    if importlib.util.find_spec("duckduckgo_search") is not None:
        module = importlib.import_module("duckduckgo_search")
        _ddgs_class = getattr(module, "DDGS", None)
        _duckduckgo_available = _ddgs_class is not None
    else:
        logger.warning("duckduckgo_search not installed. Web search will be disabled.")
except Exception as error:
    logger.warning(f"duckduckgo_search failed to initialize: {error}")

from ..llm.enhanced_client import EnhancedLLMClient


@dataclass
class ResearchPlan:
    """Research strategy for a company."""

    company_name: str
    queries: list[dict[str, Any]]
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
    data: dict[str, Any]
    confidence: float
    extraction_method: str
    extracted_at: datetime = field(default_factory=datetime.now)
    raw_content: str = ""


@dataclass
class ValidationResult:
    """Data validation outcome."""

    is_valid: bool
    issues: list[str]
    confidence_adjustment: float
    recommendations: list[str]


@dataclass
class ResearchReport:
    """Final research report for a company."""

    company_name: str
    is_synthetic: bool = False
    confidence_score: float = 0.0
    basic_info: dict[str, Any] = field(default_factory=dict)
    financials: dict[str, Any] = field(default_factory=dict)
    funding: dict[str, Any] = field(default_factory=dict)
    data_sources: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


class ResearchPlannerAgent:
    """Creates research strategies using the configured LLM provider."""

    def __init__(self, llm_client: EnhancedLLMClient | None = None) -> None:
        self.llm = llm_client or EnhancedLLMClient()

    async def create_plan(self, company_name: str, industry: str | None = None) -> ResearchPlan:
        """Generate a research plan with prioritized search queries."""
        industry_context = f"in the {industry} industry" if industry else ""
        prompt = f"""Create a detailed web research plan for: {company_name} {industry_context}

Your goal is to find factual information about this company from web sources.
Generate 6-8 specific search queries for website, funding, financials,
headcount, news, social presence, and industry positioning.

Return ONLY valid JSON in this format:
{{
  "queries": [
    {{"query": "...", "priority": 1, "intent": "website"}},
    {{"query": "...", "priority": 1, "intent": "funding"}}
  ],
  "estimated_sources": 5
}}
"""

        try:
            response = await self.llm.generate(prompt)
            if response is None or response == "":
                raise ValueError("Planner returned empty response")
            response_text = str(response)
            plan_data = json.loads(self._extract_json(response_text))
            queries = sorted(plan_data.get("queries", []), key=lambda item: item.get("priority", 3))
            return ResearchPlan(
                company_name=company_name,
                queries=queries,
                estimated_sources=plan_data.get("estimated_sources", 5),
            )
        except Exception as error:
            logger.error(f"Failed to create plan for {company_name}: {error}")
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
        """Extract JSON payload from an LLM response."""
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            return text[start:end].strip()

        if "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            return text[start:end].strip()

        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return text[start : end + 1]

        return text


class WebSearchAgent:
    """Performs web searches and relevance ranking.

    Primary backend: SearXNG (local instance, aggregates Brave+DDG+Google).
    Fallback: direct DuckDuckGo library.
    """

    SEARXNG_URL = "http://localhost:8889/search"

    def __init__(self) -> None:
        self.ddgs = _ddgs_class() if _duckduckgo_available and _ddgs_class is not None else None
        self.cache: dict[str, list[SearchResult]] = {}

    async def search(self, query: str, intent: str, max_results: int = 10) -> list[SearchResult]:
        """Execute search and return ranked results."""
        cache_key = f"{query}_{intent}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        results: list[SearchResult] = []

        # Primary: SearXNG (aggregates Brave, DDG, Google, Wikipedia)
        try:
            searxng_results = await self._search_searxng(query, max_results)
            results.extend(searxng_results)
            if searxng_results:
                logger.info(f"SearXNG returned {len(searxng_results)} results for '{query}'")
        except Exception as error:
            logger.warning(f"SearXNG search failed for '{query}': {error}")

        # Fallback: direct DuckDuckGo library
        if not results and self.ddgs is not None:
            try:
                ddg_results = await asyncio.to_thread(self._search_duckduckgo, query, max_results)
                results.extend(ddg_results)
                if ddg_results:
                    logger.info(f"DDG fallback returned {len(ddg_results)} results for '{query}'")
            except Exception as error:
                logger.warning(f"DuckDuckGo fallback failed for '{query}': {error}")

        if not results:
            logger.warning(f"All search backends returned 0 results for '{query}'")

        ranked = self._rank_by_relevance(results, intent)
        self.cache[cache_key] = ranked
        return ranked

    async def _search_searxng(self, query: str, max_results: int) -> list[SearchResult]:
        """Search using local SearXNG instance (aggregates multiple engines)."""
        results: list[SearchResult] = []
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(
                self.SEARXNG_URL,
                params={"q": query, "format": "json", "language": "en"},
            )
            response.raise_for_status()
            data = response.json()

            for item in data.get("results", [])[:max_results]:
                url = item.get("url", "")
                if not url:
                    continue
                results.append(
                    SearchResult(
                        title=item.get("title", ""),
                        url=url,
                        snippet=item.get("content", ""),
                        source=urlparse(url).netloc,
                    )
                )

            # Also pull infobox data as a bonus result if available
            for infobox in data.get("infoboxes", []):
                ib_url = infobox.get("id", "")
                if ib_url and ib_url.startswith("http"):
                    results.append(
                        SearchResult(
                            title=infobox.get("infobox", ""),
                            url=ib_url,
                            snippet=infobox.get("content", ""),
                            source=urlparse(ib_url).netloc,
                        )
                    )

        return results

    def _search_duckduckgo(self, query: str, max_results: int) -> list[SearchResult]:
        """Fallback: search using DuckDuckGo library."""
        if self.ddgs is None:
            return []

        results: list[SearchResult] = []
        for result in self.ddgs.text(query, max_results=max_results):
            href = result.get("href", "")
            results.append(
                SearchResult(
                    title=result.get("title", ""),
                    url=href,
                    snippet=result.get("body", ""),
                    source=urlparse(href).netloc,
                )
            )
        return results

    def _rank_by_relevance(self, results: list[SearchResult], intent: str) -> list[SearchResult]:
        """Rank search results by intent relevance and source quality."""
        intent_keywords: dict[str, list[str]] = {
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

            for keyword in keywords:
                if keyword in text:
                    score += 0.2

            if any(domain in result.source for domain in ["crunchbase.com", "linkedin.com", "bloomberg.com"]):
                score += 0.3
            elif any(domain in result.source for domain in ["techcrunch.com", "forbes.com", "reuters.com"]):
                score += 0.25
            elif ".gov" in result.source:
                score += 0.2

            if any(year in text for year in ["2024", "2025", "2026"]):
                score += 0.1

            result.relevance_score = min(score, 1.0)
            result.intent_match = intent

        return sorted(results, key=lambda item: item.relevance_score, reverse=True)


class ContentExtractorAgent:
    """Extracts structured data from web pages using an LLM."""

    def __init__(self, llm_client: EnhancedLLMClient | None = None) -> None:
        self.llm = llm_client or EnhancedLLMClient()
        self.http = httpx.AsyncClient(timeout=30.0, follow_redirects=True)

    async def extract(self, url: str, company_name: str) -> ExtractedData:
        """Extract structured data from a single URL."""
        try:
            html = await self._fetch_page(url)
            text = self._clean_html(html)
            if len(text) < 100:
                return ExtractedData(url, "error", {}, 0.0, "fetch_too_short", raw_content="")

            data = await self._llm_extract(text[:8000], company_name, url)
            source_type = self._classify_source(url)
            confidence = self._calculate_confidence(data)

            return ExtractedData(
                source_url=url,
                source_type=source_type,
                data=data,
                confidence=confidence,
                extraction_method="llm_parsing",
                raw_content=text[:2000],
            )
        except Exception as error:
            logger.error(f"Extraction failed for {url}: {error}")
            return ExtractedData(url, "error", {}, 0.0, f"error: {error}", raw_content="")

    async def _fetch_page(self, url: str) -> str:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; SolsteinResearchBot/1.0)"}
        response = await self.http.get(url, headers=headers)
        response.raise_for_status()
        return response.text

    def _clean_html(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        for node in soup(["script", "style", "nav", "footer"]):
            node.decompose()
        text = soup.get_text(separator="\n")
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        return "\n".join(chunk for chunk in chunks if chunk)

    async def _llm_extract(self, text: str, company_name: str, url: str) -> dict[str, Any]:
        prompt = f"""Extract structured company information from this content.
Company: {company_name}
Source: {url}

Return ONLY valid JSON (no markdown, no explanation) with these keys:
company_name, website, description, industry, headquarters, founded_year,
employees, revenue, revenue_currency, funding_raised, valuation,
funding_rounds, key_executives, products, is_public.
Use null for unknown values.

Content:
{text[:6000]}
"""
        try:
            response = await self.llm.generate(prompt)
            if response is None or response == "":
                raise ValueError("Extractor returned empty response")
            response_text = str(response)
            # Strip markdown code fences and extract JSON object
            json_str = self._extract_json_from_response(response_text)
            return json.loads(json_str)
        except Exception as error:
            logger.error(f"LLM extraction failed for {url}: {error}")
            return {}

    @staticmethod
    def _extract_json_from_response(text: str) -> str:
        """Extract JSON payload from an LLM response that may contain markdown fences."""
        # Strip markdown code fences
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            if end > start:
                return text[start:end].strip()

        if "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            if end > start:
                return text[start:end].strip()

        # Find raw JSON object
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return text[start : end + 1]

        return text

    def _classify_source(self, url: str) -> str:
        domain = urlparse(url).netloc.lower()
        if "crunchbase.com" in domain:
            return "crunchbase"
        if "linkedin.com" in domain:
            return "linkedin"
        if any(name in domain for name in ["bloomberg.com", "reuters.com", "forbes.com", "techcrunch.com"]):
            return "news"
        if "wikipedia.org" in domain:
            return "wikipedia"
        return "company_website"

    def _calculate_confidence(self, data: dict[str, Any]) -> float:
        critical_fields = ["company_name", "website", "description"]
        important_fields = ["industry", "headquarters", "founded_year", "employees"]
        financial_fields = ["revenue", "funding_raised"]

        score = 0.0
        score += sum(0.2 for key in critical_fields if data.get(key))
        score += sum(0.075 for key in important_fields if data.get(key))
        score += sum(0.05 for key in financial_fields if data.get(key))
        return min(score, 1.0)


class DataValidatorAgent:
    """Validates extracted data for sanity and consistency."""

    VALIDATION_RULES = {
        "revenue": {"min": 0, "max": 1_000_000},
        "employees": {"min": 1, "max": 1_000_000},
        "founded_year": {"min": 1800, "max": 2026},
        "funding_raised": {"min": 0, "max": 100_000},
        "valuation": {"min": 0, "max": 1_000_000},
    }

    @staticmethod
    def _to_number(value: Any) -> float | int | None:
        """Coerce a value to a number, returning None if impossible."""
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return value
        if isinstance(value, str):
            # Strip currency symbols, commas, whitespace
            cleaned = value.replace(",", "").replace("$", "").replace("€", "").replace("£", "").strip()
            if not cleaned:
                return None
            try:
                return float(cleaned) if "." in cleaned else int(cleaned)
            except ValueError:
                return None
        return None

    async def validate(self, data: ExtractedData) -> ValidationResult:
        issues: list[str] = []
        recommendations: list[str] = []
        confidence_adjustment = 0.0
        payload = data.data

        for field_name, rule in self.VALIDATION_RULES.items():
            raw_value = payload.get(field_name)
            if raw_value is None:
                continue
            value = self._to_number(raw_value)
            if value is None:
                issues.append(f"{field_name} is not numeric: {raw_value}")
                confidence_adjustment -= 0.1
                continue
            # Write back the coerced numeric value for downstream use
            payload[field_name] = value
            if value < rule["min"] or value > rule["max"]:
                issues.append(f"{field_name}={value} outside [{rule['min']}, {rule['max']}]")
                confidence_adjustment -= 0.15

        funding = self._to_number(payload.get("funding_raised")) or 0
        valuation = self._to_number(payload.get("valuation")) or 0
        if funding > 0 and valuation > 0 and funding > valuation * 0.9:
            issues.append(f"Funding ({funding}M) unusually high vs valuation ({valuation}M)")
            recommendations.append("Verify funding and valuation values")
            confidence_adjustment -= 0.1

        employees = self._to_number(payload.get("employees"))
        revenue = self._to_number(payload.get("revenue"))
        if employees and revenue and employees > 0:
            revenue_per_employee = revenue / employees
            if revenue_per_employee > 10:
                issues.append(f"Revenue per employee unusually high: {revenue_per_employee:.2f}M")
                confidence_adjustment -= 0.1
            elif revenue_per_employee < 0.01:
                issues.append(f"Revenue per employee unusually low: {revenue_per_employee:.3f}M")
                confidence_adjustment -= 0.1

        return ValidationResult(
            is_valid=len(issues) == 0,
            issues=issues,
            confidence_adjustment=confidence_adjustment,
            recommendations=recommendations,
        )


class AIResearchOrchestrator:
    """Orchestrates the multi-agent research workflow."""

    TARGET_FIELDS = [
        "website",
        "description",
        "industry",
        "headquarters",
        "founded_year",
        "employees",
        "revenue",
        "revenue_currency",
        "valuation",
        "funding_raised",
        "funding_rounds",
    ]

    def __init__(self) -> None:
        self.planner = ResearchPlannerAgent()
        self.searcher = WebSearchAgent()
        self.extractor = ContentExtractorAgent()
        self.validator = DataValidatorAgent()
        self.memory_path = Path("data/research_results/research_memory.json")
        self._memory = self._load_memory()

    def _load_memory(self) -> dict[str, Any]:
        if self.memory_path.exists():
            try:
                with open(self.memory_path) as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    return data
            except Exception as error:
                logger.warning(f"Failed loading research memory from {self.memory_path}: {error}")

        bootstrap_path = Path("data/research_results/research_results.json")
        if bootstrap_path.exists():
            try:
                with open(bootstrap_path) as f:
                    bootstrap = json.load(f)
                companies = bootstrap.get("companies", []) if isinstance(bootstrap, dict) else []
                if isinstance(companies, list):
                    memory: dict[str, Any] = {"companies": {}}
                    for report in companies:
                        if not isinstance(report, dict):
                            continue
                        company_name = report.get("company_name")
                        if not isinstance(company_name, str) or not company_name.strip():
                            continue
                        key = self._company_key(company_name)
                        urls: set[str] = set()
                        for source in report.get("data_sources", []):
                            if isinstance(source, dict):
                                url = source.get("url")
                                if isinstance(url, str) and url:
                                    urls.add(url)
                        memory["companies"][key] = {
                            "latest_report": report,
                            "known_urls": sorted(urls),
                            "updated_at": datetime.now().isoformat(),
                        }
                    return memory
            except Exception as error:
                logger.warning(f"Failed bootstrapping research memory from {bootstrap_path}: {error}")

        return {"companies": {}}

    def _save_memory(self) -> None:
        try:
            self.memory_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.memory_path, "w") as f:
                json.dump(self._memory, f, indent=2)
        except Exception as error:
            logger.warning(f"Failed saving research memory to {self.memory_path}: {error}")

    @staticmethod
    def _company_key(company_name: str) -> str:
        return " ".join(company_name.lower().split())

    @staticmethod
    def _score_completeness(payload: dict[str, Any], fields: list[str]) -> float:
        if not fields:
            return 0.0
        filled = 0
        for field_name in fields:
            value = payload.get(field_name)
            if value in (None, "", [], {}):
                continue
            filled += 1
        return filled / len(fields)

    def _previous_report(self, company_name: str) -> dict[str, Any] | None:
        company_key = self._company_key(company_name)
        company_entry = self._memory.get("companies", {}).get(company_key, {})
        report = company_entry.get("latest_report")
        return report if isinstance(report, dict) else None

    def _previous_urls(self, company_name: str) -> set[str]:
        company_key = self._company_key(company_name)
        company_entry = self._memory.get("companies", {}).get(company_key, {})
        urls = company_entry.get("known_urls", [])
        if isinstance(urls, list):
            return {url for url in urls if isinstance(url, str) and url}
        return set()

    @staticmethod
    def _flatten_report_fields(report_dict: dict[str, Any]) -> dict[str, Any]:
        basic = report_dict.get("basic_info", {}) if isinstance(report_dict.get("basic_info"), dict) else {}
        financials = report_dict.get("financials", {}) if isinstance(report_dict.get("financials"), dict) else {}
        funding = report_dict.get("funding", {}) if isinstance(report_dict.get("funding"), dict) else {}
        return {
            "website": basic.get("website"),
            "description": basic.get("description"),
            "industry": basic.get("industry"),
            "headquarters": basic.get("headquarters"),
            "founded_year": basic.get("founded_year"),
            "employees": basic.get("employees"),
            "revenue": financials.get("revenue"),
            "revenue_currency": financials.get("revenue_currency"),
            "valuation": financials.get("valuation"),
            "funding_raised": funding.get("total_raised"),
            "funding_rounds": funding.get("rounds"),
        }

    def _merge_with_previous(self, company_name: str, current: ResearchReport) -> tuple[ResearchReport, int]:
        previous = self._previous_report(company_name)
        if not previous:
            return current, 0

        previous_fields = self._flatten_report_fields(previous)
        merged_fields = self._flatten_report_fields(
            {
                "basic_info": current.basic_info,
                "financials": current.financials,
                "funding": current.funding,
            }
        )

        carry_forward_count = 0
        for field_name in self.TARGET_FIELDS:
            if merged_fields.get(field_name) in (None, "", [], {}):
                previous_value = previous_fields.get(field_name)
                if previous_value not in (None, "", [], {}):
                    merged_fields[field_name] = previous_value
                    carry_forward_count += 1

        current.basic_info = {
            "website": merged_fields.get("website"),
            "description": merged_fields.get("description"),
            "industry": merged_fields.get("industry"),
            "headquarters": merged_fields.get("headquarters"),
            "founded_year": merged_fields.get("founded_year"),
            "employees": merged_fields.get("employees"),
        }
        current.financials = {
            "revenue": merged_fields.get("revenue"),
            "revenue_currency": merged_fields.get("revenue_currency") or "EUR",
            "valuation": merged_fields.get("valuation"),
        }
        current.funding = {
            "total_raised": merged_fields.get("funding_raised"),
            "rounds": merged_fields.get("funding_rounds") if merged_fields.get("funding_rounds") is not None else [],
        }

        previous_sources = previous.get("data_sources", []) if isinstance(previous.get("data_sources"), list) else []
        seen_urls: set[str] = set()
        merged_sources: list[dict[str, Any]] = []
        for source in current.data_sources + previous_sources:
            if not isinstance(source, dict):
                continue
            url = source.get("url")
            if not isinstance(url, str) or not url or url in seen_urls:
                continue
            seen_urls.add(url)
            merged_sources.append(source)
        current.data_sources = merged_sources

        return current, carry_forward_count

    def _persist_report(self, report: ResearchReport) -> None:
        company_key = self._company_key(report.company_name)
        companies = self._memory.setdefault("companies", {})
        entry = companies.setdefault(company_key, {})
        report_dict = {
            "company_name": report.company_name,
            "is_synthetic": report.is_synthetic,
            "confidence_score": report.confidence_score,
            "basic_info": report.basic_info,
            "financials": report.financials,
            "funding": report.funding,
            "data_sources": report.data_sources,
            "metadata": report.metadata,
            "errors": report.errors,
        }
        known_urls = {url for url in self._previous_urls(report.company_name)}
        for source in report.data_sources:
            url = source.get("url") if isinstance(source, dict) else None
            if isinstance(url, str) and url:
                known_urls.add(url)

        entry["latest_report"] = report_dict
        entry["known_urls"] = sorted(known_urls)
        entry["updated_at"] = datetime.now().isoformat()
        self._save_memory()

    async def research_company(
        self, company_name: str, industry: str | None = None, max_sources: int = 8
    ) -> ResearchReport:
        """Perform full autonomous research on a company."""
        start_time = datetime.now()
        report = ResearchReport(company_name=company_name)
        previous_report = self._previous_report(company_name)
        previous_urls = self._previous_urls(company_name)

        if previous_report:
            previous_flat = self._flatten_report_fields(previous_report)
            completeness = self._score_completeness(previous_flat, self.TARGET_FIELDS)
            if completeness >= 0.65:
                report = ResearchReport(
                    company_name=company_name,
                    is_synthetic=bool(previous_report.get("is_synthetic", False)),
                    confidence_score=float(previous_report.get("confidence_score", 0.0)),
                    basic_info=previous_report.get("basic_info", {}),
                    financials=previous_report.get("financials", {}),
                    funding=previous_report.get("funding", {}),
                    data_sources=previous_report.get("data_sources", []),
                    metadata={
                        **(previous_report.get("metadata", {}) if isinstance(previous_report.get("metadata"), dict) else {}),
                        "research_date": datetime.now().isoformat(),
                        "cache_reuse": True,
                        "previous_completeness": round(completeness, 3),
                        "sources_reused": len(previous_urls),
                        "research_time_seconds": (datetime.now() - start_time).total_seconds(),
                    },
                    errors=list(previous_report.get("errors", [])) if isinstance(previous_report.get("errors"), list) else [],
                )
                self._persist_report(report)
                return report

        try:
            plan = await self.planner.create_plan(company_name, industry)

            all_search_results: list[SearchResult] = []
            for query_info in plan.queries[:6]:
                query = query_info.get("query", "")
                intent = query_info.get("intent", "general")
                if not query:
                    continue
                all_search_results.extend(await self.searcher.search(query, intent, max_results=5))
                await asyncio.sleep(0.3)

            unique_results: list[SearchResult] = []
            seen_urls: set[str] = set()
            known_urls = set(previous_urls)
            deferred_known: list[SearchResult] = []
            for result in all_search_results:
                if result.url and result.url not in seen_urls:
                    seen_urls.add(result.url)
                    if result.url in known_urls:
                        deferred_known.append(result)
                    else:
                        unique_results.append(result)
                if len(unique_results) >= max_sources:
                    break

            if len(unique_results) < max_sources:
                for result in deferred_known:
                    unique_results.append(result)
                    if len(unique_results) >= max_sources:
                        break

            extracted_data_list: list[ExtractedData] = []
            for result in unique_results:
                extracted = await self.extractor.extract(result.url, company_name)
                if extracted.confidence > 0.2:
                    extracted_data_list.append(extracted)
                await asyncio.sleep(0.2)

            validated_data: list[dict[str, Any]] = []
            for extraction in extracted_data_list:
                validation = await self.validator.validate(extraction)
                adjusted_confidence = max(0.0, min(1.0, extraction.confidence + validation.confidence_adjustment))
                if adjusted_confidence > 0.3:
                    validated_data.append(
                        {
                            "extraction": extraction,
                            "validation": validation,
                            "confidence": adjusted_confidence,
                        }
                    )

            final_data = self._synthesize_data(validated_data)
            report = ResearchReport(
                company_name=company_name,
                is_synthetic=False,
                confidence_score=final_data.get("_confidence", 0.0),
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
                        "url": item["extraction"].source_url,
                        "type": item["extraction"].source_type,
                        "confidence": item["confidence"],
                    }
                    for item in validated_data
                ],
                metadata={
                    "research_date": datetime.now().isoformat(),
                    "queries_executed": len(plan.queries),
                    "sources_found": len(unique_results),
                    "sources_used": len(validated_data),
                    "known_sources_skipped": max(0, len(previous_urls) - len([r for r in unique_results if r.url in previous_urls])),
                    "known_sources_revisited": len([r for r in unique_results if r.url in previous_urls]),
                    "research_time_seconds": (datetime.now() - start_time).total_seconds(),
                },
            )

            report, carry_forward_count = self._merge_with_previous(company_name, report)
            report.metadata["fields_carried_forward"] = carry_forward_count
        except Exception as error:
            logger.error(f"Research failed for {company_name}: {error}")
            report.errors.append(str(error))

        self._persist_report(report)
        return report

    def _synthesize_data(self, validated_data: list[dict[str, Any]]) -> dict[str, Any]:
        """Merge data from multiple sources, preferring higher-confidence values."""
        field_values: dict[str, list[dict[str, Any]]] = {}

        for item in validated_data:
            extraction = item["extraction"]
            confidence = item["confidence"]
            for f_name, value in extraction.data.items():
                if value is None:
                    continue
                field_values.setdefault(f_name, []).append(
                    {"value": value, "confidence": confidence, "source": extraction.source_url}
                )

        final_data: dict[str, Any] = {"_confidence": 0.0}
        total_confidence = 0.0
        field_count = 0

        for f_name, values in field_values.items():
            values.sort(key=lambda item: item["confidence"], reverse=True)
            best = values[0]
            final_data[f_name] = best["value"]
            total_confidence += best["confidence"]
            field_count += 1

        if field_count > 0:
            final_data["_confidence"] = total_confidence / field_count

        return final_data


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
