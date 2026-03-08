from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import TYPE_CHECKING, cast

from sqlalchemy import select
from sqlalchemy.exc import OperationalError

from .database_models import OutboxRecord
from .retry_policy import FailureClassification, RetryPolicy

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

JsonValue = dict[str, "JsonValue"] | list["JsonValue"] | str | int | float | bool | None


@dataclass(frozen=True)
class OutboxEvent:
    event_key: str
    event_type: str
    payload: dict[str, JsonValue]


def load_research_artifacts(output_dir: Path) -> tuple[dict[str, JsonValue], dict[str, JsonValue]]:
    stage_report_path = output_dir / "stage_report.json"
    if not stage_report_path.exists():
        raise FileNotFoundError(f"Missing stage report at {stage_report_path}")

    stage_report_obj = json.loads(stage_report_path.read_text(encoding="utf-8"))
    stage_report = cast("dict[str, JsonValue]", stage_report_obj) if isinstance(stage_report_obj, dict) else {}

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
    event: OutboxEvent,
    exc: Exception,
    max_attempts: int = 3,
) -> None:
    now = datetime.now(timezone.utc)
    retry_policy = RetryPolicy(max_attempts=max_attempts)

    outbox = session.execute(select(OutboxRecord).where(OutboxRecord.event_key == event.event_key)).scalar_one_or_none()
    if outbox is None:
        outbox = OutboxRecord(
            event_key=event.event_key,
            event_type=event.event_type,
            status="pending",
            payload=event.payload,
            attempt_count=0,
            available_at=now,
            created_at=now,
            updated_at=now,
            last_error=None,
        )
        session.add(outbox)

    outbox.attempt_count = (outbox.attempt_count or 0) + 1
    outbox.last_error = str(exc)
    outbox.payload = event.payload
    outbox.updated_at = now

    classification = retry_policy.classify_failure(retryable=isinstance(exc, OperationalError))
    decision = retry_policy.evaluate(attempt=outbox.attempt_count, key=event.event_key, classification=classification)

    if classification == FailureClassification.TERMINAL or not decision.should_retry:
        outbox.status = "failed"
        outbox.available_at = now
    else:
        outbox.status = "pending"
        outbox.available_at = now + timedelta(seconds=decision.delay_seconds)

    session.commit()
