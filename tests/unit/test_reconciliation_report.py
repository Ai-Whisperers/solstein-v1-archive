from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import TYPE_CHECKING

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

if TYPE_CHECKING:
    from pathlib import Path

from solstein.infrastructure.database import Base
from solstein.infrastructure.database_models import (
    OutboxRecord,
    ResearchArtifactRecord,
    ResearchRunRecord,
)
from solstein.infrastructure.reconcile_runs import (
    ReconciliationError,
    reconcile_research_run,
)
from solstein.research.hashing import canonical_json_dumps


def _write_required_artifacts(
    output_dir: Path,
    *,
    artifact_hashes: dict[str, str],
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / "discovery_candidates.json").write_text("[]", encoding="utf-8")
    (output_dir / "extracted.json").write_text("[]", encoding="utf-8")
    (output_dir / "provenance_report.json").write_text("{}", encoding="utf-8")
    (output_dir / "contradictions_report.json").write_text("{}", encoding="utf-8")
    (output_dir / "evidence_readiness.json").write_text("{}", encoding="utf-8")
    (output_dir / "scored.json").write_text("[]", encoding="utf-8")
    (output_dir / "market_analysis.json").write_text("{}", encoding="utf-8")

    stage_report = {
        "market": "Test Market",
        "seed_company": "Test Seed",
        "stages": [],
        "artifact_hashes": artifact_hashes,
    }
    (output_dir / "stage_report.json").write_text(
        json.dumps(stage_report, indent=2),
        encoding="utf-8",
    )

    run_summary = {
        "market": "Test Market",
        "seed_company": "Test Seed",
        "output_dir": str(output_dir),
    }
    (output_dir / "run_summary.json").write_text(
        json.dumps(run_summary, indent=2),
        encoding="utf-8",
    )


def _create_session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return Session(engine)


def test_reconcile_research_run_by_run_id_writes_report(tmp_path: Path) -> None:
    output_dir = tmp_path / "reconcile"
    artifact_hashes = {
        "discovery_candidates": "a" * 64,
        "extracted": "b" * 64,
        "provenance": "c" * 64,
        "contradictions": "d" * 64,
        "evidence_readiness": "e" * 64,
        "scored": "f" * 64,
        "market_analysis": "1" * 64,
        "stage_report": "2" * 64,
        "run_summary": "3" * 64,
    }
    _write_required_artifacts(output_dir, artifact_hashes=artifact_hashes)

    with _create_session() as session:
        run_id = "run-reconcile-001"
        run = ResearchRunRecord(
            run_id=run_id,
            market="Test Market",
            seed_company="Test Seed",
            status="completed",
            strict_provenance=False,
            summary={"output_dir": str(output_dir)},
            created_at=datetime.now(UTC),
        )
        session.add(run)
        session.flush()

        session.add_all(
            [
                ResearchArtifactRecord(
                    run_id=run.id,
                    artifact_name="discovery_candidates",
                    payload={
                        "artifact_hash": "a" * 64,
                        "artifact": [],
                    },
                    created_at=datetime.now(UTC),
                ),
                ResearchArtifactRecord(
                    run_id=run.id,
                    artifact_name="extracted",
                    payload={
                        "artifact_hash": "x" * 64,
                        "artifact": [],
                    },
                    created_at=datetime.now(UTC),
                ),
                ResearchArtifactRecord(
                    run_id=run.id,
                    artifact_name="db_only",
                    payload={
                        "artifact_hash": "z" * 64,
                        "artifact": {},
                    },
                    created_at=datetime.now(UTC),
                ),
            ]
        )

        session.add(
            OutboxRecord(
                event_key=f"{run_id}:research_run_persist",
                event_type="research_run_persist",
                status="succeeded",
                payload={
                    "run_id": run_id,
                    "output_dir": str(output_dir),
                },
                attempt_count=1,
                available_at=datetime.now(UTC),
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
                last_error=None,
            )
        )
        session.commit()

        report = reconcile_research_run(session=session, run_id=run_id)

    assert report["run_id"] == run_id
    assert report["output_dir"] == str(output_dir)
    counts = report["counts"]
    assert isinstance(counts, dict)
    assert counts["matched"] == 1
    assert counts["missing_in_db"] == 7
    assert counts["missing_in_json"] == 1
    assert counts["mismatched_hash"] == 1

    report_path = output_dir / "reconciliation_report.json"
    assert report_path.exists()
    assert report_path.read_text(encoding="utf-8") == canonical_json_dumps(report) + "\n"


def test_reconcile_research_run_by_output_dir_resolves_run_id(tmp_path: Path) -> None:
    output_dir = tmp_path / "reconcile-output-dir"
    artifact_hashes = {
        "discovery_candidates": "a" * 64,
        "extracted": "b" * 64,
        "provenance": "c" * 64,
        "contradictions": "d" * 64,
        "evidence_readiness": "e" * 64,
        "scored": "f" * 64,
        "market_analysis": "1" * 64,
        "stage_report": "2" * 64,
        "run_summary": "3" * 64,
    }
    _write_required_artifacts(output_dir, artifact_hashes=artifact_hashes)

    with _create_session() as session:
        run_id = "run-reconcile-002"
        run = ResearchRunRecord(
            run_id=run_id,
            market="Test Market",
            seed_company="Test Seed",
            status="completed",
            strict_provenance=False,
            summary={"output_dir": str(output_dir)},
            created_at=datetime.now(UTC),
        )
        session.add(run)
        session.flush()

        for artifact_name, artifact_hash in artifact_hashes.items():
            session.add(
                ResearchArtifactRecord(
                    run_id=run.id,
                    artifact_name=artifact_name,
                    payload={"artifact_hash": artifact_hash, "artifact": {}},
                    created_at=datetime.now(UTC),
                )
            )

        session.add(
            OutboxRecord(
                event_key=f"{run_id}:research_run_persist",
                event_type="research_run_persist",
                status="succeeded",
                payload={
                    "run_id": run_id,
                    "output_dir": str(output_dir),
                },
                attempt_count=1,
                available_at=datetime.now(UTC),
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
                last_error=None,
            )
        )
        session.commit()

        report = reconcile_research_run(session=session, output_dir=output_dir)

    assert report["run_id"] == run_id
    counts = report["counts"]
    assert isinstance(counts, dict)
    assert counts["matched"] == 9
    assert counts["missing_in_db"] == 0
    assert counts["missing_in_json"] == 0
    assert counts["mismatched_hash"] == 0


def test_reconcile_research_run_raises_when_run_id_not_in_outbox(
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "reconcile-error"
    artifact_hashes = {
        "discovery_candidates": "a" * 64,
        "extracted": "b" * 64,
        "provenance": "c" * 64,
        "contradictions": "d" * 64,
        "evidence_readiness": "e" * 64,
        "scored": "f" * 64,
        "market_analysis": "1" * 64,
        "stage_report": "2" * 64,
        "run_summary": "3" * 64,
    }
    _write_required_artifacts(output_dir, artifact_hashes=artifact_hashes)

    with _create_session() as session, pytest.raises(ReconciliationError, match="Could not resolve output_dir"):
        _ = reconcile_research_run(session=session, run_id="missing-run-id")
