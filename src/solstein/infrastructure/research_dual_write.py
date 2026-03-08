"""Research dual-write persistence with outbox pattern.

EPIC-020: Refactored persist_research_run_records to use helper functions.
"""

from __future__ import annotations

# pyright: reportMissingTypeStubs=false
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING, cast

from sqlalchemy import select
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.sql.schema import Table

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
from .database import Base as BaseImported
from .research_outbox_helpers import JsonValue, OutboxEvent, record_outbox_failure

if TYPE_CHECKING:
    from uuid import UUID

    from sqlalchemy.orm import Session


@dataclass(frozen=True)
class PersistRunPayload:
    run_id: str
    market: str
    seed_company: str
    strict_provenance: bool
    min_readiness_score: float | None
    max_contradictions: int | None
    min_total_sources: int | None
    stage_report: dict[str, JsonValue]
    artifacts: dict[str, JsonValue]


ALLOWED_CONTRADICTION_TRANSITIONS = {
    "open": {"resolved", "ignored"},
}


class ContradictionLifecycleError(Exception):
    code: str
    details: dict[str, object | None]

    def __init__(self, message: str, *, code: str, details: dict[str, object | None] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.details = details or {}

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
                details={
                    "contradiction_id": str(contradiction_id),
                    "to_status": to_status,
                },
            )

        from_status = contradiction.status
        if (
            from_status not in ALLOWED_CONTRADICTION_TRANSITIONS
            or to_status not in ALLOWED_CONTRADICTION_TRANSITIONS[from_status]
        ):
            raise ContradictionLifecycleError(
                f"Invalid transition from '{from_status}' to '{to_status}'",
                code="INVALID_TRANSITION",
                details={
                    "contradiction_id": str(contradiction_id),
                    "from_status": from_status,
                    "to_status": to_status,
                    "allowed_transitions": {
                        key: sorted(values) for key, values in ALLOWED_CONTRADICTION_TRANSITIONS.items()
                    },
                },
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
    payload: PersistRunPayload,
) -> UUID:
    """Persist research run records to database.

    EPIC-020: Refactored from 198-line monolithic function to use
    helper functions for better maintainability.
    """
    # Delete existing run if present
    delete_existing_run(session, payload.run_id)

    # Create new research run
    run = create_research_run(
        session,
        payload,
    )

    # Get run primary key
    run_pk = session.execute(
        select(ResearchRunRecord.id).where(ResearchRunRecord.run_id == payload.run_id)
    ).scalar_one()

    # Extract stages from stage report
    stages: list[dict[str, JsonValue]] = []
    stages_obj = payload.stage_report.get("stages")
    if isinstance(stages_obj, list):
        for stage in stages_obj:
            if isinstance(stage, dict):
                stages.append(cast("dict[str, JsonValue]", stage))

    # Persist stage records
    persist_stage_records(session, run, stages)

    # Extract artifact hashes
    artifact_hashes_obj = payload.stage_report.get("artifact_hashes", {})
    artifact_hashes: dict[str, str] = {}
    if isinstance(artifact_hashes_obj, dict):
        artifact_hashes = cast("dict[str, str]", artifact_hashes_obj)

    # Persist artifact records
    persist_artifact_records(session, run, payload.artifacts, artifact_hashes)

    # Persist source documents
    extracted = payload.artifacts.get("extracted", [])
    if isinstance(extracted, list):
        persist_source_documents(session, run, extracted)

    # Persist metric observations
    if isinstance(extracted, list):
        persist_metric_observations(session, run, extracted)

    # Persist evidence readiness
    readiness = payload.artifacts.get("evidence_readiness", {})
    if isinstance(readiness, dict):
        persist_evidence_readiness(session, run, readiness)

    # Persist contradictions
    contradictions = payload.artifacts.get("contradictions", {})
    if isinstance(contradictions, dict):
        persist_contradictions(session, run, contradictions)

    return run_pk


