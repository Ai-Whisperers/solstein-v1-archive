from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, cast

from loguru import logger
from sqlalchemy import select

from solstein.config import Settings
from solstein.infrastructure.database import db_manager
from solstein.research.hashing import canonical_json_dumps

from .database_models import OutboxRecord, ResearchArtifactRecord, ResearchRunRecord
from .research_dual_write import JsonValue
from .research_outbox_helpers import load_research_artifacts

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class ReconciliationError(RuntimeError):
    pass


def _as_payload_dict(payload: object) -> dict[str, JsonValue] | None:
    import json
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError:
            pass
    if not isinstance(payload, dict):
        return None
    return {str(key): value for key, value in payload.items()}


def _outbox_candidates_for_research_runs(session: Session) -> list[OutboxRecord]:
    return list(
        session.execute(select(OutboxRecord).where(OutboxRecord.event_type == "research_run_persist")).scalars().all()
    )


def _select_latest_outbox(records: list[OutboxRecord]) -> OutboxRecord | None:
    if not records:
        return None
    records_sorted = sorted(records, key=lambda item: (item.updated_at, item.created_at))
    return records_sorted[-1]


def _find_outbox_for_run_id(session: Session, run_id: str) -> OutboxRecord | None:
    matches: list[OutboxRecord] = []
    for record in _outbox_candidates_for_research_runs(session):
        payload = _as_payload_dict(record.payload)
        if payload is None:
            continue
        payload_run_id = payload.get("run_id")
        if isinstance(payload_run_id, str) and payload_run_id == run_id:
            matches.append(record)
    return _select_latest_outbox(matches)


def _find_outbox_for_output_dir(session: Session, output_dir: Path) -> OutboxRecord | None:
    expected = str(output_dir)
    matches: list[OutboxRecord] = []
    for record in _outbox_candidates_for_research_runs(session):
        payload = _as_payload_dict(record.payload)
        if payload is None:
            continue
        payload_output_dir = payload.get("output_dir")
        if isinstance(payload_output_dir, str) and payload_output_dir == expected:
            matches.append(record)
    return _select_latest_outbox(matches)


def _extract_db_artifact_hash(payload: object) -> str | None:
    if not isinstance(payload, dict):
        return None
    wrapped_hash = payload.get("artifact_hash")
    if isinstance(wrapped_hash, str) and wrapped_hash:
        return wrapped_hash
    return None


def _write_reconciliation_report(*, output_dir: Path, report: object) -> Path:
    report_path = output_dir / "reconciliation_report.json"
    _ = report_path.write_text(canonical_json_dumps(report) + "\n", encoding="utf-8")
    return report_path


def reconcile_research_run(
    *,
    session: Session,
    run_id: str | None = None,
    output_dir: Path | None = None,
) -> dict[str, object]:
    """Reconcile JSON research artifacts against persisted research records.

    EPIC-020: Refactored from 170-line function to use helper functions.
    """
    from .reconciliation_helpers import (
        build_reconciliation_report,
        compare_artifacts,
        extract_artifact_hashes,
        resolve_run_and_output_dir,
    )

    # Resolve run_id and output_dir
    resolved_run_id, resolved_output_dir, outbox_record = resolve_run_and_output_dir(
        session, run_id, output_dir,
        _find_outbox_for_run_id, _find_outbox_for_output_dir, _as_payload_dict
    )

    # Load artifacts
    stage_report, artifacts = load_research_artifacts(resolved_output_dir)

    # Query database records
    run_record = session.execute(
        select(ResearchRunRecord).where(ResearchRunRecord.run_id == resolved_run_id)
    ).scalar_one_or_none()
    run_db_present = run_record is not None

    # Get outbox matches
    outbox_records = _outbox_candidates_for_research_runs(session)
    outbox_matches_for_run: list[OutboxRecord] = []
    for record in outbox_records:
        payload = _as_payload_dict(record.payload)
        if payload is None:
            continue
        payload_run_id = payload.get("run_id")
        if isinstance(payload_run_id, str) and payload_run_id == resolved_run_id:
            outbox_matches_for_run.append(record)

    # Get DB artifact records
    db_artifact_records: list[ResearchArtifactRecord] = []
    if run_record is not None:
        db_artifact_records = list(
            session.execute(select(ResearchArtifactRecord).where(ResearchArtifactRecord.run_id == run_record.id))
            .scalars()
            .all()
        )

    # Build artifact name mappings
    db_artifacts_by_name = {
        row.artifact_name: row for row in sorted(db_artifact_records, key=lambda row: row.artifact_name)
    }

    # Extract artifact hashes
    stage_hashes = extract_artifact_hashes(stage_report)

    # Compare artifacts
    json_artifact_names = sorted(str(name) for name in artifacts.keys())
    db_artifact_names = sorted(db_artifacts_by_name.keys())

    matched, missing_in_db, missing_in_json, mismatched_hash = compare_artifacts(
        artifacts, db_artifacts_by_name, stage_hashes
    )

    # Build and write report
    report = build_reconciliation_report(
        resolved_run_id, resolved_output_dir, run_db_present,
        matched, missing_in_db, missing_in_json, mismatched_hash,
        json_artifact_names, db_artifact_names, len(outbox_matches_for_run)
    )

    _ = _write_reconciliation_report(output_dir=resolved_output_dir, report=report)
    return report

def reconcile_research_run_with_configured_db(
    *,
    run_id: str | None = None,
    output_dir: Path | None = None,
) -> dict[str, object]:
    settings = Settings.load()
    db_manager.settings = settings
    db_manager.init_sync()
    session = db_manager.get_sync_session()
    try:
        return reconcile_research_run(
            session=session,
            run_id=run_id,
            output_dir=output_dir,
        )
    finally:
        session.close()
        db_manager.close_sync()


def _parse_args() -> tuple[str | None, Path | None]:
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Reconcile JSON research artifacts against persisted research records and write reconciliation_report.json"
        )
    )
    _ = parser.add_argument("--run-id", dest="run_id", required=False)
    _ = parser.add_argument("--output-dir", dest="output_dir", required=False)
    args = parser.parse_args()
    run_id = cast("str | None", args.run_id)
    output_dir_value = cast("str | None", args.output_dir)
    output_dir = Path(output_dir_value) if output_dir_value is not None else None
    return run_id, output_dir


def main() -> int:
    run_id, output_dir = _parse_args()
    report = reconcile_research_run_with_configured_db(
        run_id=run_id,
        output_dir=output_dir,
    )
    logger.info(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
