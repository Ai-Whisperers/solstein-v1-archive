#!/usr/bin/env python3
"""Generate connector contract surface index from source analysis.

STORY-245: Produces docs/reference/generated/CONNECTOR_CONTRACT_INDEX.md

Indexes all connector implementations, their methods, and contract surface.
"""

import ast
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SRC = Path("src/solstein")
OUT_MD = Path("docs/reference/generated/CONNECTOR_CONTRACT_INDEX.md")
OUT_JSON = Path("docs/reference/generated/CONNECTOR_CONTRACT_INDEX.json")

SCAN_DIRS = [
    "connectors",
    "data/connectors",
    "infrastructure/connectors",
    "adapters",
    "agents",
    "data_sources",
]


def _base_name(node: ast.expr) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return "?"


def _extract_public_methods(class_node: ast.ClassDef) -> list[dict]:
    """Extract public methods from a class definition."""
    methods = []
    for item in class_node.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not item.name.startswith("_"):
                methods.append({
                    "name": item.name,
                    "async": isinstance(item, ast.AsyncFunctionDef),
                    "line": item.lineno,
                    "args": [a.arg for a in item.args.args if a.arg != "self"],
                })
    return methods


def _scan_file_for_connectors(py_file: Path, root: Path) -> list[dict]:
    """Scan a single file for connector classes."""
    rel = py_file.relative_to(root)
    results = []

    try:
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
    except SyntaxError:
        return results

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        bases = [_base_name(b) for b in node.bases]
        methods = _extract_public_methods(node)
        if not methods:
            continue
        results.append({
            "class_name": node.name,
            "file": str(rel),
            "line": node.lineno,
            "bases": bases,
            "methods": methods,
            "method_count": len(methods),
            "has_async": any(m["async"] for m in methods),
        })
    return results


def find_connectors(root: Path) -> list[dict]:
    """Find all connector classes and their public methods."""
    connectors = []
    for scan_dir in SCAN_DIRS:
        target = root / scan_dir
        if not target.exists():
            continue
        for py_file in sorted(target.rglob("*.py")):
            if "__pycache__" in str(py_file):
                continue
            connectors.extend(_scan_file_for_connectors(py_file, root))
    return connectors


def render_md(connectors: list[dict]) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Connector Contract Surface Index",
        "",
        f"> Auto-generated on {now} by `scripts/ci/generate_connector_contract_index.py`.",
        "> Do not edit manually.",
        "",
        f"**Total connector classes**: {len(connectors)}",
        f"**Total public methods**: {sum(c['method_count'] for c in connectors)}",
        f"**Async-capable connectors**: {sum(1 for c in connectors if c['has_async'])}",
        "",
    ]

    # Group by directory
    by_dir: dict[str, list[dict]] = {}
    for c in connectors:
        d = str(Path(c["file"]).parent)
        by_dir.setdefault(d, []).append(c)

    for dir_path in sorted(by_dir):
        items = by_dir[dir_path]
        lines.append(f"## {dir_path}/ ({len(items)} classes)")
        lines.append("")
        for c in sorted(items, key=lambda x: x["class_name"]):
            async_tag = " (async)" if c["has_async"] else ""
            bases_str = ", ".join(c["bases"]) if c["bases"] else "none"
            lines.append(f"### `{c['class_name']}`{async_tag}")
            lines.append("")
            lines.append(f"- **File**: `{c['file']}:{c['line']}`")
            lines.append(f"- **Bases**: {bases_str}")
            lines.append(f"- **Public methods**: {c['method_count']}")
            lines.append("")
            if c["methods"]:
                lines.append("| Method | Async | Args |")
                lines.append("|--------|-------|------|")
                for m in c["methods"]:
                    async_mark = "yes" if m["async"] else "no"
                    args_str = ", ".join(m["args"]) if m["args"] else "-"
                    lines.append(f"| `{m['name']}` | {async_mark} | {args_str} |")
                lines.append("")

    return "\n".join(lines)


def main() -> int:
    connectors = find_connectors(SRC)
    if not connectors:
        print("WARNING: no connectors found", file=sys.stderr)

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text(render_md(connectors), encoding="utf-8")
    OUT_JSON.write_text(json.dumps(connectors, indent=2), encoding="utf-8")

    print(f"Connector contract index: {len(connectors)} connectors -> {OUT_MD}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
