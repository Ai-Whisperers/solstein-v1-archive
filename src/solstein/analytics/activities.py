"""
Temporal Activities for Solstein Intelligence Engine.

NOTE: Temporal integration currently disabled (temporalio dependency removed).
Activities kept for reference but are not called. Will be reimplemented with
asyncio-based task queue in Phase 2.
"""

import asyncio
from typing import Any

from loguru import logger

# from temporalio import activity
from ..config import get_settings
from ..core.repositories import CompanyFilter, CompanyRepository
from ..data.repositories import JsonFileRepository, SupabaseRepository
from .scoring import GrowthScorer, classify_company


def _get_repo() -> CompanyRepository:
    """Helper to get repo with fallback logic."""
    settings = get_settings()
    if not settings.supabase.url or "your-project" in settings.supabase.url:
        return JsonFileRepository()
    try:
        return SupabaseRepository()
    except Exception:
        return JsonFileRepository()


async def calculate_company_score(company_id: str) -> dict[str, Any]:
    """Calculate scores for a single company."""
    logger.info(f"Activity starting: calculate_company_score for {company_id}")

    # 1. Fetch from Repository
    repo = _get_repo()
    company = await asyncio.to_thread(repo.get_by_id, company_id)
    if not company:
        raise ValueError(f"Company {company_id} not found in database.")

    # 2. Score
    scorer = GrowthScorer()
    scored = scorer.calculate_scores(company)

    # 3. Classify
    classification = classify_company(scored.growth_score)
    scored.classification = classification

    # 4. Save back to Supabase
    await asyncio.to_thread(repo.save, scored)

    return {
        "company_id": company.id,
        "classification": classification,
        "growth_score": scored.growth_score,
    }


async def fetch_market_company_ids(filters: dict[str, Any]) -> list[str]:
    """Fetch all company IDs matching a filter for batch scoring."""
    repo = _get_repo()
    companies = await asyncio.to_thread(repo.get_all, filters=CompanyFilter(**filters))
    return [c.id for c in companies if c.id]
