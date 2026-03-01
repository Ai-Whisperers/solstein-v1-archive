"""Celery tasks for data refresh operations - Refactored with Dependency Injection.

This version uses dependency injection to allow testing without sys.modules manipulation.

Usage:
    # Normal execution (production)
    refresh_sec_edgar.delay()
    
    # Testing with dependency injection
    from unittest.mock import MagicMock
    mock_connector = MagicMock()
    mock_connector.fetch_facts = AsyncMock(return_value=[])
    refresh_sec_edgar(connector=mock_connector)
"""

from typing import Optional
from celery import shared_task, Task
from celery.exceptions import MaxRetriesExceededError, SoftTimeLimitExceeded
from loguru import logger
from sqlalchemy import select
from datetime import datetime, timezone

from solstein.config import get_settings
from solstein.core.ports import DataConnector
from solstein.infrastructure.database import DatabaseManager
from solstein.infrastructure.database_models import CompanyRecord

# Import connectors for default behavior
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


def _get_db_manager():
    """Get initialized database manager."""
    settings = get_settings()
    db_manager = DatabaseManager(settings)
    db_manager.init_async()
    return db_manager


async def _get_tracked_company_ids(db_manager) -> list[str]:
    """Get list of tracked company IDs from database."""
    async with db_manager.get_session() as session:
        result = await session.execute(select(CompanyRecord.company_id))
        return [row[0] for row in result.fetchall()]


async def _store_facts(db_manager, facts: list[dict], source: str) -> int:
    """Store fetched facts in database."""
    stored_count = 0
    async with db_manager.get_session() as session:
        for fact in facts:
            try:
                company_id = fact.get("company_id")
                if not company_id:
                    continue
                stored_count += 1
            except Exception as e:
                logger.warning(f"Failed to store fact from {source}: {e}")
                continue
        await session.commit()
    return stored_count


class DeadLetterQueue:
    """Track permanently failed jobs after max retries exceeded."""

    def __init__(self):
        self.failed_jobs = []

    def record_failure(self, task_name: str, task_id: str, error: str, attempt: int):
        """Record a permanently failed job."""
        logger.info(
            f"[RETRY-FAILED] {task_name} (task_id={task_id}): {error} after {attempt} attempts"
        )
        self.failed_jobs.append(
            {
                "task_name": task_name,
                "task_id": task_id,
                "error": error,
                "final_attempt": attempt,
                "timestamp": datetime.now(timezone.utc),
            }
        )


dead_letter_queue = DeadLetterQueue()


@shared_task(name="solstein.worker_tasks.refresh_sec_edgar", bind=True, max_retries=3)
def refresh_sec_edgar(
    self,
    connector: Optional[DataConnector] = None
):
    """Refresh SEC EDGAR data for all tracked companies.
    
    Args:
        connector: Optional DataConnector instance. If None, uses SECEDGARRefreshConnector.
        
    Phase 13.4: Implements exponential backoff retry logic
    - Attempt 1: 5 seconds
    - Attempt 2: 10 seconds
    - Attempt 3: 20 seconds
    """
    logger.info("Starting SEC EDGAR refresh task")

    try:
        import asyncio

        async def _refresh():
            db_manager = _get_db_manager()
            company_ids = await _get_tracked_company_ids(db_manager)

            if not company_ids:
                logger.warning("No tracked companies found for SEC EDGAR refresh")
                return {"status": "completed", "source": "sec_edgar", "facts_fetched": 0}

            # Use provided connector or create default
            conn = connector or SECEDGARRefreshConnector(db_manager)
            from datetime import datetime, timedelta

            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)

            facts = await conn.fetch_facts(company_ids, start_date, end_date)
            stored = await _store_facts(db_manager, facts, "sec_edgar")

            logger.info(f"SEC EDGAR refresh completed: {stored} facts stored")
            return {"status": "completed", "source": "sec_edgar", "facts_fetched": stored}

        return asyncio.run(_refresh())

    except Exception as exc:
        logger.error(f"SEC EDGAR refresh failed: {exc}")
        countdown = 5 * (2**self.request.retries)
        logger.info(f"[RETRY-ATTEMPT-{self.request.retries + 1}] SEC EDGAR refresh will retry in {countdown}s")

        try:
            raise self.retry(exc=exc, countdown=countdown)
        except MaxRetriesExceededError:
            dead_letter_queue.record_failure("refresh_sec_edgar", self.request.id, str(exc), self.request.retries + 1)
            raise


