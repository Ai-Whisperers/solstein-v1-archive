"""LLM API optimizations for EPIC-023 Story 7.

Features:
- Request batching
- Prompt caching
- Model tiering
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from typing import Any

from loguru import logger


@dataclass
class LLMRequest:
    """LLM request for batching."""

    prompt: str
    system_prompt: str | None = None
    model: str | None = None
    temperature: float = 0.3
    max_tokens: int = 2000


class LLMBatcher:
    """Batch multiple LLM requests together."""

    def __init__(self, max_batch_size: int = 5, max_wait_time: float = 0.1):
        self.max_batch_size = max_batch_size
        self.max_wait_time = max_wait_time
        self._pending: list[tuple[LLMRequest, Any]] = []  # request, future
        self._last_flush = time.time()

    async def submit(self, request: LLMRequest) -> Any:
        """Submit request to batch."""
        import asyncio

        future = asyncio.get_event_loop().create_future()
        self._pending.append((request, future))

        # Check if we should flush
        if len(self._pending) >= self.max_batch_size or time.time() - self._last_flush > self.max_wait_time:
            await self._flush()

        return await future

    async def _flush(self) -> None:
        """Process pending requests."""
        if not self._pending:
            return

        batch = self._pending[: self.max_batch_size]
        self._pending = self._pending[self.max_batch_size :]
        self._last_flush = time.time()

        # Process batch
        for request, future in batch:
            # Single request for now
            # In production, would batch to provider API
            if not future.done():
                future.set_result(await self._execute(request))

    async def _execute(self, request: LLMRequest) -> str:
        """Execute single request."""
        # Placeholder - actual implementation in enhanced_client
        return ""


class PromptCache:
    """Cache LLM prompts and responses."""

    def __init__(self, ttl: int = 3600):
        self.ttl = ttl
        self._cache: dict[str, tuple[str, float]] = {}  # hash -> (response, timestamp)

    def _hash(self, prompt: str, model: str) -> str:
        """Create hash key for prompt."""
        key = f"{model}:{prompt}"
        return hashlib.sha256(key.encode()).hexdigest()[:16]

    async def get(self, prompt: str, model: str) -> str | None:
        """Get cached response."""
        key = self._hash(prompt, model)
        if key in self._cache:
            response, timestamp = self._cache[key]
            if time.time() - timestamp < self.ttl:
                logger.debug(f"Prompt cache hit for {key[:8]}...")
                return response
            else:
                del self._cache[key]
        return None

    async def set(self, prompt: str, model: str, response: str) -> None:
        """Cache response."""
        key = self._hash(prompt, model)
        self._cache[key] = (response, time.time())
        logger.debug(f"Prompt cached for {key[:8]}...")

    def clear(self) -> None:
        """Clear cache."""
        self._cache.clear()


class ModelTier:
    """Model tiering for cost/quality optimization."""

    TIERS = {
        "fast": ["groq", "fireworks", "ollama"],  # Fast, cheap models
        "balanced": ["openai", "anthropic", "mistral"],  # Balance speed/quality
        "quality": ["anthropic", "openai", "gemini"],  # Best quality
    }

    @classmethod
    def get_models(cls, tier: str) -> list[str]:
        """Get models for tier."""
        return cls.TIERS.get(tier, cls.TIERS["balanced"])


__all__ = ["LLMBatcher", "LLMRequest", "PromptCache", "ModelTier"]
