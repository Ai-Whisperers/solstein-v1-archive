"""Celery tasks for data refresh operations.

EPIC-021: Refactored from monolithic 902-line file to modular structure.
This module now serves as the orchestration layer, delegating to specialized modules.

Provides scheduled tasks for refreshing data from all 12 sources:
- SEC EDGAR (financial filings)
- Companies House (UK/EU company data)
- News Signals (funding, partnerships, key hires)
- GitHub (repository metrics)
- Yahoo Finance (market data)
- Patents (patent filings)
- News (general news)
- Website (company website data)
- LinkedIn (professional profiles)
- Funding (funding rounds)
- Global Market (market trends)
- Web Search (search results)

Phase 13.4: Async Job Retry Logic
- Exponential backoff: 5s, 10s, 20s for retries 1, 2, 3
- Dead Letter Queue tracking for permanently failed jobs
- Logging with [RETRY-ATTEMPT-N] and [RETRY-FAILED] prefixes
"""

from __future__ import annotations

# Base utilities
from solstein.worker.base import (
    DeadLetterQueue,
    dead_letter_queue,
    get_db_manager,
    get_tracked_company_ids,
    store_facts,
)

# Enrichment tasks
from solstein.worker.enrichment_tasks import (
    EnrichmentTask,
    enrich_companies_batch_async,
    enrich_company_async,
)

# Orchestration
from solstein.worker.orchestration import refresh_all_sources

# Refresh tasks (all 12 sources)
from solstein.worker.refresh_tasks import (
    create_refresh_task,
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

__all__ = [
    # Base utilities
    "DeadLetterQueue",
    "dead_letter_queue",
    "get_db_manager",
    "get_tracked_company_ids",
    "store_facts",
    # Refresh tasks
    "refresh_sec_edgar",
    "refresh_companies_house",
    "refresh_news_signals",
    "refresh_github",
    "refresh_yahoo_finance",
    "refresh_patents",
    "refresh_news",
    "refresh_website",
    "refresh_linkedin",
    "refresh_funding",
    "refresh_global_market",
    "refresh_web_search",
    "create_refresh_task",
    # Enrichment tasks
    "EnrichmentTask",
    "enrich_company_async",
    "enrich_companies_batch_async",
    # Orchestration
    "refresh_all_sources",
]
