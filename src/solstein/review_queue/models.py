"""Pydantic models for the human review queue.

STORY-079: ReviewQueueEntry represents one paused research graph waiting for
analyst approval or rejection before the pipeline resumes.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ReviewStatus(str, Enum):
    """Lifecycle state of a human review queue entry."""

    PENDING = "pending"
    """Awaiting analyst action — graph is paused at interrupt point."""

    APPROVED = "approved"
    """Analyst approved — graph will resume from the interrupt point."""

    REJECTED = "rejected"
    """Analyst rejected — result must not be delivered to clients."""


class ReviewQueueEntry(BaseModel):
    """One paused research result awaiting human review.

    Created by the ``human_review_gate`` LangGraph node when any company's
    confidence score falls below ``Settings.human_review_confidence_threshold``.

    The graph is paused at the interrupt point until the entry is approved
    (graph resumes from interrupt) or rejected (graph is not resumed; result
    is withheld from clients).
    """

    id: str = Field(..., description="UUID4 unique identifier for this review entry.")
    run_id: str = Field(..., description="LangGraph thread_id / research run identifier.")

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc),
        description="UTC timestamp when this entry was created.",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc),
        description="UTC timestamp of last status change.",
    )

    status: ReviewStatus = Field(
        default=ReviewStatus.PENDING,
        description="Current review lifecycle state.",
    )

    # Research result metadata for the analyst
    confidence_scores: dict[str, float] = Field(
        default_factory=dict,
        description="Per-company confidence scores that triggered review. Structure: {company_id: score_in_0_to_1}.",
    )
    company_scores: dict[str, Any] = Field(
        default_factory=dict,
        description="Per-company composite scores and classifications from the scoring node.",
    )
    conflict_flags: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Contradictions flagged during conflict resolution.",
    )
    low_confidence_companies: list[str] = Field(
        default_factory=list,
        description="Company IDs whose confidence score triggered this review.",
    )

    # Analyst response fields
    reviewer_id: str | None = Field(
        default=None,
        description="ID or name of the analyst who actioned this review.",
    )
    reviewer_rationale: str | None = Field(
        default=None,
        description="Free-text rationale provided by the analyst on rejection.",
    )
