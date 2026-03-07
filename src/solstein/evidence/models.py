"""
Evidence Graph System - Core data models for claim-based evidence.

This module defines the claim data model that powers EPIC-042:
Evidence Graph and Claim Provenance.

FREE tools used:
- Pydantic (data validation)
- Python dataclasses
- UUID (unique identifiers)
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum, auto
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ClaimStatus(str, Enum):
    """Status of a claim in the evidence lifecycle."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CONFLICTING = "conflicting"
    STALE = "stale"
    UNDER_REVIEW = "under_review"


class SourceType(str, Enum):
    """Types of sources for claims."""

    WEBSITE = "website"
    NEWS = "news"
    PRESS_RELEASE = "press_release"
    REGULATORY_FILING = "regulatory_filing"
    SOCIAL_MEDIA = "social_media"
    INTERVIEW = "interview"
    PODCAST = "podcast"
    ACADEMIC_PAPER = "academic_paper"
    PATENT = "patent"
    JOB_POSTING = "job_posting"
    REVIEW = "review"
    ARCHIVE = "archive"
    API = "api"
    UNKNOWN = "unknown"


class ConfidenceComponent(BaseModel):
    """Component of confidence score with explanation."""

    name: str
    score: float = Field(ge=0.0, le=1.0)
    explanation: str
    weight: float = Field(default=1.0, ge=0.0, le=1.0)


class Claim(BaseModel):
    """
    A claim represents an extracted statement from a source.

    This is the core unit of evidence in the system. Every metric,
    signal, and score should ultimately trace back to one or more claims.
    """

    # Identity
    id: UUID = Field(default_factory=uuid4)

    # What is being claimed
    entity_id: str  # Company ID, market ID, etc.
    entity_type: str = "company"  # company, market, product, person
    field: str  # e.g., "revenue", "employee_count", "funding_round"
    value: Any  # The actual value
    unit: Optional[str] = None  # e.g., "USD", "employees", "percent"

    # Source information
    source_url: str
    source_type: SourceType
    source_title: Optional[str] = None
    source_published_date: Optional[datetime] = None
    source_author: Optional[str] = None

    # Evidence location
    snippet: str  # The exact text snippet supporting the claim
    snippet_location: Optional[str] = None  # e.g., "paragraph 3", "table row 5"
    page_section: Optional[str] = None  # e.g., "About Us", "Investor Relations"

    # Extraction metadata
    extracted_at: datetime = Field(default_factory=datetime.utcnow)
    extraction_method: str  # e.g., "regex", "llm", "structured_data"
    extractor_version: str = "1.0"

    # Status and lifecycle
    status: ClaimStatus = ClaimStatus.PENDING
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None
    review_notes: Optional[str] = None

    # Confidence (decomposed)
    confidence_components: list[ConfidenceComponent] = Field(default_factory=list)
    overall_confidence: float = Field(default=0.0, ge=0.0, le=1.0)

    # Contradiction tracking
    contradicts_claims: list[UUID] = Field(default_factory=list)
    supported_by_claims: list[UUID] = Field(default_factory=list)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }

    def calculate_overall_confidence(self) -> float:
        """Calculate weighted overall confidence from components."""
        if not self.confidence_components:
            return self.overall_confidence

        total_weight = sum(c.weight for c in self.confidence_components)
        if total_weight == 0:
            return 0.0

        weighted_sum = sum(c.score * c.weight for c in self.confidence_components)
        self.overall_confidence = weighted_sum / total_weight
        return self.overall_confidence


class SourceDocument(BaseModel):
    """
    A source document from which claims are extracted.
    """

    id: UUID = Field(default_factory=uuid4)
    url: str
    title: Optional[str] = None
    source_type: SourceType

    # Content
    raw_content: Optional[str] = None  # Raw HTML/text
    cleaned_content: Optional[str] = None  # Cleaned text

    # Metadata
    domain: str
    published_date: Optional[datetime] = None
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    content_hash: Optional[str] = None  # For change detection

    # Quality signals
    word_count: int = 0
    has_structured_data: bool = False
    language: str = "en"

    # Crawl metadata
    crawl_depth: int = 0
    referrer_url: Optional[str] = None
    user_agent: str = "SolsteinBot/1.0"

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


