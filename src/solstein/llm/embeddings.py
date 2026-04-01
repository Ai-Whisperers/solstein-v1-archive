"""Embedding generation for company profiles (EPIC-023 STORY-081).

Generates vector embeddings from company profile text using OpenAI's
embedding API. Embeddings are used for semantic similarity search via pgvector.

Design decisions:
- Uses OpenAI text-embedding-3-small (1536 dims) by default.
- Profile text is serialized as a structured brief, not raw field concatenation.
- Graceful degradation: if embedding fails, returns None (never crashes pipeline).
- Configurable model and dimensions via Settings.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import TYPE_CHECKING

import httpx
from loguru import logger

if TYPE_CHECKING:
    from solstein.config import Settings
    from solstein.domain.models import Company


def company_to_profile_text(company: Company) -> str:
    """Serialize a company profile into natural-language text for embedding.

    The text should read like a brief company description — the kind of
    paragraph a human would write to describe the company to a colleague.
    Naive field concatenation produces poor embeddings; structured prose
    captures semantic relationships between attributes.

    Args:
        company: Domain Company object with enriched data.

    Returns:
        A natural-language company profile string.
    """
    parts: list[str] = []

    # Identity
    parts.append(f"{company.name} is a company in the {company.industry} industry.")

    if company.description:
        parts.append(company.description)

    if company.headquarters:
        parts.append(f"Headquartered in {company.headquarters}.")

    if company.founded_year:
        parts.append(f"Founded in {company.founded_year}.")

    # Classification and positioning
    if company.classification:
        parts.append(f"Classified as {company.classification}.")

    if company.tier:
        tier_val = company.tier.value if hasattr(company.tier, "value") else str(company.tier)
        parts.append(f"Market tier: {tier_val}.")

    # Financial profile
    financials: list[str] = []
    # Domain model uses 'revenue', DB model uses 'revenue_eur_m'
    revenue = getattr(company, "revenue", None) or getattr(company, "revenue_eur_m", None)
    if revenue is not None:
        financials.append(f"revenue of EUR {revenue}M")
    growth = getattr(company, "growth_rate", None) or getattr(company, "growth_rate_pct", None)
    if growth is not None:
        financials.append(f"growth rate of {growth}%")
    employees = getattr(company, "employee_count", None)
    if employees is not None:
        financials.append(f"{employees} employees")
    if financials:
        parts.append("Financial profile: " + ", ".join(financials) + ".")

    # AI and technology
    ai_score = getattr(company, "ai_score", None)
    if ai_score is not None:
        parts.append(f"AI readiness score: {ai_score}.")
    ai_maturity = getattr(company, "ai_maturity", None)
    if ai_maturity is not None:
        parts.append(f"AI maturity: {ai_maturity}.")

    # Scores
    composite = getattr(company, "composite_score", None)
    if composite is not None:
        parts.append(f"Composite score: {composite}.")

    return " ".join(parts)


async def generate_embedding(
    text: str,
    settings: Settings,
) -> list[float] | None:
    """Generate an embedding vector for the given text.

    Uses OpenAI's embedding API via httpx (async). Falls back to None
    on any failure — embedding generation must never crash the pipeline.

    Args:
        text: The text to embed.
        settings: Application settings (contains API key, model, dimensions).

    Returns:
        A list of floats (the embedding vector) or None on failure.
    """
    if not settings.openai_api_key:
        logger.warning("[Embedding] No OpenAI API key configured — skipping embedding generation")
        return None

    if not text.strip():
        logger.warning("[Embedding] Empty text provided — skipping embedding generation")
        return None

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/embeddings",
                headers={
                    "Authorization": f"Bearer {settings.openai_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.embedding_model,
                    "input": text,
                    "dimensions": settings.embedding_dimensions,
                },
            )
            response.raise_for_status()
            data = response.json()
            embedding = data["data"][0]["embedding"]
            logger.debug(
                f"[Embedding] Generated {len(embedding)}-dim embedding "
                f"using {settings.embedding_model}, "
                f"tokens: {data.get('usage', {}).get('total_tokens', 'unknown')}"
            )
            return embedding
    except httpx.HTTPStatusError as e:
        logger.error(f"[Embedding] HTTP error from OpenAI API: {e.response.status_code}: {e}")
        return None
    except httpx.RequestError as e:
        logger.error(f"[Embedding] Request failed (network/timeout): {type(e).__name__}: {e}")
        return None
    except (KeyError, IndexError, TypeError) as e:
        logger.error(f"[Embedding] Malformed API response: {type(e).__name__}: {e}")
        return None


async def generate_company_embedding(
    company: Company,
    settings: Settings,
) -> tuple[list[float] | None, str]:
    """Generate an embedding for a company profile.

    Args:
        company: Domain Company object.
        settings: Application settings.

    Returns:
        Tuple of (embedding_vector_or_None, profile_text_used).
    """
    profile_text = company_to_profile_text(company)
    embedding = await generate_embedding(profile_text, settings)
    return embedding, profile_text


async def batch_generate_embeddings(
    companies: list[Company],
    settings: Settings,
    batch_size: int | None = None,
) -> list[tuple[str, list[float] | None]]:
    """Generate embeddings for a batch of companies with rate limiting.

    Args:
        companies: List of Company domain objects.
        settings: Application settings.
        batch_size: Override for settings.embedding_batch_size.

    Returns:
        List of (company_name, embedding_or_None) tuples.
    """
    effective_batch_size = batch_size or settings.embedding_batch_size
    results: list[tuple[str, list[float] | None]] = []

    for i in range(0, len(companies), effective_batch_size):
        batch = companies[i : i + effective_batch_size]
        batch_results = await asyncio.gather(
            *[generate_company_embedding(c, settings) for c in batch],
            return_exceptions=True,
        )

        for company, result in zip(batch, batch_results):
            if isinstance(result, Exception):
                logger.error(
                    f"[Embedding] Batch embedding failed for {company.name}: "
                    f"{type(result).__name__}: {result}"
                )
                results.append((company.name, None))
            else:
                embedding, _ = result
                results.append((company.name, embedding))

        # Brief pause between batches to respect rate limits
        if i + effective_batch_size < len(companies):
            await asyncio.sleep(0.5)

    succeeded = sum(1 for _, emb in results if emb is not None)
    logger.info(
        f"[Embedding] Batch complete: {succeeded}/{len(results)} embeddings generated"
    )
    return results


def get_embedding_metadata(settings: Settings) -> dict[str, str | datetime]:
    """Return metadata dict for embedding records.

    Args:
        settings: Application settings.

    Returns:
        Dict with embedding_model and embedding_updated_at.
    """
    return {
        "embedding_model": settings.embedding_model,
        "embedding_updated_at": datetime.now(timezone.utc),
    }
