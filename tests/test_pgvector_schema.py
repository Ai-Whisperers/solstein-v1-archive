"""Tests for EPIC-023 STORY-080: pgvector schema and embedding column.

Validates that:
- CompanyRecord has the profile_embedding vector column
- Embedding metadata columns exist (embedding_model, embedding_updated_at)
- Column nullability is correct (embeddings are optional)
- Migration file structure is valid
- to_dict includes embedding metadata
"""

from __future__ import annotations

import importlib.util
from datetime import datetime, timezone
from pathlib import Path

import pytest
from pgvector.sqlalchemy import Vector
from pydantic import ValidationError
from sqlalchemy import inspect

from solstein.config import Settings
from solstein.infrastructure.models.company import CompanyRecord


class TestCompanyRecordEmbeddingColumn:
    """Test that CompanyRecord has the correct embedding schema."""

    def test_profile_embedding_column_exists(self):
        """CompanyRecord must have a profile_embedding column."""
        mapper = inspect(CompanyRecord)
        column_names = [col.key for col in mapper.columns]
        assert "profile_embedding" in column_names

    def test_embedding_model_column_exists(self):
        """CompanyRecord must have an embedding_model metadata column."""
        mapper = inspect(CompanyRecord)
        column_names = [col.key for col in mapper.columns]
        assert "embedding_model" in column_names

    def test_embedding_updated_at_column_exists(self):
        """CompanyRecord must have an embedding_updated_at metadata column."""
        mapper = inspect(CompanyRecord)
        column_names = [col.key for col in mapper.columns]
        assert "embedding_updated_at" in column_names

    def test_profile_embedding_is_nullable(self):
        """Embedding column must be nullable (companies without research have no embedding)."""
        mapper = inspect(CompanyRecord)
        embedding_col = mapper.columns["profile_embedding"]
        assert embedding_col.nullable is True

    def test_embedding_model_is_nullable(self):
        """Embedding model column must be nullable."""
        mapper = inspect(CompanyRecord)
        col = mapper.columns["embedding_model"]
        assert col.nullable is True

    def test_embedding_updated_at_is_nullable(self):
        """Embedding updated_at column must be nullable."""
        mapper = inspect(CompanyRecord)
        col = mapper.columns["embedding_updated_at"]
        assert col.nullable is True

    def test_embedding_vector_dimension(self):
        """Embedding column must use Vector(1536) type."""
        mapper = inspect(CompanyRecord)
        embedding_col = mapper.columns["profile_embedding"]
        col_type = embedding_col.type
        assert isinstance(col_type, Vector)
        assert col_type.dim == 1536


class TestCompanyRecordToDict:
    """Test that to_dict includes embedding metadata."""

    def test_to_dict_has_embedding_field(self):
        """to_dict must include has_embedding boolean."""
        record = CompanyRecord(
            company_id="test-001",
            name="Test Corp",
            profile_embedding=None,
        )
        result = record.to_dict()
        assert "has_embedding" in result
        assert result["has_embedding"] is False

    def test_to_dict_has_embedding_model_field(self):
        """to_dict must include embedding_model."""
        record = CompanyRecord(
            company_id="test-001",
            name="Test Corp",
            embedding_model="text-embedding-3-small",
        )
        result = record.to_dict()
        assert "embedding_model" in result
        assert result["embedding_model"] == "text-embedding-3-small"

    def test_to_dict_has_embedding_updated_at_field(self):
        """to_dict must include embedding_updated_at as ISO string."""
        now = datetime.now(timezone.utc)
        record = CompanyRecord(
            company_id="test-001",
            name="Test Corp",
            embedding_updated_at=now,
        )
        result = record.to_dict()
        assert "embedding_updated_at" in result
        assert result["embedding_updated_at"] == now.isoformat()

    def test_to_dict_embedding_does_not_include_raw_vector(self):
        """to_dict must NOT include the raw embedding vector (too large for API responses)."""
        record = CompanyRecord(
            company_id="test-001",
            name="Test Corp",
        )
        result = record.to_dict()
        assert "profile_embedding" not in result


class TestMigrationFileStructure:
    """Test that the migration file has correct structure."""

    def test_merge_migration_exists(self):
        """Merge migration 016 must exist to unify EPIC-019 heads."""
        migration_path = Path("alembic/versions/016_merge_epic019_heads.py")
        assert migration_path.exists(), "Merge migration 016 must exist"

    def test_pgvector_migration_exists(self):
        """pgvector migration 017 must exist."""
        migration_path = Path("alembic/versions/017_epic023_pgvector_embedding.py")
        assert migration_path.exists(), "pgvector migration 017 must exist"

    def test_pgvector_migration_revision_chain(self):
        """Migration 017 must depend on merge migration 016."""
        spec = importlib.util.spec_from_file_location(
            "migration_017",
            Path("alembic/versions/017_epic023_pgvector_embedding.py"),
        )
        assert spec is not None
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        assert mod.revision == "017"
        assert mod.down_revision == "016"

    def test_merge_migration_depends_on_all_epic019_heads(self):
        """Merge migration 016 must depend on 013, 014, and 015."""
        spec = importlib.util.spec_from_file_location(
            "migration_016",
            Path("alembic/versions/016_merge_epic019_heads.py"),
        )
        assert spec is not None
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        assert mod.revision == "016"
        assert set(mod.down_revision) == {"013", "014", "015"}


class TestEmbeddingConfig:
    """Test embedding configuration in Settings."""

    def test_embedding_config_defaults(self):
        """Settings must have embedding configuration with sensible defaults."""
        settings = Settings.load()
        assert settings.embedding_model == "text-embedding-3-small"
        assert settings.embedding_dimensions == 1536
        assert settings.embedding_batch_size == 50

    def test_embedding_batch_size_constraints(self):
        """Batch size must be between 1 and 500."""
        with pytest.raises(ValidationError):
            Settings(
                _env_file=None,
                embedding_batch_size=0,
            )
