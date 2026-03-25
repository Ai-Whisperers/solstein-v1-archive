"""Refresh tasks for all data sources.

Extracted from worker_tasks.py as part of EPIC-021 file splitting.
Provides Celery tasks for refreshing data from 12 sources.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Callable

from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from loguru import logger

from solstein.infrastructure.connectors.companies_house_refresh import (
    CompaniesHouseRefreshConnector,
)
from solstein.infrastructure.connectors.funding_refresh import FundingRefreshConnector
from solstein.infrastructure.connectors.github_refresh import GitHubRefreshConnector
from solstein.infrastructure.connectors.global_market_refresh import (
    GlobalMarketRefreshConnector,
)
from solstein.infrastructure.connectors.linkedin_refresh import LinkedInRefreshConnector
from solstein.infrastructure.connectors.news_refresh import NewsRefreshConnector
from solstein.infrastructure.connectors.news_signal_refresh import (
    NewsSignalRefreshConnector,
)
from solstein.infrastructure.connectors.patents_refresh import PatentsRefreshConnector
from solstein.infrastructure.connectors.sec_edgar_refresh import SECEDGARRefreshConnector
from solstein.infrastructure.connectors.web_search_refresh import WebSearchRefreshConnector
from solstein.infrastructure.connectors.website_refresh import WebsiteRefreshConnector
from solstein.infrastructure.connectors.yahoo_finance_refresh import (
    YahooFinanceRefreshConnector,
)

from .base import dead_letter_queue, get_db_manager, get_tracked_company_ids, store_facts


def _run_in_dedicated_loop(coro):
    """Run a coroutine in a short-lived event loop owned by this task."""
    import asyncio

    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    finally:
        try:
            loop.run_until_complete(loop.shutdown_asyncgens())
        except Exception:
            pass
        asyncio.set_event_loop(None)
        loop.close()


def create_refresh_task(
    task_name: str,
    connector_class: type,
    source_name: str,
    get_date_range: Callable[[], tuple[datetime, datetime]] | None = None,
):
    """Factory function to create a refresh task with retry logic.

    Args:
        task_name: Full Celery task name (e.g., "solstein.worker_tasks.refresh_sec_edgar")
        connector_class: Connector class to instantiate
        source_name: Source name for logging (e.g., "SEC EDGAR")
        get_date_range: Optional function to get (start_date, end_date) tuple

    Returns:
        Configured Celery task function
    """

    @shared_task(name=task_name, bind=True, max_retries=3)
    def refresh_task(self):
        """Refresh data for all tracked companies."""
        logger.info(f"Starting {source_name} refresh task")

        try:
            async def _refresh():
                db_manager = get_db_manager()
                company_ids = await get_tracked_company_ids(db_manager)

                if not company_ids:
                    logger.warning(f"No tracked companies found for {source_name} refresh")
                    return {"status": "completed", "source": source_name.lower().replace(" ", "_"), "facts_fetched": 0}

                connector = connector_class(db_manager)

                if get_date_range:
                    start_date, end_date = get_date_range()
                    facts = await connector.fetch_facts(company_ids, start_date, end_date)
                else:
                    facts = await connector.fetch_facts(company_ids)

                stored = await store_facts(db_manager, facts, source_name.lower().replace(" ", "_"))

                logger.info(f"{source_name} refresh completed: {stored} facts stored")
                return {"status": "completed", "source": source_name.lower().replace(" ", "_"), "facts_fetched": stored}

            return _run_in_dedicated_loop(_refresh())

        except Exception as exc:
            logger.error(f"{source_name} refresh failed: {exc}")
            # Phase 13.4: Exponential backoff - 5 * (2^(attempt-1))
            countdown = 5 * (2**self.request.retries)
            logger.info(f"[RETRY-ATTEMPT-{self.request.retries + 1}] {source_name} refresh will retry in {countdown}s")

            try:
                raise self.retry(exc=exc, countdown=countdown)  # noqa: B904
            except MaxRetriesExceededError:
                dead_letter_queue.record_failure(
                    task_name.split(".")[-1], self.request.id, str(exc), self.request.retries + 1
                )
                raise

    return refresh_task


# ============================================================================
# ORIGINAL 4 REFRESH TASKS
# ============================================================================

# SEC EDGAR: 365 days lookback
refresh_sec_edgar = create_refresh_task(
    "solstein.worker_tasks.refresh_sec_edgar",
    SECEDGARRefreshConnector,
    "SEC EDGAR",
    lambda: (datetime.now() - timedelta(days=365), datetime.now()),
)

# Companies House: 90 days lookback
refresh_companies_house = create_refresh_task(
    "solstein.worker_tasks.refresh_companies_house",
    CompaniesHouseRefreshConnector,
    "Companies House",
    lambda: (datetime.now() - timedelta(days=90), datetime.now()),
)

# News Signals: 24 hours lookback
refresh_news_signals = create_refresh_task(
    "solstein.worker_tasks.refresh_news_signals",
    NewsSignalRefreshConnector,
    "News Signals",
    lambda: (datetime.now() - timedelta(hours=24), datetime.now()),
)

# GitHub: 7 days lookback
refresh_github = create_refresh_task(
    "solstein.worker_tasks.refresh_github",
    GitHubRefreshConnector,
    "GitHub",
    lambda: (datetime.now() - timedelta(days=7), datetime.now()),
)

# ============================================================================
# NEW REFRESH CONNECTORS (Tasks 5-12)
# ============================================================================

# Yahoo Finance: no date range needed
refresh_yahoo_finance = create_refresh_task(
    "solstein.worker_tasks.refresh_yahoo_finance",
    YahooFinanceRefreshConnector,
    "Yahoo Finance",
)

# Patents: 30 days lookback
refresh_patents = create_refresh_task(
    "solstein.worker_tasks.refresh_patents",
    PatentsRefreshConnector,
    "Patents",
    lambda: (datetime.now() - timedelta(days=30), datetime.now()),
)

# News: 6 hours lookback
refresh_news = create_refresh_task(
    "solstein.worker_tasks.refresh_news",
    NewsRefreshConnector,
    "News",
    lambda: (datetime.now() - timedelta(hours=6), datetime.now()),
)

# Website: no date range needed
refresh_website = create_refresh_task(
    "solstein.worker_tasks.refresh_website",
    WebsiteRefreshConnector,
    "Website",
)

# LinkedIn: no date range needed
refresh_linkedin = create_refresh_task(
    "solstein.worker_tasks.refresh_linkedin",
    LinkedInRefreshConnector,
    "LinkedIn",
)

# Funding: 30 days lookback
refresh_funding = create_refresh_task(
    "solstein.worker_tasks.refresh_funding",
    FundingRefreshConnector,
    "Funding",
    lambda: (datetime.now() - timedelta(days=30), datetime.now()),
)

# Global Market: no date range needed
refresh_global_market = create_refresh_task(
    "solstein.worker_tasks.refresh_global_market",
    GlobalMarketRefreshConnector,
    "Global Market",
)

# Web Search: 12 hours lookback
refresh_web_search = create_refresh_task(
    "solstein.worker_tasks.refresh_web_search",
    WebSearchRefreshConnector,
    "Web Search",
    lambda: (datetime.now() - timedelta(hours=12), datetime.now()),
)
