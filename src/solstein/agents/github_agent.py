"""GitHub data gathering agent.

Analyzes GitHub repositories for tech stack, engineering velocity,
AI/ML signals, and code quality indicators.
"""

import asyncio
import base64
import json
import re
from collections.abc import Mapping
from datetime import datetime, timedelta, timezone

import requests

from ..domain.models import DataSourceType
from .base_agent import AgentTaskResult, BaseDataGatheringAgent
from .resilience import GITHUB_RETRY_CONFIG, CircuitBreaker, call_with_retry


class GitHubAgent(BaseDataGatheringAgent):
    """Agent for gathering data from GitHub."""

    def __init__(self, github_token: str | None = None):
        """Initialize GitHub agent.

        Args:
            github_token: GitHub API token (optional, increases rate limit)
        """
        super().__init__("GitHubAgent", DataSourceType.GITHUB)
        from solstein.config import get_settings

        settings = get_settings()
        self.github_token = github_token or settings.github_token
        self.api_base = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Solstein-AI",
        }
        if self.github_token:
            self.headers["Authorization"] = f"token {self.github_token}"

        self.circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60.0, name="GitHubAPI")

    def _request_headers(self, unauthenticated: bool = False) -> dict[str, str]:
        headers = dict(self.headers)
        if unauthenticated:
            headers.pop("Authorization", None)
        return headers

    def _get(
        self,
        url: str,
        *,
        params: Mapping[str, str | int | float] | None = None,
        timeout: float = 15,
    ) -> requests.Response:
        resp = requests.get(url, headers=self._request_headers(), params=params, timeout=timeout)
        if resp.status_code == 401 and "Authorization" in self.headers:
            resp = requests.get(
                url,
                headers=self._request_headers(unauthenticated=True),
                params=params,
                timeout=timeout,
            )
        return resp

    async def gather(self, company_name: str, context: dict[str, object]) -> AgentTaskResult:
        """Gather GitHub data for a company."""
        start_time = datetime.now(timezone.utc)
        result = AgentTaskResult(
            agent_name=self.agent_name,
            source_type=self.source_type,
            success=False,
        )

        try:
            self.log_info(f"Starting GitHub research for {company_name}")

            known_github_org = context.get("known_github_org")
            github_org = known_github_org if isinstance(known_github_org, str) and known_github_org else None
            if github_org is None:
                github_org = await self._search_github_org(company_name)
                if github_org is None:
                    self.log_warning(f"No GitHub org found for {company_name}")
                    result.coverage_gaps.append("GitHub organization not found")
                    result.success = False
                    result.error_message = "No GitHub organization found"
                    result.execution_time_seconds = (datetime.now(timezone.utc) - start_time).total_seconds()
                    return result

            repos = await self._fetch_org_repos(github_org)
            if not repos:
                self.log_warning(f"No repos found in {github_org}")
                result.coverage_gaps.append("No public repositories available")
                result.success = False
                result.error_message = f"No repositories found in {github_org}"
                result.execution_time_seconds = (datetime.now(timezone.utc) - start_time).total_seconds()
                return result

            def _stars(repo: dict[str, object]) -> int:
                value = repo.get("stargazers_count")
                return value if isinstance(value, int) else 0

            primary_repos = sorted(repos, key=_stars, reverse=True)[:5]
            self.log_info(f"Analyzing {len(primary_repos)} repos for {company_name}")

            for repo in primary_repos:
                html_url = repo.get("html_url")
                raw_source = self._create_raw_source(
                    raw_content=repo,
                    source_name=f"GitHub: {repo.get('full_name', 'unknown')}",
                    url=html_url if isinstance(html_url, str) else None,
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
                    sources_used=[f"GitHub: {repo.get('full_name')}" for repo in primary_repos],
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

            velocity_trend = await self._get_commit_velocity_trend(github_org)
            if velocity_trend is not None:
                result.extracted_facts.append(
                    self._create_fact(
                        fact_type="engineering_velocity_trend",
                        value=velocity_trend,
                        confidence=0.80,
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
                        sources_used=[f"GitHub: {repo.get('full_name')}" for repo in primary_repos],
                    )
                )

            dependency_health = await self._get_dependency_health(github_org, primary_repos)
            if dependency_health is not None:
                result.extracted_facts.append(
                    self._create_fact(
                        fact_type="dependency_health",
                        value=dependency_health,
                        confidence=0.85,
                        sources_used=[f"GitHub: {github_org}"],
                    )
                )

            result.success = True
            self.log_info(f"Successfully gathered GitHub data for {company_name}")

        except Exception as e:
            self.log_error(f"Error gathering GitHub data: {e}")
            result.error_message = str(e)
            result.success = False

        finally:
            result.execution_time_seconds = (datetime.now(timezone.utc) - start_time).total_seconds()

        return result

    async def _get_dependency_health(self, org_name: str, repos: list[dict[str, object]]) -> dict[str, object] | None:
        try:
            return await call_with_retry(
                asyncio.to_thread,
                self._api_dependency_health,
                org_name,
                repos,
                retry_config=GITHUB_RETRY_CONFIG,
                circuit_breaker=self.circuit_breaker,
                name=f"dependency_health[{org_name}]",
            )
        except Exception as e:
            self.log_error(f"Error computing dependency health: {e}")
            return None

    def _api_dependency_health(self, org_name: str, repos: list[dict[str, object]]) -> dict[str, object] | None:
        latest_cache: dict[tuple[str, str], str | None] = {}
        osv_cache: dict[tuple[str, str, str], list[dict[str, object]]] = {}

        python_deps: dict[str, dict[str, object]] = {}
        js_deps: dict[str, dict[str, object]] = {}

        for repo in repos[:5]:
            repo_name = repo.get("name")
            if not isinstance(repo_name, str) or not repo_name:
                continue

            reqs_text = self._fetch_repo_text_file(org_name, repo_name, "requirements.txt")
            if reqs_text:
                for dep in self._parse_requirements_txt(reqs_text):
                    name = dep.get("name")
                    if isinstance(name, str) and name and name not in python_deps:
                        python_deps[name] = dep

            pkg_text = self._fetch_repo_text_file(org_name, repo_name, "package.json")
            if pkg_text:
                for name, spec in self._parse_package_json_deps(pkg_text).items():
                    if name not in js_deps:
                        js_deps[name] = {"name": name, "spec": spec}

        python_outdated, python_vulns = self._analyze_dep_set(
            ecosystem="PyPI",
            deps=python_deps,
            latest_cache=latest_cache,
            osv_cache=osv_cache,
        )
        js_outdated, js_vulns = self._analyze_dep_set(
            ecosystem="npm",
            deps=js_deps,
            latest_cache=latest_cache,
            osv_cache=osv_cache,
        )

        if not python_deps and not js_deps:
            return None

        high_vuln_count = sum(1 for v in [*python_vulns, *js_vulns] if v.get("severity") in {"HIGH", "CRITICAL"})
        outdated_count = len(python_outdated) + len(js_outdated)

        score = 10
        score -= min(5, outdated_count)
        score -= min(6, high_vuln_count * 2)
        score = max(0, min(10, score))

        signal = f"{outdated_count} outdated dependencies"
        if high_vuln_count:
            signal += f", {high_vuln_count} high/critical vulnerabilities"

        return {
            "python": {
                "dependencies_parsed": len(python_deps),
                "outdated": python_outdated,
                "vulnerabilities": python_vulns,
            },
            "javascript": {
                "dependencies_parsed": len(js_deps),
                "outdated": js_outdated,
                "vulnerabilities": js_vulns,
            },
            "health_score_0_to_10": score,
            "signal": signal,
        }

    def _fetch_repo_text_file(self, org_name: str, repo_name: str, path: str) -> str | None:
        url = f"{self.api_base}/repos/{org_name}/{repo_name}/contents/{path}"
        try:
            resp = self._get(url, timeout=10)
            if resp.status_code == 404:
                return None
            if resp.status_code != 200:
                self.log_warning(f"GitHub contents API error {resp.status_code} for {org_name}/{repo_name}:{path}")
                return None

            data = resp.json()
            content = data.get("content")
            encoding = data.get("encoding")
            if not isinstance(content, str) or encoding != "base64":
                return None
            raw = base64.b64decode(content.encode("utf-8"))
            return raw.decode("utf-8", errors="replace")
        except Exception as e:
            self.log_warning(f"Error fetching {org_name}/{repo_name}:{path}: {e}")
            return None

    _REQ_LINE_RE = re.compile(r"^(?P<name>[A-Za-z0-9_.-]+)(?:\[[^\]]+\])?\s*(?P<op>==|>=)\s*(?P<ver>[0-9][^;\s]*)")

    def _parse_requirements_txt(self, text: str) -> list[dict[str, object]]:
        deps: list[dict[str, object]] = []
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

            name = m.group("name")
            op = m.group("op")
            ver = m.group("ver")
            deps.append(
                {
                    "name": name,
                    "pinned_version": ver if op == "==" else None,
                    "min_version": ver if op == ">=" else None,
                    "specifier": f"{op}{ver}",
                }
            )
        return deps

    def _parse_package_json_deps(self, text: str) -> dict[str, str]:
        try:
            data = json.loads(text)
        except Exception:
            return {}
        if not isinstance(data, dict):
            return {}

        deps: dict[str, str] = {}
        for section in ("dependencies", "devDependencies"):
            raw = data.get(section)
            if not isinstance(raw, dict):
                continue
            for name, spec in raw.items():
                if isinstance(name, str) and isinstance(spec, str) and name and spec:
                    deps[name] = spec
        return deps

    def _analyze_dep_set(
        self,
        *,
        ecosystem: str,
        deps: dict[str, dict[str, object]],
        latest_cache: dict[tuple[str, str], str | None],
        osv_cache: dict[tuple[str, str, str], list[dict[str, object]]],
    ) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
        outdated: list[dict[str, object]] = []
        vulns: list[dict[str, object]] = []

        for name, meta in deps.items():
            current = None
            if ecosystem == "PyPI":
                pinned = meta.get("pinned_version")
                current = pinned if isinstance(pinned, str) and pinned else None
            else:
                spec = meta.get("spec")
                if isinstance(spec, str):
                    current = self._extract_js_version(spec)

            latest = self._get_latest_version(ecosystem, name, latest_cache)
            if current and latest and self._is_outdated(current, latest):
                outdated.append(
                    {
                        "name": name,
                        "current_version": current,
                        "latest_version": latest,
                    }
                )

            if current:
                vulns.extend(self._get_osv_vulns(ecosystem, name, current, osv_cache))

        return outdated, vulns

    def _get_latest_version(self, ecosystem: str, name: str, cache: dict[tuple[str, str], str | None]) -> str | None:
        key = (ecosystem, name)
        if key in cache:
            return cache[key]

        latest: str | None = None
        try:
            if ecosystem == "PyPI":
                resp = requests.get(f"https://pypi.org/pypi/{name}/json", timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    info = data.get("info", {})
                    version = info.get("version")
                    latest = version if isinstance(version, str) else None
            elif ecosystem == "npm":
                resp = requests.get(f"https://registry.npmjs.org/{name}", timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    dist_tags = data.get("dist-tags", {})
                    version = dist_tags.get("latest")
                    latest = version if isinstance(version, str) else None
        except Exception as e:
            self.log_warning(f"Error looking up latest version for {ecosystem}:{name}: {e}")

        cache[key] = latest
        return latest

    def _get_osv_vulns(
        self,
        ecosystem: str,
        name: str,
        version: str,
        cache: dict[tuple[str, str, str], list[dict[str, object]]],
    ) -> list[dict[str, object]]:
        key = (ecosystem, name, version)
        if key in cache:
            return cache[key]

        results: list[dict[str, object]] = []
        try:
            payload = {"package": {"name": name, "ecosystem": ecosystem}, "version": version}
            resp = requests.post("https://api.osv.dev/v1/query", json=payload, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                vulns = data.get("vulns")
                if isinstance(vulns, list):
                    for v in vulns:
                        if not isinstance(v, dict):
                            continue
                        severity = self._osv_severity(v)
                        results.append(
                            {
                                "ecosystem": ecosystem,
                                "name": name,
                                "version": version,
                                "id": v.get("id"),
                                "summary": v.get("summary"),
                                "severity": severity,
                            }
                        )
        except Exception as e:
            self.log_warning(f"Error querying OSV for {ecosystem}:{name}@{version}: {e}")

        cache[key] = results
        return results

    def _osv_severity(self, vuln: dict[str, object]) -> str | None:
        severity = vuln.get("severity")
        if not isinstance(severity, list):
            return None

        best: float | None = None
        for entry in severity:
            if not isinstance(entry, dict):
                continue
            if entry.get("type") not in {"CVSS_V3", "CVSS_V2"}:
                continue
            score = entry.get("score")
            if not isinstance(score, str):
                continue
            try:
                numeric = float(score)
            except ValueError:
                continue
            best = numeric if best is None else max(best, numeric)

        if best is None:
            return None
        if best >= 9.0:
            return "CRITICAL"
        if best >= 7.0:
            return "HIGH"
        if best >= 4.0:
            return "MEDIUM"
        if best > 0:
            return "LOW"
        return None

    _SEMVER_RE = re.compile(r"^(?P<maj>\d+)\.(?P<min>\d+)(?:\.(?P<pat>\d+))?")

    def _is_outdated(self, current: str, latest: str) -> bool:
        c = self._parse_semver(current)
        lat = self._parse_semver(latest)
        if not c or not lat:
            return False
        cmaj, cmin, _ = c
        lmaj, lmin, _ = lat
        if lmaj != cmaj:
            return True
        return (lmin - cmin) > 3

    def _parse_semver(self, version: str) -> tuple[int, int, int] | None:
        m = self._SEMVER_RE.match(version.strip())
        if not m:
            return None
        maj = int(m.group("maj"))
        min_ = int(m.group("min"))
        pat = int(m.group("pat") or 0)
        return (maj, min_, pat)

    def _extract_js_version(self, spec: str) -> str | None:
        cleaned = spec.strip()
        cleaned = cleaned.lstrip("^~<>= ")
        m = self._SEMVER_RE.match(cleaned)
        return m.group(0) if m else None

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

            resp = self._get(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("items", [])
                if items:
                    org_login = items[0].get("login")
                    self.log_info(f"Found GitHub org: {org_login}")
                    return org_login
            elif resp.status_code == 403:
                self.log_warning("GitHub API rate limited")
            elif resp.status_code == 401:
                self.log_warning("GitHub API unauthorized")
        except requests.Timeout:
            self.log_warning(f"Timeout searching for org: {query}")
        except Exception as e:
            self.log_warning(f"Error searching org: {e}")

        return None

    async def _fetch_org_repos(self, org_name: str) -> list[dict[str, object]]:
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

    def _api_fetch_repos(self, org_name: str) -> list[dict[str, object]]:
        """API call to fetch org repos."""
        try:
            url = f"{self.api_base}/orgs/{org_name}/repos"
            params = {
                "per_page": 100,
                "sort": "stars",
                "direction": "desc",
            }

            resp = self._get(url, params=params, timeout=15)
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

    def _api_count_commits(self, org_name: str, repos: list[dict[str, object]]) -> int | None:
        """API call to count commits."""
        total_commits = 0
        thirty_days_ago = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()

        for repo in repos:
            try:
                url = f"{self.api_base}/repos/{org_name}/{repo['name']}/commits"
                params = {
                    "since": thirty_days_ago,
                    "per_page": 100,
                }

                resp = self._get(url, params=params, timeout=10)
                if resp.status_code == 200:
                    commits = resp.json()
                    total_commits += len(commits)
            except Exception as e:
                self.log_warning(f"Error counting commits: {e}")

        return total_commits if total_commits > 0 else None

    async def _get_commit_velocity_trend(self, org_name: str) -> dict[str, object] | None:
        try:
            repos = await self._fetch_org_repos(org_name)
            if not repos:
                return None

            return await call_with_retry(
                asyncio.to_thread,
                self._api_commit_velocity_trend,
                org_name,
                repos[:5],
                retry_config=GITHUB_RETRY_CONFIG,
                circuit_breaker=self.circuit_breaker,
                name=f"commit_velocity_trend[{org_name}]",
            )
        except Exception as e:
            self.log_error(f"Error computing commit velocity trend: {e}")
            return None

    def _api_commit_velocity_trend(self, org_name: str, repos: list[dict[str, object]]) -> dict[str, object] | None:
        now = datetime.now(timezone.utc)
        recent_since = (now - timedelta(days=14)).isoformat()
        prev_since = (now - timedelta(days=28)).isoformat()
        prev_until = (now - timedelta(days=14)).isoformat()

        recent_count = 0
        prev_count = 0

        for repo in repos:
            try:
                repo_name = repo.get("name")
                if not repo_name:
                    continue

                url = f"{self.api_base}/repos/{org_name}/{repo_name}/commits"

                resp_recent = self._get(url, params={"since": recent_since, "per_page": 100}, timeout=10)
                if resp_recent.status_code == 200:
                    recent_count += len(resp_recent.json())

                resp_prev = self._get(
                    url,
                    params={"since": prev_since, "until": prev_until, "per_page": 100},
                    timeout=10,
                )
                if resp_prev.status_code == 200:
                    prev_count += len(resp_prev.json())
            except Exception as e:
                self.log_warning(f"Error computing trend for repo {repo.get('name')}: {e}")

        if recent_count == 0 and prev_count == 0:
            return None

        trend_ratio = None
        if prev_count > 0:
            trend_ratio = (recent_count - prev_count) / prev_count

        direction = "flat"
        if prev_count == 0 and recent_count > 0 or prev_count > 0 and recent_count > prev_count:
            direction = "up"
        elif prev_count > 0 and recent_count < prev_count:
            direction = "down"

        return {
            "recent_14d": recent_count,
            "previous_14d": prev_count,
            "trend_ratio": trend_ratio,
            "direction": direction,
        }

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

    def _api_count_contributors(self, org_name: str, repos: list[dict[str, object]]) -> int | None:
        """API call to count contributors."""
        total_contributors = set()

        for repo in repos:
            try:
                url = f"{self.api_base}/repos/{org_name}/{repo['name']}/contributors"
                params = {"per_page": 100}

                resp = self._get(url, params=params, timeout=10)
                if resp.status_code == 200:
                    contributors = resp.json()
                    for contrib in contributors:
                        total_contributors.add(contrib.get("login"))
            except Exception as e:
                self.log_warning(f"Error in {repo['name']}: {e}")

        return len(total_contributors) if total_contributors else None

    def _extract_tech_stack(self, repos: list[dict[str, object]]) -> list[str]:
        """Extract languages from repos."""
        languages = set()
        for repo in repos:
            if repo.get("language"):
                languages.add(repo["language"])
        return sorted(list(languages))

    def _analyze_ai_signals(self, repos: list[dict[str, object]]) -> dict[str, object] | None:
        """Analyze repos for AI/ML signals."""
        return {
            "has_ml_languages": any(repo.get("language") in ["Python", "Rust", "Go"] for repo in repos),
            "active_development": True,
        }
