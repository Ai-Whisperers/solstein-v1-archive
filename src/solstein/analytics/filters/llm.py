"""LLM-based company filtering using natural language criteria."""

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
        from ...config import get_settings

        settings = get_settings()
        self.groq_api_key = settings.groq_api_key
        self.openai_api_key = settings.openai_api_key
        self.fireworks_api_key = settings.fireworks_api_key
        self.llm_provider = settings.llm_provider
        self.ollama_url = settings.ollama_url
        self.ollama_model = settings.ollama_model
        self.openai_model = settings.openai_model
        self.groq_model = settings.groq_model
        self.fireworks_model = settings.fireworks_model
        self._client = None
        self._keyword_filter = KeywordFilter()
        self._use_ollama = None

    def _normalize_provider(self) -> str:
        provider = (self.llm_provider or "auto").strip().lower()
        allowed = {"auto", "ollama", "fireworks", "openai", "groq", "none"}
        if provider in allowed:
            return provider
        logger.warning(f"Unknown LLM provider '{self.llm_provider}', using 'auto'")
        return "auto"

    def _get_cloud_provider(self) -> str | None:
        provider = self._normalize_provider()

        if provider == "none":
            return None
        if provider == "openai":
            return "openai" if self.openai_api_key else None
        if provider == "groq":
            return "groq" if self.groq_api_key else None
        if provider == "fireworks":
            return "fireworks" if self.fireworks_api_key else None

        if self.fireworks_api_key:
            return "fireworks"
        if self.openai_api_key:
            return "openai"
        if self.groq_api_key:
            return "groq"
        return None

    def _check_ollama(self) -> bool:
        provider = self._normalize_provider()
        if provider not in {"auto", "ollama"}:
            self._use_ollama = False
            return False
        if self._use_ollama is not None:
            return self._use_ollama
        try:
            import requests

            r = requests.get(f"{self.ollama_url}/api/version", timeout=2)
            self._use_ollama = r.status_code == 200
        except Exception:
            self._use_ollama = False
        return self._use_ollama

    def _get_client(self):
        if self._client is None:
            provider = self._get_cloud_provider()
            if provider == "fireworks":
                try:
                    from openai import AsyncOpenAI

                    self._client = AsyncOpenAI(
                        api_key=self.fireworks_api_key,
                        base_url="https://api.fireworks.ai/inference/v1",
                    )
                except Exception:
                    self._client = None
            elif provider == "openai":
                try:
                    from openai import AsyncOpenAI

                    self._client = AsyncOpenAI(api_key=self.openai_api_key)
                except Exception:
                    self._client = None
            elif provider == "groq":
                try:
                    import importlib

                    groq_mod = importlib.import_module("groq")
                    async_groq = groq_mod.AsyncGroq
                    self._client = async_groq(api_key=self.groq_api_key)
                except Exception:
                    self._client = None
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
        provider = self._normalize_provider()
        if provider == "none":
            return False
        if provider == "openai":
            return bool(self.openai_api_key)
        if provider == "groq":
            return bool(self.groq_api_key)
        if provider == "fireworks":
            return bool(self.fireworks_api_key)
        return bool(self.groq_api_key or self.openai_api_key or self.fireworks_api_key)

    async def _query_ollama(self, company: Any, criteria: str) -> tuple[bool, str]:
        """Query local Ollama instance."""
        try:
            import aiohttp

            company_info = self._format_company_info(company)

            system_prompt = """You are a company analysis assistant. Given a company profile and a filter criteria, determine if the company matches. Respond ONLY with JSON: {"matches": true/false, "reasoning": "..."}"""

            user_prompt = f"""Company Profile:
{company_info}

Filter Criteria: "{criteria}"

Does this company match? JSON only."""

            async with (
                aiohttp.ClientSession() as session,
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
                    timeout=aiohttp.ClientTimeout(total=30),
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

        provider = self._get_cloud_provider()
        if not provider:
            return self._keyword_filter.matches_criteria(company, criteria)

        company_info = self._format_company_info(company)

        system_prompt = """You are a company analysis assistant. Given a company profile and a filter criteria, determine if the company matches. Respond ONLY with JSON: {"matches": true/false, "reasoning": "..."}"""

        user_prompt = f"""Company Profile:
{company_info}

Filter Criteria: "{criteria}"

Does this company match? JSON only."""

        try:
            if provider == "fireworks":
                model = self.fireworks_model
            elif provider == "openai":
                model = self.openai_model
            else:
                model = self.groq_model

            use_parse = (
                provider == "openai"
                and hasattr(client, "beta")
                and hasattr(client.beta, "chat")
                and hasattr(client.beta.chat.completions, "parse")
            )

            if use_parse:
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
                raise RuntimeError("Empty parsed response")

            create_kwargs = {}
            if provider in {"openai", "fireworks"}:
                create_kwargs["response_format"] = {"type": "json_object"}

            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
                max_tokens=200,
                **create_kwargs,
            )
            result_text = response.choices[0].message.content
            if not result_text:
                raise RuntimeError("Empty response content")
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
            parts.append(f"Geographic Presence: {', '.join(company.geographic_presence)}")

        return "\n".join(parts)


llm_filter = LLMFilter()
