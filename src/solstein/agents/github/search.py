"""GitHub organization search.

STORY-133: Migrated to async — all methods now use await for HTTP calls.
"""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any

from solstein.config import get_settings
from solstein.infrastructure.cache import get_cache

from .client import GitHubClient

logger = logging.getLogger(__name__)


class GitHubOrgSearcher:
    """Search for company GitHub organizations."""

    def __init__(self, client: GitHubClient):
        self.client = client
        self.cache = get_cache()
        self.cache_ttl = get_settings().search_cache_ttl

    def _cache_key(self, prefix: str, **payload: Any) -> str:
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
        return f"github:{prefix}:{digest}"

    async def _get_json(self, url: str, *, params: dict[str, Any], cache_key: str) -> tuple[int, Any]:
        cached = await self.cache.get(cache_key)
        if isinstance(cached, dict) and "status_code" in cached and "data" in cached:
            return int(cached["status_code"]), cached["data"]

        resp = await self.client.get(url, params=params)
        if resp.status_code == 200:
            payload = {"status_code": resp.status_code, "data": resp.json()}
            await self.cache.set(cache_key, payload, ttl=self.cache_ttl)
            return resp.status_code, payload["data"]

        return resp.status_code, None

    async def search(self, company_name: str) -> str | None:
        """Search for company's GitHub organization."""
        search_queries = [
            company_name,
            company_name.split()[0] if " " in company_name else None,
            company_name.lower().replace(" ", "-"),
        ]

        for query in [q for q in search_queries if q]:
            result = await self._search_org(query)
            if result:
                return result

        return None

    async def _search_org(self, query: str) -> str | None:
        """API call to search for GitHub org."""
        url = f"{self.client.api_base}/search/users"
        params = {"q": f"{query} type:org", "per_page": 5}
        cache_key = self._cache_key("org-search", query=query, params=params)

        try:
            status_code, data = await self._get_json(url, params=params, cache_key=cache_key)
            if status_code == 200 and isinstance(data, dict):
                items = data.get("items", [])
                if items:
                    return items[0].get("login")
            elif status_code == 403:
                logger.warning(f"GitHub org search rate-limited for query '{query}'")
        except Exception as error:
            logger.warning(f"GitHub org search failed for query '{query}': {error}")

        return None

    async def fetch_repos(self, org_name: str, max_repos: int = 100) -> list[dict]:
        """Fetch repos from GitHub org, paginating until max_repos is reached."""
        url = f"{self.client.api_base}/orgs/{org_name}/repos"
        all_repos: list[dict] = []
        page = 1

        while len(all_repos) < max_repos:
            per_page = min(100, max_repos - len(all_repos))
            params = {
                "per_page": per_page,
                "page": page,
                "sort": "stars",
                "direction": "desc",
            }
            cache_key = self._cache_key("repos", org=org_name, params=params)

            try:
                status_code, data = await self._get_json(url, params=params, cache_key=cache_key)
                if status_code != 200:
                    logger.warning(f"GitHub repo fetch failed for org '{org_name}' (status={status_code})")
                    break
                batch = data if isinstance(data, list) else []
                if not batch:
                    break
                all_repos.extend(batch)
                page += 1
            except Exception as error:
                logger.warning(f"GitHub repo fetch error for org '{org_name}': {error}")
                break

        return all_repos[:max_repos]

    async def fetch_repo_issues(
        self,
        org_name: str,
        repo_name: str,
        *,
        state: str = "open",
        max_issues: int = 20,
    ) -> list[dict[str, Any]]:
        """Fetch GitHub issues for a repository, excluding pull requests."""
        url = f"{self.client.api_base}/repos/{org_name}/{repo_name}/issues"
        params = {
            "state": state,
            "per_page": min(100, max_issues),
            "page": 1,
            "sort": "updated",
            "direction": "desc",
        }
        cache_key = self._cache_key("issues", org=org_name, repo=repo_name, params=params)

        try:
            status_code, data = await self._get_json(url, params=params, cache_key=cache_key)
            if status_code != 200:
                logger.warning(
                    "GitHub issue fetch failed for repo '%s/%s' (status=%s)",
                    org_name,
                    repo_name,
                    status_code,
                )
                return []
            items = data if isinstance(data, list) else []
            issues = [item for item in items if isinstance(item, dict) and "pull_request" not in item]
            return issues[:max_issues]
        except Exception as error:
            logger.warning(f"GitHub issue fetch error for repo '{org_name}/{repo_name}': {error}")
            return []
