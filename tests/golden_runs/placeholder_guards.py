"""Placeholder and empty-success detection guards.

STORY-269 / EPIC-070: Functions that detect when graph nodes or
pipeline adapters return placeholder data that looks like success
but contains no real content. Used in golden-run tests to block
regressions from hiding behind empty outputs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from solstein.domain.models import RawDataSource


@dataclass
class PlaceholderViolation:
    """A single placeholder detection finding."""

    location: str
    field_name: str
    reason: str
    severity: str = "error"


@dataclass
class PlaceholderReport:
    """Result of scanning for placeholder outputs."""

    violations: list[PlaceholderViolation] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not any(v.severity == "error" for v in self.violations)

    def summary(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        lines = [f"[{status}] Placeholder scan: {len(self.violations)} findings"]
        for v in self.violations:
            lines.append(f"  [{v.severity.upper()}] {v.location}.{v.field_name}: {v.reason}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Graph Node Placeholder Guards
# ---------------------------------------------------------------------------


def check_conflict_resolution_output(output: dict[str, Any]) -> PlaceholderReport:
    """Verify conflict resolution node produced real output, not placeholders.

    Known placeholder pattern (STORY-271 ledger):
      conflict_flags: [], resolved_facts: {}
    """
    report = PlaceholderReport()
    loc = "conflict_resolution"

    resolved = output.get("resolved_facts")
    if resolved is not None and isinstance(resolved, dict) and len(resolved) == 0:
        report.violations.append(PlaceholderViolation(
            location=loc,
            field_name="resolved_facts",
            reason="Empty dict — no actual reconciliation performed",
        ))

    flags = output.get("conflict_flags")
    if flags is not None and isinstance(flags, list) and len(flags) == 0:
        # Empty conflict flags alone is a warning (could be legitimately no conflicts)
        # but combined with empty resolved_facts it's a placeholder
        if resolved is not None and isinstance(resolved, dict) and len(resolved) == 0:
            report.violations.append(PlaceholderViolation(
                location=loc,
                field_name="conflict_flags",
                reason="Empty list combined with empty resolved_facts — placeholder pattern",
            ))

    return report


def check_scoring_output(output: dict[str, Any]) -> PlaceholderReport:
    """Verify scoring node produced real scores, not placeholders.

    Known placeholder pattern (STORY-271 ledger):
      confidence_scores: {}, company_scores: {}
    """
    report = PlaceholderReport()
    loc = "scoring"

    scores = output.get("confidence_scores")
    if scores is not None and isinstance(scores, dict) and len(scores) == 0:
        report.violations.append(PlaceholderViolation(
            location=loc,
            field_name="confidence_scores",
            reason="Empty dict — no actual scoring performed",
        ))

    company_scores = output.get("company_scores")
    if company_scores is not None and isinstance(company_scores, dict) and len(company_scores) == 0:
        report.violations.append(PlaceholderViolation(
            location=loc,
            field_name="company_scores",
            reason="Empty dict — no company classification performed",
        ))

    return report


def check_analysis_output(output: dict[str, Any]) -> PlaceholderReport:
    """Verify analysis node produced real analysis, not placeholders.

    Known placeholder pattern (STORY-271 ledger):
      ai_adoption_index: 0.0, top_companies: [], market_trends: []
    """
    report = PlaceholderReport()
    loc = "analysis"

    analysis = output.get("market_analysis", {})
    if not isinstance(analysis, dict):
        report.violations.append(PlaceholderViolation(
            location=loc,
            field_name="market_analysis",
            reason=f"Expected dict, got {type(analysis).__name__}",
        ))
        return report

    if analysis.get("ai_adoption_index", 0.0) == 0.0:
        report.violations.append(PlaceholderViolation(
            location=loc,
            field_name="market_analysis.ai_adoption_index",
            reason="Zero value — no actual AI adoption analysis performed",
        ))

    for list_field in ["top_companies", "market_trends"]:
        val = analysis.get(list_field)
        if isinstance(val, list) and len(val) == 0:
            report.violations.append(PlaceholderViolation(
                location=loc,
                field_name=f"market_analysis.{list_field}",
                reason="Empty list — no actual analysis data produced",
            ))

    return report


def check_export_output(output: dict[str, Any]) -> PlaceholderReport:
    """Verify export node actually exported, not just returned placeholders.

    Known placeholder pattern (STORY-271 ledger):
      export_path: "", export_status: "pending"
    """
    report = PlaceholderReport()
    loc = "export"

    path = output.get("export_path", "")
    if isinstance(path, str) and len(path) == 0:
        report.violations.append(PlaceholderViolation(
            location=loc,
            field_name="export_path",
            reason="Empty string — no artifact actually written",
        ))

    status = output.get("export_status", "")
    if status == "pending":
        report.violations.append(PlaceholderViolation(
            location=loc,
            field_name="export_status",
            reason="Still 'pending' — export never completed",
        ))

    return report


# ---------------------------------------------------------------------------
# Router Bypass Guard
# ---------------------------------------------------------------------------


def check_router_empty_scores_bypass(
    confidence_scores: dict[str, float],
    human_review_required: bool,
) -> PlaceholderReport:
    """Verify the router doesn't silently bypass human review on empty scores.

    Known bug (STORY-271 ledger, line 67-70):
      When confidence_scores == {}, the condition
      `confidence_scores and any(v < threshold for v in {}.values())`
      evaluates to False (empty dict is falsy), silently skipping review.

    The correct behavior: empty scores MUST trigger human review because
    absence of scores means scoring didn't produce results.
    """
    report = PlaceholderReport()

    if not confidence_scores and not human_review_required:
        report.violations.append(PlaceholderViolation(
            location="human_review_router",
            field_name="confidence_scores",
            reason=(
                "Empty confidence_scores with human_review_required=False "
                "silently bypasses human review gate"
            ),
        ))

    return report


# ---------------------------------------------------------------------------
# Enrichment Pipeline Guards
# ---------------------------------------------------------------------------


def check_raw_data_source_not_placeholder(
    source: RawDataSource,
    adapter_name: str,
) -> PlaceholderReport:
    """Verify a RawDataSource contains real data, not placeholder content."""
    report = PlaceholderReport()
    loc = f"adapter:{adapter_name}"

    # Check raw_content is not empty
    content = source.raw_content
    if isinstance(content, dict) and len(content) == 0:
        report.violations.append(PlaceholderViolation(
            location=loc,
            field_name="raw_content",
            reason="Empty dict — adapter returned no actual data",
        ))
    elif isinstance(content, str) and len(content.strip()) == 0:
        report.violations.append(PlaceholderViolation(
            location=loc,
            field_name="raw_content",
            reason="Empty/whitespace string — adapter returned no actual data",
        ))

    # Check confidence is not the generic default
    if source.confidence == 0.0:
        report.violations.append(PlaceholderViolation(
            location=loc,
            field_name="confidence",
            reason="Zero confidence — likely unset placeholder",
            severity="warning",
        ))

    # Check extraction_method is set
    if not source.extraction_method:
        report.violations.append(PlaceholderViolation(
            location=loc,
            field_name="extraction_method",
            reason="Missing extraction_method — adapter didn't declare how data was obtained",
            severity="warning",
        ))

    return report