@shared_task(name="solstein.worker_tasks.refresh_companies_house", bind=True, max_retries=3)
def refresh_companies_house(
    self,
    connector: Optional[DataConnector] = None
):
    """Refresh Companies House data for all tracked companies.
    
    Args:
        connector: Optional DataConnector instance. If None, uses CompaniesHouseRefreshConnector.
    """
    logger.info("Starting Companies House refresh task")

    try:
        import asyncio

        async def _refresh():
            db_manager = _get_db_manager()
            company_ids = await _get_tracked_company_ids(db_manager)

            if not company_ids:
                logger.warning("No tracked companies found for Companies House refresh")
                return {"status": "completed", "source": "companies_house", "facts_fetched": 0}

            conn = connector or CompaniesHouseRefreshConnector(db_manager)
            facts = await conn.fetch_facts(company_ids)
            stored = await _store_facts(db_manager, facts, "companies_house")

            logger.info(f"Companies House refresh completed: {stored} facts stored")
            return {"status": "completed", "source": "companies_house", "facts_fetched": stored}

        return asyncio.run(_refresh())

    except Exception as exc:
        logger.error(f"Companies House refresh failed: {exc}")
        countdown = 5 * (2**self.request.retries)
        logger.info(f"[RETRY-ATTEMPT-{self.request.retries + 1}] Companies House refresh will retry in {countdown}s")

        try:
            raise self.retry(exc=exc, countdown=countdown)
        except MaxRetriesExceededError:
            dead_letter_queue.record_failure("refresh_companies_house", self.request.id, str(exc), self.request.retries + 1)
            raise



# ============================================================================
# REMAINING 10 REFRESH TASKS (with DI pattern)
# ============================================================================


@shared_task(name="solstein.worker_tasks.refresh_news_signals", bind=True, max_retries=3)
def refresh_news_signals(
    self,
    connector: Optional[DataConnector] = None
):
    """Refresh news signals for all tracked companies.
    
    Args:
        connector: Optional DataConnector instance. If None, uses NewsSignalRefreshConnector.
    """
    logger.info("Starting News Signals refresh task")
    
    try:
        import asyncio
        
        async def _refresh():
            db_manager = _get_db_manager()
            company_ids = await _get_tracked_company_ids(db_manager)
            
            if not company_ids:
                logger.warning("No tracked companies found for News Signals refresh")
                return {"status": "completed", "source": "news_signals", "facts_fetched": 0}
            
            conn = connector or NewsSignalRefreshConnector(db_manager)
            facts = await conn.fetch_facts(company_ids)
            stored = await _store_facts(db_manager, facts, "news_signals")
            
            logger.info(f"News Signals refresh completed: {stored} facts stored")
            return {"status": "completed", "source": "news_signals", "facts_fetched": stored}
        
        return asyncio.run(_refresh())
    
    except Exception as exc:
        logger.error(f"News Signals refresh failed: {exc}")
        countdown = 5 * (2**self.request.retries)
        logger.info(f"[RETRY-ATTEMPT-{self.request.retries + 1}] News Signals refresh will retry in {countdown}s")
        
        try:
            raise self.retry(exc=exc, countdown=countdown)
        except MaxRetriesExceededError:
            dead_letter_queue.record_failure("refresh_news_signals", self.request.id, str(exc), self.request.retries + 1)
            raise


@shared_task(name="solstein.worker_tasks.refresh_github", bind=True, max_retries=3)
def refresh_github(
    self,
    connector: Optional[DataConnector] = None
):
    """Refresh GitHub data for all tracked companies.
    
    Args:
        connector: Optional DataConnector instance. If None, uses GitHubRefreshConnector.
    """
    logger.info("Starting GitHub refresh task")
    
    try:
        import asyncio
        
        async def _refresh():
            db_manager = _get_db_manager()
            company_ids = await _get_tracked_company_ids(db_manager)
            
            if not company_ids:
                logger.warning("No tracked companies found for GitHub refresh")
                return {"status": "completed", "source": "github", "facts_fetched": 0}
            
            conn = connector or GitHubRefreshConnector(db_manager)
            facts = await conn.fetch_facts(company_ids)
            stored = await _store_facts(db_manager, facts, "github")
            
            logger.info(f"GitHub refresh completed: {stored} facts stored")
            return {"status": "completed", "source": "github", "facts_fetched": stored}
        
        return asyncio.run(_refresh())
    
    except Exception as exc:
        logger.error(f"GitHub refresh failed: {exc}")
        countdown = 5 * (2**self.request.retries)
        logger.info(f"[RETRY-ATTEMPT-{self.request.retries + 1}] GitHub refresh will retry in {countdown}s")
        
        try:
            raise self.retry(exc=exc, countdown=countdown)
        except MaxRetriesExceededError:
            dead_letter_queue.record_failure("refresh_github", self.request.id, str(exc), self.request.retries + 1)
            raise


