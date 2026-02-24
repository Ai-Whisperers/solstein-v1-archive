"""Conflict resolution engine for handling data source conflicts."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from loguru import logger


class ConflictStrategy(Enum):
    """Strategies for resolving conflicts between data sources."""

    HIGHER_CONFIDENCE = "higher_confidence"
    NEWER_TIMESTAMP = "newer_timestamp"
    AUTHORITATIVE_SOURCE = "authoritative_source"
    MANUAL_REVIEW = "manual_review"


class SourceAuthority(Enum):
    """Authority levels for different data sources.

    Higher values indicate more authoritative sources that win
    when facts conflict between sources.
    """

    # Most authoritative - official government/regulatory sources
    SEC_EDGAR = 1.0
    COMPANIES_HOUSE = 0.95

    # Highly authoritative - financial market data
    YAHOO_FINANCE = 0.88
    GLOBAL_MARKET = 0.87

    # Authoritative - technical and corporate data
    GITHUB = 0.85
    WEBSITE = 0.84
    PATENTS = 0.80

    # Moderate authority - professional and industry data
    LINKEDIN = 0.75
    FUNDING = 0.73

    # Lower authority - news and general market signals
    NEWS = 0.72
    NEWS_SIGNAL = 0.70
    WEB_SEARCH = 0.68

    # Lowest authority - catalog and reference data
    STATIC_CATALOG = 0.65
    COMPETITOR_JSON = 0.60


@dataclass
class Conflict:
    """Represents a conflict between facts from different sources."""

    company_id: str
    fact_type: str
    existing_fact: dict[str, Any]
    new_fact: dict[str, Any]
    conflict_type: str
    detected_at: datetime


@dataclass
class Resolution:
    """Result of conflict resolution."""

    conflict: Conflict
    winning_fact: dict[str, Any]
    strategy_used: ConflictStrategy
    reason: str
    resolved_at: datetime


class ConflictResolutionEngine:
    """Engine for detecting and resolving conflicts between data sources.

    Uses multiple strategies:
    - Higher confidence wins
    - Authoritative source priority
    - Newer timestamp wins
    - Manual review for critical conflicts
    """

    def __init__(self):
        self.authority_map = {
            "sec_edgar": SourceAuthority.SEC_EDGAR,
            "companies_house": SourceAuthority.COMPANIES_HOUSE,
            "yahoo_finance": SourceAuthority.YAHOO_FINANCE,
            "github": SourceAuthority.GITHUB,
            "news_signal": SourceAuthority.NEWS_SIGNAL,
            "news": SourceAuthority.NEWS,
            "patents": SourceAuthority.PATENTS,
            "website": SourceAuthority.WEBSITE,
            "linkedin": SourceAuthority.LINKEDIN,
            "funding": SourceAuthority.FUNDING,
            "global_market": SourceAuthority.GLOBAL_MARKET,
            "web_search": SourceAuthority.WEB_SEARCH,
            "static_catalog": SourceAuthority.STATIC_CATALOG,
            "competitor_json": SourceAuthority.COMPETITOR_JSON,
        }
        self.resolution_log: list[Resolution] = []

    def detect_conflicts(
        self,
        existing_facts: list[dict[str, Any]],
        new_facts: list[dict[str, Any]],
    ) -> list[Conflict]:
        """Detect conflicts between existing and new facts.

        A conflict exists when:
        - Same company_id and fact_type
        - Different values
        - Within recent time window (e.g., same reporting period)
        """
        conflicts = []

        # Index existing facts by (company_id, fact_type)
        existing_index = {}
        for fact in existing_facts:
            key = (fact.get("company_id"), fact.get("fact_type"))
            existing_index[key] = fact

        # Check each new fact for conflicts
        for new_fact in new_facts:
            key = (new_fact.get("company_id"), new_fact.get("fact_type"))
            existing_fact = existing_index.get(key)

            if existing_fact and self._values_differ(existing_fact, new_fact):
                conflict = Conflict(
                    company_id=key[0],
                    fact_type=key[1],
                    existing_fact=existing_fact,
                    new_fact=new_fact,
                    conflict_type="value_mismatch",
                    detected_at=datetime.now(),
                )
                conflicts.append(conflict)
                logger.info(
                    f"Conflict detected: {key[0]} {key[1]} - {existing_fact.get('source')} vs {new_fact.get('source')}"
                )

        return conflicts

    def _values_differ(
        self,
        fact1: dict[str, Any],
        fact2: dict[str, Any],
    ) -> bool:
        """Check if two facts have different values."""
        val1 = fact1.get("value")
        val2 = fact2.get("value")

        # Handle nested dict comparison
        if isinstance(val1, dict) and isinstance(val2, dict):
            return val1 != val2

        # Simple value comparison
        return val1 != val2

    def resolve_conflict(
        self,
        conflict: Conflict,
        strategy: ConflictStrategy | None = None,
    ) -> Resolution:
        """Resolve a single conflict using specified or auto-selected strategy."""
        if strategy is None:
            strategy = self._select_strategy(conflict)

        winning_fact = self._apply_strategy(conflict, strategy)

        resolution = Resolution(
            conflict=conflict,
            winning_fact=winning_fact,
            strategy_used=strategy,
            reason=self._get_resolution_reason(conflict, strategy),
            resolved_at=datetime.now(),
        )

        self.resolution_log.append(resolution)
        logger.info(
            f"Conflict resolved: {conflict.company_id} {conflict.fact_type} - "
            f"Winner: {winning_fact.get('source')} using {strategy.value}"
        )

        return resolution

    def _select_strategy(self, conflict: Conflict) -> ConflictStrategy:
        """Auto-select best strategy based on conflict characteristics."""
        existing_source = conflict.existing_fact.get("source", "")
        new_source = conflict.new_fact.get("source", "")

        # Check if one source is more authoritative
        existing_auth = self.authority_map.get(existing_source)
        new_auth = self.authority_map.get(new_source)

        if existing_auth and new_auth:
            if existing_auth != new_auth:
                return ConflictStrategy.AUTHORITATIVE_SOURCE

        # Check confidence difference
        existing_conf = conflict.existing_fact.get("confidence", 0.5)
        new_conf = conflict.new_fact.get("confidence", 0.5)
        conf_diff = abs(existing_conf - new_conf)

        if conf_diff >= 0.1:  # Significant confidence difference
            return ConflictStrategy.HIGHER_CONFIDENCE

        # Check timestamp difference
        existing_time = conflict.existing_fact.get("extracted_at")
        new_time = conflict.new_fact.get("extracted_at")

        if existing_time and new_time:
            return ConflictStrategy.NEWER_TIMESTAMP

        # Default to manual review for unclear cases
        return ConflictStrategy.MANUAL_REVIEW

    def _apply_strategy(
        self,
        conflict: Conflict,
        strategy: ConflictStrategy,
    ) -> dict[str, Any]:
        """Apply resolution strategy to determine winning fact."""
        existing = conflict.existing_fact
        new = conflict.new_fact

        if strategy == ConflictStrategy.HIGHER_CONFIDENCE:
            existing_conf = existing.get("confidence", 0.5)
            new_conf = new.get("confidence", 0.5)
            return new if new_conf > existing_conf else existing

        elif strategy == ConflictStrategy.NEWER_TIMESTAMP:
            existing_time = existing.get("extracted_at")
            new_time = new.get("extracted_at")

            if existing_time and new_time:
                return new if new_time > existing_time else existing
            return new if new_time else existing

        elif strategy == ConflictStrategy.AUTHORITATIVE_SOURCE:
            existing_source = existing.get("source", "")
            new_source = new.get("source", "")

            existing_auth = self.authority_map.get(existing_source)
            new_auth = self.authority_map.get(new_source)

            if existing_auth and new_auth:
                return new if new_auth.value > existing_auth.value else existing

            # Fall back to confidence if authority not mapped
            existing_conf = existing.get("confidence", 0.5)
            new_conf = new.get("confidence", 0.5)
            return new if new_conf > existing_conf else existing

        elif strategy == ConflictStrategy.MANUAL_REVIEW:
            # For manual review, keep existing as default
            # In production, this would flag for human review
            logger.warning(f"Manual review required: {conflict.company_id} {conflict.fact_type}")
            return existing

        # Default to keeping existing
        return existing

    def _get_resolution_reason(
        self,
        conflict: Conflict,
        strategy: ConflictStrategy,
    ) -> str:
        """Generate human-readable reason for resolution."""
        reasons = {
            ConflictStrategy.HIGHER_CONFIDENCE: "Selected fact with higher confidence score",
            ConflictStrategy.NEWER_TIMESTAMP: "Selected more recently extracted fact",
            ConflictStrategy.AUTHORITATIVE_SOURCE: "Selected fact from more authoritative source",
            ConflictStrategy.MANUAL_REVIEW: "Flagged for manual review - unclear resolution",
        }
        return reasons.get(strategy, "Unknown resolution strategy")

    def resolve_all(
        self,
        conflicts: list[Conflict],
        strategy: ConflictStrategy | None = None,
    ) -> list[Resolution]:
        """Resolve all conflicts using specified or auto-selected strategy."""
        resolutions = []
        for conflict in conflicts:
            resolution = self.resolve_conflict(conflict, strategy)
            resolutions.append(resolution)
        return resolutions

    def get_resolution_stats(self) -> dict[str, Any]:
        """Get statistics on conflict resolutions."""
        if not self.resolution_log:
            return {"total_resolved": 0}

        strategy_counts = {}
        for resolution in self.resolution_log:
            strategy = resolution.strategy_used.value
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1

        return {
            "total_resolved": len(self.resolution_log),
            "strategy_breakdown": strategy_counts,
            "sources_involved": list(self.authority_map.keys()),
        }
