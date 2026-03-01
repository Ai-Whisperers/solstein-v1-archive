"""Cache abstraction protocol for Solstein.

Any class that implements these async methods is a valid cache backend.
The production implementation is ``CacheManager`` (Redis + in-memory fallback).
Test code can provide a simple dict-backed implementation without touching Redis.

Usage::

    from solstein.infrastructure.cache_protocol import ICacheRepository

    async def warm(cache: ICacheRepository) -> None:
        await cache.set("key", {"data": 1}, ttl=300)
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ICacheRepository(Protocol):
    """Async cache backend protocol.

    All methods are async to support both Redis (I/O bound) and any
    future distributed cache without blocking the event loop.
    """

    async def get(self, key: str) -> Any | None:
        """Return the cached value or ``None`` if missing / expired."""
        ...

    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Store *value* under *key* with time-to-live *ttl* seconds.

        Returns:
            ``True`` on success, ``False`` on failure.
        """
        ...

    async def delete(self, key: str) -> bool:
        """Remove *key*.

        Returns:
            ``True`` if key existed and was deleted, ``False`` otherwise.
        """
        ...

    async def exists(self, key: str) -> bool:
        """Return ``True`` if *key* exists in cache (not expired)."""
        ...

    async def clear(self, pattern: str = "*") -> int:
        """Delete all keys matching *pattern*.

        Returns:
            Number of keys deleted.
        """
        ...
