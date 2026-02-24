from __future__ import annotations

from typing import Any, cast

import pytest

from solstein.agents.github_agent import GitHubAgent


class _FakeResponse:
    def __init__(self, status_code: int, json_data: Any):
        self.status_code = status_code
        self._json_data = json_data

    def json(self) -> Any:
        return self._json_data


def test_dependency_health_parses_manifests_and_scores(monkeypatch: pytest.MonkeyPatch) -> None:
    agent = GitHubAgent(github_token="test")

    def _fake_fetch_repo_text_file(org_name: str, repo_name: str, path: str) -> str | None:
        assert org_name == "acme"
        assert repo_name == "repo1"
        if path == "requirements.txt":
            return """
            # comment
            requests==1.0.0
            numpy==1.0.0
            pandas==1.0.0
            flask==1.0.0
            uvicorn==1.0.0
            """.strip()
        if path == "package.json":
            return """
            {
              "dependencies": {
                "lodash": "1.0.0",
                "react": "1.0.0",
                "axios": "1.0.0"
              },
              "devDependencies": {
                "typescript": "1.0.0",
                "eslint": "1.0.0"
              }
            }
            """.strip()
        return None

    monkeypatch.setattr(agent, "_fetch_repo_text_file", _fake_fetch_repo_text_file)

    def _fake_get(url: str, timeout: float = 10, **kwargs: Any) -> _FakeResponse:
        if url == "https://pypi.org/pypi/requests/json":
            return _FakeResponse(200, {"info": {"version": "1.5.0"}})
        if url == "https://pypi.org/pypi/numpy/json":
            return _FakeResponse(200, {"info": {"version": "1.5.0"}})
        if url == "https://pypi.org/pypi/pandas/json":
            return _FakeResponse(200, {"info": {"version": "1.5.0"}})
        if url == "https://pypi.org/pypi/flask/json":
            return _FakeResponse(200, {"info": {"version": "1.5.0"}})
        if url == "https://pypi.org/pypi/uvicorn/json":
            return _FakeResponse(200, {"info": {"version": "1.5.0"}})

        if url == "https://registry.npmjs.org/lodash":
            return _FakeResponse(200, {"dist-tags": {"latest": "1.5.0"}})
        if url == "https://registry.npmjs.org/react":
            return _FakeResponse(200, {"dist-tags": {"latest": "1.5.0"}})
        if url == "https://registry.npmjs.org/axios":
            return _FakeResponse(200, {"dist-tags": {"latest": "1.5.0"}})
        if url == "https://registry.npmjs.org/typescript":
            return _FakeResponse(200, {"dist-tags": {"latest": "1.5.0"}})
        if url == "https://registry.npmjs.org/eslint":
            return _FakeResponse(200, {"dist-tags": {"latest": "1.5.0"}})

        return _FakeResponse(404, {})

    def _fake_post(url: str, json: dict[str, Any] | None = None, timeout: float = 10, **kwargs: Any) -> _FakeResponse:
        assert url == "https://api.osv.dev/v1/query"
        assert json is not None
        return _FakeResponse(
            200,
            {
                "vulns": [
                    {
                        "id": "OSV-TEST-0001",
                        "summary": "Test vulnerability",
                        "severity": [{"type": "CVSS_V3", "score": "7.5"}],
                    }
                ]
            },
        )

    import solstein.agents.github_agent as github_agent_module

    monkeypatch.setattr(github_agent_module.requests, "get", _fake_get)
    monkeypatch.setattr(github_agent_module.requests, "post", _fake_post)

    result = agent._api_dependency_health("acme", [{"name": "repo1"}])
    assert result is not None
    result_typed = cast(dict[str, Any], result)

    assert result_typed["python"]["dependencies_parsed"] >= 5
    assert result_typed["javascript"]["dependencies_parsed"] >= 5
    assert result_typed["health_score_0_to_10"] <= 10
    assert isinstance(result_typed["signal"], str)

    assert len(result_typed["python"]["outdated"]) >= 1
    assert len(result_typed["javascript"]["outdated"]) >= 1

    # Ensure OSV results appear.
    assert len(result_typed["python"]["vulnerabilities"]) >= 1
    vuln = result_typed["python"]["vulnerabilities"][0]
    assert vuln["id"] == "OSV-TEST-0001"
