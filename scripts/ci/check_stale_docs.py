#!/usr/bin/env python3
"""Check for stale documentation based on last modification time."""

import argparse
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

STALE_DAYS = 90

POLICY = {
    "max_age_days": STALE_DAYS,
    "owner_rotation_days": 180,
    "review_frequency_days": 30,
}


def get_git_history(path: Path) -> list[dict]:
    result = subprocess.run(
        ["git", "log", "--format=%H|%ai|%an|%s", "--", str(path)],
        capture_output=True,
        text=True,
    )
    commits = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        parts = line.split("|")
        if len(parts) >= 4:
            commits.append(
                {
                    "sha": parts[0],
                    "date": parts[1],
                    "author": parts[2],
                    "subject": "|".join(parts[3:]),
                }
            )
    return commits


def check_stale(path: str, fail_on_stale: bool = False, json_output: bool = False) -> dict:
    docs_path = Path(path)
    if not docs_path.exists():
        return {"error": f"Path not found: {path}"}

    stale_files = []
    now = datetime.now()
    cutoff = now - timedelta(days=STALE_DAYS)

    for md_file in docs_path.rglob("*.md"):
        if "generated" in md_file.parts or "__pycache__" in str(md_file):
            continue

        try:
            result = subprocess.run(
                ["git", "log", "-1", "--format=%ai", "--", str(md_file)],
                capture_output=True,
                text=True,
            )
            if result.stdout.strip():
                last_modified = datetime.fromisoformat(result.stdout.strip().replace(" ", "T").split("+")[0])
                age_days = (now - last_modified).days

                if age_days > STALE_DAYS:
                    stale_files.append(
                        {
                            "file": str(md_file),
                            "last_modified": result.stdout.strip(),
                            "age_days": age_days,
                        }
                    )
        except (subprocess.CalledProcessError, ValueError, OSError):
            continue

    actionable = [f for f in stale_files if f["age_days"] > STALE_DAYS]

    report = {
        "total_scanned": len(list(docs_path.rglob("*.md"))),
        "stale_count": len(stale_files),
        "actionable_stale_count": len(actionable),
        "stale_files": stale_files[:10],
        "policy": POLICY,
        "checked_at": datetime.now().isoformat(),
    }

    if json_output:
        with open("/tmp/stale-docs-report.json", "w") as f:
            json.dump(report, f, indent=2)

    if actionable and fail_on_stale:
        print(f"FAIL: {len(actionable)} stale docs found (>{STALE_DAYS} days)")
        for f in actionable[:5]:
            print(f"  - {f['file']} ({f['age_days']} days old)")
        return report

    print(f"Checked {report['total_scanned']} docs: {len(actionable)} actionable stale")
    return report


def main():
    parser = argparse.ArgumentParser(description="Check for stale documentation")
    parser.add_argument("--path", default="docs", help="Path to check")
    parser.add_argument("--fail", action="store_true", help="Exit with error if stale docs found")
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    args = parser.parse_args()

    check_stale(args.path, args.fail, args.json)


if __name__ == "__main__":
    main()
