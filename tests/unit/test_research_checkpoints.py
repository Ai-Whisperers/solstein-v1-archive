from __future__ import annotations

from pathlib import Path

import json

from solstein.research.checkpoints import (
    build_replay_diagnostics,
    can_resume_from_checkpoint,
    list_checkpoint_files,
    load_checkpoint_history,
    load_latest_checkpoint,
    replay_run_states,
)


def _write_checkpoint(path: Path, sequence: int, state: str) -> None:
    payload = {
        "sequence": sequence,
        "run_id": "run-1",
        "state": state,
        "current_stage": "scoring",
        "reason": None,
        "stage_count": sequence,
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_list_checkpoint_files_orders_by_sequence(tmp_path: Path) -> None:
    _write_checkpoint(tmp_path / "checkpoint_0002.json", 2, "running")
    _write_checkpoint(tmp_path / "checkpoint_0001.json", 1, "running")
    _write_checkpoint(tmp_path / "checkpoint_0003.json", 3, "completed")

    files = list_checkpoint_files(tmp_path)

    assert [f.name for f in files] == [
        "checkpoint_0001.json",
        "checkpoint_0002.json",
        "checkpoint_0003.json",
    ]


def test_load_checkpoint_history_reads_all(tmp_path: Path) -> None:
    _write_checkpoint(tmp_path / "checkpoint_0001.json", 1, "running")
    _write_checkpoint(tmp_path / "checkpoint_0002.json", 2, "failed")

    history = load_checkpoint_history(tmp_path)

    assert [item["sequence"] for item in history] == [1, 2]
    assert [item["state"] for item in history] == ["running", "failed"]


def test_replay_run_states_returns_ordered_state_progression(tmp_path: Path) -> None:
    _write_checkpoint(tmp_path / "checkpoint_0001.json", 1, "running")
    _write_checkpoint(tmp_path / "checkpoint_0002.json", 2, "running")
    _write_checkpoint(tmp_path / "checkpoint_0003.json", 3, "completed")

    replay = replay_run_states(tmp_path)

    assert replay == ["running", "running", "completed"]


def test_load_latest_checkpoint_prefers_latest_file(tmp_path: Path) -> None:
    _write_checkpoint(tmp_path / "checkpoint_0001.json", 1, "running")
    _write_checkpoint(tmp_path / "checkpoint_0002.json", 2, "failed")

    latest_payload = {
        "sequence": 99,
        "run_id": "run-latest",
        "state": "completed",
        "current_stage": "analysis",
        "reason": None,
        "stage_count": 10,
    }
    (tmp_path / "checkpoint_latest.json").write_text(json.dumps(latest_payload), encoding="utf-8")

    latest = load_latest_checkpoint(tmp_path)

    assert latest is not None
    assert latest["state"] == "completed"
    assert latest["run_id"] == "run-latest"


def test_can_resume_from_checkpoint_states() -> None:
    assert can_resume_from_checkpoint({"state": "running"}) is True
    assert can_resume_from_checkpoint({"state": "paused"}) is True
    assert can_resume_from_checkpoint({"state": "failed"}) is True
    assert can_resume_from_checkpoint({"state": "completed"}) is False
    assert can_resume_from_checkpoint({"state": "cancelled"}) is False
    assert can_resume_from_checkpoint(None) is False


def test_build_replay_diagnostics_reports_valid_progression(tmp_path: Path) -> None:
    _write_checkpoint(tmp_path / "checkpoint_0001.json", 1, "running")
    _write_checkpoint(tmp_path / "checkpoint_0002.json", 2, "running")
    _write_checkpoint(tmp_path / "checkpoint_0003.json", 3, "completed")

    diagnostics = build_replay_diagnostics(tmp_path)

    assert diagnostics["checkpoint_count"] == 3
    assert diagnostics["states"] == ["running", "running", "completed"]
    assert diagnostics["anomalies"] == []


def test_build_replay_diagnostics_flags_invalid_transition(tmp_path: Path) -> None:
    _write_checkpoint(tmp_path / "checkpoint_0001.json", 1, "completed")
    _write_checkpoint(tmp_path / "checkpoint_0002.json", 2, "running")

    diagnostics = build_replay_diagnostics(tmp_path)

    assert diagnostics["anomalies"]
    assert diagnostics["anomalies"][0]["type"] == "invalid_transition"


def test_build_replay_diagnostics_flags_post_terminal_progression(tmp_path: Path) -> None:
    _write_checkpoint(tmp_path / "checkpoint_0001.json", 1, "running")
    _write_checkpoint(tmp_path / "checkpoint_0002.json", 2, "completed")
    _write_checkpoint(tmp_path / "checkpoint_0003.json", 3, "completed")

    diagnostics = build_replay_diagnostics(tmp_path)

    anomaly_types = {item["type"] for item in diagnostics["anomalies"]}
    assert "post_terminal_progression" in anomaly_types
