"""Ollama query handler for EnhancedLLMClient."""

from __future__ import annotations

from typing import Any

from loguru import logger
from pydantic import BaseModel

from solstein.config import Settings


class OllamaQuerier:
    """Handles queries to Ollama local instance."""

    def __init__(self, settings: Settings):
        self.settings = settings

    async def query(
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
                        return self._parse_schema_response(content, schema)

                    return content
                else:
                    raise Exception(f"Ollama returned {response.status}")
        except TimeoutError as e:
            logger.error(f"Ollama request timed out for model {self.settings.ollama_model}")
            raise Exception("Ollama request timeout") from e
        except Exception as e:
            logger.error(
                f"[OllamaQuerier] query failed: {e}",
                extra={
                    "model": self.settings.ollama_model,
                    "url": f"{self.settings.ollama_url}/api/chat",
                    "error_type": type(e).__name__,
                },
            )
            raise

    def _parse_schema_response(self, content: str, schema: type[BaseModel]) -> BaseModel | None:
        """Parse schema response from Ollama."""
        try:
            if "```json" in content:
                content = content.split("```json")[-1].split("```")[0].strip()
            return schema.model_validate_json(content)
        except Exception as e:
            logger.warning(f"Ollama schema validation failed: {e}")
            return None
