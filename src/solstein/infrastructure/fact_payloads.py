"""Shared validated schemas for connector-produced fact payloads."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from loguru import logger
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator


class ConnectorFactPayload(BaseModel):
    """Canonical fact envelope at connector and refresh boundaries."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    company_id: str = Field(min_length=1)
    fact_type: str = Field(min_length=1)
    value: Any = None
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    extracted_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    value_hash: str | None = Field(default=None, alias="_hash")

    @model_validator(mode="before")
    @classmethod
    def normalize_legacy_aliases(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        normalized = dict(data)
        if not normalized.get("fact_type") and normalized.get("type"):
            normalized["fact_type"] = normalized["type"]
        if normalized.get("metadata") is None:
            normalized["metadata"] = {}
        return normalized


def validate_connector_fact_payloads(
    facts: list[dict[str, Any]],
    *,
    source_name: str,
    default_confidence: float,
) -> list[dict[str, Any]]:
    """Normalize and validate connector fact envelopes.

    Invalid payloads are rejected before delta detection or persistence to keep
    malformed dicts from moving deeper into the pipeline.
    """

    validated_facts: list[dict[str, Any]] = []

    for index, fact in enumerate(facts):
        try:
            payload = ConnectorFactPayload.model_validate(
                {
                    "confidence": default_confidence,
                    **fact,
                }
            )
        except ValidationError as exc:
            logger.warning(f"[connector-fact-schema] Rejecting invalid fact from {source_name} at index {index}: {exc}")
            continue

        validated_facts.append(payload.model_dump(by_alias=True))

    return validated_facts
