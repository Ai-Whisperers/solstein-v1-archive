#!/usr/bin/env python3
"""Module boundary enforcer for CI/CD.

EPIC-019 Story 14: Enforces clean module boundaries and layer separation.
Validates that imports follow the architectural design (API → Service → Domain → Infrastructure).

Usage:
    python enforce_module_boundaries.py [src_path]

Exit codes:
    0 - All boundaries respected
    1 - Boundary violations detected
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Any


class ModuleBoundaryEnforcer:
    """Enforce module boundaries and layer separation."""

    # Define architectural layers (higher = outer layer)
    LAYERS = {
        "api": 4,  # Outermost - FastAPI routers, schemas
        "cli": 4,  # CLI commands
        "presentation": 3,  # Report generators, formatters
        "services": 3,  # Business logic services
        "application": 3,  # Application orchestration
        "analytics": 2,  # Scoring, analysis
        "research": 2,  # Research pipeline
        "agents": 2,  # AI agents
        "domain": 1,  # Core business logic
        "data": 1,  # Data loading, connectors
        "infrastructure": 0,  # Innermost - DB, external APIs
        "core": 0,  # Core utilities
    }

    # Allowed dependencies (layer can import from these layers)
    ALLOWED_DEPS = {
        4: [4, 3, 2, 1, 0],  # API can import from all layers
        3: [3, 2, 1, 0],  # Services can import from domain and below
        2: [2, 1, 0],  # Analytics can import from domain and below
        1: [1, 0],  # Domain can import from infrastructure
        0: [0],  # Infrastructure can only import from infrastructure
    }

    # Special exceptions for specific modules
    EXCEPTIONS = {
        # Allow infrastructure to import domain for repository pattern
        ("infrastructure", "domain"): "Repository pattern requires domain models",
        # Allow api to import infrastructure for dependencies
        ("api", "infrastructure"): "FastAPI dependency injection",
    }

    def __init__(self, src_path: str):
        self.src_path = Path(src_path)
        self.violations: list[dict[str, Any]] = []

    def enforce(self) -> bool:
        """Enforce module boundaries."""
        found = False

        for file in self.src_path.rglob("*.py"):
            if "__pycache__" in str(file):
                continue

            try:
                content = file.read_text()
                tree = ast.parse(content)

                source_layer = self._get_layer(file)
                if source_layer is None:
                    continue

                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.module and node.module.startswith("solstein"):
                            target_layer = self._get_layer_from_module(node.module)

                            if target_layer is not None:
                                violation = self._check_violation(
                                    file, source_layer, target_layer, node.module, node.lineno
                                )
                                if violation:
                                    self.violations.append(violation)
                                    found = True

            except Exception as e:
                print(f"Warning: Could not parse {file}: {e}")

        return found

    def _get_layer(self, file: Path) -> int | None:
        """Get architectural layer for a file."""
        try:
            rel_path = file.relative_to(self.src_path)
            parts = rel_path.parts

            if parts:
                first_dir = parts[0]
                return self.LAYERS.get(first_dir)

        except ValueError:
            pass

        return None

    def _get_layer_from_module(self, module: str) -> int | None:
        """Get architectural layer from module name."""
        parts = module.split(".")
        if len(parts) >= 2:
            return self.LAYERS.get(parts[1])
        return None

    def _check_violation(
        self, file: Path, source_layer: int, target_layer: int, module: str, line: int
    ) -> dict[str, Any] | None:
        """Check if import violates architectural boundaries."""
        # Check if import is allowed
        allowed = self.ALLOWED_DEPS.get(source_layer, [])

        if target_layer not in allowed:
            # Check for exceptions
            source_name = self._get_layer_name(source_layer)
            target_name = self._get_layer_name(target_layer)

            if (source_name, target_name) in self.EXCEPTIONS:
                return None

            return {
                "file": str(file),
                "line": line,
                "source_layer": source_name,
                "target_layer": target_name,
                "imported_module": module,
                "issue": f"{source_name} layer should not import from {target_name} layer",
                "severity": "error",
            }

        return None

    def _get_layer_name(self, layer: int) -> str:
        """Get layer name from level."""
        for name, level in self.LAYERS.items():
            if level == layer:
                return name
        return "unknown"

    def get_import_graph(self) -> dict[str, set[str]]:
        """Generate import dependency graph."""
        graph: dict[str, set[str]] = {}

        for file in self.src_path.rglob("*.py"):
            if "__pycache__" in str(file):
                continue

            try:
                content = file.read_text()
                tree = ast.parse(content)

                module_name = self._get_module_name(file)
                graph[module_name] = set()

                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.module and node.module.startswith("solstein"):
                            graph[module_name].add(node.module)

            except Exception:
                pass

        return graph

    def _get_module_name(self, file: Path) -> str:
        """Convert file path to module name."""
        try:
            rel_path = file.relative_to(self.src_path)
            parts = list(rel_path.parts)
            parts[-1] = parts[-1].replace(".py", "")
            return f"solstein.{'.'.join(parts)}"
        except ValueError:
            return str(file)

    def print_report(self) -> bool:
        """Print enforcement report. Returns True if violations found."""
        print("=" * 80)
        print("MODULE BOUNDARY ENFORCEMENT REPORT")
        print("=" * 80)

        print("\n📊 Architectural Layers:")
        for name, level in sorted(self.LAYERS.items(), key=lambda x: x[1], reverse=True):
            indent = "  " * (4 - level)
            print(f"{indent}Layer {level}: {name}")

        print("\n📋 Allowed Dependencies:")
        for layer, allowed in sorted(self.ALLOWED_DEPS.items(), reverse=True):
            layer_name = self._get_layer_name(layer)
            allowed_names = [self._get_layer_name(allowed_layer) for allowed_layer in allowed]
            print(f"  {layer_name}: can import from {', '.join(allowed_names)}")

        self.enforce()

        if self.violations:
            print(f"\n❌ BOUNDARY VIOLATIONS ({len(self.violations)} found):")
            print()

            # Group by source layer
            by_source: dict[str, list[dict]] = {}
            for v in self.violations:
                by_source.setdefault(v["source_layer"], []).append(v)

            for source, violations in sorted(by_source.items()):
                print(f"🔴 {source} layer violations ({len(violations)}):")
                for v in violations:
                    print(f"   ❌ {v['file']}:{v['line']}")
                    print(f"      Imports: {v['imported_module']}")
                    print(f"      Issue: {v['issue']}")
                print()

            print("💡 To fix:")
            print("   1. Move shared code to a lower layer")
            print("   2. Use dependency injection")
            print("   3. Define interfaces in lower layers")
            print("   4. Apply dependency inversion principle")

            return True
        else:
            print("\n✅ No boundary violations detected!")
            print("   All imports follow architectural boundaries.")
            return False


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Enforce module boundaries")
    parser.add_argument("src", nargs="?", default="src/solstein", help="Source directory")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--graph", action="store_true", help="Output import graph")
    args = parser.parse_args()

    enforcer = ModuleBoundaryEnforcer(args.src)

    if args.graph:
        import json

        graph = enforcer.get_import_graph()
        print(json.dumps({k: list(v) for k, v in graph.items()}, indent=2))
        sys.exit(0)

    if args.json:
        import json

        enforcer.enforce()
        output = {
            "violation_count": len(enforcer.violations),
            "violations": enforcer.violations,
            "layers": enforcer.LAYERS,
            "allowed_deps": dict(enforcer.ALLOWED_DEPS),
        }
        print(json.dumps(output, indent=2))
        sys.exit(0 if len(enforcer.violations) == 0 else 1)

    has_violations = enforcer.print_report()

    if has_violations:
        print("\n❌ Module boundary enforcement FAILED!")
        print("   Please refactor to respect architectural boundaries.")
        sys.exit(1)
    else:
        print("\n✅ Module boundary enforcement PASSED!")
        sys.exit(0)


if __name__ == "__main__":
    main()
