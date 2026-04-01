"""Human review queue API endpoints — STORY-079.

Provides endpoints for analysts to list, inspect, approve, and reject
low-confidence research results that are paused at the human_review_gate
LangGraph node.

Workflow:
    1. Research graph pauses at human_review_gate for runs where any company's
       confidence score falls below ``Settings.human_review_confidence_threshold``.
    2. GET  /review/         — list all pending review items.
    3. GET  /review/{id}     — fetch a single review item with full detail.
    4. POST /review/{id}/approve — approve: resumes the LangGraph graph execution.
    5. POST /review/{id}/reject  — reject: marks result as rejected; graph is NOT
       resumed; result is withheld from clients.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, HTTPException, status
from loguru import logger
from pydantic import BaseModel, ConfigDict

from solstein.review_queue import ReviewQueueEntry, ReviewStatus, get_review_store

router = APIRouter(prefix="/review", tags=["Human Review Queue"])


# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------


class ApproveRequest(BaseModel):
    """Optional body for the approve endpoint."""

    model_config = ConfigDict(extra="forbid")

    reviewer_id: str | None = None
    """Identifier of the approving analyst (email, username, etc.)."""


class RejectRequest(BaseModel):
    """Required body for the reject endpoint."""

    model_config = ConfigDict(extra="forbid")

    reviewer_id: str | None = None
    """Identifier of the rejecting analyst."""

    rationale: str
    """Free-text reason for rejection. Required so the audit trail is meaningful."""


class ReviewQueueEntryResponse(BaseModel):
    """Public-facing response schema for a review queue entry."""

    id: str
    run_id: str
    created_at: str
    updated_at: str
    status: str
    confidence_scores: dict[str, float]
    company_scores: dict[str, Any]
    low_confidence_companies: list[str]
    conflict_flag_count: int
    reviewer_id: str | None
    reviewer_rationale: str | None

    @classmethod
    def from_entry(cls, entry: ReviewQueueEntry) -> ReviewQueueEntryResponse:
        return cls(
            id=entry.id,
            run_id=entry.run_id,
            created_at=entry.created_at.isoformat(),
            updated_at=entry.updated_at.isoformat(),
            status=entry.status.value,
            confidence_scores=entry.confidence_scores,
            company_scores=entry.company_scores,
            low_confidence_companies=entry.low_confidence_companies,
            conflict_flag_count=len(entry.conflict_flags),
            reviewer_id=entry.reviewer_id,
            reviewer_rationale=entry.reviewer_rationale,
        )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/",
    response_model=list[ReviewQueueEntryResponse],
    summary="List review queue entries",
    description=(
        "Returns all review queue entries. Pass ``status=pending`` to see only "
        "items awaiting analyst action."
    ),
)
def list_review_entries(
    filter_status: str | None = None,
) -> list[ReviewQueueEntryResponse]:
    """List review queue entries, optionally filtered by status."""
    store = get_review_store()
    if filter_status == "pending":
        entries = store.list_pending()
    else:
        entries = store.list_all()
    return [ReviewQueueEntryResponse.from_entry(e) for e in entries]


@router.get(
    "/{review_id}",
    response_model=ReviewQueueEntryResponse,
    summary="Get a review queue entry",
)
def get_review_entry(review_id: str) -> ReviewQueueEntryResponse:
    """Fetch a single review entry by its UUID."""
    store = get_review_store()
    entry = store.get_entry(review_id)
    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review entry {review_id} not found.",
        )
    return ReviewQueueEntryResponse.from_entry(entry)


@router.post(
    "/{review_id}/approve",
    response_model=ReviewQueueEntryResponse,
    summary="Approve a review entry and resume graph execution",
    description=(
        "Marks the review entry as APPROVED and resumes the paused LangGraph "
        "research graph from the human_review_gate interrupt point. The graph "
        "continues to the analysis and export nodes."
    ),
)
def approve_review_entry(
    review_id: str,
    body: ApproveRequest = Body(default=ApproveRequest()),
) -> ReviewQueueEntryResponse:
    """Approve a PENDING review entry and resume the research graph."""
    store = get_review_store()
    entry = store.get_entry(review_id)
    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review entry {review_id} not found.",
        )
    if entry.status != ReviewStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Review entry {review_id} is already {entry.status.value}.",
        )

    # 1. Persist the approval
    updated = store.approve(review_id, reviewer_id=body.reviewer_id)
    logger.info("[ReviewAPI] Approved review %s for run %s", review_id, entry.run_id)

    # 2. Resume the LangGraph graph
    # NOTE (STORY-255): This is the ONLY active graph runtime path in the
    # codebase — a resume-after-approval trigger, not end-to-end graph
    # execution. The canonical production runtime is research/pipeline.py.
    try:
        from solstein.research.graph.executor import _get_default_executor

        executor = _get_default_executor()
        executor.resume_after_approval(entry.run_id)
        logger.info("[ReviewAPI] Graph resumed for run %s", entry.run_id)
    except Exception as exc:
        logger.error(
            "[ReviewAPI] Graph resume failed for run %s: %s (approval recorded)",
            entry.run_id,
            exc,
        )
        # Approval is already persisted — surface error as warning, not 500

    return ReviewQueueEntryResponse.from_entry(updated)


@router.post(
    "/{review_id}/reject",
    response_model=ReviewQueueEntryResponse,
    status_code=status.HTTP_200_OK,
    summary="Reject a review entry — result will not be delivered to clients",
    description=(
        "Marks the review entry as REJECTED with the analyst's rationale. "
        "The paused LangGraph graph is NOT resumed — the export node never runs, "
        "so the result is withheld from clients."
    ),
)
def reject_review_entry(
    review_id: str,
    body: RejectRequest,
) -> ReviewQueueEntryResponse:
    """Reject a PENDING review entry. The research result is withheld."""
    store = get_review_store()
    entry = store.get_entry(review_id)
    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review entry {review_id} not found.",
        )
    if entry.status != ReviewStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Review entry {review_id} is already {entry.status.value}.",
        )

    updated = store.reject(
        review_id,
        reviewer_id=body.reviewer_id,
        rationale=body.rationale,
    )
    logger.info(
        "[ReviewAPI] Rejected review %s for run %s: %s",
        review_id,
        entry.run_id,
        body.rationale,
    )
    return ReviewQueueEntryResponse.from_entry(updated)
