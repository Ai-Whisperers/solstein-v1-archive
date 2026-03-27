"""CSV exporter for company profiles.

Exports all Company model fields to a UTF-8 CSV file.  This is the
simplest portable format — every field is included and the output is
readable in Excel, pandas, or any spreadsheet application.

Usage::

    from pathlib import Path
    from solstein.exporters.csv import CSVExporter

    exporter = CSVExporter()
    path = exporter.export(companies, output_path=Path("/tmp/companies.csv"))
    logger.info(f"Exported {len(companies)} companies to {path}")
"""

from __future__ import annotations

import csv
import io
from collections.abc import Sequence
from pathlib import Path

from loguru import logger

from solstein.domain.models import Company


class CSVExporter:
    """Exports Company objects to CSV."""

    # Ordered list of (csv_header, attribute_path) pairs.
    # Dot-notation is NOT used — getattr with defaults handles all optional fields.
    COLUMNS: list[tuple[str, str]] = [
        ("Name", "name"),
        ("Industry", "industry"),
        ("Headquarters", "headquarters"),
        ("Founded Year", "founded_year"),
        ("Website", "website"),
        ("Employees", "employees"),
        ("Ticker", "ticker"),
        ("Company Number", "company_number"),
        ("ISIN", "isin"),
        ("Geography Code", "geography_code"),
        ("Tier", "tier"),
        ("Threat Level", "threat_level"),
        ("Classification", "classification"),
        ("AI Maturity", "ai_maturity"),
        ("AI Score", "ai_score"),
        ("AI Readiness Score", "ai_readiness_score"),
        ("AI Readiness Tier", "ai_readiness_tier"),
        ("SaaS Maturity", "saas_maturity"),
        ("Composite Score", "composite_score"),
        ("Growth Score", "growth_score"),
        ("Financial Health Score", "financial_health_score"),
        ("Competitive Position Score", "competitive_position_score"),
        ("Revenue EUR M", "financials.revenue"),
        ("Growth Rate %", "financials.growth_rate"),
        ("Revenue CAGR 3yr %", "revenue_cagr_3yr"),
        ("Profit Margin %", "profit_margin"),
        ("EBITDA Margin %", "ebitda_margin"),
        ("Recurring Revenue %", "recurring_revenue_pct"),
        ("Total Funding EUR M", "total_funding_raised_eur"),
        ("Latest Valuation EUR M", "latest_valuation_eur"),
        ("AI In Production", "ai_in_production"),
        ("Transform Time (months)", "transformation_time_months"),
        ("Transform Cost (EUR)", "transformation_cost_eur"),
        ("Transform Efficiency Gain %", "transformation_efficiency_gain_pct"),
        ("Transform Risk", "transformation_risk_level"),
        ("Confidence Level", "confidence_level"),
        ("Description", "description"),
    ]

    def export(
        self,
        companies: Sequence[Company],
        output_path: Path | None = None,
    ) -> Path:
        """Export companies to a CSV file.

        Args:
            companies: Sequence of Company domain objects.
            output_path: Destination path.  Defaults to ``./companies_export.csv``.

        Returns:
            Resolved path to the written file.
        """
        if output_path is None:
            output_path = Path("companies_export.csv")

        headers = [col for col, _ in self.COLUMNS]
        rows = [self._company_to_row(c) for c in companies]

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(headers)
            writer.writerows(rows)

        logger.info("CSV export complete", path=str(output_path), rows=len(rows))
        return output_path.resolve()

    def to_bytes(self, companies: Sequence[Company]) -> bytes:
        """Return CSV content as UTF-8 encoded bytes (for API streaming)."""
        headers = [col for col, _ in self.COLUMNS]
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(headers)
        for c in companies:
            writer.writerow(self._company_to_row(c))
        return output.getvalue().encode("utf-8")

    def _company_to_row(self, company: Company) -> list:
        """Map a Company object to a list of cell values."""
        row = []
        for _, attr in self.COLUMNS:
            if "." in attr:
                # Nested attribute (e.g. financials.revenue)
                parts = attr.split(".", 1)
                parent = getattr(company, parts[0], None)
                value = getattr(parent, parts[1], "") if parent else ""
            else:
                value = getattr(company, attr, "")

            # Normalise enum values
            if hasattr(value, "value"):
                value = value.value
            elif isinstance(value, list):
                value = "; ".join(str(v) for v in value)
            elif value is None:
                value = ""
            row.append(value)
        return row
