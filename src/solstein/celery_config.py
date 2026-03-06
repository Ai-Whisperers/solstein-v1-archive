"""Celery configuration and tasks for Solstein data refresh.

This module provides Celery-based scheduling for automated data refresh
of all 12 data sources:
- SEC EDGAR (financial filings) - daily
- Companies House (UK/EU company data) - daily
- News Signals (funding, partnerships, key hires) - hourly
- GitHub (repository metrics) - every 6 hours
- Yahoo Finance (market data) - every 6 hours
- Patents (patent filings) - daily
- News (general news) - every 2 hours
- Website (company website data) - daily
- LinkedIn (professional profiles) - every 12 hours
- Funding (funding rounds) - every 6 hours
- Global Market (market trends) - every 6 hours
- Web Search (search results) - every 6 hours
"""

from celery import Celery
from celery.schedules import crontab

from solstein.config import get_settings

settings = get_settings()

celery_app = Celery(
    "solstein",
    broker=settings.celery_broker_url or "redis://localhost:6379/0",
    backend=settings.celery_result_backend or "redis://localhost:6379/1",
    include=[
        "solstein.worker_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    # Phase 13.4: Timeout configuration for single vs batch tasks
    task_time_limit=30,  # 30 seconds hard limit for single tasks
    task_soft_time_limit=25,  # 25 seconds soft limit for graceful shutdown
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
)

# Beat schedule for automated data refresh
# All 12 sources with appropriate frequencies based on data freshness requirements
celery_app.conf.beat_schedule = {
    # ============================================================================
    # ORIGINAL 4 SOURCES
    # ============================================================================
    "refresh-sec-edgar-daily": {
        "task": "solstein.worker_tasks.refresh_sec_edgar",
        "schedule": crontab(hour=9, minute=0),
        "options": {"queue": "default"},
    },
    "refresh-companies-house-daily": {
        "task": "solstein.worker_tasks.refresh_companies_house",
        "schedule": crontab(hour=9, minute=30),
        "options": {"queue": "default"},
    },
    "refresh-news-signals-hourly": {
        "task": "solstein.worker_tasks.refresh_news_signals",
        "schedule": crontab(minute=0),  # Every hour
        "options": {"queue": "default"},
    },
    "refresh-github-every-6-hours": {
        "task": "solstein.worker_tasks.refresh_github",
        "schedule": crontab(hour="*/6"),  # Every 6 hours
        "options": {"queue": "default"},
    },
    # ============================================================================
    # NEW 8 SOURCES (Wave 2 Refresh Connectors)
    # ============================================================================
    "refresh-yahoo-finance-every-6-hours": {
        "task": "solstein.worker_tasks.refresh_yahoo_finance",
        "schedule": crontab(hour="*/6", minute=15),  # Every 6 hours, offset by 15 min
        "options": {"queue": "default"},
    },
    "refresh-patents-daily": {
        "task": "solstein.worker_tasks.refresh_patents",
        "schedule": crontab(hour=10, minute=0),  # Daily at 10 AM
        "options": {"queue": "default"},
    },
    "refresh-news-every-2-hours": {
        "task": "solstein.worker_tasks.refresh_news",
        "schedule": crontab(hour="*/2", minute=30),  # Every 2 hours
        "options": {"queue": "default"},
    },
    "refresh-website-daily": {
        "task": "solstein.worker_tasks.refresh_website",
        "schedule": crontab(hour=11, minute=0),  # Daily at 11 AM
        "options": {"queue": "default"},
    },
    "refresh-linkedin-every-12-hours": {
        "task": "solstein.worker_tasks.refresh_linkedin",
        "schedule": crontab(hour="*/12", minute=0),  # Every 12 hours
        "options": {"queue": "default"},
    },
    "refresh-funding-every-6-hours": {
        "task": "solstein.worker_tasks.refresh_funding",
        "schedule": crontab(hour="*/6", minute=45),  # Every 6 hours, offset by 45 min
        "options": {"queue": "default"},
    },
    "refresh-global-market-every-6-hours": {
        "task": "solstein.worker_tasks.refresh_global_market",
        "schedule": crontab(hour="*/6", minute=30),  # Every 6 hours, offset by 30 min
        "options": {"queue": "default"},
    },
    "refresh-web-search-every-6-hours": {
        "task": "solstein.worker_tasks.refresh_web_search",
        "schedule": crontab(hour="*/6", minute=0),  # Every 6 hours
        "options": {"queue": "default"},
    },
    # ============================================================================
    # FULL REFRESH (All sources) - Weekly on Sunday at 2 AM
    # ============================================================================
    "refresh-all-sources-weekly": {
        "task": "solstein.worker_tasks.refresh_all_sources",
        "schedule": crontab(day_of_week=0, hour=2, minute=0),  # Sunday 2 AM
        "options": {"queue": "default"},
    },
}

# Override schedules from settings if provided
if settings.refresh_schedule:
    for source, schedule in settings.refresh_schedule.items():
        task_name = f"refresh-{source}"
        celery_app.conf.beat_schedule[task_name] = {
            "task": f"solstein.worker_tasks.refresh_{source}",
            "schedule": schedule,
        }


# Import celery_context to register signal handlers for context propagation
from . import celery_context  # noqa: F401
