#!/usr/bin/env python3
"""Automated refactoring bot.

EPIC-019 Story 9: Suggests and applies automated refactoring for common issues.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any


class RefactoringBot:
    """Bot that suggests automated refactoring."""

    def __init__(self, src_path: str):
        self.src_path = Path(src_path)
        self.suggestions: list[dict[str, Any]] = []

    def analyze(self) -> list[dict[str, Any]]:
        """Analyze codebase and generate refactoring suggestions."""
        self._find_bare_excepts()
        self._find_lazy_imports()
        self._find_long_functions()
        return self.suggestions

    def _find_bare_excepts(self):
        """Find bare except clauses that can be auto-fixed."""
        for file in self.src_path.rglob("*.py"):
            if "__pycache__" in str(file):
                continue

            try:
                content = file.read_text()
                lines = content.splitlines()

                for i, line in enumerate(lines, 1):
                    stripped = line.strip()
                    if stripped == "except:":
                        self.suggestions.append(
                            {
                                "file": str(file),
                                "line": i,
                                "type": "bare_except",
                                "original": line,
                                "suggested": line.replace("except:", "except Exception:"),
                                "confidence": "high",
                            }
                        )
            except Exception:
                pass

    def _find_lazy_imports(self):
        """Find lazy imports that should be moved."""
        for file in self.src_path.rglob("*.py"):
            if "__pycache__" in str(file):
                continue

            try:
                content = file.read_text()
                tree = ast.parse(content)

                # Track function ranges
                function_ranges = []
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        function_ranges.append((node.lineno, node.end_lineno or node.lineno))

                # Check for imports inside functions
                for node in ast.walk(tree):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        import_line = node.lineno

                        for func_start, func_end in function_ranges:
                            if func_start < import_line <= func_end:
                                lines = content.splitlines()
                                original = lines[import_line - 1]

                                self.suggestions.append(
                                    {
                                        "file": str(file),
                                        "line": import_line,
                                        "type": "lazy_import",
                                        "original": original,
                                        "suggested": f"# TODO: Move to top of file\n# {original.strip()}",
                                        "confidence": "medium",
                                    }
                                )
                                break

            except Exception:
                pass

    def _find_long_functions(self):
        """Find long functions that could be extracted."""
        for file in self.src_path.rglob("*.py"):
            if "__pycache__" in str(file):
                continue

            try:
                content = file.read_text()
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        lines = (node.end_lineno or node.lineno) - node.lineno
                        if lines > 50:
                            self.suggestions.append(
                                {
                                    "file": str(file),
                                    "line": node.lineno,
                                    "type": "long_function",
                                    "original": f"def {node.name}(...)",
                                    "suggested": f"# TODO: Break into smaller functions ({lines} lines)",
                                    "confidence": "low",
                                }
                            )

            except Exception:
                pass

    def generate_report(self) -> str:
        """Generate refactoring report."""
        if not self.suggestions:
            return "✅ No refactoring suggestions found!"

        report = ["## 🤖 Automated Refactoring Suggestions\n"]

        # Group by type
        by_type: dict[str, list] = {}
        for s in self.suggestions:
            by_type.setdefault(s["type"], []).append(s)

        for type_name, suggestions in by_type.items():
            report.append(f"### {type_name.replace('_', ' ').title()} ({len(suggestions)})")
            report.append()

            for s in suggestions:
                report.append(f"**{s['file']}:{s['line']}** (confidence: {s['confidence']})")
                report.append("```python")
                report.append("# Original:")
                report.append(str(s["original"]))
                report.append("")
                report.append("# Suggested:")
                report.append(str(s["suggested"]))
                report.append("```")
                report.append("")

        return "\n".join(report)

    def apply_suggestion(self, suggestion: dict[str, Any]) -> bool:
        """Apply a single refactoring suggestion."""
        try:
            file = Path(suggestion["file"])
            if not file.exists():
                return False

            content = file.read_text()
            lines = content.splitlines()

            line_idx = suggestion["line"] - 1
            if line_idx >= len(lines):
                return False

            # Apply the change
            lines[line_idx] = suggestion["suggested"]

            file.write_text("\n".join(lines))
            return True

        except Exception as e:
            print(f"Failed to apply suggestion: {e}")
            return False


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Automated refactoring bot")
    parser.add_argument("src", nargs="?", default="src/solstein", help="Source directory")
    parser.add_argument("--apply", action="store_true", help="Apply high-confidence suggestions")
    parser.add_argument("--output", help="Output file for report")
    args = parser.parse_args()

    print("🤖 Running automated refactoring bot...")
    print()

    bot = RefactoringBot(args.src)
    suggestions = bot.analyze()

    report = bot.generate_report()

    if args.output:
        Path(args.output).write_text(report)
        print(f"✅ Report written to {args.output}")
    else:
        print(report)

    if args.apply:
        high_confidence = [s for s in suggestions if s["confidence"] == "high"]
        print(f"\n🔧 Applying {len(high_confidence)} high-confidence suggestions...")

        applied = 0
        for suggestion in high_confidence:
            if bot.apply_suggestion(suggestion):
                applied += 1

        print(f"✅ Applied {applied} suggestions")


if __name__ == "__main__":
    main()
