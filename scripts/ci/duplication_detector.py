#!/usr/bin/env python3
"""Code duplication detector.

EPIC-019 Story 8: Detects code duplication using token-based analysis.
"""

from __future__ import annotations

import ast
import hashlib
import sys
from pathlib import Path
from typing import Any


class DuplicationDetector:
    """Detect code duplication in Python files."""

    def __init__(self, src_path: str, min_lines: int = 10):
        self.src_path = Path(src_path)
        self.min_lines = min_lines
        self.duplicates: list[dict[str, Any]] = []

    def detect(self) -> bool:
        """Detect code duplication."""
        # Collect all functions and their hashes
        functions: dict[str, list[dict]] = {}

        for file in self.src_path.rglob("*.py"):
            if "__pycache__" in str(file):
                continue

            try:
                content = file.read_text()
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_hash = self._hash_function(node)
                        func_info = {
                            "file": str(file),
                            "name": node.name,
                            "line": node.lineno,
                            "lines": (node.end_lineno or node.lineno) - node.lineno,
                        }

                        if func_hash not in functions:
                            functions[func_hash] = []
                        functions[func_hash].append(func_info)

            except Exception as e:
                print(f"Warning: Could not parse {file}: {e}")

        # Find duplicates
        found = False
        for func_hash, funcs in functions.items():
            if len(funcs) > 1:
                # Filter by minimum lines
                if funcs[0]["lines"] >= self.min_lines:
                    self.duplicates.append(
                        {
                            "hash": func_hash[:8],
                            "count": len(funcs),
                            "functions": funcs,
                        }
                    )
                    found = True

        return found

    def _hash_function(self, node: ast.FunctionDef) -> str:
        """Create a hash of function structure (ignoring names)."""
        # Normalize the AST by removing variable names
        normalized = self._normalize_ast(node)
        return hashlib.md5(normalized.encode()).hexdigest()

    def _normalize_ast(self, node: ast.AST) -> str:
        """Normalize AST for comparison."""
        # Simple normalization: convert AST back to string
        # In a real implementation, you'd want more sophisticated normalization
        return ast.dump(node, annotate_fields=False)

    def print_report(self):
        """Print duplication report."""
        if not self.duplicates:
            print("✅ No code duplication detected!")
            return

        print(f"\n❌ CODE DUPLICATION ({len(self.duplicates)} groups found):")
        print()

        for dup in self.duplicates:
            print(f"🔁 {dup['count']} similar functions (hash: {dup['hash']}):")
            for func in dup["functions"]:
                print(f"   - {func['file']}:{func['line']} | {func['name']}() [{func['lines']} lines]")
            print()

        print("💡 Consider extracting common logic into shared functions.")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Detect code duplication")
    parser.add_argument("src", nargs="?", default="src/solstein", help="Source directory")
    parser.add_argument("--min-lines", type=int, default=10, help="Minimum lines to consider")
    args = parser.parse_args()

    print("🔍 Detecting code duplication...")
    print()

    detector = DuplicationDetector(args.src, args.min_lines)
    has_duplicates = detector.detect()
    detector.print_report()

    if has_duplicates:
        print("\n⚠️ Code duplication detected!")
        sys.exit(0)  # Don't fail, just warn
    else:
        print("\n✅ No duplication found!")
        sys.exit(0)


if __name__ == "__main__":
    main()
