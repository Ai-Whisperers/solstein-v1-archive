"""Orchestration tasks for running all refresh operations.

Extracted from worker_tasks.py as part of EPIC-021 file splitting.
Provides tasks for coordinating multiple refresh operations.
"""

from __future__ import annotations

from celery import shared_task
from loguru import logger

from .refresh_tasks import (
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
from .tenant_isolation import validate_task_tenant_id


@shared_task(name="solstein.worker_tasks.refresh_all_sources", bind=True)
def refresh_all_sources(self, tenant_id: str):
    """Refresh all data sources for a given tenant.

    STORY-066: tenant_id is now a required parameter. Each sub-task
    receives the tenant_id for scoped data access.

    Args:
        tenant_id: Tenant identifier (required, validated at entry)
    """
    # STORY-066: Validate tenant_id at orchestrator entry
    validated_tenant = validate_task_tenant_id(tenant_id, task_name="refresh_all_sources")
    logger.info(f"Starting full refresh for all sources (tenant={validated_tenant[:8]}...)")

    results = []

    # Original 4 sources — pass tenant_id to each sub-task
    results.append(refresh_sec_edgar.apply_async(args=[validated_tenant]).id)
    results.append(refresh_companies_house.apply_async(args=[validated_tenant]).id)
    results.append(refresh_news_signals.apply_async(args=[validated_tenant]).id)
    results.append(refresh_github.apply_async(args=[validated_tenant]).id)

    # New 8 sources
    results.append(refresh_yahoo_finance.apply_async(args=[validated_tenant]).id)
    results.append(refresh_patents.apply_async(args=[validated_tenant]).id)
    results.append(refresh_news.apply_async(args=[validated_tenant]).id)
    results.append(refresh_website.apply_async(args=[validated_tenant]).id)
    results.append(refresh_linkedin.apply_async(args=[validated_tenant]).id)
    results.append(refresh_funding.apply_async(args=[validated_tenant]).id)
    results.append(refresh_global_market.apply_async(args=[validated_tenant]).id)
    results.append(refresh_web_search.apply_async(args=[validated_tenant]).id)

    logger.info(f"Queued {len(results)} refresh tasks for tenant {validated_tenant[:8]}...")
    return {
        "status": "queued",
        "tenant_id": validated_tenant,
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
