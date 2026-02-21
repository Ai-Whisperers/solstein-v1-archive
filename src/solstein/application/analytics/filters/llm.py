"""LLM-based company filtering using natural language criteria."""

import os
from typing import Any

from loguru import logger
from pydantic import BaseModel, Field


class FilterResponse(BaseModel):
    matches: bool = Field(description="Whether the company matches the criteria")
    reasoning: str = Field(description="Reasoning for the match status")


class KeywordFilter:
    """Fallback keyword-based filter when LLM is unavailable."""

    KEYWORDS = {
        "tech": [
            "software",
            "technology",
            "tech",
            "digital",
            "ai",
            "cloud",
            "saas",
            "platform",
        ],
        "software": ["software", "saas", "app", "platform", "cloud"],
        "energy": [
            "energy",
            "renewable",
            "solar",
            "wind",
            "power",
            "electricity",
            "utilities",
        ],
        "fast growing": [
            "growth",
            "fast",
            "rapid",
            "high growth",
            "scaling",
            "expanding",
        ],
        "saas": ["saas", "software", "subscription", "cloud", "platform", "app"],
        "enterprise": ["enterprise", "b2b", "business", "corporate"],
        "startup": ["startup", "early stage", "seed", "series a", "founder"],
        "ai": [
            "ai",
            "artificial intelligence",
            "ml",
            "machine learning",
            "deep learning",
        ],
        "fintech": ["fintech", "financial", "banking", "payments", "insurance"],
        "healthcare": ["health", "medical", "pharma", "biotech", "life sciences"],
    }

    def matches_criteria(self, company: Any, criteria: str) -> tuple[bool, str]:
        criteria_lower = criteria.lower()
        company_info = self._format_company_info(company).lower()

        matched_keywords = []
        for keyword, related_terms in self.KEYWORDS.items():
            if keyword in criteria_lower:
                for term in related_terms:
                    if term in company_info:
                        matched_keywords.append(term)
                        break

        if matched_keywords:
            return True, f"Matched keywords: {', '.join(matched_keywords)}"

        return False, "No keyword match found"

    def _format_company_info(self, company: Any) -> str:
        parts = [
            company.name or "",
            getattr(company, "industry", "") or "",
        ]
        if company.financials:
            fin = company.financials
            if fin.revenue:
                parts.append(f"Revenue {fin.revenue}M")
            if fin.growth_rate:
                parts.append(f"Growth {fin.growth_rate}%")
        if company.geographic_presence:
            parts.append(" ".join(company.geographic_presence))
        return " ".join(parts)


