"""GitHub analyzers for extracting insights from repositories."""

from __future__ import annotations

import re
from typing import Any

from .client import GitHubClient
from .models import AISignal, DependencyHealth, GitHubRepo, TechStack, VelocityMetrics


class TechStackAnalyzer:
    """Analyze tech stack from GitHub repos."""

    AI_ML_KEYWORDS = [
        "machine learning",
        "deep learning",
        "neural network",
        "artificial intelligence",
        "tensorflow",
        "pytorch",
        "scikit-learn",
        "sklearn",
        "keras",
        "jax",
        "huggingface",
        "transformers",
        "llm",
        "langchain",
        "openai",
        "gpt",
        "computer vision",
        "nlp",
        "natural language",
        "model training",
        "inference",
        "prediction",
        "classification",
        "regression",
    ]

    def analyze(self, repos: list[GitHubRepo]) -> TechStack:
        """Extract tech stack from repos."""
        languages: dict[str, int] = {}
        frameworks: list[str] = []
        ai_ml_signals: list[str] = []

        for repo in repos:
            if repo.language:
                languages[repo.language] = languages.get(repo.language, 0) + repo.stars

            # Check for AI/ML signals in repo name/description
            text = f"{repo.name} {repo.description or ''}".lower()
            for keyword in self.AI_ML_KEYWORDS:
                if keyword in text:
                    ai_ml_signals.append(f"{repo.name}: {keyword}")

        # Calculate AI/ML score
        ai_score = min(1.0, len(ai_ml_signals) / max(len(repos), 1))

        return TechStack(
            languages=languages,
            frameworks=frameworks,
            ai_ml_score=ai_score,
            ai_ml_signals=ai_ml_signals[:10],  # Limit to top 10
        )


class VelocityAnalyzer:
    """Analyze engineering velocity from GitHub data."""

    def __init__(self, client: GitHubClient):
        self.client = client

    def analyze(self, org_name: str, repos: list[GitHubRepo]) -> VelocityMetrics:
        """Calculate engineering velocity metrics."""
        # Simplified - in production would fetch actual commit data
        total_stars = sum(r.stars for r in repos)

        # Estimate based on stars as proxy for activity
        estimated_contributors = min(total_stars // 10, 1000)

        return VelocityMetrics(
            commits_30d=estimated_contributors * 5,  # Rough estimate
            contributor_count=estimated_contributors,
            trend=None,
        )


class AISignalAnalyzer:
    """Analyze AI/ML signals in repositories."""

    AI_FRAMEWORKS = [
        "tensorflow",
        "pytorch",
        "jax",
        "huggingface",
        "transformers",
        "langchain",
        "openai",
        "anthropic",
        "ollama",
        "llama.cpp",
    ]

    def analyze(self, repos: list[GitHubRepo]) -> AISignal | None:
        """Detect AI/ML signals."""
        signals = []
        evidence = []

        for repo in repos:
            text = f"{repo.name} {repo.description or ''}".lower()

            for framework in self.AI_FRAMEWORKS:
                if framework in text:
                    signals.append(framework)
                    evidence.append(f"{repo.full_name}: mentions {framework}")

        if not signals:
            return None

        score = min(1.0, len(set(signals)) / 5)  # Score based on framework diversity

        return AISignal(
            score=score,
            signals=list(set(signals)),
            evidence=evidence[:5],
        )


class DependencyAnalyzer:
    """Analyze dependency health from requirements.txt and package.json."""

    def __init__(self, client: GitHubClient):
        self.client = client

    def analyze(self, org_name: str, repos: list[GitHubRepo]) -> DependencyHealth | None:
        """Analyze dependency health."""
        python_deps: dict[str, dict] = {}
        js_deps: dict[str, dict] = {}

        for repo in repos[:5]:  # Limit to top 5 repos
            # Parse Python requirements
            reqs_text = self.client.fetch_file(org_name, repo.name, "requirements.txt")
            if reqs_text:
                for dep in self._parse_requirements_txt(reqs_text):
                    name = dep.get("name")
                    if name and name not in python_deps:
                        python_deps[name] = dep

            # Parse JS package.json
            pkg_text = self.client.fetch_file(org_name, repo.name, "package.json")
            if pkg_text:
                for name, spec in self._parse_package_json_deps(pkg_text).items():
                    if name not in js_deps:
                        js_deps[name] = {"name": name, "spec": spec}

        if not python_deps and not js_deps:
            return None

        # Calculate health score
        outdated_count = 0  # Would need version lookup for accurate count
        high_vuln_count = 0

        score = 10
        score -= min(5, outdated_count)
        score -= min(6, high_vuln_count * 2)
        score = max(0, min(10, score))

        signal_parts = []
        if python_deps:
            signal_parts.append(f"{len(python_deps)} Python deps")
        if js_deps:
            signal_parts.append(f"{len(js_deps)} JS deps")

        return DependencyHealth(
            python={"count": len(python_deps)},
            javascript={"count": len(js_deps)},
            health_score_0_to_10=score,
            signal=", ".join(signal_parts),
            outdated_count=outdated_count,
            high_vuln_count=high_vuln_count,
        )

    _REQ_LINE_RE = re.compile(r"^(?P<name>[A-Za-z0-9_.-]+)(?:\[[^\]]+\])?\s*(?P<op>==|>=)\s*(?P<ver>[0-9][^;\s]*)")

    def _parse_requirements_txt(self, text: str) -> list[dict[str, Any]]:
        """Parse requirements.txt content."""
        deps: list[dict[str, Any]] = []

        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith(("-r", "--", "git+", "http://", "https://")):
                continue

            line = line.split(";", 1)[0].strip()
            line = line.split(" #", 1)[0].strip()

            m = self._REQ_LINE_RE.match(line)
            if not m:
                continue

            deps.append(
                {
                    "name": m.group("name"),
                    "pinned_version": m.group("ver") if m.group("op") == "==" else None,
                    "min_version": m.group("ver") if m.group("op") == ">=" else None,
                    "specifier": f"{m.group('op')}{m.group('ver')}",
                }
            )

        return deps

    def _parse_package_json_deps(self, text: str) -> dict[str, str]:
        """Parse package.json dependencies."""
        import json

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return {}

        if not isinstance(data, dict):
            return {}

        deps: dict[str, str] = {}
        for section in ("dependencies", "devDependencies"):
            raw = data.get(section)
            if not isinstance(raw, dict):
                continue
            for name, spec in raw.items():
                if isinstance(name, str) and isinstance(spec, str):
                    deps[name] = spec

        return deps
