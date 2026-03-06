"""Tests for coverage dashboard (G1: Build coverage truth dashboard).

Tests the coverage collection, parsing, and reporting functionality.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from solstein.core.coverage_dashboard import (
    CoverageCollector,
    CoverageDashboard,
    CoverageMetrics,
    CoverageReport,
    ModuleCoverage,
    generate_coverage_badge,
)


class TestCoverageMetrics:
    """Tests for CoverageMetrics dataclass."""

    def test_basic_initialization(self):
        """Test basic initialization with values."""
        metrics = CoverageMetrics(
            total_lines=100,
            covered_lines=80,
            missing_lines=20,
        )
        assert metrics.total_lines == 100
        assert metrics.covered_lines == 80
        assert metrics.missing_lines == 20
        assert metrics.coverage_percent == 80.0

    def test_coverage_percent_calculation(self):
        """Test coverage percentage is calculated correctly."""
        metrics = CoverageMetrics(total_lines=200, covered_lines=150)
        assert metrics.coverage_percent == 75.0

    def test_zero_total_lines(self):
        """Test handling of zero total lines."""
        metrics = CoverageMetrics(total_lines=0, covered_lines=0)
        assert metrics.coverage_percent == 0.0

    def test_full_coverage(self):
        """Test 100% coverage."""
        metrics = CoverageMetrics(total_lines=100, covered_lines=100)
        assert metrics.coverage_percent == 100.0

    def test_no_coverage(self):
        """Test 0% coverage."""
        metrics = CoverageMetrics(total_lines=100, covered_lines=0)
        assert metrics.coverage_percent == 0.0

    def test_to_dict(self):
        """Test conversion to dictionary."""
        metrics = CoverageMetrics(
            total_lines=100,
            covered_lines=75,
            missing_lines=25,
        )
        result = metrics.to_dict()
        assert result == {
            "total_lines": 100,
            "covered_lines": 75,
            "missing_lines": 25,
            "coverage_percent": 75.0,
        }


class TestModuleCoverage:
    """Tests for ModuleCoverage dataclass."""

    def test_basic_initialization(self):
        """Test basic initialization."""
        module = ModuleCoverage(name="analytics", path=Path("/src/solstein/analytics"))
        assert module.name == "analytics"
        assert module.path == Path("/src/solstein/analytics")
        assert module.metrics.total_lines == 0
        assert module.files == {}

    def test_with_metrics(self):
        """Test initialization with metrics."""
        metrics = CoverageMetrics(total_lines=100, covered_lines=80)
        module = ModuleCoverage(
            name="scoring",
            path=Path("/src/solstein/scoring"),
            metrics=metrics,
        )
        assert module.metrics.coverage_percent == 80.0

    def test_with_files(self):
        """Test module with file coverage."""
        module = ModuleCoverage(name="api", path=Path("/src/solstein/api"))
        module.files["api/routes.py"] = CoverageMetrics(total_lines=50, covered_lines=40)
        module.files["api/schemas.py"] = CoverageMetrics(total_lines=30, covered_lines=30)
        assert len(module.files) == 2

    def test_to_dict(self):
        """Test conversion to dictionary."""
        module = ModuleCoverage(
            name="domain",
            path=Path("/src/solstein/domain"),
            metrics=CoverageMetrics(total_lines=100, covered_lines=90),
        )
        module.files["models.py"] = CoverageMetrics(total_lines=50, covered_lines=45)

        result = module.to_dict()
        assert result["name"] == "domain"
        assert result["path"] == "/src/solstein/domain"
        assert result["metrics"]["coverage_percent"] == 90.0
        assert "models.py" in result["files"]


class TestCoverageReport:
    """Tests for CoverageReport dataclass."""

    def test_basic_initialization(self):
        """Test basic initialization."""
        report = CoverageReport()
        assert report.total_metrics.total_lines == 0
        assert report.modules == []
        assert report.threshold == 80.0
        assert report.timestamp == ""

    def test_passed_threshold_true(self):
        """Test passed_threshold when above threshold."""
        report = CoverageReport(
            total_metrics=CoverageMetrics(total_lines=100, covered_lines=85),
            threshold=80.0,
        )
        assert report.passed_threshold is True

    def test_passed_threshold_false(self):
        """Test passed_threshold when below threshold."""
        report = CoverageReport(
            total_metrics=CoverageMetrics(total_lines=100, covered_lines=70),
            threshold=80.0,
        )
        assert report.passed_threshold is False

    def test_passed_threshold_exact(self):
        """Test passed_threshold at exact threshold."""
        report = CoverageReport(
            total_metrics=CoverageMetrics(total_lines=100, covered_lines=80),
            threshold=80.0,
        )
        assert report.passed_threshold is True

    def test_get_low_coverage_modules(self):
        """Test getting modules with low coverage."""
        report = CoverageReport(
            modules=[
                ModuleCoverage(
                    name="high",
                    path=Path("/high"),
                    metrics=CoverageMetrics(total_lines=100, covered_lines=90),
                ),
                ModuleCoverage(
                    name="medium",
                    path=Path("/medium"),
                    metrics=CoverageMetrics(total_lines=100, covered_lines=70),
                ),
                ModuleCoverage(
                    name="low",
                    path=Path("/low"),
                    metrics=CoverageMetrics(total_lines=100, covered_lines=40),
                ),
            ]
        )
        low = report.get_low_coverage_modules(min_coverage=60.0)
        assert len(low) == 1
        assert low[0].name == "low"

    def test_get_low_coverage_modules_empty(self):
        """Test getting low coverage when all pass."""
        report = CoverageReport(
            modules=[
                ModuleCoverage(
                    name="mod1",
                    path=Path("/mod1"),
                    metrics=CoverageMetrics(total_lines=100, covered_lines=90),
                ),
            ]
        )
        low = report.get_low_coverage_modules(min_coverage=80.0)
        assert low == []

    def test_to_dict(self):
        """Test conversion to dictionary."""
        report = CoverageReport(
            total_metrics=CoverageMetrics(total_lines=100, covered_lines=80),
            timestamp="2024-01-01T00:00:00",
            threshold=80.0,
        )
        result = report.to_dict()
        assert result["timestamp"] == "2024-01-01T00:00:00"
        assert result["threshold"] == 80.0
        assert result["passed_threshold"] is True
        assert result["total_metrics"]["coverage_percent"] == 80.0


class TestCoverageCollector:
    """Tests for CoverageCollector class."""

    def test_initialization(self):
        """Test initialization with default and custom root."""
        collector = CoverageCollector()
        assert collector.project_root == Path.cwd()

        custom_root = Path("/custom/path")
        collector = CoverageCollector(project_root=custom_root)
        assert collector.project_root == custom_root

    @patch("solstein.core.coverage_dashboard.subprocess.run")
    @patch("pathlib.Path.exists")
    @patch("builtins.open", mock_open(read_data='{"totals": {"num_statements": 100}}'))
    def test_run_coverage_success(self, mock_exists, mock_run):
        """Test successful coverage run."""
        mock_exists.return_value = True
        mock_run.return_value = MagicMock(returncode=0)

        collector = CoverageCollector()
        result = collector.run_coverage()

        assert result == {"totals": {"num_statements": 100}}
        mock_run.assert_called_once()

    @patch("solstein.core.coverage_dashboard.subprocess.run")
    @patch("pathlib.Path.exists")
    def test_run_coverage_file_not_found(self, mock_exists, mock_run):
        """Test coverage when JSON file not generated."""
        mock_exists.return_value = False
        mock_run.return_value = MagicMock(returncode=0)

        collector = CoverageCollector()
        result = collector.run_coverage()

        assert result == {}

    @patch("solstein.core.coverage_dashboard.subprocess.run")
    def test_run_coverage_exception(self, mock_run):
        """Test coverage when subprocess fails."""
        mock_run.side_effect = Exception("Subprocess error")

        collector = CoverageCollector()
        result = collector.run_coverage()

        assert result == {}

    def test_parse_coverage_empty(self):
        """Test parsing empty coverage data."""
        collector = CoverageCollector()
        report = collector.parse_coverage({})
        assert report.total_metrics.total_lines == 0
        assert report.modules == []

    def test_parse_coverage_with_totals(self):
        """Test parsing coverage with totals."""
        collector = CoverageCollector()
        coverage_data = {
            "totals": {
                "num_statements": 1000,
                "covered_lines": 800,
                "missing_lines": 200,
            },
            "files": {},
        }
        report = collector.parse_coverage(coverage_data)
        assert report.total_metrics.total_lines == 1000
        assert report.total_metrics.covered_lines == 800
        assert report.total_metrics.coverage_percent == 80.0

    def test_parse_coverage_with_files(self):
        """Test parsing coverage with file data."""
        collector = CoverageCollector()
        coverage_data = {
            "totals": {"num_statements": 100, "covered_lines": 80},
            "files": {
                "src/solstein/analytics/scoring.py": {
                    "num_statements": 50,
                    "executed_lines": 40,
                    "missing_lines": 10,
                },
                "src/solstein/api/routes.py": {
                    "num_statements": 50,
                    "executed_lines": 40,
                    "missing_lines": 10,
                },
            },
        }
        report = collector.parse_coverage(coverage_data)
        assert len(report.modules) == 2
        module_names = {m.name for m in report.modules}
        assert "analytics" in module_names
        assert "api" in module_names

    def test_parse_coverage_skips_test_files(self):
        """Test that test files are skipped."""
        collector = CoverageCollector()
        coverage_data = {
            "totals": {"num_statements": 100, "covered_lines": 80},
            "files": {
                "src/solstein/analytics/scoring.py": {
                    "num_statements": 50,
                    "executed_lines": 40,
                    "missing_lines": 10,
                },
                "tests/unit/test_scoring.py": {
                    "num_statements": 50,
                    "executed_lines": 50,
                    "missing_lines": 0,
                },
            },
        }
        report = collector.parse_coverage(coverage_data)
        assert len(report.modules) == 1
        assert report.modules[0].name == "analytics"

    def test_parse_coverage_aggregation(self):
        """Test that module metrics are aggregated correctly."""
        collector = CoverageCollector()
        coverage_data = {
            "totals": {"num_statements": 150, "covered_lines": 120},
            "files": {
                "src/solstein/analytics/scoring.py": {
                    "num_statements": 50,
                    "executed_lines": 40,
                    "missing_lines": 10,
                },
                "src/solstein/analytics/classification.py": {
                    "num_statements": 50,
                    "executed_lines": 50,
                    "missing_lines": 0,
                },
            },
        }
        report = collector.parse_coverage(coverage_data)
        analytics_module = next(m for m in report.modules if m.name == "analytics")
        assert analytics_module.metrics.total_lines == 100
        assert analytics_module.metrics.covered_lines == 90
        assert analytics_module.metrics.coverage_percent == 90.0


class TestCoverageDashboard:
    """Tests for CoverageDashboard class."""

    def test_initialization(self):
        """Test initialization."""
        dashboard = CoverageDashboard()
        assert dashboard.project_root == Path.cwd()
        assert dashboard.collector is not None

    @patch.object(CoverageCollector, "run_coverage")
    @patch.object(CoverageCollector, "parse_coverage")
    def test_generate_report(self, mock_parse, mock_run):
        """Test generating coverage report."""
        mock_run.return_value = {"totals": {}}
        mock_parse.return_value = CoverageReport(
            total_metrics=CoverageMetrics(total_lines=100, covered_lines=80),
        )

        dashboard = CoverageDashboard()
        report = dashboard.generate_report()

        assert report.total_metrics.coverage_percent == 80.0
        assert report.timestamp != ""
        mock_run.assert_called_once()
        mock_parse.assert_called_once()

    @patch.object(CoverageDashboard, "generate_report")
    def test_print_summary(self, mock_generate):
        """Test printing summary."""
        mock_generate.return_value = CoverageReport(
            total_metrics=CoverageMetrics(total_lines=100, covered_lines=85),
            timestamp="2024-01-01T00:00:00",
            modules=[
                ModuleCoverage(
                    name="analytics",
                    path=Path("/analytics"),
                    metrics=CoverageMetrics(total_lines=50, covered_lines=45),
                ),
            ],
        )

        dashboard = CoverageDashboard()
        # Should not raise
        dashboard.print_summary()

    @patch.object(CoverageDashboard, "generate_report")
    def test_print_summary_with_report(self, mock_generate):
        """Test printing summary with provided report."""
        report = CoverageReport(
            total_metrics=CoverageMetrics(total_lines=100, covered_lines=85),
        )

        dashboard = CoverageDashboard()
        # Should not raise and not call generate_report
        dashboard.print_summary(report)
        mock_generate.assert_not_called()

    @patch("pathlib.Path.write_text")
    def test_export_html(self, mock_write):
        """Test exporting HTML report."""
        report = CoverageReport(
            total_metrics=CoverageMetrics(total_lines=100, covered_lines=85),
            timestamp="2024-01-01T00:00:00",
            modules=[
                ModuleCoverage(
                    name="analytics",
                    path=Path("/analytics"),
                    metrics=CoverageMetrics(total_lines=50, covered_lines=45),
                ),
            ],
        )

        dashboard = CoverageDashboard()
        output_path = Path("/tmp/report.html")
        dashboard.export_html(report, output_path)

        mock_write.assert_called_once()
        written_content = mock_write.call_args[0][0]
        assert "Coverage Truth Dashboard" in written_content
        assert "analytics" in written_content
        assert "85.0%" in written_content or "85%" in written_content


class TestGenerateCoverageBadge:
    """Tests for generate_coverage_badge function."""

    @patch("pathlib.Path.write_text")
    def test_badge_green(self, mock_write):
        """Test badge generation for high coverage (green)."""
        output_path = Path("/tmp/badge.svg")
        generate_coverage_badge(85.0, output_path)

        mock_write.assert_called_once()
        content = mock_write.call_args[0][0]
        assert "#4CAF50" in content  # Green color
        assert "85%" in content

    @patch("pathlib.Path.write_text")
    def test_badge_yellow(self, mock_write):
        """Test badge generation for medium coverage (yellow)."""
        output_path = Path("/tmp/badge.svg")
        generate_coverage_badge(70.0, output_path)

        mock_write.assert_called_once()
        content = mock_write.call_args[0][0]
        assert "#FFC107" in content  # Yellow color
        assert "70%" in content

    @patch("pathlib.Path.write_text")
    def test_badge_red(self, mock_write):
        """Test badge generation for low coverage (red)."""
        output_path = Path("/tmp/badge.svg")
        generate_coverage_badge(50.0, output_path)

        mock_write.assert_called_once()
        content = mock_write.call_args[0][0]
        assert "#F44336" in content  # Red color
        assert "50%" in content

    @patch("pathlib.Path.write_text")
    def test_badge_exact_thresholds(self, mock_write):
        """Test badge at exact thresholds."""
        # Exactly 80 should be green
        generate_coverage_badge(80.0, Path("/tmp/badge.svg"))
        content = mock_write.call_args[0][0]
        assert "#4CAF50" in content

        # Exactly 60 should be yellow
        generate_coverage_badge(60.0, Path("/tmp/badge.svg"))
        content = mock_write.call_args[0][0]
        assert "#FFC107" in content


class TestIntegrationPatterns:
    """Integration-style tests for coverage dashboard workflows."""

    def test_end_to_end_report_generation(self):
        """Test complete report generation workflow."""
        # This test simulates the full workflow without actually running pytest
        collector = CoverageCollector()

        # Mock coverage data
        coverage_data = {
            "totals": {
                "num_statements": 500,
                "covered_lines": 400,
                "missing_lines": 100,
            },
            "files": {
                "src/solstein/analytics/scoring.py": {
                    "num_statements": 100,
                    "executed_lines": 90,
                    "missing_lines": 10,
                },
                "src/solstein/api/routes.py": {
                    "num_statements": 100,
                    "executed_lines": 80,
                    "missing_lines": 20,
                },
                "src/solstein/domain/models.py": {
                    "num_statements": 100,
                    "executed_lines": 100,
                    "missing_lines": 0,
                },
                "src/solstein/data/loader.py": {
                    "num_statements": 100,
                    "executed_lines": 70,
                    "missing_lines": 30,
                },
                "src/solstein/core/config.py": {
                    "num_statements": 100,
                    "executed_lines": 60,
                    "missing_lines": 40,
                },
            },
        }

        report = collector.parse_coverage(coverage_data)

        # Verify totals
        assert report.total_metrics.total_lines == 500
        assert report.total_metrics.covered_lines == 400
        assert report.total_metrics.coverage_percent == 80.0

        # Verify modules are sorted by coverage
        assert len(report.modules) == 5
        coverages = [m.metrics.coverage_percent for m in report.modules]
        assert coverages == sorted(coverages)

        # Verify low coverage detection
        low = report.get_low_coverage_modules(min_coverage=70.0)
        assert len(low) == 1  # Only config (60%) is below 70%

    def test_module_aggregation_accuracy(self):
        """Test that module aggregation is mathematically correct."""
        collector = CoverageCollector()

        coverage_data = {
            "totals": {"num_statements": 300, "covered_lines": 240},
            "files": {
                "src/solstein/analytics/file1.py": {
                    "num_statements": 100,
                    "executed_lines": 80,
                    "missing_lines": 20,
                },
                "src/solstein/analytics/file2.py": {
                    "num_statements": 100,
                    "executed_lines": 90,
                    "missing_lines": 10,
                },
                "src/solstein/analytics/file3.py": {
                    "num_statements": 100,
                    "executed_lines": 70,
                    "missing_lines": 30,
                },
            },
        }

        report = collector.parse_coverage(coverage_data)
        analytics = next(m for m in report.modules if m.name == "analytics")

        # Total lines: 100 + 100 + 100 = 300
        assert analytics.metrics.total_lines == 300
        # Covered lines: 80 + 90 + 70 = 240
        assert analytics.metrics.covered_lines == 240
        # Coverage: 240 / 300 = 80%
        assert analytics.metrics.coverage_percent == 80.0

    def test_report_serialization_roundtrip(self):
        """Test that reports can be serialized and deserialized."""
        report = CoverageReport(
            total_metrics=CoverageMetrics(total_lines=100, covered_lines=80),
            timestamp="2024-01-01T00:00:00",
            threshold=80.0,
            modules=[
                ModuleCoverage(
                    name="test",
                    path=Path("/test"),
                    metrics=CoverageMetrics(total_lines=50, covered_lines=40),
                    files={
                        "file.py": CoverageMetrics(total_lines=50, covered_lines=40),
                    },
                ),
            ],
        )

        # Serialize
        data = report.to_dict()

        # Verify structure
        assert "timestamp" in data
        assert "threshold" in data
        assert "passed_threshold" in data
        assert "total_metrics" in data
        assert "modules" in data
        assert "low_coverage_modules" in data

        # Verify values preserved
        assert data["total_metrics"]["coverage_percent"] == 80.0
        assert data["modules"][0]["name"] == "test"
