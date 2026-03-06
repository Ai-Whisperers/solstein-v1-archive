"""Code Smell Detector for CI/CD

Automatically detects code smells in Python files:
- God functions (>100 lines)
- Long functions (50-100 lines)
- Many parameters (>5)
- Deep nesting (>4 levels)
- Bare except clauses
- God classes (>300 lines)

Usage:
    python code_smell_detector.py [files...]

If no files provided, analyzes all changed files in git.
"""

import ast
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import subprocess


@dataclass
class FunctionSmell:
    file: str
    name: str
    line: int
    lines: int
    params: int
    nesting: int
    severity: str  # 'critical' if >100, 'warning' if >50


@dataclass
class ClassSmell:
    file: str
    name: str
    line: int
    lines: int
    methods: int
    severity: str


@dataclass
class ExceptSmell:
    file: str
    line: int
    code: str


class CodeSmellDetector:
    def __init__(self):
        self.function_smells: list[FunctionSmell] = []
        self.class_smells: list[ClassSmell] = []
        self.except_smells: list[ExceptSmell] = []

    def analyze_file(self, filepath: Path) -> None:
        """Analyze a single Python file."""
        try:
            content = filepath.read_text()
            tree = ast.parse(content)
            lines = content.split("\n")
        except Exception as e:
            print(f"Error parsing {filepath}: {e}")
            return

        file_rel = str(filepath)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self._analyze_function(node, file_rel, lines)
            elif isinstance(node, ast.ClassDef):
                self._analyze_class(node, file_rel, lines)

        # Check for bare excepts
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped == "except:" or stripped.startswith("except Exception"):
                self.except_smells.append(ExceptSmell(file=file_rel, line=i, code=stripped[:60]))

    def _analyze_function(self, node: ast.FunctionDef, file: str, lines: list[str]) -> None:
        """Analyze a function for smells."""
        func_lines = node.end_lineno - node.lineno if node.end_lineno else 0
        params = len(node.args.args) + len(node.args.kwonlyargs)
        if node.args.vararg:
            params += 1
        if node.args.kwarg:
            params += 1

        # Count nesting levels
        nesting = self._count_nesting(node)

        # Determine severity
        if func_lines > 100 or params > 8 or nesting > 6:
            severity = "critical"
        elif func_lines > 50 or params > 5 or nesting > 4:
            severity = "warning"
        else:
            return

        self.function_smells.append(
            FunctionSmell(
                file=file,
                name=node.name,
                line=node.lineno,
                lines=func_lines,
                params=params,
                nesting=nesting,
                severity=severity,
            )
        )

    def _analyze_class(self, node: ast.ClassDef, file: str, lines: list[str]) -> None:
        """Analyze a class for smells."""
        cls_lines = node.end_lineno - node.lineno if node.end_lineno else 0
        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]

        if cls_lines > 300 or len(methods) > 15:
            severity = "critical" if cls_lines > 400 else "warning"
            self.class_smells.append(
                ClassSmell(
                    file=file,
                    name=node.name,
                    line=node.lineno,
                    lines=cls_lines,
                    methods=len(methods),
                    severity=severity,
                )
            )

    def _count_nesting(self, node: ast.FunctionDef) -> int:
        """Count maximum nesting depth in function."""
        max_depth = 0

        def visit(node, depth=0):
            nonlocal max_depth
            if isinstance(node, (ast.If, ast.For, ast.While, ast.With, ast.Try, ast.ExceptHandler)):
                depth += 1
                max_depth = max(max_depth, depth)
            for child in ast.iter_child_nodes(node):
                visit(child, depth)

        for child in ast.iter_child_nodes(node):
            visit(child, 0)

        return max_depth

    def report(self) -> bool:
        """Print report and return True if critical issues found."""
        has_critical = False

        print("=" * 80)
        print("CODE SMELL DETECTION REPORT")
        print("=" * 80)

        # Critical function smells
        critical_funcs = [s for s in self.function_smells if s.severity == "critical"]
        if critical_funcs:
            has_critical = True
            print(f"\n🔴 CRITICAL FUNCTION SMELLS ({len(critical_funcs)}):")
            for smell in sorted(critical_funcs, key=lambda x: x.lines, reverse=True):
                print(
                    f"  {smell.lines:4d} lines | {smell.params} params | {smell.nesting} nesting | {smell.file}:{smell.line} | {smell.name}"
                )

        # Warning function smells
        warning_funcs = [s for s in self.function_smells if s.severity == "warning"]
        if warning_funcs:
            print(f"\n🟡 WARNING FUNCTION SMELLS ({len(warning_funcs)}):")
            for smell in sorted(warning_funcs, key=lambda x: x.lines, reverse=True)[:20]:
                print(
                    f"  {smell.lines:4d} lines | {smell.params} params | {smell.nesting} nesting | {smell.file}:{smell.line} | {smell.name}"
                )

        # Class smells
        if self.class_smells:
            critical_classes = [s for s in self.class_smells if s.severity == "critical"]
            if critical_classes:
                has_critical = True
                print(f"\n🔴 CRITICAL CLASS SMELLS ({len(critical_classes)}):")
                for smell in critical_classes:
                    print(
                        f"  {smell.lines:4d} lines | {smell.methods} methods | {smell.file}:{smell.line} | {smell.name}"
                    )

        # Bare excepts
        if self.except_smells:
            print(f"\n🚫 BARE EXCEPT CLAUSES ({len(self.except_smells)}):")
            for smell in self.except_smells[:10]:
                print(f"  {smell.file}:{smell.line} | {smell.code}")
            if len(self.except_smells) > 10:
                print(f"  ... and {len(self.except_smells) - 10} more")

        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Critical function smells: {len(critical_funcs)}")
        print(f"Warning function smells:  {len(warning_funcs)}")
        print(f"Class smells:             {len(self.class_smells)}")
        print(f"Bare except clauses:      {len(self.except_smells)}")
        print(f"\nTotal issues: {len(self.function_smells) + len(self.class_smells) + len(self.except_smells)}")

        return has_critical


def get_changed_files() -> list[Path]:
    """Get list of changed Python files from git."""
    try:
        result = subprocess.run(["git", "diff", "--name-only", "HEAD~1", "HEAD"], capture_output=True, text=True)
        files = []
        for line in result.stdout.strip().split("\n"):
            if line.endswith(".py") and not "__pycache__" in line:
                path = Path(line)
                if path.exists():
                    files.append(path)
        return files
    except Exception:
        return []


def main():
    if len(sys.argv) > 1:
        # Analyze specified files
        files = [Path(f) for f in sys.argv[1:]]
    else:
        # Analyze changed files
        files = get_changed_files()
        if not files:
            print("No Python files changed in latest commit")
            sys.exit(0)

    detector = CodeSmellDetector()

    for file in files:
        if file.exists() and file.suffix == ".py":
            detector.analyze_file(file)

    has_critical = detector.report()

    if has_critical:
        print("\n❌ CI FAILED: Critical code smells detected!")
        print("   Please break down large functions/classes before merging.")
        sys.exit(1)
    else:
        print("\n✅ No critical code smells detected.")
        sys.exit(0)


if __name__ == "__main__":
    main()
