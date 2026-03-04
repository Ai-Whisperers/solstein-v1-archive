"""Database performance baseline and SLAs.

This module documents the expected performance characteristics of the database
and provides tools to measure and verify performance.
"""

from dataclasses import dataclass


@dataclass
class QuerySLA:
    """Service Level Agreement for a database query."""

    name: str
    description: str
    max_duration_ms: float
    expected_rows: int


# Define SLAs for common queries
QUERY_SLAS: dict[str, QuerySLA] = {
    "get_company_by_id": QuerySLA(
        name="Get company by ID",
        description="Fetch a single company record by ID",
        max_duration_ms=10.0,
        expected_rows=1,
    ),
    "list_companies": QuerySLA(
        name="List all companies",
        description="Fetch all company records with pagination",
        max_duration_ms=100.0,
        expected_rows=65,
    ),
    "get_company_metrics": QuerySLA(
        name="Get company metrics",
        description="Fetch all metrics for a single company",
        max_duration_ms=50.0,
        expected_rows=10,
    ),
    "search_companies": QuerySLA(
        name="Search companies",
        description="Search companies by name or industry",
        max_duration_ms=200.0,
        expected_rows=10,
    ),
    "get_research_results": QuerySLA(
        name="Get research results",
        description="Fetch research results for a company",
        max_duration_ms=100.0,
        expected_rows=5,
    ),
    "get_enrichment_data": QuerySLA(
        name="Get enrichment data",
        description="Fetch enrichment audit trail for a company",
        max_duration_ms=50.0,
        expected_rows=10,
    ),
}


# Baseline metrics (measured on 2026-02-27)
BASELINE_METRICS = {
    "total_companies": 65,
    "total_scoring_records": 1300,
    "total_signal_records": 6500,
    "total_research_runs": 130,
    "database_size_mb": 50,
    "avg_query_time_ms": 25,
}


def get_sla(query_name: str) -> QuerySLA | None:
    """Get SLA for a query by name.

    Args:
        query_name: The name of the query to get the SLA for.

    Returns:
        The QuerySLA object if found, None otherwise.
    """
    return QUERY_SLAS.get(query_name)


def list_all_slas() -> list[QuerySLA]:
    """List all defined SLAs.

    Returns:
        A list of all QuerySLA objects.
    """
    return list(QUERY_SLAS.values())
