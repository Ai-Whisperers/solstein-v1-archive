"""Repository for company embedding operations (EPIC-023).

Handles vector storage, retrieval, and similarity search using pgvector.
Extracted from CompanyRepository to keep class sizes under 300 lines.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from loguru import logger
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from .database_models import CompanyRecord


@dataclass
class SimilaritySearchParams:
    """Parameters for vector similarity search.

    Bundles filter/pagination options for find_similar_by_vector to keep
    the method signature under the 5-parameter limit.

    Attributes:
        limit: Maximum number of results per page.
        offset: Number of results to skip (for pagination).
        tenant_id: Optional tenant scope filter.
        min_similarity: Minimum similarity threshold (0.0-1.0).
        exclude_company_id: Exclude this company from results.
    """

    limit: int = 10
    offset: int = 0
    tenant_id: str | None = None
    min_similarity: float = 0.0
    exclude_company_id: str | None = None


class EmbeddingRepository:
    """Repository for embedding-related database operations.

    Provides async methods for storing, querying, and searching
    company profile embeddings via pgvector.
    """

    def __init__(self, session: AsyncSession):
        """Initialize repository with async database session.

        Args:
            session: AsyncSession instance for database operations.
        """
        self.session = session

    async def update_embedding(
        self,
        company_id: str,
        embedding: list[float],
        model: str,
        updated_at: datetime,
    ) -> bool:
        """Update a company's profile embedding vector.

        Args:
            company_id: Unique company identifier.
            embedding: The embedding vector as a list of floats.
            model: Name of the embedding model used.
            updated_at: Timestamp of embedding generation.

        Returns:
            True if update succeeded, False if company not found.
        """
        result = await self.session.execute(
            select(CompanyRecord).where(CompanyRecord.company_id == company_id)
        )
        record = result.scalar_one_or_none()

        if not record:
            logger.warning(f"[EmbeddingUpdate] Company {company_id} not found")
            return False

        record.profile_embedding = embedding
        record.embedding_model = model
        record.embedding_updated_at = updated_at
        self.session.add(record)
        await self.session.flush()
        return True

    async def get_companies_without_embeddings(
        self,
        limit: int = 100,
    ) -> list[CompanyRecord]:
        """Retrieve companies that do not yet have embeddings.

        Used by the batch backfill script to find companies needing embeddings.

        Args:
            limit: Maximum number of records to return.

        Returns:
            List of CompanyRecord objects without embeddings.
        """
        result = await self.session.execute(
            select(CompanyRecord)
            .where(CompanyRecord.profile_embedding.is_(None))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_embedding_by_company_id(
        self,
        company_id: str,
    ) -> list[float] | None:
        """Retrieve the stored embedding vector for a specific company.

        Args:
            company_id: The company's unique identifier.

        Returns:
            The embedding vector as a list of floats, or None if not found
            or if the company has no embedding.
        """
        result = await self.session.execute(
            select(CompanyRecord.profile_embedding).where(
                CompanyRecord.company_id == company_id
            )
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None
        # pgvector returns a numpy-like object; convert to plain list
        return list(row) if row is not None else None

    async def find_similar_by_vector(
        self,
        query_vector: list[float],
        search_params: SimilaritySearchParams | None = None,
    ) -> tuple[list[tuple[CompanyRecord, float]], int]:
        """Find companies similar to a query vector using cosine distance.

        Uses pgvector's cosine distance operator (<=>). Returns results
        ordered by similarity (highest first).

        Args:
            query_vector: The query embedding vector.
            search_params: Filter/pagination options. Defaults to
                SimilaritySearchParams() if not provided.

        Returns:
            Tuple of (results, total_count) where results is a list of
            (CompanyRecord, similarity_score) tuples ordered by similarity,
            and total_count is the total matching rows (before pagination).
        """
        sp = search_params or SimilaritySearchParams()
        vector_str = "[" + ",".join(str(v) for v in query_vector) + "]"

        where_clauses = ["profile_embedding IS NOT NULL"]
        params: dict[str, Any] = {"vec": vector_str, "lim": sp.limit, "off": sp.offset}

        if sp.tenant_id is not None:
            where_clauses.append("tenant_id = :tid")
            params["tid"] = sp.tenant_id

        if sp.min_similarity > 0.0:
            where_clauses.append("1 - (profile_embedding <=> :vec::vector) >= :min_sim")
            params["min_sim"] = sp.min_similarity

        if sp.exclude_company_id is not None:
            where_clauses.append("company_id != :excl_cid")
            params["excl_cid"] = sp.exclude_company_id

        where_sql = " AND ".join(where_clauses)

        # Count total matching rows
        count_sql = text(
            f"SELECT COUNT(*) FROM companies WHERE {where_sql}"
        )
        count_result = await self.session.execute(count_sql, params)
        total_count = count_result.scalar() or 0

        # Fetch paginated results
        sql = text(
            f"SELECT *, 1 - (profile_embedding <=> :vec::vector) AS similarity "
            f"FROM companies "
            f"WHERE {where_sql} "
            f"ORDER BY profile_embedding <=> :vec::vector "
            f"LIMIT :lim OFFSET :off"
        )

        result = await self.session.execute(sql, params)
        rows = result.fetchall()

        results: list[tuple[CompanyRecord, float]] = []
        for row in rows:
            record = CompanyRecord(**{
                col: getattr(row, col)
                for col in CompanyRecord.__table__.columns.keys()
                if hasattr(row, col)
            })
            similarity = row.similarity
            results.append((record, similarity))

        return results, total_count
