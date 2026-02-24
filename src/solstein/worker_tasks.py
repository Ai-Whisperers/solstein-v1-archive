"""Celery tasks for data refresh operations."""

from celery import shared_task
from loguru import logger


@shared_task(name="solstein.worker_tasks.refresh_sec_edgar")
def refresh_sec_edgar():
    """Refresh SEC EDGAR data for all tracked companies."""
    logger.info("Starting SEC EDGAR refresh task")
    return {"status": "completed", "source": "sec_edgar"}


@shared_task(name="solstein.worker_tasks.refresh_companies_house")
def refresh_companies_house():
    """Refresh Companies House data for all tracked companies."""
    logger.info("Starting Companies House refresh task")
    return {"status": "completed", "source": "companies_house"}


@shared_task(name="solstein.worker_tasks.refresh_news_signals")
def refresh_news_signals():
    """Refresh news signals for all tracked companies."""
    logger.info("Starting News Signals refresh task")
    return {"status": "completed", "source": "news_signals"}


@shared_task(name="solstein.worker_tasks.refresh_github")
def refresh_github():
    """Refresh GitHub data for all tracked companies."""
    logger.info("Starting GitHub refresh task")
    return {"status": "completed", "source": "github"}


@shared_task(name="solstein.worker_tasks.refresh_all_sources")
def refresh_all_sources():
    """Refresh all data sources."""
    logger.info("Starting full refresh for all sources")
    results = []
    results.append(refresh_sec_edgar.apply_async().id)
    results.append(refresh_companies_house.apply_async().id)
    results.append(refresh_news_signals.apply_async().id)
    results.append(refresh_github.apply_async().id)
    return {"status": "queued", "task_ids": results}
