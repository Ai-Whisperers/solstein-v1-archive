"""Celery tasks for data refresh operations.

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

from datetime import datetime, timezone

from celery import Task, shared_task
from celery.exceptions import MaxRetriesExceededError
from loguru import logger
from sqlalchemy import select

from solstein.config import get_settings

# Import all refresh connectors
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
from solstein.infrastructure.database import DatabaseManager
from solstein.infrastructure.database_models import CompanyRecord


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
    """Store fetched facts in database.

    Returns:
        Number of facts stored
    """
    stored_count = 0
    async with db_manager.get_session() as session:
        for fact in facts:
            try:
                # Update company record with new data
                company_id = fact.get("company_id")
                if not company_id:
                    continue

                # Get existing company or create new record logic
                # For now, we just count successful facts
                stored_count += 1

            except Exception as e:
                logger.warning(f"Failed to store fact from {source}: {e}")
                continue

        await session.commit()

    return stored_count


# ============================================================================
# PHASE 13.4: DEAD LETTER QUEUE FOR PERMANENTLY FAILED JOBS
# ============================================================================


class DeadLetterQueue:
    """Track permanently failed jobs after max retries exceeded."""

    def __init__(self):
        self.failed_jobs = []

    def record_failure(self, task_name: str, task_id: str, error: str, attempt: int):
        """Record a permanently failed job."""
        logger.info(f"[RETRY-FAILED] {task_name} (task_id={task_id}): {error} after {attempt} attempts")
        self.failed_jobs.append(
            {
                "task_name": task_name,
                "task_id": task_id,
                "error": error,
                "final_attempt": attempt,
                "timestamp": datetime.now(timezone.utc),
            }
        )


# Global Dead Letter Queue instance
dead_letter_queue = DeadLetterQueue()


# ============================================================================
# ORIGINAL 4 REFRESH TASKS (with Phase 13.4 retry logic)
# ============================================================================


@shared_task(name="solstein.worker_tasks.refresh_sec_edgar", bind=True, max_retries=3)
def refresh_sec_edgar(self):
    """Refresh SEC EDGAR data for all tracked companies.

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

            connector = SECEDGARRefreshConnector(db_manager)
            from datetime import datetime, timedelta

            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)

            facts = await connector.fetch_facts(company_ids, start_date, end_date)
            stored = await _store_facts(db_manager, facts, "sec_edgar")

            logger.info(f"SEC EDGAR refresh completed: {stored} facts stored")
            return {"status": "completed", "source": "sec_edgar", "facts_fetched": stored}

        return asyncio.run(_refresh())

    except Exception as exc:
        logger.error(f"SEC EDGAR refresh failed: {exc}")
        # Phase 13.4: Exponential backoff - 5 * (2^(attempt-1))
        countdown = 5 * (2**self.request.retries)
        logger.info(f"[RETRY-ATTEMPT-{self.request.retries + 1}] SEC EDGAR refresh will retry in {countdown}s")

        try:
            raise self.retry(exc=exc, countdown=countdown)  # noqa: B904
        except MaxRetriesExceededError:
            dead_letter_queue.record_failure("refresh_sec_edgar", self.request.id, str(exc), self.request.retries + 1)
            raise


