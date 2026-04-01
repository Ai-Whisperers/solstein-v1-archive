"""Semantic similarity search service (STORY-082).

Orchestrates the semantic search workflow:
1. Accept text query or company_id reference.
2. Generate or retrieve the query embedding vector.
3. Query the embedding repository for similar companies.
4. Return typed results with similarity scores.

Design decisions:
- Service layer owns the orchestration; repository owns the SQL.
- Text queries hit the OpenAI embedding API; company_id queries reuse stored vectors.
- All results are tenant-scoped via the repository layer.
- Never crashes on embedding failure — returns structured error result.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

from solstein.api.schemas.semantic_search import (
    SemanticSearchRequest,
    SemanticSearchResponse,
    SemanticSearchResultItem,
)
from solstein.infrastructure.embedding_repository import SimilaritySearchParams

if TYPE_CHECKING:
    from solstein.config import Settings
    from solstein.infrastructure.embedding_repository import EmbeddingRepository


class SemanticSearchError(Exception):
    """Raised when semantic search cannot proceed.

    Attributes:
        code: Machine-readable error code.
        message: Human-readable description.
    """

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


async def execute_semantic_search(
    request: SemanticSearchRequest,
    embedding_repo: EmbeddingRepository,
    settings: Settings,
    tenant_id: str,
) -> SemanticSearchResponse:
    """Execute a semantic similarity search.

    Args:
        request: Validated search request with query or company_id.
        embedding_repo: Repository for vector operations.
        settings: Application settings (embedding model config).
        tenant_id: Authenticated tenant ID for data scoping.

    Returns:
        SemanticSearchResponse with ranked results.

    Raises:
        SemanticSearchError: If the search cannot be executed (e.g., missing
            embedding, invalid company_id, no API key for text queries).
    """
    # Validate that exactly one of query or company_id is provided
    if request.query and request.company_id:
        raise SemanticSearchError(
            code="INVALID_REQUEST",
            message="Provide either 'query' or 'company_id', not both.",
        )
    if not request.query and not request.company_id:
        raise SemanticSearchError(
            code="INVALID_REQUEST",
            message="Provide either 'query' (text) or 'company_id' (reference company).",
        )

    query_vector: list[float]
    query_type: str
    exclude_company_id: str | None = None

    if request.company_id:
        query_type = "company_id"
        query_vector, exclude_company_id = await _resolve_company_vector(
            request.company_id, embedding_repo
        )
    else:
        query_type = "text"
        query_vector = await _resolve_text_vector(request.query, settings)

    search_params = SimilaritySearchParams(
        limit=request.limit,
        offset=request.offset,
        tenant_id=tenant_id,
        min_similarity=request.min_similarity,
        exclude_company_id=exclude_company_id,
    )
    results, total_count = await embedding_repo.find_similar_by_vector(
        query_vector=query_vector,
        search_params=search_params,
    )

    items = [
        _record_to_result_item(record, similarity)
        for record, similarity in results
    ]

    return SemanticSearchResponse(
        items=items,
        total=total_count,
        limit=request.limit,
        offset=request.offset,
        has_next=(request.offset + request.limit) < total_count,
        query_type=query_type,
    )


async def _resolve_company_vector(
    company_id: str,
    embedding_repo: EmbeddingRepository,
) -> tuple[list[float], str]:
    """Retrieve the embedding vector for a reference company.

    Args:
        company_id: The reference company's ID.
        embedding_repo: Repository for embedding lookups.

    Returns:
        Tuple of (query_vector, company_id_to_exclude).

    Raises:
        SemanticSearchError: If the company is not found or has no embedding.
    """
    embedding = await embedding_repo.get_embedding_by_company_id(company_id)
    if embedding is None:
        logger.warning(
            f"[SemanticSearch] Company {company_id} not found or has no embedding"
        )
        raise SemanticSearchError(
            code="EMBEDDING_NOT_FOUND",
            message=(
                f"Company '{company_id}' was not found or does not have an embedding. "
                "Embeddings are generated during the research pipeline."
            ),
        )
    return embedding, company_id


async def _resolve_text_vector(
    query_text: str | None,
    settings: Settings,
) -> list[float]:
    """Generate an embedding vector for a text query.

    Args:
        query_text: The text to embed.
        settings: Application settings with OpenAI API key.

    Returns:
        The embedding vector.

    Raises:
        SemanticSearchError: If embedding generation fails.
    """
    if not query_text:
        raise SemanticSearchError(
            code="INVALID_REQUEST",
            message="Query text must not be empty.",
        )

    from solstein.llm.embeddings import generate_embedding

    embedding = await generate_embedding(query_text, settings)
    if embedding is None:
        logger.error("[SemanticSearch] Failed to generate embedding for text query")
        raise SemanticSearchError(
            code="EMBEDDING_GENERATION_FAILED",
            message=(
                "Failed to generate embedding for the query. "
                "Check that the OpenAI API key is configured and valid."
            ),
        )
    return embedding


def _record_to_result_item(
    record: object,
    similarity: float,
) -> SemanticSearchResultItem:
    """Convert a CompanyRecord + similarity score to a response item.

    Args:
        record: CompanyRecord ORM object.
        similarity: Cosine similarity score (0.0-1.0).

    Returns:
        SemanticSearchResultItem with company details and similarity.
    """
    tier_val = getattr(record, "tier", None)
    if tier_val is not None and hasattr(tier_val, "value"):
        tier_val = tier_val.value

    return SemanticSearchResultItem(
        company_id=record.company_id,
        name=record.name,
        industry=getattr(record, "industry", None),
        description=getattr(record, "description", None),
        similarity_score=round(max(0.0, min(1.0, similarity)), 4),
        classification=getattr(record, "classification", None),
        tier=str(tier_val) if tier_val is not None else None,
        revenue_eur_m=getattr(record, "revenue_eur_m", None),
        employee_count=getattr(record, "employee_count", None),
        composite_score=getattr(record, "composite_score", None),
        has_embedding=getattr(record, "profile_embedding", None) is not None,
    )
