"""Cache layer implementation using Redis - Phase 2, Item 2.3

Provides Redis-based caching with fallback to in-memory cache when Redis is unavailable.
"""

import json
import logging
from collections.abc import Callable
from functools import wraps
from typing import Any

try:
    import redis
    from redis.asyncio import Redis as AsyncRedis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None  # type: ignore
    AsyncRedis = None  # type: ignore

logger = logging.getLogger(__name__)


class CacheManager:
    """Redis-based caching with fallback to in-memory cache."""

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        """
        Initialize cache manager.

        Args:
            redis_url: Redis connection URL
        """
        if not REDIS_AVAILABLE:
            logger.warning("Redis not installed, using in-memory cache")
            self.redis = None
            self.available = False
            self._memory_cache: dict[str, tuple[Any, float | None]] = {}
            return

        try:
            # Try async Redis client first
            self.redis: AsyncRedis | None = AsyncRedis.from_url(redis_url, decode_responses=True)
            self.available = True
            logger.info("Redis cache configured")
        except Exception as e:
            logger.warning(f"Redis unavailable: {e}, using in-memory cache")
            self.redis = None
            self.available = False
            self._memory_cache: dict[str, tuple[Any, float | None]] = {}

    async def get(self, key: str) -> Any | None:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        try:
            if self.available and self.redis:
                value = await self.redis.get(key)
                if value:
                    return json.loads(value)
            else:
                # In-memory fallback
                if key in self._memory_cache:
                    value, _ = self._memory_cache[key]
                    return value
        except Exception as e:
            logger.error(f"Cache get error: {e}")

        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = 3600,
    ) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds

        Returns:
            True if successful
        """
        try:
            serialized = json.dumps(value, default=str)

            if self.available and self.redis:
                await self.redis.setex(key, ttl, serialized)
            else:
                # In-memory fallback (no TTL enforcement)
                self._memory_cache[key] = (value, None)

            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete from cache."""
        try:
            if self.available and self.redis:
                await self.redis.delete(key)
            else:
                self._memory_cache.pop(key, None)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    async def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching pattern.

        Args:
            pattern: Key pattern (e.g., 'company:*')

        Returns:
            Number of keys deleted
        """
        try:
            if self.available and self.redis:
                keys = await self.redis.keys(pattern)
                if keys:
                    return await self.redis.delete(*keys)
            else:
                # In-memory fallback - simple prefix matching
                keys_to_delete = [k for k in self._memory_cache.keys() if k.startswith(pattern.rstrip("*"))]
                for k in keys_to_delete:
                    self._memory_cache.pop(k, None)
                return len(keys_to_delete)
        except Exception as e:
            logger.error(f"Cache clear error: {e}")

        return 0

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            if self.available and self.redis:
                return await self.redis.exists(key) > 0
            else:
                return key in self._memory_cache
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False

    async def ttl(self, key: str) -> int:
        """Get remaining TTL for key in seconds."""
        try:
            if self.available and self.redis:
                return await self.redis.ttl(key)
            else:
                # In-memory fallback - no TTL tracking
                return -1 if key in self._memory_cache else -2
        except Exception as e:
            logger.error(f"Cache ttl error: {e}")
            return -2


# Global cache manager instance
cache_manager = CacheManager()


def cached(
    key_prefix: str,
    ttl: int = 3600,
    key_builder: Callable[..., str] | None = None,
):
    """
    Decorator to cache function results.

    Args:
        key_prefix: Prefix for cache key
        ttl: Time-to-live in seconds
        key_builder: Optional function to build custom cache key

    Example:
        @cached("company", ttl=3600)
        async def get_company(company_id: str):
            return await fetch_company(company_id)
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                # Default key: prefix:arg1:arg2:...
                key_parts = [key_prefix]
                key_parts.extend(str(arg) for arg in args if arg)
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()) if v)
                cache_key = ":".join(key_parts)

            # Try to get from cache
            cached_value = await cache_manager.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached_value

            # Call function and cache result
            result = await func(*args, **kwargs)
            await cache_manager.set(cache_key, result, ttl)
            logger.debug(f"Cache miss: {cache_key}")
            return result

        return wrapper

    return decorator


def cache_invalidate(pattern: str):
    """
    Decorator to invalidate cache entries matching pattern after function execution.

    Args:
        pattern: Key pattern to invalidate (e.g., 'company:*')
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            await cache_manager.clear_pattern(pattern)
            logger.debug(f"Cache invalidated: {pattern}")
            return result

        return wrapper

    return decorator


# Cache key builders for common patterns
def company_key(company_id: str) -> str:
    """Build cache key for company data."""
    return f"company:{company_id}"


def market_analysis_key(industry: str | None, region: str | None) -> str:
    """Build cache key for market analysis."""
    parts = ["market_analysis"]
    if industry:
        parts.append(f"industry={industry}")
    if region:
        parts.append(f"region={region}")
    return ":".join(parts)


def scoring_key(company_id: str) -> str:
    """Build cache key for scoring data."""
    return f"scoring:{company_id}"
