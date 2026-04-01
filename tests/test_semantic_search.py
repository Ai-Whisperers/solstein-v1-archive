"""Tests for STORY-082: Semantic similarity search endpoint.

Validates:
- Text query returns ranked results with similarity scores.
- Company ID reference returns similar companies (excluding the reference).
- Tenant isolation: results scoped to the authenticated tenant.
- Pagination works correctly with offset/limit.
- Edge cases: no embeddings, empty database, invalid requests.
- Min similarity threshold filtering.
- Schema validation for request and response models.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from solstein.api.schemas.semantic_search import (
    SemanticSearchRequest,
    SemanticSearchResponse,
    SemanticSearchResultItem,
)
from solstein.application.services.semantic_search_service import (
    SemanticSearchError,
    execute_semantic_search,
)

# --- Schema Validation Tests ---


class TestSemanticSearchRequest:
    """Test request schema validation."""

    def test_valid_text_query(self):
        # Arrange & Act
        req = SemanticSearchRequest(query="AI companies in fintech")

        # Assert
        assert req.query == "AI companies in fintech"
        assert req.company_id is None
        assert req.limit == 20
        assert req.offset == 0
        assert req.min_similarity == 0.0

    def test_valid_company_id_query(self):
        # Arrange & Act
        req = SemanticSearchRequest(company_id="comp-123")

        # Assert
        assert req.query is None
        assert req.company_id == "comp-123"

    def test_custom_pagination(self):
        # Arrange & Act
        req = SemanticSearchRequest(query="test", limit=50, offset=10)

        # Assert
        assert req.limit == 50
        assert req.offset == 10

    def test_min_similarity_threshold(self):
        # Arrange & Act
        req = SemanticSearchRequest(query="test", min_similarity=0.7)

        # Assert
        assert req.min_similarity == 0.7

    def test_limit_bounds(self):
        # Arrange & Act & Assert
        with pytest.raises(Exception):
            SemanticSearchRequest(query="test", limit=0)

        with pytest.raises(Exception):
            SemanticSearchRequest(query="test", limit=101)

    def test_min_similarity_bounds(self):
        # Arrange & Act & Assert
        with pytest.raises(Exception):
            SemanticSearchRequest(query="test", min_similarity=-0.1)

        with pytest.raises(Exception):
            SemanticSearchRequest(query="test", min_similarity=1.1)


class TestSemanticSearchResultItem:
    """Test response item schema."""

    def test_valid_result_item(self):
        # Arrange & Act
        item = SemanticSearchResultItem(
            company_id="comp-1",
            name="Acme Corp",
            industry="Technology",
            similarity_score=0.92,
        )

        # Assert
        assert item.company_id == "comp-1"
        assert item.name == "Acme Corp"
        assert item.similarity_score == 0.92
        assert item.has_embedding is True

    def test_similarity_score_bounds(self):
        # Arrange & Act & Assert
        with pytest.raises(Exception):
            SemanticSearchResultItem(
                company_id="comp-1",
                name="Test",
                similarity_score=1.5,
            )

        with pytest.raises(Exception):
            SemanticSearchResultItem(
                company_id="comp-1",
                name="Test",
                similarity_score=-0.1,
            )


class TestSemanticSearchResponse:
    """Test response envelope schema."""

    def test_valid_response(self):
        # Arrange
        items = [
            SemanticSearchResultItem(
                company_id="comp-1",
                name="Acme Corp",
                similarity_score=0.95,
            ),
            SemanticSearchResultItem(
                company_id="comp-2",
                name="Beta Inc",
                similarity_score=0.82,
            ),
        ]

        # Act
        resp = SemanticSearchResponse(
            items=items,
            total=10,
            limit=20,
            offset=0,
            has_next=False,
            query_type="text",
        )

        # Assert
        assert len(resp.items) == 2
        assert resp.total == 10
        assert resp.query_type == "text"
        assert resp.has_next is False

    def test_empty_results(self):
        # Arrange & Act
        resp = SemanticSearchResponse(
            items=[],
            total=0,
            limit=20,
            offset=0,
            has_next=False,
            query_type="text",
        )

        # Assert
        assert len(resp.items) == 0
        assert resp.total == 0


# --- Service Layer Tests ---


def _mock_company_record(
    company_id: str = "comp-1",
    name: str = "Acme Corp",
    industry: str = "Technology",
    profile_embedding: list[float] | None = None,
    **kwargs: object,
) -> MagicMock:
    """Create a mock CompanyRecord for testing."""
    record = MagicMock()
    record.company_id = company_id
    record.name = name
    record.industry = industry
    record.description = kwargs.get("description")
    record.classification = kwargs.get("classification")
    record.tier = kwargs.get("tier")
    record.revenue_eur_m = kwargs.get("revenue_eur_m")
    record.employee_count = kwargs.get("employee_count")
    record.composite_score = kwargs.get("composite_score")
    record.profile_embedding = profile_embedding or [0.1] * 1536
    return record


def _mock_settings() -> MagicMock:
    """Create mock Settings for testing."""
    settings = MagicMock()
    settings.openai_api_key = "test-key"
    settings.embedding_model = "text-embedding-3-small"
    settings.embedding_dimensions = 1536
    return settings


class TestExecuteSemanticSearch:
    """Test the semantic search service function."""

    @pytest.mark.asyncio
    async def test_text_query_returns_results(self):
        # Arrange
        request = SemanticSearchRequest(query="AI fintech companies")
        mock_repo = AsyncMock()
        mock_repo.find_similar_by_vector.return_value = (
            [
                (_mock_company_record("comp-1", "Acme AI"), 0.95),
                (_mock_company_record("comp-2", "Beta Fin"), 0.82),
            ],
            2,
        )
        settings = _mock_settings()
        embedding_vector = [0.1] * 1536

        with patch(
            "solstein.llm.embeddings.generate_embedding",
            new_callable=AsyncMock,
            return_value=embedding_vector,
        ):
            # Act
            result = await execute_semantic_search(
                request=request,
                embedding_repo=mock_repo,
                settings=settings,
                tenant_id="tenant-abc",
            )

        # Assert
        assert isinstance(result, SemanticSearchResponse)
        assert len(result.items) == 2
        assert result.items[0].similarity_score == 0.95
        assert result.items[0].name == "Acme AI"
        assert result.query_type == "text"
        assert result.total == 2

    @pytest.mark.asyncio
    async def test_company_id_query_returns_results(self):
        # Arrange
        request = SemanticSearchRequest(company_id="comp-ref")
        mock_repo = AsyncMock()
        mock_repo.get_embedding_by_company_id.return_value = [0.2] * 1536
        mock_repo.find_similar_by_vector.return_value = (
            [
                (_mock_company_record("comp-1", "Similar Corp"), 0.88),
            ],
            1,
        )
        settings = _mock_settings()

        # Act
        result = await execute_semantic_search(
            request=request,
            embedding_repo=mock_repo,
            settings=settings,
            tenant_id="tenant-abc",
        )

        # Assert
        assert result.query_type == "company_id"
        assert len(result.items) == 1
        assert result.items[0].similarity_score == 0.88
        mock_repo.find_similar_by_vector.assert_called_once()
        call_kwargs = mock_repo.find_similar_by_vector.call_args.kwargs
        assert call_kwargs["search_params"].exclude_company_id == "comp-ref"

    @pytest.mark.asyncio
    async def test_both_query_and_company_id_raises(self):
        # Arrange
        request = SemanticSearchRequest(query="test", company_id="comp-1")
        mock_repo = AsyncMock()
        settings = _mock_settings()

        # Act & Assert
        with pytest.raises(SemanticSearchError) as exc_info:
            await execute_semantic_search(
                request=request,
                embedding_repo=mock_repo,
                settings=settings,
                tenant_id="tenant-abc",
            )
        assert exc_info.value.code == "INVALID_REQUEST"

    @pytest.mark.asyncio
    async def test_neither_query_nor_company_id_raises(self):
        # Arrange
        request = SemanticSearchRequest()
        mock_repo = AsyncMock()
        settings = _mock_settings()

        # Act & Assert
        with pytest.raises(SemanticSearchError) as exc_info:
            await execute_semantic_search(
                request=request,
                embedding_repo=mock_repo,
                settings=settings,
                tenant_id="tenant-abc",
            )
        assert exc_info.value.code == "INVALID_REQUEST"

    @pytest.mark.asyncio
    async def test_company_id_not_found_raises(self):
        # Arrange
        request = SemanticSearchRequest(company_id="nonexistent")
        mock_repo = AsyncMock()
        mock_repo.get_embedding_by_company_id.return_value = None
        settings = _mock_settings()

        # Act & Assert
        with pytest.raises(SemanticSearchError) as exc_info:
            await execute_semantic_search(
                request=request,
                embedding_repo=mock_repo,
                settings=settings,
                tenant_id="tenant-abc",
            )
        assert exc_info.value.code == "EMBEDDING_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_embedding_generation_failure_raises(self):
        # Arrange
        request = SemanticSearchRequest(query="test query")
        mock_repo = AsyncMock()
        settings = _mock_settings()

        with patch(
            "solstein.llm.embeddings.generate_embedding",
            new_callable=AsyncMock,
            return_value=None,
        ):
            # Act & Assert
            with pytest.raises(SemanticSearchError) as exc_info:
                await execute_semantic_search(
                    request=request,
                    embedding_repo=mock_repo,
                    settings=settings,
                    tenant_id="tenant-abc",
                )
            assert exc_info.value.code == "EMBEDDING_GENERATION_FAILED"

    @pytest.mark.asyncio
    async def test_empty_results_returns_empty_response(self):
        # Arrange
        request = SemanticSearchRequest(query="obscure query nobody matches")
        mock_repo = AsyncMock()
        mock_repo.find_similar_by_vector.return_value = ([], 0)
        settings = _mock_settings()

        with patch(
            "solstein.llm.embeddings.generate_embedding",
            new_callable=AsyncMock,
            return_value=[0.1] * 1536,
        ):
            # Act
            result = await execute_semantic_search(
                request=request,
                embedding_repo=mock_repo,
                settings=settings,
                tenant_id="tenant-abc",
            )

        # Assert
        assert len(result.items) == 0
        assert result.total == 0
        assert result.has_next is False

    @pytest.mark.asyncio
    async def test_pagination_pass_through(self):
        # Arrange
        request = SemanticSearchRequest(query="test", limit=5, offset=10)
        mock_repo = AsyncMock()
        mock_repo.find_similar_by_vector.return_value = (
            [(_mock_company_record(), 0.9)],
            15,
        )
        settings = _mock_settings()

        with patch(
            "solstein.llm.embeddings.generate_embedding",
            new_callable=AsyncMock,
            return_value=[0.1] * 1536,
        ):
            # Act
            result = await execute_semantic_search(
                request=request,
                embedding_repo=mock_repo,
                settings=settings,
                tenant_id="tenant-abc",
            )

        # Assert
        assert result.limit == 5
        assert result.offset == 10
        assert result.total == 15
        assert result.has_next is False  # 10 + 5 = 15, no more

    @pytest.mark.asyncio
    async def test_has_next_true_when_more_results(self):
        # Arrange
        request = SemanticSearchRequest(query="test", limit=5, offset=0)
        mock_repo = AsyncMock()
        mock_repo.find_similar_by_vector.return_value = (
            [(_mock_company_record(), 0.9)] * 5,
            20,
        )
        settings = _mock_settings()

        with patch(
            "solstein.llm.embeddings.generate_embedding",
            new_callable=AsyncMock,
            return_value=[0.1] * 1536,
        ):
            # Act
            result = await execute_semantic_search(
                request=request,
                embedding_repo=mock_repo,
                settings=settings,
                tenant_id="tenant-abc",
            )

        # Assert
        assert result.has_next is True

    @pytest.mark.asyncio
    async def test_tenant_id_passed_to_repository(self):
        # Arrange
        request = SemanticSearchRequest(query="test")
        mock_repo = AsyncMock()
        mock_repo.find_similar_by_vector.return_value = ([], 0)
        settings = _mock_settings()

        with patch(
            "solstein.llm.embeddings.generate_embedding",
            new_callable=AsyncMock,
            return_value=[0.1] * 1536,
        ):
            # Act
            await execute_semantic_search(
                request=request,
                embedding_repo=mock_repo,
                settings=settings,
                tenant_id="tenant-xyz",
            )

        # Assert
        call_kwargs = mock_repo.find_similar_by_vector.call_args.kwargs
        assert call_kwargs["search_params"].tenant_id == "tenant-xyz"

    @pytest.mark.asyncio
    async def test_min_similarity_passed_to_repository(self):
        # Arrange
        request = SemanticSearchRequest(query="test", min_similarity=0.7)
        mock_repo = AsyncMock()
        mock_repo.find_similar_by_vector.return_value = ([], 0)
        settings = _mock_settings()

        with patch(
            "solstein.llm.embeddings.generate_embedding",
            new_callable=AsyncMock,
            return_value=[0.1] * 1536,
        ):
            # Act
            await execute_semantic_search(
                request=request,
                embedding_repo=mock_repo,
                settings=settings,
                tenant_id="tenant-abc",
            )

        # Assert
        call_kwargs = mock_repo.find_similar_by_vector.call_args.kwargs
        assert call_kwargs["search_params"].min_similarity == 0.7
