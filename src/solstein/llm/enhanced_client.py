"""Enhanced LLM client with health checking, smart retries, and provider rotation.

EPIC-022: Refactored to use query handler classes.
"""

from __future__ import annotations

import asyncio
from typing import Any, TypeVar

from loguru import logger
from pydantic import BaseModel

from ..config import get_settings
from .health_checker import (
    ProviderErrorType,
    ProviderHealthChecker,
    get_health_checker,
)
from .query import CloudProviderQuerier, OllamaQuerier

TBaseModel = TypeVar("TBaseModel", bound=BaseModel)


class LLMGenerationError(Exception):
    """Raised when all LLM providers fail."""

    def __init__(self, message: str, attempts: list[dict]):
        super().__init__(message)
        self.attempts = attempts


class EnhancedLLMClient:
    """Enhanced LLM client with health tracking and automatic failover."""

    # Provider priority order — only working providers included.
    # Tested 2026-03-11: DeepInfra ✅, Mistral ✅, NVIDIA ✅ — all others 401/404/429/503.
    # Dead providers commented out to avoid ~20s wasted per LLM call.
    PROVIDER_PRIORITY = [
        "deepinfra",  # ✅ 200 OK — cheapest working provider
        "mistral",  # ✅ 200 OK
        "nvidia",  # ✅ 200 OK
        # --- broken as of 2026-03-11 (re-enable when keys/endpoints fixed) ---
        # "groq",       # 401 Unauthorized
        # "cerebras",   # 404 Not Found (wrong model?)
        # "kimi",       # 401 Unauthorized
        # "fireworks",  # 503 Service Unavailable
        # "siliconflow",# 401 Unauthorized
        # "alibaba",    # 404 Not Found (wrong base_url)
        # "gemini",     # 404 Not Found (wrong base_url)
        # "openai",     # 429 Too Many Requests
        # "anthropic",  # 401 (not OpenAI-compatible)
    ]

    def __init__(self, health_checker: ProviderHealthChecker | None = None):
        """Initialize enhanced LLM client."""
        self.settings = get_settings()
        self.health_checker = health_checker or get_health_checker()
        self._clients: dict[str, Any] = {}

        # Initialize query handlers
        self.ollama_querier = OllamaQuerier(self.settings)
        self.cloud_querier = CloudProviderQuerier()

    def _get_client(self, provider: str) -> Any | None:
        """Get or create API client for provider."""
        from .provider_strategies import ProviderClientFactory

        if provider in self._clients:
            return self._clients[provider]

        client = ProviderClientFactory.create_client(provider, self.settings)
        if client is not None:
            self._clients[provider] = client

        return client

    def _get_model(self, provider: str) -> str:
        """Get the appropriate model for a provider."""
        models = {
            "ollama": self.settings.ollama_model,
            "openai": self.settings.openai_model,
            "groq": self.settings.groq_model,
            "fireworks": self.settings.fireworks_model,
            "mistral": self.settings.mistral_model,
            "deepinfra": self.settings.deepinfra_model,
            "gemini": self.settings.gemini_model,
            "nvidia": self.settings.nvidia_model,
            "cerebras": self.settings.cerebras_model,
            "kimi": self.settings.kimi_model,
            "anthropic": self.settings.anthropic_model,
            "siliconflow": self.settings.siliconflow_model,
            "alibaba": self.settings.alibaba_model,
        }
        return models.get(provider, "gpt-4o-mini")

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_retries: int = 2,
        preferred_provider: str | None = None,
    ) -> str:
        """Generate text using available LLM with automatic failover.

        Raises:
            RuntimeError: If all providers fail and no response can be generated.
        """
        await self.health_checker.check_all_providers()

        providers = self._get_provider_order(preferred_provider)
        attempts: list[dict] = []

        for provider in providers:
            if await self._try_provider(provider, prompt, system_prompt, max_retries, attempts):
                return attempts[-1].get("result")

        logger.error(f"All LLM providers failed after {len(attempts)} attempts")
        raise LLMGenerationError(
            f"All LLM providers exhausted ({len(attempts)} attempts); no response generated",
            attempts=attempts,
        )

    def _get_provider_order(self, preferred: str | None) -> list[str]:
        """Determine provider order based on preference."""
        if preferred:
            return [preferred] + [p for p in self.PROVIDER_PRIORITY if p != preferred]
        return self.PROVIDER_PRIORITY.copy()

    async def _try_provider(
        self,
        provider: str,
        prompt: str,
        system_prompt: str | None,
        max_retries: int,
        attempts: list[dict],
    ) -> bool:
        """Try to generate with a provider, handling retries."""
        health = self.health_checker.get_health(provider)
        if health and not health.is_available:
            return False

        for attempt in range(max_retries + 1):
            try:
                result = await self._query_provider(provider, prompt, system_prompt)
                self.health_checker.report_success(provider)
                attempts.append({"provider": provider, "attempt": attempt + 1, "result": result})
                return True

            except Exception as e:
                error = self.health_checker.report_error(provider, e)
                attempts.append(
                    {
                        "provider": provider,
                        "attempt": attempt + 1,
                        "error": str(e),
                        "error_type": error.last_error.value if error.last_error else "unknown",
                    }
                )

                if not await self._should_retry(provider, error, attempt, max_retries):
                    break

        return False

    async def _query_provider(
        self,
        provider: str,
        prompt: str,
        system_prompt: str | None,
    ) -> Any:
        """Query a specific provider."""
        if provider == "ollama":
            # Ollama removed from this deployment — skip to next provider
            raise Exception("Ollama is not available (removed from VPS)")

        client = self._get_client(provider)
        if not client:
            raise Exception(f"No client available for {provider}")

        model = self._get_model(provider)
        return await self.cloud_querier.query(client, provider, model, prompt, system_prompt)

    async def _should_retry(
        self,
        provider: str,
        error: Any,
        attempt: int,
        max_retries: int,
    ) -> bool:
        """Determine if we should retry the provider."""
        if not self.health_checker.should_retry(provider):
            return False

        if error.last_error == ProviderErrorType.QUOTA_EXHAUSTED:
            return False

        if error.last_error == ProviderErrorType.AUTHENTICATION:
            return False

        if error.last_error == ProviderErrorType.RATE_LIMIT:
            delay = self.health_checker.get_retry_delay(provider)
            await asyncio.sleep(delay)
            return True

        if attempt < max_retries:
            await asyncio.sleep(1.0 * (attempt + 1))
            return True

        return False

    async def generate_structured(
        self,
        prompt: str,
        schema: type[TBaseModel],
        system_prompt: str | None = None,
        max_retries: int = 2,
        preferred_provider: str | None = None,
    ) -> TBaseModel | None:
        """Generate structured output using Pydantic schema."""
        json_prompt = f"{prompt}\n\nIMPORTANT: Respond ONLY with valid JSON matching this schema"

        result = await self.generate(
            prompt=json_prompt,
            system_prompt=system_prompt,
            max_retries=max_retries,
            preferred_provider=preferred_provider,
        )

        if result is None:
            return None

        return self._parse_structured_result(result, schema)

    def _parse_structured_result(
        self,
        result: str | BaseModel,
        schema: type[TBaseModel],
    ) -> TBaseModel | None:
        """Parse structured result into schema."""
        try:
            if isinstance(result, str):
                return self._parse_json_string(result, schema)
            elif isinstance(result, BaseModel):
                return schema.model_validate(result.model_dump())
            else:
                return schema.model_validate(result)
        except Exception as e:
            logger.warning(f"Failed to parse structured output: {e}")
            return None

    def _parse_json_string(
        self,
        text: str,
        schema: type[TBaseModel],
    ) -> TBaseModel:
        """Parse JSON string, handling markdown code blocks."""
        if "```json" in text:
            text = text.split("```json")[-1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[-2].strip()
        return schema.model_validate_json(text)

    async def check_all_providers(self) -> dict[str, Any]:
        """Check health of all providers and return status report."""
        health = await self.health_checker.check_all_providers()

        return {
            "checked_at": asyncio.get_event_loop().time(),
            "providers": {
                name: {
                    "status": h.status.value,
                    "available": h.is_available,
                    "last_error": h.last_error.value if h.last_error else None,
                }
                for name, h in health.items()
            },
        }


def get_enhanced_llm_client(
    health_checker: ProviderHealthChecker | None = None,
) -> EnhancedLLMClient:
    return EnhancedLLMClient(health_checker=health_checker)
