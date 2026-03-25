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

from typing import Any

from loguru import logger
from sqlalchemy import Column, Float, Index, String, Text, func, select, text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.types import UserDefinedType

Base = declarative_base()


class PgVector(UserDefinedType):
    """SQLAlchemy type for pgvector's vector column type."""

    cache_ok = True

    def __init__(self, dimensions: int = 1536):
        self.dimensions = dimensions

    def get_col_spec(self) -> str:
        return f"vector({self.dimensions})"

    def bind_processor(self, dialect):
        def process(value):
            if value is None:
                return None
            if isinstance(value, list):
                return str(value)
            return value
        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            if value is None:
                return None
            if isinstance(value, str):
                return [float(x) for x in value.strip("[]").split(",")]
            return value
        return process


class EmbeddingRecord(Base):
    """ORM model for stored embeddings.

    Attributes:
        id: Primary key (UUID)
        entity_id: External ID of the entity (e.g., company_id)
        entity_type: Type of entity (default: company)
        embedding: Vector embedding (pgvector format)
        model: Model used to generate embedding
        text_preview: Snippet of text used for embedding
    """

    __tablename__ = "embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=func.uuid_generate_v4())
    entity_id = Column(String(100), index=True, nullable=False)
    entity_type = Column(String(50), index=True, default="company")
    embedding = Column(PgVector(1536), nullable=False)
    model = Column(String(100), index=True)
    text_preview = Column(Text)

    __table_args__ = (
        Index(
            "ix_embeddings_cosine",
            "embedding",
            postgresql_using="ivfflat",
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )


class VectorStore:
    """Interface for pgvector storage operations."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def upsert(
        self,
        entity_id: str,
        embedding: list[float],
        entity_type: str = "company",
        model: str | None = None,
        text_preview: str | None = None,
    ) -> None:
        """Store or update an embedding vector."""
        # Check if exists
        stmt = select(EmbeddingRecord).where(
            EmbeddingRecord.entity_id == entity_id,
            EmbeddingRecord.entity_type == entity_type,
        )
        result = await self._session.execute(stmt)
        record = result.scalar_one_or_none()

        if record:
            record.embedding = embedding
            record.model = model
            record.text_preview = text_preview
        else:
            record = EmbeddingRecord(
                entity_id=entity_id,
                entity_type=entity_type,
                embedding=embedding,
                model=model,
                text_preview=text_preview,
            )
            self._session.add(record)

        await self._session.commit()
        logger.debug(f"Stored embedding for {entity_type}:{entity_id}")

    async def similarity_search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        entity_type: str | None = None,
        model: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search for similar embeddings using cosine distance.

        Returns:
            List of matches with similarity scores.
        """
        # Note: We use raw SQL for pgvector specific operators (<=>)
        # unless we use the pgvector-python integration library.
        params: dict[str, Any] = {
            "query_vec": query_embedding,
            "top_k": top_k,
        }

        sql = """
            SELECT
                entity_id,
                entity_type,
                model,
                text_preview,
                1 - (embedding <=> :query_vec) as similarity
            FROM embeddings
            WHERE 1=1
        """

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

        result = await self._session.execute(text(sql), params)
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
        stmt = select(EmbeddingRecord).where(
            EmbeddingRecord.entity_id == entity_id,
            EmbeddingRecord.entity_type == entity_type,
        )
        result = await self._session.execute(stmt)
        record = result.scalar_one_or_none()

        if record:
            await self._session.delete(record)
            await self._session.commit()
            return True

        return False

    async def hybrid_search(
        self,
        query_text: str,
        query_embedding: list[float],
        top_k: int = 5,
        vector_weight: float = 0.7,
    ) -> list[dict[str, Any]]:
        """Perform hybrid search combining full-text and vector similarity.

        Reranks results using a weighted score.
        """
        # 1. Get vector matches
        vector_matches = await self.similarity_search(query_embedding, top_k=top_k * 2)

        # 2. Hybrid scoring logic (mocked for now - requires text search backend)
        # In a real implementation, we would also query the Companies full-text index
        # and combine the scores using Reciprocal Rank Fusion (RRF).

        # For now, just return top vector matches
        return vector_matches[:top_k]
