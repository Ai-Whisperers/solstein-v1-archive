"""
Research agent classes for the AI research orchestrator.

Extracted from ai_research_orchestrator.py to reduce file size.
Contains planner, extraction, and validation agents.
"""

from __future__ import annotations

import json
from typing import Any
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from loguru import logger

from ..llm.enhanced_client import EnhancedLLMClient
from .fetch_policy import FetchResult, execute_policy_fetch
from .research_types import (
    ExtractedData,
    ResearchPlan,
    ResearchReport,
    SearchResult,
    ValidationResult,
)
from .web_search_agent import WebSearchAgent

# ---------------------------------------------------------------------------
# Agent classes
# ---------------------------------------------------------------------------


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
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
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

    @staticmethod
    def _extract_json(text: str) -> str:
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


def classify_source(url: str) -> str:
    """Classify a URL into a source category."""
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


class ContentExtractorAgent:
    """Extracts structured data from web pages using an LLM."""

    def __init__(self, llm_client: EnhancedLLMClient | None = None) -> None:
        self.llm = llm_client or EnhancedLLMClient()
        self.http = httpx.AsyncClient(timeout=30.0, follow_redirects=True)

    async def aclose(self) -> None:
        """Close the underlying HTTP client and release connection pool."""
        await self.http.aclose()

    async def __aenter__(self) -> ContentExtractorAgent:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.aclose()

    async def extract(self, url: str, company_name: str) -> ExtractedData:
        """Extract structured data from a single URL."""
        try:
            fetch_result = await self._fetch_page(url)
            if not fetch_result.success:
                logger.warning(
                    f"Fetch failed for {url}: {fetch_result.terminal_outcome.value}",
                    extra={"fetch_metadata": fetch_result.to_metadata()},
                )
                return ExtractedData(
                    url,
                    "error",
                    {"_fetch_metadata": fetch_result.to_metadata()},
                    0.0,
                    f"fetch_failed:{fetch_result.terminal_outcome.value}",
                    raw_content="",
                )

            text = self._clean_html(fetch_result.content)
            if len(text) < 100:
                return ExtractedData(url, "error", {}, 0.0, "fetch_too_short", raw_content="")

            data = await self._llm_extract(text[:8000], company_name, url)
            source_type = classify_source(url)
            confidence = self._calculate_confidence(data)
            data["_fetch_metadata"] = fetch_result.to_metadata()

            return ExtractedData(
                source_url=url,
                source_type=source_type,
                data=data,
                confidence=confidence,
                extraction_method="llm_parsing",
                raw_content=text[:2000],
            )
        except (httpx.HTTPError, json.JSONDecodeError, ValueError, KeyError) as error:
            logger.error(f"Extraction failed for {url}: {error}")
            return ExtractedData(url, "error", {}, 0.0, f"error: {error}", raw_content="")

    def is_usable(self, text: str, content_type: str) -> bool:
        """UsabilityChecker protocol: check if fetched content is usable."""
        return self._is_usable_content(text, content_type)

    def looks_blocked(self, text: str) -> bool:
        """UsabilityChecker protocol: check if page appears blocked."""
        return self._looks_blocked_page(text)

    async def _fetch_page(self, url: str) -> FetchResult:
        """Fetch a page using domain-aware policy matrix."""
        return await execute_policy_fetch(url, self.http, self)

    @staticmethod
    def _looks_blocked_page(text: str) -> bool:
        lower = text.lower()
        blocked_markers = [
            "enable javascript",
            "access denied",
            "are you a human",
            "captcha",
            "bot detection",
            "cloudflare",
            "forbidden",
            "please sign in",
            "login required",
        ]
        return any(marker in lower for marker in blocked_markers)

    @staticmethod
    def _visible_text_length(text: str) -> int:
        try:
            soup = BeautifulSoup(text, "html.parser")
            visible = soup.get_text(" ", strip=True)
            if visible:
                return len(visible)
        except (TypeError, AttributeError) as error:
            logger.debug(f"Visible-text parse failed, using fallback length: {error}")
        return len(" ".join(text.split()))

    def _is_usable_content(self, text: str, content_type: str) -> bool:
        if not text:
            return False
        if "application/pdf" in content_type:
            return False
        if self._looks_blocked_page(text):
            return False
        return len(text) >= 300 and self._visible_text_length(text) >= 120

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
            json_str = self._extract_json_from_response(response_text)
            return json.loads(json_str)
        except (json.JSONDecodeError, ValueError, TypeError) as error:
            logger.error(f"LLM extraction failed for {url}: {error}")
            return {}

    @staticmethod
    def _extract_json_from_response(text: str) -> str:
        """Extract JSON payload from an LLM response that may contain markdown fences."""
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
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return text[start : end + 1]
        return text

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


__all__ = [
    "ResearchPlan",
    "SearchResult",
    "ExtractedData",
    "ValidationResult",
    "ResearchReport",
    "ResearchPlannerAgent",
    "WebSearchAgent",
    "ContentExtractorAgent",
    "DataValidatorAgent",
    "classify_source",
]
