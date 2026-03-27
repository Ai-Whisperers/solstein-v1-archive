from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast


def _checkpoint_sequence(path: Path) -> int:
    stem = path.stem
    if not stem.startswith("checkpoint_"):
        return -1
    suffix = stem.split("_", 1)[1]
    if not suffix.isdigit():
        return -1
    return int(suffix)


def list_checkpoint_files(output_dir: Path) -> list[Path]:
    files = [path for path in output_dir.glob("checkpoint_*.json") if _checkpoint_sequence(path) >= 0]
    return sorted(files, key=_checkpoint_sequence)


def load_checkpoint_history(output_dir: Path) -> list[dict[str, Any]]:
    history: list[dict[str, Any]] = []
    for file_path in list_checkpoint_files(output_dir):
        payload = cast("dict[str, Any]", json.loads(file_path.read_text(encoding="utf-8")))
        history.append(payload)
    return history


def load_latest_checkpoint(output_dir: Path) -> dict[str, Any] | None:
    latest_path = output_dir / "checkpoint_latest.json"
    if latest_path.exists():
        return cast("dict[str, Any]", json.loads(latest_path.read_text(encoding="utf-8")))

    history = load_checkpoint_history(output_dir)
    if not history:
        return None
    return history[-1]


def can_resume_from_checkpoint(checkpoint: dict[str, Any] | None) -> bool:
    if checkpoint is None:
        return False
    state = str(checkpoint.get("state", "")).lower()
    return state in {"running", "paused", "failed"}


def write_checkpoint(
    output_dir: Path,
    *,
    run_id: str,
    state: str,
    current_stage: str | None,
    reason: str | None,
    stage_count: int,
) -> dict[str, Any]:
    sequence = len(list_checkpoint_files(output_dir)) + 1
    checkpoint = {
        "sequence": sequence,
        "run_id": run_id,
        "state": state,
        "current_stage": current_stage,
        "reason": reason,
        "stage_count": stage_count,
    }
    (output_dir / "checkpoint_latest.json").write_text(
        json.dumps(checkpoint, indent=2),
        encoding="utf-8",
    )
    (output_dir / f"checkpoint_{sequence:04d}.json").write_text(
        json.dumps(checkpoint, indent=2),
        encoding="utf-8",
    )
    return checkpoint


def replay_run_states(output_dir: Path) -> list[str]:
    return [
        str(checkpoint.get("state", ""))
        for checkpoint in load_checkpoint_history(output_dir)
        if checkpoint.get("state") is not None
    ]


_ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "created": {"running", "cancelled"},
    "running": {"running", "paused", "failed", "completed", "cancelled"},
    "paused": {"running", "cancelled"},
    "failed": {"running", "cancelled", "failed"},
    "completed": {"completed"},
    "cancelled": {"cancelled"},
}


def build_replay_diagnostics(output_dir: Path) -> dict[str, Any]:
    history = load_checkpoint_history(output_dir)
    states = [str(item.get("state", "")) for item in history]
    transitions: list[dict[str, Any]] = []
    anomalies: list[dict[str, Any]] = []

    for idx in range(1, len(states)):
        prev_state = states[idx - 1]
        next_state = states[idx]
        transition = {
            "index": idx,
            "from": prev_state,
            "to": next_state,
            "sequence": history[idx].get("sequence"),
        }
        transitions.append(transition)

        allowed = _ALLOWED_TRANSITIONS.get(prev_state, set())
        if next_state not in allowed:
            anomalies.append({"type": "invalid_transition", **transition})

    terminal_states = {"completed", "cancelled"}
    first_terminal = next((i for i, state in enumerate(states) if state in terminal_states), None)
    if first_terminal is not None and first_terminal < len(states) - 1:
        anomalies.append(
            {
                "type": "post_terminal_progression",
                "terminal_index": first_terminal,
                "terminal_state": states[first_terminal],
                "remaining_states": states[first_terminal + 1 :],
            }
        )

    return {
        "checkpoint_count": len(history),
        "states": states,
        "transitions": transitions,
        "anomalies": anomalies,
        "last_checkpoint": history[-1] if history else None,
    }
