"""Repository for company embedding operations (EPIC-023).

Handles vector storage, retrieval, and similarity search using pgvector.
Extracted from CompanyRepository to keep class sizes under 300 lines.
"""

from datetime import datetime
from typing import Any

from loguru import logger
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from .database_models import CompanyRecord


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

    async def find_similar_by_vector(
        self,
        query_vector: list[float],
        limit: int = 10,
        tenant_id: str | None = None,
    ) -> list[tuple[CompanyRecord, float]]:
        """Find companies similar to a query vector using cosine distance.

        Uses pgvector's cosine distance operator (<=>). Returns results
        ordered by similarity (highest first).

        Args:
            query_vector: The query embedding vector.
            limit: Maximum number of results.
            tenant_id: Optional tenant scope filter.

        Returns:
            List of (CompanyRecord, similarity_score) tuples, ordered by similarity.
        """
        vector_str = "[" + ",".join(str(v) for v in query_vector) + "]"

        where_clause = "profile_embedding IS NOT NULL"
        params: dict[str, Any] = {"vec": vector_str, "lim": limit}

        if tenant_id is not None:
            where_clause += " AND tenant_id = :tid"
            params["tid"] = tenant_id

        sql = text(
            f"SELECT *, 1 - (profile_embedding <=> :vec::vector) AS similarity "
            f"FROM companies "
            f"WHERE {where_clause} "
            f"ORDER BY profile_embedding <=> :vec::vector "
            f"LIMIT :lim"
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

        return results
