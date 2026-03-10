"""Tests for conflict_resolution module.

E3: Tests for extracted conflict resolution adapter.
"""

from datetime import datetime
from decimal import Decimal

import pytest

from solstein.data.conflict_resolution import (
    CompositeResolver,
    ConflictStrategy,
    FieldConflict,
    ListResolver,
    NumericResolver,
    RecencyResolver,
    ResolutionResult,
    SourcePriorityResolver,
    StringResolver,
)


class TestFieldConflict:
    """Tests for FieldConflict dataclass."""

    def test_creation(self) -> None:
        conflict = FieldConflict(
            field_name="revenue",
            existing_value=100,
            incoming_value=200,
            existing_source="source_a",
            incoming_source="source_b",
        )
        assert conflict.field_name == "revenue"
        assert conflict.existing_value == 100
        assert conflict.incoming_value == 200


class TestResolutionResult:
    """Tests for ResolutionResult dataclass."""

    def test_creation(self) -> None:
        result = ResolutionResult(
            resolved_value=200,
            strategy_used=ConflictStrategy.SOURCE_PRIORITY,
            notes="Higher priority source",
        )
        assert result.resolved_value == 200
        assert result.strategy_used == ConflictStrategy.SOURCE_PRIORITY
        assert result.notes == "Higher priority source"
        assert result.requires_review is False


class TestSourcePriorityResolver:
    """Tests for SourcePriorityResolver."""

    def test_higher_priority_wins(self) -> None:
        resolver = SourcePriorityResolver()
        conflict = FieldConflict(
            field_name="revenue",
            existing_value=100,
            incoming_value=200,
            existing_source="web_scrape",
            incoming_source="sec_edgar",
        )
        result = resolver.resolve(conflict)

        assert result.resolved_value == 200
        assert result.strategy_used == ConflictStrategy.SOURCE_PRIORITY
        assert "sec_edgar" in result.notes

    def test_equal_priority_keeps_existing(self) -> None:
        resolver = SourcePriorityResolver()
        conflict = FieldConflict(
            field_name="revenue",
            existing_value=100,
            incoming_value=200,
            existing_source="crunchbase",
            incoming_source="pitchbook",
        )
        result = resolver.resolve(conflict)

        assert result.resolved_value == 100

    def test_custom_priorities(self) -> None:
        resolver = SourcePriorityResolver({"custom_high": 1, "custom_low": 10})
        conflict = FieldConflict(
            field_name="value",
            existing_value=100,
            incoming_value=200,
            existing_source="custom_low",
            incoming_source="custom_high",
        )
        result = resolver.resolve(conflict)

        assert result.resolved_value == 200


class TestRecencyResolver:
    """Tests for RecencyResolver."""

    def test_more_recent_wins(self) -> None:
        resolver = RecencyResolver()
        conflict = FieldConflict(
            field_name="revenue",
            existing_value=100,
            incoming_value=200,
            existing_timestamp=datetime(2024, 1, 1),
            incoming_timestamp=datetime(2024, 6, 1),
        )
        result = resolver.resolve(conflict)

        assert result.resolved_value == 200
        assert result.strategy_used == ConflictStrategy.RECENCY_WINS

    def test_older_kept(self) -> None:
        resolver = RecencyResolver()
        conflict = FieldConflict(
            field_name="revenue",
            existing_value=100,
            incoming_value=200,
            existing_timestamp=datetime(2024, 6, 1),
            incoming_timestamp=datetime(2024, 1, 1),
        )
        result = resolver.resolve(conflict)

        assert result.resolved_value == 100

    def test_fallback_to_confidence(self) -> None:
        resolver = RecencyResolver()
        conflict = FieldConflict(
            field_name="revenue",
            existing_value=100,
            incoming_value=200,
            existing_confidence=0.5,
            incoming_confidence=0.8,
        )
        result = resolver.resolve(conflict)

        assert result.resolved_value == 200
        assert "confidence" in result.notes


class TestNumericResolver:
    """Tests for NumericResolver."""

    def test_prefer_maximum(self) -> None:
        resolver = NumericResolver(prefer_maximum=True)
        conflict = FieldConflict(
            field_name="revenue",
            existing_value=100,
            incoming_value=200,
        )
        result = resolver.resolve(conflict)

        assert result.resolved_value == 200
        assert result.strategy_used == ConflictStrategy.MAXIMUM_VALUE

    def test_prefer_minimum(self) -> None:
        resolver = NumericResolver(prefer_maximum=False)
        conflict = FieldConflict(
            field_name="risk_score",
            existing_value=0.8,
            incoming_value=0.3,
        )
        result = resolver.resolve(conflict)

        assert result.resolved_value == 0.3
        assert result.strategy_used == ConflictStrategy.MINIMUM_VALUE

    def test_non_numeric_fallback(self) -> None:
        resolver = NumericResolver()
        conflict = FieldConflict(
            field_name="name",
            existing_value="TestCo",
            incoming_value="OtherCo",
        )
        result = resolver.resolve(conflict)

        # Should fall back to source priority
        assert result.strategy_used == ConflictStrategy.SOURCE_PRIORITY


