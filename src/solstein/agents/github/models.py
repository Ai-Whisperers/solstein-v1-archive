"""GitHub data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GitHubRepo:
    """GitHub repository data."""

    name: str
    full_name: str
    stars: int
    language: str | None
    html_url: str
    description: str | None = None
    forks: int = 0
    open_issues: int = 0
    created_at: str | None = None
    updated_at: str | None = None

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "GitHubRepo":
        """Create from GitHub API response."""
        return cls(
            name=data.get("name", ""),
            full_name=data.get("full_name", ""),
            stars=data.get("stargazers_count", 0),
            language=data.get("language"),
            html_url=data.get("html_url", ""),
            description=data.get("description"),
            forks=data.get("forks_count", 0),
            open_issues=data.get("open_issues_count", 0),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )


@dataclass
class TechStack:
    """Extracted tech stack from repos."""

    languages: dict[str, int] = field(default_factory=dict)
    frameworks: list[str] = field(default_factory=list)
    ai_ml_score: float = 0.0
    ai_ml_signals: list[str] = field(default_factory=list)


@dataclass
class DependencyHealth:
    """Dependency health metrics."""

    python: dict[str, Any] = field(default_factory=dict)
    javascript: dict[str, Any] = field(default_factory=dict)
    health_score_0_to_10: float = 10.0
    signal: str = ""
    outdated_count: int = 0
    high_vuln_count: int = 0


@dataclass
class VelocityMetrics:
    """Engineering velocity metrics."""

    commits_30d: int = 0
    contributor_count: int = 0
    trend: str | None = None


@dataclass
class AISignal:
    """AI/ML signal detection result."""

    score: float = 0.0
    signals: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
