"""Base refresh connector interface and delta detection for incremental updates."""

import hashlib
import uuid
from dataclasses import dataclass
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Any

from loguru import logger
from sqlalchemy import text

from solstein.domain.facts import Fact, GatheringBatch
from solstein.infrastructure.database import DatabaseManager


@dataclass(frozen=True)
class RefreshStatus:
    source_name: str
    source_type: str
    last_refresh_time: datetime | None
    next_scheduled_time: datetime | None
    refresh_interval_seconds: int
    stale: bool
    stale_reason: str | None
    freshness_window_hours: float


class BaseRefreshConnector(ABC):
    """Abstract base class for data source refresh connectors.

    Provides interface for:
    - Incremental refresh (only fetch changed data)
    - Delta detection (compare new vs stored facts)
    - Refresh metadata tracking
    """

    def __init__(
        self,
        source_name: str,
        source_type: str,
        db_manager: DatabaseManager | None,
        confidence: float = 0.5,
    ):
        self.source_name: str = source_name
        self.source_type: str = source_type
        self.db_manager: DatabaseManager | None = db_manager
        self.confidence: float = confidence

    def _require_db_manager(self) -> DatabaseManager:
        """Assert db_manager is set; raise if not."""
        if self.db_manager is None:
            raise RuntimeError(f"{type(self).__name__} requires a db_manager but none was provided.")
        return self.db_manager

    @abstractmethod
    async def fetch_facts(
        self,
        company_ids: list[str],
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch facts from the data source.

        Args:
            company_ids: List of company IDs to fetch data for
            start_date: Start date for data range
            end_date: End date for data range

        Returns:
            List of fact dictionaries
        """
        pass

    async def get_facts_to_refresh(
        self,
        company_ids: list[str],
        since: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Get only facts that have changed since last refresh.

        Args:
            company_ids: List of company IDs to check
            since: Last refresh time (if None, gets last from metadata)

        Returns:
            List of facts that need updating
        """
        if since is None:
            since = await self._get_last_refresh_time()

        # Fetch all facts from source
        all_facts = await self.fetch_facts(company_ids)

        # Filter to only changed facts
        changed_facts = await self._filter_delta(all_facts, since)

        logger.info(f"{self.source_name}: {len(changed_facts)}/{len(all_facts)} facts changed since {since}")

        return changed_facts

    async def _get_last_refresh_time(self) -> datetime:
        """Get last successful refresh time from metadata."""
        async with self._require_db_manager().get_session() as session:
            result = await session.execute(
                text(
                    """
                    SELECT last_refresh_time
                    FROM refresh_metadata
                    WHERE source_name = :name
                    """
                ),
                {"name": self.source_name},
            )
            row = result.fetchone()
            if row and row[0]:
                return row[0]
            # Default to 30 days ago if no previous refresh
            return datetime.now() - timedelta(days=30)

    async def _filter_delta(self, facts: list[dict[str, Any]], since: datetime) -> list[dict[str, Any]]:
        """Filter facts to only return changed data since last refresh.

        Default implementation compares fact hashes.
        Subclasses can override for source-specific delta detection.
        """
        changed_facts = []

        for fact in facts:
            company_id = fact.get("company_id")
            fact_type = fact.get("fact_type")
            value = fact.get("value")

            if not company_id or not fact_type:
                continue

            # Compute hash of new fact
            new_hash = compute_fact_hash(company_id, fact_type, value)

            # Check if fact exists and has changed
            if await self._fact_changed(company_id, fact_type, new_hash):
                fact["_hash"] = new_hash  # Store hash for later comparison
                changed_facts.append(fact)

        return changed_facts

    async def _fact_changed(self, company_id: str, fact_type: str, new_hash: str) -> bool:
        """Check if a fact has changed compared to stored version."""
        async with self._require_db_manager().get_session() as session:
            result = await session.execute(
                text(
                    """
                    SELECT value_hash
                    FROM facts
                    WHERE company_id = :cid
                    AND fact_type = :ft
                    AND source = :src
                    ORDER BY extracted_at DESC
                    LIMIT 1
                    """
                ),
                {"cid": company_id, "ft": fact_type, "src": self.source_name},
            )
            row = result.fetchone()

            if not row:
                # Fact doesn't exist, so it's "changed" (new)
                return True

            stored_hash = row[0]
            return stored_hash != new_hash

    async def store_facts(
        self,
        facts: list[dict[str, Any]],
        batch_id: str | None = None,
    ) -> GatheringBatch:
        """Store facts to database with metadata tracking.

        Args:
            facts: List of fact dictionaries to store
            batch_id: Optional batch ID (generated if not provided)

        Returns:
            GatheringBatch with storage results
        """
        if batch_id is None:
            batch_id = str(uuid.uuid4())

        batch = GatheringBatch(
            batch_id=batch_id,
            source=self.source_name,
            facts=[],
        )

        refresh_time = datetime.now()

        async with self._require_db_manager().get_session() as session:
            for fact_data in facts:
                try:
                    # Compute hash if not already present
                    value_hash = fact_data.get("_hash") or compute_fact_hash(
                        fact_data["company_id"],
                        fact_data["fact_type"],
                        fact_data["value"],
                    )

                    fact = Fact(
                        company_id=fact_data["company_id"],
                        fact_type=fact_data["fact_type"],
                        value=fact_data["value"],
                        confidence=fact_data.get("confidence", self.confidence),
                        extracted_at=fact_data.get("extracted_at", refresh_time),
                        source=self.source_name,
                        source_type=self.source_type,
                        batch_id=batch_id,
                        metadata=fact_data.get("metadata", {}),
                        value_hash=value_hash,
                    )

                    session.add(fact)
                    batch.facts.append(fact)

                except Exception as e:
                    logger.error(f"Failed to store fact: {e}")
                    batch.errors.append(str(e))

            await session.commit()

        # Update refresh metadata
        await self._update_refresh_metadata(refresh_time)

        return batch

    async def _update_refresh_metadata(self, refresh_time: datetime) -> None:
        async with self._require_db_manager().get_session() as session:
            await session.execute(
                text(
                    """
                    INSERT INTO refresh_metadata (source_name, source_type, last_refresh_time, last_refresh_status, last_refresh_job_id, next_scheduled_time)
                    VALUES (:name, :type, :time, :status, :job, :next)
                    ON CONFLICT (source_name) DO UPDATE SET
                        last_refresh_time = :time,
                        last_refresh_status = :status,
                        last_refresh_job_id = :job,
                        next_scheduled_time = :next
                    """
                ),
                {
                    "name": self.source_name,
                    "type": self.source_type,
                    "time": refresh_time,
                    "status": "completed",
                    "job": str(uuid.uuid4()),
                    "next": refresh_time + timedelta(hours=24),
                },
            )
            await session.commit()


def _compute_stale(
    last_refresh_time: datetime | None,
    refresh_interval_seconds: int,
    now: datetime,
) -> tuple[bool, str | None]:
    if last_refresh_time is None:
        return True, "no refresh recorded"
    if now - last_refresh_time > timedelta(seconds=refresh_interval_seconds):
        return True, "last refresh exceeded freshness window"
    return False, None


def build_refresh_snapshot(statuses: list[RefreshStatus], generated_at: datetime) -> dict[str, object]:
    stale_count = sum(1 for status in statuses if status.stale)
    fresh_count = len(statuses) - stale_count
    overall_stale = stale_count > 0 or not statuses
    return {
        "generated_at": generated_at.isoformat(),
        "overall_stale": overall_stale,
        "stale_count": stale_count,
        "fresh_count": fresh_count,
        "statuses": [
            {
                "source_name": status.source_name,
                "source_type": status.source_type,
                "last_refresh_time": status.last_refresh_time.isoformat() if status.last_refresh_time else None,
                "next_scheduled_time": status.next_scheduled_time.isoformat() if status.next_scheduled_time else None,
                "refresh_interval_seconds": status.refresh_interval_seconds,
                "freshness_window_hours": status.freshness_window_hours,
                "stale": status.stale,
                "stale_reason": status.stale_reason,
            }
            for status in statuses
        ],
    }


def raise_if_stale(statuses: list[RefreshStatus]) -> None:
    stale_reasons = [f"{status.source_name}:{status.stale_reason or 'stale'}" for status in statuses if status.stale]
    if stale_reasons:
        raise ValueError("Stale refresh metadata detected: " + "; ".join(stale_reasons))


async def get_refresh_statuses(
    db_manager: DatabaseManager,
    source_name: str | None = None,
    now: datetime | None = None,
) -> list[RefreshStatus]:
    current_time = now or datetime.now(timezone.utc)
    query = (
        "SELECT source_name, source_type, last_refresh_time, next_scheduled_time, refresh_interval_seconds "
        "FROM refresh_metadata"
    )
    params = {}
    if source_name:
        query += " WHERE source_name = :name"
        params["name"] = source_name

    async with db_manager.get_session() as session:
        result = await session.execute(text(query), params)
        rows = result.fetchall()

    statuses: list[RefreshStatus] = []
    for row in rows:
        last_refresh_time = row[2]
        refresh_interval_seconds = row[4] or 0
        stale, reason = _compute_stale(last_refresh_time, refresh_interval_seconds, current_time)
        statuses.append(
            RefreshStatus(
                source_name=row[0],
                source_type=row[1],
                last_refresh_time=last_refresh_time,
                next_scheduled_time=row[3],
                refresh_interval_seconds=refresh_interval_seconds,
                stale=stale,
                stale_reason=reason,
                freshness_window_hours=refresh_interval_seconds / 3600 if refresh_interval_seconds else 0.0,
            )
        )
    return statuses


def compute_fact_hash(company_id: str, fact_type: str, value: Any) -> str:
    """Compute hash for fact to detect changes."""
    content = f"{company_id}:{fact_type}:{value}"
    return hashlib.sha256(content.encode()).hexdigest()
