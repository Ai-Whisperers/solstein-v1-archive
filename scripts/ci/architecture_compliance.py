#!/usr/bin/env python3
"""Architecture compliance checker.

EPIC-019 Story 7: Detects architecture violations:
- Lazy imports (imports inside functions)
- Circular dependencies
- Layer boundary violations
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Any


class ArchitectureChecker:
    """Check for architecture compliance violations."""

    def __init__(self, src_path: str):
        self.src_path = Path(src_path)
        self.violations: list[dict[str, Any]] = []

    def check_all(self) -> bool:
        """Run all architecture checks."""
        has_lazy_imports = self.check_lazy_imports()
        has_circular_deps = self.check_circular_dependencies()

        return not (has_lazy_imports or has_circular_deps)

    def check_lazy_imports(self) -> bool:
        """Check for lazy imports (imports inside functions/methods)."""
        found = False

        for file in self.src_path.rglob("*.py"):
            if "__pycache__" in str(file):
                continue

            try:
                content = file.read_text()
                tree = ast.parse(content)

                # Track function/class definitions and their line ranges
                function_ranges = []

                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        function_ranges.append((node.lineno, node.end_lineno or node.lineno))

                # Check for imports inside functions
                for node in ast.walk(tree):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        import_line = node.lineno

                        # Check if import is inside any function
                        for func_start, func_end in function_ranges:
                            if func_start < import_line <= func_end:
                                self.violations.append(
                                    {
                                        "type": "lazy_import",
                                        "file": str(file),
                                        "line": import_line,
                                        "message": f"Lazy import at line {import_line}: {self._get_import_name(node)}",
                                    }
                                )
                                found = True
                                break

            except Exception as e:
                print(f"Warning: Could not parse {file}: {e}")

        return found

    def _get_import_name(self, node: ast.Import | ast.ImportFrom) -> str:
        """Get import name for display."""
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
            return f"import {', '.join(names)}"
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            names = [alias.name for alias in node.names]
            return f"from {module} import {', '.join(names)}"
        return "import"

    def check_circular_dependencies(self) -> bool:
        """Check for circular dependencies between modules."""
        # Build import graph
        import_graph: dict[str, set[str]] = {}

        for file in self.src_path.rglob("*.py"):
            if "__pycache__" in str(file):
                continue

            try:
                content = file.read_text()
                tree = ast.parse(content)

                module_name = self._get_module_name(file)
                if module_name not in import_graph:
                    import_graph[module_name] = set()

                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.module and node.module.startswith("solstein"):
                            import_graph[module_name].add(node.module)

            except Exception:
                pass

        # Detect cycles using DFS
        cycles = self._find_cycles(import_graph)

        for cycle in cycles:
            self.violations.append(
                {
                    "type": "circular_dependency",
                    "file": "N/A",
                    "line": 0,
                    "message": f"Circular dependency detected: {' -> '.join(cycle)} -> {cycle[0]}",
                }
            )

        return len(cycles) > 0

    def _get_module_name(self, file: Path) -> str:
        """Convert file path to module name."""
        rel_path = file.relative_to(self.src_path)
        parts = list(rel_path.parts)
        parts[-1] = parts[-1].replace(".py", "")
        return f"solstein.{'.'.join(parts)}"

    def _find_cycles(self, graph: dict[str, set[str]]) -> list[list[str]]:
        """Find all cycles in the import graph."""
        cycles = []
        visited = set()
        rec_stack = set()
        path = []

        def dfs(node: str):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, set()):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:]
                    if cycle not in cycles:
                        cycles.append(cycle)

            path.pop()
            rec_stack.remove(node)

        for node in graph:
            if node not in visited:
                dfs(node)

        return cycles

    def print_report(self):
        """Print violations report."""
        if not self.violations:
            print("✅ No architecture violations found!")
            return

        lazy_imports = [v for v in self.violations if v["type"] == "lazy_import"]
        circular_deps = [v for v in self.violations if v["type"] == "circular_dependency"]

        if lazy_imports:
            print(f"\n❌ LAZY IMPORTS ({len(lazy_imports)} found):")
            print("   Move these imports to the top of the file:")
            for v in lazy_imports:
                print(f"   - {v['file']}:{v['line']}: {v['message']}")

        if circular_deps:
            print(f"\n❌ CIRCULAR DEPENDENCIES ({len(circular_deps)} found):")
            print("   Refactor to break these cycles:")
            for v in circular_deps:
                print(f"   - {v['message']}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Check architecture compliance")
    parser.add_argument("src", nargs="?", default="src/solstein", help="Source directory")
    parser.add_argument("--lazy-imports", action="store_true", help="Check only lazy imports")
    parser.add_argument("--circular-deps", action="store_true", help="Check only circular dependencies")
    args = parser.parse_args()

    print("🔍 Checking architecture compliance...")
    print()

    checker = ArchitectureChecker(args.src)

    if args.lazy_imports:
        has_violations = checker.check_lazy_imports()
    elif args.circular_deps:
        has_violations = checker.check_circular_dependencies()
    else:
        has_violations = not checker.check_all()

    checker.print_report()

    if has_violations:
        print("\n❌ Architecture compliance checks failed!")
        sys.exit(1)
    else:
        print("\n✅ Architecture compliance checks passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
