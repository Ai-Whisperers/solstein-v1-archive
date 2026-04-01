"""Notification dispatcher: routes events to configured channels.

STORY-104: Central dispatcher that manages channel registration,
per-user preference filtering, and async fire-and-forget delivery.
"""

from __future__ import annotations

import logging
from typing import Any

from solstein.notifications.channels import NotificationChannel
from solstein.notifications.events import EventType, NotificationEvent

logger = logging.getLogger(__name__)


class NotificationDispatcher:
    """Routes notification events to registered channels.

    Features:
    - Multiple channels (Slack, Email, etc.) registered independently
    - Per-user opt-out preferences respected
    - Fire-and-forget: delivery failures are logged, never propagated
    - Channel-level enable/disable for quick operational control
    """

    def __init__(self) -> None:
        self._channels: list[NotificationChannel] = []
        # user_id -> set of opted-out event types
        self._user_preferences: dict[str, set[EventType]] = {}

    def register_channel(self, channel: NotificationChannel) -> None:
        """Register a notification channel."""
        self._channels.append(channel)
        logger.info(
            "[NotificationDispatcher] Registered channel: %s",
            channel.channel_name,
        )

    def set_user_opt_out(self, user_id: str, event_types: list[EventType]) -> None:
        """Set opt-out preferences for a user.

        Args:
            user_id: User identifier.
            event_types: Event types the user does NOT want to receive.
        """
        self._user_preferences[user_id] = set(event_types)

    def _is_opted_out(self, event: NotificationEvent) -> bool:
        """Check if the event's target user has opted out of this event type."""
        if not event.user_id:
            return False
        opted_out = self._user_preferences.get(event.user_id, set())
        return event.event_type in opted_out

    async def dispatch(self, event: NotificationEvent) -> dict[str, bool]:
        """Dispatch a notification event to all registered channels.

        Respects user opt-out preferences. Delivery failures are logged
        but never propagated — this is a fire-and-forget operation.

        Returns:
            Dict mapping channel_name -> delivery success.
        """
        if self._is_opted_out(event):
            logger.info(
                "[NotificationDispatcher] User %s opted out of %s, skipping",
                event.user_id,
                event.event_type.value,
            )
            return {}

        if not self._channels:
            logger.warning(
                "[NotificationDispatcher] No channels registered, notification dropped: %s",
                event.event_type.value,
            )
            return {}

        results: dict[str, bool] = {}
        for channel in self._channels:
            try:
                success = await channel.send(event)
                results[channel.channel_name] = success
            except Exception as exc:
                # Fire-and-forget: log and continue
                logger.error(
                    "[NotificationDispatcher] Channel %s failed: %s",
                    channel.channel_name,
                    exc,
                )
                results[channel.channel_name] = False

        delivered = sum(1 for v in results.values() if v)
        logger.info(
            "[NotificationDispatcher] Event %s dispatched: %d/%d channels succeeded",
            event.event_type.value,
            delivered,
            len(results),
        )
        return results

    def get_status(self) -> dict[str, Any]:
        """Return dispatcher status for health checks."""
        return {
            "channels_registered": len(self._channels),
            "channel_names": [c.channel_name for c in self._channels],
            "users_with_preferences": len(self._user_preferences),
        }
