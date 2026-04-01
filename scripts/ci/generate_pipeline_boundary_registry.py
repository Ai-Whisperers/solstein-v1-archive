#!/usr/bin/env python3
"""Generate pipeline boundary registry from source analysis.

STORY-245: Produces docs/reference/generated/PIPELINE_BOUNDARY_REGISTRY.md

Identifies cross-layer function/class boundaries: where one layer calls into another.
"""

import ast
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SRC = Path("src/solstein")
OUT_MD = Path("docs/reference/generated/PIPELINE_BOUNDARY_REGISTRY.md")
OUT_JSON = Path("docs/reference/generated/PIPELINE_BOUNDARY_REGISTRY.json")


def _extract_import_target(node: ast.stmt) -> tuple[str | None, str | None]:
    """Extract target layer and imported name from an import statement."""
    if isinstance(node, ast.ImportFrom) and node.module:
        mod = node.module
        if mod.startswith("solstein."):
            parts = mod.split(".")
            if len(parts) >= 2:
                name = mod
                if node.names:
                    name += f".{node.names[0].name}"
                return parts[1], name
    elif isinstance(node, ast.Import):
        for alias in node.names:
            if alias.name.startswith("solstein."):
                parts = alias.name.split(".")
                if len(parts) >= 2:
                    return parts[1], alias.name
    return None, None


def _scan_file(py_file: Path, root: Path) -> list[dict]:
    """Scan a single file for cross-layer imports."""
    rel = py_file.relative_to(root)
    source_layer = rel.parts[0] if rel.parts else "unknown"
    results = []

    try:
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
    except SyntaxError:
        return results

    for node in ast.walk(tree):
        if not isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        target_layer, imported_name = _extract_import_target(node)
        if target_layer and target_layer != source_layer:
            results.append({
                "source_file": str(rel),
                "source_layer": source_layer,
                "target_layer": target_layer,
                "imported": imported_name or "?",
                "line": node.lineno,
            })
    return results


def detect_boundaries(root: Path) -> list[dict]:
    """Find import statements that cross layer boundaries."""
    boundaries = []
    for py_file in sorted(root.rglob("*.py")):
        if "__pycache__" in str(py_file):
            continue
        boundaries.extend(_scan_file(py_file, root))
    return boundaries


def _build_adjacency(boundaries: list[dict]) -> dict[str, dict[str, int]]:
    """Build adjacency count matrix from boundaries."""
    adj: dict[str, dict[str, int]] = {}
    for b in boundaries:
        src, tgt = b["source_layer"], b["target_layer"]
        adj.setdefault(src, {})
        adj[src][tgt] = adj[src].get(tgt, 0) + 1
    return adj


def _render_matrix(adj: dict[str, dict[str, int]], all_layers: list[str]) -> list[str]:
    """Render the dependency matrix as markdown table rows."""
    lines = []
    header = "| Source \\ Target | " + " | ".join(f"`{layer}`" for layer in all_layers) + " |"
    sep = "|---" * (len(all_layers) + 1) + "|"
    lines.append(header)
    lines.append(sep)
    for src in all_layers:
        cells = []
        for tgt in all_layers:
            count = adj.get(src, {}).get(tgt, 0)
            cells.append(str(count) if count else ".")
        lines.append(f"| `{src}` | " + " | ".join(cells) + " |")
    return lines


def render_md(boundaries: list[dict]) -> str:
    """Render the full markdown report."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    adj = _build_adjacency(boundaries)

    all_layers = sorted(
        set(b["source_layer"] for b in boundaries) | set(b["target_layer"] for b in boundaries)
    )

    lines = [
        "# Pipeline Boundary Registry",
        "",
        f"> Auto-generated on {now} by `scripts/ci/generate_pipeline_boundary_registry.py`.",
        "> Do not edit manually.",
        "",
        f"**Total cross-layer imports**: {len(boundaries)}",
        f"**Layer pairs with traffic**: {sum(len(v) for v in adj.values())}",
        "",
        "## Layer Dependency Matrix",
        "",
        "Shows how many imports flow from source (row) to target (column).",
        "",
    ]
    lines.extend(_render_matrix(adj, all_layers))
    lines.append("")

    # Top boundary hotspots
    lines.append("## Top 20 Boundary Hotspots")
    lines.append("")
    lines.append("Files with the most cross-layer imports (potential coupling risk).")
    lines.append("")

    file_counts: dict[str, int] = {}
    for b in boundaries:
        file_counts[b["source_file"]] = file_counts.get(b["source_file"], 0) + 1

    top = sorted(file_counts.items(), key=lambda x: -x[1])[:20]
    lines.append("| File | Cross-Layer Imports |")
    lines.append("|------|---------------------|")
    for filepath, count in top:
        lines.append(f"| `{filepath}` | {count} |")
    lines.append("")

    return "\n".join(lines)


def main() -> int:
    boundaries = detect_boundaries(SRC)

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text(render_md(boundaries), encoding="utf-8")
    OUT_JSON.write_text(json.dumps(boundaries, indent=2), encoding="utf-8")

    print(f"Pipeline boundary registry: {len(boundaries)} cross-layer imports -> {OUT_MD}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
