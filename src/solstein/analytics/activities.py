"""
Temporal Activities for Solstein Intelligence Engine.
These represent the atomic, side-effect-heavy tasks orchestratd by Temporal.
"""

import asyncio
from typing import Any
from temporalio import activity
from loguru import logger

from ..data.repositories import SupabaseRepository
from ..core.repositories import CompanyFilter
from .scoring import GrowthScorer, classify_company

@activity.defn
async def calculate_company_score(company_id: str) -> dict[str, Any]:
    """Calculate scores for a single company."""
    logger.info(f"Activity starting: calculate_company_score for {company_id}")
    
    # 1. Fetch from Supabase
    repo = SupabaseRepository()
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
        "growth_score": growth
    }

@activity.defn
async def fetch_market_company_ids(filters: dict[str, Any]) -> list[str]:
    """Fetch all company IDs matching a filter for batch scoring."""
    repo = SupabaseRepository()
    companies = await asyncio.to_thread(repo.get_all, filters=CompanyFilter(**filters))
    return [c.id for c in companies if c.id]
