#!/usr/bin/env python3
"""EPIC-020 pattern validator for CI/CD.

EPIC-019 Story 13: Validates that new code follows patterns established in EPIC-020:
- Pipeline stages follow Stage pattern
- Provider clients use Strategy pattern
- Extractor functions are pure functions
- Helper modules have consistent naming

Usage:
    python validate_epic020_patterns.py [src_path]

Exit codes:
    0 - All patterns valid
    1 - Pattern violations detected
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Any


class EPIC020PatternValidator:
    """Validate EPIC-020 established patterns."""

    # Pattern definitions
    STAGE_PATTERN = {
        "required_methods": ["execute", "run"],  # Accept either execute() or run()
        "optional_methods": ["validate", "cleanup"],
        "naming": "*Stage",
    }

    STRATEGY_PATTERN = {
        "required_methods": ["execute", "create_client"],
        "optional_methods": ["validate", "health_check"],
        "naming": "*Strategy",
    }

    EXTRACTOR_PATTERN = {
        "naming": "_extract_*",
        "pure_function": True,
    }

    HELPER_MODULE_PATTERNS = {
        "*_helpers.py": "Helper functions",
        "*_strategies.py": "Strategy pattern implementations",
        "*_stages.py": "Pipeline stage classes",
        "*_builders.py": "Builder pattern implementations",
        "*_extractors.py": "Data extraction functions",
        "*_executors.py": "Execution classes",
    }

    def __init__(self, src_path: str):
        self.src_path = Path(src_path)
        self.violations: list[dict[str, Any]] = []

    def validate_all(self) -> bool:
        """Run all pattern validations."""
        has_violations = False

        has_violations |= self.validate_stage_classes()
        has_violations |= self.validate_strategy_classes()
        has_violations |= self.validate_extractor_functions()
        has_violations |= self.validate_helper_module_naming()

        return has_violations

    def validate_stage_classes(self) -> bool:
        """Validate that Stage classes follow the pattern."""
        found = False

        for file in self.src_path.rglob("*.py"):
            if "__pycache__" in str(file):
                continue

            try:
                content = file.read_text()
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Check if it's a Stage class
                        if node.name.endswith("Stage"):
                            methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                            
                            # Check for inheritance - if inherits from PipelineStage, it has execute()
                            has_inherited_execute = False
                            for base in node.bases:
                                if isinstance(base, ast.Name) and base.id == "PipelineStage":
                                    has_inherited_execute = True
                                    break
                                elif isinstance(base, ast.Attribute):
                                    if base.attr == "PipelineStage":
                                        has_inherited_execute = True
                                        break

                            # Check required methods - need at least one of execute() or run()
                            has_execute = "execute" in methods or has_inherited_execute
                            has_run = "run" in methods

                            if not (has_execute or has_run):
                                self.violations.append(
                                    {
                                        "type": "stage_pattern",
                                        "file": str(file),
                                        "line": node.lineno,
                                        "class": node.name,
                                        "issue": "Missing required method: Stage classes must have execute() or run() method",
                                        "severity": "error",
                                    }
                                )
                                found = True

                            # Check for execute/run method signature
                            method_name = "execute" if has_execute else "run"
                            if has_execute or has_run:
                                execute_method = next(
                                    n for n in node.body if isinstance(n, ast.FunctionDef) and n.name == method_name
                                )
                                if not self._has_proper_execute_signature(execute_method):
                                    self.violations.append(
                                        {
                                            "type": "stage_pattern",
                                            "file": str(file),
                                            "line": node.lineno,
                                            "class": node.name,
                                            "issue": f"{method_name}() method should accept **kwargs for flexibility",
                                            "severity": "warning",
                                        }
                                    )

            except Exception as e:
                print(f"Warning: Could not parse {file}: {e}")

        return found

    def _has_proper_execute_signature(self, node: ast.FunctionDef) -> bool:
        """Check if execute method has proper signature."""
        # Should accept self and **kwargs
        args = node.args
        has_kwargs = args.kwarg is not None
        return has_kwargs

    def validate_strategy_classes(self) -> bool:
        """Validate that Strategy classes follow the pattern."""
        found = False

        for file in self.src_path.rglob("*strategy*.py"):
            if "__pycache__" in str(file):
                continue

            try:
                content = file.read_text()
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Check if it's a Strategy class
                        if node.name.endswith("Strategy") and node.name != "Strategy":
                            methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]

                            # Check required methods
                            for required in self.STRATEGY_PATTERN["required_methods"]:
                                if required not in methods:
                                    self.violations.append(
                                        {
                                            "type": "strategy_pattern",
                                            "file": str(file),
                                            "line": node.lineno,
                                            "class": node.name,
                                            "issue": f"Missing required method: {required}",
                                            "severity": "error",
                                        }
                                    )
                                    found = True

            except Exception as e:
                print(f"Warning: Could not parse {file}: {e}")

        return found

    def validate_extractor_functions(self) -> bool:
        """Validate that extractor functions follow the pattern."""
        found = False

        for file in self.src_path.rglob("*extractor*.py"):
            if "__pycache__" in str(file):
                continue

            try:
                content = file.read_text()
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Check if it's an extractor function
                        if node.name.startswith("_extract_"):
                            # Check for side effects (should be pure)
                            has_side_effects = self._has_side_effects(node)
                            if has_side_effects:
                                self.violations.append(
                                    {
                                        "type": "extractor_pattern",
                                        "file": str(file),
                                        "line": node.lineno,
                                        "function": node.name,
                                        "issue": "Extractor functions should be pure (no side effects)",
                                        "severity": "warning",
                                    }
                                )
                                found = True

            except Exception as e:
                print(f"Warning: Could not parse {file}: {e}")

        return found

    def _has_side_effects(self, node: ast.FunctionDef) -> bool:
        """Check if function has side effects (simplified check)."""
        for child in ast.walk(node):
            # Check for print statements
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name) and child.func.id == "print":
                    return True
            # Check for file operations
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Attribute):
                    if child.func.attr in ["write", "append", "save"]:
                        return True
        return False

    def validate_helper_module_naming(self) -> bool:
        """Validate helper module naming conventions."""
        found = False

        for file in self.src_path.rglob("*.py"):
            if "__pycache__" in str(file):
                continue

            filename = file.name

            # Check if it's a helper module
            is_helper = any(
                filename.endswith(pattern.replace("*", "")) for pattern in self.HELPER_MODULE_PATTERNS.keys()
            )

            if is_helper:
                # Check for module docstring
                try:
                    content = file.read_text()
                    tree = ast.parse(content)

                    has_docstring = False
                    if ast.get_docstring(tree):
                        has_docstring = True

                    if not has_docstring:
                        self.violations.append(
                            {
                                "type": "helper_naming",
                                "file": str(file),
                                "line": 1,
                                "issue": f"Helper module {filename} should have a module-level docstring",
                                "severity": "warning",
                            }
                        )
                        found = True

                except Exception as e:
                    print(f"Warning: Could not parse {file}: {e}")

        return found

    def print_report(self) -> bool:
        """Print validation report. Returns True if violations found."""
        print("=" * 80)
        print("EPIC-020 PATTERN VALIDATION REPORT")
        print("=" * 80)

        print("\n📋 Patterns Validated:")
        print("  • Stage Pattern: Classes ending with 'Stage' must have execute() or run() method")
        print("  • Strategy Pattern: Classes ending with 'Strategy' must have execute() and create_client()")
        print("  • Extractor Pattern: Functions starting with '_extract_' should be pure")
        print("  • Helper Naming: Helper modules should have docstrings")

        has_violations = self.validate_all()

        if self.violations:
            print(f"\n❌ VIOLATIONS ({len(self.violations)} found):")
            print()

            # Group by type
            by_type: dict[str, list[dict]] = {}
            for v in self.violations:
                by_type.setdefault(v["type"], []).append(v)

            for vtype, violations in sorted(by_type.items()):
                print(f"🔴 {vtype.replace('_', ' ').title()} ({len(violations)}):")
                for v in violations:
                    emoji = "❌" if v["severity"] == "error" else "⚠️"
                    print(f"   {emoji} {v['file']}:{v.get('line', 'N/A')}")
                    if "class" in v:
                        print(f"      Class: {v['class']}")
                    if "function" in v:
                        print(f"      Function: {v['function']}")
                    print(f"      Issue: {v['issue']}")
                print()

            print("💡 To fix:")
            print("   • Stage classes: Add execute() or run() method")
            print("   • Strategy classes: Add execute() and create_client() methods")
            print("   • Extractor functions: Remove side effects (print, file writes)")
            print("   • Helper modules: Add module-level docstring")

            return True
        else:
            print("\n✅ All EPIC-020 patterns validated successfully!")
            print("   Code follows established architectural patterns.")
            return False


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Validate EPIC-020 patterns")
    parser.add_argument("src", nargs="?", default="src/solstein", help="Source directory")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    args = parser.parse_args()

    validator = EPIC020PatternValidator(args.src)

    if args.json:
        import json

        has_violations = validator.validate_all()
        output = {
            "violation_count": len(validator.violations),
            "violations": validator.violations,
            "patterns_validated": list(validator.HELPER_MODULE_PATTERNS.keys()),
        }
        print(json.dumps(output, indent=2))
        sys.exit(0 if not has_violations else 1)

    has_violations = validator.print_report()

    if has_violations:
        print("\n❌ EPIC-020 pattern validation FAILED!")
        print("   Please fix the violations above.")
        sys.exit(1)
    else:
        print("\n✅ EPIC-020 pattern validation PASSED!")
        sys.exit(0)


if __name__ == "__main__":
    main()
