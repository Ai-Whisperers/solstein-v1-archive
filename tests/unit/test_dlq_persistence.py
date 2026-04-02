"""Focused regressions for durable dead-letter queue handling."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from solstein.worker.base import DeadLetterQueue
from solstein.worker.enrichment_tasks import _build_failure_result


def test_dead_letter_queue_persists_structured_record_and_tracks_error(tmp_path: Path) -> None:
    # DLQ now persists to PostgreSQL via persist_failed_task, not a .jsonl file.
    # audit_path is kept for backward compat but is no longer written.
    audit_path = tmp_path / "dead_letter_queue.jsonl"
    queue = DeadLetterQueue(audit_path=audit_path)
    error = RuntimeError("connector exploded")

    with (
        patch("solstein.worker.base.global_error_tracker.track_error") as mock_track,
        patch("solstein.worker.base.persist_failed_task") as mock_persist,
    ):
        record = queue.record_failure(
            "refresh_sec_edgar",
            "task-123",
            error,
            3,
            traceback_text="traceback-line-1\ntraceback-line-2",
            context={"source_name": "SEC EDGAR"},
        )

    assert record["error"] == "connector exploded"
    assert record["error_type"] == "RuntimeError"
    assert record["traceback"] == "traceback-line-1\ntraceback-line-2"
    assert record["context"]["source_name"] == "SEC EDGAR"
    assert len(queue.failed_jobs) == 1

    # Verify persist_failed_task was called with the right task identifiers
    mock_persist.assert_called_once()
    call_kwargs = mock_persist.call_args.kwargs
    assert call_kwargs["task_name"] == "refresh_sec_edgar"
    assert call_kwargs["task_id"] == "task-123"
    mock_track.assert_called_once()


def test_dead_letter_queue_accepts_string_errors_for_backward_compatibility(tmp_path: Path) -> None:
    audit_path = tmp_path / "dead_letter_queue.jsonl"
    queue = DeadLetterQueue(audit_path=audit_path)

    with patch("solstein.worker.base.global_error_tracker.track_error") as mock_track:
        record = queue.record_failure("refresh_news", "task-456", "plain-string-error", 2)

    assert record["error"] == "plain-string-error"
    assert record["error_type"] == "TaskFailure"
    assert queue.failed_jobs[0]["error_type"] == "TaskFailure"
    mock_track.assert_called_once()


def test_build_failure_result_includes_type_and_traceback() -> None:
    payload = _build_failure_result(
        "task-789",
        company_id="acme",
        company_name="Acme",
        status="FAILED",
        error=ValueError("bad payload"),
        traceback_text="traceback-goes-here",
        timestamp="2026-03-26T17:00:00+00:00",
    )

    assert payload["task_id"] == "task-789"
    assert payload["company_id"] == "acme"
    assert payload["company_name"] == "Acme"
    assert payload["status"] == "FAILED"
    assert payload["error"] == "bad payload"
    assert payload["error_type"] == "ValueError"
    assert payload["error_traceback"] == "traceback-goes-here"
