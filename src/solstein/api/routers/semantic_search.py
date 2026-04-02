"""Semantic similarity search API endpoint (STORY-082, EPIC-023).

Provides POST /api/v1/companies/search/semantic for finding companies
by semantic similarity using pgvector embeddings.

Two search modes:
- Text query: embed the query text and find similar companies.
- Company reference: use an existing company's embedding as the query vector.

All results are tenant-scoped via RLS from EPIC-019.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, status
from loguru import logger

from ...application.services.semantic_search_service import (
    SemanticSearchError,
    execute_semantic_search,
)
from ...config import Settings, get_settings
from ...infrastructure.embedding_repository import EmbeddingRepository
from ..dependencies import get_current_tenant, get_db_session
from ..exceptions import APIError
from ..schemas.semantic_search import SemanticSearchRequest, SemanticSearchResponse

router = APIRouter(tags=["Semantic Search"])


@router.post(
    "/companies/search/semantic",
    response_model=SemanticSearchResponse,
    summary="Semantic similarity search for companies",
    description=(
        "Search for companies by semantic similarity. Provide either a free-text "
        "query or a reference company_id. Results are ranked by cosine similarity "
        "and scoped to the authenticated tenant."
    ),
    responses={
        200: {"description": "Successful search with ranked results"},
        400: {"description": "Invalid request (missing query/company_id or both provided)"},
        404: {"description": "Reference company not found or has no embedding"},
        503: {"description": "Embedding service unavailable"},
    },
)
async def semantic_search(
    request: SemanticSearchRequest,
    tenant: dict[str, Any] = Depends(get_current_tenant),
    session: Any = Depends(get_db_session),
) -> SemanticSearchResponse:
    """Search for semantically similar companies.

    Accepts a text query OR a reference company_id and returns companies
    ranked by vector similarity. Results are scoped to the authenticated
    tenant's data.

    Args:
        request: Search parameters (query text or company_id, pagination, filters).
        tenant: Authenticated tenant context from middleware.
        session: Async database session.

    Returns:
        SemanticSearchResponse with ranked company results and similarity scores.

    Raises:
        APIError: On invalid request, missing embedding, or service failure.
    """
    tenant_id = tenant.get("tenant_id", "")
    settings: Settings = get_settings()
    embedding_repo = EmbeddingRepository(session)

    try:
        response = await execute_semantic_search(
            request=request,
            embedding_repo=embedding_repo,
            settings=settings,
            tenant_id=tenant_id,
        )
        logger.info(
            f"[SemanticSearch] query_type={response.query_type} "
            f"results={len(response.items)} total={response.total} "
            f"tenant={tenant_id[:8]}..."
        )
        return response

    except SemanticSearchError as e:
        logger.warning(f"[SemanticSearch] Search failed: code={e.code} message={e.message}")
        status_map = {
            "INVALID_REQUEST": status.HTTP_400_BAD_REQUEST,
            "EMBEDDING_NOT_FOUND": status.HTTP_404_NOT_FOUND,
            "EMBEDDING_GENERATION_FAILED": status.HTTP_503_SERVICE_UNAVAILABLE,
        }
        raise APIError(
            code=e.code,
            message=e.message,
            status_code=status_map.get(e.code, status.HTTP_500_INTERNAL_SERVER_ERROR),
        ) from e
    except (ValueError, TypeError, RuntimeError, OSError) as e:
        logger.error(
            f"[SemanticSearch] Unexpected error: {type(e).__name__}: {e}",
            exc_info=True,
        )
        raise APIError(
            code="INTERNAL_ERROR",
            message="An unexpected error occurred during semantic search.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from e
