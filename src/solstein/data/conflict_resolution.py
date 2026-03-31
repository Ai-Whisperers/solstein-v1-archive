"""Conflict resolution strategies for data merging.

E3: Extract merge/conflict resolver adapter from unified_loader.py
Provides pluggable strategies for resolving data conflicts during merge operations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Any, Protocol

from loguru import logger


class ConflictStrategy(Enum):
    """Available conflict resolution strategies."""

    SOURCE_PRIORITY = auto()  # Prefer data from higher-priority source
    RECENCY_WINS = auto()  # Prefer most recently updated data
    MAXIMUM_VALUE = auto()  # Prefer larger numeric values
    MINIMUM_VALUE = auto()  # Prefer smaller numeric values
    CONCATENATE = auto()  # Combine string values
    UNION = auto()  # Union of list values
    INTERSECTION = auto()  # Intersection of list values
    MANUAL_REVIEW = auto()  # Flag for manual review


@dataclass(frozen=True)
class FieldConflict:
    """Represents a conflict between two values for the same field."""

    field_name: str
    existing_value: Any
    incoming_value: Any
    existing_source: str = "unknown"
    incoming_source: str = "unknown"
    existing_timestamp: datetime | None = None
    incoming_timestamp: datetime | None = None
    existing_confidence: float = 0.5
    incoming_confidence: float = 0.5


class ConflictResolution(Protocol):
    """Protocol for conflict resolution results."""

    resolved_value: Any
    strategy_used: ConflictStrategy
    requires_review: bool
    notes: str


@dataclass(frozen=True)
class ResolutionResult:
    """Result of conflict resolution."""

    resolved_value: Any
    strategy_used: ConflictStrategy
    requires_review: bool = False
    notes: str = ""


class ConflictResolver(ABC):
    """Abstract base class for conflict resolvers."""

    @abstractmethod
    def resolve(self, conflict: FieldConflict) -> ResolutionResult:
        """Resolve a field conflict.

        Args:
            conflict: The conflict to resolve

        Returns:
            Resolution result with resolved value and metadata
        """
        ...


class SourcePriorityResolver(ConflictResolver):
    """Resolves conflicts based on source priority.

    Higher-priority sources win when there are conflicts.
    """

    # Default source priorities (lower number = higher priority)
    DEFAULT_PRIORITIES: dict[str, int] = {
        "sec_edgar": 1,  # Most authoritative for public companies
        "crunchbase": 2,  # Good for startups/funding
        "linkedin": 3,  # Good for employee data
        "github": 4,  # Good for tech signals
        "pitchbook": 2,  # Good for PE/VC data
        "bloomberg": 1,  # Authoritative financial data
        "manual_entry": 0,  # Highest priority - human verified
        "web_scrape": 10,  # Lowest priority - least reliable
        "unknown": 100,
    }

    def __init__(self, priorities: dict[str, int] | None = None) -> None:
        self.priorities = priorities or self.DEFAULT_PRIORITIES

    def resolve(self, conflict: FieldConflict) -> ResolutionResult:
        """Resolve using source priority."""
        existing_priority = self.priorities.get(conflict.existing_source, 100)
        incoming_priority = self.priorities.get(conflict.incoming_source, 100)

        if incoming_priority < existing_priority:
            return ResolutionResult(
                resolved_value=conflict.incoming_value,
                strategy_used=ConflictStrategy.SOURCE_PRIORITY,
                notes=f"Incoming source '{conflict.incoming_source}' has higher priority ({incoming_priority} vs {existing_priority})",
            )
        else:
            return ResolutionResult(
                resolved_value=conflict.existing_value,
                strategy_used=ConflictStrategy.SOURCE_PRIORITY,
                notes=f"Existing source '{conflict.existing_source}' has higher or equal priority",
            )


class RecencyResolver(ConflictResolver):
    """Resolves conflicts based on data recency.

    More recent data wins. Falls back to confidence if timestamps unavailable.
    """

    def resolve(self, conflict: FieldConflict) -> ResolutionResult:
        """Resolve using recency."""
        # If we have timestamps, use them
        if conflict.existing_timestamp and conflict.incoming_timestamp:
            if conflict.incoming_timestamp > conflict.existing_timestamp:
                return ResolutionResult(
                    resolved_value=conflict.incoming_value,
                    strategy_used=ConflictStrategy.RECENCY_WINS,
                    notes=f"Incoming data is newer ({conflict.incoming_timestamp} vs {conflict.existing_timestamp})",
                )
            else:
                return ResolutionResult(
                    resolved_value=conflict.existing_value,
                    strategy_used=ConflictStrategy.RECENCY_WINS,
                    notes="Existing data is newer or same age",
                )

        # Fall back to confidence scores
        if conflict.incoming_confidence > conflict.existing_confidence:
            return ResolutionResult(
                resolved_value=conflict.incoming_value,
                strategy_used=ConflictStrategy.RECENCY_WINS,
                notes=f"Using confidence fallback: incoming has higher confidence ({conflict.incoming_confidence} vs {conflict.existing_confidence})",
            )

        return ResolutionResult(
            resolved_value=conflict.existing_value,
            strategy_used=ConflictStrategy.RECENCY_WINS,
            notes="Using confidence fallback: existing has higher or equal confidence",
        )


class NumericResolver(ConflictResolver):
    """Resolves conflicts for numeric fields.

    Can prefer maximum (e.g., revenue, funding) or minimum (e.g., risk scores).
    """

    def __init__(self, prefer_maximum: bool = True) -> None:
        self.prefer_maximum = prefer_maximum

    def resolve(self, conflict: FieldConflict) -> ResolutionResult:
        """Resolve numeric conflict."""
        try:
            existing_num = float(conflict.existing_value)  # type: ignore
            incoming_num = float(conflict.incoming_value)  # type: ignore

            if self.prefer_maximum:
                if incoming_num > existing_num:
                    return ResolutionResult(
                        resolved_value=conflict.incoming_value,
                        strategy_used=ConflictStrategy.MAXIMUM_VALUE,
                        notes=f"Incoming value {incoming_num} > existing {existing_num}",
                    )
                else:
                    return ResolutionResult(
                        resolved_value=conflict.existing_value,
                        strategy_used=ConflictStrategy.MAXIMUM_VALUE,
                        notes=f"Existing value {existing_num} >= incoming {incoming_num}",
                    )
            else:
                if incoming_num < existing_num:
                    return ResolutionResult(
                        resolved_value=conflict.incoming_value,
                        strategy_used=ConflictStrategy.MINIMUM_VALUE,
                        notes=f"Incoming value {incoming_num} < existing {existing_num}",
                    )
                else:
                    return ResolutionResult(
                        resolved_value=conflict.existing_value,
                        strategy_used=ConflictStrategy.MINIMUM_VALUE,
                        notes=f"Existing value {existing_num} <= incoming {incoming_num}",
                    )
        except (TypeError, ValueError) as e:
            logger.warning(
                "Numeric resolution failed, falling back to source priority",
                error=str(e),
            )
            # Fall back to source priority
            return SourcePriorityResolver().resolve(conflict)


class StringResolver(ConflictResolver):
    """Resolves conflicts for string fields.

    Can concatenate or prefer longer/more detailed strings.
    """

    def __init__(self, concatenate: bool = False, separator: str = " | ") -> None:
        self.concatenate = concatenate
        self.separator = separator

    def resolve(self, conflict: FieldConflict) -> ResolutionResult:
        """Resolve string conflict."""
        existing = str(conflict.existing_value or "")
        incoming = str(conflict.incoming_value or "")

        if existing == incoming:
            return ResolutionResult(
                resolved_value=conflict.existing_value,
                strategy_used=ConflictStrategy.CONCATENATE,
                notes="Values are identical",
            )

        if self.concatenate:
            # Concatenate unique values
            if existing in incoming:
                return ResolutionResult(
                    resolved_value=conflict.incoming_value,
                    strategy_used=ConflictStrategy.CONCATENATE,
                    notes="Incoming contains existing",
                )
            if incoming in existing:
                return ResolutionResult(
                    resolved_value=conflict.existing_value,
                    strategy_used=ConflictStrategy.CONCATENATE,
                    notes="Existing contains incoming",
                )

            combined = f"{existing}{self.separator}{incoming}"
            return ResolutionResult(
                resolved_value=combined,
                strategy_used=ConflictStrategy.CONCATENATE,
                notes="Concatenated values",
            )

        # Prefer longer/more detailed string
        if len(incoming) > len(existing):
            return ResolutionResult(
                resolved_value=conflict.incoming_value,
                strategy_used=ConflictStrategy.CONCATENATE,
                notes=f"Incoming is more detailed ({len(incoming)} vs {len(existing)} chars)",
            )

        return ResolutionResult(
            resolved_value=conflict.existing_value,
            strategy_used=ConflictStrategy.CONCATENATE,
            notes=f"Existing is more detailed or equal ({len(existing)} vs {len(incoming)} chars)",
        )


class ListResolver(ConflictResolver):
    """Resolves conflicts for list fields.

    Can use union (combine all) or intersection (only common elements).
    """

    def __init__(self, strategy: ConflictStrategy = ConflictStrategy.UNION) -> None:
        if strategy not in (ConflictStrategy.UNION, ConflictStrategy.INTERSECTION):
            raise ValueError(f"ListResolver only supports UNION or INTERSECTION, got {strategy}")
        self.strategy = strategy

    def resolve(self, conflict: FieldConflict) -> ResolutionResult:
        """Resolve list conflict."""
        try:
            existing_list = list(conflict.existing_value or [])
            incoming_list = list(conflict.incoming_value or [])

            if self.strategy == ConflictStrategy.UNION:
                # Union: combine all unique elements
                combined = list(dict.fromkeys(existing_list + incoming_list))
                return ResolutionResult(
                    resolved_value=combined,
                    strategy_used=ConflictStrategy.UNION,
                    notes=f"Union: {len(existing_list)} + {len(incoming_list)} = {len(combined)} unique",
                )
            else:
                # Intersection: only common elements
                common = [x for x in existing_list if x in incoming_list]
                return ResolutionResult(
                    resolved_value=common,
                    strategy_used=ConflictStrategy.INTERSECTION,
                    notes=f"Intersection: {len(common)} common elements",
                )
        except TypeError as e:
            logger.warning(
                "List resolution failed, falling back to source priority",
                error=str(e),
            )
            return SourcePriorityResolver().resolve(conflict)


class CompositeResolver(ConflictResolver):
    """Composite resolver that delegates to field-specific resolvers.

    E3: Main entry point for conflict resolution in unified loader.
    """

    # Field-specific resolution strategies
    FIELD_STRATEGIES: dict[str, ConflictResolver] = {
        # Numeric fields - prefer maximum (revenue, funding)
        "revenue": NumericResolver(prefer_maximum=True),
        "valuation": NumericResolver(prefer_maximum=True),
        "funding_total": NumericResolver(prefer_maximum=True),
        "employees": NumericResolver(prefer_maximum=True),
        # Risk scores - prefer minimum (lower risk)
        "risk_score": NumericResolver(prefer_maximum=False),
        # String fields - concatenate descriptions
        "description": StringResolver(concatenate=False),
        # List fields - union
        "competitors": ListResolver(ConflictStrategy.UNION),
        "investors": ListResolver(ConflictStrategy.UNION),
        "tags": ListResolver(ConflictStrategy.UNION),
    }

    def __init__(
        self,
        field_strategies: dict[str, ConflictResolver] | None = None,
        default_resolver: ConflictResolver | None = None,
    ) -> None:
        self.field_strategies = field_strategies or self.FIELD_STRATEGIES
        self.default_resolver = default_resolver or RecencyResolver()

    def resolve(self, conflict: FieldConflict) -> ResolutionResult:
        """Resolve conflict using field-specific or default strategy."""
        resolver = self.field_strategies.get(conflict.field_name, self.default_resolver)
        return resolver.resolve(conflict)

    def resolve_merge(
        self,
        existing: dict[str, Any],
        incoming: dict[str, Any],
        existing_source: str = "unknown",
        incoming_source: str = "unknown",
        adjudication_decisions: dict[str, dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Resolve all conflicts between two records.

        Args:
            existing: Existing record
            incoming: Incoming record with potential updates
            existing_source: Source of existing data
            incoming_source: Source of incoming data

        Returns:
            Merged record with conflicts resolved
        """
        merged = dict(existing)

        for key, incoming_value in incoming.items():
            if incoming_value is None:
                continue

            existing_value = merged.get(key)

            # No conflict if existing is None or values are equal
            if existing_value is None:
                merged[key] = incoming_value
                continue

            if existing_value == incoming_value:
                continue

            decision = (adjudication_decisions or {}).get(key)
            if isinstance(decision, dict):
                action = str(decision.get("decision", decision.get("status", ""))).lower()
                if action in {"existing", "keep_existing", "approved_existing", "approve_existing"}:
                    continue
                if action in {"incoming", "approved", "approve_incoming", "approved_incoming"}:
                    merged[key] = incoming_value
                    continue
                if action in {"override", "resolved"} and "value" in decision:
                    merged[key] = decision["value"]
                    continue

            # Create conflict and resolve
            conflict = FieldConflict(
                field_name=key,
                existing_value=existing_value,
                incoming_value=incoming_value,
                existing_source=existing_source,
                incoming_source=incoming_source,
            )

            result = self.resolve(conflict)
            merged[key] = result.resolved_value

            if result.requires_review:
                logger.warning(
                    "Conflict requires manual review",
                    field=key,
                    existing=existing_value,
                    incoming=incoming_value,
                    notes=result.notes,
                )

        return merged
