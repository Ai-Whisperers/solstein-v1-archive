"""SQLite-backed store for the human review queue.

STORY-079: Persists ReviewQueueEntry records to a SQLite database so that
review state survives application restart (REQ-2). Uses the stdlib sqlite3
module directly — no ORM dependency, no migration framework needed for this
simple key-value-style table.

Thread safety: ``ReviewQueueStore`` is safe for concurrent reads from multiple
request handlers. Writes use ``check_same_thread=False`` and rely on SQLite's
built-in write serialization.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from loguru import logger

from solstein.config import Settings

from .models import ReviewQueueEntry, ReviewStatus

__all__ = ["ReviewQueueStore", "get_review_store"]

# Module-level singleton — initialized lazily by get_review_store()
_STORE: ReviewQueueStore | None = None

_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS review_queue (
    id                      TEXT PRIMARY KEY,
    run_id                  TEXT NOT NULL,
    created_at              TEXT NOT NULL,
    updated_at              TEXT NOT NULL,
    status                  TEXT NOT NULL DEFAULT 'pending',
    confidence_scores       TEXT NOT NULL DEFAULT '{}',
    company_scores          TEXT NOT NULL DEFAULT '{}',
    conflict_flags          TEXT NOT NULL DEFAULT '[]',
    low_confidence_companies TEXT NOT NULL DEFAULT '[]',
    reviewer_id             TEXT,
    reviewer_rationale      TEXT
);
CREATE INDEX IF NOT EXISTS idx_review_queue_run_id ON review_queue(run_id);
CREATE INDEX IF NOT EXISTS idx_review_queue_status  ON review_queue(status);
"""


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _row_to_entry(row: sqlite3.Row) -> ReviewQueueEntry:
    return ReviewQueueEntry(
        id=row["id"],
        run_id=row["run_id"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
        status=ReviewStatus(row["status"]),
        confidence_scores=json.loads(row["confidence_scores"]),
        company_scores=json.loads(row["company_scores"]),
        conflict_flags=json.loads(row["conflict_flags"]),
        low_confidence_companies=json.loads(row["low_confidence_companies"]),
        reviewer_id=row["reviewer_id"],
        reviewer_rationale=row["reviewer_rationale"],
    )


class ReviewQueueStore:
    """SQLite-backed persistence layer for ReviewQueueEntry records.

    Usage:
        store = ReviewQueueStore(Path("data/checkpoints/review_queue.db"))
        entry = store.create_entry(run_id="abc-123", state=graph_state)
        store.approve(entry.id, reviewer_id="analyst@example.com")
    """

    def __init__(self, db_path: Path) -> None:
        db_path = Path(db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_CREATE_TABLE_SQL)
        self._conn.commit()
        logger.debug(f"[ReviewQueueStore] Initialized at {db_path}")

    def create_entry(
        self,
        run_id: str,
        state: dict[str, Any],
        threshold: float = 0.5,
    ) -> ReviewQueueEntry:
        """Create a new PENDING review entry for a research run.

        Extracts confidence scores, company scores, and conflict flags from the
        LangGraph ResearchState dict. Identifies which companies triggered the
        review (confidence < threshold).

        Args:
            run_id: LangGraph thread_id for the paused graph.
            state:  ResearchState dict at the point of interruption.
            threshold: Confidence threshold used to identify low-confidence companies.

        Returns:
            The newly created ReviewQueueEntry (status=PENDING).
        """
        confidence_scores: dict[str, float] = state.get("confidence_scores") or {}
        company_scores: dict[str, Any] = state.get("company_scores") or {}
        conflict_flags: list[dict[str, Any]] = state.get("conflict_flags") or []
        low_conf = [cid for cid, score in confidence_scores.items() if score < threshold]

        entry = ReviewQueueEntry(
            id=str(uuid.uuid4()),
            run_id=run_id,
            confidence_scores=confidence_scores,
            company_scores=company_scores,
            conflict_flags=conflict_flags,
            low_confidence_companies=low_conf,
        )

        self._conn.execute(
            """
            INSERT INTO review_queue
                (id, run_id, created_at, updated_at, status,
                 confidence_scores, company_scores, conflict_flags,
                 low_confidence_companies, reviewer_id, reviewer_rationale)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry.id,
                entry.run_id,
                entry.created_at.isoformat(),
                entry.updated_at.isoformat(),
                entry.status.value,
                json.dumps(entry.confidence_scores),
                json.dumps(entry.company_scores),
                json.dumps(entry.conflict_flags),
                json.dumps(entry.low_confidence_companies),
                entry.reviewer_id,
                entry.reviewer_rationale,
            ),
        )
        self._conn.commit()
        logger.info(f"[ReviewQueueStore] Created entry {entry.id} for run {run_id}")
        return entry

    def get_entry(self, entry_id: str) -> ReviewQueueEntry | None:
        """Retrieve a review entry by its UUID.

        Returns None if not found.
        """
        row = self._conn.execute("SELECT * FROM review_queue WHERE id = ?", (entry_id,)).fetchone()
        if row is None:
            return None
        return _row_to_entry(row)

    def get_by_run_id(self, run_id: str) -> ReviewQueueEntry | None:
        """Retrieve the most recent review entry for a given run_id.

        Returns None if no entry exists for this run.
        """
        row = self._conn.execute(
            "SELECT * FROM review_queue WHERE run_id = ? ORDER BY created_at DESC LIMIT 1",
            (run_id,),
        ).fetchone()
        if row is None:
            return None
        return _row_to_entry(row)

    def list_pending(self) -> list[ReviewQueueEntry]:
        """Return all PENDING review entries, oldest first."""
        rows = self._conn.execute(
            "SELECT * FROM review_queue WHERE status = 'pending' ORDER BY created_at ASC"
        ).fetchall()
        return [_row_to_entry(r) for r in rows]

    def list_all(self, limit: int = 100) -> list[ReviewQueueEntry]:
        """Return recent review entries (any status), newest first."""
        rows = self._conn.execute("SELECT * FROM review_queue ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return [_row_to_entry(r) for r in rows]

    def approve(self, entry_id: str, reviewer_id: str | None = None) -> ReviewQueueEntry:
        """Approve a PENDING review entry.

        Transitions status: PENDING → APPROVED.

        Args:
            entry_id:    UUID of the entry to approve.
            reviewer_id: Optional identifier of the approving analyst.

        Returns:
            The updated ReviewQueueEntry.

        Raises:
            ValueError: If the entry does not exist or is not PENDING.
        """
        entry = self._get_or_raise(entry_id)
        if entry.status != ReviewStatus.PENDING:
            raise ValueError(f"Review entry {entry_id} is already {entry.status.value} — cannot approve.")
        now = _now_iso()
        self._conn.execute(
            "UPDATE review_queue SET status = 'approved', reviewer_id = ?, updated_at = ? WHERE id = ?",
            (reviewer_id, now, entry_id),
        )
        self._conn.commit()
        logger.info(f"[ReviewQueueStore] Approved entry {entry_id} by {reviewer_id}")
        return self.get_entry(entry_id)  # type: ignore[return-value]

    def reject(
        self,
        entry_id: str,
        reviewer_id: str | None = None,
        rationale: str | None = None,
    ) -> ReviewQueueEntry:
        """Reject a PENDING review entry.

        Transitions status: PENDING → REJECTED. The associated research result
        must not be delivered to clients after rejection.

        Args:
            entry_id:   UUID of the entry to reject.
            reviewer_id: Optional identifier of the rejecting analyst.
            rationale:  Free-text rejection reason.

        Returns:
            The updated ReviewQueueEntry.

        Raises:
            ValueError: If the entry does not exist or is not PENDING.
        """
        entry = self._get_or_raise(entry_id)
        if entry.status != ReviewStatus.PENDING:
            raise ValueError(f"Review entry {entry_id} is already {entry.status.value} — cannot reject.")
        now = _now_iso()
        self._conn.execute(
            """
            UPDATE review_queue
            SET status = 'rejected', reviewer_id = ?, reviewer_rationale = ?, updated_at = ?
            WHERE id = ?
            """,
            (reviewer_id, rationale, now, entry_id),
        )
        self._conn.commit()
        logger.info(f"[ReviewQueueStore] Rejected entry {entry_id} by {reviewer_id}: {rationale}")
        return self.get_entry(entry_id)  # type: ignore[return-value]

    def _get_or_raise(self, entry_id: str) -> ReviewQueueEntry:
        entry = self.get_entry(entry_id)
        if entry is None:
            raise ValueError(f"Review entry {entry_id} not found.")
        return entry

    def close(self) -> None:
        """Close the SQLite connection."""
        self._conn.close()


def get_review_store(db_path: Path | None = None) -> ReviewQueueStore:
    """Return the module-level singleton ReviewQueueStore.

    On first call, initializes the store using ``db_path`` (or the
    default path from Settings if db_path is None).

    Args:
        db_path: Optional explicit DB path for the first-call initialization.
                 Ignored on subsequent calls once the singleton is set.

    Returns:
        The singleton ReviewQueueStore instance.
    """
    global _STORE
    if _STORE is None:
        if db_path is None:
            db_path = Settings().review_queue_db_path
        _STORE = ReviewQueueStore(db_path)
    return _STORE
