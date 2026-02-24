from __future__ import annotations

# pyright: reportMissingTypeStubs=false
import json
import logging
from datetime import UTC, datetime, timedelta
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

logger = logging.getLogger(__name__)

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
    now = datetime.now(UTC)
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
            or to_status not in ALLOWED_CONTRADICTION_TRANSITIONS.get(from_status, set())
        ):
            raise ContradictionLifecycleError(
                "Invalid contradiction status transition",
                code="CONTRADICTION_INVALID_TRANSITION",
                contradiction_id=str(contradiction_id),
                from_status=from_status,
                to_status=to_status,
                allowed_transitions=ALLOWED_CONTRADICTION_TRANSITIONS,
            )

        contradiction.status = to_status
        contradiction.updated_at = now
        contradiction.resolved_at = now if to_status == "resolved" else None
        contradiction.ignored_at = now if to_status == "ignored" else None
        session.add(
            ContradictionTransitionRecord(
                contradiction_id=contradiction.id,
                from_status=from_status,
                to_status=to_status,
                changed_at=now,
                changed_by=changed_by,
                reason=reason,
            )
        )

    return contradiction


def _read_json_file(path: Path) -> JsonValue:
    try:
        value: JsonValue = json.loads(path.read_text(encoding="utf-8"))
        return value
    except Exception:
        logger.exception("Failed to read JSON artifact at %s", path)
        raise


def _coerce_float(value: JsonValue, *, default: float = 0.0) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    return default


def _coerce_int(value: JsonValue, *, default: int = 0) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    return default


def load_research_artifacts(
    output_dir: Path,
) -> tuple[dict[str, JsonValue], dict[str, JsonValue]]:
    if not output_dir.exists():
        raise FileNotFoundError(f"Output directory does not exist: {output_dir}")
    if not output_dir.is_dir():
        raise NotADirectoryError(f"Output directory is not a directory: {output_dir}")

    stage_report_path = output_dir / "stage_report.json"
    if not stage_report_path.exists():
        raise FileNotFoundError(f"Missing stage_report.json in {output_dir}")

    stage_report_value = _read_json_file(stage_report_path)
    if not isinstance(stage_report_value, dict):
        raise ValueError("stage_report.json must contain a JSON object")
    stage_report: dict[str, JsonValue] = cast("dict[str, JsonValue]", stage_report_value)

    artifacts: dict[str, JsonValue] = {
        "discovery_candidates": _read_json_file(output_dir / "discovery_candidates.json"),
        "extracted": _read_json_file(output_dir / "extracted.json"),
        "provenance": _read_json_file(output_dir / "provenance_report.json"),
        "contradictions": _read_json_file(output_dir / "contradictions_report.json"),
        "evidence_readiness": _read_json_file(output_dir / "evidence_readiness.json"),
        "scored": _read_json_file(output_dir / "scored.json"),
        "market_analysis": _read_json_file(output_dir / "market_analysis.json"),
        "stage_report": stage_report,
    }

    run_summary_path = output_dir / "run_summary.json"
    if run_summary_path.exists():
        artifacts["run_summary"] = _read_json_file(run_summary_path)

    return stage_report, artifacts


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
    output_dir: str | None = None
    run_summary = artifacts.get("run_summary")
    if isinstance(run_summary, dict):
        output_dir_value = run_summary.get("output_dir")
        if output_dir_value is not None:
            output_dir = str(output_dir_value)

    return {
        "run_id": run_id,
        "event_type": event_type,
        "market": market,
        "seed_company": seed_company,
        "strict_provenance": strict_provenance,
        "min_readiness_score": min_readiness_score,
        "max_contradictions": max_contradictions,
        "min_total_sources": min_total_sources,
        "output_dir": output_dir,
    }


