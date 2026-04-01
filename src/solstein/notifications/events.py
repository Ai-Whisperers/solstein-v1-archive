"""Notification event types and payloads.

STORY-104: Defines the event schema for all notification types.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class EventType(str, Enum):
    """Supported notification event types."""

    RESEARCH_COMPLETED = "research.completed"
    RESEARCH_FAILED = "research.failed"
    SOURCE_DEGRADED = "source.degraded"
    DLQ_THRESHOLD_EXCEEDED = "dlq.threshold_exceeded"
    EXPORT_READY = "export.ready"


@dataclass
class NotificationEvent:
    """A notification event to be dispatched to configured channels.

    Attributes:
        event_type: The type of event (from EventType enum).
        title: Human-readable event title.
        message: Detailed event message.
        metadata: Additional structured data for templates.
        timestamp: When the event occurred.
        tenant_id: Optional tenant scope for multi-tenant routing.
        user_id: Optional user scope for preference filtering.
    """

    event_type: EventType
    title: str
    message: str
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tenant_id: str | None = None
    user_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize for logging and transport."""
        return {
            "event_type": self.event_type.value,
            "title": self.title,
            "message": self.message,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
        }


def research_completed_event(
    company_name: str,
    duration_seconds: float,
    score: float | None = None,
    tenant_id: str | None = None,
    user_id: str | None = None,
) -> NotificationEvent:
    """Create a research.completed notification event."""
    duration_min = duration_seconds / 60.0
    score_str = f" | Score: {score:.2f}" if score is not None else ""
    return NotificationEvent(
        event_type=EventType.RESEARCH_COMPLETED,
        title=f"Research completed: {company_name}",
        message=(
            f"Research pipeline for {company_name} completed in "
            f"{duration_min:.1f} minutes{score_str}."
        ),
        metadata={
            "company_name": company_name,
            "duration_seconds": duration_seconds,
            "score": score,
        },
        tenant_id=tenant_id,
        user_id=user_id,
    )


def research_failed_event(
    company_name: str,
    error_summary: str,
    tenant_id: str | None = None,
    user_id: str | None = None,
) -> NotificationEvent:
    """Create a research.failed notification event."""
    return NotificationEvent(
        event_type=EventType.RESEARCH_FAILED,
        title=f"Research failed: {company_name}",
        message=f"Research pipeline for {company_name} failed: {error_summary}",
        metadata={
            "company_name": company_name,
            "error_summary": error_summary,
        },
        tenant_id=tenant_id,
        user_id=user_id,
    )


def source_degraded_event(
    source_name: str,
    failure_reason: str,
    consecutive_failures: int,
) -> NotificationEvent:
    """Create a source.degraded notification event."""
    return NotificationEvent(
        event_type=EventType.SOURCE_DEGRADED,
        title=f"Data source degraded: {source_name}",
        message=(
            f"Source {source_name} marked DEGRADED after {consecutive_failures} "
            f"consecutive failures. Reason: {failure_reason}"
        ),
        metadata={
            "source_name": source_name,
            "failure_reason": failure_reason,
            "consecutive_failures": consecutive_failures,
        },
    )
