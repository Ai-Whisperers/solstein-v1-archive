"""Explicit batch enrichment outcome contracts."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .company import UnifiedCompany

BatchEnrichmentStatus = Literal["success", "partial", "failure"]


class BatchEnrichmentOutcome(BaseModel):
    """Per-company enrichment outcome for batch processing."""

    model_config = ConfigDict(extra="forbid")

    company: UnifiedCompany
    status: BatchEnrichmentStatus
    errors: list[str] = Field(default_factory=list)
    from_cache: bool = False
