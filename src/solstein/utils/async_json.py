"""Async JSON utilities for EPIC-023 Story 3.

Provides non-blocking JSON encoding/decoding for large payloads.
"""

from __future__ import annotations

import asyncio
import json
from concurrent.futures import ThreadPoolExecutor
from typing import Any

# Thread pool for JSON operations
_json_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="json_worker")


async def dumps_async(
    obj: Any,
    *,
    indent: int | None = None,
    default: Any = None,
    ensure_ascii: bool = False,
) -> str:
    """Async JSON encoding."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        _json_executor,
        lambda: json.dumps(
            obj,
            indent=indent,
            default=default,
            ensure_ascii=ensure_ascii,
        ),
    )


async def loads_async(data: str) -> Any:
    """Async JSON decoding."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_json_executor, json.loads, data)


class AsyncJSONEncoder:
    """Streaming JSON encoder for large payloads."""

    def __init__(self, chunk_size: int = 8192):
        self.chunk_size = chunk_size

    async def encode_streaming(self, obj: Any) -> bytes:
        """Encode to bytes in chunks."""
        # For now, simple implementation
        # In production, use ijson or similar for true streaming
        loop = asyncio.get_event_loop()
        json_str = await loop.run_in_executor(
            _json_executor,
            lambda: json.dumps(obj, default=str),
        )
        return json_str.encode("utf-8")


__all__ = ["dumps_async", "loads_async", "AsyncJSONEncoder"]