def _build_outbox_payload(*, payload: PersistRunPayload, event_type: str) -> dict[str, JsonValue]:
    return {
        "run_id": payload.run_id,
        "event_type": event_type,
        "market": payload.market,
        "seed_company": payload.seed_company,
        "strict_provenance": payload.strict_provenance,
        "min_readiness_score": payload.min_readiness_score,
        "max_contradictions": payload.max_contradictions,
        "min_total_sources": payload.min_total_sources,
        "stage_report": payload.stage_report,
        "artifacts": payload.artifacts,
    }


def persist_research_run(
    session: Session | None = None,
    payload: PersistRunPayload | None = None,
    **legacy_kwargs: object,
) -> UUID:
    resolved_payload = payload or _payload_from_legacy_kwargs(legacy_kwargs)

    if session is None:
        from solstein.config import Settings

        from .database import db_manager

        db_manager.settings = Settings.load()
        db_manager.init_sync()
        managed_session = db_manager.get_sync_session()
        try:
            return persist_research_run(
                session=managed_session,
                payload=resolved_payload,
            )
        finally:
            managed_session.close()

    tables = [
        cast(Table, OutboxRecord.__table__),
        cast(Table, ResearchRunRecord.__table__),
        cast(Table, ResearchStageRecord.__table__),
        cast(Table, ResearchArtifactRecord.__table__),
        cast(Table, EvidenceReadinessRecord.__table__),
        cast(Table, ContradictionRecord.__table__),
        cast(Table, ContradictionTransitionRecord.__table__),
        cast(Table, SourceDocumentRecord.__table__),
        cast(Table, MetricObservationRecord.__table__),
    ]
    BaseImported.metadata.create_all(bind=session.get_bind(), tables=tables)

    event_type = "research_run_persist"
    event_key = f"{resolved_payload.run_id}:{event_type}"
    now = datetime.now(timezone.utc)
    outbox_payload = _build_outbox_payload(payload=resolved_payload, event_type=event_type)
    outbox_event = OutboxEvent(event_key=event_key, event_type=event_type, payload=outbox_payload)
    try:
        with session.begin():
            outbox = session.execute(
                select(OutboxRecord).where(OutboxRecord.event_key == event_key)
            ).scalar_one_or_none()
            if outbox is None:
                outbox = OutboxRecord(
                    event_key=event_key,
                    event_type=event_type,
                    status="pending",
                    payload=outbox_payload,
                    attempt_count=0,
                    available_at=now,
                    created_at=now,
                    updated_at=now,
                    last_error=None,
                )
                session.add(outbox)
            else:
                outbox.payload = outbox_payload
                outbox.status = "pending"
                outbox.last_error = None
                outbox.available_at = now
                outbox.updated_at = now

            run_pk = persist_research_run_records(
                session=session,
                payload=resolved_payload,
            )
            outbox.status = "succeeded"
            outbox.attempt_count = (outbox.attempt_count or 0) + 1
            outbox.updated_at = datetime.now(timezone.utc)
            outbox.available_at = outbox.updated_at
            outbox.last_error = None
            return run_pk
    except OperationalError as e:
        session.rollback()
        raise RuntimeError(f"Failed to persist dual-write transaction: {e}") from e
    except (ValueError, TypeError, RuntimeError, SQLAlchemyError, OSError) as e:
        session.rollback()
        record_outbox_failure(session=session, event=outbox_event, exc=e)
        raise


