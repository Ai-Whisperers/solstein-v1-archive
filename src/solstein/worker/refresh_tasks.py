"""Refresh tasks for all data sources.

Extracted from worker_tasks.py as part of EPIC-021 file splitting.
Provides Celery tasks for refreshing data from 12 sources.

STORY-092: This module is the canonical location for all 12 Beat-scheduled refresh
tasks.  It incorporates:
  - STORY-088: DLQ persistence (via dead_letter_queue.record_failure)
  - STORY-089: at-least-once delivery (task_acks_late / task_reject_on_worker_lost
               configured in celery_config.py)
  - STORY-090: idempotency deduplication lock (via deduplicate wrapper applied in
               create_refresh_task factory with task_name_override per task)
"""

from __future__ import annotations

import asyncio
import contextlib
import traceback
from collections.abc import Callable
from datetime import datetime, timedelta, timezone

from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from loguru import logger

from solstein.config import get_settings
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
from .idempotency import deduplicate
from .tenant_isolation import task_tenant_context, validate_task_tenant_id


def _run_in_dedicated_loop(coro):
    """Run a coroutine in a short-lived event loop owned by this task."""
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    finally:
        with contextlib.suppress(Exception):
            loop.run_until_complete(loop.shutdown_asyncgens())
        asyncio.set_event_loop(None)
        loop.close()


def _handle_retry_or_dlq(
    task_self,
    exc: Exception,
    task_name: str,
    source_name: str,
) -> None:
    """Apply exponential back-off retry; persist to DLQ on MaxRetriesExceededError.

    STORY-088: DLQ persistence. Phase 13.4: backoff = 5 * 2^(attempt-1) seconds.
    Extracted from create_refresh_task to keep the factory under the 100-line limit.
    """
    countdown = 5 * (2**task_self.request.retries)
    logger.info(f"[RETRY-ATTEMPT-{task_self.request.retries + 1}] {source_name} refresh will retry in {countdown}s")
    try:
        raise task_self.retry(exc=exc, countdown=countdown)  # noqa: B904
    except MaxRetriesExceededError:
        tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        dead_letter_queue.record_failure(
            task_name.split(".")[-1],
            task_self.request.id,
            exc,
            task_self.request.retries + 1,
            traceback_text=tb,
            context={"source_name": source_name},
        )
        raise