class Contradiction(BaseModel):
    """
    A contradiction between two or more claims.
    """

    id: UUID = Field(default_factory=uuid4)
    claim_ids: list[UUID]

    # Contradiction details
    field: str  # What field is contradictory
    values: list[Any]  # The conflicting values
    severity: str = "medium"  # low, medium, high, critical

    # Resolution
    status: str = "open"  # open, resolved, false_positive
    resolution_strategy: Optional[str] = None
    resolved_claim_id: Optional[UUID] = None  # Which claim was accepted

    # Metadata
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


class EvidenceReadiness(BaseModel):
    """
    Evidence readiness score for an entity.
    """

    entity_id: str
    entity_type: str = "company"

    # Coverage metrics
    total_claims: int = 0
    claims_by_field: dict[str, int] = Field(default_factory=dict)
    claims_by_source_type: dict[str, int] = Field(default_factory=dict)

    # Quality metrics
    avg_confidence: float = 0.0
    pending_claims: int = 0
    conflicting_claims: int = 0
    stale_claims: int = 0

    # Readiness level
    level: str = "insufficient"  # insufficient, needs_more, decision_support, investment_ready

    # Gaps
    missing_critical_fields: list[str] = Field(default_factory=list)
    recommended_sources: list[str] = Field(default_factory=list)

    calculated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


# Field definitions for common company metrics
COMPANY_METRIC_FIELDS = {
    "revenue": {"type": "currency", "unit": "USD"},
    "growth_rate": {"type": "percentage", "unit": "percent"},
    "employee_count": {"type": "integer", "unit": "employees"},
    "funding_total": {"type": "currency", "unit": "USD"},
    "valuation": {"type": "currency", "unit": "USD"},
    "profit_margin": {"type": "percentage", "unit": "percent"},
    "burn_rate": {"type": "currency", "unit": "USD/month"},
    "cash_on_hand": {"type": "currency", "unit": "USD"},
    "debt_to_equity": {"type": "ratio", "unit": "ratio"},
    "ltv": {"type": "currency", "unit": "USD"},
    "cac": {"type": "currency", "unit": "USD"},
    "mrr": {"type": "currency", "unit": "USD"},
    "magic_number": {"type": "ratio", "unit": "ratio"},
    "founded_year": {"type": "integer", "unit": "year"},
    "headquarters": {"type": "string", "unit": None},
    "industry": {"type": "string", "unit": None},
    "funding_stage": {"type": "string", "unit": None},
}

# Critical fields for investment readiness
CRITICAL_FIELDS = [
    "revenue",
    "growth_rate",
    "employee_count",
    "funding_total",
    "valuation",
]


def create_claim(
    entity_id: str,
    field: str,
    value: Any,
    source_url: str,
    snippet: str,
    source_type: SourceType = SourceType.WEBSITE,
    **kwargs,
) -> Claim:
    """Factory function to create a claim with sensible defaults."""
    return Claim(
        entity_id=entity_id,
        field=field,
        value=value,
        source_url=source_url,
        snippet=snippet,
        source_type=source_type,
        **kwargs,
    )


if __name__ == "__main__":
    # Test the models
    claim = create_claim(
        entity_id="company-001",
        field="revenue",
        value=1000000,
        source_url="https://example.com/about",
        snippet="Our revenue reached $1M in 2024",
        source_type=SourceType.WEBSITE,
        confidence_components=[
            ConfidenceComponent(
                name="source_credibility", score=0.8, explanation="Official company website", weight=0.3
            ),
            ConfidenceComponent(
                name="extraction_quality", score=0.9, explanation="Clear numeric value with context", weight=0.3
            ),
            ConfidenceComponent(name="freshness", score=0.7, explanation="Published in 2024", weight=0.2),
            ConfidenceComponent(name="agreement", score=1.0, explanation="No conflicting claims", weight=0.2),
        ],
    )

    claim.calculate_overall_confidence()
    print(f"Created claim: {claim.id}")
    print(f"Field: {claim.field} = {claim.value}")
    print(f"Confidence: {claim.overall_confidence:.2f}")
    print(f"Status: {claim.status}")
