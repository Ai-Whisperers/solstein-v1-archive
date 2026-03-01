"""GitHub API connector wrapper for data refresh operations.

Provides a simple interface to GitHub data retrieval for refresh connectors.
"""


from typing import Any

import requests
from loguru import logger


class GitHubConnector:
    """GitHub API connector for fetching repository and commit data.

    Provides methods to retrieve:
    - User/organization repositories
    - Recent commits
    - Repository activity
    """

    def __init__(self, github_token: str | None = None):
        """Initialize GitHub connector.

        Args:
            github_token: GitHub API token (optional, increases rate limit)
        """
        from solstein.config import get_settings
        settings = get_settings()
        self.github_token = github_token or settings.github_token
        self.api_base = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Solstein-DataConnector",
        }
        if self.github_token:
            self.headers["Authorization"] = f"token {self.github_token}"

    def get_user_repositories(self, username: str, per_page: int = 30) -> list[dict[str, Any]]:
        """Fetch repositories for a GitHub user or organization.

        Args:
            username: GitHub username or organization name
            per_page: Number of results per page (max 100)

        Returns:
            List of repository data dictionaries
        """
        try:
            url = f"{self.api_base}/users/{username}/repos"
            params = {"per_page": per_page, "sort": "updated"}

            response = requests.get(url, headers=self.headers, params=params, timeout=15)

            if response.status_code == 200:
                repos = response.json()
                logger.debug(f"Fetched {len(repos)} repositories for {username}")
                return repos
            elif response.status_code == 404:
                logger.warning(f"GitHub user/org not found: {username}")
                return []
            elif response.status_code == 403:
                logger.warning(f"GitHub rate limit exceeded or access denied for {username}")
                return []
            else:
                logger.warning(f"GitHub API error ({response.status_code}) fetching repos for {username}")
                return []

        except requests.RequestException as e:
            logger.warning(f"Failed to fetch repositories for {username}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching repositories for {username}: {e}")
            return []

    def get_recent_commits(self, username: str, per_page: int = 30) -> list[dict[str, Any]]:
        """Fetch recent commits for a GitHub user.

        Note: GitHub API doesn't provide a direct "commits by user" endpoint.
        This fetches the user's public events which include push events with commit data.

        Args:
            username: GitHub username
            per_page: Number of results per page (max 100)

        Returns:
            List of commit data from public events
        """
        try:
            url = f"{self.api_base}/users/{username}/events/public"
            params = {"per_page": per_page}

            response = requests.get(url, headers=self.headers, params=params, timeout=15)

            if response.status_code == 200:
                events = response.json()
                # Filter for push events which contain commit data
                commits = []
                for event in events:
                    if event.get("type") == "PushEvent" and event.get("payload", {}).get("commits"):
                        commits.extend(event["payload"]["commits"])

                logger.debug(f"Fetched {len(commits)} commits from {username}'s public events")
                return commits[:per_page]
            elif response.status_code == 404:
                logger.warning(f"GitHub user not found: {username}")
                return []
            elif response.status_code == 403:
                logger.warning(f"GitHub rate limit exceeded or access denied for {username}")
                return []
            else:
                logger.warning(f"GitHub API error ({response.status_code}) fetching commits for {username}")
                return []

        except requests.RequestException as e:
            logger.warning(f"Failed to fetch commits for {username}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching commits for {username}: {e}")
            return []

    def get_repository_activity(self, username: str, per_page: int = 30) -> list[dict[str, Any]]:
        """Fetch recent activity for a GitHub user.

        Returns the user's public events (activity stream).

        Args:
            username: GitHub username
            per_page: Number of results per page (max 100)

        Returns:
            List of activity event dictionaries
        """
        try:
            url = f"{self.api_base}/users/{username}/events/public"
            params = {"per_page": per_page}

            response = requests.get(url, headers=self.headers, params=params, timeout=15)

            if response.status_code == 200:
                events = response.json()
                logger.debug(f"Fetched {len(events)} activity events for {username}")
                return events
            elif response.status_code == 404:
                logger.warning(f"GitHub user not found: {username}")
                return []
            elif response.status_code == 403:
                logger.warning(f"GitHub rate limit exceeded or access denied for {username}")
                return []
            else:
                logger.warning(f"GitHub API error ({response.status_code}) fetching activity for {username}")
                return []

        except requests.RequestException as e:
            logger.warning(f"Failed to fetch activity for {username}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching activity for {username}: {e}")
            return []