@shared_task(name="solstein.worker_tasks.refresh_yahoo_finance", bind=True, max_retries=3)
def refresh_yahoo_finance(
    self,
    connector: Optional[DataConnector] = None
):
    """Refresh Yahoo Finance market data for all tracked companies.
    
    Args:
        connector: Optional DataConnector instance. If None, uses YahooFinanceRefreshConnector.
    """
    logger.info("Starting Yahoo Finance refresh task")
    
    try:
        import asyncio
        
        async def _refresh():
            db_manager = _get_db_manager()
            company_ids = await _get_tracked_company_ids(db_manager)
            
            if not company_ids:
                logger.warning("No tracked companies found for Yahoo Finance refresh")
                return {"status": "completed", "source": "yahoo_finance", "facts_fetched": 0}
            
            conn = connector or YahooFinanceRefreshConnector(db_manager)
            facts = await conn.fetch_facts(company_ids)
            stored = await _store_facts(db_manager, facts, "yahoo_finance")
            
            logger.info(f"Yahoo Finance refresh completed: {stored} facts stored")
            return {"status": "completed", "source": "yahoo_finance", "facts_fetched": stored}
        
        return asyncio.run(_refresh())
    
    except Exception as exc:
        logger.error(f"Yahoo Finance refresh failed: {exc}")
        countdown = 5 * (2**self.request.retries)
        logger.info(f"[RETRY-ATTEMPT-{self.request.retries + 1}] Yahoo Finance refresh will retry in {countdown}s")
        
        try:
            raise self.retry(exc=exc, countdown=countdown)
        except MaxRetriesExceededError:
            dead_letter_queue.record_failure("refresh_yahoo_finance", self.request.id, str(exc), self.request.retries + 1)
            raise


@shared_task(name="solstein.worker_tasks.refresh_patents", bind=True, max_retries=3)
def refresh_patents(
    self,
    connector: Optional[DataConnector] = None
):
    """Refresh patent data for all tracked companies.
    
    Args:
        connector: Optional DataConnector instance. If None, uses PatentsRefreshConnector.
    """
    logger.info("Starting Patents refresh task")
    
    try:
        import asyncio
        
        async def _refresh():
            db_manager = _get_db_manager()
            company_ids = await _get_tracked_company_ids(db_manager)
            
            if not company_ids:
                logger.warning("No tracked companies found for Patents refresh")
                return {"status": "completed", "source": "patents", "facts_fetched": 0}
            
            conn = connector or PatentsRefreshConnector(db_manager)
            facts = await conn.fetch_facts(company_ids)
            stored = await _store_facts(db_manager, facts, "patents")
            
            logger.info(f"Patents refresh completed: {stored} facts stored")
            return {"status": "completed", "source": "patents", "facts_fetched": stored}
        
        return asyncio.run(_refresh())
    
    except Exception as exc:
        logger.error(f"Patents refresh failed: {exc}")
        countdown = 5 * (2**self.request.retries)
        logger.info(f"[RETRY-ATTEMPT-{self.request.retries + 1}] Patents refresh will retry in {countdown}s")
        
        try:
            raise self.retry(exc=exc, countdown=countdown)
        except MaxRetriesExceededError:
            dead_letter_queue.record_failure("refresh_patents", self.request.id, str(exc), self.request.retries + 1)
            raise


@shared_task(name="solstein.worker_tasks.refresh_news", bind=True, max_retries=3)
def refresh_news(
    self,
    connector: Optional[DataConnector] = None
):
    """Refresh news data for all tracked companies.
    
    Args:
        connector: Optional DataConnector instance. If None, uses NewsRefreshConnector.
    """
    logger.info("Starting News refresh task")
    
    try:
        import asyncio
        
        async def _refresh():
            db_manager = _get_db_manager()
            company_ids = await _get_tracked_company_ids(db_manager)
            
            if not company_ids:
                logger.warning("No tracked companies found for News refresh")
                return {"status": "completed", "source": "news", "facts_fetched": 0}
            
            conn = connector or NewsRefreshConnector(db_manager)
            facts = await conn.fetch_facts(company_ids)
            stored = await _store_facts(db_manager, facts, "news")
            
            logger.info(f"News refresh completed: {stored} facts stored")
            return {"status": "completed", "source": "news", "facts_fetched": stored}
        
        return asyncio.run(_refresh())
    
    except Exception as exc:
        logger.error(f"News refresh failed: {exc}")
        countdown = 5 * (2**self.request.retries)
        logger.info(f"[RETRY-ATTEMPT-{self.request.retries + 1}] News refresh will retry in {countdown}s")
        
        try:
            raise self.retry(exc=exc, countdown=countdown)
        except MaxRetriesExceededError:
            dead_letter_queue.record_failure("refresh_news", self.request.id, str(exc), self.request.retries + 1)
            raise