class LLMFilter:
    """Filter companies using natural language criteria via LLM.

    Supports multiple backends:
    1. Ollama (local) - preferred if running
    2. OpenAI API
    3. Groq API
    4. Keyword-based fallback (no API needed)
    """

    def __init__(self):
        from solstein.core.config import get_settings

        settings = get_settings()
        self.groq_api_key = settings.groq_api_key
        self.openai_api_key = settings.openai_api_key
        self.fireworks_api_key = settings.fireworks_api_key
        self.ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
        self.ollama_model = os.environ.get("OLLAMA_MODEL", "llama3.2:latest")
        self._client = None
        self._keyword_filter = KeywordFilter()
        self._use_ollama = None

    def _check_ollama(self) -> bool:
        if self._use_ollama is not None:
            return self._use_ollama
        try:
            import httpx

            r = httpx.get(f"{self.ollama_url}/api/version", timeout=2)
            self._use_ollama = r.status_code == 200
        except Exception:
            self._use_ollama = False
        return self._use_ollama

    def _get_client(self):
        if self._client is None:
            if self.fireworks_api_key:
                from openai import AsyncOpenAI

                self._client = AsyncOpenAI(
                    api_key=self.fireworks_api_key,
                    base_url="https://api.fireworks.ai/inference/v1",
                )
            elif self.openai_api_key:
                from openai import AsyncOpenAI

                self._client = AsyncOpenAI(api_key=self.openai_api_key)
            elif self.groq_api_key:
                from groq import AsyncGroq

                self._client = AsyncGroq(api_key=self.groq_api_key)
        return self._client

    async def matches_criteria(self, company: Any, criteria: str) -> tuple[bool, str]:
        """Check if a company matches the natural language criteria.

        Tries in order:
        1. Ollama (local) - if available
        2. Cloud APIs (OpenAI, Groq) - if keys work
        3. Keyword fallback - always works

        Args:
            company: Company domain object
            criteria: Natural language filter criteria (e.g., "tech companies", "fast growing SaaS")

        Returns:
            Tuple of (matches: bool, reasoning: str)
        """
        if self._check_ollama():
            result = await self._query_ollama(company, criteria)
            if "Error" not in result[1]:
                return result

        if self._has_valid_api_key():
            result = await self._query_llm(company, criteria)
            if "Error" not in result[1]:
                return result

        return self._keyword_filter.matches_criteria(company, criteria)

    def _has_valid_api_key(self) -> bool:
        if self.groq_api_key:
            return True
        if self.openai_api_key:
            return True
        if self.fireworks_api_key:
            return True
        return False

    async def _query_ollama(self, company: Any, criteria: str) -> tuple[bool, str]:
        """Query local Ollama instance."""
        try:
            import httpx

            company_info = self._format_company_info(company)

            system_prompt = """You are a company analysis assistant. Given a company profile and a filter criteria, determine if the company matches. Respond ONLY with JSON: {"matches": true/false, "reasoning": "..."}"""

            user_prompt = f"""Company Profile:
{company_info}

Filter Criteria: "{criteria}"

Does this company match? JSON only."""

            async with (
                httpx.AsyncClient() as session,
                session.post(
                    f"{self.ollama_url}/api/chat",
                    json={
                        "model": self.ollama_model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        "temperature": 0.1,
                        "max_tokens": 200,
                        "stream": False,
                        "format": FilterResponse.model_json_schema(),
                    },
                    timeout=httpx.Timeout(30),
                ) as resp,
            ):
                if resp.status != 200:
                    raise Exception(f"Ollama returned {resp.status}")
                data = await resp.json()
                content = data.get("message", {}).get("content", "")

                try:
                    result = FilterResponse.model_validate_json(content)
                except Exception:
                    # Fallback string manipulation if ollama hallucinates wrapper
                    if "```json" in content:
                        clean = content.split("```json")[-1].split("```")[0].strip()
                        result = FilterResponse.model_validate_json(clean)
                    else:
                        raise
                return result.matches, f"[Ollama] {result.reasoning}"

        except Exception as e:
            logger.warning(f"Ollama error: {e}, falling back to keyword")
            return self._keyword_filter.matches_criteria(company, criteria)

    async def _query_llm(self, company: Any, criteria: str) -> tuple[bool, str]:
        """Query cloud LLM (OpenAI/Groq)."""
        client = self._get_client()
        if not client:
            return self._keyword_filter.matches_criteria(company, criteria)

        company_info = self._format_company_info(company)

        system_prompt = """You are a company analysis assistant. Given a company profile and a filter criteria, determine if the company matches. Respond ONLY with JSON: {"matches": true/false, "reasoning": "..."}"""

        user_prompt = f"""Company Profile:
{company_info}

Filter Criteria: "{criteria}"

Does this company match? JSON only."""

        try:
            if self.fireworks_api_key:
                model = "qwen2-72b-instruct"
            elif self.openai_api_key:
                model = "gpt-4o-mini"
            elif self.groq_api_key:
                model = "llama-3.3-70b-versatile"
            else:
                model = "gpt-4o-mini"

            if hasattr(client.chat.completions, "parse") and (
                self.openai_api_key or model.startswith("gpt")
            ):
                response = await client.beta.chat.completions.parse(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.1,
                    max_tokens=200,
                    response_format=FilterResponse,
                )
                result = response.choices[0].message.parsed
                if result:
                    return result.matches, result.reasoning
                raise Exception("Empty parsed response")
            else:
                response = await client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.1,
                    max_tokens=200,
                    response_format={"type": "json_object"},
                )
                result_text = response.choices[0].message.content
                result = FilterResponse.model_validate_json(result_text)
                return result.matches, result.reasoning

        except Exception as e:
            logger.warning(f"LLM API error: {e}, falling back to keyword")
            return self._keyword_filter.matches_criteria(company, criteria)

    def _format_company_info(self, company: Any) -> str:
        """Format company info for LLM prompt."""
        parts = [
            f"Name: {company.name}",
            f"Industry: {getattr(company, 'industry', 'Unknown')}",
        ]

        if company.financials:
            fin = company.financials
            if fin.revenue:
                parts.append(f"Revenue: €{fin.revenue}M")
            if fin.growth_rate:
                parts.append(f"Growth Rate: {fin.growth_rate}%")

        if company.tier:
            parts.append(f"Tier: {company.tier}")

        if company.ai_maturity:
            parts.append(f"AI Maturity: {company.ai_maturity}")

        if company.saas_maturity:
            parts.append(f"SaaS Maturity: {company.saas_maturity}/10")

        if company.geographic_presence:
            parts.append(
                f"Geographic Presence: {', '.join(company.geographic_presence)}"
            )

        return "\n".join(parts)


llm_filter = LLMFilter()
