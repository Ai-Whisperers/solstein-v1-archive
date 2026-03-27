"""Canonical Celery task registry for all data refresh and enrichment operations.

STORY-092 (capstone of EPIC-025): This module is the single authoritative import
surface for all Celery tasks. worker_tasks_v2.py has been removed; all task
definitions live in solstein.worker submodules re-exported here.

All 12 Beat-scheduled refresh tasks
------------------------------------
Task name                                       Queue     Schedule
----------------------------------------------------------------------
solstein.worker_tasks.refresh_sec_edgar         default   Daily   09:00
solstein.worker_tasks.refresh_companies_house   default   Daily   09:30
solstein.worker_tasks.refresh_news_signals      default   Hourly  :00
solstein.worker_tasks.refresh_github            default   Every 6h
solstein.worker_tasks.refresh_yahoo_finance     default   Every 6h  (+15m)
solstein.worker_tasks.refresh_patents           default   Daily   10:00
solstein.worker_tasks.refresh_news              default   Every 2h  (+30m)
solstein.worker_tasks.refresh_website           default   Daily   11:00
solstein.worker_tasks.refresh_linkedin          default   Every 12h
solstein.worker_tasks.refresh_funding           default   Every 6h  (+45m)
solstein.worker_tasks.refresh_global_market     default   Every 6h  (+30m)
solstein.worker_tasks.refresh_web_search        default   Every 6h  :00
solstein.worker_tasks.refresh_all_sources       default   Weekly  Sun 02:00

(Schedules are authoritative in celery_config.py beat_schedule; this table
is a human-readable summary for onboarding and code-review purposes.)

Reliability guarantees per task (EPIC-025)
------------------------------------------
- STORY-088: On MaxRetriesExceededError the failure is persisted to PostgreSQL
  DLQ via solstein.worker.dlq.persist_failed_task (not lost in memory).
- STORY-089: task_acks_late=True + task_reject_on_worker_lost=True in
  celery_config.py — tasks are re-queued on worker crash (at-least-once).
- STORY-090: Each task is wrapped with a Redis dedup lock keyed to the full
  task name + 1-hour period bucket.  Duplicate invocations within the same
  period are skipped with a WARNING log (not an error). Fail-open on Redis
  unavailability.

Retry strategy (Phase 13.4)
----------------------------
- Exponential backoff: 5 s, 10 s, 20 s for retries 1, 2, 3
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

# Tenant isolation (STORY-066)
from solstein.worker.tenant_isolation import (
    TenantIsolationError,
    require_tenant_id,
    task_tenant_context,
    validate_task_tenant_id,
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
    # Tenant isolation (STORY-066)
    "TenantIsolationError",
    "validate_task_tenant_id",
    "task_tenant_context",
    "require_tenant_id",
]