@shared_task(name="solstein.worker_tasks.refresh_website", bind=True, max_retries=3)
def refresh_website(
    self,
    connector: Optional[DataConnector] = None
):
    """Refresh website data for all tracked companies.
    
    Args:
        connector: Optional DataConnector instance. If None, uses WebsiteRefreshConnector.
    """
    logger.info("Starting Website refresh task")
    
    try:
        import asyncio
        
        async def _refresh():
            db_manager = _get_db_manager()
            company_ids = await _get_tracked_company_ids(db_manager)
            
            if not company_ids:
                logger.warning("No tracked companies found for Website refresh")
                return {"status": "completed", "source": "website", "facts_fetched": 0}
            
            conn = connector or WebsiteRefreshConnector(db_manager)
            facts = await conn.fetch_facts(company_ids)
            stored = await _store_facts(db_manager, facts, "website")
            
            logger.info(f"Website refresh completed: {stored} facts stored")
            return {"status": "completed", "source": "website", "facts_fetched": stored}
        
        return asyncio.run(_refresh())
    
    except Exception as exc:
        logger.error(f"Website refresh failed: {exc}")
        countdown = 5 * (2**self.request.retries)
        logger.info(f"[RETRY-ATTEMPT-{self.request.retries + 1}] Website refresh will retry in {countdown}s")
        
        try:
            raise self.retry(exc=exc, countdown=countdown)
        except MaxRetriesExceededError:
            dead_letter_queue.record_failure("refresh_website", self.request.id, str(exc), self.request.retries + 1)
            raise


@shared_task(name="solstein.worker_tasks.refresh_linkedin", bind=True, max_retries=3)
def refresh_linkedin(
    self,
    connector: Optional[DataConnector] = None
):
    """Refresh LinkedIn data for all tracked companies.
    
    Args:
        connector: Optional DataConnector instance. If None, uses LinkedInRefreshConnector.
    """
    logger.info("Starting LinkedIn refresh task")
    
    try:
        import asyncio
        
        async def _refresh():
            db_manager = _get_db_manager()
            company_ids = await _get_tracked_company_ids(db_manager)
            
            if not company_ids:
                logger.warning("No tracked companies found for LinkedIn refresh")
                return {"status": "completed", "source": "linkedin", "facts_fetched": 0}
            
            conn = connector or LinkedInRefreshConnector(db_manager)
            facts = await conn.fetch_facts(company_ids)
            stored = await _store_facts(db_manager, facts, "linkedin")
            
            logger.info(f"LinkedIn refresh completed: {stored} facts stored")
            return {"status": "completed", "source": "linkedin", "facts_fetched": stored}
        
        return asyncio.run(_refresh())
    
    except Exception as exc:
        logger.error(f"LinkedIn refresh failed: {exc}")
        countdown = 5 * (2**self.request.retries)
        logger.info(f"[RETRY-ATTEMPT-{self.request.retries + 1}] LinkedIn refresh will retry in {countdown}s")
        
        try:
            raise self.retry(exc=exc, countdown=countdown)
        except MaxRetriesExceededError:
            dead_letter_queue.record_failure("refresh_linkedin", self.request.id, str(exc), self.request.retries + 1)
            raise


@shared_task(name="solstein.worker_tasks.refresh_funding", bind=True, max_retries=3)
def refresh_funding(
    self,
    connector: Optional[DataConnector] = None
):
    """Refresh funding data for all tracked companies.
    
    Args:
        connector: Optional DataConnector instance. If None, uses FundingRefreshConnector.
    """
    logger.info("Starting Funding refresh task")
    
    try:
        import asyncio
        
        async def _refresh():
            db_manager = _get_db_manager()
            company_ids = await _get_tracked_company_ids(db_manager)
            
            if not company_ids:
                logger.warning("No tracked companies found for Funding refresh")
                return {"status": "completed", "source": "funding", "facts_fetched": 0}
            
            conn = connector or FundingRefreshConnector(db_manager)
            facts = await conn.fetch_facts(company_ids)
            stored = await _store_facts(db_manager, facts, "funding")
            
            logger.info(f"Funding refresh completed: {stored} facts stored")
            return {"status": "completed", "source": "funding", "facts_fetched": stored}
        
        return asyncio.run(_refresh())
    
    except Exception as exc:
        logger.error(f"Funding refresh failed: {exc}")
        countdown = 5 * (2**self.request.retries)
        logger.info(f"[RETRY-ATTEMPT-{self.request.retries + 1}] Funding refresh will retry in {countdown}s")
        
        try:
            raise self.retry(exc=exc, countdown=countdown)
        except MaxRetriesExceededError:
            dead_letter_queue.record_failure("refresh_funding", self.request.id, str(exc), self.request.retries + 1)
            raise


