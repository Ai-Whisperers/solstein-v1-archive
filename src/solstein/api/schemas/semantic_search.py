"""Request and response schemas for semantic similarity search (STORY-082).

Defines typed Pydantic models for the POST /api/v1/companies/search/semantic
endpoint. Follows typed envelope conventions — no loose dicts cross boundaries.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator


class SemanticSearchRequest(BaseModel):
    """Request body for semantic similarity search.

    Exactly one of ``query`` or ``company_id`` must be provided.
    - ``query``: free-text description; the server embeds it and searches.
    - ``company_id``: use that company's stored embedding as the query vector.

    Attributes:
        query: Free-text search query to embed and match against.
        company_id: Reference company whose embedding is used as the query.
        limit: Maximum number of results to return (1-100).
        offset: Zero-based offset for pagination.
        min_similarity: Minimum cosine similarity threshold (0.0-1.0).
    """

    query: str | None = Field(
        default=None,
        min_length=1,
        max_length=2000,
        description="Free-text query to embed and search against company profiles.",
    )
    company_id: str | None = Field(
        default=None,
        description="ID of a reference company whose embedding is used as the query vector.",
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of results to return.",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Zero-based offset for pagination.",
    )
    min_similarity: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Minimum cosine similarity threshold. Results below this are excluded.",
    )

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    @model_validator(mode="after")
    def validate_exactly_one_query_source(self) -> "SemanticSearchRequest":
        has_query = bool(self.query)
        has_company_id = bool(self.company_id)
        if has_query == has_company_id:
            raise ValueError("Exactly one of 'query' or 'company_id' must be provided")
        return self


class SemanticSearchResultItem(BaseModel):
    """A single company result from semantic similarity search.

    Attributes:
        company_id: Unique company identifier.
        name: Company name.
        industry: Industry classification.
        description: Brief company description.
        similarity_score: Cosine similarity score (0.0-1.0).
        classification: Company classification label.
        tier: Market tier.
        revenue_eur_m: Revenue in EUR millions.
        employee_count: Number of employees.
        composite_score: Composite scoring metric.
        has_embedding: Whether the company has a complete embedding.
    """

    company_id: str
    name: str
    industry: str | None = None
    description: str | None = None
    similarity_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Cosine similarity to the query (1.0 = identical, 0.0 = unrelated).",
    )
    classification: str | None = None
    tier: str | None = None
    revenue_eur_m: float | None = None
    employee_count: int | None = None
    composite_score: float | None = None
    has_embedding: bool = True


class SemanticSearchResponse(BaseModel):
    """Response envelope for semantic similarity search.

    Attributes:
        items: List of matching companies with similarity scores.
        total: Total number of results matching the query (before pagination).
        limit: Page size used for this request.
        offset: Offset used for this request.
        has_next: Whether more results exist beyond this page.
        query_type: Whether the search used 'text' or 'company_id' as input.
    """

    items: list[SemanticSearchResultItem] = Field(
        description="Matching companies ranked by similarity.",
    )
    total: int = Field(ge=0, description="Total matching results.")
    limit: int = Field(ge=1, description="Page size.")
    offset: int = Field(ge=0, description="Zero-based start offset.")
    has_next: bool = Field(description="Whether more pages follow.")
    query_type: str = Field(description="Search mode: 'text' or 'company_id'.")
