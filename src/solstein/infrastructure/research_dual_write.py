"""Research dual-write persistence with outbox pattern.

EPIC-020: Refactored persist_research_run_records to use helper functions.
"""

from __future__ import annotations

# pyright: reportMissingTypeStubs=false
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import TYPE_CHECKING, cast

from sqlalchemy import select
from sqlalchemy.exc import OperationalError

from solstein.research.sources import canonicalize_url  # type: ignore[reportMissingTypeStubs]

from .database_models import (
    ContradictionRecord,
    ContradictionTransitionRecord,
    OutboxRecord,
    ResearchRunRecord,
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
    stage_report: dict[str, JsonValue],
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
        "stage_report": stage_report,
        "artifacts": artifacts,
    }


def persist_research_run(
    session: Session | None = None,
    run_id: str | None = None,
    market: str | None = None,
    seed_company: str | None = None,
    strict_provenance: bool = False,
    min_readiness_score: float | None = None,
    max_contradictions: int | None = None,
    min_total_sources: int | None = None,
    stage_report: dict[str, JsonValue] | None = None,
    artifacts: dict[str, JsonValue] | None = None,
    **legacy_kwargs: object,
) -> UUID:
    if run_id is None and isinstance(legacy_kwargs.get("batch_id"), str):
        run_id = cast("str", legacy_kwargs["batch_id"])
    if market is None and isinstance(legacy_kwargs.get("market"), str):
        market = cast("str", legacy_kwargs["market"])
    if seed_company is None:
        seed_company_obj = legacy_kwargs.get("seed_company")
        seed_company = seed_company_obj if isinstance(seed_company_obj, str) else "unknown"

    companies_obj = legacy_kwargs.get("companies")
    artifact_hashes_obj = legacy_kwargs.get("artifact_hashes")

    if run_id is None or market is None:
        raise ValueError("persist_research_run requires run_id and market")

    if stage_report is None:
        stage_report = {
            "market": market,
            "seed_company": seed_company,
            "stages": [],
        }
        if isinstance(artifact_hashes_obj, dict):
            stage_report["artifact_hashes"] = cast("JsonValue", artifact_hashes_obj)

    if artifacts is None:
        extracted: list[JsonValue] = []
        if isinstance(companies_obj, list):
            for company in cast("list[object]", companies_obj):
                model_dump = getattr(company, "model_dump", None)
                if callable(model_dump):
                    extracted_obj = model_dump(mode="json")
                    if isinstance(extracted_obj, dict):
                        extracted.append(cast("JsonValue", extracted_obj))

        artifacts = {
            "extracted": extracted,
            "run_summary": {
                "market": market,
                "seed_company": seed_company,
                "profiles": len(extracted),
                "scored": len(extracted),
            },
        }

    if session is None:
        from solstein.config import Settings

        from .database import db_manager

        try:
            managed_session = db_manager.get_sync_session()
        except RuntimeError:
            db_manager.settings = Settings.load()
            db_manager.init_sync()
            managed_session = db_manager.get_sync_session()
        try:
            return persist_research_run(
                session=managed_session,
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
        finally:
            managed_session.close()

    stage_report_payload = stage_report
    artifacts_payload = artifacts

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
        stage_report=stage_report_payload,
        artifacts=artifacts_payload,
    )
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
                    payload=payload,
                    attempt_count=0,
                    available_at=now,
                    created_at=now,
                    updated_at=now,
                    last_error=None,
                )
                session.add(outbox)
            else:
                outbox.payload = payload
                outbox.status = "pending"
                outbox.last_error = None
                outbox.available_at = now
                outbox.updated_at = now

            run_pk = persist_research_run_records(
                session=session,
                run_id=run_id,
                market=market,
                seed_company=seed_company,
                strict_provenance=strict_provenance,
                min_readiness_score=min_readiness_score,
                max_contradictions=max_contradictions,
                min_total_sources=min_total_sources,
                stage_report=stage_report_payload,
                artifacts=artifacts_payload,
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
    except Exception as e:
        session.rollback()
        record_outbox_failure(
            session=session,
            event_key=event_key,
            event_type=event_type,
            payload=payload,
            exc=e,
        )
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
                        run_id=run_id,
                        market=market,
                        seed_company=seed_company,
                        strict_provenance=strict_provenance,
                        min_readiness_score=min_readiness_score,
                        max_contradictions=max_contradictions,
                        min_total_sources=min_total_sources,
                        stage_report=cast("dict[str, JsonValue]", stage_report),
                        artifacts=cast("dict[str, JsonValue]", artifacts),
                    )
            outbox.status = "succeeded"
            outbox.updated_at = datetime.now(timezone.utc)
            processed += 1
        except Exception as e:
            record_outbox_failure(
                session=session,
                event_key=outbox.event_key,
                event_type=outbox.event_type,
                payload=payload,
                exc=e,
                max_attempts=max_attempts,
            )
    session.commit()
    return processed


def load_research_artifacts(output_dir: Path) -> tuple[dict[str, JsonValue], dict[str, JsonValue]]:
    stage_report_path = output_dir / "stage_report.json"
    if not stage_report_path.exists():
        raise FileNotFoundError(f"Missing stage report at {stage_report_path}")

    stage_report_obj = json.loads(stage_report_path.read_text(encoding="utf-8"))
    if isinstance(stage_report_obj, dict):
        stage_report = cast("dict[str, JsonValue]", stage_report_obj)
    else:
        stage_report = {}

    artifacts: dict[str, JsonValue] = {}
    known_artifacts = {
        "extracted": "extracted.json",
        "market_analysis": "market_analysis.json",
        "scored_companies": "scored_companies.json",
        "provenance_report": "provenance_report.json",
        "contradictions_report": "contradictions_report.json",
        "evidence_readiness": "evidence_readiness.json",
        "run_summary": "run_summary.json",
    }

    for key, filename in known_artifacts.items():
        artifact_path = output_dir / filename
        if not artifact_path.exists():
            continue
        artifact_obj = json.loads(artifact_path.read_text(encoding="utf-8"))
        if isinstance(artifact_obj, (dict, list, str, int, float, bool)) or artifact_obj is None:
            artifacts[key] = cast("JsonValue", artifact_obj)

    return stage_report, artifacts


def record_outbox_failure(
    *,
    session: Session,
    event_key: str,
    event_type: str,
    payload: dict[str, JsonValue],
    exc: Exception,
    max_attempts: int = 3,
) -> None:
    now = datetime.now(timezone.utc)
    retry_policy = RetryPolicy(max_attempts=max_attempts)

    outbox = session.execute(select(OutboxRecord).where(OutboxRecord.event_key == event_key)).scalar_one_or_none()
    if outbox is None:
        outbox = OutboxRecord(
            event_key=event_key,
            event_type=event_type,
            status="pending",
            payload=payload,
            attempt_count=0,
            available_at=now,
            created_at=now,
            updated_at=now,
            last_error=None,
        )
        session.add(outbox)

    outbox.attempt_count = (outbox.attempt_count or 0) + 1
    outbox.last_error = str(exc)
    outbox.payload = payload
    outbox.updated_at = now

    classification = retry_policy.classify_failure(retryable=isinstance(exc, OperationalError))
    decision = retry_policy.evaluate(
        attempt=outbox.attempt_count,
        key=event_key,
        classification=classification,
    )

    if classification == FailureClassification.TERMINAL or not decision.should_retry:
        outbox.status = "failed"
        outbox.available_at = now
    else:
        outbox.status = "pending"
        outbox.available_at = now + timedelta(seconds=decision.delay_seconds)

    session.commit()
