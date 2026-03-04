"""Tests for GitHubRefreshConnector."""

from unittest.mock import MagicMock, patch

import pytest

from solstein.infrastructure.connectors.github_refresh import GitHubRefreshConnector
from solstein.infrastructure.database import DatabaseManager


class TestGitHubRefreshConnector:
    """Test suite for GitHubRefreshConnector."""

    @pytest.fixture
    def mock_db_manager(self):
        """Provide a mocked DatabaseManager."""
        return MagicMock(spec=DatabaseManager)

    @pytest.fixture
    def connector(self, mock_db_manager):
        """Provide a GitHubRefreshConnector instance with mocked dependencies."""
        with patch("solstein.infrastructure.connectors.github_refresh.GitHubConnector") as mock_connector_class:
            mock_connector = MagicMock()
            mock_connector_class.return_value = mock_connector
            connector = GitHubRefreshConnector(mock_db_manager)
            connector.github_connector = mock_connector
            return connector

    def test_initialization(self, mock_db_manager):
        """Test connector initializes with valid config."""
        with patch("solstein.infrastructure.connectors.github_refresh.GitHubConnector"):
            connector = GitHubRefreshConnector(mock_db_manager)

            assert connector is not None
            assert connector.db_manager == mock_db_manager
            assert connector.source_name == "github"
            assert connector.source_type == "technical_signal"
            assert connector.confidence == 0.85

    @pytest.mark.asyncio
    async def test_fetch_facts_success(self, connector):
        """Test successful fact fetching with mocked GitHub API."""
        # Mock repository data
        connector.github_connector.get_user_repositories = MagicMock(
            return_value=[
                {
                    "id": 1,
                    "name": "repo1",
                    "full_name": "user/repo1",
                    "description": "Test repo",
                    "language": "Python",
                    "stargazers_count": 100,
                    "forks_count": 10,
                    "open_issues_count": 5,
                    "created_at": "2020-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z",
                    "pushed_at": "2023-06-01T00:00:00Z",
                    "owner": {"login": "testuser"},
                }
            ]
        )
        connector.github_connector.get_recent_commits = MagicMock(return_value=[])
        connector.github_connector.get_repository_activity = MagicMock(return_value=[])

        facts = await connector.fetch_facts(["testuser"])

        assert len(facts) == 1
        assert facts[0]["fact_type"] == "github_repository"
        assert facts[0]["source"] == "github"
        assert facts[0]["confidence"] == 0.85
        assert facts[0]["value"]["repo_name"] == "repo1"

    @pytest.mark.asyncio
    async def test_fetch_facts_error_handling(self, connector):
        """Test error handling for API failures."""
        connector.github_connector.get_user_repositories = MagicMock(side_effect=Exception("API connection failed"))
        connector.github_connector.get_recent_commits = MagicMock(return_value=[])
        connector.github_connector.get_repository_activity = MagicMock(return_value=[])

        # Should handle error gracefully and return empty list
        facts = await connector.fetch_facts(["testuser"])
        assert facts == []

    @pytest.mark.asyncio
    async def test_empty_results_handling(self, connector):
        """Test handling of empty results."""
        connector.github_connector.get_user_repositories = MagicMock(return_value=[])
        connector.github_connector.get_recent_commits = MagicMock(return_value=[])
        connector.github_connector.get_repository_activity = MagicMock(return_value=[])

        facts = await connector.fetch_facts(["testuser"])
        assert facts == []

    @pytest.mark.asyncio
    async def test_data_transformation_repo_to_fact(self, connector):
        """Test data transformation from GitHub repo to Fact object."""
        repo_data = {
            "id": 1,
            "name": "test-repo",
            "full_name": "user/test-repo",
            "description": "A test repository",
            "language": "Python",
            "stargazers_count": 100,
            "forks_count": 10,
            "open_issues_count": 5,
            "created_at": "2020-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "pushed_at": "2023-06-01T00:00:00Z",
            "owner": {"login": "testuser"},
        }

        fact = connector._convert_repo_to_fact(repo_data)

        assert fact["fact_type"] == "github_repository"
        assert fact["source"] == "github"
        assert fact["company_id"] == "testuser"
        assert fact["confidence"] == 0.85
        assert fact["value"]["repo_name"] == "test-repo"
        assert fact["value"]["language"] == "Python"
        assert fact["value"]["stargazers_count"] == 100

    @pytest.mark.asyncio
    async def test_data_transformation_commit_to_fact(self, connector):
        """Test data transformation from GitHub commit to Fact object."""
        commit_data = {
            "sha": "abc123",
            "commit": {
                "message": "Fix bug in parser",
                "author": {
                    "name": "John Doe",
                    "email": "john@example.com",
                    "date": "2023-06-01T12:00:00Z",
                },
                "committer": {
                    "name": "Jane Doe",
                    "email": "jane@example.com",
                    "date": "2023-06-01T12:00:00Z",
                },
            },
            "stats": {"additions": 50, "deletions": 20, "total": 70},
            "files": [{"filename": "parser.py", "changes": 70}],
            "author": {"login": "testuser"},
        }

        fact = connector._convert_commit_to_fact(commit_data)

        assert fact["fact_type"] == "github_commit"
        assert fact["source"] == "github"
        assert fact["company_id"] == "testuser"
        assert fact["confidence"] == 0.85
        assert fact["value"]["sha"] == "abc123"
        assert fact["value"]["message"] == "Fix bug in parser"

    @pytest.mark.asyncio
    async def test_data_transformation_activity_to_fact(self, connector):
        """Test data transformation from GitHub activity to Fact object."""
        activity_data = {
            "type": "PushEvent",
            "repo": {"name": "user/repo"},
            "payload": {"ref": "refs/heads/main", "commits": []},
            "created_at": "2023-06-01T12:00:00Z",
            "org": {"login": "myorg"},
            "actor": {"login": "testuser"},
        }

        fact = connector._convert_activity_to_fact(activity_data)

        assert fact["fact_type"] == "github_activity"
        assert fact["source"] == "github"
        assert fact["company_id"] == "testuser"
        assert fact["confidence"] == 0.85
        assert fact["value"]["type"] == "PushEvent"
        assert fact["value"]["repo"] == "user/repo"

    @pytest.mark.asyncio
    async def test_fetch_facts_with_all_data_types(self, connector):
        """Test fetching facts including repos, commits, and activity."""
        repo_data = {
            "id": 1,
            "name": "repo1",
            "full_name": "user/repo1",
            "description": "Test",
            "language": "Python",
            "stargazers_count": 50,
            "forks_count": 5,
            "open_issues_count": 2,
            "created_at": "2020-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "pushed_at": "2023-06-01T00:00:00Z",
            "owner": {"login": "testuser"},
        }

        commit_data = {
            "sha": "abc123",
            "commit": {
                "message": "Fix bug",
                "author": {"name": "John", "email": "john@example.com", "date": "2023-06-01T12:00:00Z"},
                "committer": {"name": "Jane", "email": "jane@example.com", "date": "2023-06-01T12:00:00Z"},
            },
            "stats": {"additions": 50, "deletions": 20, "total": 70},
            "files": [],
            "author": {"login": "testuser"},
        }

        activity_data = {
            "type": "PushEvent",
            "repo": {"name": "user/repo"},
            "payload": {"ref": "refs/heads/main", "commits": []},
            "created_at": "2023-06-01T12:00:00Z",
            "org": {"login": "myorg"},
            "actor": {"login": "testuser"},
        }

        connector.github_connector.get_user_repositories = MagicMock(return_value=[repo_data])
        connector.github_connector.get_recent_commits = MagicMock(return_value=[commit_data])
        connector.github_connector.get_repository_activity = MagicMock(return_value=[activity_data])

        facts = await connector.fetch_facts(["testuser"])

        # Should have 3 facts: 1 repo + 1 commit + 1 activity
        assert len(facts) == 3
        assert facts[0]["fact_type"] == "github_repository"
        assert facts[1]["fact_type"] == "github_commit"
        assert facts[2]["fact_type"] == "github_activity"

    @pytest.mark.asyncio
    async def test_confidence_and_source_attribution(self, connector):
        """Test that confidence and source are correctly attributed to all facts."""
        connector.github_connector.get_user_repositories = MagicMock(
            return_value=[
                {
                    "id": 1,
                    "name": "repo",
                    "full_name": "u/repo",
                    "description": "test",
                    "language": "Python",
                    "stargazers_count": 0,
                    "forks_count": 0,
                    "open_issues_count": 0,
                    "created_at": "2020-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z",
                    "pushed_at": "2023-06-01T00:00:00Z",
                    "owner": {"login": "u"},
                }
            ]
        )
        connector.github_connector.get_recent_commits = MagicMock(return_value=[])
        connector.github_connector.get_repository_activity = MagicMock(return_value=[])

        facts = await connector.fetch_facts(["u"])

        for fact in facts:
            assert fact["source"] == "github"
            assert fact["confidence"] == 0.85
            assert "extracted_at" in fact
            assert "metadata" in fact
