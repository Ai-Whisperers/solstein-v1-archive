#!/usr/bin/env python3
"""
Code Duplication Detection Script (EPIC-019 Story 8)

Detects duplicate/similar code blocks across the codebase using AST comparison.

Usage:
    python scripts/ci/detect_code_duplication.py [--threshold 0.8] [--min-lines 5]
"""

import argparse
import ast
import hashlib
import sys
from collections import defaultdict
from pathlib import Path


class CodeBlock:
    """Represents a code block for comparison."""

    def __init__(self, node: ast.AST, file_path: Path, start_line: int, end_line: int):
        self.node = node
        self.file_path = file_path
        self.start_line = start_line
        self.end_line = end_line
        self.hash = self._compute_hash()

    def _compute_hash(self) -> str:
        """Compute a structural hash of the AST node."""
        # Normalize the AST by removing variable names and literals
        normalized = self._normalize_ast(ast.dump(self.node))
        return hashlib.md5(normalized.encode()).hexdigest()[:16]

    def _normalize_ast(self, dump: str) -> str:
        """Normalize AST dump by replacing variable names and literals."""
        # This is a simplified normalization
        # In production, you'd want more sophisticated AST normalization
        return dump

    def __repr__(self):
        return f"{self.file_path}:{self.start_line}-{self.end_line}"


class DuplicationDetector:
    """Detects code duplication in Python files."""

    def __init__(self, min_lines: int = 5, similarity_threshold: float = 0.8):
        self.min_lines = min_lines
        self.similarity_threshold = similarity_threshold
        self.blocks: list[CodeBlock] = []
        self.duplicates: list[tuple[CodeBlock, CodeBlock, float]] = []

    def scan_directory(self, directory: Path) -> None:
        """Scan all Python files in directory for duplicates."""
        for py_file in directory.rglob("*.py"):
            if self._should_skip(py_file):
                continue
            self._scan_file(py_file)

    def _should_skip(self, file_path: Path) -> bool:
        """Check if file should be skipped."""
        skip_patterns = [
            "__pycache__",
            ".venv",
            "venv",
            "node_modules",
            ".git",
            "tests/",
            "test_",
            "_test.py",
        ]
        return any(pattern in str(file_path) for pattern in skip_patterns)

    def _scan_file(self, file_path: Path) -> None:
        """Scan a single file for code blocks."""
        try:
            content = file_path.read_text()
            tree = ast.parse(content)
        except (SyntaxError, UnicodeDecodeError):
            return

        for node in ast.walk(tree):
            # Extract function definitions
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                self._extract_block(node, file_path)
            # Extract if/else blocks
            elif isinstance(node, (ast.If, ast.For, ast.While, ast.With)):
                if hasattr(node, "body") and len(node.body) >= self.min_lines:
                    self._extract_block(node, file_path)

    def _extract_block(self, node: ast.AST, file_path: Path) -> None:
        """Extract a code block from an AST node."""
        start_line = getattr(node, "lineno", 0)
        end_line = getattr(node, "end_lineno", start_line)

        if end_line - start_line >= self.min_lines:
            block = CodeBlock(node, file_path, start_line, end_line)
            self.blocks.append(block)

    def find_duplicates(self) -> list[tuple[CodeBlock, CodeBlock, float]]:
        """Find duplicate/similar code blocks."""
        # Group blocks by hash
        hash_groups: dict[str, list[CodeBlock]] = defaultdict(list)
        for block in self.blocks:
            hash_groups[block.hash].append(block)

        # Find duplicates (same hash, different location)
        for hash_val, blocks in hash_groups.items():
            if len(blocks) > 1:
                # Report all pairs
                for i in range(len(blocks)):
                    for j in range(i + 1, len(blocks)):
                        similarity = self._compute_similarity(blocks[i], blocks[j])
                        if similarity >= self.similarity_threshold:
                            self.duplicates.append((blocks[i], blocks[j], similarity))

        return self.duplicates

    def _compute_similarity(self, block1: CodeBlock, block2: CodeBlock) -> float:
        """Compute similarity between two code blocks."""
        # For exact matches (same hash), similarity is 1.0
        if block1.hash == block2.hash:
            return 1.0

        # For near-matches, compute line-based similarity
        try:
            content1 = block1.file_path.read_text()
            content2 = block2.file_path.read_text()

            lines1 = content1.split("\n")[block1.start_line - 1 : block1.end_line]
            lines2 = content2.split("\n")[block2.start_line - 1 : block2.end_line]

            # Simple line-based similarity
            common = sum(1 for a, b in zip(lines1, lines2) if a.strip() == b.strip())
            total = max(len(lines1), len(lines2))

            return common / total if total > 0 else 0.0
        except Exception:
            return 0.0

    def print_report(self) -> int:
        """Print duplication report and return exit code."""
        print("=" * 80)
        print("CODE DUPLICATION DETECTION REPORT")
        print("=" * 80)
        print(f"\nScanned: {len(self.blocks)} code blocks")
        print(f"Found: {len(self.duplicates)} duplicate pairs\n")

        if not self.duplicates:
            print("✅ No code duplication detected!")
            return 0

        # Group by similarity level
        exact = [d for d in self.duplicates if d[2] >= 0.95]
        high = [d for d in self.duplicates if 0.85 <= d[2] < 0.95]
        medium = [d for d in self.duplicates if 0.70 <= d[2] < 0.85]

        if exact:
            print(f"\n🔴 EXACT DUPLICATES ({len(exact)} pairs):")
            for block1, block2, sim in exact:
                print(f"  {block1} ~~~ {block2} ({sim:.0%} similar)")

        if high:
            print(f"\n🟠 HIGH SIMILARITY ({len(high)} pairs):")
            for block1, block2, sim in high[:10]:  # Limit output
                print(f"  {block1} ~~~ {block2} ({sim:.0%} similar)")

        if medium:
            print(f"\n🟡 MEDIUM SIMILARITY ({len(medium)} pairs, showing first 10):")
            for block1, block2, sim in medium[:10]:
                print(f"  {block1} ~~~ {block2} ({sim:.0%} similar)")

        print("\n" + "=" * 80)
        print("RECOMMENDATIONS:")
        print("=" * 80)
        print("- Extract duplicate logic into shared functions")
        print("- Use inheritance or composition for similar classes")
        print("- Consider strategy pattern for similar algorithms")
        print("- Review exact duplicates for accidental copy-paste")

        return 1 if exact else 0


def main():
    parser = argparse.ArgumentParser(description="Detect code duplication in Python codebase")
    parser.add_argument(
        "--directory",
        type=Path,
        default=Path("src"),
        help="Directory to scan (default: src)",
    )
    parser.add_argument(
        "--min-lines",
        type=int,
        default=5,
        help="Minimum lines to consider (default: 5)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.8,
        help="Similarity threshold 0-1 (default: 0.8)",
    )
    parser.add_argument(
        "--fail-on-exact",
        action="store_true",
        help="Fail CI if exact duplicates found",
    )

    args = parser.parse_args()

    detector = DuplicationDetector(
        min_lines=args.min_lines,
        similarity_threshold=args.threshold,
    )

    print(f"🔍 Scanning {args.directory} for code duplication...")
    print(f"   Min lines: {args.min_lines}")
    print(f"   Similarity threshold: {args.threshold}")
    print()

    detector.scan_directory(args.directory)
    detector.find_duplicates()

    exit_code = detector.print_report()

    if args.fail_on_exact:
        exact = [d for d in detector.duplicates if d[2] >= 0.95]
        if exact:
            sys.exit(1)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
