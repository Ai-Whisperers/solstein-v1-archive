#!/usr/bin/env python3
"""Cache a GitHub issue snapshot for local planning visibility.

This script intentionally does not drive autonomous execution order.
`planning/QUEUE.md` remains the canonical work queue; the issue snapshot is
informational so local agents can inspect the current GitHub tracker without
depending on live network calls during every shift.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_REPO = "Ai-Whisperers/solstein"
DEFAULT_STATE = "open"
DEFAULT_OUTPUT_DIR = Path("planning/generated")


def _build_request(url: str, *, token: str | None) -> urllib.request.Request:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "solstein-github-issue-cache",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return urllib.request.Request(url, headers=headers)


def fetch_issues(repo: str, *, state: str, token: str | None = None) -> list[dict[str, Any]]:
    """Fetch issues from GitHub REST API, excluding pull requests."""
    base_url = f"https://api.github.com/repos/{repo}/issues"
    page = 1
    issues: list[dict[str, Any]] = []

    while True:
        query = urllib.parse.urlencode(
            {
                "state": state,
                "per_page": 100,
                "page": page,
                "sort": "updated",
                "direction": "desc",
            }
        )
        request = _build_request(f"{base_url}?{query}", token=token)

        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"GitHub API request failed with status {exc.code}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"GitHub API request failed: {exc.reason}") from exc

        if not isinstance(payload, list):
            raise RuntimeError("GitHub API returned a non-list issues payload")
        if not payload:
            break

        for item in payload:
            if isinstance(item, dict) and "pull_request" not in item:
                issues.append(item)

        if len(payload) < 100:
            break
        page += 1

    return issues


def normalize_issues(issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Normalize raw GitHub issue payloads into a compact snapshot schema."""
    normalized: list[dict[str, Any]] = []
    for issue in issues:
        labels = [
            label.get("name", "")
            for label in issue.get("labels", [])
            if isinstance(label, dict) and isinstance(label.get("name"), str)
        ]
        normalized.append(
            {
                "number": int(issue.get("number", 0) or 0),
                "title": str(issue.get("title", "")),
                "state": str(issue.get("state", "")),
                "labels": labels,
                "comments": int(issue.get("comments", 0) or 0),
                "updated_at": issue.get("updated_at"),
                "created_at": issue.get("created_at"),
                "url": issue.get("html_url"),
            }
        )
    return normalized


def render_markdown(repo: str, state: str, issues: list[dict[str, Any]], generated_on: str) -> str:
    lines = [
        "# GitHub Issue Snapshot",
        "",
        f"- Repo: `{repo}`",
        f"- State: `{state}`",
        f"- Generated on: `{generated_on}`",
        "- Planning authority: `planning/QUEUE.md` remains canonical; this snapshot is informational.",
        "",
        f"Total issues: **{len(issues)}**",
        "",
    ]

    if not issues:
        lines.append("No issues matched the requested state.")
        return "\n".join(lines)

    lines.extend(
        [
            "| # | Title | Labels | Comments | Updated |",
            "|---|-------|--------|----------|---------|",
        ]
    )
    for issue in issues:
        labels = ", ".join(issue["labels"]) if issue["labels"] else "-"
        title = str(issue["title"]).replace("|", "\\|")
        url = issue["url"] or ""
        updated = issue["updated_at"] or "-"
        lines.append(f"| [#{issue['number']}]({url}) | {title} | {labels} | {issue['comments']} | {updated} |")

    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=DEFAULT_REPO, help="GitHub repository in owner/name form")
    parser.add_argument("--state", default=DEFAULT_STATE, help="Issue state to fetch (open, closed, all)")
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory where JSON and Markdown snapshots are written",
    )
    parser.add_argument(
        "--input-json",
        help="Optional path to a raw GitHub issues JSON payload for offline generation/testing",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.input_json:
        raw_payload = json.loads(Path(args.input_json).read_text(encoding="utf-8"))
        if not isinstance(raw_payload, list):
            raise RuntimeError("--input-json must point to a JSON list")
        raw_issues = [
            item for item in raw_payload if isinstance(item, dict) and "pull_request" not in item
        ]
    else:
        raw_issues = fetch_issues(args.repo, state=args.state, token=os.getenv("GITHUB_TOKEN"))

    issues = normalize_issues(raw_issues)
    generated_on = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    payload = {
        "repo": args.repo,
        "state": args.state,
        "generated_on": generated_on,
        "planning_authority": "planning/QUEUE.md",
        "issues": issues,
    }

    out_json = output_dir / "GITHUB_ISSUE_SNAPSHOT.json"
    out_md = output_dir / "GITHUB_ISSUE_SNAPSHOT.md"
    out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    out_md.write_text(render_markdown(args.repo, args.state, issues, generated_on), encoding="utf-8")

    print(f"Wrote {len(issues)} issues to {out_json} and {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