def record_outbox_failure(
    *,
    session: Session,
    event_key: str,
    event_type: str,
    payload: dict[str, JsonValue],
    exc: Exception,
) -> None:
    failed_time = datetime.now(UTC)
    retryable = isinstance(exc, (TimeoutError, ConnectionError, OperationalError))
    classification = FailureClassification.RETRYABLE if retryable else FailureClassification.TERMINAL
    retry_policy = RetryPolicy()
    failed_outbox = session.execute(
        select(OutboxRecord).where(OutboxRecord.event_key == event_key)
    ).scalar_one_or_none()
    attempt_count = failed_outbox.attempt_count if failed_outbox is not None else 1
    if attempt_count < 1:
        attempt_count = 1
    decision = retry_policy.evaluate(attempt=attempt_count, key=event_key, classification=classification)
    delay_seconds = decision.delay_seconds
    available_at = failed_time + timedelta(seconds=delay_seconds) if decision.should_retry else failed_time
    last_error = {
        "error_type": type(exc).__name__,
        "message": str(exc),
        "recorded_at": failed_time.isoformat(),
        "retryable": classification.is_retryable,
        "should_retry": decision.should_retry,
        "delay_seconds": delay_seconds,
        "attempt_count": attempt_count,
    }
    if failed_outbox is None:
        failed_outbox = OutboxRecord(
            event_key=event_key,
            event_type=event_type,
            status="failed",
            payload=payload,
            attempt_count=attempt_count,
            available_at=available_at,
            created_at=failed_time,
            updated_at=failed_time,
            last_error=last_error,
        )
        session.add(failed_outbox)
    else:
        failed_outbox.status = "failed"
        failed_outbox.attempt_count = attempt_count
        failed_outbox.updated_at = failed_time
        failed_outbox.available_at = available_at
        failed_outbox.last_error = last_error
    session.commit()


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
    existing = session.execute(select(ResearchRunRecord).where(ResearchRunRecord.run_id == run_id)).scalar_one_or_none()
    if existing is not None:
        _ = session.query(ResearchStageRecord).filter(ResearchStageRecord.run_id == existing.id).delete()
        _ = session.query(ResearchArtifactRecord).filter(ResearchArtifactRecord.run_id == existing.id).delete()
        _ = session.query(SourceDocumentRecord).filter(SourceDocumentRecord.run_id == existing.id).delete()
        _ = session.query(MetricObservationRecord).filter(MetricObservationRecord.run_id == existing.id).delete()
        _ = session.query(EvidenceReadinessRecord).filter(EvidenceReadinessRecord.run_id == existing.id).delete()
        _ = session.query(ContradictionRecord).filter(ContradictionRecord.run_id == existing.id).delete()
        session.delete(existing)
        session.flush()

    run = ResearchRunRecord(
        run_id=run_id,
        market=market,
        seed_company=seed_company,
        status="completed",
        strict_provenance=strict_provenance,
        min_readiness_score=min_readiness_score,
        max_contradictions=max_contradictions,
        min_total_sources=min_total_sources,
        summary=artifacts.get("run_summary"),
        created_at=datetime.now(UTC),
    )
    session.add(run)
    session.flush()

    run_pk = session.execute(select(ResearchRunRecord.id).where(ResearchRunRecord.run_id == run_id)).scalar_one()

    stages: list[dict[str, JsonValue]] = []
    stages_obj = stage_report.get("stages")
    if isinstance(stages_obj, list):
        for stage in stages_obj:
            if isinstance(stage, dict):
                stages.append(cast("dict[str, JsonValue]", stage))

    for idx, stage in enumerate(stages):
        stage_name = str(stage.get("stage", f"stage_{idx}"))
        status = stage.get("status")
        session.add(
            ResearchStageRecord(
                run_id=run.id,
                stage_name=stage_name,
                stage_order=idx,
                status=str(status) if status is not None else None,
                metrics=stage,
                created_at=datetime.now(UTC),
            )
        )

    artifact_hashes_obj = stage_report.get("artifact_hashes", {})
    artifact_hashes: dict[str, str] = {}
    if isinstance(artifact_hashes_obj, dict):
        artifact_hashes = cast("dict[str, str]", artifact_hashes_obj)

    for name, payload in artifacts.items():
        artifact_hash = artifact_hashes.get(name)
        persisted_payload: object
        if isinstance(artifact_hash, str) and artifact_hash:
            persisted_payload = {
                "artifact_hash": artifact_hash,
                "artifact": payload,
            }
        else:
            persisted_payload = payload

        session.add(
            ResearchArtifactRecord(
                run_id=run.id,
                artifact_name=name,
                artifact_path=None,
                payload=persisted_payload,
                created_at=datetime.now(UTC),
            )
        )

    extracted = artifacts.get("extracted", [])
    if isinstance(extracted, list):
        for company in extracted:
            if not isinstance(company, dict):
                continue
            company_payload = cast("dict[str, JsonValue]", company)
            company_id = str(company_payload.get("id", "unknown"))

            source_links = company_payload.get("source_links", [])
            if isinstance(source_links, list):
                for source_url in source_links:
                    if not isinstance(source_url, str):
                        continue
                    canonical = canonicalize_url(source_url)
                    parsed = urlparse(canonical)
                    observed_time = datetime.now(UTC)
                    session.add(
                        SourceDocumentRecord(
                            run_id=run.id,
                            company_id=company_id,
                            source_url=canonical,
                            source_domain=(parsed.netloc.lower() if parsed.netloc else None),
                            source_type="web",
                            observed_at=observed_time,
                            status="observed",
                            fetched_at=observed_time,
                            content_hash=None,
                            extract_hash=None,
                        )
                    )

            observations = company_payload.get("metric_observations", {})
            if isinstance(observations, dict):
                for metric_key, rows in observations.items():
                    if not isinstance(rows, list):
                        continue
                    for row in rows:
                        if not isinstance(row, dict):
                            continue
                        row_payload = cast("dict[str, JsonValue]", row)
                        raw_value = row_payload.get("value")
                        metric_value: float | None
                        if isinstance(raw_value, (int, float)):
                            metric_value = float(raw_value)
                        else:
                            metric_value = None
                        session.add(
                            MetricObservationRecord(
                                run_id=run.id,
                                company_id=company_id,
                                metric_key=str(metric_key),
                                metric_value=metric_value,
                                metric_value_raw=raw_value,
                                source_url=(
                                    str(row_payload.get("source")) if row_payload.get("source") is not None else None
                                ),
                                created_at=datetime.now(UTC),
                            )
                        )

    readiness = artifacts.get("evidence_readiness", {})
    if isinstance(readiness, dict):
        readiness_payload = cast("dict[str, JsonValue]", readiness)
        company_reports = readiness_payload.get("company_reports", [])
        if isinstance(company_reports, list):
            for report in company_reports:
                if not isinstance(report, dict):
                    continue
                report_payload = cast("dict[str, JsonValue]", report)
                session.add(
                    EvidenceReadinessRecord(
                        run_id=run.id,
                        company_id=str(report_payload.get("company_id", "unknown")),
                        company_name=str(report_payload.get("company_name", "unknown")),
                        readiness_score=_coerce_float(report_payload.get("readiness_score"), default=0.0),
                        readiness_level=str(report_payload.get("readiness_level", "unknown")),
                        source_count=_coerce_int(report_payload.get("source_count"), default=0),
                        source_domain_count=int(_coerce_int(report_payload.get("source_domain_count"), default=0)),
                        metric_source_coverage=_coerce_float(report_payload.get("metric_source_coverage"), default=0.0),
                        metric_explainability=_coerce_float(report_payload.get("metric_explainability"), default=0.0),
                        unsupported_metrics=_coerce_int(report_payload.get("unsupported_metrics"), default=0),
                        created_at=datetime.now(UTC),
                    )
                )

    contradictions = artifacts.get("contradictions", {})
    if isinstance(contradictions, dict):
        for company_id, rows in contradictions.items():
            if not isinstance(rows, list):
                continue
            for row in rows:
                if not isinstance(row, dict):
                    continue
                row_payload = cast("dict[str, JsonValue]", row)
                created_at = datetime.now(UTC)
                session.add(
                    ContradictionRecord(
                        run_id=run.id,
                        company_id=str(company_id),
                        metric_key=str(row_payload.get("metric", "unknown")),
                        contradiction_type=str(row_payload.get("type", "unknown")),
                        details=row_payload,
                        status="open",
                        updated_at=created_at,
                        resolved_at=None,
                        ignored_at=None,
                        created_at=created_at,
                    )
                )

    return run_pk


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
    now = datetime.now(UTC)
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
    else:
        outbox.status = "pending"
        outbox.payload = payload
        outbox.updated_at = now
        outbox.last_error = None
        outbox.available_at = now

    session.commit()

    in_progress_time = datetime.now(UTC)
    outbox = session.execute(select(OutboxRecord).where(OutboxRecord.event_key == event_key)).scalar_one()
    outbox.status = "in_progress"
    outbox.attempt_count = (outbox.attempt_count or 0) + 1
    outbox.updated_at = in_progress_time
    outbox.last_error = None
    session.commit()

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
        success_time = datetime.now(UTC)
        outbox.status = "succeeded"
        outbox.updated_at = success_time
        outbox.available_at = success_time
        outbox.last_error = None
        session.commit()
        return run_pk
    except Exception as exc:
        session.rollback()
        logger.exception("Failed to persist research run", extra={"run_id": run_id})
        record_outbox_failure(
            session=session,
            event_key=event_key,
            event_type=event_type,
            payload=payload,
            exc=exc,
        )
        raise
