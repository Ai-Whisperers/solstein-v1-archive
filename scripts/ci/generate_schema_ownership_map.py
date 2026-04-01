#!/usr/bin/env python3
"""Generate schema ownership map from Pydantic models and SQLAlchemy tables.

STORY-245: Produces docs/reference/generated/SCHEMA_OWNERSHIP_MAP.md
"""

import ast
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SRC = Path("src/solstein")
OUT_MD = Path("docs/reference/generated/SCHEMA_OWNERSHIP_MAP.md")
OUT_JSON = Path("docs/reference/generated/SCHEMA_OWNERSHIP_MAP.json")


def find_schemas(root: Path) -> list[dict]:
    """Walk source tree, extract Pydantic BaseModel and SQLAlchemy DeclarativeBase subclasses."""
    schemas = []
    for py_file in sorted(root.rglob("*.py")):
        if "__pycache__" in str(py_file):
            continue
        rel = py_file.relative_to(root)
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            bases = [_base_name(b) for b in node.bases]
            schema_type = _classify(bases)
            if schema_type is None:
                continue

            fields = []
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    fields.append(item.target.id)

            # Determine owning layer from path
            parts = list(rel.parts)
            layer = parts[0] if parts else "unknown"

            schemas.append({
                "class_name": node.name,
                "file": str(rel),
                "line": node.lineno,
                "layer": layer,
                "type": schema_type,
                "bases": bases,
                "field_count": len(fields),
                "fields": fields[:20],  # cap for readability
            })
    return schemas


def _base_name(node: ast.expr) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return "?"


def _classify(bases: list[str]) -> str | None:
    pydantic = {"BaseModel", "BaseSettings", "BaseSchema"}
    sqla = {"Base", "DeclarativeBase", "MappedAsDataclass"}
    dataclass_markers = {"NamedTuple", "TypedDict"}
    if pydantic & set(bases):
        return "pydantic"
    if sqla & set(bases):
        return "sqlalchemy"
    if dataclass_markers & set(bases):
        return "typed_dict_or_namedtuple"
    return None


def render_md(schemas: list[dict]) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Schema Ownership Map",
        "",
        f"> Auto-generated on {now} by `scripts/ci/generate_schema_ownership_map.py`.",
        "> Do not edit manually.",
        "",
        f"**Total schemas**: {len(schemas)}",
        "",
    ]

    # Group by layer
    by_layer: dict[str, list[dict]] = {}
    for s in schemas:
        by_layer.setdefault(s["layer"], []).append(s)

    for layer in sorted(by_layer):
        items = by_layer[layer]
        lines.append(f"## {layer}/ ({len(items)} schemas)")
        lines.append("")
        lines.append("| Class | Type | File | Fields |")
        lines.append("|-------|------|------|--------|")
        for s in sorted(items, key=lambda x: x["class_name"]):
            fields_str = str(s["field_count"])
            lines.append(f"| `{s['class_name']}` | {s['type']} | `{s['file']}:{s['line']}` | {fields_str} |")
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    schemas = find_schemas(SRC)
    if not schemas:
        print("WARNING: no schemas found", file=sys.stderr)

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text(render_md(schemas), encoding="utf-8")
    OUT_JSON.write_text(json.dumps(schemas, indent=2), encoding="utf-8")

    print(f"Schema ownership map: {len(schemas)} schemas -> {OUT_MD}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
