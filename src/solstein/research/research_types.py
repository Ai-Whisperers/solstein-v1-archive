"""
Research data types used across the research orchestrator.

Extracted from research_agents.py to reduce file size.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ResearchPlan:
    """Research strategy for a company."""

    company_name: str
    queries: list[dict[str, Any]]
    estimated_sources: int
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SearchResult:
    """Web search result."""

    title: str
    url: str
    snippet: str
    source: str
    relevance_score: float = 0.0
    intent_match: str = ""


@dataclass
class ExtractedData:
    """Structured data extracted from a source."""

    source_url: str
    source_type: str
    data: dict[str, Any]
    confidence: float
    extraction_method: str
    extracted_at: datetime = field(default_factory=datetime.now)
    raw_content: str = ""


@dataclass
class ValidationResult:
    """Data validation outcome."""

    is_valid: bool
    issues: list[str]
    confidence_adjustment: float
    recommendations: list[str]


@dataclass
class ResearchReport:
    """Final research report for a company."""

    company_name: str
    is_synthetic: bool = False
    confidence_score: float = 0.0
    basic_info: dict[str, Any] = field(default_factory=dict)
    financials: dict[str, Any] = field(default_factory=dict)
    funding: dict[str, Any] = field(default_factory=dict)
    data_sources: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


__all__ = [
    "ResearchPlan",
    "SearchResult",
    "ExtractedData",
    "ValidationResult",
    "ResearchReport",
]
