#!/usr/bin/env python3
"""Check documentation quality - placeholder tokens, missing metadata, etc."""

import argparse
import re
from pathlib import Path

PLACEHOLDER_PATTERNS = [
    r"TODO",
    r"FIXME",
    r"XXX",
    r"HACK",
    r"\[ \]",  # Unchecked checkbox
    r"PLACEHOLDER",
    r"INSERT_.*_HERE",
]

REQUIRED_METADATA = ["status", "priority"]


def check_quality(path: str, strict: bool = False) -> dict:
    docs_path = Path(path)
    if not docs_path.exists():
        return {"error": f"Path not found: {path}"}

    violations = []

    for md_file in docs_path.rglob("*.md"):
        if "generated" in md_file.parts:
            continue

        content = md_file.read_text(errors="ignore")

        for pattern in PLACEHOLDER_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                violations.append(
                    {
                        "file": str(md_file),
                        "type": "placeholder",
                        "pattern": pattern,
                        "matches": len(matches),
                    }
                )

        frontmatter_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if frontmatter_match:
            frontmatter = frontmatter_match.group(1)
            for field in REQUIRED_METADATA:
                if f"{field}:" not in frontmatter:
                    violations.append(
                        {
                            "file": str(md_file),
                            "type": "missing_metadata",
                            "field": field,
                        }
                    )

    blocking = [v for v in violations if v["type"] == "placeholder"]

    print(f"Quality check: {len(blocking)} violations found")

    if blocking and strict:
        print("STRICT MODE: Blocking violations found:")
        for v in blocking[:5]:
            print(f"  - {v['file']}: {v['pattern']}")
        return {"blocking": blocking, "warnings": violations}

    return {"violations": violations}


def main():
    parser = argparse.ArgumentParser(description="Check documentation quality")
    parser.add_argument("--path", default="docs", help="Path to check")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    args = parser.parse_args()

    result = check_quality(args.path, args.strict)

    if "blocking" in result:
        exit(1)


if __name__ == "__main__":
    main()
