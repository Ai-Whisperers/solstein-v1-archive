"""JSON parsing utilities for LLM responses.

STORY-071: Extracted from enhanced_client.py to keep the main client
under 100 lines.
"""

from __future__ import annotations

from typing import TypeVar

from loguru import logger
from pydantic import BaseModel

TBaseModel = TypeVar("TBaseModel", bound=BaseModel)


def parse_structured_result(
    result: str | BaseModel,
    schema: type[TBaseModel],
) -> TBaseModel | None:
    """Parse structured result into schema.

    Args:
        result: Raw LLM response (string or BaseModel).
        schema: Target Pydantic model class.

    Returns:
        Validated model instance, or None if parsing fails.
    """
    try:
        if isinstance(result, str):
            return parse_json_string(result, schema)
        elif isinstance(result, BaseModel):
            return schema.model_validate(result.model_dump())
        else:
            return schema.model_validate(result)
    except Exception as e:  # noqa: BLE001 — intentional broad catch for graceful fallback
        logger.warning(
            f"[LLMParsing] Failed to parse structured output: {e}",
            extra={"schema": schema.__name__, "error_type": type(e).__name__},
        )
        return None


def parse_json_string(
    text: str,
    schema: type[TBaseModel],
) -> TBaseModel:
    """Parse JSON string, handling markdown code blocks.

    Args:
        text: Raw text potentially containing JSON in markdown fences.
        schema: Target Pydantic model class.

    Returns:
        Validated model instance.

    Raises:
        ValidationError: If JSON doesn't match schema.
        JSONDecodeError: If text isn't valid JSON.
    """
    cleaned = clean_json(text)
    return schema.model_validate_json(cleaned)


def clean_json(text: str) -> str:
    """Strip markdown code fences from JSON text."""
    if "```json" in text:
        return text.split("```json")[-1].split("```")[0].strip()
    if "```" in text:
        return text.split("```")[-2].strip()
    return text.strip()
