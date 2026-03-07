"""Additional Data Sources for Solstein Company Research.

⚠️ DEPRECATED: This module has been split into solstein.data.sources package.
For new code, use: from solstein.data.sources import NewsSource, PatentSource, etc.

This file is kept for backward compatibility and re-exports all symbols.
"""

from __future__ import annotations

# Re-export everything from the new modular package
from solstein.data.sources import (
    AdditionalDataSources,
    FundingData,
    FundingSource,
    LinkedInData,
    LinkedInSource,
    NewsArticle,
    NewsSource,
    PatentData,
    PatentSource,
    PressCoverage,
    ProductInfo,
    WebSource,
)
from solstein.data.sources.base import analyze_sentiment

__all__ = [
    "AdditionalDataSources",
    "FundingData",
    "FundingSource",
    "LinkedInData",
    "LinkedInSource",
    "NewsArticle",
    "NewsSource",
    "PatentData",
    "PatentSource",
    "PressCoverage",
    "ProductInfo",
    "WebSource",
    "analyze_sentiment",
]
