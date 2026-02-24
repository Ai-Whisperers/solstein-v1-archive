import pytest

from solstein.agents.github_agent import GitHubAgent


class _FakeResponse:
    def __init__(self, status_code: int, payload: list[dict[str, object]]):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


def test_api_commit_velocity_trend_up(monkeypatch: pytest.MonkeyPatch):
    agent = GitHubAgent(github_token=None)

    def fake_get(url: str, *, params=None, timeout: float = 0):
        if params and "until" in params:
            return _FakeResponse(200, [{"sha": "x"}] * 5)
        return _FakeResponse(200, [{"sha": "x"}] * 10)

    monkeypatch.setattr(agent, "_get", fake_get)

    trend = agent._api_commit_velocity_trend("org", [{"name": "repo"}])
    assert trend is not None
    assert trend["recent_14d"] == 10
    assert trend["previous_14d"] == 5
    assert trend["direction"] == "up"
    assert trend["trend_ratio"] == pytest.approx(1.0)


def test_api_commit_velocity_trend_down(monkeypatch: pytest.MonkeyPatch):
    agent = GitHubAgent(github_token=None)

    def fake_get(url: str, *, params=None, timeout: float = 0):
        if params and "until" in params:
            return _FakeResponse(200, [{"sha": "x"}] * 4)
        return _FakeResponse(200, [{"sha": "x"}] * 2)

    monkeypatch.setattr(agent, "_get", fake_get)

    trend = agent._api_commit_velocity_trend("org", [{"name": "repo"}])
    assert trend is not None
    assert trend["direction"] == "down"
    assert trend["trend_ratio"] == pytest.approx(-0.5)


def test_api_commit_velocity_trend_flat(monkeypatch: pytest.MonkeyPatch):
    agent = GitHubAgent(github_token=None)

    def fake_get(url: str, *, params=None, timeout: float = 0):
        if params and "until" in params:
            return _FakeResponse(200, [{"sha": "x"}] * 3)
        return _FakeResponse(200, [{"sha": "x"}] * 3)

    monkeypatch.setattr(agent, "_get", fake_get)

    trend = agent._api_commit_velocity_trend("org", [{"name": "repo"}])
    assert trend is not None
    assert trend["direction"] == "flat"
    assert trend["trend_ratio"] == pytest.approx(0.0)


def test_api_commit_velocity_trend_prev_zero_recent_nonzero(monkeypatch: pytest.MonkeyPatch):
    agent = GitHubAgent(github_token=None)

    def fake_get(url: str, *, params=None, timeout: float = 0):
        if params and "until" in params:
            return _FakeResponse(200, [])
        return _FakeResponse(200, [{"sha": "x"}] * 3)

    monkeypatch.setattr(agent, "_get", fake_get)

    trend = agent._api_commit_velocity_trend("org", [{"name": "repo"}])
    assert trend is not None
    assert trend["direction"] == "up"
    assert trend["trend_ratio"] is None


def test_api_commit_velocity_trend_none_when_no_activity(monkeypatch: pytest.MonkeyPatch):
    agent = GitHubAgent(github_token=None)

    def fake_get(url: str, *, params=None, timeout: float = 0):
        return _FakeResponse(200, [])

    monkeypatch.setattr(agent, "_get", fake_get)

    assert agent._api_commit_velocity_trend("org", [{"name": "repo"}]) is None
