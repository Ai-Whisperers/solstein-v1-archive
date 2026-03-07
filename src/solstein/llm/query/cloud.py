"""Cloud provider query handler for EnhancedLLMClient."""

from __future__ import annotations

from typing import Any

from loguru import logger
from pydantic import BaseModel


class CloudProviderQuerier:
    """Handles queries to cloud LLM providers."""

    async def query(
        self,
        client: Any,
        provider: str,
        model: str,
        prompt: str,
        system_prompt: str | None = None,
        schema: type[BaseModel] | None = None,
    ) -> Any:
        """Query a cloud LLM provider."""
        system = (
            system_prompt
            or "You are an expert business analyst specializing in technology companies and private equity. Provide concise, data-driven insights."
        )

        # Check if we can use structured output (OpenAI only)
        use_parse = (
            schema is not None
            and provider == "openai"
            and hasattr(client, "beta")
            and hasattr(client.beta, "chat")
            and hasattr(client.beta.chat.completions, "parse")
        )

        if use_parse:
            return await self._query_with_parse(client, model, system, prompt, schema)

        return await self._query_standard(client, model, system, prompt, schema, provider)

    async def _query_with_parse(
        self,
        client: Any,
        model: str,
        system: str,
        prompt: str,
        schema: type[BaseModel],
    ) -> BaseModel:
        """Query using OpenAI's parse method for structured output."""
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

    async def _query_standard(
        self,
        client: Any,
        model: str,
        system: str,
        prompt: str,
        schema: type[BaseModel] | None,
        provider: str,
    ) -> Any:
        """Standard chat completion query."""
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
            return schema.model_validate_json(self._clean_json(content))

        return content

    def _clean_json(self, text: str) -> str:
        """Clean JSON from markdown code blocks."""
        if "```json" in text:
            return text.split("```json")[-1].split("```")[0].strip()
        if "```" in text:
            return text.split("```")[-2].strip()
        return text.strip()
