#!/usr/bin/env python3
"""
OpenCode Compliance Checker

This module provides validation and compliance checking mechanisms for OpenCode standards.
It validates code against the rules defined in the .claude/rules directory.
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass
import json
import ast
import tokenize
from io import BytesIO


class ValidationResult:
    """Result of a validation check."""

    def __init__(
        self,
        rule: str,
        file: str,
        line: Optional[int],
        column: Optional[int],
        message: str,
        severity: str,
        passed: bool,
    ):
        self.rule = rule
        self.file = file
        self.line = line
        self.column = column
        self.message = message
        self.severity = severity
        self.passed = passed


class ComplianceChecker:
    """Main compliance checker for OpenCode standards."""

    def __init__(self):
        self.rules_dir = Path(".claude/rules")
        self.rules: Dict[str, Dict] = {}
        self.load_rules()

    def load_rules(self):
        """Load validation rules from the rules directory."""
        if not self.rules_dir.exists():
            return

        for rule_file in self.rules_dir.glob("*.md"):
            rule_name = rule_file.stem
            try:
                with open(rule_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    if rule_name == "testing":
                        self.rules[rule_name] = {
                            "file": str(rule_file),
                            "content": content,
                            "category": "testing",
                            "patterns": [
                                "def t():",
                                "def test_no_assert():",
                                "assert os.path.exists('/path/to/file')",
                                "global_counter = 0",
                                "risky_operation()",
                                "temp_file = open('temp.txt')",
                                "assert add(2, 2) == 4",
                            ],
                            "requirements": [
                                "Test Coverage",
                                "Test Organization",
                                "Test Isolation",
                                "Test Naming",
                                "Test Data",
                                "Test Pollution",
                                "Brittle Tests",
                                "Over-Mocking",
                                "Slow Tests",
                                "Test Code Duplication",
                            ],
                            "severity": "warning",
                            "custom_validators": [validate_python_syntax],
                        }
                        print(
                            f"[93mDEBUG: Loaded testing rule with {len(self.rules[rule_name]['patterns'])} patterns[0m"
                        )
                    else:
                        self.rules[rule_name] = {
                            "file": str(rule_file),
                            "content": content,
                            "category": self._extract_category(content),
                            "patterns": self._extract_patterns(content),
                            "requirements": self._extract_requirements(content),
                            "severity": self._extract_severity(content),
                            "custom_validators": self._extract_custom_validators(
                                content
                            ),
                        }
            except Exception as e:
                print(f"Error loading rule {rule_name}: {e}")

    def _extract_category(self, content: str) -> str:
        """Extract category from rule content."""
        categories = {
            "testing": ["testing", "test", "unit test", "integration test"],
            "api": ["api", "rest", "graphql", "endpoint"],
            "database": ["database", "sql", "migration", "orm"],
            "deployment": ["deployment", "ci/cd", "infrastructure", "docker"],
            "security": ["security", "auth", "encryption", "vulnerability"],
            "performance": ["performance", "optimization", "speed", "memory"],
            "documentation": ["documentation", "doc", "readme", "comment"],
            "project": ["project", "management", "agile", "team"],
        }

        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword.lower() in content.lower():
                    return category
        return "general"

    def _should_validate_file(self, file_path: str) -> bool:
        """Check if a file should be validated."""
        if file_path.startswith(".") or "/." in file_path:
            return False

        if any(
            dir in file_path
            for dir in [
                ".git",
                "node_modules",
                "__pycache__",
                "venv",
                "build",
                "dist",
                "target",
                "out",
                ".next",
                ".nuxt",
            ]
        ):
            return False

        if os.path.getsize(file_path) > 10 * 1024 * 1024:
            return False

        # Exclude generated files
        if any(
            pattern in file_path
            for pattern in ["_generated", "_pb2", "_pb2_grpc", ".gen", ".tmp", ".cache"]
        ):
            return False

        # Exclude documentation files
        if any(
            file_path.endswith(ext)
            for ext in [
                ".md",
                ".txt",
                ".rst",
                ".yml",
                ".yaml",
                ".json",
                ".lock",
                ".env",
            ]
        ):
            return False

        return True

    def _rule_applies(self, rule: Dict, file_path: str) -> bool:
        """Check if a rule applies to a specific file."""
        # Check file extension patterns
        if "file_patterns" in rule:
            file_patterns = rule["file_patterns"]
            if not any(file_path.endswith(ext) for ext in file_patterns):
                return False

        # Check excluded directories
        if "excluded_dirs" in rule:
            excluded_dirs = rule["excluded_dirs"]
            if any(dir in file_path for dir in excluded_dirs):
                return False

        return True

    def _extract_patterns(self, content: str) -> List[str]:
        """Extract validation patterns from rule content."""
        patterns = []

        pattern_regex = (
            r"```(?:python|javascript|typescript|java|csharp|go|rust|sql)\n(.*?\n)```"
        )
        matches = re.findall(pattern_regex, content, re.DOTALL)
        patterns.extend(matches)

        anti_pattern_regex = r"## Anti-Patterns to Avoid\n([^#]+)"
        matches = re.findall(anti_pattern_regex, content, re.DOTALL)
        for match in matches:
            lines = match.strip().split("\n")
            patterns.extend([line.strip() for line in lines if line.strip()])

        return patterns

    def _extract_requirements(self, content: str) -> List[str]:
        """Extract requirements from rule content."""
        requirements = []

        req_regex = r"## Requirements\n([^#]+)"
        matches = re.findall(req_regex, content, re.DOTALL)
        for match in matches:
            lines = match.strip().split("\n")
            requirements.extend([line.strip() for line in lines if line.strip()])

        bullet_regex = r"^-\s+(.+)$"
        matches = re.findall(bullet_regex, content, re.MULTILINE)
        requirements.extend([m.strip() for m in matches if m.strip()])

        return requirements

    def _extract_severity(self, content: str) -> str:
        """Extract severity level from rule content."""
        severity_map = {
            "error": ["error", "critical", "must", "required"],
            "warning": ["warning", "should", "recommended"],
            "info": ["info", "best practice", "guideline"],
        }

        for severity, keywords in severity_map.items():
            for keyword in keywords:
                if keyword.lower() in content.lower():
                    return severity
        return "info"

    def _extract_custom_validators(self, content: str) -> List[Callable]:
        """Extract custom validation functions from rule content."""
        validators = []

        validator_regex = r"## Custom Validator\n([^#]+)"
        matches = re.findall(validator_regex, content, re.DOTALL)
        for match in matches:
            try:
                # Parse the validator function definition
                validator_def = match.strip()
                if validator_def.startswith("def "):
                    # Execute the validator function definition
                    exec(validator_def, globals())
                    # Get the validator function name
                    func_name = validator_def.split("(")[0].split(" ")[-1]
                    validators.append(globals()[func_name])
            except Exception as e:
                print(f"Error parsing custom validator: {e}")

        return validators

    def validate_file(self, file_path: str) -> List[ValidationResult]:
        """Validate a single file against all rules."""
        results = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")

                for rule_name, rule in self.rules.items():
                    if not self._rule_applies(rule, file_path):
                        continue

                    # Check patterns
                    for pattern in rule["patterns"]:
                        if self._pattern_matches(pattern, content, lines):
                            results.append(
                                ValidationResult(
                                    rule=rule_name,
                                    file=file_path,
                                    line=None,
                                    column=None,
                                    message=f"Pattern match: {pattern}",
                                    severity=rule.get("severity", "info"),
                                    passed=True,
                                )
                            )

                    # Check requirements
                    for requirement in rule["requirements"]:
                        if not self._requirement_met(requirement, content, lines):
                            results.append(
                                ValidationResult(
                                    rule=rule_name,
                                    file=file_path,
                                    line=None,
                                    column=None,
                                    message=f"Requirement not met: {requirement}",
                                    severity=rule.get("severity", "warning"),
                                    passed=False,
                                )
                            )

                    for validator in rule.get("custom_validators", []):
                        try:
                            passed, message = validator(file_path, content, lines)
                            results.append(
                                ValidationResult(
                                    rule=rule_name,
                                    file=file_path,
                                    line=None,
                                    column=None,
                                    message=message,
                                    severity=rule.get("severity", "warning"),
                                    passed=passed,
                                )
                            )
                        except Exception as e:
                            results.append(
                                ValidationResult(
                                    rule=rule_name,
                                    file=file_path,
                                    line=None,
                                    column=None,
                                    message=f"Validator error: {e}",
                                    severity="error",
                                    passed=False,
                                )
                            )

        except Exception as e:
            results.append(
                ValidationResult(
                    rule="general",
                    file=file_path,
                    line=None,
                    column=None,
                    message=f"Error reading file: {e}",
                    severity="error",
                    passed=False,
                )
            )

        return results

    def _pattern_matches(self, pattern: str, content: str, lines: List[str]) -> bool:
        if pattern.startswith("r"):
            pattern = pattern[1:]
            return bool(re.search(pattern, content, re.DOTALL))
        return pattern in content

    def _requirement_met(
        self, requirement: str, content: str, lines: List[str]
    ) -> bool:
        if requirement.startswith("r"):
            requirement = requirement[1:]
            return bool(re.search(requirement, content, re.DOTALL))

        if requirement.startswith("line:"):
            line_num = int(requirement.split(":")[1])
            return line_num <= len(lines)

        return requirement.lower() in content.lower()

    def validate_directory(self, dir_path: str) -> List[ValidationResult]:
        """Validate all files in a directory."""
        results = []

        for root, dirs, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                if self._should_validate_file(file_path):
                    results.extend(self.validate_file(file_path))

        return results

    def _should_validate_file(self, file_path: str) -> bool:
        """Check if a file should be validated."""
        if file_path.startswith(".") or "/." in file_path:
            return False

        if any(
            dir in file_path
            for dir in [
                ".git",
                "node_modules",
                "__pycache__",
                "venv",
                "build",
                "dist",
                "target",
                "out",
                ".next",
                ".nuxt",
            ]
        ):
            return False

        if os.path.getsize(file_path) > 10 * 1024 * 1024:
            return False

        # Exclude generated files
        if any(
            pattern in file_path
            for pattern in ["_generated", "_pb2", "_pb2_grpc", ".gen", ".tmp", ".cache"]
        ):
            return False

        # Exclude documentation files
        if any(
            file_path.endswith(ext)
            for ext in [
                ".md",
                ".txt",
                ".rst",
                ".yml",
                ".yaml",
                ".json",
                ".lock",
                ".env",
            ]
        ):
            return False

        return True

    def _rule_applies(self, rule: Dict, file_path: str) -> bool:
        """Check if a rule applies to a specific file."""
        # Check file extension patterns
        if "file_patterns" in rule:
            file_patterns = rule["file_patterns"]
            if not any(file_path.endswith(ext) for ext in file_patterns):
                return False

        # Check excluded directories
        if "excluded_dirs" in rule:
            excluded_dirs = rule["excluded_dirs"]
            if any(dir in file_path for dir in excluded_dirs):
                return False

        return True

    def generate_report(self, results: List[ValidationResult]) -> str:
        """Generate a compliance report."""
        report = []

        errors = [r for r in results if r.severity == "error"]
        warnings = [r for r in results if r.severity == "warning"]
        infos = [r for r in results if r.severity == "info"]

        report.append("OpenCode Compliance Report")
        report.append("=" * 30)
        report.append(f"Total checks: {len(results)}")
        report.append(f"Errors: {len(errors)}")
        report.append(f"Warnings: {len(warnings)}")
        report.append(f"Info: {len(infos)}")
        report.append("")

        if errors:
            report.append("ERRORS:")
            report.append("-" * 30)
            for result in errors:
                report.append(f"{result.file}:{result.line or ''} - {result.message}")
            report.append("")

        if warnings:
            report.append("WARNINGS:")
            report.append("-" * 30)
            for result in warnings:
                report.append(f"{result.file}:{result.line or ''} - {result.message}")
            report.append("")

        if infos:
            report.append("INFO:")
            report.append("-" * 30)
            for result in infos:
                report.append(f"{result.file}:{result.line or ''} - {result.message}")
            report.append("")

        if not results:
            report.append("No issues found. Code is compliant with OpenCode standards!")

        return "\n".join(report)


def validate_python_syntax(
    file_path: str, content: str, lines: List[str]
) -> Tuple[bool, str]:
    """Custom validator for Python syntax checking."""
    try:
        ast.parse(content)
        return True, "Python syntax is valid"
    except SyntaxError as e:
        return False, f"Python syntax error: {e.msg} at line {e.lineno}"


def validate_no_debug_statements(
    file_path: str, content: str, lines: List[str]
) -> Tuple[bool, str]:
    """Custom validator to check for debug statements."""
    debug_statements = ["print(", "console.log(", "debugger;"]
    for i, line in enumerate(lines, 1):
        for stmt in debug_statements:
            if stmt in line:
                return False, f"Debug statement found: {stmt} at line {i}"
    return True, "No debug statements found"


def validate_file_size(
    file_path: str, content: str, lines: List[str]
) -> Tuple[bool, str]:
    """Custom validator to check file size."""
    max_size = 5 * 1024 * 1024  # 5MB
    file_size = os.path.getsize(file_path)
    if file_size > max_size:
        return False, f"File size {file_size} bytes exceeds limit of {max_size} bytes"
    return True, f"File size {file_size} bytes is within limits"


def validate_no_todo_todo(
    file_path: str, content: str, lines: List[str]
) -> Tuple[bool, str]:
    """Custom validator to check for TODO/FIXME comments."""
    todo_patterns = ["TODO:", "FIXME:", "XXX:"]
    for i, line in enumerate(lines, 1):
        for pattern in todo_patterns:
            if pattern in line:
                return False, f"TODO/FIXME comment found: {pattern} at line {i}"
    return True, "No TODO/FIXME comments found"


def validate_no_hardcoded_secrets(
    file_path: str, content: str, lines: List[str]
) -> Tuple[bool, str]:
    """Custom validator to check for hardcoded secrets."""
    secret_patterns = [
        r"password\s*=\s*['\"][^'\"]*['\"]",
        r"secret\s*=\s*['\"][^'\"]*['\"]",
        r"key\s*=\s*['\"][^'\"]*['\"]",
        r"token\s*=\s*['\"][^'\"]*['\"]",
    ]
    for pattern in secret_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return False, f"Hardcoded secret found in {file_path}"
    return True, "No hardcoded secrets found"


def validate_python_imports(
    file_path: str, content: str, lines: List[str]
) -> Tuple[bool, str]:
    """Custom validator for Python import style."""
    if not file_path.endswith(".py"):
        return True, "Not a Python file"

    try:
        import_statements = []
        for line in lines:
            if line.strip().startswith("import ") or line.strip().startswith("from "):
                import_statements.append(line.strip())

        # Check for proper import style
        if len(import_statements) > 0:
            first_import = import_statements[0]
            if "#" in first_import:
                return False, "Import statement contains comment"

            # Check for wildcard imports
            for imp in import_statements:
                if "import *" in imp:
                    return False, f"Wildcard import found: {imp}"

        return True, f"{len(import_statements)} imports found, style compliant"
    except Exception as e:
        return False, f"Import validation error: {e}"


def main():
    """Main entry point for compliance checking."""
    import argparse

    parser = argparse.ArgumentParser(description="OpenCode Compliance Checker")
    parser.add_argument("path", help="File or directory to validate")
    parser.add_argument(
        "--report", action="store_true", help="Generate compliance report"
    )

    args = parser.parse_args()

    checker = ComplianceChecker()

    if os.path.isfile(args.path):
        results = checker.validate_file(args.path)
    else:
        results = checker.validate_directory(args.path)

    if args.report:
        print(checker.generate_report(results))
    else:
        for result in results:
            print(f"{result.file}:{result.line or ''} - {result.message}")


if __name__ == "__main__":
    main()
