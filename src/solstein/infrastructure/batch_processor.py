"""Batch processing for bulk operations - EPIC-014.

Provides efficient batch processing for large datasets with progress tracking
and error isolation.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Generic, TypeVar

from loguru import logger

if TYPE_CHECKING:
    from ..domain.models import Company

T = TypeVar("T")
R = TypeVar("R")


@dataclass
class BatchResult(Generic[T, R]):
    """Result of batch processing."""

    items: list[T]
    results: list[R]
    errors: list[tuple[T, Exception]]
    processed_count: int
    error_count: int


class BatchProcessor(Generic[T, R]):
    """Process items in batches with error isolation.

    Usage:
        processor = BatchProcessor(batch_size=100, max_concurrency=10)
        results = await processor.process(items, process_func)
    """

    def __init__(
        self,
        batch_size: int = 100,
        max_concurrency: int = 10,
        continue_on_error: bool = True,
    ):
        self.batch_size = batch_size
        self.max_concurrency = max_concurrency
        self.continue_on_error = continue_on_error

    async def process(
        self,
        items: list[T],
        process_func: Callable[[T], Coroutine[Any, Any, R]],
    ) -> BatchResult[T, R]:
        """Process items in batches.

        Args:
            items: List of items to process
            process_func: Async function to process each item

        Returns:
            BatchResult with results and errors
        """
        results: list[R] = []
        errors: list[tuple[T, Exception]] = []

        # Split into batches
        batches = [items[i : i + self.batch_size] for i in range(0, len(items), self.batch_size)]

        logger.info(f"Processing {len(items)} items in {len(batches)} batches")

        for batch_num, batch in enumerate(batches, 1):
            batch_results, batch_errors = await self._process_batch(batch, process_func, batch_num, len(batches))
            results.extend(batch_results)
            errors.extend(batch_errors)

        return BatchResult(
            items=items,
            results=results,
            errors=errors,
            processed_count=len(results),
            error_count=len(errors),
        )

    async def _process_batch(
        self,
        batch: list[T],
        process_func: Callable[[T], Coroutine[Any, Any, R]],
        batch_num: int,
        total_batches: int,
    ) -> tuple[list[R], list[tuple[T, Exception]]]:
        """Process a single batch with concurrency control."""
        results: list[R] = []
        errors: list[tuple[T, Exception]] = []

        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.max_concurrency)

        async def process_with_semaphore(item: T) -> tuple[T, R | None, Exception | None]:
            async with semaphore:
                try:
                    result = await process_func(item)
                    return item, result, None
                except Exception as e:
                    logger.error(f"Error processing item: {e}")
                    return item, None, e

        # Process all items in batch concurrently
        tasks = [process_with_semaphore(item) for item in batch]
        batch_results = await asyncio.gather(*tasks)

        # Collect results and errors
        for item, result, error in batch_results:
            if error:
                errors.append((item, error))
                if not self.continue_on_error:
                    break
            elif result is not None:
                results.append(result)

        logger.info(f"Batch {batch_num}/{total_batches} complete: {len(results)} succeeded, {len(errors)} failed")

        return results, errors


class BulkIngestionProcessor:
    """Specialized processor for bulk data ingestion.

    Handles large datasets with:
    - Chunked reading
    - Batch processing
    - Progress tracking
    - Error isolation
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        batch_size: int = 100,
        max_concurrency: int = 10,
    ):
        self.chunk_size = chunk_size
        self.batch_processor = BatchProcessor(
            batch_size=batch_size,
            max_concurrency=max_concurrency,
        )

    async def ingest_companies(
        self,
        companies: list[dict[str, Any]],
        ingest_func: Callable[[dict[str, Any]], Coroutine[Any, Any, Company]],
    ) -> BatchResult[dict[str, Any], Company]:
        """Ingest a large number of companies.

        Args:
            companies: List of company dictionaries
            ingest_func: Function to convert dict to Company and save

        Returns:
            BatchResult with ingested companies
        """
        logger.info(f"Starting bulk ingestion of {len(companies)} companies")

        result = await self.batch_processor.process(companies, ingest_func)

        logger.info(f"Bulk ingestion complete: {result.processed_count} succeeded, {result.error_count} failed")

        return result


# Convenience function for simple batch processing
async def batch_process(
    items: list[T],
    process_func: Callable[[T], Coroutine[Any, Any, R]],
    batch_size: int = 100,
    max_concurrency: int = 10,
) -> BatchResult[T, R]:
    """Process items in batches with default settings.

    Usage:
        results = await batch_process(
            companies,
            enrich_company,
            batch_size=50,
            max_concurrency=5,
        )
    """
    processor = BatchProcessor(
        batch_size=batch_size,
        max_concurrency=max_concurrency,
    )
    return await processor.process(items, process_func)
