"""Query result caching decorator for improved performance.

Provides caching for database query results to reduce load and improve response times.
"""

import hashlib
import json
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

from loguru import logger

from solstein.infrastructure.cache import cache_manager as _cache_manager


def get_cache() -> object:
    return _cache_manager


T = TypeVar("T")


def cached_query(
    ttl: int = 300,
    key_prefix: str | None = None,
    invalidate_on: list[str] | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to cache database query results.

    Args:
        ttl: Time to live in seconds (default: 5 minutes)
        key_prefix: Optional prefix for cache key
        invalidate_on: List of function names that should invalidate this cache

    Usage:
        @cached_query(ttl=300)
        async def get_company_by_id(company_id: str) -> Company:
            return await db.fetch_one(...)
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        cache_key_prefix = key_prefix or func.__name__

        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> T:
            cache = get_cache()

            # Generate cache key from function name and arguments
            key_parts = [cache_key_prefix]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = hashlib.md5(json.dumps(key_parts).encode()).hexdigest()

            # Try to get from cache
            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {func.__name__}: {cache_key[:8]}...")
                return cached_value

            # Execute function and cache result
            logger.debug(f"Cache miss for {func.__name__}: {cache_key[:8]}...")
            result = await func(*args, **kwargs)

            if result is not None:
                await cache.set(cache_key, result, ttl=ttl)

            return result

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> T:
            cache = get_cache()

            # Generate cache key
            key_parts = [cache_key_prefix]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = hashlib.md5(json.dumps(key_parts).encode()).hexdigest()

            # Try to get from cache
            cached_value = cache.get_sync(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {func.__name__}: {cache_key[:8]}...")
                return cached_value

            # Execute function and cache result
            logger.debug(f"Cache miss for {func.__name__}: {cache_key[:8]}...")
            result = func(*args, **kwargs)

            if result is not None:
                cache.set_sync(cache_key, result, ttl=ttl)

            return result

        # Return appropriate wrapper
        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        return sync_wrapper  # type: ignore

    return decorator


class CacheStats:
    """Cache statistics tracker."""

    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return self.hits / total

    def record_hit(self) -> None:
        """Record a cache hit."""
        self.hits += 1

    def record_miss(self) -> None:
        """Record a cache miss."""
        self.misses += 1

    def record_eviction(self) -> None:
        """Record a cache eviction."""
        self.evictions += 1

    def to_dict(self) -> dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "hit_rate": self.hit_rate,
        }
