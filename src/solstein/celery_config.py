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
        "solstein.worker.export_tasks",  # STORY-111: Async export tasks
    ],
)

# STORY-091: Resolve result TTL — top-level CELERY_RESULT_EXPIRES_SECONDS overrides the
# nested CELERY_TIMING__RESULT_EXPIRES if both are set. Default is 86400s (24 hours).
# Polling contract: callers must read AsyncResult.status within this window.
# After expiry, a PENDING status is returned for completed tasks — this is misleading,
# not a bug. Size the TTL to exceed your longest expected polling delay.
_result_expires: int = (
    settings.celery_result_expires_seconds
    if settings.celery_result_expires_seconds is not None
    else settings.celery_timing.result_expires
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=settings.celery_timing.task_time_limit,
    task_soft_time_limit=settings.celery_timing.task_soft_time_limit,
    # Result TTL — see STORY-091. Default: 86400s (24h). Set via:
    #   CELERY_RESULT_EXPIRES_SECONDS=86400  (top-level alias)
    #   CELERY_TIMING__RESULT_EXPIRES=86400  (nested config)
    # Pollers must read results within this window or accept expiry.
    result_expires=_result_expires,
    # STORY-089: At-least-once delivery semantics.
    #
    # task_acks_late=True — tasks are acknowledged to the broker AFTER execution
    # completes, not on receipt. If a worker is killed between receipt and
    # completion (OOM, SIGKILL, pod eviction), the broker re-queues the task
    # automatically. Without this, a worker crash silently drops the task.
    #
    # task_reject_on_worker_lost=True — when the worker connection is lost (not
    # just an application-level exception), the task is rejected back to the
    # broker (nack'd) rather than acked. This completes the acks_late guarantee:
    # even a hard connection loss triggers re-queue.
    #
    # IMPORTANT: acks_late creates at-least-once semantics. Tasks MAY execute
    # more than once (e.g. on Beat scheduler restart or worker eviction mid-task).
    # All 12 Beat-scheduled tasks are guarded by the Redis deduplication lock in
    # solstein.worker.idempotency — see STORY-090. Deploy these two stories together.
    #
    # worker_prefetch_multiplier=1 is required for acks_late correctness. With
    # higher prefetch a worker holds multiple unacked tasks in memory; a crash
    # then requeues all prefetched tasks, increasing duplicate risk. With prefetch=1
    # only one task is in-flight per worker process at a time.
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    # STORY-093: Enable task events so Flower (STORY-095) can monitor
    # real-time task state, success/failure rates, and queue depths.
    # This adds minimal overhead (~1 Redis message per task state change).
    worker_send_task_events=True,
    task_send_sent_event=True,
    # STORY-111: Route export tasks to dedicated queue with higher time limits.
    # Default exports: 60 s soft / 90 s hard.
    # LLM exports override per-task via task_time_limit annotation.
    task_routes={
        "solstein.worker_tasks.generate_export": {"queue": "export"},
    },
)

# STORY-111: Per-task time limit overrides for LLM exports (120 s)
celery_app.conf.task_annotations = {
    "solstein.worker_tasks.generate_export": {
        "time_limit": 150,
        "soft_time_limit": 120,
    },
}

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
