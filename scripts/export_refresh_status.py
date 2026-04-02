from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

from loguru import logger
from sqlalchemy.exc import OperationalError

from solstein.infrastructure.database import db_manager
from solstein.infrastructure.refresh import build_refresh_snapshot, get_refresh_statuses


async def main(output_path: Path) -> None:
    db_manager.init_async()
    try:
        statuses = await get_refresh_statuses(db_manager=db_manager)
    except OperationalError as exc:
        logger.warning("Refresh metadata unavailable", error=str(exc))
        statuses = []
    snapshot = build_refresh_snapshot(statuses, generated_at=datetime.now(timezone.utc))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(snapshot, indent=2))
    logger.info("Wrote refresh status snapshot", path=str(output_path))


if __name__ == "__main__":
    target = Path("data/output/refresh/refresh_status.json")
    try:
        asyncio.run(main(target))
    except Exception as exc:
        logger.error("Refresh status snapshot failed", error=str(exc))
        raise
