"""Tests for STORY-013: Fix Conflict Resolution Logic.

Covers:
- REQ-1: Newer record wins over older record on conflict
- REQ-2: Higher-reliability source wins when timestamps are equal
- REQ-3: MANUAL_REVIEW creates a persisted review record
- REQ-3: Manual review records are retrievable / resolvable
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from solstein.infrastructure.conflict_resolution import (
    Conflict,
    ConflictResolutionEngine,
    ConflictStrategy,
    ManualReviewRecord,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@dataclass
class FactSpec:
    """Parameter object for building test facts (keeps _make_conflict <= 5 params)."""

    source: str = "competitor_json"
    extracted_at: datetime | str | None = None
    confidence: float = 0.5
    value: str = "old_value"

    def to_dict(self) -> dict[str, Any]:
        """Convert to the dict format expected by Conflict."""
        return {
            "source": self.source,
            "extracted_at": self.extracted_at,
            "confidence": self.confidence,
            "value": self.value,
        }


def _make_conflict(
    existing: FactSpec | None = None,
    new: FactSpec | None = None,
) -> Conflict:
    """Build a Conflict with sensible defaults for testing."""
    _existing = existing or FactSpec()
    _new = new or FactSpec(source="sec_edgar", value="new_value")
    return Conflict(
        company_id="COMP-001",
        fact_type="revenue",
        existing_fact=_existing.to_dict(),
        new_fact=_new.to_dict(),
        conflict_type="value_mismatch",
        detected_at=datetime.now(),
    )


# ---------------------------------------------------------------------------
# REQ-1: Recency — newer record wins
# ---------------------------------------------------------------------------


class TestNewerTimestampWins:
    """Conflict resolution must prefer more recent records (REQ-1)."""

    def test_newer_record_wins_over_older(self) -> None:
        engine = ConflictResolutionEngine()
        now = datetime.now()
        conflict = _make_conflict(
            existing=FactSpec(source="sec_edgar", extracted_at=now - timedelta(days=7)),
            new=FactSpec(source="sec_edgar", value="new_value", extracted_at=now),
        )
        resolution = engine.resolve_conflict(conflict)
        assert resolution.strategy_used == ConflictStrategy.NEWER_TIMESTAMP
        assert resolution.winning_fact["value"] == "new_value"

    def test_older_record_loses(self) -> None:
        engine = ConflictResolutionEngine()
        now = datetime.now()
        conflict = _make_conflict(
            existing=FactSpec(source="sec_edgar", extracted_at=now),
            new=FactSpec(source="sec_edgar", value="new_value", extracted_at=now - timedelta(days=7)),
        )
        resolution = engine.resolve_conflict(conflict)
        assert resolution.strategy_used == ConflictStrategy.NEWER_TIMESTAMP
        assert resolution.winning_fact["value"] == "old_value"

    def test_iso_string_timestamps_are_normalised(self) -> None:
        engine = ConflictResolutionEngine()
        conflict = _make_conflict(
            existing=FactSpec(source="sec_edgar", extracted_at="2025-01-01T00:00:00"),
            new=FactSpec(source="sec_edgar", value="new_value", extracted_at="2026-01-01T00:00:00"),
        )
        resolution = engine.resolve_conflict(conflict)
        assert resolution.strategy_used == ConflictStrategy.NEWER_TIMESTAMP
        assert resolution.winning_fact["value"] == "new_value"

    def test_recency_takes_priority_over_reliability(self) -> None:
        """Even if existing is from a more authoritative source, newer wins."""
        engine = ConflictResolutionEngine()
        now = datetime.now()
        conflict = _make_conflict(
            existing=FactSpec(source="sec_edgar", extracted_at=now - timedelta(days=30)),
            new=FactSpec(source="competitor_json", value="new_value", extracted_at=now),
        )
        resolution = engine.resolve_conflict(conflict)
        assert resolution.strategy_used == ConflictStrategy.NEWER_TIMESTAMP
        assert resolution.winning_fact["value"] == "new_value"


# ---------------------------------------------------------------------------
# REQ-2: Reliability — higher-reliability source wins on equal timestamps
# ---------------------------------------------------------------------------


class TestReliabilityTiebreaker:
    """Higher-reliability source wins when recency is equal (REQ-2)."""

    def test_higher_reliability_wins_on_equal_timestamp(self) -> None:
        engine = ConflictResolutionEngine()
        same_time = datetime.now()
        conflict = _make_conflict(
            existing=FactSpec(source="competitor_json", extracted_at=same_time),
            new=FactSpec(source="sec_edgar", value="new_value", extracted_at=same_time),
        )
        resolution = engine.resolve_conflict(conflict)
        assert resolution.strategy_used == ConflictStrategy.AUTHORITATIVE_SOURCE
        assert resolution.winning_fact["value"] == "new_value"

    def test_lower_reliability_loses_on_equal_timestamp(self) -> None:
        engine = ConflictResolutionEngine()
        same_time = datetime.now()
        conflict = _make_conflict(
            existing=FactSpec(source="sec_edgar", extracted_at=same_time),
            new=FactSpec(source="competitor_json", value="new_value", extracted_at=same_time),
        )
        resolution = engine.resolve_conflict(conflict)
        assert resolution.strategy_used == ConflictStrategy.AUTHORITATIVE_SOURCE
        assert resolution.winning_fact["value"] == "old_value"

    def test_same_source_equal_time_falls_to_confidence(self) -> None:
        """When both source and time match, confidence breaks the tie."""
        engine = ConflictResolutionEngine()
        same_time = datetime.now()
        conflict = _make_conflict(
            existing=FactSpec(source="sec_edgar", extracted_at=same_time, confidence=0.5),
            new=FactSpec(source="sec_edgar", value="new_value", extracted_at=same_time, confidence=0.9),
        )
        resolution = engine.resolve_conflict(conflict)
        assert resolution.strategy_used == ConflictStrategy.HIGHER_CONFIDENCE
        assert resolution.winning_fact["value"] == "new_value"


# ---------------------------------------------------------------------------
# REQ-3: MANUAL_REVIEW creates a persisted record
# ---------------------------------------------------------------------------


class TestManualReviewPersistence:
    """MANUAL_REVIEW must create a queryable review record (REQ-3)."""

    def test_manual_review_creates_record(self) -> None:
        engine = ConflictResolutionEngine()
        same_time = datetime.now()
        conflict = _make_conflict(
            existing=FactSpec(source="sec_edgar", extracted_at=same_time),
            new=FactSpec(source="sec_edgar", value="new_value", extracted_at=same_time),
        )
        resolution = engine.resolve_conflict(conflict)
        assert resolution.strategy_used == ConflictStrategy.MANUAL_REVIEW
        assert len(engine.manual_review_queue) == 1
        record = engine.manual_review_queue[0]
        assert record.company_id == "COMP-001"
        assert record.fact_type == "revenue"
        assert record.status == "pending"

    def test_manual_review_stores_both_facts(self) -> None:
        engine = ConflictResolutionEngine()
        same_time = datetime.now()
        conflict = _make_conflict(
            existing=FactSpec(source="sec_edgar", extracted_at=same_time),
            new=FactSpec(source="sec_edgar", value="new_value", extracted_at=same_time),
        )
        engine.resolve_conflict(conflict)
        record = engine.manual_review_queue[0]
        assert record.existing_fact["value"] == "old_value"
        assert record.new_fact["value"] == "new_value"

    def test_pending_reviews_are_retrievable(self) -> None:
        engine = ConflictResolutionEngine()
        same_time = datetime.now()
        for i in range(3):
            conflict = _make_conflict(
                existing=FactSpec(source="sec_edgar", extracted_at=same_time),
                new=FactSpec(source="sec_edgar", value="new_value", extracted_at=same_time),
            )
            conflict.company_id = f"COMP-{i:03d}"
            engine.resolve_conflict(conflict)

        pending = engine.get_pending_reviews()
        assert len(pending) == 3
        assert all(r.status == "pending" for r in pending)

    def test_review_can_be_resolved_by_operator(self) -> None:
        engine = ConflictResolutionEngine()
        same_time = datetime.now()
        conflict = _make_conflict(
            existing=FactSpec(source="sec_edgar", extracted_at=same_time),
            new=FactSpec(source="sec_edgar", value="new_value", extracted_at=same_time),
        )
        engine.resolve_conflict(conflict)
        review_id = engine.manual_review_queue[0].review_id

        updated = engine.resolve_review(review_id, resolved_by="admin@example.com")
        assert updated is not None
        assert updated.status == "resolved"
        assert updated.resolved_by == "admin@example.com"
        assert updated.resolved_at is not None
        assert len(engine.get_pending_reviews()) == 0

    def test_resolve_nonexistent_review_returns_none(self) -> None:
        engine = ConflictResolutionEngine()
        result = engine.resolve_review("nonexistent-id", resolved_by="admin")
        assert result is None

    def test_get_review_by_id(self) -> None:
        engine = ConflictResolutionEngine()
        same_time = datetime.now()
        conflict = _make_conflict(
            existing=FactSpec(source="sec_edgar", extracted_at=same_time),
            new=FactSpec(source="sec_edgar", value="new_value", extracted_at=same_time),
        )
        engine.resolve_conflict(conflict)
        review_id = engine.manual_review_queue[0].review_id

        record = engine.get_review_by_id(review_id)
        assert record is not None
        assert record.review_id == review_id

    def test_stats_include_pending_reviews(self) -> None:
        engine = ConflictResolutionEngine()
        same_time = datetime.now()
        conflict = _make_conflict(
            existing=FactSpec(source="sec_edgar", extracted_at=same_time),
            new=FactSpec(source="sec_edgar", value="new_value", extracted_at=same_time),
        )
        engine.resolve_conflict(conflict)
        stats = engine.get_resolution_stats()
        assert stats["pending_reviews"] == 1


# ---------------------------------------------------------------------------
# ManualReviewRecord dataclass
# ---------------------------------------------------------------------------


class TestManualReviewRecordDataclass:
    """Verify ManualReviewRecord fields and defaults."""

    def test_defaults(self) -> None:
        record = ManualReviewRecord()
        assert record.status == "pending"
        assert record.resolved_at is None
        assert record.resolved_by is None
        assert record.review_id  # non-empty UUID string

    def test_uuid_uniqueness(self) -> None:
        records = [ManualReviewRecord() for _ in range(10)]
        ids = {r.review_id for r in records}
        assert len(ids) == 10


# ---------------------------------------------------------------------------
# Strategy selection logic
# ---------------------------------------------------------------------------


class TestStrategySelection:
    """Verify the priority chain in _select_strategy."""

    def test_no_timestamps_uses_authority(self) -> None:
        engine = ConflictResolutionEngine()
        conflict = _make_conflict(
            existing=FactSpec(source="competitor_json"),
            new=FactSpec(source="sec_edgar", value="new_value"),
        )
        resolution = engine.resolve_conflict(conflict)
        assert resolution.strategy_used == ConflictStrategy.AUTHORITATIVE_SOURCE

    def test_no_timestamps_same_source_uses_confidence(self) -> None:
        engine = ConflictResolutionEngine()
        conflict = _make_conflict(
            existing=FactSpec(source="sec_edgar", confidence=0.3),
            new=FactSpec(source="sec_edgar", value="new_value", confidence=0.9),
        )
        resolution = engine.resolve_conflict(conflict)
        assert resolution.strategy_used == ConflictStrategy.HIGHER_CONFIDENCE

    def test_forced_strategy_overrides_auto(self) -> None:
        """Explicitly passing a strategy skips auto-selection."""
        engine = ConflictResolutionEngine()
        now = datetime.now()
        conflict = _make_conflict(
            existing=FactSpec(source="sec_edgar", extracted_at=now - timedelta(days=1)),
            new=FactSpec(source="sec_edgar", value="new_value", extracted_at=now),
        )
        resolution = engine.resolve_conflict(conflict, strategy=ConflictStrategy.MANUAL_REVIEW)
        assert resolution.strategy_used == ConflictStrategy.MANUAL_REVIEW
        assert len(engine.manual_review_queue) == 1
