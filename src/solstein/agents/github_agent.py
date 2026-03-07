"""GitHub data gathering agent.

EPIC-022: Refactored from 756-line god class to use analyzers package.
"""

from __future__ import annotations

from datetime import datetime, timezone

from ..domain.models import DataSourceType
from .base_agent import AgentTaskResult, BaseDataGatheringAgent
from .github import (
    AISignalAnalyzer,
    DependencyAnalyzer,
    GitHubClient,
    GitHubOrgSearcher,
    GitHubRepo,
    TechStackAnalyzer,
    VelocityAnalyzer,
)


class GitHubAgent(BaseDataGatheringAgent):
    """Agent for gathering data from GitHub using modular analyzers."""

    def __init__(self, github_token: str | None = None):
        """Initialize GitHub agent."""
        super().__init__("GitHubAgent", DataSourceType.GITHUB)

        from solstein.config import get_settings

        settings = get_settings()
        token = github_token or settings.github_token

        # Initialize modular components
        self.client = GitHubClient(token)
        self.searcher = GitHubOrgSearcher(self.client)
        self.tech_analyzer = TechStackAnalyzer()
        self.velocity_analyzer = VelocityAnalyzer(self.client)
        self.ai_analyzer = AISignalAnalyzer()
        self.dep_analyzer = DependencyAnalyzer(self.client)

    async def gather(self, company_name: str, context: dict) -> AgentTaskResult:
        """Gather GitHub data for a company."""
        start_time = datetime.now(timezone.utc)
        result = AgentTaskResult(
            agent_name=self.agent_name,
            source_type=self.source_type,
            success=False,
        )

        try:
            self.log_info(f"Starting GitHub research for {company_name}")

            # Find GitHub org
            known_org = context.get("known_github_org")
            github_org = known_org if isinstance(known_org, str) and known_org else None

            if github_org is None:
                github_org = self.searcher.search(company_name)
                if github_org is None:
                    self.log_warning(f"No GitHub org found for {company_name}")
                    result.coverage_gaps.append("GitHub organization not found")
                    result.error_message = "No GitHub organization found"
                    result.execution_time_seconds = (datetime.now(timezone.utc) - start_time).total_seconds()
                    return result

            # Fetch repos
            repos_data = self.searcher.fetch_repos(github_org)
            if not repos_data:
                self.log_warning(f"No repos found in {github_org}")
                result.coverage_gaps.append("No public repositories available")
                result.error_message = f"No repositories found in {github_org}"
                result.execution_time_seconds = (datetime.now(timezone.utc) - start_time).total_seconds()
                return result

            # Convert to models
            repos = [GitHubRepo.from_api(r) for r in repos_data]
            primary_repos = sorted(repos, key=lambda r: r.stars, reverse=True)[:5]

            self.log_info(f"Analyzing {len(primary_repos)} repos for {company_name}")

            # Add raw sources
            for repo in primary_repos:
                raw_source = self._create_raw_source(
                    raw_content=repo.__dict__,
                    source_name=f"GitHub: {repo.full_name}",
                    url=repo.html_url,
                    confidence=0.95,
                    extraction_method="github_api",
                    metadata={
                        "repo_name": repo.name,
                        "stars": repo.stars,
                        "language": repo.language,
                    },
                )
                result.raw_sources.append(raw_source)

            # Analyze tech stack
            tech_stack = self.tech_analyzer.analyze(primary_repos)
            result.extracted_facts.append(
                self._create_fact(
                    fact_type="tech_stack",
                    value=tech_stack.languages,
                    confidence=0.90,
                    sources_used=[f"GitHub: {r.full_name}" for r in primary_repos],
                )
            )

            # Analyze AI signals
            ai_signal = self.ai_analyzer.analyze(primary_repos)
            if ai_signal:
                result.extracted_facts.append(
                    self._create_fact(
                        fact_type="ai_signals",
                        value={"score": ai_signal.score, "signals": ai_signal.signals},
                        confidence=0.82,
                        sources_used=[f"GitHub: {r.full_name}" for r in primary_repos],
                    )
                )

            # Analyze dependency health
            dep_health = self.dep_analyzer.analyze(github_org, primary_repos)
            if dep_health:
                result.extracted_facts.append(
                    self._create_fact(
                        fact_type="dependency_health",
                        value=dep_health.__dict__,
                        confidence=0.85,
                        sources_used=[f"GitHub: {github_org}"],
                    )
                )

            # Analyze velocity (simplified - would need actual API calls)
            velocity = self.velocity_analyzer.analyze(github_org, primary_repos)
            if velocity.contributor_count > 0:
                result.extracted_facts.append(
                    self._create_fact(
                        fact_type="engineering_velocity",
                        value=velocity.__dict__,
                        confidence=0.80,
                        sources_used=[f"GitHub: {github_org}"],
                    )
                )

            result.success = True
            self.log_info(f"Successfully gathered GitHub data for {company_name}")

        except Exception as e:
            self.log_error(f"Error gathering GitHub data: {e}")
            result.error_message = str(e)

        finally:
            result.execution_time_seconds = (datetime.now(timezone.utc) - start_time).total_seconds()

        return result
