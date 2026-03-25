from datetime import datetime
from typing import Any

from loguru import logger
from sqlalchemy import text

from solstein.data.connectors.github_connector import GitHubConnector
from solstein.infrastructure.database import DatabaseManager
from solstein.infrastructure.refresh import BaseRefreshConnector


class GitHubRefreshConnector(BaseRefreshConnector):
    """GitHub refresh connector for technical and development data updates."""

    def __init__(self, db_manager: DatabaseManager):
        super().__init__(
            source_name="github",
            source_type="technical_signal",
            db_manager=db_manager,
            confidence=0.85,  # GitHub is authoritative for technical data
        )
        self.github_connector: GitHubConnector = GitHubConnector()

    async def fetch_facts(
        self,
        company_ids: list[str],
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch technical facts from GitHub repositories."""
        logger.info(f"Fetching GitHub facts for {len(company_ids)} companies")
        facts = []

        for company_id in company_ids:
            try:
                # Extract GitHub username from company_id (assuming format: username-org)
                github_username = company_id

                try:
                    # Fetch repository data
                    repos = self.github_connector.get_user_repositories(github_username)

                    # Fetch recent commits
                    commits = self.github_connector.get_recent_commits(github_username)

                    # Fetch repository activity
                    activity = self.github_connector.get_repository_activity(github_username)

                    # Convert all data to facts
                    for repo in repos:
                        fact = self._convert_repo_to_fact(repo)
                        facts.append(fact)

                    for commit in commits:
                        fact = self._convert_commit_to_fact(commit)
                        facts.append(fact)

                    for activity_item in activity:
                        fact = self._convert_activity_to_fact(activity_item)
                        facts.append(fact)

                except Exception as e:
                    logger.warning(f"Failed to fetch GitHub data for {github_username}: {e}")
                    continue

            except Exception as e:
                logger.error(f"Failed to process company {company_id}: {e}")
                continue

        return facts

    def _convert_repo_to_fact(self, repo: dict[str, Any]) -> dict[str, Any]:
        """Convert GitHub repository data to fact dictionary."""
        # Extract repository metrics
        repo_metrics = {
            "repo_name": repo.get("name"),
            "full_name": repo.get("full_name"),
            "description": repo.get("description"),
            "language": repo.get("language"),
            "stargazers_count": repo.get("stargazers_count"),
            "forks_count": repo.get("forks_count"),
            "open_issues_count": repo.get("open_issues_count"),
            "created_at": repo.get("created_at"),
            "updated_at": repo.get("updated_at"),
            "pushed_at": repo.get("pushed_at"),
        }

        # Create fact data
        fact_data = {
            "company_id": repo.get("owner", {}).get("login"),
            "fact_type": "github_repository",
            "value": repo_metrics,
            "confidence": 0.85,
            "extracted_at": datetime.now(),
            "source": "github",
            "metadata": {
                "repo_name": repo.get("name"),
                "full_name": repo.get("full_name"),
                "language": repo.get("language"),
                "stargazers_count": repo.get("stargazers_count"),
                "forks_count": repo.get("forks_count"),
                "open_issues_count": repo.get("open_issues_count"),
                "created_at": repo.get("created_at"),
                "updated_at": repo.get("updated_at"),
                "pushed_at": repo.get("pushed_at"),
            },
        }

        return fact_data

    def _convert_commit_to_fact(self, commit: dict[str, Any]) -> dict[str, Any]:
        """Convert GitHub commit data to fact dictionary."""
        # Extract commit metrics
        commit_metrics = {
            "sha": commit.get("sha"),
            "message": commit.get("commit", {}).get("message"),
            "author": commit.get("commit", {}).get("author"),
            "committer": commit.get("commit", {}).get("committer"),
            "committed_at": commit.get("commit", {}).get("author", {}).get("date"),
            "stats": commit.get("stats"),
            "files": commit.get("files"),
        }

        # Create fact data
        fact_data = {
            "company_id": commit.get("author", {}).get("login"),
            "fact_type": "github_commit",
            "value": commit_metrics,
            "confidence": 0.85,
            "extracted_at": datetime.now(),
            "source": "github",
            "metadata": {
                "sha": commit.get("sha"),
                "message": commit.get("commit", {}).get("message"),
                "author": commit.get("commit", {}).get("author"),
                "committer": commit.get("commit", {}).get("committer"),
                "committed_at": commit.get("commit", {}).get("author", {}).get("date"),
                "stats": commit.get("stats"),
                "files": commit.get("files"),
            },
        }

        return fact_data

    def _convert_activity_to_fact(self, activity: dict[str, Any]) -> dict[str, Any]:
        """Convert GitHub activity data to fact dictionary."""
        # Extract activity metrics
        activity_metrics = {
            "type": activity.get("type"),
            "repo": activity.get("repo", {}).get("name"),
            "payload": activity.get("payload"),
            "created_at": activity.get("created_at"),
            "org": activity.get("org", {}).get("login"),
            "actor": activity.get("actor", {}).get("login"),
        }

        # Create fact data
        fact_data = {
            "company_id": activity.get("actor", {}).get("login"),
            "fact_type": "github_activity",
            "value": activity_metrics,
            "confidence": 0.85,
            "extracted_at": datetime.now(),
            "source": "github",
            "metadata": {
                "type": activity.get("type"),
                "repo": activity.get("repo", {}).get("name"),
                "payload": activity.get("payload"),
                "created_at": activity.get("created_at"),
                "org": activity.get("org", {}).get("login"),
                "actor": activity.get("actor", {}).get("login"),
            },
        }

        return fact_data

    async def _filter_delta(self, facts: list[dict[str, Any]], since: datetime) -> list[dict[str, Any]]:
        """Filter GitHub facts to only return changed data since last refresh."""
        filtered_facts = []

        for fact in facts:
            # Check if date fields are newer than last refresh
            value = fact["value"]
            date_fields = [
                value.get("created_at"),
                value.get("updated_at"),
                value.get("pushed_at"),
                value.get("committed_at"),
                value.get("created_at"),  # for activity
            ]

            for date_str in date_fields:
                if date_str:
                    try:
                        fact_date = datetime.fromisoformat(date_str)
                        if fact_date > since:
                            filtered_facts.append(fact)
                            break
                    except Exception:
                        # If date parsing fails, include the fact
                        filtered_facts.append(fact)
                        break
            else:
                # No date fields or all parsing failed, include the fact
                filtered_facts.append(fact)

        return filtered_facts

    async def _fact_exists(self, company_id: str, fact_type: str) -> bool:
        """Check if a GitHub fact already exists for company_id."""
        async with self.db_manager.get_session() as session:
            result = await session.execute(
                text("""
                SELECT COUNT(*)
                FROM facts
                WHERE company_id = :cid
                AND fact_type = :ft
                AND source = 'github'
                """),
                {"cid": company_id, "ft": fact_type},
            )
            return result.fetchone()[0] > 0
