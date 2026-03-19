from __future__ import annotations

from typing import Protocol

from ..domain.models import FinancialMetric


class EnrichableCompany(Protocol):
    name: str
    ticker: str | None
    company_number: str | None
    financials: FinancialMetric
    metric_sources: dict[str, list[str]]
    metric_justifications: dict[str, str]
    enrichment_sources: list[str]
    enrichment_timestamps: dict[str, object]
    data_source_type: str  # 'synthetic', 'real', 'mixed', 'unknown'
