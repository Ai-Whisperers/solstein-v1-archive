"""Provider client management for health checking."""

from __future__ import annotations

from typing import Any

from solstein.config import get_settings


class ProviderClientManager:
    """Manages LLM provider clients for health checking."""

    # Provider configurations
    PROVIDER_URLS = {
        "ollama": "http://localhost:11434",
        "openai": "https://api.openai.com/v1",
        "anthropic": "https://api.anthropic.com/v1",
        "groq": "https://api.groq.com/openai/v1",
        "fireworks": "https://api.fireworks.ai/inference/v1",
        "mistral": "https://api.mistral.ai/v1",
        "deepinfra": "https://api.deepinfra.com/v1/openai",
        "gemini": "https://generativelanguage.googleapis.com/v1",
        "nvidia": "https://integrate.api.nvidia.com/v1",
        "cerebras": "https://api.cerebras.ai/v1",
        "kimi": "https://api.moonshot.cn/v1",
        "siliconflow": "https://api.siliconflow.cn/v1",
        "alibaba": "https://dashscope.aliyuncs.com/api/v1",
    }

    def __init__(self):
        self._clients: dict[str, Any] = {}
        self._settings = None

    def _get_settings(self):
        """Lazy load settings."""
        if self._settings is None:
            self._settings = get_settings()
        return self._settings

    def get_client(self, provider: str) -> Any | None:
        """Get or create client for provider."""
        if provider in self._clients:
            return self._clients[provider]

        client = self._create_client(provider)
        if client:
            self._clients[provider] = client
        return client

    def _create_client(self, provider: str) -> Any | None:
        """Create client for provider."""
        settings = self._get_settings()

        # Get API key
        api_key = self._get_api_key(provider, settings)
        if not api_key and provider != "ollama":
            return None

        # Create client based on provider type
        if provider == "ollama":
            return self._create_ollama_client(settings)

        return self._create_openai_compatible_client(provider, api_key, settings)

    def _get_api_key(self, provider: str, settings: Any) -> str | None:
        """Get API key for provider."""
        key_map = {
            "openai": settings.openai_api_key,
            "anthropic": settings.anthropic_api_key,
            "groq": settings.groq_api_key,
            "fireworks": settings.fireworks_api_key,
            "mistral": settings.mistral_api_key,
            "deepinfra": settings.deepinfra_api_key,
            "gemini": settings.gemini_api_key,
            "nvidia": settings.nvidia_api_key,
            "cerebras": settings.cerebras_api_key,
            "kimi": settings.kimi_api_key,
            "siliconflow": settings.siliconflow_api_key,
            "alibaba": settings.alibaba_api_key,
        }
        return key_map.get(provider)

    def _create_ollama_client(self, settings: Any) -> Any | None:
        """Create Ollama client."""
        try:
            from ollama import Client as OllamaClient

            return OllamaClient(host=settings.ollama_url or "http://localhost:11434")
        except ImportError:
            return None

    def _create_openai_compatible_client(self, provider: str, api_key: str, settings: Any) -> Any | None:
        """Create OpenAI-compatible client."""
        try:
            from openai import AsyncOpenAI

            base_url = self.PROVIDER_URLS.get(provider)
            if not base_url:
                return None

            return AsyncOpenAI(api_key=api_key, base_url=base_url)
        except ImportError:
            return None

    def get_model_for_provider(self, provider: str, settings: Any) -> str:
        """Get the appropriate model for a provider."""
        model_map = {
            "fireworks": settings.fireworks_model,
            "openai": settings.openai_model,
            "groq": settings.groq_model,
            "mistral": settings.mistral_model,
            "deepinfra": settings.deepinfra_model,
            "gemini": settings.gemini_model,
            "nvidia": settings.nvidia_model,
            "cerebras": settings.cerebras_model,
            "kimi": settings.kimi_model,
            "anthropic": settings.anthropic_model,
            "siliconflow": settings.siliconflow_model,
            "alibaba": settings.alibaba_model,
        }
        return model_map.get(provider, settings.groq_model)
