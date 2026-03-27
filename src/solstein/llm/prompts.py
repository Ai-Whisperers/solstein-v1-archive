"""Prompt management with Langfuse integration.

STORY-073: Prompts are stored as named, versioned entities in Langfuse.
When Langfuse is unavailable, falls back to local default prompts.

Usage::

    from solstein.llm.prompts import get_prompt

    prompt = get_prompt("research_planner", company_name="Acme")
"""

from __future__ import annotations

from typing import Any

from loguru import logger

# ---------------------------------------------------------------------------
# Local default prompts (fallback when Langfuse is unavailable)
# ---------------------------------------------------------------------------

_DEFAULT_PROMPTS: dict[str, str] = {
    "research_planner": (
        "Create a detailed web research plan for: {company_name} {industry_context}\n\n"
        "Generate 6-8 specific search queries for website, funding, financials, "
        "headcount, news, social presence, and industry positioning."
    ),
    "company_extractor": (
        "Extract structured company information from this content.\n"
        "Company: {company_name}\nSource: {url}\n\n"
        "Content:\n{content}"
    ),
    "system_research_planner": (
        "You are a research planning assistant. Generate structured "
        "search plans for competitive intelligence research."
    ),
    "system_company_extractor": (
        "You are a company data extraction specialist. "
        "Extract all available structured information about the company. "
        "Use null for unknown values."
    ),
    "system_business_analyst": (
        "You are an expert business analyst specializing in technology "
        "companies and private equity. Provide concise, data-driven insights."
    ),
    "system_data_extractor": (
        "You are an expert data extractor. Return structured data "
        "matching the requested schema. Use null for unknown values."
    ),
}


class PromptManager:
    """Manages prompts with Langfuse-first, local-fallback retrieval.

    Tries to fetch the named prompt from Langfuse. If Langfuse is unavailable
    or the prompt doesn't exist, falls back to local defaults.
    """

    def __init__(self, langfuse_client: Any | None = None) -> None:
        self._langfuse = langfuse_client

    def get(self, name: str, **kwargs: Any) -> str:
        """Retrieve a prompt by name, formatted with kwargs.

        Args:
            name: Prompt name (e.g. 'research_planner').
            **kwargs: Variables to interpolate into the prompt template.

        Returns:
            Formatted prompt string.
        """
        template = self._fetch_from_langfuse(name)
        if template is None:
            template = _DEFAULT_PROMPTS.get(name)

        if template is None:
            logger.warning(f"[PromptManager] Unknown prompt: {name}")
            return ""

        try:
            return template.format(**kwargs)
        except KeyError as exc:
            logger.warning(f"[PromptManager] Missing variable in prompt '{name}': {exc}")
            return template

    def _fetch_from_langfuse(self, name: str) -> str | None:
        """Try to fetch a prompt from Langfuse. Returns None on failure."""
        if self._langfuse is None:
            return None
        try:
            prompt = self._langfuse.get_prompt(name)
            return prompt.prompt if hasattr(prompt, "prompt") else str(prompt)
        except Exception as exc:  # noqa: BLE001
            logger.debug(f"[PromptManager] Langfuse prompt fetch failed for '{name}': {exc}")
            return None


# Module-level singleton
_prompt_manager: PromptManager | None = None


def get_prompt_manager(langfuse_client: Any | None = None) -> PromptManager:
    """Return the process-wide PromptManager singleton."""
    global _prompt_manager
    if _prompt_manager is None:
        _prompt_manager = PromptManager(langfuse_client=langfuse_client)
    return _prompt_manager


def get_prompt(name: str, **kwargs: Any) -> str:
    """Convenience function to get a formatted prompt."""
    return get_prompt_manager().get(name, **kwargs)