@shared_task(name="solstein.worker_tasks.refresh_global_market", bind=True, max_retries=3)
def refresh_global_market(
    self,
    connector: Optional[DataConnector] = None
):
    """Refresh global market data.
    
    Args:
        connector: Optional DataConnector instance. If None, uses GlobalMarketRefreshConnector.
    """
    logger.info("Starting Global Market refresh task")
    
    try:
        import asyncio
        
        async def _refresh():
            db_manager = _get_db_manager()
            company_ids = await _get_tracked_company_ids(db_manager)
            
            if not company_ids:
                logger.warning("No tracked companies found for Global Market refresh")
                return {"status": "completed", "source": "global_market", "facts_fetched": 0}
            
            conn = connector or GlobalMarketRefreshConnector(db_manager)
            facts = await conn.fetch_facts(company_ids)
            stored = await _store_facts(db_manager, facts, "global_market")
            
            logger.info(f"Global Market refresh completed: {stored} facts stored")
            return {"status": "completed", "source": "global_market", "facts_fetched": stored}
        
        return asyncio.run(_refresh())
    
    except Exception as exc:
        logger.error(f"Global Market refresh failed: {exc}")
        countdown = 5 * (2**self.request.retries)
        logger.info(f"[RETRY-ATTEMPT-{self.request.retries + 1}] Global Market refresh will retry in {countdown}s")
        
        try:
            raise self.retry(exc=exc, countdown=countdown)
        except MaxRetriesExceededError:
            dead_letter_queue.record_failure("refresh_global_market", self.request.id, str(exc), self.request.retries + 1)
            raise


@shared_task(name="solstein.worker_tasks.refresh_web_search", bind=True, max_retries=3)
def refresh_web_search(
    self,
    connector: Optional[DataConnector] = None
):
    """Refresh web search data for all tracked companies.
    
    Args:
        connector: Optional DataConnector instance. If None, uses WebSearchRefreshConnector.
    """
    logger.info("Starting Web Search refresh task")
    
    try:
        import asyncio
        
        async def _refresh():
            db_manager = _get_db_manager()
            company_ids = await _get_tracked_company_ids(db_manager)
            
            if not company_ids:
                logger.warning("No tracked companies found for Web Search refresh")
                return {"status": "completed", "source": "web_search", "facts_fetched": 0}
            
            conn = connector or WebSearchRefreshConnector(db_manager)
            facts = await conn.fetch_facts(company_ids)
            stored = await _store_facts(db_manager, facts, "web_search")
            
            logger.info(f"Web Search refresh completed: {stored} facts stored")
            return {"status": "completed", "source": "web_search", "facts_fetched": stored}
        
        return asyncio.run(_refresh())
    
    except Exception as exc:
        logger.error(f"Web Search refresh failed: {exc}")
        countdown = 5 * (2**self.request.retries)
        logger.info(f"[RETRY-ATTEMPT-{self.request.retries + 1}] Web Search refresh will retry in {countdown}s")
        
        try:
            raise self.retry(exc=exc, countdown=countdown)
        except MaxRetriesExceededError:
            dead_letter_queue.record_failure("refresh_web_search", self.request.id, str(exc), self.request.retries + 1)
            raise


@shared_task(name="solstein.worker_tasks.refresh_all_sources", bind=True)
def refresh_all_sources(self):
    """Refresh all data sources.
    
    Queues refresh tasks for all 12 sources in parallel.
    """
    logger.info("Starting full refresh for all sources")
    
    results = []
    
    # All 12 sources
    results.append(refresh_sec_edgar.apply_async().id)
    results.append(refresh_companies_house.apply_async().id)
    results.append(refresh_news_signals.apply_async().id)
    results.append(refresh_github.apply_async().id)
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


# Export all tasks
__all__ = [
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
    "refresh_all_sources",
]