"""Tests for exception handling lint script.

F4: Tests for policy lint check.
"""

import ast
import tempfile
from pathlib import Path
from typing import Any

import pytest
import tempfile
from pathlib import Path

import pytest

from scripts.lint_exception_handling import (
    ExceptionHandlingChecker,
    Violation,
    check_directory,
    check_file,
    format_violation,
    main,
)


class TestExceptionHandlingChecker:
    """Tests for ExceptionHandlingChecker AST visitor."""

    def test_bare_except_detection(self) -> None:
        code = """
try:
    pass
except:
    pass
"""
        tree = ast.parse(code)
        checker = ExceptionHandlingChecker(Path("test.py"))
        checker.visit(tree)

        assert len(checker.violations) == 1
        assert checker.violations[0].pattern == "bare_except"

    def test_except_exception_detection(self) -> None:
        code = """
try:
    pass
except Exception:
    pass
"""
        tree = ast.parse(code)
        checker = ExceptionHandlingChecker(Path("test.py"))
        checker.visit(tree)

        assert len(checker.violations) == 1
        assert checker.violations[0].pattern == "except_exception"

    def test_except_base_exception_detection(self) -> None:
        code = """
try:
    pass
except BaseException:
    pass
"""
        tree = ast.parse(code)
        checker = ExceptionHandlingChecker(Path("test.py"))
        checker.visit(tree)

        assert len(checker.violations) == 1
        assert checker.violations[0].pattern == "except_base_exception"

    def test_specific_exception_allowed(self) -> None:
        code = """
try:
    pass
except ValueError:
    pass
except (TypeError, KeyError):
    pass
"""
        tree = ast.parse(code)
        checker = ExceptionHandlingChecker(Path("test.py"))
        checker.visit(tree)

        assert len(checker.violations) == 0

    def test_critical_module_error_severity(self) -> None:
        code = """
try:
    pass
except Exception:
    pass
"""
        tree = ast.parse(code)
        checker = ExceptionHandlingChecker(Path("worker_tasks.py"))
        checker.visit(tree)

        assert len(checker.violations) == 1
        assert checker.violations[0].severity == "error"

    def test_non_critical_module_warning_severity(self) -> None:
        code = """
try:
    pass
except Exception:
    pass
"""
        tree = ast.parse(code)
        checker = ExceptionHandlingChecker(Path("utils.py"))
        checker.visit(tree)

        assert len(checker.violations) == 1
        assert checker.violations[0].severity == "warning"

    def test_critical_only_mode_skips_non_critical(self) -> None:
        code = """
try:
    pass
except Exception:
    pass
"""
        tree = ast.parse(code)
        checker = ExceptionHandlingChecker(Path("utils.py"), critical_only=True)
        checker.visit(tree)

        assert len(checker.violations) == 0


class TestCheckFile:
    """Tests for check_file function."""

    def test_finds_violations_in_file(self, tmp_path: Path) -> None:
        test_file = tmp_path / "test.py"
        test_file.write_text("""
try:
    risky_operation()
except:
    pass

except Exception:
    pass
""")

        violations = check_file(test_file)

        assert len(violations) == 2

    def test_handles_syntax_error(self, tmp_path: Path) -> None:
        test_file = tmp_path / "test.py"
        test_file.write_text("def broken(")  # Invalid syntax

        violations = check_file(test_file)

        assert len(violations) == 1
        assert violations[0].pattern == "syntax_error"

    def test_handles_file_read_error(self, tmp_path: Path) -> None:
        # Create a file with invalid encoding
        test_file = tmp_path / "test.py"
        test_file.write_bytes(b"\xff\xfe invalid utf-8")

        violations = check_file(test_file)

        # Should not crash, may or may not have violations depending on content


class TestCheckDirectory:
    """Tests for check_directory function."""

    def test_checks_all_python_files(self, tmp_path: Path) -> None:
        # Create test files
        (tmp_path / "file1.py").write_text("try:\n    pass\nexcept:\n    pass")
        (tmp_path / "file2.py").write_text("try:\n    pass\nexcept Exception:\n    pass")
        (tmp_path / "file3.txt").write_text("not python")  # Should be ignored

        violations = check_directory(tmp_path)

        assert len(violations) == 2

    def test_respects_exclude_patterns(self, tmp_path: Path) -> None:
        # Create files
        (tmp_path / "file.py").write_text("try:\n    pass\nexcept:\n    pass")
        pycache = tmp_path / "__pycache__"
        pycache.mkdir()
        (pycache / "cached.py").write_text("try:\n    pass\nexcept:\n    pass")

        violations = check_directory(tmp_path, exclude_patterns={"__pycache__"})

        assert len(violations) == 1  # Only file.py, not cached.py


class TestFormatViolation:
    """Tests for format_violation function."""

    def test_formatting(self) -> None:
        v = Violation(
            file=Path("/path/to/file.py"),
            line=10,
            column=5,
            pattern="bare_except",
            message="Bare except is bad",
            severity="error",
        )

        result = format_violation(v)

        assert "file.py:10:5" in result
        assert "[ERROR]" in result
        assert "Bare except is bad" in result


class TestMain:
    """Tests for main function."""

    def test_no_violations_exit_code_0(self, tmp_path: Path) -> None:
        test_file = tmp_path / "clean.py"
        test_file.write_text("try:\n    pass\nexcept ValueError:\n    pass")

        import sys

        old_argv = sys.argv
        try:
            sys.argv = ["lint_exception_handling.py", str(test_file)]
            result = main()
        finally:
            sys.argv = old_argv

        assert result == 0

    def test_violations_exit_code_1(self, tmp_path: Path) -> None:
        # Use a critical module name so violations are errors
        test_file = tmp_path / "worker_tasks.py"
        test_file.write_text("try:\n    pass\nexcept:\n    pass")

        import sys

        old_argv = sys.argv
        try:
            sys.argv = ["lint_exception_handling.py", str(test_file)]
            result = main()
        finally:
            sys.argv = old_argv

        assert result == 1

    def test_critical_only_mode(self, tmp_path: Path) -> None:
        test_file = tmp_path / "dirty.py"
        test_file.write_text("try:\n    pass\nexcept:\n    pass")

        import sys

        old_argv = sys.argv
        try:
            sys.argv = ["lint_exception_handling.py", str(test_file)]
            result = main()
        finally:
            sys.argv = old_argv

        assert result == 1

    def test_critical_only_mode(self, tmp_path: Path) -> None:
        # Create non-critical file with violation
        test_file = tmp_path / "utils.py"
        test_file.write_text("try:\n    pass\nexcept Exception:\n    pass")

        import sys

        old_argv = sys.argv
        try:
            sys.argv = [
                "lint_exception_handling.py",
                "--critical-only",
                str(test_file),
            ]
            result = main()
        finally:
            sys.argv = old_argv

        # Should pass because utils.py is not critical
        assert result == 0

    def test_json_format(self, tmp_path: Path, capsys: Any) -> None:
        test_file = tmp_path / "dirty.py"
        test_file.write_text("try:\n    pass\nexcept:\n    pass")

        import sys

        old_argv = sys.argv
        try:
            sys.argv = [
                "lint_exception_handling.py",
                "--format",
                "json",
                str(test_file),
            ]
            main()
        finally:
            sys.argv = old_argv

        captured = capsys.readouterr()
        assert '"pattern":' in captured.out
        assert '"message":' in captured.out
