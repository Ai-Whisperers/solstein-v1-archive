"""Centralized Pydantic schemas for structured LLM outputs.

STORY-072: All structured LLM response types defined here.
Import from this package instead of defining inline schemas at call sites.
"""

from __future__ import annotations

from .research import (
    CompanyExtractionResponse,
    ResearchPlanResponse,
    SearchQueryItem,
)

__all__ = [
    "CompanyExtractionResponse",
    "ResearchPlanResponse",
    "SearchQueryItem",
]
