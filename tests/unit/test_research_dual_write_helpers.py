import json
from datetime import datetime, timezone
from typing import cast

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.sql.schema import Table

from solstein.infrastructure.database_models import OutboxRecord
from solstein.infrastructure.research_dual_write import JsonValue, record_outbox_failure
from solstein.infrastructure.research_outbox_helpers import OutboxEvent, load_research_artifacts


def test_load_research_artifacts_reads_stage_report_and_known_artifacts(tmp_path) -> None:
    output_dir = tmp_path / "run"
    output_dir.mkdir(parents=True, exist_ok=True)

    stage_report = {"stages": [], "artifact_hashes": {"run_summary.json": "abc"}}
    extracted = [{"name": "Acme"}]
    run_summary = {"market": "Fintech", "seed_company": "Acme"}

    (output_dir / "stage_report.json").write_text(json.dumps(stage_report), encoding="utf-8")
    (output_dir / "extracted.json").write_text(json.dumps(extracted), encoding="utf-8")
    (output_dir / "run_summary.json").write_text(json.dumps(run_summary), encoding="utf-8")

    loaded_stage_report, artifacts = load_research_artifacts(output_dir)

    loaded_hashes = cast("dict[str, JsonValue]", loaded_stage_report["artifact_hashes"])
    extracted_artifacts = cast("list[JsonValue]", artifacts["extracted"])
    first_extracted = cast("dict[str, JsonValue]", extracted_artifacts[0])
    run_summary_artifact = cast("dict[str, JsonValue]", artifacts["run_summary"])

    assert loaded_hashes["run_summary.json"] == "abc"
    assert first_extracted["name"] == "Acme"
    assert run_summary_artifact["seed_company"] == "Acme"


def test_record_outbox_failure_marks_failed_for_terminal_errors() -> None:
    engine = create_engine("sqlite:///:memory:")
    cast(Table, OutboxRecord.__table__).create(bind=engine)

    with Session(engine) as session:
        session.add(
            OutboxRecord(
                event_key="run-1:research_run_persist",
                event_type="research_run_persist",
                status="pending",
                payload={"run_id": "run-1"},
                attempt_count=0,
                available_at=datetime.now(timezone.utc),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                last_error=None,
            )
        )
        session.commit()

        record_outbox_failure(
            session=session,
            event=OutboxEvent(
                event_key="run-1:research_run_persist", event_type="research_run_persist", payload={"run_id": "run-1"}
            ),
            exc=ValueError("terminal"),
            max_attempts=3,
        )

        record = session.query(OutboxRecord).one()
        assert record.status == "failed"
        assert record.attempt_count == 1
        assert record.last_error == "terminal"
