"""Orchestration tasks for running all refresh operations.

Extracted from worker_tasks.py as part of EPIC-021 file splitting.
Provides tasks for coordinating multiple refresh operations.
"""

from __future__ import annotations

from celery import shared_task
from loguru import logger

from .refresh_tasks import (
    refresh_companies_house,
    refresh_funding,
    refresh_github,
    refresh_global_market,
    refresh_linkedin,
    refresh_news,
    refresh_news_signals,
    refresh_patents,
    refresh_sec_edgar,
    refresh_web_search,
    refresh_website,
    refresh_yahoo_finance,
)


@shared_task(name="solstein.worker_tasks.refresh_all_sources", bind=True)
def refresh_all_sources(self):
    """Refresh all data sources.

    Queues refresh tasks for all 12 sources in parallel.
    """
    logger.info("Starting full refresh for all sources")

    results = []

    # Original 4 sources
    results.append(refresh_sec_edgar.apply_async().id)
    results.append(refresh_companies_house.apply_async().id)
    results.append(refresh_news_signals.apply_async().id)
    results.append(refresh_github.apply_async().id)

    # New 8 sources
    results.append(refresh_yahoo_finance.apply_async().id)
    results.append(refresh_patents.apply_async().id)
    results.append(refresh_news.apply_async().id)
    results.append(refresh_website.apply_async().id)
    results.append(refresh_linkedin.apply_async().id)
    results.append(refresh_funding.apply_async().id)
    results.append(refresh_global_market.apply_async().id)
    results.append(refresh_web_search.apply_async().id)

    logger.info(f"Queued {len(results)} refresh tasks")
    return {
        "status": "queued",
        "task_ids": results,
        "sources": [
            "sec_edgar",
            "companies_house",
            "news_signals",
            "github",
            "yahoo_finance",
            "patents",
            "news",
            "website",
            "linkedin",
            "funding",
            "global_market",
            "web_search",
        ],
    }
