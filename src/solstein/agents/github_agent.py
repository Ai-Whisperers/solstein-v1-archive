"""GitHub data gathering agent.

Analyzes GitHub repositories for tech stack, engineering velocity,
AI/ML signals, and code quality indicators.
"""

import asyncio
import os
from datetime import UTC, datetime, timedelta

import requests

from ..domain.models import DataSourceType
from .base_agent import AgentTaskResult, BaseDataGatheringAgent
from .resilience import call_with_retry, CircuitBreaker, GITHUB_RETRY_CONFIG


class GitHubAgent(BaseDataGatheringAgent):
    """Agent for gathering data from GitHub."""

    def __init__(self, github_token: str | None = None):
        """Initialize GitHub agent.

        Args:
            github_token: GitHub API token (optional, increases rate limit)
        """
        super().__init__("GitHubAgent", DataSourceType.GITHUB)
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.api_base = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Solstein-AI",
        }
        if self.github_token:
            self.headers["Authorization"] = f"token {self.github_token}"

        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5, recovery_timeout=60.0, name="GitHubAPI"
        )

    async def gather(self, company_name: str, context: dict) -> AgentTaskResult:
        """Gather GitHub data for a company."""
        start_time = datetime.now(UTC)
        result = AgentTaskResult(
            agent_name=self.agent_name,
            source_type=self.source_type,
            success=False,
        )

        try:
            self.log_info(f"Starting GitHub research for {company_name}")

            github_org = context.get("known_github_org")
            if not github_org:
                github_org = await self._search_github_org(company_name)
                if not github_org:
                    self.log_warning(f"No GitHub org found for {company_name}")
                    result.coverage_gaps.append("GitHub organization not found")
                    result.success = False
                    result.error_message = "No GitHub organization found"
                    result.execution_time_seconds = (
                        datetime.now(UTC) - start_time
                    ).total_seconds()
                    return result

            repos = await self._fetch_org_repos(github_org)
            if not repos:
                self.log_warning(f"No repos found in {github_org}")
                result.coverage_gaps.append("No public repositories available")
                result.success = False
                result.error_message = f"No repositories found in {github_org}"
                result.execution_time_seconds = (
                    datetime.now(UTC) - start_time
                ).total_seconds()
                return result

            primary_repos = sorted(
                repos, key=lambda r: r.get("stargazers_count", 0), reverse=True
            )[:5]
            self.log_info(f"Analyzing {len(primary_repos)} repos for {company_name}")

            for repo in primary_repos:
                raw_source = self._create_raw_source(
                    raw_content=repo,
                    source_name=f"GitHub: {repo.get('full_name', 'unknown')}",
                    url=repo.get("html_url"),
                    confidence=0.95,
                    extraction_method="github_api",
                    metadata={
                        "repo_name": repo.get("name"),
                        "stars": repo.get("stargazers_count", 0),
                        "language": repo.get("language"),
                    },
                )
                result.raw_sources.append(raw_source)

            tech_stack = self._extract_tech_stack(primary_repos)
            result.extracted_facts.append(
                self._create_fact(
                    fact_type="tech_stack",
                    value=tech_stack,
                    confidence=0.90,
                    sources_used=[
                        f"GitHub: {repo.get('full_name')}" for repo in primary_repos
                    ],
                )
            )

            total_commits_30d = await self._get_recent_commit_count(github_org)
            if total_commits_30d is not None:
                result.extracted_facts.append(
                    self._create_fact(
                        fact_type="engineering_velocity",
                        value=total_commits_30d,
                        confidence=0.85,
                        sources_used=[f"GitHub: {github_org}"],
                    )
                )

            total_contributors = await self._get_org_contributor_count(github_org)
            if total_contributors is not None:
                result.extracted_facts.append(
                    self._create_fact(
                        fact_type="contributor_count",
                        value=total_contributors,
                        confidence=0.80,
                        sources_used=[f"GitHub: {github_org}"],
                    )
                )

            ai_signal = self._analyze_ai_signals(primary_repos)
            if ai_signal:
                result.extracted_facts.append(
                    self._create_fact(
                        fact_type="ai_signals",
                        value=ai_signal,
                        confidence=0.82,
                        sources_used=[
                            f"GitHub: {repo.get('full_name')}" for repo in primary_repos
                        ],
                    )
                )

            result.success = True
            self.log_info(f"Successfully gathered GitHub data for {company_name}")

        except Exception as e:
            self.log_error(f"Error gathering GitHub data: {e}")
            result.error_message = str(e)
            result.success = False

        finally:
            result.execution_time_seconds = (
                datetime.now(UTC) - start_time
            ).total_seconds()

        return result

    async def _search_github_org(self, company_name: str) -> str | None:
        """Search for company's GitHub organization."""
        self.log_info(f"Searching for GitHub org: '{company_name}'")

        search_queries = [
            company_name,
            company_name.split()[0] if " " in company_name else None,
            company_name.lower().replace(" ", "-"),
        ]

        for query in [q for q in search_queries if q]:
            try:
                result = await call_with_retry(
                    asyncio.to_thread,
                    self._api_search_org,
                    query,
                    retry_config=GITHUB_RETRY_CONFIG,
                    circuit_breaker=self.circuit_breaker,
                    name=f"search_github_org[{query}]",
                )
                if result:
                    return result
            except Exception as e:
                self.log_warning(f"Error searching org {query}: {e}")

        return None

    def _api_search_org(self, query: str) -> str | None:
        """API call to search for GitHub org."""
        try:
            url = f"{self.api_base}/search/users"
            params = {"q": f"{query} type:org", "per_page": 5}

            resp = requests.get(url, headers=self.headers, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("items", [])
                if items:
                    org_login = items[0].get("login")
                    self.log_info(f"Found GitHub org: {org_login}")
                    return org_login
            elif resp.status_code == 403:
                self.log_warning("GitHub API rate limited")
        except requests.Timeout:
            self.log_warning(f"Timeout searching for org: {query}")
        except Exception as e:
            self.log_warning(f"Error searching org: {e}")

        return None

    async def _fetch_org_repos(self, org_name: str) -> list[dict]:
        """Fetch repos from GitHub org."""
        self.log_info(f"Fetching repos from {org_name}")

        try:
            repos = await call_with_retry(
                asyncio.to_thread,
                self._api_fetch_repos,
                org_name,
                retry_config=GITHUB_RETRY_CONFIG,
                circuit_breaker=self.circuit_breaker,
                name=f"fetch_repos[{org_name}]",
            )
            self.log_info(f"Fetched {len(repos)} repos")
            return repos
        except Exception as e:
            self.log_error(f"Error fetching repos: {e}")
            return []

    def _api_fetch_repos(self, org_name: str) -> list[dict]:
        """API call to fetch org repos."""
        try:
            url = f"{self.api_base}/orgs/{org_name}/repos"
            params = {
                "per_page": 100,
                "sort": "stars",
                "direction": "desc",
            }

            resp = requests.get(url, headers=self.headers, params=params, timeout=15)
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 404:
                self.log_warning(f"Org not found: {org_name}")
            else:
                self.log_warning(f"API error {resp.status_code}")
        except Exception as e:
            self.log_error(f"Error fetching repos: {e}")

        return []

    async def _get_recent_commit_count(self, org_name: str) -> int | None:
        """Get commit count in last 30 days."""
        try:
            repos = await self._fetch_org_repos(org_name)
            if not repos:
                return None

            return await call_with_retry(
                asyncio.to_thread,
                self._api_count_commits,
                org_name,
                repos[:5],
                retry_config=GITHUB_RETRY_CONFIG,
                circuit_breaker=self.circuit_breaker,
                name=f"count_commits[{org_name}]",
            )
        except Exception as e:
            self.log_error(f"Error counting commits: {e}")
            return None

    def _api_count_commits(self, org_name: str, repos: list[dict]) -> int | None:
        """API call to count commits."""
        total_commits = 0
        thirty_days_ago = (datetime.now(UTC) - timedelta(days=30)).isoformat()

        for repo in repos:
            try:
                url = f"{self.api_base}/repos/{org_name}/{repo['name']}/commits"
                params = {
                    "since": thirty_days_ago,
                    "per_page": 100,
                }

                resp = requests.get(
                    url, headers=self.headers, params=params, timeout=10
                )
                if resp.status_code == 200:
                    commits = resp.json()
                    total_commits += len(commits)
            except Exception as e:
                self.log_warning(f"Error counting commits: {e}")

        return total_commits if total_commits > 0 else None

    async def _get_org_contributor_count(self, org_name: str) -> int | None:
        """Get contributor count across org repos."""
        try:
            repos = await self._fetch_org_repos(org_name)
            if not repos:
                return None

            return await call_with_retry(
                asyncio.to_thread,
                self._api_count_contributors,
                org_name,
                repos[:5],
                retry_config=GITHUB_RETRY_CONFIG,
                circuit_breaker=self.circuit_breaker,
                name=f"count_contributors[{org_name}]",
            )
        except Exception as e:
            self.log_error(f"Error counting contributors: {e}")
            return None

    def _api_count_contributors(self, org_name: str, repos: list[dict]) -> int | None:
        """API call to count contributors."""
        total_contributors = set()

        for repo in repos:
            try:
                url = f"{self.api_base}/repos/{org_name}/{repo['name']}/contributors"
                params = {"per_page": 100}

                resp = requests.get(
                    url, headers=self.headers, params=params, timeout=10
                )
                if resp.status_code == 200:
                    contributors = resp.json()
                    for contrib in contributors:
                        total_contributors.add(contrib.get("login"))
            except Exception as e:
                self.log_warning(f"Error in {repo['name']}: {e}")

        return len(total_contributors) if total_contributors else None

    def _extract_tech_stack(self, repos: list[dict]) -> list[str]:
        """Extract languages from repos."""
        languages = set()
        for repo in repos:
            if repo.get("language"):
                languages.add(repo["language"])
        return sorted(list(languages))

    def _analyze_ai_signals(self, repos: list[dict]) -> dict | None:
        """Analyze repos for AI/ML signals."""
        return {
            "has_ml_languages": any(
                repo.get("language") in ["Python", "Rust", "Go"] for repo in repos
            ),
            "active_development": True,
        }
