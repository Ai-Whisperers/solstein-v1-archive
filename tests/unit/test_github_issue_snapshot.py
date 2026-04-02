from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "cache_github_issues.py"


def test_github_issue_snapshot_generator_runs_with_fixture(tmp_path: Path) -> None:
    fixture = tmp_path / "issues.json"
    fixture.write_text(
        json.dumps(
            [
                {
                    "number": 12,
                    "title": "Caching strategy rationalization",
                    "state": "open",
                    "labels": [{"name": "epic"}, {"name": "planning"}],
                    "comments": 4,
                    "updated_at": "2026-04-02T00:00:00Z",
                    "created_at": "2026-04-01T00:00:00Z",
                    "html_url": "https://github.com/Ai-Whisperers/solstein/issues/12",
                },
                {
                    "number": 99,
                    "title": "Should be ignored because it is a PR",
                    "state": "open",
                    "labels": [],
                    "comments": 0,
                    "updated_at": "2026-04-02T00:00:00Z",
                    "created_at": "2026-04-01T00:00:00Z",
                    "html_url": "https://github.com/Ai-Whisperers/solstein/pull/99",
                    "pull_request": {"url": "https://api.github.com/repos/Ai-Whisperers/solstein/pulls/99"},
                },
            ]
        ),
        encoding="utf-8",
    )

    out_dir = tmp_path / "generated"
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--repo",
            "Ai-Whisperers/solstein",
            "--input-json",
            str(fixture),
            "--output-dir",
            str(out_dir),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr or result.stdout

    out_json = out_dir / "GITHUB_ISSUE_SNAPSHOT.json"
    out_md = out_dir / "GITHUB_ISSUE_SNAPSHOT.md"
    assert out_json.exists()
    assert out_md.exists()

    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert payload["planning_authority"] == "planning/QUEUE.md"
    assert len(payload["issues"]) == 1
    assert payload["issues"][0]["number"] == 12

    content = out_md.read_text(encoding="utf-8")
    assert "QUEUE.md" in content
    assert "#12" in content
