"""LLM-based company filtering using natural language criteria.

Uses the enhanced LLM client with automatic health checking and failover.
"""

from __future__ import annotations

from typing import Any

from loguru import logger
from pydantic import BaseModel, Field

from ...config import get_settings
from ...llm.enhanced_client import EnhancedLLMClient, get_enhanced_llm_client
from ...llm.prompts import get_system_prompt


class FilterResponse(BaseModel):
    """Filter response schema."""

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
        """Check if company matches criteria using keyword matching.

        Args:
            company: Company domain object
            criteria: Natural language filter criteria

        Returns:
            Tuple of (matches: bool, reasoning: str)
        """
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
        """Format company info for keyword matching."""
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

    Uses the EnhancedLLMClient for automatic failover between providers.

    Supports multiple backends:
    1. Ollama (local) - preferred if running
    2. OpenAI API
    3. Groq API
    4. Fireworks API
    5. Keyword-based fallback (no API needed)

    Example:
        >>> filter = LLMFilter()
        >>> matches, reasoning = await filter.matches_criteria(company, "fast growing tech")
        >>> print(matches)
        True
    """

    def __init__(self, enhanced_client: EnhancedLLMClient | None = None):
        """Initialize LLM filter.

        Args:
            enhanced_client: Optional pre-configured enhanced client.
                           Creates new instance if not provided.
        """
        self.settings = get_settings()
        self._client = enhanced_client or get_enhanced_llm_client()
        self._keyword_filter = KeywordFilter()

    def _get_preferred_provider(self) -> str | None:
        """Get preferred provider from settings."""
        provider = (self.settings.llm_provider or "auto").strip().lower()
        if provider in {"auto", "none"}:
            return None
        return provider

    async def matches_criteria(self, company: Any, criteria: str) -> tuple[bool, str]:
        """Check if a company matches the natural language criteria.

        Tries in order:
        1. Enhanced LLM client with automatic provider failover
        2. Keyword fallback - always works

        Args:
            company: Company domain object
            criteria: Natural language filter criteria (e.g., "tech companies", "fast growing SaaS")

        Returns:
            Tuple of (matches: bool, reasoning: str)
        """
        company_info = self._format_company_info(company)

        system_prompt = get_system_prompt("system_company_filter")

        user_prompt = (
            f"Company Profile:\n{company_info}\n\n"
            f'Filter Criteria: "{criteria}"\n\n'
            "Does this company match? JSON only."
        )

        # Try using the enhanced LLM client
        try:
            result = await self._client.generate_structured(
                prompt=user_prompt,
                schema=FilterResponse,
                system_prompt=system_prompt,
                preferred_provider=self._get_preferred_provider(),
            )

            if result:
                return result.matches, f"[LLM] {result.reasoning}"

        except Exception as e:  # noqa: BLE001 - broad catch intentional for LLM failover
            logger.warning(f"LLM filter failed: {e}, falling back to keyword")

        # Fallback to keyword filter
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


# Global instances for backward compatibility
keyword_filter = KeywordFilter()
llm_filter = LLMFilter()
