"""Tests for STORY-084: Supabase Realtime listener and WebSocket manager.

Validates:
- ConnectionManager connect/disconnect/broadcast behaviour.
- Realtime listener callback routes events to correct channels.
- Tenant-level broadcasting for dashboard views.
- Graceful handling of missing job IDs and malformed payloads.
- Start/stop lifecycle with missing Supabase config.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from solstein.api.websocket.manager import ConnectionManager
from solstein.api.websocket.realtime_listener import (
    RealtimeListenerState,
    _on_research_job_change,
    _state,
    start_realtime_listener,
    stop_realtime_listener,
)

# ---------------------------------------------------------------------------
# ConnectionManager tests
# ---------------------------------------------------------------------------


class TestConnectionManager:
    """Test the WebSocket ConnectionManager."""

    @pytest.mark.asyncio
    async def test_connect_and_broadcast(self):
        # Arrange
        mgr = ConnectionManager()
        ws = AsyncMock()

        # Act
        await mgr.connect(ws, "job:abc")
        await mgr.broadcast("job:abc", {"type": "test"})

        # Assert
        ws.accept.assert_awaited_once()
        ws.send_text.assert_awaited_once_with(json.dumps({"type": "test"}))

    @pytest.mark.asyncio
    async def test_disconnect_removes_websocket(self):
        # Arrange
        mgr = ConnectionManager()
        ws = AsyncMock()
        await mgr.connect(ws, "job:abc")

        # Act
        mgr.disconnect(ws, "job:abc")

        # Assert - channel should be cleaned up
        assert "job:abc" not in mgr._channels

    @pytest.mark.asyncio
    async def test_broadcast_to_empty_channel(self):
        # Arrange
        mgr = ConnectionManager()

        # Act & Assert - should not raise
        await mgr.broadcast("nonexistent", {"type": "test"})

    @pytest.mark.asyncio
    async def test_broadcast_cleans_dead_connections(self):
        # Arrange
        mgr = ConnectionManager()
        ws_good = AsyncMock()
        ws_dead = AsyncMock()
        ws_dead.send_text.side_effect = RuntimeError("connection closed")

        await mgr.connect(ws_good, "ch")
        await mgr.connect(ws_dead, "ch")

        # Act
        await mgr.broadcast("ch", {"type": "test"})

        # Assert - dead connection removed, good one stays
        ws_good.send_text.assert_awaited_once()
        assert ws_dead not in mgr._channels.get("ch", [])

    @pytest.mark.asyncio
    async def test_send_personal(self):
        # Arrange
        mgr = ConnectionManager()
        ws = AsyncMock()

        # Act
        await mgr.send_personal(ws, {"type": "hello"})

        # Assert
        ws.send_text.assert_awaited_once_with(json.dumps({"type": "hello"}))

    @pytest.mark.asyncio
    async def test_disconnect_nonexistent_channel(self):
        # Arrange
        mgr = ConnectionManager()
        ws = AsyncMock()

        # Act & Assert - should not raise
        mgr.disconnect(ws, "nonexistent")


# ---------------------------------------------------------------------------
# Realtime listener callback tests
# ---------------------------------------------------------------------------


class TestRealtimeCallback:
    """Test the _on_research_job_change callback."""

    @pytest.mark.asyncio
    async def test_broadcasts_job_update(self):
        # Arrange
        payload = {
            "data": {
                "type": "UPDATE",
                "record": {
                    "id": "job-123",
                    "tenant_id": "tenant-abc",
                    "status": "running",
                    "progress_pct": 50,
                    "current_stage": "gathering",
                    "error_message": None,
                },
                "old_record": {},
            }
        }

        with patch("solstein.api.websocket.realtime_listener.manager") as mock_manager:
            mock_manager.broadcast = AsyncMock()

            # Act
            await _on_research_job_change(payload)

            # Assert - broadcasts to both job and tenant channels
            assert mock_manager.broadcast.await_count == 2

            job_call = mock_manager.broadcast.await_args_list[0]
            assert job_call.args[0] == "job:job-123"
            msg = job_call.args[1]
            assert msg["type"] == "job_update"
            assert msg["status"] == "running"
            assert msg["progress_pct"] == 50

            tenant_call = mock_manager.broadcast.await_args_list[1]
            assert tenant_call.args[0] == "tenant:tenant-abc:jobs"

    @pytest.mark.asyncio
    async def test_handles_missing_job_id(self):
        # Arrange
        payload = {"data": {"type": "UPDATE", "record": {}, "old_record": {}}}

        with patch("solstein.api.websocket.realtime_listener.manager") as mock_manager:
            mock_manager.broadcast = AsyncMock()

            # Act - should not raise
            await _on_research_job_change(payload)

            # Assert - no broadcast when no job ID
            mock_manager.broadcast.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_handles_empty_payload(self):
        # Arrange & Act - should not raise
        with patch("solstein.api.websocket.realtime_listener.manager") as mock_manager:
            mock_manager.broadcast = AsyncMock()
            await _on_research_job_change({})
            mock_manager.broadcast.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_falls_back_to_old_record_for_job_id(self):
        # Arrange - DELETE event where record is empty
        payload = {
            "data": {
                "type": "DELETE",
                "record": {},
                "old_record": {
                    "id": "job-456",
                    "tenant_id": "tenant-xyz",
                    "status": "cancelled",
                    "progress_pct": 0,
                    "current_stage": None,
                    "error_message": None,
                },
            }
        }

        with patch("solstein.api.websocket.realtime_listener.manager") as mock_manager:
            mock_manager.broadcast = AsyncMock()

            # Act
            await _on_research_job_change(payload)

            # Assert
            job_call = mock_manager.broadcast.await_args_list[0]
            assert job_call.args[0] == "job:job-456"

    @pytest.mark.asyncio
    async def test_no_tenant_broadcast_when_tenant_missing(self):
        # Arrange
        payload = {
            "data": {
                "type": "INSERT",
                "record": {
                    "id": "job-789",
                    "status": "queued",
                    "progress_pct": 0,
                    "current_stage": None,
                    "error_message": None,
                },
                "old_record": {},
            }
        }

        with patch("solstein.api.websocket.realtime_listener.manager") as mock_manager:
            mock_manager.broadcast = AsyncMock()

            # Act
            await _on_research_job_change(payload)

            # Assert - only job channel broadcast, not tenant
            assert mock_manager.broadcast.await_count == 1
            assert mock_manager.broadcast.await_args_list[0].args[0] == "job:job-789"


# ---------------------------------------------------------------------------
# Lifecycle tests
# ---------------------------------------------------------------------------


class TestRealtimeLifecycle:
    """Test start/stop lifecycle of the realtime listener."""

    @pytest.mark.asyncio
    async def test_start_skips_when_already_running(self):
        # Arrange
        original_running = _state.running
        _state.running = True

        try:
            # Act - should be a no-op
            await start_realtime_listener()

            # Assert - state unchanged
            assert _state.running is True
        finally:
            _state.running = original_running

    @pytest.mark.asyncio
    async def test_start_skips_when_supabase_not_configured(self):
        # Arrange
        original_running = _state.running
        _state.running = False

        mock_settings = MagicMock()
        mock_settings.supabase.url = ""
        mock_settings.supabase.key = ""

        try:
            with patch(
                "solstein.config.get_settings",
                return_value=mock_settings,
            ):
                # Act
                await start_realtime_listener()

                # Assert - not started
                assert _state.running is False
        finally:
            _state.running = original_running

    @pytest.mark.asyncio
    async def test_stop_when_not_running(self):
        # Arrange
        original_running = _state.running
        _state.running = False

        try:
            # Act & Assert - should not raise
            await stop_realtime_listener()
            assert _state.running is False
        finally:
            _state.running = original_running

    @pytest.mark.asyncio
    async def test_stop_cleans_up_resources(self):
        # Arrange
        original_state = (_state.client, _state.channel, _state.running)
        mock_channel = AsyncMock()
        mock_client = AsyncMock()
        _state.client = mock_client
        _state.channel = mock_channel
        _state.running = True

        try:
            # Act
            await stop_realtime_listener()

            # Assert
            mock_channel.unsubscribe.assert_awaited_once()
            mock_client.close.assert_awaited_once()
            assert _state.running is False
            assert _state.client is None
            assert _state.channel is None
        finally:
            _state.client, _state.channel, _state.running = original_state

    @pytest.mark.asyncio
    async def test_realtime_listener_state_defaults(self):
        # Assert
        state = RealtimeListenerState()
        assert state.client is None
        assert state.channel is None
        assert state.running is False
