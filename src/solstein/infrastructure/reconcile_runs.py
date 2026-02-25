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
from .research_dual_write import JsonValue, load_research_artifacts

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class ReconciliationError(RuntimeError):
    pass


def _as_payload_dict(payload: object) -> dict[str, JsonValue] | None:
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
    if run_id is None and output_dir is None:
        raise ReconciliationError("Either run_id or output_dir must be provided")

    resolved_run_id = run_id
    resolved_output_dir = output_dir
    outbox_record: OutboxRecord | None = None

    if resolved_run_id is not None and resolved_output_dir is None:
        outbox_record = _find_outbox_for_run_id(session, resolved_run_id)
        if outbox_record is None:
            raise ReconciliationError(f"Could not resolve output_dir from outbox payload for run_id {resolved_run_id}")
        payload = _as_payload_dict(outbox_record.payload)
        if payload is None:
            raise ReconciliationError(f"Outbox payload for run_id {resolved_run_id} is not a JSON object")
        output_dir_value = payload.get("output_dir")
        if not isinstance(output_dir_value, str) or not output_dir_value:
            raise ReconciliationError(f"Outbox payload for run_id {resolved_run_id} is missing output_dir")
        resolved_output_dir = Path(output_dir_value)

    if resolved_output_dir is not None and resolved_run_id is None:
        outbox_record = _find_outbox_for_output_dir(session, resolved_output_dir)
        if outbox_record is None:
            raise ReconciliationError(
                f"Could not resolve run_id from outbox payload for output_dir {resolved_output_dir}"
            )
        payload = _as_payload_dict(outbox_record.payload)
        if payload is None:
            raise ReconciliationError(f"Outbox payload for output_dir {resolved_output_dir} is not a JSON object")
        run_id_value = payload.get("run_id")
        if not isinstance(run_id_value, str) or not run_id_value:
            raise ReconciliationError(f"Outbox payload for output_dir {resolved_output_dir} is missing run_id")
        resolved_run_id = run_id_value

    if resolved_run_id is None or resolved_output_dir is None:
        raise ReconciliationError("Unable to resolve both run_id and output_dir")

    stage_report, artifacts = load_research_artifacts(resolved_output_dir)

    run_record = session.execute(
        select(ResearchRunRecord).where(ResearchRunRecord.run_id == resolved_run_id)
    ).scalar_one_or_none()
    run_db_present = run_record is not None

    outbox_records = _outbox_candidates_for_research_runs(session)
    outbox_matches_for_run: list[OutboxRecord] = []
    for record in outbox_records:
        payload = _as_payload_dict(record.payload)
        if payload is None:
            continue
        payload_run_id = payload.get("run_id")
        if isinstance(payload_run_id, str) and payload_run_id == resolved_run_id:
            outbox_matches_for_run.append(record)

    db_artifact_records: list[ResearchArtifactRecord] = []
    if run_record is not None:
        db_artifact_records = list(
            session.execute(select(ResearchArtifactRecord).where(ResearchArtifactRecord.run_id == run_record.id))
            .scalars()
            .all()
        )

    db_artifacts_by_name = {
        row.artifact_name: row for row in sorted(db_artifact_records, key=lambda row: row.artifact_name)
    }

    stage_hashes_obj = stage_report.get("artifact_hashes")
    stage_hashes: dict[str, str] = {}
    if isinstance(stage_hashes_obj, dict):
        stage_hashes = {
            str(name): str(value)
            for name, value in sorted(stage_hashes_obj.items(), key=lambda item: str(item[0]))
            if isinstance(value, str)
        }

    json_artifact_names = sorted(str(name) for name in artifacts.keys())
    db_artifact_names = sorted(db_artifacts_by_name.keys())

    matched: list[dict[str, JsonValue]] = []
    missing_in_db: list[dict[str, JsonValue]] = []
    missing_in_json: list[dict[str, JsonValue]] = []
    mismatched_hash: list[dict[str, JsonValue]] = []

    for artifact_name in json_artifact_names:
        json_hash = stage_hashes.get(artifact_name)
        db_record = db_artifacts_by_name.get(artifact_name)
        if db_record is None:
            missing_in_db.append(
                {
                    "artifact_name": artifact_name,
                    "json_artifact_hash": json_hash,
                }
            )
            continue

        db_hash = _extract_db_artifact_hash(db_record.payload)
        if json_hash == db_hash:
            matched.append(
                {
                    "artifact_name": artifact_name,
                    "json_artifact_hash": json_hash,
                    "db_artifact_hash": db_hash,
                }
            )
            continue

        if json_hash is None and db_hash is None:
            matched.append(
                {
                    "artifact_name": artifact_name,
                    "json_artifact_hash": None,
                    "db_artifact_hash": None,
                }
            )
            continue

        mismatched_hash.append(
            {
                "artifact_name": artifact_name,
                "json_artifact_hash": json_hash,
                "db_artifact_hash": db_hash,
            }
        )

    for artifact_name in db_artifact_names:
        if artifact_name in artifacts:
            continue
        db_hash = _extract_db_artifact_hash(db_artifacts_by_name[artifact_name].payload)
        missing_in_json.append(
            {
                "artifact_name": artifact_name,
                "db_artifact_hash": db_hash,
            }
        )

    matched.sort(key=lambda item: cast("str", item["artifact_name"]))
    missing_in_db.sort(key=lambda item: cast("str", item["artifact_name"]))
    missing_in_json.sort(key=lambda item: cast("str", item["artifact_name"]))
    mismatched_hash.sort(key=lambda item: cast("str", item["artifact_name"]))

    report: dict[str, object] = {
        "run_id": resolved_run_id,
        "output_dir": str(resolved_output_dir),
        "presence": {
            "json_run_present": True,
            "db_run_present": run_db_present,
        },
        "counts": {
            "matched": len(matched),
            "missing_in_db": len(missing_in_db),
            "missing_in_json": len(missing_in_json),
            "mismatched_hash": len(mismatched_hash),
            "json_artifacts": len(json_artifact_names),
            "db_artifacts": len(db_artifact_names),
            "outbox_records": len(outbox_matches_for_run),
        },
        "artifacts": {
            "matched": matched,
            "missing_in_db": missing_in_db,
            "missing_in_json": missing_in_json,
            "mismatched_hash": mismatched_hash,
        },
    }

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