def process_outbox(session: Session, max_attempts: int = 3) -> int:
    pending = session.execute(select(OutboxRecord).where(OutboxRecord.status == "pending")).scalars().all()

    processed = 0
    for outbox in pending:
        payload: dict[str, JsonValue] = {}
        try:
            payload_obj = outbox.payload
            if not isinstance(payload_obj, dict):
                continue
            payload_source = cast("dict[object, JsonValue]", payload_obj)
            payload = {str(key): value for key, value in payload_source.items()}

            event_type_obj = payload.get("event_type")
            event_type = event_type_obj if isinstance(event_type_obj, str) else ""
            if event_type == "research_run_persist":
                run_id_obj = payload.get("run_id")
                market_obj = payload.get("market")
                seed_company_obj = payload.get("seed_company")
                strict_obj = payload.get("strict_provenance")
                min_readiness_obj = payload.get("min_readiness_score")
                max_contradictions_obj = payload.get("max_contradictions")
                min_total_sources_obj = payload.get("min_total_sources")

                run_id = run_id_obj if isinstance(run_id_obj, str) else ""
                market = market_obj if isinstance(market_obj, str) else ""
                seed_company = seed_company_obj if isinstance(seed_company_obj, str) else ""
                strict_provenance = strict_obj if isinstance(strict_obj, bool) else False
                min_readiness_score = float(min_readiness_obj) if isinstance(min_readiness_obj, (int, float)) else None
                max_contradictions = (
                    int(max_contradictions_obj) if isinstance(max_contradictions_obj, (int, float)) else None
                )
                min_total_sources = (
                    int(min_total_sources_obj) if isinstance(min_total_sources_obj, (int, float)) else None
                )

                if run_id:
                    stage_report_payload = payload.get("stage_report", {})
                    artifacts_payload = payload.get("artifacts", {})
                    stage_report = stage_report_payload if isinstance(stage_report_payload, dict) else {}
                    artifacts = artifacts_payload if isinstance(artifacts_payload, dict) else {}
                    persist_research_run_records(
                        session=session,
                        payload=PersistRunPayload(
                            run_id=run_id,
                            market=market,
                            seed_company=seed_company,
                            strict_provenance=strict_provenance,
                            min_readiness_score=min_readiness_score,
                            max_contradictions=max_contradictions,
                            min_total_sources=min_total_sources,
                            stage_report=cast("dict[str, JsonValue]", stage_report),
                            artifacts=cast("dict[str, JsonValue]", artifacts),
                        ),
                    )
            outbox.status = "succeeded"
            outbox.updated_at = datetime.now(timezone.utc)
            processed += 1
        except (ValueError, TypeError, RuntimeError, SQLAlchemyError, OSError) as e:
            record_outbox_failure(
                session=session,
                event=OutboxEvent(event_key=outbox.event_key, event_type=outbox.event_type, payload=payload),
                exc=e,
                max_attempts=max_attempts,
            )
    session.commit()
    return processed


def _payload_from_legacy_kwargs(legacy_kwargs: dict[str, object]) -> PersistRunPayload:
    run_id_obj = legacy_kwargs.get("batch_id")
    market_obj = legacy_kwargs.get("market")
    if not isinstance(run_id_obj, str) or not isinstance(market_obj, str):
        raise ValueError("persist_research_run requires run_id and market")

    seed_company_obj = legacy_kwargs.get("seed_company")
    seed_company = seed_company_obj if isinstance(seed_company_obj, str) else "unknown"
    companies_obj = legacy_kwargs.get("companies")
    artifact_hashes_obj = legacy_kwargs.get("artifact_hashes")

    stage_report: dict[str, JsonValue] = {
        "market": market_obj,
        "seed_company": seed_company,
        "stages": [],
    }
    if isinstance(artifact_hashes_obj, dict):
        stage_report["artifact_hashes"] = cast("JsonValue", artifact_hashes_obj)

    extracted: list[JsonValue] = []
    if isinstance(companies_obj, list):
        for company in cast("list[object]", companies_obj):
            model_dump = getattr(company, "model_dump", None)
            if callable(model_dump):
                extracted_obj = model_dump(mode="json")
                if isinstance(extracted_obj, dict):
                    extracted.append(cast("JsonValue", extracted_obj))

    artifacts: dict[str, JsonValue] = {
        "extracted": extracted,
        "run_summary": {
            "market": market_obj,
            "seed_company": seed_company,
            "profiles": len(extracted),
            "scored": len(extracted),
        },
    }

    return PersistRunPayload(
        run_id=run_id_obj,
        market=market_obj,
        seed_company=seed_company,
        strict_provenance=False,
        min_readiness_score=None,
        max_contradictions=None,
        min_total_sources=None,
        stage_report=stage_report,
        artifacts=artifacts,
    )
