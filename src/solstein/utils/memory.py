"""Memory optimization utilities for EPIC-023 Story 8.

Features:
- Streaming for large datasets
- Generator patterns
- Memory monitoring
"""

from __future__ import annotations

import gc
import sys
from collections.abc import AsyncGenerator, Generator, Iterator
from contextlib import contextmanager
from typing import Any, TypeVar

from loguru import logger

T = TypeVar("T")


def chunk_iterator(items: list[T], chunk_size: int = 100) -> Generator[list[T], None, None]:
    """Yield chunks of items to reduce memory usage."""
    for i in range(0, len(items), chunk_size):
        yield items[i : i + chunk_size]


def stream_jsonl(filepath: str) -> Generator[dict, None, None]:
    """Stream JSON lines file without loading entire file."""
    import json

    with open(filepath, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


@contextmanager
def memory_monitor(name: str, threshold_mb: float = 100.0):
    """Context manager to monitor memory usage."""
    import tracemalloc

    tracemalloc.start()
    start_size = tracemalloc.get_traced_memory()[0]

    try:
        yield
    finally:
        current_size = tracemalloc.get_traced_memory()[0]
        tracemalloc.stop()

        used_mb = (current_size - start_size) / (1024 * 1024)
        if used_mb > threshold_mb:
            logger.warning(
                f"High memory usage in {name}: {used_mb:.2f}MB",
                threshold_mb=threshold_mb,
            )
        else:
            logger.debug(f"Memory usage in {name}: {used_mb:.2f}MB")


def clear_memory() -> None:
    """Force garbage collection to free memory."""
    gc.collect()
    logger.debug("Garbage collection completed")


class StreamingJSONResponse:
    """Streaming JSON response for large payloads."""

    def __init__(self, data: Iterator[Any], chunk_size: int = 100):
        self.data = data
        self.chunk_size = chunk_size

    async def stream(self) -> AsyncGenerator[str, None]:
        """Stream JSON data in chunks."""
        import json

        yield "["
        first = True

        for item in self.data:
            if not first:
                yield ","
            first = False
            yield json.dumps(item, default=str)

        yield "]"


def estimate_object_size(obj: Any) -> int:
    """Estimate object size in bytes."""

    return sys.getsizeof(obj)


__all__ = [
    "chunk_iterator",
    "stream_jsonl",
    "memory_monitor",
    "clear_memory",
    "StreamingJSONResponse",
    "estimate_object_size",
]