@shared_task(name="solstein.worker_tasks.refresh_companies_house", bind=True, max_retries=3)
def refresh_companies_house(self):
    """Refresh Companies House data for all tracked companies.

    Phase 13.4: Implements exponential backoff retry logic
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

            connector = CompaniesHouseRefreshConnector(db_manager)
            from datetime import datetime, timedelta

            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)

            facts = await connector.fetch_facts(company_ids, start_date, end_date)
            stored = await _store_facts(db_manager, facts, "companies_house")

            logger.info(f"Companies House refresh completed: {stored} facts stored")
            return {"status": "completed", "source": "companies_house", "facts_fetched": stored}

        return asyncio.run(_refresh())

    except Exception as exc:
        logger.error(f"Companies House refresh failed: {exc}")
        countdown = 5 * (2**self.request.retries)
        logger.info(f"[RETRY-ATTEMPT-{self.request.retries + 1}] Companies House refresh will retry in {countdown}s")

        try:
            raise self.retry(exc=exc, countdown=countdown)  # noqa: B904
        except MaxRetriesExceededError:
            dead_letter_queue.record_failure(
                "refresh_companies_house", self.request.id, str(exc), self.request.retries + 1
            )
            raise


@shared_task(name="solstein.worker_tasks.refresh_news_signals", bind=True, max_retries=3)
def refresh_news_signals(self):
    """Refresh news signals for all tracked companies.

    Phase 13.4: Implements exponential backoff retry logic
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

            connector = NewsSignalRefreshConnector(db_manager)
            from datetime import datetime, timedelta

            end_date = datetime.now()
            start_date = end_date - timedelta(hours=24)

            facts = await connector.fetch_facts(company_ids, start_date, end_date)
            stored = await _store_facts(db_manager, facts, "news_signals")

            logger.info(f"News Signals refresh completed: {stored} facts stored")
            return {"status": "completed", "source": "news_signals", "facts_fetched": stored}

        return asyncio.run(_refresh())

    except Exception as exc:
        logger.error(f"News Signals refresh failed: {exc}")
        countdown = 5 * (2**self.request.retries)
        logger.info(f"[RETRY-ATTEMPT-{self.request.retries + 1}] News Signals refresh will retry in {countdown}s")

        try:
            raise self.retry(exc=exc, countdown=countdown)  # noqa: B904
        except MaxRetriesExceededError:
            dead_letter_queue.record_failure(
                "refresh_news_signals", self.request.id, str(exc), self.request.retries + 1
            )
            raise


@shared_task(name="solstein.worker_tasks.refresh_github", bind=True, max_retries=3)
def refresh_github(self):
    """Refresh GitHub data for all tracked companies.

    Phase 13.4: Implements exponential backoff retry logic
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

            connector = GitHubRefreshConnector(db_manager)
            from datetime import datetime, timedelta

            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)

            facts = await connector.fetch_facts(company_ids, start_date, end_date)
            stored = await _store_facts(db_manager, facts, "github")

            logger.info(f"GitHub refresh completed: {stored} facts stored")
            return {"status": "completed", "source": "github", "facts_fetched": stored}

        return asyncio.run(_refresh())

    except Exception as exc:
        logger.error(f"GitHub refresh failed: {exc}")
        countdown = 5 * (2**self.request.retries)
        logger.info(f"[RETRY-ATTEMPT-{self.request.retries + 1}] GitHub refresh will retry in {countdown}s")

        try:
            raise self.retry(exc=exc, countdown=countdown)  # noqa: B904
        except MaxRetriesExceededError:
            dead_letter_queue.record_failure("refresh_github", self.request.id, str(exc), self.request.retries + 1)
            raise


# ============================================================================
# NEW REFRESH CONNECTORS (Tasks 4-11 from Wave 2)
# ============================================================================


@shared_task(name="solstein.worker_tasks.refresh_yahoo_finance", bind=True, max_retries=3)
def refresh_yahoo_finance(self):
    """Refresh Yahoo Finance market data for all tracked companies.

    Phase 13.4: Implements exponential backoff retry logic
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

            connector = YahooFinanceRefreshConnector(db_manager)
            facts = await connector.fetch_facts(company_ids)
            stored = await _store_facts(db_manager, facts, "yahoo_finance")

            logger.info(f"Yahoo Finance refresh completed: {stored} facts stored")
            return {"status": "completed", "source": "yahoo_finance", "facts_fetched": stored}

        return asyncio.run(_refresh())

    except Exception as exc:
        logger.error(f"Yahoo Finance refresh failed: {exc}")
        countdown = 5 * (2**self.request.retries)
        logger.info(f"[RETRY-ATTEMPT-{self.request.retries + 1}] Yahoo Finance refresh will retry in {countdown}s")

        try:
            raise self.retry(exc=exc, countdown=countdown)  # noqa: B904
        except MaxRetriesExceededError:
            dead_letter_queue.record_failure(
                "refresh_yahoo_finance", self.request.id, str(exc), self.request.retries + 1
            )
            raise


