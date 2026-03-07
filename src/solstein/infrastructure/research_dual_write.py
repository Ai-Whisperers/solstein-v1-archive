"""Research dual-write persistence with outbox pattern.

EPIC-020: Refactored persist_research_run_records to use helper functions.
"""

from __future__ import annotations

# pyright: reportMissingTypeStubs=false
import json
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, cast
from urllib.parse import urlparse

from sqlalchemy import select
from sqlalchemy.exc import OperationalError

from solstein.research.sources import canonicalize_url  # type: ignore[reportMissingTypeStubs]

from .database_models import (
    ContradictionRecord,
    ContradictionTransitionRecord,
    EvidenceReadinessRecord,
    MetricObservationRecord,
    OutboxRecord,
    ResearchArtifactRecord,
    ResearchRunRecord,
    ResearchStageRecord,
    SourceDocumentRecord,
)
from .retry_policy import FailureClassification, RetryPolicy

if TYPE_CHECKING:
    from pathlib import Path
    from uuid import UUID

    from sqlalchemy.orm import Session


JsonValue = dict[str, "JsonValue"] | list["JsonValue"] | str | int | float | bool | None

ALLOWED_CONTRADICTION_TRANSITIONS = {
    "open": {"resolved", "ignored"},
}


class ContradictionLifecycleError(Exception):
    code: str
    details: dict[str, object | None]

    def __init__(
        self,
        message: str,
        *,
        code: str,
        contradiction_id: str | None = None,
        from_status: str | None = None,
        to_status: str | None = None,
        allowed_transitions: dict[str, set[str]] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        normalized_transitions = None
        if allowed_transitions is not None:
            normalized_transitions = {key: sorted(values) for key, values in allowed_transitions.items()}
        self.details = {
            "contradiction_id": contradiction_id,
            "from_status": from_status,
            "to_status": to_status,
            "allowed_transitions": normalized_transitions,
        }

    def to_dict(self) -> dict[str, object | None]:
        return {
            "code": self.code,
            "message": str(self),
            "details": self.details,
        }


def transition_contradiction_status(
    *,
    session: Session,
    contradiction_id: UUID | str,
    to_status: str,
    changed_by: str | None = None,
    reason: str | None = None,
) -> ContradictionRecord:
    now = datetime.now(timezone.utc)
    transaction = session.begin_nested() if session.in_transaction() else session.begin()
    with transaction:
        contradiction = session.execute(
            select(ContradictionRecord).where(ContradictionRecord.id == contradiction_id)
        ).scalar_one_or_none()
        if contradiction is None:
            raise ContradictionLifecycleError(
                "Contradiction record not found",
                code="CONTRADICTION_NOT_FOUND",
                contradiction_id=str(contradiction_id),
                to_status=to_status,
            )

        from_status = contradiction.status
        if (
            from_status not in ALLOWED_CONTRADICTION_TRANSITIONS
            or to_status not in ALLOWED_CONTRADICTION_TRANSITIONS[from_status]
        ):
            raise ContradictionLifecycleError(
                f"Invalid transition from '{from_status}' to '{to_status}'",
                code="INVALID_TRANSITION",
                contradiction_id=str(contradiction_id),
                from_status=from_status,
                to_status=to_status,
                allowed_transitions=ALLOWED_CONTRADICTION_TRANSITIONS,
            )

        transition = ContradictionTransitionRecord(
            contradiction_id=contradiction.id,
            from_status=from_status,
            to_status=to_status,
            changed_by=changed_by,
            reason=reason,
            created_at=now,
        )
        session.add(transition)

        contradiction.status = to_status
        if to_status == "resolved":
            contradiction.resolved_at = now
        elif to_status == "ignored":
            contradiction.ignored_at = now
        contradiction.updated_at = now

        session.commit()
    return contradiction


# Import helper functions from research_persistence module
from .research_persistence import (
    delete_existing_run,
    create_research_run,
    persist_stage_records,
    persist_artifact_records,
    persist_source_documents,
    persist_metric_observations,
    persist_evidence_readiness,
    persist_contradictions,
)


def persist_research_run_records(
    *,
    session: Session,
    run_id: str,
    market: str,
    seed_company: str,
    strict_provenance: bool,
    min_readiness_score: float | None,
    max_contradictions: int | None,
    min_total_sources: int | None,
    stage_report: dict[str, JsonValue],
    artifacts: dict[str, JsonValue],
) -> UUID:
    """Persist research run records to database.

    EPIC-020: Refactored from 198-line monolithic function to use
    helper functions for better maintainability.
    """
    # Delete existing run if present
    delete_existing_run(session, run_id)

    # Create new research run
    run = create_research_run(
        session,
        run_id,
        market,
        seed_company,
        strict_provenance,
        min_readiness_score,
        max_contradictions,
        min_total_sources,
        artifacts.get("run_summary"),
    )

    # Get run primary key
    run_pk = session.execute(select(ResearchRunRecord.id).where(ResearchRunRecord.run_id == run_id)).scalar_one()

    # Extract stages from stage report
    stages: list[dict[str, JsonValue]] = []
    stages_obj = stage_report.get("stages")
    if isinstance(stages_obj, list):
        for stage in stages_obj:
            if isinstance(stage, dict):
                stages.append(cast("dict[str, JsonValue]", stage))

    # Persist stage records
    persist_stage_records(session, run, stages)

    # Extract artifact hashes
    artifact_hashes_obj = stage_report.get("artifact_hashes", {})
    artifact_hashes: dict[str, str] = {}
    if isinstance(artifact_hashes_obj, dict):
        artifact_hashes = cast("dict[str, str]", artifact_hashes_obj)

    # Persist artifact records
    persist_artifact_records(session, run, artifacts, artifact_hashes)

    # Persist source documents
    extracted = artifacts.get("extracted", [])
    if isinstance(extracted, list):
        persist_source_documents(session, run, extracted)

    # Persist metric observations
    if isinstance(extracted, list):
        persist_metric_observations(session, run, extracted)

    # Persist evidence readiness
    readiness = artifacts.get("evidence_readiness", {})
    if isinstance(readiness, dict):
        persist_evidence_readiness(session, run, readiness)

    # Persist contradictions
    contradictions = artifacts.get("contradictions", {})
    if isinstance(contradictions, dict):
        persist_contradictions(session, run, contradictions)

    return run_pk


def _build_outbox_payload(
    *,
    run_id: str,
    event_type: str,
    market: str,
    seed_company: str,
    strict_provenance: bool,
    min_readiness_score: float | None,
    max_contradictions: int | None,
    min_total_sources: int | None,
    artifacts: dict[str, JsonValue],
) -> dict[str, JsonValue]:
    return {
        "run_id": run_id,
        "event_type": event_type,
        "market": market,
        "seed_company": seed_company,
        "strict_provenance": strict_provenance,
        "min_readiness_score": min_readiness_score,
        "max_contradictions": max_contradictions,
        "min_total_sources": min_total_sources,
        "artifacts": artifacts,
    }


def persist_research_run(
    session: Session,
    run_id: str,
    market: str,
    seed_company: str,
    strict_provenance: bool,
    min_readiness_score: float | None,
    max_contradictions: int | None,
    min_total_sources: int | None,
    stage_report: dict[str, JsonValue],
    artifacts: dict[str, JsonValue],
) -> UUID:
    event_type = "research_run_persist"
    event_key = f"{run_id}:{event_type}"
    now = datetime.now(timezone.utc)
    payload = _build_outbox_payload(
        run_id=run_id,
        event_type=event_type,
        market=market,
        seed_company=seed_company,
        strict_provenance=strict_provenance,
        min_readiness_score=min_readiness_score,
        max_contradictions=max_contradictions,
        min_total_sources=min_total_sources,
        artifacts=artifacts,
    )

    try:
        outbox = session.execute(select(OutboxRecord).where(OutboxRecord.event_key == event_key)).scalar_one_or_none()
        if outbox is None:
            outbox = OutboxRecord(
                event_key=event_key,
                event_type=event_type,
                status="pending",
                payload=payload,
                attempt_count=0,
                created_at=now,
                updated_at=now,
            )
            session.add(outbox)
        else:
            outbox.payload = payload
            outbox.status = "pending"
            outbox.attempt_count = 0
            outbox.last_error = None
            outbox.updated_at = now
        session.commit()
    except OperationalError as e:
        session.rollback()
        raise RuntimeError(f"Failed to persist outbox record: {e}") from e

    try:
        run_pk = persist_research_run_records(
            session=session,
            run_id=run_id,
            market=market,
            seed_company=seed_company,
            strict_provenance=strict_provenance,
            min_readiness_score=min_readiness_score,
            max_contradictions=max_contradictions,
            min_total_sources=min_total_sources,
            stage_report=stage_report,
            artifacts=artifacts,
        )
        outbox.status = "completed"
        outbox.updated_at = datetime.now(timezone.utc)
        session.commit()
        return run_pk
    except Exception as e:
        session.rollback()
        outbox.status = "failed"
        outbox.last_error = str(e)
        outbox.updated_at = datetime.now(timezone.utc)
        session.commit()
        raise


def process_outbox(session: Session, max_attempts: int = 3) -> int:
    retry_policy = RetryPolicy(max_attempts=max_attempts)
    pending = session.execute(select(OutboxRecord).where(OutboxRecord.status == "pending")).scalars().all()

    processed = 0
    for outbox in pending:
        try:
            payload = outbox.payload
            if not isinstance(payload, dict):
                continue
            event_type = payload.get("event_type")
            if event_type == "research_run_persist":
                run_id = payload.get("run_id")
                if run_id:
                    persist_research_run_records(
                        session=session,
                        run_id=run_id,
                        market=payload.get("market", ""),
                        seed_company=payload.get("seed_company", ""),
                        strict_provenance=payload.get("strict_provenance", False),
                        min_readiness_score=payload.get("min_readiness_score"),
                        max_contradictions=payload.get("max_contradictions"),
                        min_total_sources=payload.get("min_total_sources"),
                        stage_report=payload.get("stage_report", {}),
                        artifacts=payload.get("artifacts", {}),
                    )
            outbox.status = "completed"
            outbox.updated_at = datetime.now(timezone.utc)
            processed += 1
        except Exception as e:
            outbox.attempt_count += 1
            classification = retry_policy.classify(e)
            if classification == FailureClassification.PERMANENT or outbox.attempt_count >= max_attempts:
                outbox.status = "failed"
            outbox.last_error = str(e)
            outbox.updated_at = datetime.now(timezone.utc)
    session.commit()
    return processed