def create_refresh_task(
    task_name: str,
    connector_class: type,
    source_name: str,
    get_date_range: Callable[[], tuple[datetime, datetime]] | None = None,
):
    """Factory: create a Celery refresh task wired with EPIC-025 reliability guarantees.

    Incorporates STORY-066 (tenant isolation), STORY-088 (DLQ), STORY-089
    (at-least-once via celery_config.py), and STORY-090 (idempotency dedup lock).
    Lock TTL = task_time_limit; fail-open on Redis unavailability.

    Args:
        task_name: Full Celery task name (e.g., "solstein.worker_tasks.refresh_sec_edgar")
        connector_class: Connector class to instantiate
        source_name: Human-readable source label used in logs (e.g., "SEC EDGAR")
        get_date_range: Optional callable returning ``(start_date, end_date)``

    Returns:
        Celery shared_task guarded by idempotency dedup lock
    """
    _settings = get_settings()
    _task_ttl: int = _settings.celery_timing.task_time_limit

    def _refresh_task_body(self, tenant_id: str):
        """Refresh all tracked companies for tenant_id (STORY-066: tenant_id required)."""
        validated_tenant = validate_task_tenant_id(tenant_id, task_name=task_name)
        logger.info(f"Starting {source_name} refresh task for tenant {validated_tenant[:8]}...")

        try:

            async def _refresh():
                db_manager = get_db_manager()
                company_ids = await get_tracked_company_ids(db_manager, tenant_id=validated_tenant)

                if not company_ids:
                    logger.warning(
                        f"No tracked companies found for {source_name} refresh (tenant={validated_tenant[:8]}...)"
                    )
                    return {
                        "status": "completed",
                        "source": source_name.lower().replace(" ", "_"),
                        "facts_fetched": 0,
                        "tenant_id": validated_tenant,
                    }

                connector = connector_class(db_manager)

                if get_date_range:
                    start_date, end_date = get_date_range()
                    facts = await connector.fetch_facts(company_ids, start_date, end_date)
                else:
                    facts = await connector.fetch_facts(company_ids)

                stored = await store_facts(
                    db_manager, facts, source_name.lower().replace(" ", "_"), tenant_id=validated_tenant
                )

                logger.info(
                    f"{source_name} refresh completed: {stored} facts stored (tenant={validated_tenant[:8]}...)"
                )
                return {
                    "status": "completed",
                    "source": source_name.lower().replace(" ", "_"),
                    "facts_fetched": stored,
                    "tenant_id": validated_tenant,
                }

            with task_tenant_context(validated_tenant):
                return _run_in_dedicated_loop(_refresh())

        except Exception as exc:  # noqa: BLE001
            logger.error(f"{source_name} refresh failed: {exc}")
            _handle_retry_or_dlq(self, exc, task_name, source_name)

    # STORY-090/STORY-092: Apply idempotency dedup lock with the full task_name
    # as the lock discriminator so each of the 12 tasks gets a unique Redis key.
    # TTL matches task_time_limit — ensures the lock is held for the maximum
    # allowed task duration and releases before the next schedule window.
    _body_with_dedup = deduplicate(ttl=_task_ttl, task_name_override=task_name)(_refresh_task_body)

    # Register as a Celery shared_task. bind=True injects `self` (task instance)
    # as the first argument so retries can call self.retry().
    refresh_task = shared_task(name=task_name, bind=True, max_retries=3)(_body_with_dedup)
    return refresh_task


# ============================================================================
# ORIGINAL 4 REFRESH TASKS
# ============================================================================

# SEC EDGAR: 365 days lookback
refresh_sec_edgar = create_refresh_task(
    "solstein.worker_tasks.refresh_sec_edgar",
    SECEDGARRefreshConnector,
    "SEC EDGAR",
    lambda: (datetime.now(tz=timezone.utc) - timedelta(days=365), datetime.now(tz=timezone.utc)),
)

# Companies House: 90 days lookback
refresh_companies_house = create_refresh_task(
    "solstein.worker_tasks.refresh_companies_house",
    CompaniesHouseRefreshConnector,
    "Companies House",
    lambda: (datetime.now(tz=timezone.utc) - timedelta(days=90), datetime.now(tz=timezone.utc)),
)

# News Signals: 24 hours lookback
refresh_news_signals = create_refresh_task(
    "solstein.worker_tasks.refresh_news_signals",
    NewsSignalRefreshConnector,
    "News Signals",
    lambda: (datetime.now(tz=timezone.utc) - timedelta(hours=24), datetime.now(tz=timezone.utc)),
)

# GitHub: 7 days lookback
refresh_github = create_refresh_task(
    "solstein.worker_tasks.refresh_github",
    GitHubRefreshConnector,
    "GitHub",
    lambda: (datetime.now(tz=timezone.utc) - timedelta(days=7), datetime.now(tz=timezone.utc)),
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
    lambda: (datetime.now(tz=timezone.utc) - timedelta(days=30), datetime.now(tz=timezone.utc)),
)

# News: 6 hours lookback
refresh_news = create_refresh_task(
    "solstein.worker_tasks.refresh_news",
    NewsRefreshConnector,
    "News",
    lambda: (datetime.now(tz=timezone.utc) - timedelta(hours=6), datetime.now(tz=timezone.utc)),
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
    lambda: (datetime.now(tz=timezone.utc) - timedelta(days=30), datetime.now(tz=timezone.utc)),
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
    lambda: (datetime.now(tz=timezone.utc) - timedelta(hours=12), datetime.now(tz=timezone.utc)),
)
