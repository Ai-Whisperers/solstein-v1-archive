"""Instructor-wrapped LLM client for schema-validated structured outputs.

STORY-072: Wraps OpenAI-compatible and Anthropic SDK clients with Instructor
to enforce Pydantic schema validation on LLM responses. Retries on schema
violations with validation error feedback.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TypeVar

import instructor
from loguru import logger
from pydantic import BaseModel

from ..config import get_settings
from .prompts import get_system_prompt
from .provider_strategies import ProviderClientFactory

T = TypeVar("T", bound=BaseModel)

# Instructor retry config: retry up to 2 times on schema violations
_MAX_RETRIES = 2


@dataclass
class _ExtractionRequest:
    """Bundled parameters shared by Anthropic and OpenAI extraction paths."""

    model: str
    system: str
    prompt: str
    schema: type  # type[T] — generic not supported in dataclasses at runtime
    max_retries: int


class InstructorClient:
    """Schema-enforcing LLM client powered by Instructor.

    Patches SDK clients (OpenAI-compatible or Anthropic) so that
    ``create()`` calls validate responses against a Pydantic model.
    Schema violations trigger automatic retries with validation feedback.

    Free-text outputs bypass Instructor entirely - use ``EnhancedLLMClient.generate()``
    for those.
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        self._patched_clients: dict[str, Any] = {}

    def _get_patched_client(self, provider: str) -> Any:
        """Get or create an Instructor-patched client for a provider."""
        if provider in self._patched_clients:
            return self._patched_clients[provider]

        client = self._create_raw_client(provider)
        if client is None:
            raise RuntimeError(f"No API key configured for provider: {provider}")

        if provider == "anthropic":
            patched = instructor.from_anthropic(client)
        else:
            patched = instructor.from_openai(client)

        self._patched_clients[provider] = patched
        return patched

    def _create_raw_client(self, provider: str) -> Any | None:
        """Create a raw SDK client for the given provider."""
        return ProviderClientFactory.create_client(provider, self.settings)

    def _get_model(self, provider: str) -> str:
        """Get model name for a provider."""
        return getattr(self.settings, f"{provider}_model", "gpt-4o-mini")

    async def extract(
        self,
        prompt: str,
        schema: type[T],
        system_prompt: str | None = None,
        provider: str | None = None,
        max_retries: int = _MAX_RETRIES,
    ) -> T:
        """Extract structured data from an LLM, validated against a Pydantic schema.

        Args:
            prompt: User prompt describing what to extract.
            schema: Pydantic model class defining the expected response shape.
            system_prompt: Optional system prompt for context.
            provider: LLM provider to use. Defaults to first available.
            max_retries: Number of retries on schema violation (default 2).

        Returns:
            A validated Pydantic model instance.

        Raises:
            instructor.exceptions.InstructorRetryException: If all retries exhausted.
            RuntimeError: If no provider is available.
        """
        provider = provider or self._pick_provider()
        model = self._get_model(provider)
        system = system_prompt or get_system_prompt("system_data_extractor")
        patched_client = self._get_patched_client(provider)

        logger.debug(
            "[InstructorClient] Extracting structured output",
            extra={"provider": provider, "model": model, "schema": schema.__name__},
        )

        req = _ExtractionRequest(
            model=model,
            system=system,
            prompt=prompt,
            schema=schema,
            max_retries=max_retries,
        )

        if provider == "anthropic":
            return await self._extract_anthropic(patched_client, req)  # type: ignore[return-value]
        return await self._extract_openai(patched_client, req)  # type: ignore[return-value]

    async def _extract_anthropic(self, client: Any, req: _ExtractionRequest) -> Any:
        """Extract via Anthropic's native messages API."""
        return await client.messages.create(
            model=req.model,
            max_tokens=2000,
            max_retries=req.max_retries,
            messages=[{"role": "user", "content": req.prompt}],
            system=req.system,
            response_model=req.schema,
            temperature=0.3,
        )

    async def _extract_openai(self, client: Any, req: _ExtractionRequest) -> Any:
        """Extract via OpenAI-compatible chat completions API."""
        return await client.chat.completions.create(
            model=req.model,
            max_tokens=2000,
            max_retries=req.max_retries,
            messages=[
                {"role": "system", "content": req.system},
                {"role": "user", "content": req.prompt},
            ],
            response_model=req.schema,
            temperature=0.3,
        )

    def _pick_provider(self) -> str:
        """Pick the first available provider."""
        for provider in get_settings().llm_provider_order:
            if self._create_raw_client(provider) is not None:
                return provider
        raise RuntimeError("No LLM provider available (no API keys configured)")
