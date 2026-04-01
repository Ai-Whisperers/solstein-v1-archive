"""EPIC-023 STORY-080: Add pgvector extension and company embedding schema.

Enables the pgvector extension, adds profile_embedding vector column (1536 dims)
to the companies table, and creates an HNSW index for approximate nearest-neighbor
search. Also adds embedding_model and embedding_updated_at metadata columns.

Embedding dimension 1536 is chosen for OpenAI text-embedding-3-small compatibility.
HNSW index is preferred over IVFFlat for datasets under 1M rows (no reindexing
required, better recall at low latency).

Revision ID: 017
Revises: 016
Create Date: 2026-03-27 09:10:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "017"
down_revision: str | Sequence[str] | None = "016"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Embedding dimension: 1536 for OpenAI text-embedding-3-small.
# If a different model is selected, adjust this before running the migration.
EMBEDDING_DIM = 1536


def upgrade() -> None:
    """Enable pgvector, add embedding column with HNSW index."""
    # 1. Enable pgvector extension (idempotent)
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # 2. Add embedding vector column (nullable - companies without research don't have embeddings)
    op.add_column(
        "companies",
        sa.Column("profile_embedding", sa.Text(), nullable=True),
    )
    # Change the column type to vector using raw SQL (Alembic doesn't natively support vector type)
    op.execute(
        f"ALTER TABLE companies ALTER COLUMN profile_embedding TYPE vector({EMBEDDING_DIM}) USING profile_embedding::vector({EMBEDDING_DIM})"
    )

    # 3. Add embedding metadata columns
    op.add_column(
        "companies",
        sa.Column("embedding_model", sa.String(100), nullable=True),
    )
    op.add_column(
        "companies",
        sa.Column("embedding_updated_at", sa.DateTime(), nullable=True),
    )

    # 4. Create HNSW index for approximate nearest-neighbor search
    # HNSW provides better recall than IVFFlat at sub-1M row counts and
    # does not require periodic reindexing.
    # Using cosine distance operator class (vector_cosine_ops) because
    # company profile embeddings are normalized and cosine similarity is
    # the standard metric for semantic search.
    op.execute(
        "CREATE INDEX ix_company_embedding_hnsw "
        "ON companies USING hnsw (profile_embedding vector_cosine_ops) "
        "WITH (m = 16, ef_construction = 64)"
    )

    # 5. Create a composite index on (tenant_id, profile_embedding IS NOT NULL)
    # to efficiently filter tenant-scoped queries to only companies with embeddings.
    op.create_index(
        "ix_company_tenant_has_embedding",
        "companies",
        ["tenant_id"],
        postgresql_where=sa.text("profile_embedding IS NOT NULL"),
    )


def downgrade() -> None:
    """Remove embedding column, index, and pgvector extension."""
    op.drop_index("ix_company_tenant_has_embedding", table_name="companies")
    op.execute("DROP INDEX IF EXISTS ix_company_embedding_hnsw")
    op.drop_column("companies", "embedding_updated_at")
    op.drop_column("companies", "embedding_model")
    op.drop_column("companies", "profile_embedding")
    # Note: We don't drop the pgvector extension because other tables might use it.
    # op.execute("DROP EXTENSION IF EXISTS vector")
