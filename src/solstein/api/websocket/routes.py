"""WebSocket endpoints for realtime updates (EPIC-024).

Routes:
- /ws/jobs/{job_id} — Live enrichment job progress
- /ws/companies/{company_id} — Company score change notifications
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger

from .manager import manager

router = APIRouter(prefix="/ws")


@router.websocket("/jobs/{job_id}")
async def job_websocket(websocket: WebSocket, job_id: str) -> None:
    """Subscribe to realtime updates for an enrichment job.

    Messages sent by server:
    - {"type": "progress", "percent": 25, "stage": "fetching_sources"}
    - {"type": "complete", "result": {...}}
    - {"type": "error", "message": "..."}
    """
    channel = f"job:{job_id}"
    await manager.connect(websocket, channel)
    logger.info("Job WebSocket connected", job_id=job_id)
    try:
        while True:
            # Client can send keepalive pings or unsubscribe
            data = await websocket.receive_text()
            msg: dict[str, Any] = {"type": "ack", "received": data}
            await manager.send_personal(websocket, msg)
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)
        logger.info("Job WebSocket disconnected", job_id=job_id)


@router.websocket("/companies/{company_id}")
async def company_websocket(websocket: WebSocket, company_id: str) -> None:
    """Subscribe to score change notifications for a company.

    Messages sent by server:
    - {"type": "score_update", "composite_score": 7.5, "timestamp": "..."}
    - {"type": "classification_change", "old": "Salt", "new": "Phoenix"}
    """
    channel = f"company:{company_id}"
    await manager.connect(websocket, channel)
    logger.info("Company WebSocket connected", company_id=company_id)
    try:
        while True:
            data = await websocket.receive_text()
            msg: dict[str, Any] = {"type": "ack", "received": data}
            await manager.send_personal(websocket, msg)
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)
        logger.info("Company WebSocket disconnected", company_id=company_id)
