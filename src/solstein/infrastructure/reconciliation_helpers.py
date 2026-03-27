"""Research run reconciliation helpers.

EPIC-020: Extracted from reconcile_research_run function.
Each helper handles one aspect of the reconciliation process.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from .database_models import ResearchArtifactRecord
from .research_dual_write import JsonValue

if TYPE_CHECKING:
    from typing import Any


def resolve_run_and_output_dir(
    session,
    run_id: str | None,
    output_dir: Path | None,
    find_outbox_for_run_id,
    find_outbox_for_output_dir,
    as_payload_dict,
) -> tuple[str, Path, object]:
    """Resolve run_id and output_dir from outbox records."""
    resolved_run_id = run_id
    resolved_output_dir = output_dir
    outbox_record = None

    if resolved_run_id is not None and resolved_output_dir is None:
        outbox_record = find_outbox_for_run_id(session, resolved_run_id)
        if outbox_record is None:
            raise RuntimeError(f"Could not resolve output_dir from outbox payload for run_id {resolved_run_id}")
        payload = as_payload_dict(outbox_record.payload)
        if payload is None:
            raise RuntimeError(f"Outbox payload for run_id {resolved_run_id} is not a JSON object")
        output_dir_value = payload.get("output_dir")
        if not isinstance(output_dir_value, str) or not output_dir_value:
            raise RuntimeError(f"Outbox payload for run_id {resolved_run_id} is missing output_dir")
        resolved_output_dir = Path(output_dir_value)

    if resolved_output_dir is not None and resolved_run_id is None:
        outbox_record = find_outbox_for_output_dir(session, resolved_output_dir)
        if outbox_record is None:
            raise RuntimeError(f"Could not resolve run_id from outbox payload for output_dir {resolved_output_dir}")
        payload = as_payload_dict(outbox_record.payload)
        if payload is None:
            raise RuntimeError(f"Outbox payload for output_dir {resolved_output_dir} is not a JSON object")
        run_id_value = payload.get("run_id")
        if not isinstance(run_id_value, str) or not run_id_value:
            raise RuntimeError(f"Outbox payload for output_dir {resolved_output_dir} is missing run_id")
        resolved_run_id = run_id_value

    if resolved_run_id is None or resolved_output_dir is None:
        raise RuntimeError("Unable to resolve both run_id and output_dir")

    return resolved_run_id, resolved_output_dir, outbox_record


def extract_artifact_hashes(stage_report: dict[str, Any]) -> dict[str, str]:
    """Extract and normalize artifact hashes from stage report."""
    stage_hashes_obj = stage_report.get("artifact_hashes")
    if isinstance(stage_hashes_obj, dict):
        return {
            str(name): str(value)
            for name, value in sorted(stage_hashes_obj.items(), key=lambda item: str(item[0]))
            if isinstance(value, str)
        }
    return {}


def extract_db_artifact_hash(payload: object) -> str | None:
    """Extract artifact hash from database payload."""
    import json

    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError:
            pass
    if not isinstance(payload, dict):
        return None
    wrapped_hash = payload.get("artifact_hash")
    if isinstance(wrapped_hash, str) and wrapped_hash:
        return wrapped_hash
    return None


def compare_artifacts(
    json_artifacts: dict[str, Any],
    db_artifacts_by_name: dict[str, ResearchArtifactRecord],
    stage_hashes: dict[str, str],
) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    """Compare JSON artifacts against database artifacts.

    Returns:
        Tuple of (matched, missing_in_db, missing_in_json, mismatched_hash)
    """
    matched: list[dict[str, JsonValue]] = []
    missing_in_db: list[dict[str, JsonValue]] = []
    missing_in_json: list[dict[str, JsonValue]] = []
    mismatched_hash: list[dict[str, JsonValue]] = []

    json_artifact_names = sorted(str(name) for name in json_artifacts.keys())
    db_artifact_names = sorted(db_artifacts_by_name.keys())

    # Check JSON artifacts against DB
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

        db_hash = extract_db_artifact_hash(db_record.payload)

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

    # Check DB artifacts against JSON
    for artifact_name in db_artifact_names:
        if artifact_name in json_artifacts:
            continue
        db_hash = extract_db_artifact_hash(db_artifacts_by_name[artifact_name].payload)
        missing_in_json.append(
            {
                "artifact_name": artifact_name,
                "db_artifact_hash": db_hash,
            }
        )

    # Sort results
    matched.sort(key=lambda item: str(item["artifact_name"]))
    missing_in_db.sort(key=lambda item: str(item["artifact_name"]))
    missing_in_json.sort(key=lambda item: str(item["artifact_name"]))
    mismatched_hash.sort(key=lambda item: str(item["artifact_name"]))

    return matched, missing_in_db, missing_in_json, mismatched_hash


def build_reconciliation_report(
    resolved_run_id: str,
    resolved_output_dir: Path,
    run_db_present: bool,
    matched: list[dict],
    missing_in_db: list[dict],
    missing_in_json: list[dict],
    mismatched_hash: list[dict],
    json_artifact_names: list[str],
    db_artifact_names: list[str],
    outbox_matches_count: int,
) -> dict[str, object]:
    """Build reconciliation report dictionary."""
    return {
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
            "outbox_records": outbox_matches_count,
        },
        "artifacts": {
            "matched": matched,
            "missing_in_db": missing_in_db,
            "missing_in_json": missing_in_json,
            "mismatched_hash": mismatched_hash,
        },
    }
