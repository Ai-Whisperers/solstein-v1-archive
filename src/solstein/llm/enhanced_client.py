"""Enhanced LLM client — thin wrapper over SDK-backed queriers.

STORY-071: Refactored from 284→96 lines. Retry/failover in failover.py,
JSON parsing in json_parsing.py. Anthropic uses native AsyncAnthropic SDK.
STORY-073: Added Langfuse tracing via LLMTracer.
"""
from __future__ import annotations

import time
from typing import Any, TypeVar

from loguru import logger
from pydantic import BaseModel

from ..config import get_settings
from .failover import try_provider
from .health_checker import ProviderHealthChecker, get_health_checker
from .json_parsing import parse_structured_result
from .query import AnthropicQuerier, CloudProviderQuerier
from .tracing import TraceRecord, get_tracer

TBaseModel = TypeVar("TBaseModel", bound=BaseModel)
PROVIDER_PRIORITY = ["deepinfra", "mistral", "nvidia"]


class LLMGenerationError(Exception):
    """Raised when all LLM providers fail."""
    def __init__(self, message: str, attempts: list[dict[str, Any]]):
        super().__init__(message)
        self.attempts = attempts


class EnhancedLLMClient:
    """LLM client with health tracking and automatic failover."""
    def __init__(self, health_checker: ProviderHealthChecker | None = None):
        self.settings = get_settings()
        self.health_checker = health_checker or get_health_checker()
        self._clients: dict[str, Any] = {}
        self.cloud_querier = CloudProviderQuerier()
        self.anthropic_querier = AnthropicQuerier()

    def _get_client(self, provider: str) -> Any | None:
        from .provider_strategies import ProviderClientFactory
        if provider in self._clients:
            return self._clients[provider]
        client = ProviderClientFactory.create_client(provider, self.settings)
        if client is not None:
            self._clients[provider] = client
        return client

    def _get_model(self, provider: str) -> str:
        return getattr(self.settings, f"{provider}_model", "gpt-4o-mini")

    async def generate(
        self, prompt: str, system_prompt: str | None = None,
        max_retries: int = 2, preferred_provider: str | None = None,
    ) -> str:
        """Generate text using available LLM with automatic failover."""
        await self.health_checker.check_all_providers()
        providers = self._get_provider_order(preferred_provider)
        attempts: list[dict[str, Any]] = []
        for provider in providers:
            result = await try_provider(
                provider, lambda p: self._query_provider(p, prompt, system_prompt),
                self.health_checker, max_retries, attempts,
            )
            if result is not None:
                return result
        logger.error(f"All LLM providers failed after {len(attempts)} attempts")
        raise LLMGenerationError(
            f"All LLM providers exhausted ({len(attempts)} attempts)", attempts=attempts)

    async def generate_structured(
        self, prompt: str, schema: type[TBaseModel],
        system_prompt: str | None = None, max_retries: int = 2,
        preferred_provider: str | None = None,
    ) -> TBaseModel | None:
        """Generate structured output using Pydantic schema."""
        json_prompt = f"{prompt}\n\nIMPORTANT: Respond ONLY with valid JSON matching this schema"
        result = await self.generate(json_prompt, system_prompt, max_retries, preferred_provider)
        return parse_structured_result(result, schema) if result else None

    def _get_provider_order(self, preferred: str | None) -> list[str]:
        if preferred:
            return [preferred] + [p for p in PROVIDER_PRIORITY if p != preferred]
        return PROVIDER_PRIORITY.copy()

    async def _query_provider(self, provider: str, prompt: str, system_prompt: str | None) -> Any:
        """Query a provider and emit a Langfuse trace (STORY-073)."""
        client = self._get_client(provider)
        if not client:
            raise RuntimeError(f"No client available for {provider}")
        model = self._get_model(provider)
        start = time.monotonic()
        try:
            if provider == "anthropic":
                result = await self.anthropic_querier.query(client, model, prompt, system_prompt)
            else:
                result = await self.cloud_querier.query(client, provider, model, prompt, system_prompt)
            elapsed = time.monotonic() - start
            get_tracer(self.settings).record(TraceRecord(
                prompt=prompt[:500], provider=provider, model=model,
                latency_s=elapsed, success=True,
            ))
            return result
        except Exception as exc:
            elapsed = time.monotonic() - start
            get_tracer(self.settings).record(TraceRecord(
                prompt=prompt[:500], provider=provider, model=model,
                latency_s=elapsed, success=False, error=str(exc),
            ))
            raise

    async def check_all_providers(self) -> dict[str, Any]:
        health = await self.health_checker.check_all_providers()
        return {"providers": {n: {"status": h.status.value, "available": h.is_available} for n, h in health.items()}}


def get_enhanced_llm_client(health_checker: ProviderHealthChecker | None = None) -> EnhancedLLMClient:
    return EnhancedLLMClient(health_checker=health_checker)
