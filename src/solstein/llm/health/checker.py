"""Main health checker for LLM providers."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from loguru import logger

from solstein.config import get_settings

from .clients import ProviderClientManager
from .errors import ErrorClassifier
from .models import ProviderError, ProviderErrorType, ProviderHealth, ProviderStatus


class HealthChecker:
    """Checks health of LLM providers."""

    def __init__(self):
        self.client_manager = ProviderClientManager()
        self.error_classifier = ErrorClassifier()
        self._health_cache: dict[str, ProviderHealth] = {}

    async def check_provider(self, provider: str) -> ProviderHealth:
        """Check a single provider's health."""
        if provider == "ollama":
            return await self._check_ollama()

        client = self.client_manager.get_client(provider)
        if not client:
            return self._unhealthy(provider, ProviderErrorType.AUTHENTICATION, "No API key")

        settings = get_settings()
        model = self.client_manager.get_model_for_provider(provider, settings)

        return await self._make_test_call(client, model, provider)

    async def _check_ollama(self) -> ProviderHealth:
        """Check Ollama local instance."""
        try:
            from ollama import Client as OllamaClient

            settings = get_settings()
            client = OllamaClient(host=settings.ollama_url or "http://localhost:11434")
            client.list()

            return ProviderHealth(
                provider="ollama",
                status=ProviderStatus.HEALTHY,
                last_checked=datetime.now(timezone.utc),
            )
        except Exception as e:
            return self._unhealthy("ollama", ProviderErrorType.NETWORK_ERROR, str(e))

    async def _make_test_call(self, client: Any, model: str, provider: str) -> ProviderHealth:
        """Make a minimal test call to check provider."""
        try:
            if hasattr(client, "chat") and hasattr(client.chat, "completions"):
                await client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": "hi"}],
                    max_tokens=1,
                    temperature=0,
                )
                return self._healthy(provider)
            else:
                return self._healthy(provider)  # Assume healthy if no chat interface
        except Exception as e:
            error = self.error_classifier.classify(e, provider)
            return self._unhealthy_from_error(provider, error)

    async def check_all_providers(self) -> dict[str, ProviderHealth]:
        """Check all configured providers."""
        providers = [
            "ollama",
            "openai",
            "anthropic",
            "groq",
            "fireworks",
            "mistral",
            "deepinfra",
            "gemini",
            "nvidia",
            "cerebras",
            "kimi",
            "siliconflow",
            "alibaba",
        ]

        results = {}
        for provider in providers:
            results[provider] = await self.check_provider(provider)

        return results

    def _healthy(self, provider: str) -> ProviderHealth:
        """Create healthy status."""
        return ProviderHealth(
            provider=provider,
            status=ProviderStatus.HEALTHY,
            last_checked=datetime.now(timezone.utc),
        )

    def _unhealthy(self, provider: str, error_type: ProviderErrorType, message: str) -> ProviderHealth:
        """Create unhealthy status."""
        return ProviderHealth(
            provider=provider,
            status=ProviderStatus.UNHEALTHY,
            last_error=error_type,
            error_message=message,
            last_checked=datetime.now(timezone.utc),
        )

    def _unhealthy_from_error(self, provider: str, error: ProviderError) -> ProviderHealth:
        """Create unhealthy status from error."""
        status = ProviderStatus.UNHEALTHY
        if error.error_type == ProviderErrorType.RATE_LIMIT:
            status = ProviderStatus.RATE_LIMITED

        return ProviderHealth(
            provider=provider,
            status=status,
            last_error=error.error_type,
            error_message=error.message,
            last_checked=datetime.now(timezone.utc),
        )

    def get_cached_health(self, provider: str) -> ProviderHealth | None:
        """Get cached health status."""
        return self._health_cache.get(provider)

    def cache_health(self, provider: str, health: ProviderHealth) -> None:
        """Cache health status."""
        self._health_cache[provider] = health
