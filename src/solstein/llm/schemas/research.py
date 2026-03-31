"""Pydantic schemas for research agent LLM responses.

STORY-072: Centralized schema definitions for structured LLM outputs
used by ResearchPlannerAgent and ContentExtractorAgent.

STORY-252: Added minimum-validity validators so empty or unknown-only
payloads cannot pass as successful extractions.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class SearchQueryItem(BaseModel):
    """A single search query in a research plan."""

    query: str = Field(description="The search query string")
    priority: int = Field(
        ge=1, le=3, description="Priority level: 1=critical, 2=important, 3=nice-to-have"
    )
    intent: str = Field(description="What this query aims to discover (e.g. 'website', 'funding')")


class ResearchPlanResponse(BaseModel):
    """LLM response schema for research plan generation."""

    queries: list[SearchQueryItem] = Field(
        min_length=1, description="Prioritized search queries for the research plan"
    )
    estimated_sources: int = Field(
        ge=1, le=50, default=5, description="Estimated number of sources to find"
    )


class EmptyExtractionError(ValueError):
    """Raised when an extraction payload contains no meaningful data."""


# Minimum number of non-null fields required for a valid extraction
_MIN_MEANINGFUL_FIELDS = 1

# Fields that count as "meaningful" (identity + substance)
_IDENTITY_FIELDS = {"company_name", "website"}
_SUBSTANCE_FIELDS = {
    "description", "industry", "headquarters", "founded_year",
    "employees", "revenue", "funding_raised", "valuation",
    "key_executives", "products", "is_public",
}
_MEANINGFUL_FIELDS = _IDENTITY_FIELDS | _SUBSTANCE_FIELDS


class CompanyExtractionResponse(BaseModel):
    """LLM response schema for structured company data extraction.

    STORY-252: Requires at least one meaningful field to be non-null.
    An all-null or unknown-only payload raises ``EmptyExtractionError``
    so the caller can distinguish schema failure from "no data found".
    """

    company_name: str | None = Field(default=None, description="Official company name")
    website: str | None = Field(default=None, description="Company website URL")
    description: str | None = Field(default=None, description="Brief company description")
    industry: str | None = Field(default=None, description="Primary industry/sector")
    headquarters: str | None = Field(default=None, description="HQ location")
    founded_year: int | None = Field(default=None, description="Year the company was founded")
    employees: int | None = Field(default=None, description="Approximate employee count")
    revenue: float | None = Field(default=None, description="Annual revenue in millions USD")
    revenue_currency: str | None = Field(default=None, description="Revenue currency code")
    funding_raised: float | None = Field(
        default=None, description="Total funding raised in millions USD"
    )
    valuation: float | None = Field(default=None, description="Company valuation in millions USD")
    funding_rounds: list[str] | None = Field(
        default=None, description="List of funding round names"
    )
    key_executives: list[str] | None = Field(
        default=None, description="Names of key executives"
    )
    products: list[str] | None = Field(default=None, description="Main products or services")
    is_public: bool | None = Field(default=None, description="Whether the company is publicly traded")

    @model_validator(mode="after")
    def check_minimum_payload(self) -> CompanyExtractionResponse:
        """Reject empty or non-informative extraction payloads.

        At least one meaningful field must be non-null for the extraction
        to count as successful. This prevents the LLM from returning
        ``{}`` or all-null objects that pass Pydantic validation but carry
        no useful data.
        """
        populated = sum(
            1 for field_name in _MEANINGFUL_FIELDS
            if getattr(self, field_name, None) is not None
        )
        if populated < _MIN_MEANINGFUL_FIELDS:
            msg = (
                f"Extraction payload has {populated} meaningful fields "
                f"(minimum {_MIN_MEANINGFUL_FIELDS}). "
                "This looks like an empty or non-informative extraction."
            )
            raise EmptyExtractionError(msg)
        return self

    @property
    def is_minimal(self) -> bool:
        """Return True if only identity fields are populated (no substance)."""
        return not any(
            getattr(self, f, None) is not None for f in _SUBSTANCE_FIELDS
        )
