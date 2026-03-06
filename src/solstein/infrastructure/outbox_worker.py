# pyright: reportMissingTypeStubs=false
# pyright: reportUnknownArgumentType=false
# pyright: reportUnknownVariableType=false

from __future__ import annotations

from loguru import logger
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, cast

from sqlalchemy import select

from solstein.config import Settings
from solstein.infrastructure.database import Base as BaseImported  # type: ignore
from solstein.infrastructure.database import db_manager
from solstein.infrastructure.database_models import OutboxRecord
from solstein.infrastructure.research_dual_write import (
    JsonValue,
    load_research_artifacts,
    persist_research_run_records,
    record_outbox_failure,
)

if TYPE_CHECKING:
    from sqlalchemy.orm import Session



def _load_required_payload(payload: object) -> dict[str, JsonValue]:
    if not isinstance(payload, dict):
        raise ValueError("Outbox payload must be a JSON object")
    return {str(key): value for key, value in payload.items()}


def _process_outbox_record(*, session: Session, record: OutboxRecord) -> None:
    in_progress_time = datetime.now(timezone.utc)
    record.status = "in_progress"
    record.attempt_count = (record.attempt_count or 0) + 1
    record.updated_at = in_progress_time
    record.last_error = None
    session.commit()

    payload = _load_required_payload(record.payload)
    run_id = payload.get("run_id")
    market = payload.get("market")
    seed_company = payload.get("seed_company")
    strict_provenance = payload.get("strict_provenance")
    min_readiness_score = payload.get("min_readiness_score")
    max_contradictions = payload.get("max_contradictions")
    min_total_sources = payload.get("min_total_sources")
    output_dir_value = payload.get("output_dir")

    if not isinstance(run_id, str) or not run_id:
        raise ValueError("Outbox payload missing run_id")
    if not isinstance(market, str) or not market:
        raise ValueError("Outbox payload missing market")
    if not isinstance(seed_company, str) or not seed_company:
        raise ValueError("Outbox payload missing seed_company")
    if not isinstance(strict_provenance, bool):
        raise ValueError("Outbox payload missing strict_provenance")
    if not output_dir_value:
        raise ValueError("Outbox payload missing output_dir")

    output_dir = Path(str(output_dir_value))
    stage_report, artifacts = load_research_artifacts(output_dir)
    if "run_summary" not in artifacts:
        artifacts["run_summary"] = {
            "market": market,
            "seed_company": seed_company,
            "output_dir": str(output_dir),
        }

    _ = persist_research_run_records(
        session=session,
        run_id=run_id,
        market=market,
        seed_company=seed_company,
        strict_provenance=strict_provenance,
        min_readiness_score=(float(min_readiness_score) if isinstance(min_readiness_score, (int, float)) else None),
        max_contradictions=(int(max_contradictions) if isinstance(max_contradictions, (int, float)) else None),
        min_total_sources=(int(min_total_sources) if isinstance(min_total_sources, (int, float)) else None),
        stage_report=stage_report,
        artifacts=artifacts,
    )

    success_time = datetime.now(timezone.utc)
    record.status = "succeeded"
    record.updated_at = success_time
    record.available_at = success_time
    record.last_error = None
    session.commit()


def process_outbox_records(*, limit: int = 25) -> int:
    settings = Settings.load()
    db_manager.settings = settings
    db_manager.init_sync()
    session = db_manager.get_sync_session()
    try:
        engine = session.get_bind()
        BaseImported.metadata.create_all(bind=engine)  # type: ignore
        return process_outbox_records_with_session(session=session, limit=limit)
    finally:
        session.close()
        db_manager.close_sync()


def process_outbox_records_with_session(*, session: Session, limit: int = 25) -> int:
    now = datetime.now(timezone.utc)
    records = (
        session.execute(
            select(OutboxRecord)
            .where(
                OutboxRecord.status.in_(["pending", "failed"]),
                OutboxRecord.available_at <= now,
                OutboxRecord.event_type == "research_run_persist",
            )
            .order_by(OutboxRecord.available_at.asc())
            .limit(limit)
        )
        .scalars()
        .all()
    )

    processed = 0
    for record in records:
        processed += 1
        try:
            _process_outbox_record(session=session, record=record)
        except Exception as exc:
            session.rollback()
            logger.exception(
                "Failed processing outbox record",
                extra={"event_key": record.event_key, "event_type": record.event_type},
            )
            if isinstance(record.payload, dict):
                payload_source = cast("dict[str, JsonValue]", record.payload)
                payload = {str(key): value for key, value in payload_source.items()}
            else:
                payload = {}
            record_outbox_failure(
                session=session,
                event_key=record.event_key,
                event_type=record.event_type,
                payload=payload,
                exc=exc,
            )
    return processed


if __name__ == "__main__":
    _ = process_outbox_records()
