import unittest
from unittest.mock import patch
import os
from . import validate_file, validate_directory, generate_report
from .checker import ValidationResult


class TestComplianceChecker(unittest.TestCase):
    def test_validate_file(self):
        """Test file validation."""
        test_file = "test_file.py"
        with open(test_file, "w") as f:
            f.write("def test():")

        try:
            results = validate_file(test_file)
            self.assertIsInstance(results, list)
            self.assertGreater(len(results), 0)
        finally:
            os.remove(test_file)

    def test_validate_directory(self):
        """Test directory validation."""
        test_dir = "test_dir"
        os.makedirs(test_dir, exist_ok=True)

        try:
            with open(os.path.join(test_dir, "test1.py"), "w") as f:
                f.write("def test1():")
            with open(os.path.join(test_dir, "test2.py"), "w") as f:
                f.write("def test2():")

            results = validate_directory(test_dir)
            self.assertIsInstance(results, list)
            self.assertGreater(len(results), 0)
        finally:
            for file in os.listdir(test_dir):
                os.remove(os.path.join(test_dir, file))
            os.rmdir(test_dir)

    def test_generate_report(self):
        """Test report generation."""
        results = [
            ValidationResult(
                "test_rule", "test_file.py", 1, None, "Test message", "warning", False
            ),
            ValidationResult(
                "test_rule2", "test_file2.py", 2, None, "Test message 2", "error", False
            ),
        ]

        report = generate_report(results)
        self.assertIsInstance(report, str)
        self.assertIn("ERRORS:", report)
        self.assertIn("WARNINGS:", report)

    def test_empty_results(self):
        """Test empty results."""
        results = []
        report = generate_report(results)
        self.assertIsInstance(report, str)
        self.assertIn("No issues found", report)


if __name__ == "__main__":
    unittest.main()
