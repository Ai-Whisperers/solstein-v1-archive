"""Financial sanity validation — detects unrealistic financial ratios.

Validates company financial data for common sense checks without blocking
the pipeline. All violations are logged as warnings only.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loguru import logger


@dataclass
class SanityViolation:
    """A single financial sanity violation."""

    field: str
    value: float | None
    expected_range: str
    severity: str  # 'warning', 'critical'
    message: str


@dataclass
class SanityReport:
    """Aggregated sanity report for a company."""

    company_name: str
    violations: list[SanityViolation] = field(default_factory=list)

    @property
    def violation_count(self) -> int:
        """Total number of violations."""
        return len(self.violations)

    @property
    def critical_count(self) -> int:
        """Number of critical violations."""
        return sum(1 for v in self.violations if v.severity == "critical")

    @property
    def is_clean(self) -> bool:
        """True if no violations found."""
        return len(self.violations) == 0

    def summary(self) -> str:
        """Human-readable summary."""
        if self.is_clean:
            return f"{self.company_name}: CLEAN (no sanity violations)"
        parts = [f"{self.company_name}: {self.violation_count} violation(s)"]
        for v in self.violations:
            parts.append(f"  [{v.severity.upper()}] {v.field}: {v.message}")
        return "\n".join(parts)


class FinancialSanityValidator:
    """Validates financial data for common sense.

    All validations produce warnings only — the pipeline never blocks.
    Use validate_company() to get a SanityReport.
    """

    # Revenue per employee thresholds (EUR)
    REV_PER_EMP_MIN_EUR = 30_000  # Minimum reasonable: €30K/employee
    REV_PER_EMP_WARN_LOW = 80_000  # Warning below this
    REV_PER_EMP_WARN_HIGH = 3_000_000  # Warning above this

    # Profit margin thresholds
    MARGIN_IMPOSSIBLE_HIGH = 0.70  # No software company has 70%+ margins
    MARGIN_DEEP_NEGATIVE = -0.50  # -50% margin = serious distress

    # Growth rate thresholds
    GROWTH_IMPOSSIBLE_HIGH = 500.0  # 500% YoY is implausible for established companies
    GROWTH_IMPOSSIBLE_LOW = -80.0  # -80% revenue collapse

    # Funding/revenue ratio
    FUNDING_RATIO_INSANE = 50.0  # Funding > 50x revenue = implausible

    def validate_company(
        self,
        company_name: str,
        revenue_eur_millions: float | None,
        employee_count: int | None,
        profit_margin: float | None,
        growth_rate: float | None,
        total_funding_eur: float | None,
        data_source_type: str = "unknown",
    ) -> SanityReport:
        """Run all sanity checks on a company's financial data.

        Args:
            company_name: Company name for reporting.
            revenue_eur_millions: Revenue in EUR millions.
            employee_count: Number of employees.
            profit_margin: Profit margin as decimal (0.15 = 15%).
            growth_rate: YoY growth rate as percent (30 = 30%).
            total_funding_eur: Total funding in EUR.
            data_source_type: 'synthetic', 'real', or 'unknown'.

        Returns:
            SanityReport with all violations.
        """
        report = SanityReport(company_name=company_name)

        # Skip synthetic data sanity checks (they're expected to have odd values)
        if data_source_type == "synthetic":
            return report

        # Run all validation checks
        self._check_revenue_per_employee(report, revenue_eur_millions, employee_count)
        self._check_profit_margin(report, profit_margin)
        self._check_growth_rate(report, growth_rate)
        self._check_funding_ratio(report, total_funding_eur, revenue_eur_millions)

        # Log violations
        self._log_violations(company_name, report)

        return report

    def _check_revenue_per_employee(
        self,
        report: SanityReport,
        revenue_eur_millions: float | None,
        employee_count: int | None,
    ) -> None:
        """Check revenue per employee is within reasonable bounds."""
        if revenue_eur_millions is None or employee_count is None or employee_count <= 0:
            return

        rev_per_emp = (revenue_eur_millions * 1_000_000) / employee_count

        if rev_per_emp < self.REV_PER_EMP_MIN_EUR:
            report.violations.append(
                SanityViolation(
                    field="revenue_per_employee",
                    value=rev_per_emp,
                    expected_range=f">{self.REV_PER_EMP_WARN_LOW:,.0f} EUR",
                    severity="critical",
                    message=(
                        f"€{rev_per_emp:,.0f}/employee is implausibly low (expected >€{self.REV_PER_EMP_WARN_LOW:,.0f})"
                    ),
                )
            )
        elif rev_per_emp < self.REV_PER_EMP_WARN_LOW:
            report.violations.append(
                SanityViolation(
                    field="revenue_per_employee",
                    value=rev_per_emp,
                    expected_range=f">{self.REV_PER_EMP_WARN_LOW:,.0f} EUR",
                    severity="warning",
                    message=(
                        f"€{rev_per_emp:,.0f}/employee is below industry minimum €{self.REV_PER_EMP_WARN_LOW:,.0f}"
                    ),
                )
            )
        elif rev_per_emp > self.REV_PER_EMP_WARN_HIGH:
            report.violations.append(
                SanityViolation(
                    field="revenue_per_employee",
                    value=rev_per_emp,
                    expected_range=f"<{self.REV_PER_EMP_WARN_HIGH:,.0f} EUR",
                    severity="warning",
                    message=f"€{rev_per_emp:,.0f}/employee seems implausibly high",
                )
            )

    def _check_profit_margin(
        self,
        report: SanityReport,
        profit_margin: float | None,
    ) -> None:
        """Check profit margin is within reasonable bounds."""
        if profit_margin is None:
            return

        if profit_margin > self.MARGIN_IMPOSSIBLE_HIGH:
            report.violations.append(
                SanityViolation(
                    field="profit_margin",
                    value=profit_margin,
                    expected_range=f"<{self.MARGIN_IMPOSSIBLE_HIGH:.0%}",
                    severity="critical",
                    message=f"{profit_margin:.1%} profit margin is implausibly high for software",
                )
            )
        elif profit_margin < self.MARGIN_DEEP_NEGATIVE:
            report.violations.append(
                SanityViolation(
                    field="profit_margin",
                    value=profit_margin,
                    expected_range=f">{self.MARGIN_DEEP_NEGATIVE:.0%}",
                    severity="warning",
                    message=f"{profit_margin:.1%} margin indicates severe distress",
                )
            )

    def _check_growth_rate(
        self,
        report: SanityReport,
        growth_rate: float | None,
    ) -> None:
        """Check growth rate is within reasonable bounds."""
        if growth_rate is None:
            return

        if growth_rate > self.GROWTH_IMPOSSIBLE_HIGH:
            report.violations.append(
                SanityViolation(
                    field="growth_rate",
                    value=growth_rate,
                    expected_range=f"<{self.GROWTH_IMPOSSIBLE_HIGH}%",
                    severity="critical",
                    message=f"{growth_rate:.1f}% YoY growth is implausible for an established company",
                )
            )
        elif growth_rate < self.GROWTH_IMPOSSIBLE_LOW:
            report.violations.append(
                SanityViolation(
                    field="growth_rate",
                    value=growth_rate,
                    expected_range=f">{self.GROWTH_IMPOSSIBLE_LOW}%",
                    severity="warning",
                    message=f"{growth_rate:.1f}% YoY decline suggests critical situation",
                )
            )

    def _check_funding_ratio(
        self,
        report: SanityReport,
        total_funding_eur: float | None,
        revenue_eur_millions: float | None,
    ) -> None:
        """Check funding to revenue ratio is reasonable."""
        if total_funding_eur is None or revenue_eur_millions is None or revenue_eur_millions <= 0:
            return

        funding_revenue_ratio = total_funding_eur / (revenue_eur_millions * 1_000_000)
        if funding_revenue_ratio > self.FUNDING_RATIO_INSANE:
            report.violations.append(
                SanityViolation(
                    field="funding_revenue_ratio",
                    value=funding_revenue_ratio,
                    expected_range=f"<{self.FUNDING_RATIO_INSANE}x",
                    severity="warning",
                    message=f"Funding is {funding_revenue_ratio:.0f}x revenue — check data accuracy",
                )
            )

    def _log_violations(self, company_name: str, report: SanityReport) -> None:
        """Log all violations for a company."""
        if report.is_clean:
            return

        logger.warning(
            f"Sanity violations for {company_name} ({report.violation_count} total, {report.critical_count} critical)"
        )
        for v in report.violations:
            log_fn = logger.error if v.severity == "critical" else logger.warning
            log_fn(f"  {company_name}.{v.field}: {v.message}")


def validate_batch(
    companies: list[dict],
) -> tuple[list[SanityReport], int]:
    """Validate a batch of company dicts and return reports + total violation count.

    Args:
        companies: List of company dicts (from JSON or models).

    Returns:
        Tuple of (reports_list, total_violations).
    """
    validator = FinancialSanityValidator()
    reports: list[SanityReport] = []
    total_violations = 0

    for company in companies:
        name = company.get("name", "Unknown")
        report = validator.validate_company(
            company_name=name,
            revenue_eur_millions=company.get("revenue_eur_millions"),
            employee_count=company.get("employee_count"),
            profit_margin=company.get("profit_margin"),
            growth_rate=company.get("growth_rate"),
            total_funding_eur=company.get("funding_raised"),
            data_source_type=company.get("data_source_type", "unknown"),
        )
        reports.append(report)
        total_violations += report.violation_count

    logger.info(
        f"Financial sanity validation complete: {total_violations} violations across {len(companies)} companies"
    )
    return reports, total_violations
