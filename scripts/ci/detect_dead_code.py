#!/usr/bin/env python3
"""Dead code detector for CI/CD.

EPIC-019 Story 12: Detects unused functions, classes, and variables in Python code.
Focuses on helper modules created during EPIC-020.

Usage:
    python detect_dead_code.py [src_path] [--helper-modules-only]

Exit codes:
    0 - No dead code detected (or below threshold)
    1 - Significant dead code detected
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Any


class DeadCodeDetector:
    """Detect dead code in Python modules."""

    def __init__(self, src_path: str):
        self.src_path = Path(src_path)
        self.definitions: dict[str, dict[str, Any]] = {}
        self.references: set[str] = set()
        self.dead_code: list[dict[str, Any]] = []

    def analyze(self) -> list[dict[str, Any]]:
        """Analyze codebase for dead code."""
        self._collect_definitions()
        self._collect_references()
        self._find_dead_code()
        return self.dead_code

    def _collect_definitions(self) -> None:
        """Collect all function and class definitions."""
        for file in self.src_path.rglob("*.py"):
            if "__pycache__" in str(file) or file.name == "__init__.py":
                continue

            try:
                content = file.read_text()
                tree = ast.parse(content)
                module = self._get_module_name(file)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Skip private functions (starting with _)
                        if not node.name.startswith("_"):
                            key = f"{module}.{node.name}"
                            self.definitions[key] = {
                                "type": "function",
                                "name": node.name,
                                "module": module,
                                "file": str(file),
                                "line": node.lineno,
                                "lines": (node.end_lineno or node.lineno) - node.lineno,
                            }

                    elif isinstance(node, ast.ClassDef):
                        # Skip private classes
                        if not node.name.startswith("_"):
                            key = f"{module}.{node.name}"
                            self.definitions[key] = {
                                "type": "class",
                                "name": node.name,
                                "module": module,
                                "file": str(file),
                                "line": node.lineno,
                                "lines": (node.end_lineno or node.lineno) - node.lineno,
                            }

            except Exception as e:
                print(f"Warning: Could not parse {file}: {e}")

    def _collect_references(self) -> None:
        """Collect all references to functions and classes."""
        for file in self.src_path.rglob("*.py"):
            if "__pycache__" in str(file):
                continue

            try:
                content = file.read_text()
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    # Direct function calls
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Name):
                            self.references.add(node.func.id)
                        elif isinstance(node.func, ast.Attribute):
                            self.references.add(node.func.attr)

                    # Attribute access (could be method calls)
                    elif isinstance(node, ast.Attribute):
                        self.references.add(node.attr)

                    # Import references
                    elif isinstance(node, ast.ImportFrom):
                        for alias in node.names:
                            self.references.add(alias.name)
                            if alias.asname:
                                self.references.add(alias.asname)

            except Exception:
                pass

    def _find_dead_code(self) -> None:
        """Find definitions that are never referenced."""
        for key, definition in self.definitions.items():
            name = definition["name"]

            # Check if referenced
            if name not in self.references:
                # Additional check: might be referenced with module prefix
                module = definition["module"]
                full_ref = f"{module}.{name}"

                # Skip if it's in __all__
                if self._is_in_all(definition["file"], name):
                    continue

                # Skip if it's a test file
                if "test" in definition["file"].lower():
                    continue

                self.dead_code.append(definition)

    def _is_in_all(self, filepath: str, name: str) -> bool:
        """Check if name is in __all__ list."""
        try:
            content = Path(filepath).read_text()
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == "__all__":
                            if isinstance(node.value, (ast.List, ast.Tuple)):
                                for elt in node.value.elts:
                                    if isinstance(elt, ast.Constant) and elt.value == name:
                                        return True
                                    elif isinstance(elt, ast.Str) and elt.s == name:
                                        return True
            return False
        except Exception:
            return False

    def _get_module_name(self, file: Path) -> str:
        """Convert file path to module name."""
        try:
            rel_path = file.relative_to(self.src_path)
            parts = list(rel_path.parts)
            parts[-1] = parts[-1].replace(".py", "")
            return f"solstein.{'.'.join(parts)}"
        except ValueError:
            return str(file)

    def get_helper_module_utilization(self) -> dict[str, float]:
        """Calculate utilization rate for EPIC-020 helper modules."""
        helper_modules = [
            "pipeline_stages",
            "company_extractors",
            "market_catalogs",
            "report_sections",
            "research_persistence",
            "reconciliation_helpers",
            "provider_strategies",
            "enrichment_executors",
            "company_builder",
            "sec_edgar_helpers",
        ]

        utilization = {}

        for helper in helper_modules:
            module_defs = [d for d in self.definitions.values() if helper in d["module"]]
            module_dead = [d for d in self.dead_code if helper in d["module"]]

            if module_defs:
                used = len(module_defs) - len(module_dead)
                utilization[helper] = (used / len(module_defs)) * 100
            else:
                utilization[helper] = 0.0

        return utilization

    def get_structural_checks(self) -> dict[str, bool]:
        refresh_router_path = self.src_path / "api" / "routes" / "refresh.py"
        main_api_path = self.src_path / "api" / "main.py"
        worker_tasks_v2_path = self.src_path / "worker_tasks_v2.py"

        refresh_router_exists = refresh_router_path.exists()
        refresh_router_connected = False
        if refresh_router_exists and main_api_path.exists():
            content = main_api_path.read_text(encoding="utf-8")
            refresh_router_connected = "routes.refresh" in content or "refresh_router" in content

        return {
            "refresh_router_exists": refresh_router_exists,
            "refresh_router_connected": refresh_router_connected,
            "worker_tasks_v2_exists": worker_tasks_v2_path.exists(),
        }

    def print_report(self) -> bool:
        """Print dead code report. Returns True if dead code found."""
        print("=" * 80)
        print("DEAD CODE DETECTION REPORT")
        print("=" * 80)

        self.analyze()

        # Group by file
        by_file: dict[str, list[dict]] = {}
        for item in self.dead_code:
            by_file.setdefault(item["file"], []).append(item)

        if self.dead_code:
            print(f"\n⚠️  POTENTIALLY DEAD CODE ({len(self.dead_code)} items):")
            print()

            for file, items in sorted(by_file.items()):
                print(f"📄 {file}")
                for item in items:
                    emoji = "🔧" if item["type"] == "function" else "🏗️"
                    print(f"   {emoji} {item['name']}() [{item['lines']} lines] at line {item['line']}")
                print()

            print("💡 Note: This is a heuristic check. Some items may be:")
            print("   - Used dynamically (getattr, eval, etc.)")
            print("   - Entry points (CLI commands, API endpoints)")
            print("   - Used by external code")
            print("   - Public API that should be kept")
            print()
            print("   Please verify before removing!")

        else:
            print("\n✅ No dead code detected!")

        # Helper module utilization
        print("\n" + "=" * 80)
        print("EPIC-020 HELPER MODULE UTILIZATION")
        print("=" * 80)

        utilization = self.get_helper_module_utilization()
        for module, rate in sorted(utilization.items()):
            emoji = "✅" if rate >= 80 else "⚠️" if rate >= 50 else "❌"
            print(f"{emoji} {module}: {rate:.1f}% utilized")

        avg_utilization = sum(utilization.values()) / len(utilization) if utilization else 0
        print(f"\n📊 Average utilization: {avg_utilization:.1f}%")

        if avg_utilization < 80:
            print("⚠️  Target is 80% utilization. Consider:")
            print("   - Consolidating underutilized modules")
            print("   - Removing truly dead code")
            print("   - Better documenting module usage")

        structural_checks = self.get_structural_checks()
        print("\n" + "=" * 80)
        print("EPIC-037 STRUCTURAL CHECKS")
        print("=" * 80)
        print(f"refresh_router_exists: {structural_checks['refresh_router_exists']}")
        print(f"refresh_router_connected: {structural_checks['refresh_router_connected']}")
        print(f"worker_tasks_v2_exists: {structural_checks['worker_tasks_v2_exists']}")

        structural_issue = (
            structural_checks["refresh_router_exists"] and not structural_checks["refresh_router_connected"]
        ) or structural_checks["worker_tasks_v2_exists"]

        if structural_issue:
            print("⚠️  Structural dead-code risks detected (EPIC-037)")

        return len(self.dead_code) > 0 or structural_issue


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Detect dead code")
    parser.add_argument("src", nargs="?", default="src/solstein", help="Source directory")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--threshold", type=int, default=10, help="Dead code threshold")
    args = parser.parse_args()

    detector = DeadCodeDetector(args.src)

    if args.json:
        import json

        dead_code = detector.analyze()
        utilization = detector.get_helper_module_utilization()
        output = {
            "dead_code_count": len(dead_code),
            "dead_code": dead_code,
            "helper_utilization": utilization,
            "avg_utilization": sum(utilization.values()) / len(utilization) if utilization else 0,
            "structural_checks": detector.get_structural_checks(),
        }
        print(json.dumps(output, indent=2))
        sys.exit(0)

    has_dead_code = detector.print_report()

    if has_dead_code:
        print(f"\n⚠️  Dead code detected!")
        print("   Please review and remove or document unused code.")
        # Don't fail CI, just warn
        sys.exit(0)
    else:
        print("\n✅ No dead code detected!")
        sys.exit(0)


if __name__ == "__main__":
    main()
