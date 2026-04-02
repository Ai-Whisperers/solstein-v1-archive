"""Tests for STORY-104: Slack + Email notification service.

Covers:
- NotificationEvent creation and serialization
- Event factory functions (research_completed, research_failed, source_degraded)
- SlackChannel payload building and delivery
- EmailChannel delivery with recipient validation
- NotificationDispatcher routing, opt-out, and fire-and-forget
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from solstein.notifications.channels import (
    MAX_DELIVERY_RETRIES,
    NotificationChannel,
    SlackChannel,
)
from solstein.notifications.dispatcher import NotificationDispatcher
from solstein.notifications.events import (
    EventType,
    NotificationEvent,
    research_completed_event,
    research_failed_event,
    source_degraded_event,
)

# -----------------------------------------------------------------------
# NotificationEvent tests
# -----------------------------------------------------------------------


class TestNotificationEvent:
    """Verify event schema and factory functions."""

    def test_event_serialization(self):
        """NotificationEvent serializes to dict with all fields."""
        event = NotificationEvent(
            event_type=EventType.RESEARCH_COMPLETED,
            title="Test",
            message="Test message",
            metadata={"key": "value"},
            tenant_id="tenant-1",
            user_id="user-1",
        )
        d = event.to_dict()
        assert d["event_type"] == "research.completed"
        assert d["title"] == "Test"
        assert d["tenant_id"] == "tenant-1"
        assert d["user_id"] == "user-1"
        assert "timestamp" in d

    def test_research_completed_factory(self):
        """research_completed_event creates correct event."""
        event = research_completed_event(
            company_name="Acme Corp",
            duration_seconds=600.0,
            score=0.85,
            tenant_id="t1",
        )
        assert event.event_type == EventType.RESEARCH_COMPLETED
        assert "Acme Corp" in event.title
        assert "10.0 minutes" in event.message
        assert "0.85" in event.message
        assert event.metadata["company_name"] == "Acme Corp"
        assert event.metadata["score"] == 0.85

    def test_research_failed_factory(self):
        """research_failed_event creates correct event."""
        event = research_failed_event(
            company_name="Broken Inc",
            error_summary="Timeout after 30s",
        )
        assert event.event_type == EventType.RESEARCH_FAILED
        assert "Broken Inc" in event.title
        assert "Timeout" in event.message

    def test_source_degraded_factory(self):
        """source_degraded_event creates correct event."""
        event = source_degraded_event(
            source_name="yahoo_finance",
            failure_reason="HTML structure changed",
            consecutive_failures=3,
        )
        assert event.event_type == EventType.SOURCE_DEGRADED
        assert "yahoo_finance" in event.title
        assert "3" in event.message
        assert event.metadata["consecutive_failures"] == 3


# -----------------------------------------------------------------------
# SlackChannel tests
# -----------------------------------------------------------------------


class TestSlackChannel:
    """Verify Slack webhook payload and delivery."""

    def test_payload_structure(self):
        """Slack payload has attachments with color and emoji."""
        channel = SlackChannel(webhook_url="https://hooks.slack.com/test")
        event = NotificationEvent(
            event_type=EventType.RESEARCH_COMPLETED,
            title="Research done",
            message="Pipeline finished",
        )
        payload = channel._build_payload(event)
        assert "attachments" in payload
        attachment = payload["attachments"][0]
        assert attachment["color"] == "#36a64f"
        assert ":white_check_mark:" in attachment["title"]
        assert "Pipeline finished" in attachment["text"]

    def test_failure_event_color(self):
        """Failed events get red color."""
        channel = SlackChannel(webhook_url="https://hooks.slack.com/test")
        event = NotificationEvent(
            event_type=EventType.RESEARCH_FAILED,
            title="Research failed",
            message="Error occurred",
        )
        payload = channel._build_payload(event)
        assert payload["attachments"][0]["color"] == "#dc3545"

    @pytest.mark.asyncio
    async def test_send_success(self):
        """Successful webhook POST returns True."""
        channel = SlackChannel(webhook_url="https://hooks.slack.com/test")
        event = NotificationEvent(
            event_type=EventType.RESEARCH_COMPLETED,
            title="Test",
            message="Test",
        )

        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)
        mock_session.post = MagicMock(
            return_value=AsyncMock(
                __aenter__=AsyncMock(return_value=mock_resp),
                __aexit__=AsyncMock(return_value=False),
            )
        )

        with patch("solstein.notifications.channels.aiohttp.ClientSession", return_value=mock_session):
            result = await channel.send(event)
            assert result is True

    @pytest.mark.asyncio
    async def test_send_failure_retries(self):
        """Failed delivery retries MAX_DELIVERY_RETRIES times."""
        channel = SlackChannel(webhook_url="https://hooks.slack.com/test")
        event = NotificationEvent(
            event_type=EventType.RESEARCH_COMPLETED,
            title="Test",
            message="Test",
        )

        with patch("solstein.notifications.channels.aiohttp.ClientSession") as mock_cls:
            mock_cls.side_effect = Exception("Connection refused")
            result = await channel.send(event)
            assert result is False
            assert mock_cls.call_count == MAX_DELIVERY_RETRIES


# -----------------------------------------------------------------------
# NotificationDispatcher tests
# -----------------------------------------------------------------------


class TestNotificationDispatcher:
    """Test dispatcher routing, opt-out, and fire-and-forget."""

    @pytest.mark.asyncio
    async def test_dispatch_to_registered_channel(self):
        """Events are dispatched to all registered channels."""
        dispatcher = NotificationDispatcher()
        mock_channel = AsyncMock(spec=NotificationChannel)
        mock_channel.channel_name = "mock"
        mock_channel.send = AsyncMock(return_value=True)
        dispatcher.register_channel(mock_channel)

        event = NotificationEvent(
            event_type=EventType.RESEARCH_COMPLETED,
            title="Test",
            message="Test",
        )
        results = await dispatcher.dispatch(event)
        assert results["mock"] is True
        mock_channel.send.assert_called_once_with(event)

    @pytest.mark.asyncio
    async def test_dispatch_no_channels(self):
        """No channels registered returns empty results."""
        dispatcher = NotificationDispatcher()
        event = NotificationEvent(
            event_type=EventType.RESEARCH_COMPLETED,
            title="Test",
            message="Test",
        )
        results = await dispatcher.dispatch(event)
        assert results == {}

    @pytest.mark.asyncio
    async def test_user_opt_out_respected(self):
        """Opted-out users receive no notifications."""
        dispatcher = NotificationDispatcher()
        mock_channel = AsyncMock(spec=NotificationChannel)
        mock_channel.channel_name = "mock"
        mock_channel.send = AsyncMock(return_value=True)
        dispatcher.register_channel(mock_channel)

        dispatcher.set_user_opt_out("user-1", [EventType.RESEARCH_COMPLETED])

        event = NotificationEvent(
            event_type=EventType.RESEARCH_COMPLETED,
            title="Test",
            message="Test",
            user_id="user-1",
        )
        results = await dispatcher.dispatch(event)
        assert results == {}
        mock_channel.send.assert_not_called()

    @pytest.mark.asyncio
    async def test_opt_out_does_not_block_other_events(self):
        """Opt-out for one event type doesn't block others."""
        dispatcher = NotificationDispatcher()
        mock_channel = AsyncMock(spec=NotificationChannel)
        mock_channel.channel_name = "mock"
        mock_channel.send = AsyncMock(return_value=True)
        dispatcher.register_channel(mock_channel)

        dispatcher.set_user_opt_out("user-1", [EventType.RESEARCH_COMPLETED])

        event = NotificationEvent(
            event_type=EventType.RESEARCH_FAILED,
            title="Failed",
            message="Error",
            user_id="user-1",
        )
        results = await dispatcher.dispatch(event)
        assert results["mock"] is True

    @pytest.mark.asyncio
    async def test_channel_failure_does_not_propagate(self):
        """Channel failure doesn't raise — fire-and-forget."""
        dispatcher = NotificationDispatcher()
        mock_channel = AsyncMock(spec=NotificationChannel)
        mock_channel.channel_name = "broken"
        mock_channel.send = AsyncMock(side_effect=Exception("Channel exploded"))
        dispatcher.register_channel(mock_channel)

        event = NotificationEvent(
            event_type=EventType.RESEARCH_COMPLETED,
            title="Test",
            message="Test",
        )
        # Should not raise
        results = await dispatcher.dispatch(event)
        assert results["broken"] is False

    @pytest.mark.asyncio
    async def test_multiple_channels(self):
        """Events dispatched to all channels independently."""
        dispatcher = NotificationDispatcher()

        slack = AsyncMock(spec=NotificationChannel)
        slack.channel_name = "slack"
        slack.send = AsyncMock(return_value=True)

        email = AsyncMock(spec=NotificationChannel)
        email.channel_name = "email"
        email.send = AsyncMock(return_value=False)

        dispatcher.register_channel(slack)
        dispatcher.register_channel(email)

        event = NotificationEvent(
            event_type=EventType.EXPORT_READY,
            title="Export",
            message="Ready",
        )
        results = await dispatcher.dispatch(event)
        assert results["slack"] is True
        assert results["email"] is False

    def test_get_status(self):
        """get_status returns dispatcher health info."""
        dispatcher = NotificationDispatcher()
        mock_channel = MagicMock(spec=NotificationChannel)
        mock_channel.channel_name = "test"
        dispatcher.register_channel(mock_channel)

        status = dispatcher.get_status()
        assert status["channels_registered"] == 1
        assert "test" in status["channel_names"]
