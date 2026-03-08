"""Research run persistence helpers.

EPIC-020: Extracted from persist_research_run_records function.
Each function handles persisting one type of record.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import select

from solstein.research.sources import canonicalize_url

from .database_models import (
    ContradictionRecord,
    EvidenceReadinessRecord,
    MetricObservationRecord,
    ResearchArtifactRecord,
    ResearchRunRecord,
    ResearchStageRecord,
    SourceDocumentRecord,
)

if TYPE_CHECKING:
    from typing import Any

    from sqlalchemy.orm import Session

    from .research_dual_write import PersistRunPayload


JsonValue = dict[str, "JsonValue"] | list["JsonValue"] | str | int | float | bool | None


def _coerce_float(value: Any, default: float = 0.0) -> float:
    """Coerce value to float."""
    if isinstance(value, (int, float)):
        return float(value)
    return default


def _coerce_int(value: Any, default: int = 0) -> int:
    """Coerce value to int."""
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    return default


def delete_existing_run(session: Session, run_id: str) -> None:
    """Delete existing run and all related records."""
    existing = session.execute(select(ResearchRunRecord).where(ResearchRunRecord.run_id == run_id)).scalar_one_or_none()

    if existing is not None:
        # Delete related records
        session.query(ResearchStageRecord).filter(ResearchStageRecord.run_id == existing.id).delete()
        session.query(ResearchArtifactRecord).filter(ResearchArtifactRecord.run_id == existing.id).delete()
        session.query(SourceDocumentRecord).filter(SourceDocumentRecord.run_id == existing.id).delete()
        session.query(MetricObservationRecord).filter(MetricObservationRecord.run_id == existing.id).delete()
        session.query(EvidenceReadinessRecord).filter(EvidenceReadinessRecord.run_id == existing.id).delete()
        session.query(ContradictionRecord).filter(ContradictionRecord.run_id == existing.id).delete()

        session.delete(existing)
        session.flush()


def create_research_run(
    session: Session,
    payload: PersistRunPayload,
) -> ResearchRunRecord:
    """Create and persist ResearchRunRecord."""
    run = ResearchRunRecord(
        run_id=payload.run_id,
        market=payload.market,
        seed_company=payload.seed_company,
        status="completed",
        strict_provenance=payload.strict_provenance,
        min_readiness_score=payload.min_readiness_score,
        max_contradictions=payload.max_contradictions,
        min_total_sources=payload.min_total_sources,
        summary=payload.artifacts.get("run_summary"),
        created_at=datetime.now(timezone.utc),
    )
    session.add(run)
    session.flush()
    return run


def persist_stage_records(
    session: Session,
    run: ResearchRunRecord,
    stages: list[dict[str, JsonValue]],
) -> None:
    """Persist ResearchStageRecords for each stage."""
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
                created_at=datetime.now(timezone.utc),
            )
        )


def persist_artifact_records(
    session: Session,
    run: ResearchRunRecord,
    artifacts: dict[str, JsonValue],
    artifact_hashes: dict[str, str],
) -> None:
    """Persist ResearchArtifactRecords for each artifact."""
    for name, payload in artifacts.items():
        artifact_hash = artifact_hashes.get(name)

        if isinstance(artifact_hash, str) and artifact_hash:
            persisted_payload: object = {
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
                created_at=datetime.now(timezone.utc),
            )
        )


def persist_source_documents(
    session: Session,
    run: ResearchRunRecord,
    extracted: list[JsonValue],
) -> None:
    """Persist SourceDocumentRecords for each company."""
    from urllib.parse import urlparse

    for company in extracted:
        if not isinstance(company, dict):
            continue

        company_payload = company
        company_id = str(company_payload.get("id", "unknown"))
        source_links = company_payload.get("source_links", [])

        if isinstance(source_links, list):
            for source_url in source_links:
                if not isinstance(source_url, str):
                    continue

                canonical = canonicalize_url(source_url)
                parsed = urlparse(canonical)
                observed_time = datetime.now(timezone.utc)

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


def persist_metric_observations(
    session: Session,
    run: ResearchRunRecord,
    extracted: list[JsonValue],
) -> None:
    """Persist MetricObservationRecords for each company."""
    seen_keys: set[tuple[str, str, str | None, float | None]] = set()

    for company in extracted:
        if not isinstance(company, dict):
            continue

        company_payload = company
        company_id = str(company_payload.get("id", "unknown"))
        observations = company_payload.get("metric_observations", {})

        if isinstance(observations, dict):
            for metric_key, rows in observations.items():
                if not isinstance(rows, list):
                    continue

                for row in rows:
                    if not isinstance(row, dict):
                        continue

                    raw_value = row.get("value")
                    if isinstance(raw_value, (int, float)):
                        metric_value = float(raw_value)
                    else:
                        metric_value = None

                    source_obj = row.get("source")
                    source_url = str(source_obj) if source_obj is not None else None
                    dedup_key = (company_id, str(metric_key), source_url, metric_value)
                    if dedup_key in seen_keys:
                        continue
                    seen_keys.add(dedup_key)

                    session.add(
                        MetricObservationRecord(
                            run_id=run.id,
                            company_id=company_id,
                            metric_key=str(metric_key),
                            metric_value=metric_value,
                            metric_value_raw=raw_value,
                            source_url=source_url,
                            created_at=datetime.now(timezone.utc),
                        )
                    )


def persist_evidence_readiness(
    session: Session,
    run: ResearchRunRecord,
    readiness: dict[str, JsonValue],
) -> None:
    """Persist EvidenceReadinessRecords."""
    company_reports = readiness.get("company_reports", [])

    if isinstance(company_reports, list):
        for report in company_reports:
            if not isinstance(report, dict):
                continue

            session.add(
                EvidenceReadinessRecord(
                    run_id=run.id,
                    company_id=str(report.get("company_id", "unknown")),
                    company_name=str(report.get("company_name", "unknown")),
                    readiness_score=_coerce_float(report.get("readiness_score"), default=0.0),
                    readiness_level=str(report.get("readiness_level", "unknown")),
                    source_count=_coerce_int(report.get("source_count"), default=0),
                    source_domain_count=int(_coerce_int(report.get("source_domain_count"), default=0)),
                    metric_source_coverage=_coerce_float(report.get("metric_source_coverage"), default=0.0),
                    metric_explainability=_coerce_float(report.get("metric_explainability"), default=0.0),
                    unsupported_metrics=_coerce_int(report.get("unsupported_metrics"), default=0),
                    created_at=datetime.now(timezone.utc),
                )
            )


def persist_contradictions(
    session: Session,
    run: ResearchRunRecord,
    contradictions: dict[str, JsonValue],
) -> None:
    """Persist ContradictionRecords."""
    for company_id, rows in contradictions.items():
        if not isinstance(rows, list):
            continue

        for row in rows:
            if not isinstance(row, dict):
                continue

            created_at = datetime.now(timezone.utc)

            session.add(
                ContradictionRecord(
                    run_id=run.id,
                    company_id=str(company_id),
                    metric_key=str(row.get("metric", "unknown")),
                    contradiction_type=str(row.get("type", "unknown")),
                    details=row,
                    status="open",
                    updated_at=created_at,
                    resolved_at=None,
                    ignored_at=None,
                    created_at=created_at,
                )
            )
