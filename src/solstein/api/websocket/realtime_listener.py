"""Supabase Realtime listener for research job status changes (STORY-084).

Subscribes to Postgres changes on the ``research_jobs`` table via
Supabase Realtime and broadcasts updates through the WebSocket
ConnectionManager so connected clients receive live progress.

Lifecycle:
    Call :func:`start_realtime_listener` during app startup and
    :func:`stop_realtime_listener` during shutdown.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from loguru import logger

from .manager import manager


@dataclass
class RealtimeListenerState:
    """Holds the Supabase Realtime client and channel references.

    Keeps mutable state in a single object so start/stop can
    coordinate without module-level globals scattered around.
    """

    client: Any | None = None
    channel: Any | None = None
    running: bool = False


_state = RealtimeListenerState()


async def _on_research_job_change(payload: dict[str, Any]) -> None:
    """Handle a Postgres change event on the research_jobs table.

    Broadcasts the change to WebSocket clients subscribed to
    the ``job:<job_id>`` channel.

    Args:
        payload: Supabase Realtime payload with ``data`` containing
            ``type`` (INSERT/UPDATE/DELETE), ``record``, and ``old_record``.
    """
    try:
        data = payload.get("data", {})
        event_type = data.get("type", "UNKNOWN")
        record = data.get("record", {})
        old_record = data.get("old_record", {})

        job_id = record.get("id") or old_record.get("id")
        if not job_id:
            logger.warning("[RealtimeListener] Change event missing job ID")
            return

        channel_name = f"job:{job_id}"

        message: dict[str, Any] = {
            "type": "job_update",
            "event": event_type,
            "job_id": job_id,
            "status": record.get("status"),
            "progress_pct": record.get("progress_pct"),
            "current_stage": record.get("current_stage"),
            "error_message": record.get("error_message"),
        }

        await manager.broadcast(channel_name, message)

        # Also broadcast to tenant-level channel for dashboard views
        tenant_id = record.get("tenant_id")
        if tenant_id:
            tenant_channel = f"tenant:{tenant_id}:jobs"
            await manager.broadcast(tenant_channel, message)

        logger.debug(
            "[RealtimeListener] Broadcast job update",
            job_id=job_id,
            event=event_type,
            status=record.get("status"),
        )
    except (KeyError, TypeError, AttributeError) as exc:
        logger.error(f"[RealtimeListener] Error processing change event: {exc}")


async def start_realtime_listener() -> None:
    """Start listening to Supabase Realtime changes on research_jobs.

    Connects to the Supabase Realtime server and subscribes to
    INSERT/UPDATE events on the ``research_jobs`` table. Safe to call
    multiple times; subsequent calls are no-ops.
    """
    if _state.running:
        logger.debug("[RealtimeListener] Already running, skipping start")
        return

    try:
        from solstein.config import get_settings

        settings = get_settings()
        supabase_url = settings.supabase.url
        supabase_key = settings.supabase.key

        if not supabase_url or not supabase_key:
            logger.warning("[RealtimeListener] Supabase not configured, realtime listener disabled")
            return

        # Build the Realtime WebSocket URL from the Supabase project URL
        realtime_url = supabase_url.replace("https://", "wss://")
        realtime_url = realtime_url.replace("http://", "ws://")
        if not realtime_url.endswith("/"):
            realtime_url += "/"
        realtime_url += "realtime/v1"

        from realtime import AsyncRealtimeClient

        _state.client = AsyncRealtimeClient(
            realtime_url,
            supabase_key,
        )

        await _state.client.connect()

        _state.channel = _state.client.channel("research-jobs-changes")

        _state.channel.on_postgres_changes(
            event="*",
            schema="public",
            table="research_jobs",
            callback=_on_research_job_change,
        )

        await _state.channel.subscribe()
        _state.running = True

        logger.info("[RealtimeListener] Subscribed to research_jobs changes")

    except ImportError:
        logger.warning("[RealtimeListener] realtime package not available, listener disabled")
    except (ConnectionError, OSError, asyncio.TimeoutError) as exc:
        logger.error(f"[RealtimeListener] Failed to connect to Supabase Realtime: {exc}")
    except (ValueError, TypeError, RuntimeError) as exc:
        logger.error(f"[RealtimeListener] Configuration error: {exc}")


async def stop_realtime_listener() -> None:
    """Stop the Supabase Realtime listener and clean up resources."""
    if not _state.running:
        return

    try:
        if _state.channel is not None:
            await _state.channel.unsubscribe()
            _state.channel = None

        if _state.client is not None:
            await _state.client.close()
            _state.client = None

        _state.running = False
        logger.info("[RealtimeListener] Stopped and cleaned up")
    except (ConnectionError, OSError, RuntimeError) as exc:
        logger.error(f"[RealtimeListener] Error during shutdown: {exc}")
        _state.running = False
