"""GitHub organization search."""

from __future__ import annotations

import logging

from .client import GitHubClient

logger = logging.getLogger(__name__)


class GitHubOrgSearcher:
    """Search for company GitHub organizations."""

    def __init__(self, client: GitHubClient):
        self.client = client

    def search(self, company_name: str) -> str | None:
        """Search for company's GitHub organization."""
        search_queries = [
            company_name,
            company_name.split()[0] if " " in company_name else None,
            company_name.lower().replace(" ", "-"),
        ]

        for query in [q for q in search_queries if q]:
            result = self._search_org(query)
            if result:
                return result

        return None

    def _search_org(self, query: str) -> str | None:
        """API call to search for GitHub org."""
        url = f"{self.client.api_base}/search/users"
        params = {"q": f"{query} type:org", "per_page": 5}

        try:
            resp = self.client.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("items", [])
                if items:
                    return items[0].get("login")
            elif resp.status_code == 403:
                logger.warning(f"GitHub org search rate-limited for query '{query}'")
        except Exception as error:
            logger.warning(f"GitHub org search failed for query '{query}': {error}")

        return None

    def fetch_repos(self, org_name: str, max_repos: int = 100) -> list[dict]:
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

            try:
                resp = self.client.get(url, params=params, timeout=15)
                if resp.status_code != 200:
                    logger.warning(f"GitHub repo fetch failed for org '{org_name}' (status={resp.status_code})")
                    break
                batch = resp.json()
                if not batch:
                    break
                all_repos.extend(batch)
                page += 1
            except Exception as error:
                logger.warning(f"GitHub repo fetch error for org '{org_name}': {error}")
                break

        return all_repos[:max_repos]