class TestStringResolver:
    """Tests for StringResolver."""

    def test_prefer_longer(self) -> None:
        resolver = StringResolver(concatenate=False)
        conflict = FieldConflict(
            field_name="description",
            existing_value="Short",
            incoming_value="Much longer description",
        )
        result = resolver.resolve(conflict)

        assert result.resolved_value == "Much longer description"

    def test_concatenate_mode(self) -> None:
        resolver = StringResolver(concatenate=True)
        conflict = FieldConflict(
            field_name="description",
            existing_value="Part one",
            incoming_value="Part two",
        )
        result = resolver.resolve(conflict)

        assert "Part one" in result.resolved_value
        assert "Part two" in result.resolved_value

    def test_identical_values(self) -> None:
        resolver = StringResolver()
        conflict = FieldConflict(
            field_name="name",
            existing_value="TestCo",
            incoming_value="TestCo",
        )
        result = resolver.resolve(conflict)

        assert result.resolved_value == "TestCo"
        assert "identical" in result.notes.lower()


class TestListResolver:
    """Tests for ListResolver."""

    def test_union_strategy(self) -> None:
        resolver = ListResolver(ConflictStrategy.UNION)
        conflict = FieldConflict(
            field_name="competitors",
            existing_value=["A", "B"],
            incoming_value=["B", "C"],
        )
        result = resolver.resolve(conflict)

        assert set(result.resolved_value) == {"A", "B", "C"}
        assert result.strategy_used == ConflictStrategy.UNION

    def test_intersection_strategy(self) -> None:
        resolver = ListResolver(ConflictStrategy.INTERSECTION)
        conflict = FieldConflict(
            field_name="competitors",
            existing_value=["A", "B", "C"],
            incoming_value=["B", "C", "D"],
        )
        result = resolver.resolve(conflict)

        assert set(result.resolved_value) == {"B", "C"}
        assert result.strategy_used == ConflictStrategy.INTERSECTION

    def test_invalid_strategy_raises(self) -> None:
        with pytest.raises(ValueError):
            ListResolver(ConflictStrategy.SOURCE_PRIORITY)


class TestCompositeResolver:
    """Tests for CompositeResolver."""

    def test_delegates_to_field_resolver(self) -> None:
        resolver = CompositeResolver()
        conflict = FieldConflict(
            field_name="revenue",
            existing_value=100,
            incoming_value=200,
        )
        result = resolver.resolve(conflict)

        # Revenue uses NumericResolver with prefer_maximum
        assert result.resolved_value == 200

    def test_uses_default_for_unknown_field(self) -> None:
        resolver = CompositeResolver()
        conflict = FieldConflict(
            field_name="unknown_field",
            existing_value="old",
            incoming_value="new",
            existing_timestamp=datetime(2024, 1, 1),
            incoming_timestamp=datetime(2024, 6, 1),
        )
        result = resolver.resolve(conflict)

        # Unknown fields use RecencyResolver
        assert result.strategy_used == ConflictStrategy.RECENCY_WINS

    def test_resolve_merge(self) -> None:
        resolver = CompositeResolver()
        existing = {"name": "TestCo", "revenue": 100, "employees": 50}
        incoming = {"name": "TestCo", "revenue": 200, "location": "NYC"}

        result = resolver.resolve_merge(existing, incoming)

        assert result["name"] == "TestCo"
        assert result["revenue"] == 200  # Higher value wins
        assert result["employees"] == 50  # Preserved from existing
        assert result["location"] == "NYC"  # Added from incoming

    def test_resolve_merge_no_conflict(self) -> None:
        resolver = CompositeResolver()
        existing = {"name": "TestCo", "revenue": 100}
        incoming = {"name": "TestCo", "revenue": 100}

        result = resolver.resolve_merge(existing, incoming)

        assert result["revenue"] == 100

    def test_resolve_merge_null_incoming_skipped(self) -> None:
        resolver = CompositeResolver()
        existing = {"name": "TestCo", "revenue": 100}
        incoming = {"name": "TestCo", "revenue": None}

        result = resolver.resolve_merge(existing, incoming)

        assert result["revenue"] == 100

    def test_resolve_merge_with_adjudication_keep_existing(self) -> None:
        resolver = CompositeResolver()
        existing = {"revenue": 100.0}
        incoming = {"revenue": 200.0}
        decisions = {"revenue": {"decision": "keep_existing", "decision_id": "dec-keep-1"}}

        result = resolver.resolve_merge(existing, incoming, adjudication_decisions=decisions)

        assert result["revenue"] == 100.0

    def test_resolve_merge_with_adjudication_approve_incoming(self) -> None:
        resolver = CompositeResolver()
        existing = {"employees": 40}
        incoming = {"employees": 55}
        decisions = {"employees": {"decision": "approve_incoming", "decision_id": "dec-inc-1"}}

        result = resolver.resolve_merge(existing, incoming, adjudication_decisions=decisions)

        assert result["employees"] == 55

    def test_resolve_merge_with_adjudication_override_value(self) -> None:
        resolver = CompositeResolver()
        existing = {"valuation": 1_000_000.0}
        incoming = {"valuation": 1_200_000.0}
        decisions = {
            "valuation": {
                "decision": "override",
                "decision_id": "dec-ovr-1",
                "value": 1_150_000.0,
            }
        }

        result = resolver.resolve_merge(existing, incoming, adjudication_decisions=decisions)

        assert result["valuation"] == 1_150_000.0
