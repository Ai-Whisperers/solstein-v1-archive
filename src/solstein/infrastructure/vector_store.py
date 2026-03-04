"""pgvector embeddings storage and similarity search (EPIC-023).

Provides vector storage for company embeddings using PostgreSQL + pgvector
extension. Supports:
- Storing embedding vectors (OpenAI, local models)
- Similarity search via cosine distance
- Hybrid search (full-text + vector reranking)

Requires pgvector extension::

    CREATE EXTENSION IF NOT EXISTS vector;

Usage::

    from solstein.infrastructure.vector_store import VectorStore
    from sqlalchemy.ext.asyncio import AsyncSession

    store = VectorStore(session)
    await store.upsert(company_id="stripe", embedding=[0.1, ...], model="text-embedding-3")
    similar = await store.similarity_search([0.1, ...], top_k=5)
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from loguru import logger
from sqlalchemy import Column, Float, Index, String, Text, func, select
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class EmbeddingRecord(Base):
    """ORM model for stored embeddings.

    Attributes:
        id: UUID primary key.
        entity_type: Type of entity (e.g. ``'company'``, ``'document'``).
        entity_id: External identifier (e.g. company_id).
        model: Embedding model name (e.g. ``'text-embedding-3-small'``).
        embedding: The vector (list of floats). Stored as pgvector ``vector`` type.
        text_preview: Truncated text for debugging/hybrid search.
        metadata: JSON metadata dict.
    """

    __tablename__ = "embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()")
    entity_type = Column(String(64), nullable=False, index=True)
    entity_id = Column(String(255), nullable=False, index=True)
    model = Column(String(128), nullable=False)
    embedding = Column(ARRAY(Float), nullable=False)  # Will use pgvector vector type via DDL
    text_preview = Column(Text, nullable=True)
    meta = Column(Text, nullable=True)  # JSON string

    __table_args__ = (Index("ix_embeddings_entity", "entity_type", "entity_id", unique=True),)


# DDL to convert ARRAY to pgvector vector type (run once in migration)
PGVECTOR_SETUP_DDL = """
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Convert embedding column to vector type (adjust dimension to your model)
ALTER TABLE embeddings
    ALTER COLUMN embedding TYPE vector(1536)
    USING embedding::vector(1536);

-- Create IVFFlat index for approximate nearest neighbor search
CREATE INDEX IF NOT EXISTS ix_embeddings_vector
    ON embeddings
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);
"""


class VectorStore:
    """Async vector store backed by PostgreSQL pgvector.

    Args:
        session: Async SQLAlchemy session.
        embedding_dimension: Expected vector dimension (default 1536 for OpenAI).
    """

    def __init__(self, session: AsyncSession, embedding_dimension: int = 1536) -> None:
        self._session = session
        self._dim = embedding_dimension

    async def upsert(
        self,
        entity_id: str,
        embedding: Sequence[float],
        entity_type: str = "company",
        model: str = "text-embedding-3-small",
        text_preview: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Store or update an embedding vector.

        Args:
            entity_id: External identifier (e.g. company_id).
            embedding: Vector of floats (length must match ``embedding_dimension``).
            entity_type: Category of entity.
            model: Model that generated the embedding.
            text_preview: Optional truncated source text.
            metadata: Optional JSON-serializable metadata dict.
        """
        import json

        if len(embedding) != self._dim:
            raise ValueError(f"Embedding dimension mismatch: expected {self._dim}, got {len(embedding)}")

        # Check if exists
        result = await self._session.execute(
            select(EmbeddingRecord).where(
                EmbeddingRecord.entity_type == entity_type,
                EmbeddingRecord.entity_id == entity_id,
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.embedding = list(embedding)
            existing.model = model
            existing.text_preview = (text_preview or "")[:500]
            existing.meta = json.dumps(metadata) if metadata else None
            logger.debug("Updated embedding", entity_id=entity_id, model=model)
        else:
            record = EmbeddingRecord(
                entity_type=entity_type,
                entity_id=entity_id,
                model=model,
                embedding=list(embedding),
                text_preview=(text_preview or "")[:500],
                metadata=json.dumps(metadata) if metadata else None,
            )
            self._session.add(record)
            logger.debug("Inserted embedding", entity_id=entity_id, model=model)

        await self._session.commit()

    async def similarity_search(
        self,
        query_embedding: Sequence[float],
        top_k: int = 5,
        entity_type: str | None = None,
        model: str | None = None,
    ) -> list[dict[str, Any]]:
        """Find most similar vectors using cosine distance.

        Args:
            query_embedding: Query vector.
            top_k: Number of results to return.
            entity_type: Optional filter by entity type.
            model: Optional filter by embedding model.

        Returns:
            List of dicts with entity_id, similarity_score (0-1), text_preview.
        """
        if len(query_embedding) != self._dim:
            raise ValueError(f"Query dimension mismatch: expected {self._dim}, got {len(query_embedding)}")

        # Use raw SQL for pgvector cosine similarity
        # cosine_similarity = 1 - cosine_distance
        sql = """
            SELECT
                entity_id,
                entity_type,
                model,
                1 - (embedding <=> :query_vec) AS similarity,
                text_preview
            FROM embeddings
            WHERE 1=1
        """
        params: dict[str, Any] = {"query_vec": list(query_embedding), "top_k": top_k}

        if entity_type:
            sql += " AND entity_type = :entity_type"
            params["entity_type"] = entity_type
        if model:
            sql += " AND model = :model"
            params["model"] = model

        sql += """
            ORDER BY embedding <=> :query_vec
            LIMIT :top_k
        """

        result = await self._session.execute(sql, params)
        rows = result.fetchall()

        return [
            {
                "entity_id": row.entity_id,
                "entity_type": row.entity_type,
                "model": row.model,
                "similarity": round(row.similarity, 4),
                "text_preview": row.text_preview,
            }
            for row in rows
        ]

    async def delete(self, entity_id: str, entity_type: str = "company") -> bool:
        """Delete an embedding by entity ID.

        Returns:
            True if deleted, False if not found.
        """
        result = await self._session.execute(
            select(EmbeddingRecord).where(
                EmbeddingRecord.entity_type == entity_type,
                EmbeddingRecord.entity_id == entity_id,
            )
        )
        record = result.scalar_one_or_none()
        if record is None:
            return False
        await self._session.delete(record)
        await self._session.commit()
        logger.debug("Deleted embedding", entity_id=entity_id, entity_type=entity_type)
        return True

    async def get_stats(self) -> dict[str, Any]:
        """Return statistics about stored embeddings."""
        total_result = await self._session.execute(
            select(EmbeddingRecord.entity_type, func.count().label("count")).group_by(EmbeddingRecord.entity_type)
        )
        by_type = {row.entity_type: row.count for row in total_result}

        model_result = await self._session.execute(
            select(EmbeddingRecord.model, func.count().label("count")).group_by(EmbeddingRecord.model)
        )
        by_model = {row.model: row.count for row in model_result}

        return {
            "total_embeddings": sum(by_type.values()),
            "by_entity_type": by_type,
            "by_model": by_model,
        }
