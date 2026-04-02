from unittest.mock import AsyncMock

import pytest

from solstein.agents.base_agent import AgentTaskResult
from solstein.domain.models import AggregatedFact, Company, DataSourceType
from solstein.monitoring.continuous_monitor import ContinuousMonitor


@pytest.mark.asyncio
async def test_detect_github_issue_activity_returns_signal() -> None:
    monitor = ContinuousMonitor()
    monitor.github_agent.gather = AsyncMock(
        return_value=AgentTaskResult(
            agent_name="GitHubAgent",
            source_type=DataSourceType.GITHUB,
            success=True,
            extracted_facts=[
                AggregatedFact(
                    fact_type="github_issue_summary",
                    value={
                        "total_open_issues": 27,
                        "repos_with_open_issues": 2,
                        "repos": [
                            {"repo": "acme/main-repo", "issue_count": 20},
                            {"repo": "acme/sdk", "issue_count": 7},
                        ],
                    },
                    confidence=0.86,
                    sources_used=["GitHub Issues: acme/main-repo", "GitHub Issues: acme/sdk"],
                )
            ],
        )
    )

    signal = await monitor._detect_github_issue_activity("Acme")

    assert signal is not None
    assert signal["signal_type"] == "github_issue_activity"
    assert signal["severity"] == "high"
    assert "27 open issues" in signal["description"]


@pytest.mark.asyncio
async def test_detect_critical_signals_includes_github_issue_activity() -> None:
    monitor = ContinuousMonitor()
    company = Company(id="cmp-acme", name="Acme", employees=25)
    monitor._detect_funding_news = AsyncMock(return_value=None)
    monitor._detect_ma_activity = AsyncMock(return_value=None)
    monitor._detect_hiring_surge = AsyncMock(return_value=None)
    monitor._detect_product_launch = AsyncMock(return_value=None)
    monitor._detect_executive_changes = AsyncMock(return_value=None)
    monitor._detect_github_issue_activity = AsyncMock(
        return_value={
            "signal_type": "github_issue_activity",
            "description": "GitHub issue backlog detected: 8 open issues across 1 repos",
            "severity": "medium",
            "sources": 1,
        }
    )

    signals = await monitor._detect_critical_signals(company)

    assert len(signals) == 1
    assert signals[0]["signal_type"] == "github_issue_activity"
