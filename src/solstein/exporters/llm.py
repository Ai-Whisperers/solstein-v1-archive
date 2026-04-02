"""LLM-powered report enhancement module for SolStein.

EPIC-005: Excel Export Improvements
EPIC-022: Refactored to use modular report generators

Uses the enhanced LLM client with automatic health checking, smart retries,
and provider failover for reliable LLM operations.

Components are now modularized in the report_generators/ package:
- base.py: Base classes and schemas
- executive_summary.py: Executive summary generator
- swot.py: SWOT analysis generator
- recommendations.py: Strategic recommendations generator
- competitive_narrative.py: Competitive narrative generator
- market_insights.py: Market insights generator
"""

from __future__ import annotations

from typing import Any

from ..config import get_settings
from ..llm.enhanced_client import EnhancedLLMClient, get_enhanced_llm_client
from .report_generators import (
    CompetitiveNarrativeGenerator,
    ExecutiveSummaryGenerator,
    MarketInsightsGenerator,
    RecommendationsGenerator,
    StrategicRecommendations,
    SWOTAnalysis,
    SWOTGenerator,
)

__all__ = [
    "LLMReportEnhancer",
    "StrategicRecommendations",
    "SWOTAnalysis",
]


class LLMReportEnhancer:
    """Enhance reports with LLM-generated insights using Strategy Pattern.

    EPIC-022: Refactored to delegate to specialized report generators.
    Each report type has its own generator for modularity and testability.

    Uses the EnhancedLLMClient which provides:
    - Proactive health checking
    - Automatic provider failover
    - Smart retry with exponential backoff
    - Rate limit detection and handling

    Supports multiple backends:
    1. Ollama (local) - preferred
    2. OpenAI API
    3. Groq API
    4. Fireworks API
    """

    def __init__(self, enhanced_client: EnhancedLLMClient | None = None):
        """Initialize report enhancer with generators.

        Args:
            enhanced_client: Optional pre-configured enhanced client.
                           Creates new instance if not provided.
        """
        self.settings = get_settings()
        self._client = enhanced_client or get_enhanced_llm_client()

        # Initialize report generators (Strategy Pattern)
        self._generators = {
            "executive_summary": ExecutiveSummaryGenerator(self._client),
            "swot": SWOTGenerator(self._client),
            "recommendations": RecommendationsGenerator(self._client),
            "competitive_narrative": CompetitiveNarrativeGenerator(self._client),
            "market_insights": MarketInsightsGenerator(self._client),
        }

    def is_available(self) -> bool:
        """Check if any LLM backend is available.

        Avoids calling asyncio.get_event_loop().run_until_complete() which
        crashes with RuntimeError when an event loop is already running
        (e.g. inside FastAPI / any async framework).  Instead, perform a
        cheap synchronous check against the configured API keys for all
        providers that are actually in the priority rotation.
        """
        # Check all providers that are in the current priority list
        key_checks = {
            "deepinfra": self.settings.deepinfra_api_key,
            "mistral": self.settings.mistral_api_key,
            "nvidia": self.settings.nvidia_nim_api_key,
            "openai": self.settings.openai_api_key,
            "groq": self.settings.groq_api_key,
            "fireworks": self.settings.fireworks_api_key,
        }
        active_providers = getattr(self._client, "PROVIDER_PRIORITY", list(key_checks.keys()))
        return any(bool(key_checks.get(p)) for p in active_providers if p in key_checks)

    def _get_preferred_provider(self) -> str | None:
        """Get preferred provider from settings."""
        provider = (self.settings.llm_provider or "auto").strip().lower()
        if provider in {"auto", "none"}:
            return None
        return provider

    async def generate_executive_summary(self, company: Any, competitors: list[Any]) -> str:
        """Generate LLM-powered executive summary."""
        generator = self._generators["executive_summary"]
        return await generator.generate(company, competitors)

    async def generate_swot_analysis(self, company: Any, competitors: list[Any]) -> dict[str, list[str]]:
        """Generate LLM-powered SWOT analysis."""
        generator = self._generators["swot"]
        return await generator.generate(company, competitors)

    async def generate_strategic_recommendations(self, company: Any, competitors: list[Any]) -> list[str]:
        """Generate strategic recommendations."""
        generator = self._generators["recommendations"]
        return await generator.generate(company, competitors)

    async def generate_competitive_narrative(self, company: Any, competitors: list[Any]) -> str:
        """Generate competitive narrative analysis."""
        generator = self._generators["competitive_narrative"]
        return await generator.generate(company, competitors)

    async def generate_market_insights(self, companies: list[Any]) -> str:
        """Generate market-wide insights."""
        generator = self._generators["market_insights"]
        return await generator.generate(None, companies)


# Backward compatibility - maintain existing module interface
llm_enhancer = LLMReportEnhancer()
