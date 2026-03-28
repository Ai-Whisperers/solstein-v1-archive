"""Cloud provider query handler for EnhancedLLMClient."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel

from solstein.llm.prompts import get_system_prompt


@dataclass
class CloudProviderContext:
    """Bundled cloud-provider context: client handle, provider name, and model."""

    client: Any
    provider: str
    model: str


class CloudProviderQuerier:
    """Handles queries to cloud LLM providers."""

    @staticmethod
    def make_ctx(client: Any, provider: str, model: str) -> CloudProviderContext:
        """Convenience factory for building a CloudProviderContext."""
        return CloudProviderContext(client=client, provider=provider, model=model)

    async def query(
        self,
        client: Any,
        provider: str,
        model: str,
        prompt: str,
        system_prompt: str | None = None,
    ) -> Any:
        """Query a cloud LLM provider (free-text output).

        For structured output use query_structured().
        """
        system = system_prompt or get_system_prompt("system_business_analyst")
        ctx = CloudProviderContext(client=client, provider=provider, model=model)
        return await self._query_standard(ctx, system, prompt, schema=None)

    async def query_structured(
        self,
        ctx: CloudProviderContext,
        prompt: str,
        schema: type[BaseModel],
        system_prompt: str | None = None,
    ) -> Any:
        """Query a cloud LLM provider with schema-validated structured output."""
        system = system_prompt or get_system_prompt("system_business_analyst")

        # Prefer OpenAI parse endpoint when available
        use_parse = (
            ctx.provider == "openai"
            and hasattr(ctx.client, "beta")
            and hasattr(ctx.client.beta, "chat")
            and hasattr(ctx.client.beta.chat.completions, "parse")
        )
        if use_parse:
            return await self._query_with_parse(ctx, system, prompt, schema)

        return await self._query_standard(ctx, system, prompt, schema=schema)

    async def _query_with_parse(
        self,
        ctx: CloudProviderContext,
        system: str,
        prompt: str,
        schema: type[BaseModel],
    ) -> BaseModel:
        """Query using OpenAI's parse method for structured output."""
        response = await ctx.client.beta.chat.completions.parse(
            model=ctx.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=2000,
            response_format=schema,
        )
        return response.choices[0].message.parsed

    async def _query_standard(
        self,
        ctx: CloudProviderContext,
        system: str,
        prompt: str,
        schema: type[BaseModel] | None,
    ) -> Any:
        """Standard chat completion query."""
        create_kwargs: dict[str, Any] = {}
        if schema and ctx.provider in {"openai", "fireworks"}:
            create_kwargs["response_format"] = {"type": "json_object"}

        response = await ctx.client.chat.completions.create(
            model=ctx.model,
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
            return schema.model_validate_json(self._clean_json(content))

        return content

    def _clean_json(self, text: str) -> str:
        """Clean JSON from markdown code blocks."""
        if "```json" in text:
            return text.split("```json")[-1].split("```")[0].strip()
        if "```" in text:
            return text.split("```")[-2].strip()
        return text.strip()
