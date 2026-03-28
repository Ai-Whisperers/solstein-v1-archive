"""Enhanced LLM client — thin wrapper over SDK-backed queriers.

STORY-071: Refactored from 284→96 lines. Retry/failover in failover.py,
JSON parsing in json_parsing.py. Anthropic uses native AsyncAnthropic SDK.
STORY-073: Added Langfuse tracing via LLMTracer.
STORY-075: Integrated FallbackChain with circuit breakers and template fallback.
STORY-129: Classified exception handling with Prometheus metrics and health signals.
"""
from __future__ import annotations

import time
from typing import Any, TypeVar

from loguru import logger
from pydantic import BaseModel

from ..config import get_settings
from ..monitoring.metrics import LLM_ERRORS_TOTAL, LLM_REQUESTS_TOTAL
from .fallback import TEMPLATE_FALLBACK_RESPONSE, FallbackChain
from .health.errors import ErrorClassifier
from .health_checker import ProviderHealthChecker, get_health_checker
from .json_parsing import parse_structured_result
from .query import AnthropicQuerier, CloudProviderQuerier
from .tracing import TraceRecord, get_tracer

TBaseModel = TypeVar("TBaseModel", bound=BaseModel)


class LLMGenerationError(Exception):
    """Raised when all LLM providers fail and template fallback is disabled."""
    def __init__(self, message: str, attempts: list[dict[str, Any]]):
        super().__init__(message)
        self.attempts = attempts


class EnhancedLLMClient:
    """LLM client with health tracking, circuit breaking, and automatic failover.

    STORY-075: Provider order is configurable via settings.llm_provider_order.
    Circuit breakers prevent requests to known-failing providers.
    Template fallback returns structured placeholder when all providers fail.
    """
    def __init__(
        self,
        health_checker: ProviderHealthChecker | None = None,
        fallback_chain: FallbackChain | None = None,
    ):
        self.settings = get_settings()
        self.health_checker = health_checker or get_health_checker()
        self._fallback = fallback_chain or FallbackChain(self.settings)
        self._clients: dict[str, Any] = {}
        self._error_classifier = ErrorClassifier()
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
        use_template_fallback: bool = True,
    ) -> str:
        """Generate text using available LLM with automatic failover.

        STORY-075: Uses FallbackChain with circuit breakers. If all providers
        fail, returns template fallback content (or raises LLMGenerationError
        if use_template_fallback=False).
        """
        await self.health_checker.check_all_providers()
        fb_result = await self._fallback.execute(
            query_fn=lambda p: self._query_provider(p, prompt, system_prompt),
            preferred_provider=preferred_provider,
            max_retries=max_retries,
        )
        if fb_result.result is not None:
            return fb_result.result

        if fb_result.is_template_fallback and use_template_fallback:
            logger.warning("[EnhancedLLMClient] Returning template fallback response")
            return TEMPLATE_FALLBACK_RESPONSE["content"]

        attempts = [
            {"provider": d.provider, "action": d.action, "reason": d.reason}
            for d in fb_result.decisions
        ]
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

    async def _query_provider(self, provider: str, prompt: str, system_prompt: str | None) -> Any:
        """Query a provider with classified error handling (STORY-129).

        Exceptions are classified into ProviderErrorType categories, emitted
        as Prometheus metrics, reported to the health checker, and logged with
        structured fields before being re-raised for the FallbackChain.
        """
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

            # Record success traces and metrics
            get_tracer(self.settings).record(TraceRecord(
                prompt=prompt[:500], provider=provider, model=model,
                latency_s=elapsed, success=True,
            ))
            LLM_REQUESTS_TOTAL.labels(provider=provider, model=model, status="success").inc()
            self.health_checker.report_success(provider)
            return result

        except Exception as exc:
            elapsed = time.monotonic() - start
            classified = self._error_classifier.classify(exc, provider)

            # Structured logging with required fields per exception-handling.md
            logger.error(
                "[EnhancedLLMClient] Provider query failed",
                component="EnhancedLLMClient",
                operation="_query_provider",
                error_type=classified.error_type.value,
                message=str(exc),
                provider=provider,
                model=model,
                latency_s=f"{elapsed:.3f}",
                status_code=classified.status_code,
            )

            # Prometheus metrics — classified error counters
            LLM_REQUESTS_TOTAL.labels(provider=provider, model=model, status="error").inc()
            LLM_ERRORS_TOTAL.labels(provider=provider, error_type=classified.error_type.value).inc()

            # Signal health checker with explicit failure type
            self.health_checker.report_error(provider, exc)

            # Langfuse trace
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
