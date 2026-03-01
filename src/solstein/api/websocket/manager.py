"""WebSocket realtime updates for job progress (EPIC-024).

Provides WebSocket endpoints for live job status updates and
company score change notifications.

Usage::

    from fastapi import WebSocket
    from solstein.api.websocket.manager import manager

    @router.websocket("/ws/jobs/{job_id}")
    async def job_websocket(websocket: WebSocket, job_id: str):
        await manager.connect(websocket, channel=f"job:{job_id}")
        try:
            while True:
                await websocket.receive_text()  # Keepalive
        except WebSocketDisconnect:
            manager.disconnect(websocket, channel=f"job:{job_id}")
"""

from __future__ import annotations

import json
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger


class ConnectionManager:
    """Manages WebSocket connections by channel.

    Channels are arbitrary strings (e.g. ``'job:123'``, ``'user:456'``).
    Broadcasting sends a message to all connections subscribed to a channel.
    """

    def __init__(self) -> None:
        # channel -> list of websockets
        self._channels: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, channel: str) -> None:
        """Accept connection and subscribe to *channel*."""
        await websocket.accept()
        if channel not in self._channels:
            self._channels[channel] = []
        self._channels[channel].append(websocket)
        logger.debug("WebSocket connected", channel=channel, total=len(self._channels[channel]))

    def disconnect(self, websocket: WebSocket, channel: str) -> None:
        """Unsubscribe *websocket* from *channel*."""
        if channel in self._channels:
            try:
                self._channels[channel].remove(websocket)
                logger.debug("WebSocket disconnected", channel=channel, remaining=len(self._channels[channel]))
            except ValueError:
                pass
            if not self._channels[channel]:
                del self._channels[channel]

    async def broadcast(self, channel: str, message: dict[str, Any]) -> None:
        """Send *message* to all connections on *channel*."""
        if channel not in self._channels:
            return
        disconnected: list[WebSocket] = []
        payload = json.dumps(message)
        for ws in self._channels[channel]:
            try:
                await ws.send_text(payload)
            except Exception:
                disconnected.append(ws)
        # Clean up dead connections
        for ws in disconnected:
            self.disconnect(ws, channel)

    async def send_personal(self, websocket: WebSocket, message: dict[str, Any]) -> None:
        """Send *message* to a single *websocket*."""
        await websocket.send_text(json.dumps(message))


# Global singleton manager
manager = ConnectionManager()