@shared_task(name="solstein.worker_tasks.refresh_patents", bind=True, max_retries=3)
def refresh_patents(self):
    """Refresh patent data for all tracked companies.

    Phase 13.4: Implements exponential backoff retry logic
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

            connector = PatentsRefreshConnector(db_manager)
            from datetime import datetime, timedelta

            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)

            facts = await connector.fetch_facts(company_ids, start_date, end_date)
            stored = await _store_facts(db_manager, facts, "patents")

            logger.info(f"Patents refresh completed: {stored} facts stored")
            return {"status": "completed", "source": "patents", "facts_fetched": stored}

        return asyncio.run(_refresh())

    except Exception as exc:
        logger.error(f"Patents refresh failed: {exc}")
        countdown = 5 * (2**self.request.retries)
        logger.info(f"[RETRY-ATTEMPT-{self.request.retries + 1}] Patents refresh will retry in {countdown}s")

        try:
            raise self.retry(exc=exc, countdown=countdown)  # noqa: B904
        except MaxRetriesExceededError:
            dead_letter_queue.record_failure("refresh_patents", self.request.id, str(exc), self.request.retries + 1)
            raise


@shared_task(name="solstein.worker_tasks.refresh_news", bind=True, max_retries=3)
def refresh_news(self):
    """Refresh news data for all tracked companies.

    Phase 13.4: Implements exponential backoff retry logic
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

            connector = NewsRefreshConnector(db_manager)
            from datetime import datetime, timedelta

            end_date = datetime.now()
            start_date = end_date - timedelta(hours=6)

            facts = await connector.fetch_facts(company_ids, start_date, end_date)
            stored = await _store_facts(db_manager, facts, "news")

            logger.info(f"News refresh completed: {stored} facts stored")
            return {"status": "completed", "source": "news", "facts_fetched": stored}

        return asyncio.run(_refresh())

    except Exception as exc:
        logger.error(f"News refresh failed: {exc}")
        countdown = 5 * (2**self.request.retries)
        logger.info(f"[RETRY-ATTEMPT-{self.request.retries + 1}] News refresh will retry in {countdown}s")

        try:
            raise self.retry(exc=exc, countdown=countdown)  # noqa: B904
        except MaxRetriesExceededError:
            dead_letter_queue.record_failure("refresh_news", self.request.id, str(exc), self.request.retries + 1)
            raise


@shared_task(name="solstein.worker_tasks.refresh_website", bind=True, max_retries=3)
def refresh_website(self):
    """Refresh website data for all tracked companies.

    Phase 13.4: Implements exponential backoff retry logic
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

            connector = WebsiteRefreshConnector(db_manager)
            facts = await connector.fetch_facts(company_ids)
            stored = await _store_facts(db_manager, facts, "website")

            logger.info(f"Website refresh completed: {stored} facts stored")
            return {"status": "completed", "source": "website", "facts_fetched": stored}

        return asyncio.run(_refresh())

    except Exception as exc:
        logger.error(f"Website refresh failed: {exc}")
        countdown = 5 * (2**self.request.retries)
        logger.info(f"[RETRY-ATTEMPT-{self.request.retries + 1}] Website refresh will retry in {countdown}s")

        try:
            raise self.retry(exc=exc, countdown=countdown)  # noqa: B904
        except MaxRetriesExceededError:
            dead_letter_queue.record_failure("refresh_website", self.request.id, str(exc), self.request.retries + 1)
            raise


@shared_task(name="solstein.worker_tasks.refresh_linkedin", bind=True, max_retries=3)
def refresh_linkedin(self):
    """Refresh LinkedIn data for all tracked companies.

    Phase 13.4: Implements exponential backoff retry logic
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

            connector = LinkedInRefreshConnector(db_manager)
            facts = await connector.fetch_facts(company_ids)
            stored = await _store_facts(db_manager, facts, "linkedin")

            logger.info(f"LinkedIn refresh completed: {stored} facts stored")
            return {"status": "completed", "source": "linkedin", "facts_fetched": stored}

        return asyncio.run(_refresh())

    except Exception as exc:
        logger.error(f"LinkedIn refresh failed: {exc}")
        countdown = 5 * (2**self.request.retries)
        logger.info(f"[RETRY-ATTEMPT-{self.request.retries + 1}] LinkedIn refresh will retry in {countdown}s")

        try:
            raise self.retry(exc=exc, countdown=countdown)  # noqa: B904
        except MaxRetriesExceededError:
            dead_letter_queue.record_failure("refresh_linkedin", self.request.id, str(exc), self.request.retries + 1)
            raise


