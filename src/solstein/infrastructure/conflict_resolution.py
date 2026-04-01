"""Conflict resolution engine for handling data source conflicts.

Resolves data conflicts using a priority chain:
1. **Recency** — newer timestamps win when both facts have ``extracted_at``
2. **Reliability** — higher :class:`SourceAuthority` rank wins on equal timestamps
3. **Confidence** — higher confidence score wins when authority is equal
4. **Manual review** — persisted :class:`ManualReviewRecord` for ambiguous cases

See STORY-013 for the decision matrix and rationale.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
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

    Reliability rankings (rationale):
    - **SEC_EDGAR (1.0)**: Official US regulatory filings — legally mandated accuracy
    - **COMPANIES_HOUSE (0.95)**: Official UK registry — government-verified
    - **YAHOO_FINANCE (0.88)**: Aggregated market data — high coverage, slight lag
    - **GLOBAL_MARKET (0.87)**: Market indices — reliable but broad
    - **GITHUB (0.85)**: Technical signals — first-party but self-reported
    - **WEBSITE (0.84)**: Corporate websites — first-party, marketing bias
    - **PATENTS (0.80)**: Patent office data — official but lagging
    - **LINKEDIN (0.75)**: Professional data — self-reported, often outdated
    - **FUNDING (0.73)**: Funding databases — relies on voluntary disclosure
    - **NEWS (0.72)**: News articles — secondary source, variable accuracy
    - **NEWS_SIGNAL (0.70)**: Sentiment signals — derived, noisy
    - **WEB_SEARCH (0.68)**: Web search results — unverified, variable quality
    - **STATIC_CATALOG (0.65)**: Static reference data — may be stale
    - **COMPETITOR_JSON (0.60)**: Competitor JSON files — manually curated, lowest freshness
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


@dataclass
class ManualReviewRecord:
    """Persisted record for conflicts requiring manual operator review.

    Created when the resolution engine cannot automatically determine
    a winner. Operators query these records to resolve ambiguous conflicts.
    """

    review_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    company_id: str = ""
    fact_type: str = ""
    existing_fact: dict[str, Any] = field(default_factory=dict)
    new_fact: dict[str, Any] = field(default_factory=dict)
    reason: str = ""
    status: str = "pending"  # pending | resolved | dismissed
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: datetime | None = None
    resolved_by: str | None = None


class ManualReviewQueue:
    """In-memory queue for conflicts requiring operator review (STORY-013 REQ-3).

    Persists :class:`ManualReviewRecord` instances and provides query/resolve
    operations so operators can list and act on ambiguous conflicts.
    """

    def __init__(self) -> None:
        self._records: list[ManualReviewRecord] = []

    def add(self, record: ManualReviewRecord) -> None:
        """Append a new review record to the queue."""
        self._records.append(record)

    def get_pending(self) -> list[ManualReviewRecord]:
        """Return all records with status ``pending``."""
        return [r for r in self._records if r.status == "pending"]

    def get_by_id(self, review_id: str) -> ManualReviewRecord | None:
        """Look up a single record by its ``review_id``."""
        for record in self._records:
            if record.review_id == review_id:
                return record
        return None

    def resolve(
        self,
        review_id: str,
        resolved_by: str,
        status: str = "resolved",
    ) -> ManualReviewRecord | None:
        """Mark a review record as resolved or dismissed.

        Args:
            review_id: The UUID of the review record.
            resolved_by: Identifier of the operator (email, username, etc.).
            status: New status — ``"resolved"`` or ``"dismissed"``.

        Returns:
            The updated record, or ``None`` if not found.
        """
        record = self.get_by_id(review_id)
        if record is None:
            logger.warning(f"Review record not found: {review_id}")
            return None
        record.status = status
        record.resolved_at = datetime.now(tz=timezone.utc)
        record.resolved_by = resolved_by
        logger.info(f"Review {review_id} marked as {status} by {resolved_by}")
        return record

    def __len__(self) -> int:
        return len(self._records)

    def __getitem__(self, index: int) -> ManualReviewRecord:
        return self._records[index]

    def __iter__(self):  # noqa: ANN204
        return iter(self._records)


class ConflictResolutionEngine:
    """Engine for detecting and resolving conflicts between data sources.

    Uses a priority chain: recency > reliability > confidence > manual review.
    """

    def __init__(self) -> None:
        self.authority_map: dict[str, SourceAuthority] = {
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
        self.manual_review_queue: ManualReviewQueue = ManualReviewQueue()

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
                    detected_at=datetime.now(tz=timezone.utc),
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
            resolved_at=datetime.now(tz=timezone.utc),
        )

        self.resolution_log.append(resolution)
        logger.info(
            f"Conflict resolved: {conflict.company_id} {conflict.fact_type} - "
            f"Winner: {winning_fact.get('source')} using {strategy.value}"
        )

        return resolution

    def _select_strategy(self, conflict: Conflict) -> ConflictStrategy:
        """Auto-select best strategy based on conflict characteristics.

        Decision priority chain (STORY-013):
        1. **Recency** — if both facts have timestamps and they differ,
           the newer record wins (NEWER_TIMESTAMP).
        2. **Reliability** — if timestamps are equal or only one exists,
           use source authority ranking (AUTHORITATIVE_SOURCE).
        3. **Confidence** — if authority is equal or unknown, pick the
           fact with higher confidence (HIGHER_CONFIDENCE).
        4. **Manual review** — when none of the above can discriminate,
           create a persisted review record (MANUAL_REVIEW).
        """
        existing_time = conflict.existing_fact.get("extracted_at")
        new_time = conflict.new_fact.get("extracted_at")

        # Priority 1: Recency — newer timestamp wins when both are present
        if existing_time and new_time:
            et = self._normalise_datetime(existing_time)
            nt = self._normalise_datetime(new_time)
            if et != nt:
                return ConflictStrategy.NEWER_TIMESTAMP

        # Priority 2: Source reliability (tiebreaker when recency is equal)
        existing_source = conflict.existing_fact.get("source", "")
        new_source = conflict.new_fact.get("source", "")
        existing_auth = self.authority_map.get(existing_source)
        new_auth = self.authority_map.get(new_source)

        if existing_auth and new_auth and existing_auth != new_auth:
            return ConflictStrategy.AUTHORITATIVE_SOURCE

        # Priority 3: Confidence score
        existing_conf = conflict.existing_fact.get("confidence", 0.5)
        new_conf = conflict.new_fact.get("confidence", 0.5)
        conf_diff = abs(existing_conf - new_conf)

        if conf_diff >= 0.1:
            return ConflictStrategy.HIGHER_CONFIDENCE

        # Priority 4: Cannot auto-resolve — require manual review
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
                # Normalize to datetime for safe comparison
                if isinstance(existing_time, str):
                    existing_time = datetime.fromisoformat(existing_time)
                if isinstance(new_time, str):
                    new_time = datetime.fromisoformat(new_time)
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
            record = ManualReviewRecord(
                company_id=conflict.company_id,
                fact_type=conflict.fact_type,
                existing_fact=existing,
                new_fact=new,
                reason=(
                    f"Automatic resolution could not determine a winner for "
                    f"{conflict.company_id} / {conflict.fact_type}. "
                    f"Both facts have similar confidence and no clear recency or "
                    f"reliability advantage."
                ),
                created_at=conflict.detected_at,
            )
            self.manual_review_queue.add(record)
            logger.warning(
                f"Manual review record created ({record.review_id}): {conflict.company_id} {conflict.fact_type}"
            )
            # Keep existing as the provisional value until an operator resolves
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

    @staticmethod
    def _normalise_datetime(value: str | datetime) -> datetime:
        """Normalise a timestamp value to a :class:`datetime` instance."""
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        return value

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

    # ------------------------------------------------------------------
    # Manual review queue delegations (STORY-013 REQ-3)
    # ------------------------------------------------------------------

    def get_pending_reviews(self) -> list[ManualReviewRecord]:
        """Return all manual review records with status ``pending``."""
        return self.manual_review_queue.get_pending()

    def get_review_by_id(self, review_id: str) -> ManualReviewRecord | None:
        """Look up a single review record by its ``review_id``."""
        return self.manual_review_queue.get_by_id(review_id)

    def resolve_review(
        self,
        review_id: str,
        resolved_by: str,
        status: str = "resolved",
    ) -> ManualReviewRecord | None:
        """Delegate to :meth:`ManualReviewQueue.resolve`."""
        return self.manual_review_queue.resolve(review_id, resolved_by, status)

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def get_resolution_stats(self) -> dict[str, Any]:
        """Get statistics on conflict resolutions."""
        if not self.resolution_log:
            return {"total_resolved": 0}

        strategy_counts: dict[str, int] = {}
        for resolution in self.resolution_log:
            strategy = resolution.strategy_used.value
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1

        return {
            "total_resolved": len(self.resolution_log),
            "strategy_breakdown": strategy_counts,
            "sources_involved": list(self.authority_map.keys()),
            "pending_reviews": len(self.get_pending_reviews()),
        }
