"""LLM provider client factory.

EPIC-020: Extracted from _get_client function in EnhancedLLMClient.
Uses Strategy pattern to create clients for different providers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from loguru import logger

if TYPE_CHECKING:
    from ..config import Settings


class ProviderClientStrategy(ABC):
    """Abstract base class for provider client strategies."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name."""
        pass

    @abstractmethod
    def create_client(self, settings: Settings) -> Any | None:
        """Create and return the API client for this provider."""
        pass

    def _check_api_key(self, settings: Settings, key_attr: str) -> str | None:
        """Check if API key is configured."""
        api_key = getattr(settings, key_attr, None)
        if not api_key:
            logger.debug(f"{self.provider_name} provider skipped: API key not configured")
            return None
        return api_key


class OpenAIProviderStrategy(ProviderClientStrategy):
    """OpenAI provider client strategy."""

    @property
    def provider_name(self) -> str:
        return "openai"

    def create_client(self, settings: Settings) -> Any | None:
        from openai import AsyncOpenAI

        api_key = self._check_api_key(settings, "openai_api_key")
        if not api_key:
            return None

        return AsyncOpenAI(api_key=api_key)


class GroqProviderStrategy(ProviderClientStrategy):
    """Groq provider client strategy."""

    @property
    def provider_name(self) -> str:
        return "groq"

    def create_client(self, settings: Settings) -> Any | None:
        import importlib

        api_key = self._check_api_key(settings, "groq_api_key")
        if not api_key:
            return None

        groq_mod = importlib.import_module("groq")
        return groq_mod.AsyncGroq(api_key=api_key)


class FireworksProviderStrategy(ProviderClientStrategy):
    """Fireworks provider client strategy."""

    @property
    def provider_name(self) -> str:
        return "fireworks"

    def create_client(self, settings: Settings) -> Any | None:
        from openai import AsyncOpenAI

        api_key = self._check_api_key(settings, "fireworks_api_key")
        if not api_key:
            return None

        return AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.fireworks.ai/inference/v1",
        )


class MistralProviderStrategy(ProviderClientStrategy):
    """Mistral provider client strategy."""

    @property
    def provider_name(self) -> str:
        return "mistral"

    def create_client(self, settings: Settings) -> Any | None:
        from openai import AsyncOpenAI

        api_key = self._check_api_key(settings, "mistral_api_key")
        if not api_key:
            return None

        return AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.mistral.ai/v1",
        )


class DeepInfraProviderStrategy(ProviderClientStrategy):
    """DeepInfra provider client strategy."""

    @property
    def provider_name(self) -> str:
        return "deepinfra"

    def create_client(self, settings: Settings) -> Any | None:
        from openai import AsyncOpenAI

        api_key = self._check_api_key(settings, "deepinfra_api_key")
        if not api_key:
            return None

        return AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.deepinfra.com/v1/openai",
        )


class GeminiProviderStrategy(ProviderClientStrategy):
    """Gemini provider client strategy."""

    @property
    def provider_name(self) -> str:
        return "gemini"

    def create_client(self, settings: Settings) -> Any | None:
        from openai import AsyncOpenAI

        api_key = self._check_api_key(settings, "gemini_api_key")
        if not api_key:
            return None

        return AsyncOpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai",
        )


class NvidiaProviderStrategy(ProviderClientStrategy):
    """NVIDIA provider client strategy."""

    @property
    def provider_name(self) -> str:
        return "nvidia"

    def create_client(self, settings: Settings) -> Any | None:
        from openai import AsyncOpenAI

        api_key = self._check_api_key(settings, "nvidia_nim_api_key")
        if not api_key:
            return None

        return AsyncOpenAI(
            api_key=api_key,
            base_url="https://integrate.api.nvidia.com/v1",
        )


class CerebrasProviderStrategy(ProviderClientStrategy):
    """Cerebras provider client strategy."""

    @property
    def provider_name(self) -> str:
        return "cerebras"

    def create_client(self, settings: Settings) -> Any | None:
        from openai import AsyncOpenAI

        api_key = self._check_api_key(settings, "cerebras_api_key")
        if not api_key:
            return None

        return AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.cerebras.ai/v1",
        )


class KimiProviderStrategy(ProviderClientStrategy):
    """Kimi (Moonshot) provider client strategy."""

    @property
    def provider_name(self) -> str:
        return "kimi"

    def create_client(self, settings: Settings) -> Any | None:
        from openai import AsyncOpenAI

        api_key = self._check_api_key(settings, "kimi_api_key")
        if not api_key:
            return None

        return AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.moonshot.cn/v1",
        )


class AnthropicProviderStrategy(ProviderClientStrategy):
    """Anthropic provider client strategy."""

    @property
    def provider_name(self) -> str:
        return "anthropic"

    def create_client(self, settings: Settings) -> Any | None:
        from openai import AsyncOpenAI

        api_key = self._check_api_key(settings, "anthropic_api_key")
        if not api_key:
            return None

        return AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.anthropic.com/v1",
            default_headers={"anthropic-version": "2023-06-01"},
        )


class SiliconFlowProviderStrategy(ProviderClientStrategy):
    """SiliconFlow provider client strategy."""

    @property
    def provider_name(self) -> str:
        return "siliconflow"

    def create_client(self, settings: Settings) -> Any | None:
        from openai import AsyncOpenAI

        api_key = self._check_api_key(settings, "siliconflow_api_key")
        if not api_key:
            return None

        return AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.siliconflow.cn/v1",
        )


class AlibabaProviderStrategy(ProviderClientStrategy):
    """Alibaba provider client strategy."""

    @property
    def provider_name(self) -> str:
        return "alibaba"

    def create_client(self, settings: Settings) -> Any | None:
        from openai import AsyncOpenAI

        api_key = self._check_api_key(settings, "alibaba_api_key")
        if not api_key:
            return None

        return AsyncOpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )


class ProviderClientFactory:
    """Factory for creating provider clients using Strategy pattern."""

    _strategies: dict[str, ProviderClientStrategy] = {}

    @classmethod
    def register(cls, strategy: ProviderClientStrategy) -> None:
        """Register a provider strategy."""
        cls._strategies[strategy.provider_name] = strategy

    @classmethod
    def create_client(cls, provider: str, settings: Settings) -> Any | None:
        """Create client for the given provider."""
        strategy = cls._strategies.get(provider)
        if strategy is None:
            logger.warning(f"Unknown provider: {provider}")
            return None

        try:
            return strategy.create_client(settings)
        except Exception as e:
            logger.warning(f"Failed to initialize {provider} client: {e}")
            return None

    @classmethod
    def initialize(cls) -> None:
        """Register all provider strategies."""
        if cls._strategies:
            return  # Already initialized

        cls.register(OpenAIProviderStrategy())
        cls.register(GroqProviderStrategy())
        cls.register(FireworksProviderStrategy())
        cls.register(MistralProviderStrategy())
        cls.register(DeepInfraProviderStrategy())
        cls.register(GeminiProviderStrategy())
        cls.register(NvidiaProviderStrategy())
        cls.register(CerebrasProviderStrategy())
        cls.register(KimiProviderStrategy())
        cls.register(AnthropicProviderStrategy())
        cls.register(SiliconFlowProviderStrategy())
        cls.register(AlibabaProviderStrategy())


# Initialize factory on module import
ProviderClientFactory.initialize()
