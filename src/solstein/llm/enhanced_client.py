"""Enhanced LLM client with health checking, smart retries, and provider rotation.

This module provides an enhanced LLM client that:
- Tracks provider health status
- Handles rate limits with exponential backoff
- Automatically rotates providers on failures
- Provides detailed error classification

Usage:
    from ..llm.enhanced_client import EnhancedLLMClient

    client = EnhancedLLMClient()
    result = await client.generate(prompt, system_prompt)
    # Automatically handles retries and provider rotation
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, TypeVar

from loguru import logger
from pydantic import BaseModel


import asyncio
from typing import Any, TypeVar

from loguru import logger
from pydantic import BaseModel

from ..config import get_settings
from .health_checker import (
    ProviderError,
    ProviderErrorType,
    ProviderHealthChecker,
    get_health_checker,
)

TBaseModel = TypeVar("TBaseModel", bound=BaseModel)


class LLMGenerationError(Exception):
    """Raised when all LLM providers fail."""

    def __init__(self, message: str, attempts: list[dict]):
        super().__init__(message)
        self.attempts = attempts


class EnhancedLLMClient:
    """Enhanced LLM client with health tracking and automatic failover.

    Features:
    - Proactive health checking before requests
    - Smart retry with exponential backoff for rate limits
    - Automatic provider rotation on failures
    - Detailed error classification and logging
    - Fallback to alternative providers

    Example:
        >>> client = EnhancedLLMClient()
        >>> result = await client.generate("Summarize this data")
        >>> print(result)
        "The data shows..."

        # If OpenAI fails, automatically tries Groq, then Fireworks
    """

    def __init__(self, health_checker: ProviderHealthChecker | None = None):
        """Initialize enhanced LLM client.

        Args:
            health_checker: Optional health checker instance.
                          Uses global instance if not provided.
        """
        self.settings = get_settings()
        self.health_checker = health_checker or get_health_checker()
        self._clients: dict[str, Any] = {}

    def _get_client(self, provider: str) -> Any | None:
        """Get or create API client for provider."""
        if provider in self._clients:
            return self._clients[provider]

        try:
            if provider == "openai":
                from openai import AsyncOpenAI

                if not self.settings.openai_api_key:
                    logger.debug("openai provider skipped: API key not configured")
                    return None
                client = AsyncOpenAI(api_key=self.settings.openai_api_key)
                self._clients[provider] = client
                return client

            if provider == "groq":
                import importlib

                if not self.settings.groq_api_key:
                    logger.debug("groq provider skipped: API key not configured")
                    return None
                groq_mod = importlib.import_module("groq")
                client = groq_mod.AsyncGroq(api_key=self.settings.groq_api_key)
                self._clients[provider] = client
                return client

            if provider == "fireworks":
                from openai import AsyncOpenAI

                if not self.settings.fireworks_api_key:
                    logger.debug("fireworks provider skipped: API key not configured")
                    return None
                client = AsyncOpenAI(
                    api_key=self.settings.fireworks_api_key,
                    base_url="https://api.fireworks.ai/inference/v1",
                )
                self._clients[provider] = client
                return client

            if provider == "mistral":
                from openai import AsyncOpenAI

                if not self.settings.mistral_api_key:
                    logger.debug("mistral provider skipped: API key not configured")
                    return None
                client = AsyncOpenAI(
                    api_key=self.settings.mistral_api_key,
                    base_url="https://api.mistral.ai/v1",
                )
                self._clients[provider] = client
                return client

            if provider == "deepinfra":
                from openai import AsyncOpenAI

                if not self.settings.deepinfra_api_key:
                    logger.debug("deepinfra provider skipped: API key not configured")
                    return None
                client = AsyncOpenAI(
                    api_key=self.settings.deepinfra_api_key,
                    base_url="https://api.deepinfra.com/v1/openai",
                )
                self._clients[provider] = client
                return client

            if provider == "gemini":
                from openai import AsyncOpenAI

                if not self.settings.gemini_api_key:
                    logger.debug("gemini provider skipped: API key not configured")
                    return None
                # Note: Gemini uses a different format, but we'll use the OpenAI compatibility layer
                client = AsyncOpenAI(
                    api_key=self.settings.gemini_api_key,
                    base_url="https://generativelanguage.googleapis.com/v1beta/openai",
                )
                self._clients[provider] = client
                return client

            if provider == "nvidia":
                from openai import AsyncOpenAI

                if not self.settings.nvidia_nim_api_key:
                    logger.debug("nvidia provider skipped: API key not configured")
                    return None
                client = AsyncOpenAI(
                    api_key=self.settings.nvidia_nim_api_key,
                    base_url="https://integrate.api.nvidia.com/v1",
                )
                self._clients[provider] = client
                return client

            if provider == "cerebras":
                from openai import AsyncOpenAI

                if not self.settings.cerebras_api_key:
                    logger.debug("cerebras provider skipped: API key not configured")
                    return None
                client = AsyncOpenAI(
                    api_key=self.settings.cerebras_api_key,
                    base_url="https://api.cerebras.ai/v1",
                )
                self._clients[provider] = client
                return client

            if provider == "kimi":
                from openai import AsyncOpenAI

                if not self.settings.kimi_api_key:
                    logger.debug("kimi provider skipped: API key not configured")
                    return None
                client = AsyncOpenAI(
                    api_key=self.settings.kimi_api_key,
                    base_url="https://api.moonshot.cn/v1",
                )
                self._clients[provider] = client
                return client

            if provider == "anthropic":
                from openai import AsyncOpenAI

                if not self.settings.anthropic_api_key:
                    logger.debug("anthropic provider skipped: API key not configured")
                    return None
                client = AsyncOpenAI(
                    api_key=self.settings.anthropic_api_key,
                    base_url="https://api.anthropic.com/v1",
                    default_headers={"anthropic-version": "2023-06-01"},
                )
                self._clients[provider] = client
                return client

            if provider == "siliconflow":
                from openai import AsyncOpenAI

                if not self.settings.siliconflow_api_key:
                    logger.debug("siliconflow provider skipped: API key not configured")
                    return None
                client = AsyncOpenAI(
                    api_key=self.settings.siliconflow_api_key,
                    base_url="https://api.siliconflow.cn/v1",
                )
                self._clients[provider] = client
                return client

            if provider == "alibaba":
                from openai import AsyncOpenAI

                if not self.settings.alibaba_api_key:
                    logger.debug("alibaba provider skipped: API key not configured")
                    return None
                client = AsyncOpenAI(
                    api_key=self.settings.alibaba_api_key,
                    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                )
                self._clients[provider] = client
                return client

        except Exception as e:
            logger.warning(f"Failed to initialize {provider} client: {e}")
            return None

        return None

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
        return models.get(provider, "gpt-4o-mini")  # Default fallback

    async def _query_ollama(
        self,
        prompt: str,
        system_prompt: str | None = None,
        schema: type[BaseModel] | None = None,
    ) -> Any | None:
        """Query Ollama (local) instance."""
        import aiohttp

        system = (
            system_prompt
            or "You are an expert business analyst specializing in technology companies and private equity. Provide concise, data-driven insights."
        )

        payload = {
            "model": self.settings.ollama_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "options": {"temperature": 0.3},
        }

        if schema:
            payload["format"] = schema.model_json_schema()

        try:
            async with (
                aiohttp.ClientSession() as session,
                session.post(
                    f"{self.settings.ollama_url}/api/chat",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60),
                ) as response,
            ):
                if response.status == 200:
                    data = await response.json()
                    content = data.get("message", {}).get("content", "")

                    if schema:
                        try:
                            if "```json" in content:
                                content = content.split("```json")[-1].split("```")[0].strip()
                            return schema.model_validate_json(content)
                        except Exception as e:
                            logger.warning(f"Ollama schema validation failed: {e}")
                            return None

                    return content
                else:
                    raise Exception(f"Ollama returned {response.status}")
        except asyncio.TimeoutError:
            raise Exception("Ollama request timeout")
        except Exception:
            raise

    async def _query_cloud_provider(
        self,
        provider: str,
        prompt: str,
        system_prompt: str | None = None,
        schema: type[BaseModel] | None = None,
    ) -> Any:
        """Query a cloud LLM provider."""
        client = self._get_client(provider)
        if not client:
            raise Exception(f"No client available for {provider}")

        model = self._get_model(provider)

        system = (
            system_prompt
            or "You are an expert business analyst specializing in technology companies and private equity. Provide concise, data-driven insights."
        )

        def _clean_json(text: str) -> str:
            if "```json" in text:
                return text.split("```json")[-1].split("```")[0].strip()
            if "```" in text:
                return text.split("```")[-2].strip()
            return text.strip()

        # Check if we can use structured output (OpenAI only)
        use_parse = (
            schema is not None
            and provider == "openai"
            and hasattr(client, "beta")
            and hasattr(client.beta, "chat")
            and hasattr(client.beta.chat.completions, "parse")
        )

        if use_parse:
            response = await client.beta.chat.completions.parse(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=2000,
                response_format=schema,
            )
            return response.choices[0].message.parsed

        # Standard chat completion
        create_kwargs: dict[str, Any] = {}
        if schema and provider in {"openai", "fireworks"}:
            create_kwargs["response_format"] = {"type": "json_object"}

        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=2000,
            **create_kwargs,
        )

        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("Empty response content")

        if schema:
            return schema.model_validate_json(_clean_json(content))

        return content

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_retries: int = 2,
        preferred_provider: str | None = None,
    ) -> str | None:
        """Generate text using available LLM with automatic failover.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            max_retries: Max retries per provider before switching
            preferred_provider: Preferred provider to try first

        Returns:
            Generated text or None if all providers fail
        """
        # Ensure health checker has current status
        await self.health_checker.check_all_providers()

        # Determine provider order
        if preferred_provider:
            providers = [preferred_provider]
            # Add other available providers as fallbacks
            for p in self.health_checker.PROVIDER_PRIORITY:
                if p != preferred_provider:
                    providers.append(p)
        else:
            providers = self.health_checker.PROVIDER_PRIORITY.copy()

        attempts: list[dict] = []
        used_providers: list[str] = []

        for provider in providers:
            # Skip if we've already tried this provider
            if provider in used_providers:
                continue

            used_providers.append(provider)

            # Check if provider is available
            health = self.health_checker.get_health(provider)
            if health and not health.is_available:
                logger.debug(f"Skipping {provider}: {health.status}")
                continue

            # Try the provider with retries
            for attempt in range(max_retries + 1):
                try:
                    if provider == "ollama":
                        result = await self._query_ollama(prompt, system_prompt)
                    else:
                        result = await self._query_cloud_provider(provider, prompt, system_prompt)

                    # Success! Update health and return
                    self.health_checker.report_success(provider)
                    logger.debug(f"Successfully generated using {provider}")
                    return result

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

                    # Check if we should retry this provider
                    if not self.health_checker.should_retry(provider):
                        logger.warning(f"Not retrying {provider}: too many failures")
                        break

                    # Check error type for special handling
                    if error.last_error == ProviderErrorType.QUOTA_EXHAUSTED:
                        logger.error(f"{provider} quota exhausted, switching provider")
                        break  # Don't retry, move to next provider

                    if error.last_error == ProviderErrorType.AUTHENTICATION:
                        logger.error(f"{provider} authentication failed, switching provider")
                        break  # Don't retry, move to next provider

                    # Rate limited - wait and retry
                    if error.last_error == ProviderErrorType.RATE_LIMIT:
                        delay = self.health_checker.get_retry_delay(provider)
                        logger.warning(f"{provider} rate limited, waiting {delay}s")
                        await asyncio.sleep(delay)
                        continue

                    # Other errors - brief delay then retry
                    if attempt < max_retries:
                        delay = 1.0 * (attempt + 1)
                        logger.warning(f"{provider} failed (attempt {attempt + 1}), retrying in {delay}s: {e}")
                        await asyncio.sleep(delay)

        # All providers exhausted
        logger.error(f"All LLM providers failed after {len(attempts)} attempts")
        return None

    async def generate_structured(
        self,
        prompt: str,
        schema: type[TBaseModel],
        system_prompt: str | None = None,
        max_retries: int = 2,
        preferred_provider: str | None = None,
    ) -> TBaseModel | None:
        """Generate structured output using Pydantic schema.

        Args:
            prompt: The user prompt
            schema: Pydantic model class for structured output
            system_prompt: Optional system prompt
            max_retries: Max retries per provider
            preferred_provider: Preferred provider to try first

        Returns:
            Parsed Pydantic model or None if all providers fail
        """
        json_prompt = (
            f"{prompt}\n\nIMPORTANT: Respond ONLY with valid JSON matching this schema: {schema.model_json_schema()}"
        )

        result = await self.generate(
            prompt=json_prompt,
            system_prompt=system_prompt,
            max_retries=max_retries,
            preferred_provider=preferred_provider,
        )

        if result is None:
            return None

        try:
            # Try to parse as the schema
            if isinstance(result, str):
                # Clean up markdown code blocks if present
                if "```json" in result:
                    result = result.split("```json")[-1].split("```")[0].strip()
                elif "```" in result:
                    result = result.split("```")[-2].strip()
                return schema.model_validate_json(result)
            elif isinstance(result, BaseModel):
                return result
            else:
                return schema.model_validate(result)
        except Exception as e:
            logger.warning(f"Failed to parse structured output: {e}")
            return None

    async def check_all_providers(self) -> dict[str, Any]:
        """Check health of all providers and return status report."""
        health = await self.health_checker.check_all_providers()

        return {
            "checked_at": asyncio.get_event_loop().time(),
            "providers": {
                name: {
                    "status": h.status.value,
                    "is_available": h.is_available,
                    "last_error": h.last_error.value if h.last_error else None,
                    "consecutive_failures": h.consecutive_failures,
                    "total_successes": h.total_successes,
                    "total_failures": h.total_failures,
                }
                for name, h in health.items()
            },
            "available": self.health_checker.get_available_providers(),
            "best_provider": self.health_checker.get_best_provider(),
        }

    def get_health_status(self) -> dict[str, Any]:
        """Get current health status without making new checks."""
        health = self.health_checker.get_all_health()

        return {
            "providers": {
                name: {
                    "status": h.status.value,
                    "is_available": h.is_available,
                    "last_error": h.last_error.value if h.last_error else None,
                }
                for name, h in health.items()
            },
            "available": self.health_checker.get_available_providers(),
        }


# Global enhanced client instance
_enhanced_client: EnhancedLLMClient | None = None


def get_enhanced_llm_client() -> EnhancedLLMClient:
    """Get the global enhanced LLM client."""
    global _enhanced_client
    if _enhanced_client is None:
        _enhanced_client = EnhancedLLMClient()
    return _enhanced_client



# Cost tracking per model (USD per 1K tokens)
MODEL_COSTS = {
    # OpenAI
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    # Groq
    "llama-3.3-70b-versatile": {"input": 0.00059, "output": 0.00079},
    # Fireworks
    "qwen2-72b-instruct": {"input": 0.0009, "output": 0.0009},
    # Ollama (local - free)
    "llama3.2:latest": {"input": 0.0, "output": 0.0},
    # Anthropic
    "claude-3-5-haiku-20241022": {"input": 0.0008, "output": 0.004},
    "claude-sonnet-4-5": {"input": 0.003, "output": 0.015},
    "claude-opus-4-5": {"input": 0.015, "output": 0.075},
    # SiliconFlow (approximate)
    "Qwen/Qwen2.5-72B-Instruct": {"input": 0.0004, "output": 0.0004},
    # Alibaba DashScope (approximate)
    "qwen-plus": {"input": 0.0004, "output": 0.0012},
}


