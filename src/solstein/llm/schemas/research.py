"""Pydantic schemas for research agent LLM responses.

STORY-072: Centralized schema definitions for structured LLM outputs
used by ResearchPlannerAgent and ContentExtractorAgent.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class SearchQueryItem(BaseModel):
    """A single search query in a research plan."""

    query: str = Field(description="The search query string")
    priority: int = Field(ge=1, le=3, description="Priority level: 1=critical, 2=important, 3=nice-to-have")
    intent: str = Field(description="What this query aims to discover (e.g. 'website', 'funding')")


class ResearchPlanResponse(BaseModel):
    """LLM response schema for research plan generation."""

    queries: list[SearchQueryItem] = Field(min_length=1, description="Prioritized search queries for the research plan")
    estimated_sources: int = Field(ge=1, le=50, default=5, description="Estimated number of sources to find")


class CompanyExtractionResponse(BaseModel):
    """LLM response schema for structured company data extraction."""

    company_name: str | None = Field(default=None, description="Official company name")
    website: str | None = Field(default=None, description="Company website URL")
    description: str | None = Field(default=None, description="Brief company description")
    industry: str | None = Field(default=None, description="Primary industry/sector")
    headquarters: str | None = Field(default=None, description="HQ location")
    founded_year: int | None = Field(default=None, description="Year the company was founded")
    employees: int | None = Field(default=None, description="Approximate employee count")
    revenue: float | None = Field(default=None, description="Annual revenue in millions USD")
    revenue_currency: str | None = Field(default=None, description="Revenue currency code")
    funding_raised: float | None = Field(default=None, description="Total funding raised in millions USD")
    valuation: float | None = Field(default=None, description="Company valuation in millions USD")
    funding_rounds: list[str] | None = Field(default=None, description="List of funding round names")
    key_executives: list[str] | None = Field(default=None, description="Names of key executives")
    products: list[str] | None = Field(default=None, description="Main products or services")
    is_public: bool | None = Field(default=None, description="Whether the company is publicly traded")