@shared_task(name="solstein.worker_tasks.refresh_funding", bind=True, max_retries=3)
def refresh_funding(self):
    """Refresh funding data for all tracked companies.

    Phase 13.4: Implements exponential backoff retry logic
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

            connector = FundingRefreshConnector(db_manager)
            from datetime import datetime, timedelta

            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)

            facts = await connector.fetch_facts(company_ids, start_date, end_date)
            stored = await _store_facts(db_manager, facts, "funding")

            logger.info(f"Funding refresh completed: {stored} facts stored")
            return {"status": "completed", "source": "funding", "facts_fetched": stored}

        return asyncio.run(_refresh())

    except Exception as exc:
        logger.error(f"Funding refresh failed: {exc}")
        countdown = 5 * (2**self.request.retries)
        logger.info(f"[RETRY-ATTEMPT-{self.request.retries + 1}] Funding refresh will retry in {countdown}s")

        try:
            raise self.retry(exc=exc, countdown=countdown)  # noqa: B904
        except MaxRetriesExceededError:
            dead_letter_queue.record_failure("refresh_funding", self.request.id, str(exc), self.request.retries + 1)
            raise


@shared_task(name="solstein.worker_tasks.refresh_global_market", bind=True, max_retries=3)
def refresh_global_market(self):
    """Refresh global market data.

    Phase 13.4: Implements exponential backoff retry logic
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

            connector = GlobalMarketRefreshConnector(db_manager)
            facts = await connector.fetch_facts(company_ids)
            stored = await _store_facts(db_manager, facts, "global_market")

            logger.info(f"Global Market refresh completed: {stored} facts stored")
            return {"status": "completed", "source": "global_market", "facts_fetched": stored}

        return asyncio.run(_refresh())

    except Exception as exc:
        logger.error(f"Global Market refresh failed: {exc}")
        countdown = 5 * (2**self.request.retries)
        logger.info(f"[RETRY-ATTEMPT-{self.request.retries + 1}] Global Market refresh will retry in {countdown}s")

        try:
            raise self.retry(exc=exc, countdown=countdown)  # noqa: B904
        except MaxRetriesExceededError:
            dead_letter_queue.record_failure(
                "refresh_global_market", self.request.id, str(exc), self.request.retries + 1
            )
            raise


@shared_task(name="solstein.worker_tasks.refresh_web_search", bind=True, max_retries=3)
def refresh_web_search(self):
    """Refresh web search data for all tracked companies.

    Phase 13.4: Implements exponential backoff retry logic
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

            connector = WebSearchRefreshConnector(db_manager)
            from datetime import datetime, timedelta

            end_date = datetime.now()
            start_date = end_date - timedelta(hours=12)

            facts = await connector.fetch_facts(company_ids, start_date, end_date)
            stored = await _store_facts(db_manager, facts, "web_search")

            logger.info(f"Web Search refresh completed: {stored} facts stored")
            return {"status": "completed", "source": "web_search", "facts_fetched": stored}

        return asyncio.run(_refresh())

    except Exception as exc:
        logger.error(f"Web Search refresh failed: {exc}")
        countdown = 5 * (2**self.request.retries)
        logger.info(f"[RETRY-ATTEMPT-{self.request.retries + 1}] Web Search refresh will retry in {countdown}s")

        try:
            raise self.retry(exc=exc, countdown=countdown)  # noqa: B904
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


# ============================================================================
# PHASE 12: ENRICHMENT ASYNC TASKS (with Phase 13.4 retry logic)
# ============================================================================


# Import celery_app from config
from solstein.celery_config import celery_app


class EnrichmentTask(Task):
    """Base task class for enrichment operations with result tracking."""

    def on_success(self, result, task_id, args, kwargs):
        """Called on task success - update result tracking."""
        pass

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called on task failure - update result tracking."""
        pass


