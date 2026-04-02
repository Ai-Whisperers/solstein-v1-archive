"""GitHub agent analyzers package.

EPIC-022: Modularized analyzers for GitHub data extraction.
"""

from __future__ import annotations

# Analyzers
from .analyzers import (
    AISignalAnalyzer,
    DependencyAnalyzer,
    TechStackAnalyzer,
    VelocityAnalyzer,
)

# Client and Search
from .client import GitHubClient

# Models
from .models import (
    AISignal,
    DependencyHealth,
    GitHubIssue,
    GitHubRepo,
    TechStack,
    VelocityMetrics,
)
from .search import GitHubOrgSearcher

__all__ = [
    # Models
    "AISignal",
    "DependencyHealth",
    "GitHubIssue",
    "GitHubRepo",
    "TechStack",
    "VelocityMetrics",
    # Client
    "GitHubClient",
    "GitHubOrgSearcher",
    # Analyzers
    "AISignalAnalyzer",
    "DependencyAnalyzer",
    "TechStackAnalyzer",
    "VelocityAnalyzer",
]
