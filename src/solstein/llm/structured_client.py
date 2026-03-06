"""Type-safe structured LLM output client.

Wraps ``EnhancedLLMClient.generate_structured()`` with:
- Pydantic model validation and retry on malformed JSON
- LLM call tracing via ``solstein.llm.tracing.LLMTracer``
- Cleaner error propagation (raises ``StructuredOutputError`` instead of
  returning ``None``/raw dicts)

Usage::

    from pydantic import BaseModel
    from solstein.llm.structured_client import StructuredLLMClient

    class CompanyProfile(BaseModel):
        name: str
        industry: str
        competitors: list[str]

    client = StructuredLLMClient()
    profile = await client.extract(
        prompt="Describe Stripe as a JSON object.",
        schema=CompanyProfile,
    )
    logger.info(f"Profile: {profile.name}")
"""

from __future__ import annotations

import json
import time
from typing import Any, TypeVar

from loguru import logger
from pydantic import BaseModel, ValidationError

from solstein.llm.tracing import LLMTracer, TraceRecord

T = TypeVar("T", bound=BaseModel)

# Default max parse + validation retries
_DEFAULT_RETRIES = 2


class StructuredOutputError(Exception):
    """Raised when the LLM fails to return a valid structured response."""

    def __init__(self, message: str, raw_response: str | None = None) -> None:
        super().__init__(message)
        self.raw_response = raw_response


class StructuredLLMClient:
    """High-level client for structured (Pydantic-validated) LLM extraction.

    Args:
        tracer: Optional ``LLMTracer`` instance.  A default no-op tracer is
                used when not provided.
        max_retries: Number of retry attempts when the LLM returns malformed
                     JSON (each retry re-prompts with an explicit JSON schema).
    """

    def __init__(
        self,
        tracer: LLMTracer | None = None,
        max_retries: int = _DEFAULT_RETRIES,
    ) -> None:
        from solstein.llm.enhanced_client import EnhancedLLMClient

        self._inner = EnhancedLLMClient()
        self._tracer = tracer or LLMTracer()
        self._max_retries = max_retries

    async def extract(
        self,
        prompt: str,
        schema: type[T],
        context: str = "",
        temperature: float = 0.1,
    ) -> T:
        """Extract a Pydantic model from an LLM response.

        Args:
            prompt: The user-facing instruction.
            schema: Pydantic model class that defines the expected JSON shape.
            context: Optional background text injected into the system prompt.
            temperature: Sampling temperature (low values = more deterministic).

        Returns:
            A validated *schema* instance.

        Raises:
            StructuredOutputError: If all retries fail.
        """
        schema_json = json.dumps(schema.model_json_schema(), indent=2)
        system_prompt = (
            "You are a structured data extractor.  "
            "Return ONLY valid JSON that strictly conforms to the provided schema.  "
            "No markdown, no explanation—just the JSON object.\n\n"
            f"Schema:\n{schema_json}"
        )
        if context:
            system_prompt += f"\n\nContext:\n{context}"

        last_error: Exception | None = None
        raw: str = ""

        for attempt in range(1, self._max_retries + 2):
            start = time.monotonic()
            try:
                raw = await self._inner.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=temperature,
                )
                model_instance = self._parse_and_validate(raw, schema)
                elapsed = time.monotonic() - start
                self._tracer.record(
                    TraceRecord(
                        prompt=prompt,
                        schema_name=schema.__name__,
                        attempt=attempt,
                        latency_s=elapsed,
                        success=True,
                    )
                )
                return model_instance
            except (json.JSONDecodeError, ValidationError, ValueError) as exc:
                last_error = exc
                elapsed = time.monotonic() - start
                logger.warning(
                    "Structured extraction failed",
                    schema=schema.__name__,
                    attempt=attempt,
                    max_retries=self._max_retries + 1,
                    error=str(exc),
                )
                self._tracer.record(
                    TraceRecord(
                        prompt=prompt,
                        schema_name=schema.__name__,
                        attempt=attempt,
                        latency_s=elapsed,
                        success=False,
                        error=str(exc),
                    )
                )
                if attempt <= self._max_retries:
                    # Re-prompt with explicit feedback about the error
                    prompt = (
                        f"{prompt}\n\n"
                        f"[Previous attempt returned invalid JSON: {exc}. "
                        "Please return ONLY a valid JSON object.]"
                    )

        raise StructuredOutputError(
            f"Failed to extract {schema.__name__} after {self._max_retries + 1} attempts: {last_error}",
            raw_response=raw,
        )

    def _parse_and_validate(self, raw: str, schema: type[T]) -> T:
        """Strip markdown fences if present, then parse and validate JSON."""
        cleaned = raw.strip()
        # Strip ```json ... ``` fences
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            cleaned = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        data: dict[str, Any] = json.loads(cleaned)
        return schema.model_validate(data)
