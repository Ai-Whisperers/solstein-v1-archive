"""Cache management endpoints.

EPIC-021: Modularized from enrichment.py.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, Request

from solstein.api.schemas.enrichment import CacheCheckResponse, CacheClearResponse
from solstein.data.security_hardening import rate_limiter

from .enrichment_base import get_cache_repo_if_available, get_client_id, logger, router, unified_loader


@router.get("/companies/{company_id}/enrichment/cache", response_model=CacheCheckResponse)
async def check_cache(company_id: str, request: Request) -> CacheCheckResponse:
    """Check if company is cached."""
    client_id = get_client_id(request)
    if not rate_limiter.is_allowed(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    cached = False
    cache_key = None
    ttl_remaining = None
    cached_data = None

    cache_repo = await get_cache_repo_if_available()

    if cache_repo:
        try:
            cache_record = await cache_repo.get_cached(company_id)
            if cache_record:
                cached = True
                cache_key = f"company_{company_id}"
                now = datetime.now(timezone.utc)
                expires_at = cache_record.expires_at
                if expires_at > now:
                    ttl_remaining = int((expires_at - now).total_seconds() / 3600)
                cached_data = cache_record.enriched_data
        except Exception as e:
            logger.debug(f"Failed to check cache from database: {e}. Falling back to in-memory cache.")
            if hasattr(unified_loader, "cache") and unified_loader.cache:
                cache_key = f"company_{company_id}"
                cached = unified_loader.cache.get(cache_key) is not None
                if cached:
                    ttl_remaining = 24
    else:
        if hasattr(unified_loader, "cache") and unified_loader.cache:
            cache_key = f"company_{company_id}"
            cached = unified_loader.cache.get(cache_key) is not None
            if cached:
                ttl_remaining = 24

    return CacheCheckResponse(
        company_id=company_id,
        cached=cached,
        cache_key=cache_key,
        ttl_remaining_hours=ttl_remaining,
        cached_data=cached_data,
    )


@router.post("/enrichment/cache/clear", response_model=CacheClearResponse)
async def clear_all_cache(request: Request) -> CacheClearResponse:
    """Clear all enrichment cache."""
    client_id = get_client_id(request)
    if not rate_limiter.is_allowed(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    logger.info(f"🧹 Cache clear requested by {client_id}")

    entries_cleared = 0

    cache_repo = await get_cache_repo_if_available()
    if cache_repo:
        try:
            entries_cleared = await cache_repo.delete_cache(company_id=None)
        except Exception as e:
            logger.warning(f"Failed to clear database cache: {e}")

    if hasattr(unified_loader, "clear_enrichment_cache"):
        unified_loader.clear_enrichment_cache()

    return CacheClearResponse(
        status="success",
        message="Enrichment cache cleared",
        entries_cleared=entries_cleared,
    )


@router.post("/enrichment/cache/clear/{company_id}", response_model=CacheClearResponse)
async def clear_company_cache(company_id: str, request: Request) -> CacheClearResponse:
    """Clear cache for specific company."""
    client_id = get_client_id(request)
    if not rate_limiter.is_allowed(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    logger.info(f"🧹 Cache clear for {company_id} by {client_id}")

    entries_cleared = 0

    cache_repo = await get_cache_repo_if_available()
    if cache_repo:
        try:
            entries_cleared = await cache_repo.delete_cache(company_id=company_id)
        except Exception as e:
            logger.warning(f"Failed to clear database cache for {company_id}: {e}")

    if hasattr(unified_loader, "cache") and unified_loader.cache:
        cache_key = f"company_{company_id}"
        if cache_key in unified_loader.cache.cache:
            del unified_loader.cache.cache[cache_key]
            entries_cleared = max(entries_cleared, 1)

    return CacheClearResponse(
        status="success",
        message=f"Cache cleared for {company_id}",
        entries_cleared=entries_cleared,
    )
