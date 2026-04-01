"""Notification service: Slack and Email channels for pipeline events.

STORY-104: Adds async, fire-and-forget notification delivery for
research completion, failures, source degradation, and export readiness.

Event types:
- research.completed
- research.failed
- source.degraded
- dlq.threshold_exceeded
- export.ready
"""

from solstein.notifications.channels import (
    EmailChannel,
    NotificationChannel,
    SlackChannel,
)
from solstein.notifications.dispatcher import NotificationDispatcher
from solstein.notifications.events import NotificationEvent

__all__ = [
    "EmailChannel",
    "NotificationChannel",
    "NotificationDispatcher",
    "NotificationEvent",
    "SlackChannel",
]
