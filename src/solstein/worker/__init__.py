"""Celery worker tasks package.

EPIC-021: Modularized from monolithic 902-line file to specialized modules.
"""

# Base utilities
from .base import (
    DeadLetterQueue,
    dead_letter_queue,
    get_db_manager,
    get_tracked_company_ids,
    store_facts,
)

# Enrichment tasks
from .enrichment_tasks import (
    EnrichmentTask,
    enrich_companies_batch_async,
    enrich_company_async,
)

# Orchestration
from .orchestration import refresh_all_sources

# Refresh tasks (all 12 sources)
from .refresh_tasks import (
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


def run_worker():
    return None


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
    "run_worker",
]
