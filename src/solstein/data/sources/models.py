"""Data source models for Solstein."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel


class NewsArticle(BaseModel):
    """News article."""

    title: str
    description: str | None
    source: str
    url: str
    published_at: datetime
    sentiment: str | None = None


class PressCoverage(BaseModel):
    """Press coverage summary."""

    articles: list[NewsArticle]
    total_articles: int
    positive_count: int
    negative_count: int
    neutral_count: int
    sentiment_score: float | None


class LinkedInData(BaseModel):
    """LinkedIn hiring data."""

    company_name: str
    employee_count: int | None
    employee_growth_pct: float | None
    open_positions: int | None
    ai_related_positions: int | None
    recent_hires: list[dict] = []
    company_size: str | None = None


class FundingData(BaseModel):
    """Funding/investment data."""

    company_name: str
    total_raised: float | None
    last_round_amount: float | None
    last_round_date: date | None
    last_round_stage: str | None
    last_round_valuation: float | None
    investors: list[str] = []
    num_rounds: int = 0


class PatentData(BaseModel):
    """Patent data."""

    company_name: str
    total_patents: int
    recent_patents: list[dict] = []
    ai_related_patents: int
    top_patent_categories: list[str] = []


class ProductInfo(BaseModel):
    """Product information from web scraping."""

    company_name: str
    main_products: list[str]
    features: list[str]
    pricing_model: str | None
    target_customers: list[str] = []
    tech_stack: list[str] = []
