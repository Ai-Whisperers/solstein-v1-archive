"""Anthropic-native query handler using the official Anthropic SDK.

STORY-071: Replaces the OpenAI-compatible wrapper for Anthropic calls
with the native Anthropic SDK (AsyncAnthropic).
"""

from __future__ import annotations

from typing import Any

from loguru import logger
from pydantic import BaseModel


class AnthropicQuerier:
    """Handles queries to Anthropic via the native SDK."""

    async def query(
        self,
        client: Any,
        model: str,
        prompt: str,
        system_prompt: str | None = None,
        schema: type[BaseModel] | None = None,
    ) -> Any:
        """Query Anthropic using the native messages API.

        Args:
            client: An AsyncAnthropic client instance.
            model: Model name (e.g. 'claude-sonnet-4-20250514').
            prompt: User prompt text.
            system_prompt: Optional system prompt.
            schema: Optional Pydantic schema for structured output.

        Returns:
            Text content string, or validated Pydantic model if schema provided.

        Raises:
            RuntimeError: If response content is empty.
        """
        system = (
            system_prompt
            or "You are an expert business analyst specializing in technology "
            "companies and private equity. Provide concise, data-driven insights."
        )

        create_kwargs: dict[str, Any] = {
            "model": model,
            "max_tokens": 2000,
            "messages": [{"role": "user", "content": prompt}],
            "system": system,
            "temperature": 0.3,
        }

        logger.debug(
            "[AnthropicQuerier] Calling Anthropic SDK",
            extra={"model": model, "has_schema": schema is not None},
        )

        response = await client.messages.create(**create_kwargs)

        if not response.content:
            raise RuntimeError("Empty response from Anthropic")

        content = response.content[0].text

        if schema:
            return self._parse_schema_response(content, schema)

        return content

    def _parse_schema_response(
        self, content: str, schema: type[BaseModel]
    ) -> BaseModel:
        """Parse and validate JSON response against schema."""
        cleaned = self._clean_json(content)
        return schema.model_validate_json(cleaned)

    def _clean_json(self, text: str) -> str:
        """Clean JSON from markdown code blocks."""
        if "```json" in text:
            return text.split("```json")[-1].split("```")[0].strip()
        if "```" in text:
            return text.split("```")[-2].strip()
        return text.strip()
