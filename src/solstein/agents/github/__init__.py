"""GitHub agent analyzers package.

EPIC-022: Modularized analyzers for GitHub data extraction.
"""

from __future__ import annotations

# Models
from .models import (
    AISignal,
    DependencyHealth,
    GitHubRepo,
    TechStack,
    VelocityMetrics,
)

# Client and Search
from .client import GitHubClient
from .search import GitHubOrgSearcher

# Analyzers
from .analyzers import (
    AISignalAnalyzer,
    DependencyAnalyzer,
    TechStackAnalyzer,
    VelocityAnalyzer,
)

__all__ = [
    # Models
    "AISignal",
    "DependencyHealth",
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
