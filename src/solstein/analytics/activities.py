"""
Temporal Activities for Solstein Intelligence Engine.
These represent the atomic, side-effect-heavy tasks orchestratd by Temporal.
"""

from typing import Any
from temporalio import activity
from loguru import logger

from ..data.repositories import SupabaseRepository
from ..core.repositories import CompanyFilter
from .scoring import GrowthScorer

@activity.defn
async def calculate_company_score(company_id: str) -> dict[str, Any]:
    """Calculate scores for a single company."""
    logger.info(f"Activity starting: calculate_company_score for {company_id}")
    
    # 1. Fetch from Supabase
    repo = SupabaseRepository()
    company = repo.get_by_id(company_id)
    if not company:
        raise ValueError(f"Company {company_id} not found in database.")

    # 2. Score
    scorer = GrowthScorer()
    scored = scorer.calculate_scores(company)
    
    # 3. Classify
    growth = scored.growth_score or 0.0
    classification = "Neutral"
    if growth >= 7.0:
        classification = "Rocket"
    elif growth <= 4.0:
        classification = "Dinosaur"

    scored.classification = classification
    
    # 4. Save back to Supabase
    repo.save(scored)
    
    return {
        "company_id": company.id,
        "classification": classification,
        "growth_score": growth
    }

@activity.defn
async def fetch_market_company_ids(filters: dict[str, Any]) -> list[str]:
    """Fetch all company IDs matching a filter for batch scoring."""
    repo = SupabaseRepository()
    companies = repo.get_all(filters=CompanyFilter(**filters))
    return [c.id for c in companies if c.id]
