"""Cache warming on application startup.

Proactively populates the cache with frequently-accessed, slow-to-compute
data so the first real request is fast.

Warming runs in the background so it never blocks startup — if Redis is
unavailable or warming fails, the application continues normally.
"""

from __future__ import annotations

import asyncio
from typing import Any

from loguru import logger

from solstein.infrastructure.constants import (
    CACHE_DEFAULT_TTL_S,
    CACHE_LONG_TTL_S,
    CACHE_SHORT_TTL_S,
)


async def warm_cache(cache: Any, db_session_factory: Any | None = None) -> None:
    """Warm the cache with commonly-accessed data.

    Args:
        cache: Any object satisfying ``ICacheRepository`` protocol.
        db_session_factory: Optional async session factory to load DB data.
                            If ``None``, only static keys are warmed.
    """
    logger.info("Starting cache warm-up sequence")
    tasks = [
        _warm_static_config(cache),
    ]
    if db_session_factory is not None:
        tasks.append(_warm_top_companies(cache, db_session_factory))

    results = await asyncio.gather(*tasks, return_exceptions=True)
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.warning("Cache warm-up task failed", task_index=i, error=str(result))

    logger.info("Cache warm-up complete", tasks_run=len(tasks))


async def _warm_static_config(cache: Any) -> None:
    """Warm static/rarely-changing config keys."""
    from solstein.config import get_settings

    settings = get_settings()

    static_payload = {
        "environment": settings.environment,
        "version": "1.0.0",
        "features": {
            "rate_limiting": True,
            "multi_tenancy": getattr(settings, "require_api_key", False),
        },
    }

    success = await cache.set("solstein:config:static", static_payload, ttl=CACHE_LONG_TTL_S)
    if success:
        logger.debug("Warmed static config key", ttl=CACHE_LONG_TTL_S)
    else:
        logger.warning("Failed to warm static config key")


async def _warm_top_companies(cache: Any, db_session_factory: Any) -> None:
    """Warm the top-50 companies list (by composite score) to speed up /companies."""
    try:
        from sqlalchemy import select, desc
        from solstein.infrastructure.database_models import CompanyRecord

        async with db_session_factory() as session:
            result = await session.execute(
                select(CompanyRecord)
                .where(CompanyRecord.composite_score.isnot(None))
                .order_by(desc(CompanyRecord.composite_score))
                .limit(50)
            )
            companies = result.scalars().all()

        payload = [
            {
                "id": str(c.company_id),
                "name": c.name,
                "tier": c.tier,
                "composite_score": c.composite_score,
                "industry": c.industry,
            }
            for c in companies
        ]
        await cache.set("solstein:companies:top50", payload, ttl=CACHE_SHORT_TTL_S)
        logger.debug("Warmed top-50 companies cache", count=len(payload))
    except Exception as exc:
        logger.warning("Could not warm company cache (DB may not be ready)", error=str(exc))
