"""Golden artifact storage and regression diffing.

STORY-267 / EPIC-070: Stores actual provider outputs and compares
them against golden contract specifications for regression detection.

Usage:
    differ = ArtifactDiffer(artifacts_dir)
    report = differ.compare(provider="yahoo_finance", actual=raw_data_source)
    assert report.passed, report.summary()
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class DiffViolation:
    """A single contract violation found during comparison."""

    field: str
    expected: str
    actual: str
    severity: str = "error"  # "error" or "warning"


@dataclass
class DiffReport:
    """Result of comparing an actual output against a golden contract."""

    provider: str
    scenario: str
    violations: list[DiffViolation] = field(default_factory=list)
    checked_fields: int = 0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def passed(self) -> bool:
        return not any(v.severity == "error" for v in self.violations)

    def summary(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        lines = [
            f"[{status}] {self.provider}/{self.scenario}: "
            f"{self.checked_fields} fields checked, "
            f"{len(self.violations)} violations"
        ]
        for v in self.violations:
            lines.append(f"  [{v.severity.upper()}] {v.field}: expected {v.expected}, got {v.actual}")
        return "\n".join(lines)


class ArtifactDiffer:
    """Compare actual provider outputs against golden contract artifacts."""

    def __init__(self, artifacts_dir: Path) -> None:
        self.artifacts_dir = artifacts_dir

    def store_actual(self, provider: str, scenario: str, data: dict[str, Any]) -> Path:
        """Store an actual run result for future diffing."""
        actual_dir = self.artifacts_dir / "actual_runs"
        actual_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        filename = f"{provider}_{scenario}_{timestamp}.json"
        path = actual_dir / filename
        path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        return path

    def compare_success(
        self, provider: str, actual: dict[str, Any], contract: dict[str, Any]
    ) -> DiffReport:
        """Compare an actual success output against the golden contract."""
        report = DiffReport(provider=provider, scenario="success")
        spec = contract.get("contract", {})

        self._check_scalar_fields(report, actual, spec)
        self._check_required_fields(report, actual, spec)
        self._check_value_constraints(report, actual, spec)

        return report

    def _check_scalar_fields(
        self, report: DiffReport, actual: dict[str, Any], spec: dict[str, Any]
    ) -> None:
        """Check source_type, confidence, relevance, and extraction_method."""
        if "source_type" in spec:
            report.checked_fields += 1
            actual_type = actual.get("source_type", "")
            if isinstance(actual_type, str) and actual_type != spec["source_type"]:
                report.violations.append(DiffViolation(
                    field="source_type", expected=spec["source_type"], actual=actual_type,
                ))

        if "source_type_options" in spec:
            report.checked_fields += 1
            actual_type = actual.get("source_type", "")
            if actual_type not in spec["source_type_options"]:
                report.violations.append(DiffViolation(
                    field="source_type",
                    expected=f"one of {spec['source_type_options']}",
                    actual=actual_type,
                ))

        self._check_bounded_field(report, actual, spec, "confidence")
        self._check_bounded_field(report, actual, spec, "relevance_score")

        if "extraction_method" in spec:
            report.checked_fields += 1
            actual_method = actual.get("extraction_method", "")
            if actual_method != spec["extraction_method"]:
                report.violations.append(DiffViolation(
                    field="extraction_method",
                    expected=spec["extraction_method"],
                    actual=actual_method or "(none)",
                ))

        if "extraction_method_pattern" in spec:
            report.checked_fields += 1
            actual_method = actual.get("extraction_method", "")
            if not re.match(spec["extraction_method_pattern"], actual_method or ""):
                report.violations.append(DiffViolation(
                    field="extraction_method",
                    expected=f"matches /{spec['extraction_method_pattern']}/",
                    actual=actual_method or "(none)",
                ))

    def _check_bounded_field(
        self,
        report: DiffReport,
        actual: dict[str, Any],
        spec: dict[str, Any],
        field_name: str,
    ) -> None:
        """Check a field is within [min, max] bounds."""
        if field_name not in spec:
            return
        report.checked_fields += 1
        actual_val = actual.get(field_name, 0)
        bound_spec = spec[field_name]
        if isinstance(bound_spec, dict) and "min" in bound_spec:
            if actual_val < bound_spec["min"] or actual_val > bound_spec["max"]:
                report.violations.append(DiffViolation(
                    field=field_name,
                    expected=f"[{bound_spec['min']}, {bound_spec['max']}]",
                    actual=str(actual_val),
                ))

    def _check_required_fields(
        self, report: DiffReport, actual: dict[str, Any], spec: dict[str, Any]
    ) -> None:
        """Check required_fields section of the contract."""
        required = spec.get("required_fields", {})
        for fname, fspec in required.items():
            report.checked_fields += 1
            actual_val = actual.get(fname)

            if fspec.get("type") == "null":
                if actual_val is not None:
                    report.violations.append(DiffViolation(
                        field=fname, expected="null", actual=type(actual_val).__name__,
                    ))
                continue

            if fspec.get("nullable") is False and actual_val is None:
                report.violations.append(DiffViolation(
                    field=fname, expected="non-null", actual="null",
                ))
                continue

            if actual_val is None:
                continue

            if fspec.get("type") == "dict" and isinstance(actual_val, dict):
                for key in fspec.get("required_keys", []):
                    report.checked_fields += 1
                    if key not in actual_val:
                        report.violations.append(DiffViolation(
                            field=f"{fname}.{key}", expected="present", actual="missing",
                        ))

            if "pattern" in fspec and isinstance(actual_val, str):
                report.checked_fields += 1
                if not re.match(fspec["pattern"], actual_val):
                    report.violations.append(DiffViolation(
                        field=fname,
                        expected=f"matches /{fspec['pattern']}/",
                        actual=actual_val,
                    ))

    def _check_value_constraints(
        self, report: DiffReport, actual: dict[str, Any], spec: dict[str, Any]
    ) -> None:
        """Check value_constraints on raw_content fields."""
        constraints = spec.get("value_constraints", {})
        raw_content = actual.get("raw_content", {})
        if not isinstance(raw_content, dict):
            return

        for fname, constraint in constraints.items():
            report.checked_fields += 1
            val = raw_content.get(fname)
            if val is None:
                report.violations.append(DiffViolation(
                    field=f"raw_content.{fname}",
                    expected=f"type {constraint.get('type', 'any')}",
                    actual="null",
                    severity="warning",
                ))
                continue
            ctype = constraint.get("type")
            if ctype == "int" and "min" in constraint:
                if not isinstance(val, int) or val < constraint["min"]:
                    report.violations.append(DiffViolation(
                        field=f"raw_content.{fname}",
                        expected=f">= {constraint['min']}",
                        actual=str(val),
                    ))
            if ctype == "list" and not isinstance(val, list):
                report.violations.append(DiffViolation(
                    field=f"raw_content.{fname}",
                    expected="list",
                    actual=type(val).__name__,
                ))
