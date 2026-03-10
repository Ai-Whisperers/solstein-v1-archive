from __future__ import annotations

from pathlib import Path

import pytest

from solstein.research.checkpoints import load_latest_checkpoint, write_checkpoint
from solstein.research.pipeline import cancel_market_intelligence_run, resume_market_intelligence_run


def test_resume_market_intelligence_run_from_failed_checkpoint(tmp_path: Path) -> None:
    write_checkpoint(
        tmp_path,
        run_id="run-200",
        state="failed",
        current_stage="scoring",
        reason="temporary connector timeout",
        stage_count=4,
    )

    resumed = resume_market_intelligence_run(tmp_path)

    assert resumed["run_id"] == "run-200"
    assert resumed["state"] == "running"
    latest = load_latest_checkpoint(tmp_path)
    assert latest is not None
    assert latest["state"] == "running"
    assert latest["sequence"] == 2


def test_resume_market_intelligence_run_rejects_completed(tmp_path: Path) -> None:
    write_checkpoint(
        tmp_path,
        run_id="run-201",
        state="completed",
        current_stage="analysis",
        reason=None,
        stage_count=8,
    )

    with pytest.raises(RuntimeError, match="No resumable checkpoint found"):
        resume_market_intelligence_run(tmp_path)


def test_cancel_market_intelligence_run_records_reason(tmp_path: Path) -> None:
    write_checkpoint(
        tmp_path,
        run_id="run-202",
        state="running",
        current_stage="analysis",
        reason=None,
        stage_count=6,
    )

    cancelled = cancel_market_intelligence_run(tmp_path, reason="operator cancel")

    assert cancelled["state"] == "cancelled"
    assert cancelled["reason"] == "operator cancel"
    latest = load_latest_checkpoint(tmp_path)
    assert latest is not None
    assert latest["state"] == "cancelled"
    assert latest["reason"] == "operator cancel"


def test_cancel_market_intelligence_run_requires_checkpoint(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="No checkpoint found to cancel"):
        cancel_market_intelligence_run(tmp_path, reason="operator cancel")
