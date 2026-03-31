import asyncio
from collections.abc import Iterable
from typing import Any

from loguru import logger

from ..config import get_settings
from ..core.repositories import CompanyFilter
from ..data.repositories import JsonFileRepository, SupabaseRepository
from ..domain.models import Company
from .scoring import GrowthScorer


async def _get_repo() -> Any:
    settings = get_settings()
    use_supabase = bool(getattr(settings, "supabase", None) and settings.supabase.url)
    if use_supabase:
        try:
            return SupabaseRepository()
        except Exception as exc:
            logger.warning("Supabase repository init failed", error=str(exc))
    return JsonFileRepository()


async def _maybe_await(value: Any) -> Any:
    if asyncio.iscoroutine(value):
        return await value
    return value


async def calculate_company_score(company_id: str) -> dict[str, Any]:
    repo = await _get_repo()
    company = await _maybe_await(repo.get_by_id(company_id))
    if company is None:
        raise ValueError(f"Company {company_id} not found in database")

    scorer = GrowthScorer()
    scored = scorer.calculate_scores(company)

    if hasattr(repo, "save"):
        await _maybe_await(repo.save(scored))

    return {
        "company_id": scored.id,
        "classification": scored.classification,
        "growth_score": scored.growth_score,
    }


async def fetch_market_company_ids(filters: dict[str, Any]) -> list[str]:
    repo = await _get_repo()
    company_filter = CompanyFilter(**filters)
    companies: Iterable[Company] = await _maybe_await(repo.get_all(filters=company_filter))
    return [company.id for company in companies if getattr(company, "id", None) is not None]
