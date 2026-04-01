#!/usr/bin/env python3
"""Import cycle detector for CI/CD.

EPIC-019 Story 11: Detects circular imports between Python modules.
Prevents circular dependencies that can cause import errors.

Usage:
    python detect_import_cycles.py [src_path]

Exit codes:
    0 - No cycles detected
    1 - Cycles detected
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path


class ImportCycleDetector:
    """Detect circular imports in Python codebase."""

    def __init__(self, src_path: str):
        self.src_path = Path(src_path)
        self.import_graph: dict[str, set[str]] = {}
        self.cycles: list[list[str]] = []

    def build_import_graph(self) -> dict[str, set[str]]:
        """Build a graph of module imports."""
        for file in self.src_path.rglob("*.py"):
            if "__pycache__" in str(file):
                continue

            try:
                content = file.read_text()
                tree = ast.parse(content)

                module_name = self._get_module_name(file)
                if module_name not in self.import_graph:
                    self.import_graph[module_name] = set()

                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.module and self._is_internal_module(node.module):
                            self.import_graph[module_name].add(node.module)
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            if self._is_internal_module(alias.name):
                                self.import_graph[module_name].add(alias.name)

            except Exception as e:
                print(f"Warning: Could not parse {file}: {e}")

        return self.import_graph

    def _get_module_name(self, file: Path) -> str:
        """Convert file path to module name."""
        try:
            rel_path = file.relative_to(self.src_path)
            parts = list(rel_path.parts)
            parts[-1] = parts[-1].replace(".py", "")
            return f"solstein.{'.'.join(parts)}"
        except ValueError:
            return str(file)

    def _is_internal_module(self, module: str) -> bool:
        """Check if module is internal to the project."""
        return module.startswith("solstein")

    def detect_cycles(self) -> list[list[str]]:
        """Detect all cycles using DFS."""
        visited = set()
        rec_stack = set()
        path: list[str] = []

        def dfs(node: str):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self.import_graph.get(node, set()):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:]
                    # Normalize cycle (start from smallest element)
                    min_idx = cycle.index(min(cycle))
                    normalized = cycle[min_idx:] + cycle[:min_idx]
                    if normalized not in self.cycles:
                        self.cycles.append(normalized)

            path.pop()
            rec_stack.remove(node)

        for node in self.import_graph:
            if node not in visited:
                dfs(node)

        return self.cycles

    def print_report(self) -> bool:
        """Print cycle detection report. Returns True if cycles found."""
        print("=" * 80)
        print("IMPORT CYCLE DETECTION REPORT")
        print("=" * 80)

        # Build graph first
        self.build_import_graph()
        print(f"\n📊 Analyzed {len(self.import_graph)} modules")
        print(f"🔗 Found {sum(len(deps) for deps in self.import_graph.values())} import relationships")

        # Detect cycles
        self.detect_cycles()

        if self.cycles:
            print(f"\n❌ CIRCULAR IMPORTS DETECTED ({len(self.cycles)} cycles):")
            print()

            for i, cycle in enumerate(self.cycles, 1):
                print(f"  Cycle #{i}:")
                for j, module in enumerate(cycle):
                    arrow = " → " if j < len(cycle) - 1 else " → (back to start)"
                    print(f"    {module}{arrow}")
                print()

            print("💡 To fix:")
            print("   1. Extract shared code into a separate module")
            print("   2. Use dependency injection")
            print("   3. Move imports inside functions (last resort)")
            print("   4. See EPIC-020 for examples of proper module structure")

            return True
        else:
            print("\n✅ No circular imports detected!")
            print("   All module dependencies form a directed acyclic graph (DAG)")
            return False

    def get_cycle_count(self) -> int:
        """Get total number of cycles."""
        if not self.import_graph:
            self.build_import_graph()
        if not self.cycles:
            self.detect_cycles()
        return len(self.cycles)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Detect import cycles")
    parser.add_argument("src", nargs="?", default="src/solstein", help="Source directory")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--count-only", action="store_true", help="Only output cycle count")
    args = parser.parse_args()

    detector = ImportCycleDetector(args.src)

    if args.count_only:
        count = detector.get_cycle_count()
        print(count)
        sys.exit(0 if count == 0 else 1)

    if args.json:
        import json

        detector.build_import_graph()
        detector.detect_cycles()
        output = {
            "cycles": detector.cycles,
            "cycle_count": len(detector.cycles),
            "module_count": len(detector.import_graph),
            "import_count": sum(len(deps) for deps in detector.import_graph.values()),
        }
        print(json.dumps(output, indent=2))
        sys.exit(0 if len(detector.cycles) == 0 else 1)

    has_cycles = detector.print_report()

    if has_cycles:
        print("\n❌ Import cycle check FAILED!")
        print("   Please break circular dependencies before merging.")
        sys.exit(1)
    else:
        print("\n✅ Import cycle check PASSED!")
        sys.exit(0)


if __name__ == "__main__":
    main()
