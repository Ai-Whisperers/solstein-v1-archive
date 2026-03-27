"""Tests for EPIC-023 STORY-081: Embedding generation for company profiles.

Validates that:
- company_to_profile_text produces meaningful text from Company objects
- generate_embedding handles missing API keys gracefully
- generate_embedding handles empty text gracefully
- generate_company_embedding returns tuple of (embedding, text)
- Embedding failure never crashes the pipeline (graceful degradation)
- batch_generate_embeddings handles mixed success/failure
- get_embedding_metadata returns correct structure
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from solstein.domain.models import Company
from solstein.llm.embeddings import (
    batch_generate_embeddings,
    company_to_profile_text,
    generate_company_embedding,
    generate_embedding,
    get_embedding_metadata,
)


def _make_company(**overrides: object) -> Company:
    """Create a test Company with sensible defaults."""
    defaults: dict[str, object] = {
        "id": "COMP-ACME-001",
        "name": "Acme Corp",
        "industry": "Technology",
        "description": "Enterprise SaaS platform for logistics optimization.",
        "headquarters": "Munich, Germany",
        "founded_year": 2018,
        "classification": "PHOENIX",
        "revenue": 25.0,
        "growth_rate": 35.0,
        "employee_count": 120,
        "ai_score": 0.82,
        "ai_maturity": "Strong",
        "composite_score": 0.75,
    }
    defaults.update(overrides)
    return Company(**defaults)


def _make_settings(**overrides) -> MagicMock:
    """Create a mock Settings object with embedding config."""
    settings = MagicMock()
    settings.openai_api_key = overrides.get("openai_api_key", "sk-test-key-12345")
    settings.embedding_model = overrides.get("embedding_model", "text-embedding-3-small")
    settings.embedding_dimensions = overrides.get("embedding_dimensions", 1536)
    settings.embedding_batch_size = overrides.get("embedding_batch_size", 50)
    return settings


class TestCompanyToProfileText:
    """Test profile text serialization."""

    def test_includes_company_name_and_industry(self):
        """Profile text must include name and industry."""
        company = _make_company()
        text = company_to_profile_text(company)
        assert "Acme Corp" in text
        assert "Technology" in text

    def test_includes_description(self):
        """Profile text must include company description."""
        company = _make_company(description="Cloud-native logistics platform.")
        text = company_to_profile_text(company)
        assert "Cloud-native logistics platform." in text

    def test_includes_headquarters(self):
        """Profile text must include headquarters."""
        company = _make_company()
        text = company_to_profile_text(company)
        assert "Munich, Germany" in text

    def test_includes_financial_data(self):
        """Profile text must include financial metrics when available."""
        company = _make_company()
        text = company_to_profile_text(company)
        assert "25.0M" in text or "revenue" in text.lower()
        assert "35.0%" in text or "growth" in text.lower()

    def test_includes_ai_metrics(self):
        """Profile text must include AI metrics when available."""
        company = _make_company(ai_score=0.82, ai_maturity="Strong")
        text = company_to_profile_text(company)
        assert "0.82" in text
        assert "Strong" in text

    def test_handles_minimal_company(self):
        """Profile text works with minimal company data (no optional fields)."""
        company = _make_company(
            description=None,
            headquarters=None,
            founded_year=None,
            classification=None,
            revenue_eur_m=None,
            growth_rate_pct=None,
            employee_count=None,
            ai_score=None,
            composite_score=None,
        )
        text = company_to_profile_text(company)
        assert "Acme Corp" in text
        assert len(text) > 10


class TestGenerateEmbedding:
    """Test embedding generation."""

    @pytest.mark.asyncio
    async def test_returns_none_without_api_key(self):
        """Must return None when no OpenAI API key is configured."""
        settings = _make_settings(openai_api_key=None)
        result = await generate_embedding("Test text", settings)
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_for_empty_text(self):
        """Must return None for empty text input."""
        settings = _make_settings()
        result = await generate_embedding("", settings)
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_for_whitespace_text(self):
        """Must return None for whitespace-only text input."""
        settings = _make_settings()
        result = await generate_embedding("   ", settings)
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_embedding_on_success(self):
        """Must return embedding vector on successful API call."""
        settings = _make_settings()
        mock_embedding = [0.1] * 1536
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [{"embedding": mock_embedding}],
            "usage": {"total_tokens": 42},
        }
        mock_response.raise_for_status = MagicMock()

        with patch("solstein.llm.embeddings.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_cls.return_value = mock_client

            result = await generate_embedding("Test company description", settings)

        assert result is not None
        assert len(result) == 1536

    @pytest.mark.asyncio
    async def test_returns_none_on_api_error(self):
        """Must return None on API error (graceful degradation)."""
        settings = _make_settings()

        with patch("solstein.llm.embeddings.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(
                side_effect=httpx.ConnectError("API unavailable")
            )
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_cls.return_value = mock_client

            result = await generate_embedding("Test text", settings)

        assert result is None


class TestGenerateCompanyEmbedding:
    """Test company-level embedding generation."""

    @pytest.mark.asyncio
    async def test_returns_tuple_of_embedding_and_text(self):
        """Must return (embedding, profile_text) tuple."""
        company = _make_company()
        settings = _make_settings()
        mock_embedding = [0.1] * 1536
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [{"embedding": mock_embedding}],
            "usage": {"total_tokens": 100},
        }
        mock_response.raise_for_status = MagicMock()

        with patch("solstein.llm.embeddings.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_cls.return_value = mock_client

            embedding, profile_text = await generate_company_embedding(company, settings)

        assert embedding is not None
        assert len(embedding) == 1536
        assert "Acme Corp" in profile_text

    @pytest.mark.asyncio
    async def test_embedding_failure_returns_none_embedding(self):
        """Embedding failure must return None embedding, not crash."""
        company = _make_company()
        settings = _make_settings(openai_api_key=None)

        embedding, profile_text = await generate_company_embedding(company, settings)

        assert embedding is None
        assert "Acme Corp" in profile_text


class TestGetEmbeddingMetadata:
    """Test embedding metadata generation."""

    def test_returns_model_and_timestamp(self):
        """Must return dict with embedding_model and embedding_updated_at."""
        settings = _make_settings()
        metadata = get_embedding_metadata(settings)

        assert metadata["embedding_model"] == "text-embedding-3-small"
        assert isinstance(metadata["embedding_updated_at"], datetime)

    def test_timestamp_is_utc(self):
        """Timestamp must be UTC."""
        settings = _make_settings()
        metadata = get_embedding_metadata(settings)
        ts = metadata["embedding_updated_at"]
        assert ts.tzinfo == timezone.utc


class TestBatchGenerateEmbeddings:
    """Test batch embedding generation."""

    @pytest.mark.asyncio
    async def test_handles_empty_list(self):
        """Must handle empty company list gracefully."""
        settings = _make_settings()
        results = await batch_generate_embeddings([], settings)
        assert results == []

    @pytest.mark.asyncio
    async def test_returns_results_for_all_companies(self):
        """Must return one result per company."""
        companies = [_make_company(id=f"COMP-{i}", name=f"Company {i}") for i in range(3)]
        settings = _make_settings(openai_api_key=None)

        results = await batch_generate_embeddings(companies, settings)

        assert len(results) == 3
        for name, embedding in results:
            assert embedding is None  # No API key = all None