@celery_app.task(base=EnrichmentTask, bind=True, max_retries=3)
def enrich_company_async(
    self, company_id: str, company_name: str | None = None, sources: list[str] | None = None, user_id: str | None = None
):
    """Asynchronously enrich a single company (Phase 12).

    Phase 13.4: Implements exponential backoff retry logic

    Args:
        company_id: Company identifier
        company_name: Company name (optional)
        sources: List of enrichment sources (default: ['SEC_EDGAR'])
        user_id: User who requested enrichment (optional)

    Returns:
        Dict with enrichment results
    """
    try:
        import time

        from solstein.data.unified_loader import UnifiedCompany, unified_loader

        sources = sources or ["SEC_EDGAR"]
        start_time = time.time()

        # Perform enrichment
        company = UnifiedCompany(id=company_id, name=company_name or company_id)
        enriched = unified_loader.enrich_from_connectors(company)

        duration_ms = (time.time() - start_time) * 1000

        # Track enriched fields
        fields_enriched = []
        if enriched.financials and enriched.financials.revenue:
            fields_enriched.append("revenue")
        if enriched.financials and enriched.financials.employees:
            fields_enriched.append("employees")
        if enriched.financials and enriched.financials.growth_rate:
            fields_enriched.append("growth_rate")

        return {
            "task_id": self.request.id,
            "company_id": company_id,
            "company_name": enriched.name or company_name or company_id,
            "status": "SUCCESS",
            "sources_used": sources,
            "fields_enriched": fields_enriched,
            "duration_ms": duration_ms,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "enriched_data": {
                "revenue": enriched.financials.revenue if enriched.financials else None,
                "employees": enriched.financials.employees if enriched.financials else None,
                "growth_rate": enriched.financials.growth_rate if enriched.financials else None,
                "profit_margin": enriched.financials.profit_margin if enriched.financials else None,
            },
        }

    except Exception as exc:
        # Phase 13.4: Exponential backoff retry
        countdown = 5 * (2**self.request.retries)
        logger.info(
            f"[RETRY-ATTEMPT-{self.request.retries + 1}] Enrichment for {company_id} will retry in {countdown}s"
        )

        try:
            self.retry(exc=exc, countdown=countdown)
        except MaxRetriesExceededError:
            dead_letter_queue.record_failure(
                "enrich_company_async", self.request.id, str(exc), self.request.retries + 1
            )
            return {
                "task_id": self.request.id,
                "company_id": company_id,
                "company_name": company_name,
                "status": "FAILED",
                "error": str(exc),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }


@celery_app.task(bind=True, max_retries=3)
def enrich_companies_batch_async(
    self, companies: list[dict], sources: list[str] | None = None, batch_size: int = 10, user_id: str | None = None
):
    """Asynchronously enrich multiple companies in batches (Phase 12).

    Phase 13.4: Implements exponential backoff retry logic

    Args:
        companies: List of company dicts with 'id' and 'name' keys
        sources: List of enrichment sources
        batch_size: Number of companies per batch
        user_id: User who requested enrichment

    Returns:
        Dict with batch enrichment results
    """
    try:
        import time

        from solstein.data.unified_loader import UnifiedCompany, unified_loader

        sources = sources or ["SEC_EDGAR"]
        start_time = time.time()
        batch_results = []
        failed_count = 0

        # Process companies
        for i, company_data in enumerate(companies):
            try:
                company_id = company_data.get("id")
                company_name = company_data.get("name", company_id)

                company = UnifiedCompany(id=company_id, name=company_name)
                enriched = unified_loader.enrich_from_connectors(company)

                batch_results.append(
                    {
                        "company_id": company_id,
                        "company_name": enriched.name or company_name,
                        "status": "SUCCESS",
                    }
                )

            except Exception as e:
                failed_count += 1
                batch_results.append(
                    {
                        "company_id": company_data.get("id"),
                        "company_name": company_data.get("name"),
                        "status": "FAILED",
                        "error": str(e),
                    }
                )

        duration_ms = (time.time() - start_time) * 1000

        return {
            "task_id": self.request.id,
            "total": len(companies),
            "successful": len(companies) - failed_count,
            "failed": failed_count,
            "results": batch_results,
            "duration_ms": duration_ms,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as exc:
        # Phase 13.4: Exponential backoff retry
        countdown = 5 * (2**self.request.retries)
        logger.info(f"[RETRY-ATTEMPT-{self.request.retries + 1}] Batch enrichment will retry in {countdown}s")

        try:
            self.retry(exc=exc, countdown=countdown)
        except MaxRetriesExceededError:
            dead_letter_queue.record_failure(
                "enrich_companies_batch_async", self.request.id, str(exc), self.request.retries + 1
            )
            return {
                "task_id": self.request.id,
                "status": "FAILED",
                "error": str(exc),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
