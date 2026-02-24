"""Celery configuration and tasks for Solstein data refresh.

This module provides Celery-based scheduling for automated data refresh
of all data sources (SEC EDGAR, Companies House, News, GitHub).
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
    task_time_limit=3600,
    task_soft_time_limit=3000,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
)

# Beat schedule for automated data refresh
celery_app.conf.beat_schedule = {
    "refresh-sec-edgar-daily": {
        "task": "solstein.worker_tasks.refresh_sec_edgar",
        "schedule": crontab(hour=9, minute=0),
    },
    "refresh-companies-house-daily": {
        "task": "solstein.worker_tasks.refresh_companies_house",
        "schedule": crontab(hour=9, minute=30),
    },
    "refresh-news-signals-hourly": {
        "task": "solstein.worker_tasks.refresh_news_signals",
        "schedule": crontab(minute=0),
    },
    "refresh-github-every-6-hours": {
        "task": "solstein.worker_tasks.refresh_github",
        "schedule": crontab(hour="*/6"),
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
