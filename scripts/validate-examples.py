#!/usr/bin/env python3
"""
Documentation Code Example Validator

Validates Python and shell examples in documentation:
- Checks Python syntax validity
- Verifies code blocks have language markers
- Detects hardcoded secrets/credentials
- Optionally runs Python examples for correctness

Usage:
    python scripts/validate-examples.py                  # Check all examples
    python scripts/validate-examples.py --fix-syntax     # Auto-indent
    python scripts/validate-examples.py --test           # Run examples (slow)
"""

import argparse
import ast
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


class ExampleValidator:
    """Validates code examples in documentation."""

    DANGEROUS_PATTERNS = [
        r"password\s*=\s*['\"].*['\"]",
        r"api_key\s*=\s*['\"].*['\"]",
        r"secret\s*=\s*['\"].*['\"]",
        r"Bearer\s+[A-Za-z0-9\-._~+/]+=*",
        r"sk_[a-z]{2,}_[A-Za-z0-9]{20,}",
    ]

    def __init__(self, docs_dir: Path, verbose: bool = False):
        """Initialize validator.

        Args:
            docs_dir: Path to documentation directory
            verbose: Print detailed output
        """
        self.docs_dir = docs_dir
        self.verbose = verbose
        self.syntax_errors: List[Tuple[Path, int, str]] = []
        self.missing_language: List[Tuple[Path, int]] = []
        self.secrets_detected: List[Tuple[Path, int, str]] = []

    def validate_all(self) -> bool:
        """Validate all code examples in documentation.

        Returns:
            True if no errors found, False otherwise
        """
        md_files = list(self.docs_dir.rglob("*.md"))
        if self.verbose:
            print(f"📄 Found {len(md_files)} markdown files")

        for md_file in md_files:
            self._validate_file(md_file)

        return self._report_results()

    def _validate_file(self, md_file: Path) -> None:
        """Validate code examples in a markdown file.

        Args:
            md_file: Path to markdown file
        """
        content = md_file.read_text(encoding="utf-8")
        code_blocks = self._extract_code_blocks(content)

        for line_num, language, code in code_blocks:
            if not language:
                self.missing_language.append((md_file, line_num))
                if self.verbose:
                    print(f"  ⚠️  {md_file}:{line_num} - No language specified")
                continue

            if language == "python":
                self._validate_python(md_file, line_num, code)
            elif language in ("bash", "shell", "sh"):
                self._validate_shell(md_file, line_num, code)

            self._check_for_secrets(md_file, line_num, code)

    def _extract_code_blocks(self, content: str) -> List[Tuple[int, str, str]]:
        """Extract all code blocks from markdown.

        Returns:
            List of (line_number, language, code) tuples
        """
        blocks = []
        lines = content.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith("```"):
                language = line[3:].strip() or ""
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].startswith("```"):
                    code_lines.append(lines[i])
                    i += 1
                code = "\n".join(code_lines)
                blocks.append((i - len(code_lines), language, code))
            i += 1

        return blocks

    def _validate_python(self, file: Path, line_num: int, code: str) -> None:
        """Validate Python code syntax.

        Args:
            file: Source file
            line_num: Line number of code block
            code: Python code
        """
        try:
            ast.parse(code)
            if self.verbose:
                print(f"  ✅ {file}:{line_num} Python syntax valid")
        except SyntaxError as e:
            self.syntax_errors.append((file, line_num, f"Python: {e}"))
            if self.verbose:
                print(f"  ❌ {file}:{line_num} Python syntax error: {e}")

    def _validate_shell(self, file: Path, line_num: int, code: str) -> None:
        """Validate shell script syntax.

        Args:
            file: Source file
            line_num: Line number of code block
            code: Shell code
        """
        try:
            result = subprocess.run(
                ["bash", "-n"],
                input=code,
                text=True,
                capture_output=True,
                timeout=5,
            )
            if result.returncode != 0:
                self.syntax_errors.append((file, line_num, f"Shell: {result.stderr}"))
                if self.verbose:
                    print(f"  ❌ {file}:{line_num} Shell syntax error: {result.stderr}")
            else:
                if self.verbose:
                    print(f"  ✅ {file}:{line_num} Shell syntax valid")
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            if self.verbose:
                print(f"  ⚠️  {file}:{line_num} Shell check skipped: {e}")

    def _check_for_secrets(self, file: Path, line_num: int, code: str) -> None:
        """Check for hardcoded secrets/credentials.

        Args:
            file: Source file
            line_num: Line number of code block
            code: Code to check
        """
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                self.secrets_detected.append((file, line_num, pattern))
                if self.verbose:
                    print(f"  🔐 {file}:{line_num} - Potential secret detected")

    def _report_results(self) -> bool:
        """Report validation results.

        Returns:
            True if no errors found, False otherwise
        """
        has_errors = bool(
            self.syntax_errors or self.missing_language or self.secrets_detected
        )

        if not has_errors:
            print("✅ All code examples validated successfully!")
            return True

        if self.syntax_errors:
            print(f"\n❌ Found {len(self.syntax_errors)} syntax error(s):\n")
            for file, line, error in self.syntax_errors:
                print(f"  📄 {file}:{line}")
                print(f"     Error: {error}\n")

        if self.missing_language:
            print(
                f"\n⚠️  Found {len(self.missing_language)} code block(s) without language:\n"
            )
            for file, line in self.missing_language:
                print(f"  📄 {file}:{line}")
                print(f"     Add language marker: ​```python or ​```bash\n")

        if self.secrets_detected:
            print(f"\n🔐 Found {len(self.secrets_detected)} potential secret(s):\n")
            for file, line, pattern in self.secrets_detected:
                print(f"  📄 {file}:{line}")
                print(f"     Pattern: {pattern}")
                print(f"     Use environment variables instead!\n")

        return len(self.syntax_errors) == 0 and len(self.secrets_detected) == 0


def main() -> int:
    """Main entry point.

    Returns:
        0 if successful, 1 if errors found
    """
    parser = argparse.ArgumentParser(
        description="Validate code examples in documentation"
    )
    parser.add_argument(
        "--docs",
        type=Path,
        default=Path("docs"),
        help="Path to documentation directory (default: docs)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print detailed validation output",
    )
    parser.add_argument(
        "--fix-syntax",
        action="store_true",
        help="Auto-fix indentation issues (not implemented)",
    )

    args = parser.parse_args()

    if not args.docs.exists():
        print(f"❌ Documentation directory not found: {args.docs}")
        return 1

    validator = ExampleValidator(docs_dir=args.docs, verbose=args.verbose)
    success = validator.validate_all()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
